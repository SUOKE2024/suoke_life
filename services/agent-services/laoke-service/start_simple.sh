#!/bin/bash

# 老克智能体服务简化启动脚本

set -e

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# 切换到项目根目录
cd "$PROJECT_ROOT"

echo "🚀 启动老克智能体服务..."

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：Python3未安装"
    exit 1
fi

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv .venv
fi

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source .venv/bin/activate

# 安装基本依赖
echo "📦 安装依赖..."
pip install --upgrade pip
pip install fastapi uvicorn pydantic loguru pyyaml openai aiohttp

# 设置环境变量
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
export SERVICE__ENVIRONMENT="development"
export SERVICE__DEBUG="true"

# 检查配置文件
if [ ! -f "config/config.yaml" ]; then
    echo "⚠️  警告：未找到配置文件，使用默认配置"
fi

# 启动服务
echo "🎯 启动老克智能体服务..."
echo "📍 项目路径: $PROJECT_ROOT"
echo "🐍 Python版本: $(python --version)"
echo "⚙️  环境: $SERVICE__ENVIRONMENT"
echo "🔗 服务地址: http://localhost:8080"
echo ""

# 启动主服务
python main.py "$@"
