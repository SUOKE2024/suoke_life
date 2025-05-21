#!/bin/bash

# 开发环境启动脚本

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

# 生成gRPC代码
echo "生成gRPC代码..."
./scripts/generate_protos.sh

# 创建必要的目录
mkdir -p logs data

# 设置开发环境变量
export SERVICE_ENV=development
export LOG_LEVEL=DEBUG
export GRPC_PORT=50057
export METRICS_PORT=51057
export DB_PATH=data/maze.db

# 启动服务
echo "启动Corn Maze Service..."
python -m cmd.server

# 退出时取消激活虚拟环境
deactivate