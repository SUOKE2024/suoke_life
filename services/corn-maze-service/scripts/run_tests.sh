#!/bin/bash

# 测试脚本

# 确保当前目录是项目根目录
cd "$(dirname "$0")/.." || exit

# 检查Python虚拟环境
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov

# 生成gRPC代码
echo "生成gRPC代码..."
./scripts/generate_protos.sh

# 设置测试环境变量
export SERVICE_ENV=test
export LOG_LEVEL=DEBUG
export DB_PATH=:memory:

# 运行测试
echo "运行测试..."
python -m pytest test -v --cov=internal --cov=pkg

# 退出时取消激活虚拟环境
deactivate