#!/bin/bash

# 认证服务启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 启动索克生活认证服务...${NC}"

# 检查环境变量
if [ -z "$DATABASE_URL" ]; then
    echo -e "${YELLOW}⚠️  DATABASE_URL 未设置，使用默认值${NC}"
    export DATABASE_URL="postgresql+asyncpg://auth_user:auth_pass@localhost:5432/auth_db"
fi

if [ -z "$REDIS_URL" ]; then
    echo -e "${YELLOW}⚠️  REDIS_URL 未设置，使用默认值${NC}"
    export REDIS_URL="redis://localhost:6379/0"
fi

if [ -z "$JWT_SECRET_KEY" ]; then
    echo -e "${YELLOW}⚠️  JWT_SECRET_KEY 未设置，生成随机密钥${NC}"
    export JWT_SECRET_KEY=$(openssl rand -hex 32)
fi

# 设置Python路径
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 运行数据库迁移
echo -e "${GREEN}📊 运行数据库迁移...${NC}"
if command -v alembic &> /dev/null; then
    alembic upgrade head
else
    echo -e "${YELLOW}⚠️  Alembic 未安装，跳过数据库迁移${NC}"
fi

# 启动服务
echo -e "${GREEN}🌟 启动认证服务...${NC}"
echo -e "${GREEN}📍 服务地址: http://localhost:8000${NC}"
echo -e "${GREEN}📖 API文档: http://localhost:8000/docs${NC}"

# 根据环境选择启动方式
if [ "$ENVIRONMENT" = "production" ]; then
    echo -e "${GREEN}🏭 生产环境启动${NC}"
    exec uvicorn auth_service.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --workers 4 \
        --access-log \
        --log-level info
else
    echo -e "${GREEN}🔧 开发环境启动${NC}"
    exec uvicorn auth_service.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --reload \
        --log-level debug
fi 