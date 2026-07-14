# api/models/schemas.py
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class TestStatus(str, Enum):
    """测试状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class TestParams(BaseModel):
    """测试执行参数"""
    env: str = "test"
    browser: str = "chrome"
    headless: bool = True
    parallel: int = 1
    markers: Optional[str] = None
    test_path: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "env": "test",
                "browser": "chrome",
                "headless": True,
                "parallel": 4,
                "markers": "smoke or regression"
            }
        }


class TaskResponse(BaseModel):
    """任务提交响应"""
    task_id: str
    status: str
    message: str

    class Config:
        schema_extra = {
            "example": {
                "task_id": "abc12345",
                "status": "pending",
                "message": "测试任务已提交"
            }
        }


class TaskStatus(BaseModel):
    """任务状态信息"""
    task_id: str
    status: str
    env: str
    browser: str
    start_time: str
    duration: Optional[float] = None
    end_time: Optional[str] = None
    parallel: Optional[int] = 1
    markers: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

    class Config:
        schema_extra = {
            "example": {
                "task_id": "abc12345",
                "status": "success",
                "env": "test",
                "browser": "chrome",
                "start_time": "2026-07-14T15:52:11.905688",
                "duration": 172.05,
                "end_time": "2026-07-14T15:55:03.963721",
                "parallel": 4
            }
        }


# ===== 以下是原有的模型，保留兼容 =====

class TestRequest(BaseModel):
    """测试执行请求（兼容旧版本）"""
    env: str = "test"
    browser: str = "chrome"
    headless: bool = True
    test_path: Optional[str] = None
    parallel: int = 1
    markers: Optional[str] = None


class TestResponse(BaseModel):
    """测试执行响应（兼容旧版本）"""
    task_id: str
    status: str
    message: str
    env: str
    browser: str
    start_time: datetime


class TestResult(BaseModel):
    """测试结果（兼容旧版本）"""
    task_id: str
    status: str
    exit_code: int
    duration: float
    env: str
    browser: str
    start_time: datetime
    end_time: Optional[datetime] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    report_path: Optional[str] = None
    allure_url: Optional[str] = None


class TaskInfo(BaseModel):
    """任务信息（兼容旧版本）"""
    task_id: str
    status: str
    env: str
    browser: str
    start_time: datetime
    duration: Optional[float] = None