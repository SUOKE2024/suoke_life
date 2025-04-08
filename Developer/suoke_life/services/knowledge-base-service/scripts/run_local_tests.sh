#!/bin/bash
set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}====== 索克生活知识库服务本地测试脚本 ======${NC}"

# 确保工作目录是项目根目录
cd "$(dirname "$0")/.."

# 验证Go安装
if ! command -v go &> /dev/null; then
    echo -e "${RED}错误: Go未安装，请安装Go 1.24或更高版本${NC}"
    exit 1
fi

# 检查PostgreSQL容器
echo -e "${YELLOW}=> 检查PostgreSQL容器状态...${NC}"
if ! docker ps | grep -q "kb-postgres"; then
    echo -e "${RED}PostgreSQL容器未运行，请先启动容器:${NC}"
    echo -e "  docker-compose up -d postgres"
    exit 1
fi

# 设置环境变量
echo -e "${YELLOW}=> 设置测试环境变量...${NC}"
export DB_CONNECTION_STRING="postgres://postgres:postgres@localhost:5432/knowledge_base_test?sslmode=disable"
export VECTOR_STORE_USE_MOCK="true"
export EMBEDDING_MODEL_URL="http://localhost:8000/embed"

# 创建测试数据库
echo -e "${YELLOW}=> 检查测试数据库...${NC}"
if ! docker exec kb-postgres psql -U postgres -lqt | grep -q "knowledge_base_test"; then
    echo -e "${YELLOW}创建测试数据库...${NC}"
    docker exec kb-postgres psql -U postgres -c "CREATE DATABASE knowledge_base_test;"
fi

# 跳过单元测试，直接运行基准测试
echo -e "${YELLOW}=> 跳过单元测试，直接运行基准测试...${NC}"

# 运行基本的存储库测试
echo -e "${YELLOW}=> 运行存储库基准测试...${NC}"
mkdir -p ./benchmark_results
go test -bench=DocRepo ./internal/test/benchmark/real/ | tee ./benchmark_results/repository_bench.txt

echo -e "${GREEN}测试完成!${NC}" 