#!/bin/bash

# 索克生活 API 网关开发环境启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}🚀 启动索克生活 API 网关开发环境${NC}"
echo "项目目录: $PROJECT_ROOT"

# 检查 Python 版本
echo -e "\n${YELLOW}📋 检查环境...${NC}"
python_version=$(python --version 2>&1 | cut -d' ' -f2)
echo "Python 版本: $python_version"

# 检查虚拟环境
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}⚠️  未检测到虚拟环境，尝试激活...${NC}"
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
        echo -e "${GREEN}✅ 虚拟环境已激活${NC}"
    else
        echo -e "${RED}❌ 未找到虚拟环境，请先运行 scripts/setup.sh${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ 虚拟环境已激活: $VIRTUAL_ENV${NC}"
fi

# 检查依赖
echo -e "\n${YELLOW}📦 检查依赖...${NC}"
if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  依赖未安装，正在安装...${NC}"
    uv sync --dev
    echo -e "${GREEN}✅ 依赖安装完成${NC}"
else
    echo -e "${GREEN}✅ 依赖已安装${NC}"
fi

# 检查环境变量
echo -e "\n${YELLOW}🔧 检查配置...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  未找到 .env 文件，创建默认配置...${NC}"
    cat > .env << EOF
# 索克生活 API 网关配置

# 服务器配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
ENVIRONMENT=development
DEBUG=true

# 安全配置
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# 日志配置
LOG_LEVEL=INFO
LOG_FORMAT=json

# CORS 配置
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# 限流配置
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# 监控配置
METRICS_ENABLED=true
HEALTH_CHECK_ENABLED=true
EOF
    echo -e "${GREEN}✅ 默认配置已创建${NC}"
else
    echo -e "${GREEN}✅ 配置文件存在${NC}"
fi

# 检查 Redis 连接
echo -e "\n${YELLOW}🔍 检查 Redis 连接...${NC}"
if command -v redis-cli >/dev/null 2>&1; then
    if redis-cli ping >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Redis 连接正常${NC}"
    else
        echo -e "${YELLOW}⚠️  Redis 未运行，尝试启动...${NC}"
        if command -v brew >/dev/null 2>&1; then
            brew services start redis
        elif command -v systemctl >/dev/null 2>&1; then
            sudo systemctl start redis
        else
            echo -e "${RED}❌ 无法启动 Redis，请手动启动${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠️  Redis CLI 未安装，跳过连接检查${NC}"
fi

# 运行代码质量检查
echo -e "\n${YELLOW}🔍 运行代码质量检查...${NC}"
echo "运行 Ruff 检查..."
if uv run ruff check --fix; then
    echo -e "${GREEN}✅ Ruff 检查通过${NC}"
else
    echo -e "${YELLOW}⚠️  Ruff 检查发现问题，已自动修复${NC}"
fi

echo "运行 MyPy 类型检查..."
if uv run mypy suoke_api_gateway --ignore-missing-imports; then
    echo -e "${GREEN}✅ MyPy 检查通过${NC}"
else
    echo -e "${YELLOW}⚠️  MyPy 检查发现类型问题${NC}"
fi

# 启动服务
echo -e "\n${GREEN}🎯 启动 API 网关服务...${NC}"
echo "服务地址: http://localhost:8000"
echo "API 文档: http://localhost:8000/docs"
echo "健康检查: http://localhost:8000/health"
echo "指标监控: http://localhost:8000/metrics/prometheus"
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止服务${NC}"
echo ""

# 启动开发服务器
exec uv run uvicorn suoke_api_gateway.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --reload-dir suoke_api_gateway \
    --log-level info 