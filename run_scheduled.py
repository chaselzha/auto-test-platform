# run_scheduled.py
# !/usr/bin/env python3
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import logger
from utils.config import get_config


def run_tests(env="test", browser="chrome", parallel=4, markers="smoke"):
    """
    执行定时测试

    Args:
        env: 测试环境
        browser: 浏览器类型
        parallel: 并行进程数
        markers: 测试标记
    """
    logger.info("=" * 60)
    logger.info(f"🕐 定时测试开始")
    logger.info(f"📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"🌍 环境: {env}")
    logger.info(f"🌐 浏览器: {browser}")
    logger.info(f"🔢 并行数: {parallel}")
    logger.info(f"🏷️  标记: {markers}")
    logger.info("=" * 60)

    # 设置环境变量
    os.environ['BROWSER'] = browser
    os.environ['HEADLESS'] = 'true'
    os.environ['TEST_ENV'] = env

    # 构建命令
    cmd = [
        "pytest",
        "automation/tests/",
        f"--env={env}",
        f"--alluredir=automation/reports/allure-results",
        f"-n", str(parallel),
        "-v",
        "--tb=short",
        f"-m", markers
    ]

    logger.info(f"📋 执行命令: {' '.join(cmd)}")

    # 执行测试
    start_time = datetime.now()
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent
    )
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # 输出结果
    logger.info("=" * 60)
    logger.info(f"✅ 定时测试完成")
    logger.info(f"⏱️  耗时: {duration:.2f}s")
    logger.info(f"📊 退出码: {result.returncode}")

    if result.stdout:
        logger.info("📝 标准输出:")
        print(result.stdout)

    if result.stderr:
        logger.warning("⚠️ 错误输出:")
        print(result.stderr)

    logger.info("=" * 60)

    return result.returncode


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="定时测试执行器")
    parser.add_argument("--env", default="test", choices=["test", "dev", "prod"], help="测试环境")
    parser.add_argument("--browser", default="chrome", choices=["chrome", "firefox", "edge"], help="浏览器")
    parser.add_argument("--parallel", type=int, default=4, help="并行进程数")
    parser.add_argument("--markers", default="smoke", help="测试标记")

    args = parser.parse_args()

    exit_code = run_tests(
        env=args.env,
        browser=args.browser,
        parallel=args.parallel,
        markers=args.markers
    )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()