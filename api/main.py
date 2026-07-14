# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path
import os

# 导入路由
from api.routers import test, report
from api.config.settings import settings

# 创建 FastAPI 应用
app = FastAPI(
    title="自动化测试平台 API",
    description="""
## 🚀 自动化测试平台 API

### 🔐 认证方式
所有 API 都需要在请求头中添加 `X-API-Key`：

### 📋 获取 API Key
请联系管理员获取 API Key

### 🌐 公开接口（无需认证）
- `GET /api/test/public/health` - 健康检查
- `GET /` - 前端页面
- `GET /docs` - API 文档
- `GET /health` - 服务健康检查

### 📊 接口列表
- **测试任务**：`/api/test/*`
- **测试报告**：`/api/report/*`
""",
    version="2.0.0"
)

# CORS 配置 - 使用 add_middleware 的正确方式
app.add_middleware( # type: ignore
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

    # 如果 index.html 不存在，返回这个简单的页面
    html_content = """<!DOCTYPE html>
<html>
    <head>
        <title>自动化测试平台</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Seg
                oe UI", Roboto, Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .container {
                background: white;
                border-radius: 20px;
                padding: 60px 80px;
                max-width: 700px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                text-align: center;
            }
            h1 {
                font-size: 36px;
                color: #333;
                margin-bottom: 10px;
            }
            .subtitle {
                color: #888;
                font-size: 16px;
                margin-bottom: 30px;
            }
            .auth-info {
                background: #f8f9fa;
                border-radius: 12px;
                padding: 20px;
                margin: 20px 0 30px;
                text-align: left;
                border-left: 4px solid #667eea;
            }
            .auth-info label {
                font-weight: 600;
                color: #555;
                display: block;
                margin-bottom: 5px;
            }
            .auth-info code {
                background: #e9ecef;
                padding: 4px 12px;
                border-radius: 6px;
                font-size: 14px;
                color: #333;
                display: inline-block;
                margin-top: 4px;
            }
            .auth-info .note {
                font-size: 13px;
                color: #888;
                margin-top: 8px;
            }
            .links {
                display: flex;
                gap: 20px;
                justify-content: center;
                flex-wrap: wrap;
            }
            .links a {
                display: inline-block;
                padding: 12px 30px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                transition: all 0.3s;
            }
            .links a:hover {
                background: #5a6fd6;
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
            }
            .links a.secondary {
                background: #6c757d;
            }
            .links a.secondary:hover {
                background: #5a6268;
                box-shadow: 0 8px 20px rgba(108, 117, 125, 0.4);
            }
            .footer {
                margin-top: 30px;
                color: #aaa;
                font-size: 13px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 自动化测试平台</h1>
            <p class="subtitle">基于 Pytest + Selenium + Allure</p>

            <div class="auth-info">
                <label>🔐 API 认证信息</label>
                <div style="margin-top: 8px;">
                    <strong>Header:</strong> <code>""" + settings.API_KEY_HEADER + """</code>
                    <br>
                    <strong>API Key:</strong> <code>""" + settings.API_KEY + """</code>
                </div>
                <div class="note">
                    💡 所有 API 请求需要在 Header 中添加以上认证信息
                    <br>
                    <span style="font-size: 12px; color: #aaa;">认证信息可在 <code>.env</code> 文件中配置</span>
                </div>
            </div>

            <div class="links">
                <a href="/docs" target="_blank">📖 API 文档</a>
                <a href="/api/test/public/health" target="_blank" class="secondary">❤️ 健康检查</a>
            </div>

            <div class="footer">
                ⚡ """ + settings.API_HOST + ":" + str(settings.API_PORT) + """ | 认证: """ + (
        "✅ 已启用" if settings.AUTH_ENABLED else "❌ 已禁用") + """
            </div>
        </div>
    </body>
</html>"""

    return HTMLResponse(content=html_content)


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "message": "自动化测试平台运行正常",
        "version": "2.0.0",
        "auth_enabled": settings.AUTH_ENABLED
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("API_PORT", settings.API_PORT))
    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=port,
        reload=True
    )