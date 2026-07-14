# api/services/test_runner.py
import subprocess
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import asyncio
import sys


class TestRunner:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.results_dir = self.base_dir / "automation" / "reports" / "allure-results"
        self.reports_dir = self.base_dir / "task-reports"

        # 确保目录存在
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        print(f"✅ TestRunner 初始化完成")
        print(f"   📁 基础目录: {self.base_dir}")
        print(f"   📁 结果目录: {self.results_dir}")
        print(f"   📁 报告目录: {self.reports_dir}")

    async def run_tests(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行测试"""
        task_id = str(uuid.uuid4())[:8]
        start_time = datetime.now()

        # 获取参数
        env = params.get('env', 'test')
        browser = params.get('browser', 'chrome')
        parallel = params.get('parallel', 4)
        markers = params.get('markers')
        headless = params.get('headless', True)

        # 构建 pytest 命令
        cmd = [
            sys.executable, "-m", "pytest",  # 使用当前 Python 解释器
            "-v",
            "--tb=short",
            f"-n={parallel}",
            "--alluredir", str(self.results_dir),
            "--clean-alluredir"
        ]

        # 添加标记
        if markers:
            cmd.extend(["-m", markers])

        # 添加测试路径
        cmd.append("automation/tests/")

        print(f"🔧 执行命令: {' '.join(cmd)}")
        print(f"🌍 环境: {env}, 浏览器: {browser}, 并行: {parallel}")
        print(f"🏷️ 标记: {markers}")

        # 设置环境变量
        env_vars = {
            **subprocess.os.environ,
            "TEST_ENV": env,
            "BROWSER": browser,
            "HEADLESS": str(headless),
            "PYTHONUNBUFFERED": "1"  # 确保输出实时显示
        }

        try:
            # 使用 asyncio 执行子进程
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env_vars,
                cwd=str(self.base_dir)
            )

            # 等待完成，设置超时
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=3600  # 1小时超时
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise TimeoutError("测试执行超时（1小时）")

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # 解码输出
            stdout_text = stdout.decode('utf-8', errors='ignore')
            stderr_text = stderr.decode('utf-8', errors='ignore')

            # 判断状态
            status = "success" if process.returncode == 0 else "failed"

            print(f"📊 测试完成，返回码: {process.returncode}")
            print(f"⏱️ 耗时: {duration:.2f}s")

            return {
                "task_id": task_id,
                "status": status,
                "env": env,
                "browser": browser,
                "parallel": parallel,
                "markers": markers,
                "headless": headless,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration": duration,
                "result": {
                    "stdout": stdout_text,
                    "stderr": stderr_text,
                    "returncode": process.returncode
                }
            }

        except TimeoutError as e:
            print(f"⏰ 测试超时: {e}")
            return {
                "task_id": task_id,
                "status": "failed",
                "env": env,
                "browser": browser,
                "parallel": parallel,
                "markers": markers,
                "headless": headless,
                "start_time": start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration": 0,
                "result": {
                    "stdout": "",
                    "stderr": str(e),
                    "returncode": -1
                },
                "error": str(e)
            }

        except Exception as e:
            print(f"❌ 测试执行异常: {e}")
            import traceback
            traceback.print_exc()

            return {
                "task_id": task_id,
                "status": "failed",
                "env": env,
                "browser": browser,
                "parallel": parallel,
                "markers": markers,
                "headless": headless,
                "start_time": start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration": 0,
                "result": {
                    "stdout": "",
                    "stderr": str(e),
                    "returncode": -1
                },
                "error": str(e)
            }


# 创建全局实例
test_runner = TestRunner()