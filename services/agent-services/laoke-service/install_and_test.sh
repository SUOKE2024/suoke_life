#!/bin/bash

# 老克智能体服务安装和测试脚本

set -e

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# 切换到项目根目录
cd "$PROJECT_ROOT"

echo "🚀 老克智能体服务安装和测试"
echo "=" * 60

# 检查Python
echo "🐍 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：Python3未安装"
    exit 1
fi
echo "✅ Python版本: $(python3 --version)"

# 创建虚拟环境
echo "📦 创建虚拟环境..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "✅ 虚拟环境创建成功"
else
    echo "✅ 虚拟环境已存在"
fi

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source .venv/bin/activate

# 升级pip
echo "🔄 升级pip..."
pip install --upgrade pip

# 安装核心依赖
echo "📦 安装核心依赖..."
pip install fastapi uvicorn pydantic pydantic-settings loguru pyyaml aiofiles aiohttp httpx openai anthropic

# 安装测试依赖
echo "📦 安装测试依赖..."
pip install pytest pytest-asyncio pytest-cov pytest-mock

# 安装无障碍服务依赖
echo "📦 安装无障碍服务依赖..."
pip install grpcio grpcio-tools protobuf

# 设置环境变量
echo "⚙️  设置环境变量..."
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
export SERVICE__ENVIRONMENT="development"
export SERVICE__DEBUG="true"
export MODELS__API_KEY="sk-test-key-for-development"

# 创建日志目录
echo "📁 创建日志目录..."
mkdir -p logs

# 运行启动测试
echo "📝 运行启动测试..."
echo "=" * 60
python test_startup.py

if [ $? -eq 0 ]; then
    echo "=" * 60
    echo "✅ 所有测试通过！服务已准备好启动。"
    echo ""
    echo "🚀 启动服务请运行："
    echo "   ./start_simple.sh"
    echo ""
    echo "📊 测试API请访问："
    echo "   http://localhost:8080/health"
    echo "   http://localhost:8080/"
    echo "   http://localhost:8080/stats"
    echo ""
    echo "📝 查看快速指南："
    echo "   cat QUICKSTART.md"
else
    echo "=" * 60
    echo "❌ 测试失败，请检查错误信息。"
    exit 1
fi
