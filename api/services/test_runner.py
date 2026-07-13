# api/services/test_runner.py
import subprocess
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from automation.utils.logger import logger
from api.services.task_manager import task_manager


class TestRunner:
    """测试执行器"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.automation_dir = self.project_root / "automation"
        self.reports_dir = self.automation_dir / "reports" / "allure-results"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def run(self, task_id: str, env: str, browser: str, headless: bool = True,
            test_path: str = None, parallel: int = 1, markers: str = None):
        """执行测试"""
        try:
            task_manager.update_task(task_id, status="running")
            start_time = datetime.now()

            # 设置环境变量
            os.environ["TEST_ENV"] = env
            os.environ["BROWSER"] = browser
            os.environ["HEADLESS"] = str(headless).lower()
            os.environ["BUILD_NUMBER"] = f"api-{task_id}"

            # 构建命令
            cmd = [
                sys.executable, "-m", "pytest",
                str(self.automation_dir / "tests") if not test_path else str(self.automation_dir / test_path),
                f"--env={env}",
                f"--alluredir={self.reports_dir}",
                "-v",
                "--tb=short"
            ]

            if parallel > 1:
                cmd.extend(["-n", str(parallel)])

            if markers:
                cmd.extend(["-m", markers])

            logger.info(f"🚀 执行测试: task_id={task_id}, env={env}, browser={browser}")
            logger.debug(f"📋 命令: {' '.join(cmd)}")

            # 执行测试
            result = subprocess.run(
                cmd,
                cwd=str(self.automation_dir),
                capture_output=True,
                text=True,
                env=os.environ.copy()
            )

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # 更新任务结果
            status = "success" if result.returncode == 0 else "failed"

            task_manager.update_task(
                task_id,
                status=status,
                end_time=end_time.isoformat(),
                duration=duration,
                exit_code=result.returncode,
                result={
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "report_path": str(self.reports_dir),
                    "allure_url": f"/api/report/{task_id}"
                }
            )

            logger.info(f"✅ 测试完成: task_id={task_id}, status={status}, duration={duration:.2f}s")

        except Exception as e:
            logger.error(f"❌ 测试执行失败: {e}")
            task_manager.update_task(
                task_id,
                status="failed",
                end_time=datetime.now().isoformat(),
                result={"error": str(e)}
            )


# 全局测试执行器
test_runner = TestRunner()