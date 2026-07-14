from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import json
import re
import subprocess
import shutil
from datetime import datetime
from api.services.task_manager import task_manager

router = APIRouter()

# ===== 目录配置 =====
BASE_DIR = Path(__file__).parent.parent.parent

# Allure 结果目录
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
        # 返回报告页面
        return FileResponse(task_index, media_type="text/html")

    # 2. 检查 allure-results 是否存在并生成报告
    print(f"🔍 检查 Allure 结果目录: {ALLURE_RESULTS_DIR}")

    if not ALLURE_RESULTS_DIR.exists():
        print(f"❌ Allure 结果目录不存在: {ALLURE_RESULTS_DIR}")
        return await get_report_json(task_id)

    result_files = list(ALLURE_RESULTS_DIR.glob("*.json"))
    print(f"📊 找到 {len(result_files)} 个 Allure 结果文件")

    if not result_files:
        print("❌ Allure 结果目录为空")
        return await get_report_json(task_id)

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
        print(f"🔧 执行命令: {' '.join(cmd)}")

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        print(f"📝 返回码: {result.returncode}")
        if result.stdout:
            print(f"📤 标准输出: {result.stdout[:500]}")
        if result.stderr:
            print(f"⚠️ 标准错误: {result.stderr[:500]}")

        if result.returncode == 0 and task_index.exists():
            print(f"✅ 报告生成成功: {task_index}")
            return FileResponse(task_index, media_type="text/html")
        else:
            print(f"❌ 报告生成失败: {result.stderr}")
            return await get_report_json(task_id)
    except subprocess.TimeoutExpired:
        print("❌ 报告生成超时")
        return JSONResponse(content={
            "error": "报告生成超时",
            "task_id": task_id,
            "message": "⏰ Allure 报告生成超时"
        })
    except FileNotFoundError as e:
        print(f"❌ Allure 命令未找到: {e}")
        return JSONResponse(content={
            "error": "Allure 命令未找到",
            "task_id": task_id,
            "message": "❌ 请确保 Allure 已安装并添加到 PATH 中"
        })
    except Exception as e:
        print(f"❌ 报告生成异常: {e}")
        return JSONResponse(content={
            "error": str(e),
            "task_id": task_id,
            "message": f"❌ 报告生成异常: {str(e)}"
        })


@router.get("/{task_id}/assets/{filename:path}")
async def get_report_asset(task_id: str, filename: str):
    """获取 Allure 报告的静态资源文件"""
    task_report_dir = TASK_REPORTS_DIR / task_id
    asset_file = task_report_dir / "assets" / filename

    if asset_file.exists():
        return FileResponse(asset_file)

    # 尝试从全局报告目录查找
    global_asset = ALLURE_REPORT_DIR / "assets" / filename
    if global_asset.exists():
        return FileResponse(global_asset)

    raise HTTPException(status_code=404, detail="资源文件不存在")


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

        if total == 0:
            match = re.search(r"===.*?(\d+)\s+passed.*?(\d+)\s+failed.*?(\d+)\s+skipped", stdout, re.DOTALL)
            if match:
                passed = int(match.group(1))
                failed = int(match.group(2))
                skipped = int(match.group(3))
                total = passed + failed + skipped

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
        "html_available": True,
        "html_url": f"/api/report/{task_id}",
        "allure_results_exists": allure_exists,
        "message": "📊 测试报告数据"
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
                "report_url": f"/api/report/{task_id}",
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