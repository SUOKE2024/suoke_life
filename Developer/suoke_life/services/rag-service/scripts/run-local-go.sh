#!/bin/bash

# 定义彩色输出
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}===== 索克生活RAG服务本地启动脚本 =====${NC}"
echo -e "${YELLOW}开始时间: $(date)${NC}"

# 检查是否在正确的目录
if [ ! -f "cmd/server/main.go" ]; then
    echo "错误: 请在项目根目录下运行此脚本"
    exit 1
fi

# 创建必要的目录
mkdir -p data logs config

# 运行服务
echo "构建并运行服务..."
go run cmd/server/main.go 