#!/bin/bash

# 生成gRPC Python代码的脚本

# 确保当前目录是项目根目录
cd "$(dirname "$0")/.." || exit

# 输出目录
OUTPUT_DIR="api"
mkdir -p "$OUTPUT_DIR"

# 定义proto文件路径
PROTO_PATH="api/grpc"

# 检查python-grpc-tools是否安装
if ! python -c "import grpc_tools.protoc" &> /dev/null; then
    echo "未找到grpc_tools，正在安装..."
    pip install grpcio-tools
fi

# 生成Python代码
echo "正在从${PROTO_PATH}生成Python gRPC代码..."
python -m grpc_tools.protoc \
    --proto_path="$PROTO_PATH" \
    --python_out="$OUTPUT_DIR" \
    --grpc_python_out="$OUTPUT_DIR" \
    "$PROTO_PATH"/*.proto

# 创建__init__.py文件
touch "$OUTPUT_DIR/__init__.py"

echo "代码生成完成！"