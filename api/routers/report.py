# api/routers/report.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import json
import re
from datetime import datetime
from api.services.task_manager import task_manager

router = APIRouter()


@router.get("/{task_id}")
async def get_report(task_id: str):
    """获取 Allure 报告"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    report_path = Path("allure-report")
    if report_path.exists():
        return FileResponse(
            report_path / "index.html",
            media_type="text/html"
        )
    raise HTTPException(status_code=404, detail="报告不存在")


@router.get("/{task_id}/summary")
async def get_report_summary(task_id: str):
    """获取报告摘要"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 解析测试结果
    result = task.get("result", {})
    stdout = result.get("stdout", "")

    # 简单解析 pytest 输出
    total = 0
    passed = 0
    failed = 0
    skipped = 0

    # 匹配 "X passed, Y failed, Z warnings"
    match = re.search(r"(\d+)\s+passed.*?(\d+)\s+failed", stdout)
    if match:
        passed = int(match.group(1))
        failed = int(match.group(2))
        total = passed + failed + skipped

    return {
        "task_id": task_id,
        "status": task["status"],
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "duration": task.get("duration", 0),
        "start_time": task["start_time"],
        "end_time": task.get("end_time")
    }


@router.get("/latest/summary")
async def get_latest_summary():
    """获取最新报告摘要"""
    tasks = task_manager.get_tasks(limit=1)
    if not tasks:
        return {"message": "没有测试记录"}

    task = tasks[0]
    return await get_report_summary(task["task_id"])