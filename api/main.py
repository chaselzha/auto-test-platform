# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path
import os

# 导入路由
from api.routers import test, report

# 创建 FastAPI 应用
app = FastAPI(
    title="自动化测试平台 API",
    description="基于 Pytest + Selenium 的自动化测试平台",
    version="2.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(test.router, prefix="/api/test", tags=["测试任务"])
app.include_router(report.router, prefix="/api/report", tags=["测试报告"])

# ===== 挂载静态文件目录 =====
# 1. 挂载前端静态文件
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    print(f"✅ 前端静态文件目录已挂载: {static_dir}")

# 2. 挂载任务报告目录（Allure 报告）
task_reports_dir = Path(__file__).parent.parent / "task-reports"
if task_reports_dir.exists():
    app.mount("/task-reports", StaticFiles(directory=str(task_reports_dir)), name="task_reports")
    print(f"✅ 任务报告目录已挂载: {task_reports_dir}")
else:
    # 如果目录不存在，创建它
    task_reports_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ 已创建任务报告目录: {task_reports_dir}")
    app.mount("/task-reports", StaticFiles(directory=str(task_reports_dir)), name="task_reports")

# 3. 挂载 allure-report 目录（可选，兼容旧的报告路径）
allure_report_dir = Path(__file__).parent.parent / "automation" / "reports" / "allure-report"
if allure_report_dir.exists():
    app.mount("/allure-report", StaticFiles(directory=str(allure_report_dir)), name="allure_report")
    print(f"✅ Allure 报告目录已挂载: {allure_report_dir}")


@app.get("/", response_class=HTMLResponse)
async def root():
    """根路径 - 返回前端页面"""
    html_file = Path(__file__).parent / "static" / "index.html"
    if html_file.exists():
        with open(html_file, "r", encoding="utf-8") as f:
            return f.read()
    return """
    <html>
        <head>
            <title>自动化测试平台</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                h1 { color: #667eea; }
                a { color: #667eea; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h1>🚀 自动化测试平台 API</h1>
            <p>访问 <a href="/docs">/docs</a> 查看 API 文档</p>
            <p>访问 <a href="/api/test/tasks">/api/test/tasks</a> 查看任务列表</p>
            <p>访问 <a href="/task-reports">/task-reports</a> 查看报告目录</p>
        </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "message": "自动化测试平台运行正常",
        "version": "2.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )