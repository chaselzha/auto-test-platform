# api/routers/test.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import uuid
from datetime import datetime
import asyncio

from api.services.task_manager import task_manager
from api.services.test_runner import test_runner
from api.models.schemas import TestParams, TaskResponse, TaskStatus
from api.dependencies import get_current_user, rate_limit

router = APIRouter()


@router.post("/run", response_model=TaskResponse)
async def run_test(
        params: TestParams,
        current_user: dict = Depends(get_current_user),
        _: bool = Depends(rate_limit(limit=10, window=60))
):
    """
    执行测试任务（需要认证）
    """
    user_api_key = current_user.get('api_key', 'unknown')
    print(f"👤 用户: {user_api_key} 执行测试")

    params_dict = params.model_dump()
    print(f"📋 参数: {params_dict}")

    task_id = str(uuid.uuid4())[:8]

    # 创建任务
    task_manager.create_task(task_id, params_dict)

    # 执行测试（异步）
    try:
        # 直接调用异步方法
        result = await test_runner.run_tests(params_dict)
        task_manager.update_task(task_id, result)
        print(f"✅ 任务 {task_id} 完成，状态: {result.get('status')}")
    except Exception as e:
        print(f"❌ 测试执行失败: {e}")
        import traceback
        traceback.print_exc()
        task_manager.update_task(task_id, {
            "status": "failed",
            "error": str(e),
            "end_time": datetime.now().isoformat()
        })

    task = task_manager.get_task(task_id)
    return TaskResponse(
        task_id=task_id,
        status=task["status"],
        message="测试任务已提交"
    )


@router.get("/tasks", response_model=List[TaskStatus])
async def get_tasks(
        limit: int = 20,
        current_user: dict = Depends(get_current_user)
):
    """获取任务列表"""
    tasks = task_manager.get_tasks(limit=limit)
    return tasks


@router.get("/task/{task_id}", response_model=TaskStatus)
async def get_task(
        task_id: str,
        current_user: dict = Depends(get_current_user)
):
    """获取任务详情"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.delete("/task/{task_id}")
async def delete_task(
        task_id: str,
        current_user: dict = Depends(get_current_user)
):
    """删除任务"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    task_manager.delete_task(task_id)
    return {"message": f"任务 {task_id} 已删除"}


@router.get("/statistics")
async def get_statistics(
        current_user: dict = Depends(get_current_user)
):
    """获取统计信息"""
    tasks = task_manager.get_tasks(limit=1000)
    stats = {
        "total": len(tasks),
        "success": 0,
        "failed": 0,
        "pending": 0,
        "running": 0
    }

    for task in tasks:
        status = task.get("status", "pending")
        if status in stats:
            stats[status] += 1

    return stats


@router.get("/public/health")
async def public_health():
    """公开的健康检查"""
    return {
        "status": "healthy",
        "message": "API is running",
        "timestamp": datetime.now().isoformat()
    }