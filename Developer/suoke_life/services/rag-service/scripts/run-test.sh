#!/bin/bash

# 定义彩色输出
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}===== 索克生活RAG服务测试脚本 =====${NC}"
echo -e "${YELLOW}开始时间: $(date)${NC}"

# 检查是否在正确的目录
if [ ! -d "tests" ]; then
    echo -e "${RED}错误: 请在项目根目录下运行此脚本${NC}"
    exit 1
fi

# 构建测试工具
echo -e "${YELLOW}构建测试工具...${NC}"
(cd tests && go build -o ../bin/simple_test simple_test.go)

if [ $? -ne 0 ]; then
    echo -e "${RED}构建测试工具失败${NC}"
    exit 1
fi

# 运行测试
echo -e "${YELLOW}运行测试...${NC}"
mkdir -p bin

# 1. 简单文本查询测试
echo -e "${GREEN}测试1: 简单文本查询${NC}"
./bin/simple_test -query "感冒的中医治疗方法" -mode "text"

echo
echo -e "${GREEN}===== 测试完成 =====${NC}"
echo -e "${YELLOW}完成时间: $(date)${NC}" 