# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

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


@app.get("/", response_class=HTMLResponse)
async def root():
    """根路径 - 返回前端页面"""
    html_file = Path(__file__).parent / "static" / "index.html"
    if html_file.exists():
        with open(html_file, "r", encoding="utf-8") as f:
            return f.read()
    return """
    <html>
        <head><title>自动化测试平台</title></head>
        <body>
            <h1>🚀 自动化测试平台 API</h1>
            <p>访问 <a href="/docs">/docs</a> 查看 API 文档</p>
        </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "message": "自动化测试平台运行正常"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )