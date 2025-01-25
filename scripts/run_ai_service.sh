#!/bin/bash

# 确保在项目根目录
cd "$(dirname "$0")/.."

# 如果虚拟环境不存在，创建它
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# 激活虚拟环境
source .venv/bin/activate

# 如果需要，安装依赖
if ! python3 -c "import volcengine" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install 'volcengine-python-sdk[ark]'
fi

# 运行 AI 服务脚本
python3 scripts/ai_service.py 