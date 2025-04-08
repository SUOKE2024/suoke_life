#!/bin/bash
set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}====== 索克生活知识库服务文档存储库测试 ======${NC}"

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

# 获取PostgreSQL用户身份
echo -e "${YELLOW}=> 检查PostgreSQL用户...${NC}"
docker exec kb-postgres psql -U postgres -c "\du"

# 检查PostgreSQL数据库
echo -e "${YELLOW}=> 检查PostgreSQL数据库列表...${NC}"
docker exec kb-postgres psql -U postgres -c "\l"

# 获取PostgreSQL连接信息
echo -e "${YELLOW}=> 查看容器环境变量...${NC}"
docker exec kb-postgres env | grep POSTGRES_

# 设置环境变量 - 尝试使用localhost和简单格式
echo -e "${YELLOW}=> 设置测试环境变量...${NC}"
export DB_CONNECTION_STRING="postgresql://testuser:testpassword@localhost:5432/knowledge_base_test?sslmode=disable"
echo -e "${GREEN}连接字符串: $DB_CONNECTION_STRING${NC}"

# 创建测试数据库
echo -e "${YELLOW}=> 检查测试数据库...${NC}"
if ! docker exec kb-postgres psql -U postgres -lqt | grep -q "knowledge_base_test"; then
    echo -e "${YELLOW}创建测试数据库...${NC}"
    docker exec kb-postgres psql -U postgres -c "CREATE DATABASE knowledge_base_test;"
fi

# 运行测试
echo -e "${YELLOW}=> 运行PostgreSQL文档存储库测试...${NC}"
go test -v ./internal/infrastructure/repository/... 