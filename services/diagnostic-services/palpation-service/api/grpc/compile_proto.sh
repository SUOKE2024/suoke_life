#!/bin/bash

# 编译 gRPC proto 文件脚本

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}开始编译切诊服务 Proto 文件...${NC}"

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SERVICE_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

# 检查是否安装了必要的工具
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到 python3${NC}"
    exit 1
fi

if ! python3 -c "import grpc_tools" &> /dev/null; then
    echo -e "${YELLOW}警告: 未安装 grpcio-tools，正在安装...${NC}"
    pip3 install grpcio-tools
fi

# 创建输出目录（如果不存在）
mkdir -p "$SCRIPT_DIR"

# 编译 proto 文件
echo -e "${GREEN}编译 palpation_service.proto...${NC}"

python3 -m grpc_tools.protoc \
    -I"$SCRIPT_DIR" \
    --python_out="$SCRIPT_DIR" \
    --grpc_python_out="$SCRIPT_DIR" \
    "$SCRIPT_DIR/palpation_service.proto"

# 检查编译结果
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Proto 文件编译成功！${NC}"
    echo -e "${GREEN}生成的文件：${NC}"
    echo "  - palpation_service_pb2.py"
    echo "  - palpation_service_pb2_grpc.py"
    
    # 修复导入路径问题（如果有）
    if [ -f "$SCRIPT_DIR/palpation_service_pb2_grpc.py" ]; then
        # 在 macOS 上使用 sed 的兼容写法
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' 's/import palpation_service_pb2/from . import palpation_service_pb2/g' "$SCRIPT_DIR/palpation_service_pb2_grpc.py"
        else
            sed -i 's/import palpation_service_pb2/from . import palpation_service_pb2/g' "$SCRIPT_DIR/palpation_service_pb2_grpc.py"
        fi
        echo -e "${GREEN}已修复导入路径${NC}"
    fi
else
    echo -e "${RED}Proto 文件编译失败！${NC}"
    exit 1
fi

echo -e "${GREEN}编译完成！${NC}" 