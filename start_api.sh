cd /Users/chasel/PycharmProjects/auto-test-platform

# 创建 start_api.sh
cat > start_api.sh << 'EOF'
#!/bin/bash
# start_api.sh
# FastAPI 自动化测试平台启动脚本

echo "========================================="
echo "🚀 自动化测试平台 API"
echo "========================================="
echo ""
echo "📂 项目目录: $(pwd)"
echo ""

# 检查虚拟环境
if [ -d ".venv" ]; then
    echo "✅ 激活虚拟环境..."
    source .venv/bin/activate
fi

# 设置 Python 路径
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 检查依赖
echo ""
echo "📦 检查依赖..."
python3 -c "import fastapi" 2>/dev/null || {
    echo "⚠️ FastAPI 未安装，正在安装..."
    pip install fastapi uvicorn[standard] aiofiles sqlalchemy aiosqlite
}

echo ""
echo "========================================="
echo "✅ 启动 FastAPI 服务..."
echo "========================================="
echo ""
echo "🌐 Web 界面: http://localhost:8000"
echo "📚 API 文档: http://localhost:8000/docs"
echo "💚 健康检查: http://localhost:8000/health"
echo ""
echo "按 Ctrl+C 停止服务"
echo "========================================="

# 启动服务
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
EOF

# 添加执行权限
chmod +x start_api.sh