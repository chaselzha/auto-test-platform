# api/routers/test.py
from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import List, Optional
from api.models.schemas import TestRequest, TestResponse, TestResult, TaskInfo
from api.services.task_manager import task_manager
from api.services.test_runner import test_runner
from utils.logger import logger

router = APIRouter()


@router.post("/run", response_model=TestResponse)
async def run_test(request: TestRequest, background_tasks: BackgroundTasks):
    """
    执行测试
    """
    # 创建任务
    task_id = task_manager.create_task(
        env=request.env,
        browser=request.browser,
        headless=request.headless,
        test_path=request.test_path,
        parallel=request.parallel,
        markers=request.markers
    )

    # 异步执行测试
    background_tasks.add_task(
        test_runner.run,
        task_id,
        request.env,
        request.browser,
        request.headless,
        request.test_path,
        request.parallel,
        request.markers
    )

    return TestResponse(
        task_id=task_id,
        status="pending",
        message="测试任务已提交，正在异步执行",
        env=request.env,
        browser=request.browser,
        start_time=datetime.now()
    )


@router.get("/tasks", response_model=List[TaskInfo])
async def get_tasks(limit: int = 50, status: Optional[str] = None):
    """获取任务列表"""
    tasks = task_manager.get_tasks(limit, status)
    return [
        TaskInfo(
            task_id=t["task_id"],
            status=t["status"],
            env=t["env"],
            browser=t["browser"],
            start_time=datetime.fromisoformat(t["start_time"]),
            duration=t.get("duration")
        )
        for t in tasks
    ]


@router.get("/task/{task_id}")
async def get_task(task_id: str):
    """获取任务详情"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.delete("/task/{task_id}")
async def delete_task(task_id: str):
    """删除任务"""
    if task_manager.delete_task(task_id):
        return {"message": "任务已删除"}
    raise HTTPException(status_code=404, detail="任务不存在")


@router.get("/statistics")
async def get_statistics():
    """获取统计信息"""
    return task_manager.get_statistics()


# 导入 datetime
from datetime import datetime