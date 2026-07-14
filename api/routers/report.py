from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import json
import re
import subprocess
import shutil
from datetime import datetime
from api.services.task_manager import task_manager

router = APIRouter()

# ===== 目录配置 - 适配您的项目结构 =====
BASE_DIR = Path(__file__).parent.parent.parent

# Allure 结果目录（在 automation/reports 目录下）
ALLURE_RESULTS_DIR = BASE_DIR / "automation" / "reports" / "allure-results"
ALLURE_REPORT_DIR = BASE_DIR / "automation" / "reports" / "allure-report"
TASK_REPORTS_DIR = BASE_DIR / "task-reports"


@router.get("/{task_id}")
async def get_report(task_id: str):
    """获取测试报告（优先 HTML，备选 JSON）"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 1. 尝试返回任务特定的 Allure 报告
    task_report_dir = TASK_REPORTS_DIR / task_id
    task_index = task_report_dir / "index.html"

    if task_index.exists():
        return FileResponse(task_index, media_type="text/html")

    # 2. 检查 allure-results 是否存在并生成报告
    print(f"🔍 检查 Allure 结果目录: {ALLURE_RESULTS_DIR}")
    if ALLURE_RESULTS_DIR.exists():
        result_files = list(ALLURE_RESULTS_DIR.glob("*.json"))
        print(f"📊 找到 {len(result_files)} 个 Allure 结果文件")

        if result_files:
            try:
                # 创建任务报告目录
                task_report_dir.mkdir(parents=True, exist_ok=True)

                # 生成 Allure 报告
                print(f"📊 正在为任务 {task_id} 生成 Allure 报告...")
                cmd = [
                    "allure", "generate",
                    str(ALLURE_RESULTS_DIR),
                    "-o", str(task_report_dir),
                    "--clean"
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

                if result.returncode == 0 and task_index.exists():
                    print(f"✅ 报告生成成功: {task_index}")
                    return FileResponse(task_index, media_type="text/html")
                else:
                    print(f"❌ 报告生成失败: {result.stderr}")
            except subprocess.TimeoutExpired:
                print("❌ 报告生成超时")
            except Exception as e:
                print(f"❌ 报告生成异常: {e}")

    # 3. 检查全局 Allure 报告
    if ALLURE_REPORT_DIR.exists():
        index_file = ALLURE_REPORT_DIR / "index.html"
        if index_file.exists():
            return FileResponse(index_file, media_type="text/html")

    # 4. 返回 JSON 格式（备选方案）
    return await get_report_json(task_id)


@router.get("/{task_id}/json")
async def get_report_json(task_id: str):
    """获取 JSON 格式的测试报告"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 解析测试结果
    result = task.get("result", {})
    stdout = result.get("stdout", "")

    # 解析测试统计
    total = 0
    passed = 0
    failed = 0
    skipped = 0
    errors = 0

    if stdout:
        # 匹配 "X passed, Y failed"
        match = re.search(r"(\d+)\s+passed.*?(\d+)\s+failed", stdout)
        if match:
            passed = int(match.group(1))
            failed = int(match.group(2))
            total = passed + failed

        # 匹配 skipped
        match_skipped = re.search(r"(\d+)\s+skipped", stdout)
        if match_skipped:
            skipped = int(match_skipped.group(1))
            total += skipped

        # 匹配 errors
        match_errors = re.search(r"(\d+)\s+errors?", stdout)
        if match_errors:
            errors = int(match_errors.group(1))
            total += errors

        # 如果没有匹配到，尝试其他格式
        if total == 0:
            match = re.search(r"===.*?(\d+)\s+passed.*?(\d+)\s+failed.*?(\d+)\s+skipped", stdout, re.DOTALL)
            if match:
                passed = int(match.group(1))
                failed = int(match.group(2))
                skipped = int(match.group(3))
                total = passed + failed + skipped

    # 检查 Allure 结果是否存在
    allure_exists = ALLURE_RESULTS_DIR.exists() and list(ALLURE_RESULTS_DIR.glob("*.json"))

    return JSONResponse(content={
        "task_id": task_id,
        "status": task.get("status"),
        "env": task.get("env", "unknown"),
        "browser": task.get("browser", "unknown"),
        "parallel": task.get("parallel", 1),
        "duration": round(task.get("duration", 0), 2),
        "start_time": task.get("start_time"),
        "end_time": task.get("end_time"),
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "errors": errors
        },
        "output": {
            "stdout": stdout[-2000:] if len(stdout) > 2000 else stdout,
            "stderr": result.get("stderr", "")[-500:] if result.get("stderr") else ""
        },
        "html_available": False,
        "allure_results_exists": allure_exists,
        "allure_results_path": str(ALLURE_RESULTS_DIR) if allure_exists else None,
        "message": "📊 JSON 格式报告（HTML 报告不可用）"
    })


@router.get("/{task_id}/summary")
async def get_report_summary(task_id: str):
    """获取报告摘要"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    result = task.get("result", {})
    stdout = result.get("stdout", "")

    total = 0
    passed = 0
    failed = 0
    skipped = 0
    errors = 0

    if stdout:
        match = re.search(r"(\d+)\s+passed.*?(\d+)\s+failed", stdout)
        if match:
            passed = int(match.group(1))
            failed = int(match.group(2))
            total = passed + failed

        match_skipped = re.search(r"(\d+)\s+skipped", stdout)
        if match_skipped:
            skipped = int(match_skipped.group(1))
            total += skipped

        match_errors = re.search(r"(\d+)\s+errors?", stdout)
        if match_errors:
            errors = int(match_errors.group(1))
            total += errors

    return {
        "task_id": task_id,
        "status": task.get("status"),
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "errors": errors,
        "duration": round(task.get("duration", 0), 2),
        "start_time": task.get("start_time"),
        "end_time": task.get("end_time"),
        "env": task.get("env", "unknown"),
        "browser": task.get("browser", "unknown")
    }


@router.get("/latest/summary")
async def get_latest_summary():
    """获取最新报告摘要"""
    tasks = task_manager.get_tasks(limit=1)
    if not tasks:
        return {"message": "没有测试记录"}

    task = tasks[0]
    return await get_report_summary(task["task_id"])


@router.post("/{task_id}/generate")
async def generate_report(task_id: str):
    """手动生成 Allure 报告"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if not ALLURE_RESULTS_DIR.exists():
        return {
            "error": f"Allure 结果目录不存在: {ALLURE_RESULTS_DIR}",
            "suggestion": "请先执行测试生成 Allure 结果"
        }

    result_files = list(ALLURE_RESULTS_DIR.glob("*.json"))
    if not result_files:
        return {
            "error": "Allure 结果目录为空",
            "suggestion": "请先执行测试生成 Allure 结果"
        }

    task_report_dir = TASK_REPORTS_DIR / task_id
    task_report_dir.mkdir(parents=True, exist_ok=True)

    try:
        cmd = [
            "allure", "generate",
            str(ALLURE_RESULTS_DIR),
            "-o", str(task_report_dir),
            "--clean"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            return {
                "task_id": task_id,
                "status": "success",
                "report_path": str(task_report_dir / "index.html"),
                "message": "✅ Allure 报告生成成功"
            }
        else:
            return {
                "task_id": task_id,
                "status": "failed",
                "error": result.stderr,
                "message": "❌ 报告生成失败"
            }
    except subprocess.TimeoutExpired:
        return {
            "task_id": task_id,
            "status": "timeout",
            "message": "⏰ 报告生成超时"
        }
    except Exception as e:
        return {
            "task_id": task_id,
            "status": "error",
            "error": str(e),
            "message": f"❌ 报告生成异常: {str(e)}"
        }


@router.delete("/{task_id}")
async def delete_report(task_id: str):
    """删除任务报告"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    task_report_dir = TASK_REPORTS_DIR / task_id
    if task_report_dir.exists():
        shutil.rmtree(task_report_dir)
        return {"message": f"✅ 报告 {task_id} 已删除"}

    return {"message": f"报告 {task_id} 不存在"}