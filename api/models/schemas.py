# api/models/schemas.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TestStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class TestRequest(BaseModel):
    """测试执行请求"""
    env: str = "test"
    browser: str = "chrome"
    headless: bool = True
    test_path: Optional[str] = None
    parallel: int = 1
    markers: Optional[str] = None


class TestResponse(BaseModel):
    """测试执行响应"""
    task_id: str
    status: TestStatus
    message: str
    env: str
    browser: str
    start_time: datetime


class TestResult(BaseModel):
    """测试结果"""
    task_id: str
    status: TestStatus
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
    """任务信息"""
    task_id: str
    status: TestStatus
    env: str
    browser: str
    start_time: datetime
    duration: Optional[float] = None


class ReportSummary(BaseModel):
    """报告摘要"""
    total: int
    passed: int
    failed: int
    skipped: int
    duration: float
    start_time: datetime
    end_time: datetime