# api/services/task_manager.py
import json
import uuid
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 现在可以从 automation.utils 导入
from automation.utils.logger import logger
from api.models.schemas import TaskInfo, TestStatus


class TaskManager:
    """任务管理器"""

    def __init__(self):
        self.tasks: Dict[str, Dict] = {}
        self.task_dir = Path("api/tasks")
        self.task_dir.mkdir(parents=True, exist_ok=True)
        self._load_tasks()

    def _load_tasks(self):
        """从文件加载任务"""
        for task_file in self.task_dir.glob("*.json"):
            try:
                with open(task_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.tasks[data["task_id"]] = data
            except Exception as e:
                logger.warning(f"加载任务失败: {e}")

    def _save_task(self, task_id: str):
        """保存任务到文件"""
        if task_id in self.tasks:
            task_file = self.task_dir / f"{task_id}.json"
            with open(task_file, "w", encoding="utf-8") as f:
                json.dump(self.tasks[task_id], f, ensure_ascii=False, indent=2)

    def create_task(self, env: str, browser: str, **kwargs) -> str:
        """创建任务"""
        task_id = str(uuid.uuid4())[:8]
        self.tasks[task_id] = {
            "task_id": task_id,
            "status": "pending",
            "env": env,
            "browser": browser,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "duration": None,
            "exit_code": None,
            "kwargs": kwargs,
            "result": None
        }
        self._save_task(task_id)
        logger.info(f"📋 创建任务: {task_id}")
        return task_id

    def update_task(self, task_id: str, **kwargs):
        """更新任务状态"""
        if task_id in self.tasks:
            for key, value in kwargs.items():
                self.tasks[task_id][key] = value
            if "status" in kwargs:
                logger.info(f"📋 任务 {task_id} 状态: {kwargs['status']}")
            self._save_task(task_id)

    def get_task(self, task_id: str) -> Optional[Dict]:
        """获取任务"""
        return self.tasks.get(task_id)

    def get_tasks(self, limit: int = 50, status: Optional[str] = None) -> List[Dict]:
        """获取任务列表"""
        tasks = list(self.tasks.values())
        tasks.sort(key=lambda x: x["start_time"], reverse=True)

        if status:
            tasks = [t for t in tasks if t["status"] == status]

        return tasks[:limit]

    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            task_file = self.task_dir / f"{task_id}.json"
            if task_file.exists():
                task_file.unlink()
            logger.info(f"🗑️ 删除任务: {task_id}")
            return True
        return False

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        tasks = list(self.tasks.values())
        total = len(tasks)
        if total == 0:
            return {"total": 0, "success": 0, "failed": 0, "pending": 0, "running": 0}

        success = sum(1 for t in tasks if t["status"] == "success")
        failed = sum(1 for t in tasks if t["status"] == "failed")
        pending = sum(1 for t in tasks if t["status"] == "pending")
        running = sum(1 for t in tasks if t["status"] == "running")

        return {
            "total": total,
            "success": success,
            "failed": failed,
            "pending": pending,
            "running": running
        }


# 全局任务管理器
task_manager = TaskManager()