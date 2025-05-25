#!/bin/bash

# 切诊服务启动脚本

# 设置脚本目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# 设置Python路径
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# 设置默认配置文件路径
export CONFIG_PATH="${CONFIG_PATH:-$PROJECT_ROOT/config/config.yaml}"

# 检查配置文件是否存在
if [ ! -f "$CONFIG_PATH" ]; then
    echo "错误: 配置文件不存在: $CONFIG_PATH"
    exit 1
fi

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3"
    exit 1
fi

# 检查依赖
echo "检查依赖..."
python3 -c "import grpc" 2>/dev/null || {
    echo "错误: 未安装grpcio，请运行: pip install -r requirements.txt"
    exit 1
}

# 编译proto文件（如果需要）
if [ ! -f "$PROJECT_ROOT/api/grpc/palpation_service_pb2.py" ]; then
    echo "编译proto文件..."
    cd "$PROJECT_ROOT/api/grpc"
    bash compile_proto.sh
    cd "$PROJECT_ROOT"
fi

# 启动服务器
echo "启动切诊服务..."
echo "配置文件: $CONFIG_PATH"
echo "监听端口: ${GRPC_PORT:-50051}"
echo ""

# 运行服务器
exec python3 "$PROJECT_ROOT/cmd/server/main.py"