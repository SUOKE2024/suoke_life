#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}===== 配置PostgreSQL测试用户和权限 =====${NC}"

# 检查PostgreSQL容器是否运行
if ! docker ps | grep -q "kb-postgres"; then
    echo -e "${RED}PostgreSQL容器未运行，请先执行:${NC}"
    echo -e "docker-compose up -d postgres"
    exit 1
fi

# 用户名和密码
TEST_USER="testuser"
TEST_PASSWORD="testpassword"
TEST_DB="knowledge_base_test"

# 确保测试数据库存在
echo -e "${YELLOW}确保测试数据库存在...${NC}"
if ! docker exec kb-postgres psql -U postgres -lqt | grep -q "$TEST_DB"; then
    echo -e "${YELLOW}创建数据库 $TEST_DB...${NC}"
    docker exec kb-postgres psql -U postgres -c "CREATE DATABASE $TEST_DB;"
fi

# 创建测试用户并授予权限
echo -e "${YELLOW}配置测试用户...${NC}"

# 检查用户是否存在
if docker exec kb-postgres psql -U postgres -c "SELECT 1 FROM pg_roles WHERE rolname='$TEST_USER';" | grep -q "1"; then
    echo -e "${YELLOW}用户 $TEST_USER 已存在，正在重新配置权限...${NC}"
    # 重置密码
    docker exec kb-postgres psql -U postgres -c "ALTER USER $TEST_USER WITH PASSWORD '$TEST_PASSWORD';"
else
    echo -e "${YELLOW}创建用户 $TEST_USER...${NC}"
    docker exec kb-postgres psql -U postgres -c "CREATE USER $TEST_USER WITH PASSWORD '$TEST_PASSWORD';"
fi

# 授予数据库权限
echo -e "${YELLOW}授予 $TEST_USER 对 $TEST_DB 的所有权限...${NC}"
docker exec kb-postgres psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $TEST_DB TO $TEST_USER;"

# 授予特定模式的权限
echo -e "${YELLOW}授予 $TEST_USER 对 $TEST_DB 中所有表的权限...${NC}"
docker exec kb-postgres psql -U postgres -d "$TEST_DB" -c "GRANT ALL PRIVILEGES ON SCHEMA public TO $TEST_USER;"
docker exec kb-postgres psql -U postgres -d "$TEST_DB" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO $TEST_USER;"
docker exec kb-postgres psql -U postgres -d "$TEST_DB" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO $TEST_USER;"

# 修改pg_hba.conf以允许md5认证
echo -e "${YELLOW}配置pg_hba.conf允许密码认证...${NC}"
docker exec kb-postgres sh -c "echo 'host all $TEST_USER 0.0.0.0/0 md5' >> /var/lib/postgresql/data/pg_hba.conf"
docker exec kb-postgres sh -c "echo 'host all $TEST_USER 127.0.0.1/32 md5' >> /var/lib/postgresql/data/pg_hba.conf"

# 重新加载PostgreSQL配置
echo -e "${YELLOW}重新加载PostgreSQL配置...${NC}"
docker exec kb-postgres psql -U postgres -c "SELECT pg_reload_conf();"

# 测试连接
echo -e "${YELLOW}测试连接...${NC}"
TEST_CONN_STRING="postgresql://$TEST_USER:$TEST_PASSWORD@localhost:5432/$TEST_DB"
echo -e "${YELLOW}连接字符串: $TEST_CONN_STRING${NC}"

# 显示用于测试的环境变量设置
echo -e "${GREEN}设置以下环境变量用于测试:${NC}"
echo -e "export DB_CONNECTION_STRING=\"$TEST_CONN_STRING\""
echo -e "export VECTOR_STORE_USE_MOCK=\"true\""

echo -e "${GREEN}用户和权限配置完成!${NC}" 