#!/bin/bash
# 索克生活无障碍服务环境激活脚本

echo "🚀 激活索克生活无障碍服务开发环境..."

# 激活虚拟环境
source .venv/bin/activate

# 设置环境变量
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export ACCESSIBILITY_SERVICE_ENV="development"

echo "✅ 环境已激活"
echo "💡 使用 'deactivate' 命令退出环境"

# 显示Python和包信息
echo ""
echo "🐍 Python版本: $(python --version)"
echo "📦 pip版本: $(pip --version)"
echo "🔧 UV版本: $(uv --version)"
