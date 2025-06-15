#!/bin/bash
# 开发环境启动脚本

set -e

echo "🚀 启动开发环境..."

# 检查 UV 是否安装
if ! command -v uv &> /dev/null; then
    echo "❌ UV 未安装，请先安装 UV"
    echo "💡 安装命令: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# 安装依赖
echo "📦 安装依赖..."
uv sync --extra dev

# 启动开发服务器
echo "🌟 启动开发服务器..."
uv run uvicorn --reload --host 0.0.0.0 --port 8000
