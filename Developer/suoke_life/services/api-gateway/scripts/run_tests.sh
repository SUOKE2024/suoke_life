#!/bin/bash

# API网关服务测试执行脚本

# 显示彩色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

echo -e "${BLUE}===========================================${NC}"
echo -e "${BLUE}   API网关服务测试执行脚本   ${NC}"
echo -e "${BLUE}===========================================${NC}"

# 确保在项目根目录
cd "$(dirname "$0")/.." || exit 1
PROJECT_ROOT=$(pwd)

# 显示当前位置
echo -e "${GREEN}当前工作目录:${NC} $PROJECT_ROOT"
echo

# 1. 检查依赖
echo -e "${YELLOW}[1/5] 检查和更新依赖${NC}"
go mod tidy
if [ $? -ne 0 ]; then
    echo -e "${RED}依赖检查失败，请解决模块导入问题后再试。${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 依赖检查完成${NC}"
echo

# 2. 运行单元测试
echo -e "${YELLOW}[2/5] 运行单元测试${NC}"

echo -e "${BLUE}测试中间件模块...${NC}"
go test -v ./internal/middleware
echo

echo -e "${BLUE}测试代理模块...${NC}"
go test -v ./internal/proxy
echo

echo -e "${BLUE}测试服务发现模块...${NC}"
go test -v ./internal/discovery
echo

echo -e "${BLUE}测试配置模块...${NC}"
go test -v ./internal/config
echo

echo -e "${BLUE}测试服务器模块...${NC}"
go test -v ./internal/server
echo

# 3. 生成测试覆盖率报告
echo -e "${YELLOW}[3/5] 生成测试覆盖率报告${NC}"
mkdir -p coverage
go test -coverprofile=coverage/coverage.out ./internal/...
go tool cover -html=coverage/coverage.out -o coverage/coverage.html
echo -e "${GREEN}✓ 测试覆盖率报告已生成：coverage/coverage.html${NC}"
echo

# 4. 运行集成测试（如果存在）
echo -e "${YELLOW}[4/5] 运行集成测试${NC}"
if [ -d "./test/integration" ]; then
    go test -v -tags=integration ./test/integration/...
    echo -e "${GREEN}✓ 集成测试完成${NC}"
else
    echo -e "${BLUE}集成测试目录不存在，跳过${NC}"
fi
echo

# 5. 性能基准测试
echo -e "${YELLOW}[5/5] 运行性能基准测试${NC}"
echo -e "${BLUE}测试中间件模块性能...${NC}"
go test -v -bench=. ./internal/middleware -benchmem
echo

echo -e "${BLUE}测试代理模块性能...${NC}"
go test -v -bench=. ./internal/proxy -benchmem
echo

# 测试结果摘要
echo -e "${GREEN}===========================================${NC}"
echo -e "${GREEN}   测试执行完成   ${NC}"
echo -e "${GREEN}===========================================${NC}"
echo -e "${BLUE}测试结果位置:${NC}"
echo -e "  - 测试覆盖率报告: $PROJECT_ROOT/coverage/coverage.html"
echo -e "  - 测试日志: $PROJECT_ROOT/test-results"
echo

exit 0 