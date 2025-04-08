#!/bin/bash

# 设置终端颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # 无颜色

echo -e "${YELLOW}索克生活微服务开发环境启动脚本${NC}"

# 检查Redis是否运行
echo -e "${YELLOW}检查Redis服务...${NC}"
if ! redis-cli ping > /dev/null 2>&1; then
    echo -e "${RED}Redis未运行，正在启动...${NC}"
    brew services start redis
    sleep 2
    if ! redis-cli ping > /dev/null 2>&1; then
        echo -e "${RED}Redis启动失败，请手动检查${NC}"
        exit 1
    fi
    echo -e "${GREEN}Redis服务已启动${NC}"
else
    echo -e "${GREEN}Redis服务已运行${NC}"
fi

# 询问MySQL连接信息
echo -e "${YELLOW}请输入MySQL连接信息:${NC}"
read -p "用户名 [root]: " MYSQL_USER
MYSQL_USER=${MYSQL_USER:-root}
read -p "是否需要密码? (y/n) [n]: " NEEDS_PASSWORD
NEEDS_PASSWORD=${NEEDS_PASSWORD:-n}

if [[ "$NEEDS_PASSWORD" =~ ^[Yy]$ ]]; then
    read -s -p "密码: " MYSQL_PASSWORD
    echo ""  # 换行
    MYSQL_PASSWORD_ARG="-p'$MYSQL_PASSWORD'"
    MYSQL_ADMIN_ARG="-p$MYSQL_PASSWORD"
else
    MYSQL_PASSWORD=""
    MYSQL_PASSWORD_ARG=""
    MYSQL_ADMIN_ARG=""
fi

# 检查MySQL是否运行
echo -e "${YELLOW}检查MySQL服务...${NC}"
MYSQL_CHECK=$(mysqladmin ping -h127.0.0.1 -u$MYSQL_USER $MYSQL_ADMIN_ARG --silent 2>/dev/null || echo "Failed")

if [[ "$MYSQL_CHECK" == "Failed" ]]; then
    echo -e "${RED}MySQL连接失败，尝试启动本地MySQL...${NC}"
    brew services start mysql
    sleep 5
    MYSQL_CHECK=$(mysqladmin ping -h127.0.0.1 -u$MYSQL_USER $MYSQL_ADMIN_ARG --silent 2>/dev/null || echo "Failed")
    
    if [[ "$MYSQL_CHECK" == "Failed" ]]; then
        echo -e "${RED}MySQL连接仍然失败，请检查凭证或手动启动MySQL${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}MySQL服务已运行${NC}"

# 检查并创建索克生活数据库
echo -e "${YELLOW}检查数据库是否存在...${NC}"
DB_EXISTS=$(mysql -h127.0.0.1 -u$MYSQL_USER $MYSQL_PASSWORD_ARG -e "SHOW DATABASES LIKE 'suoke_db';" 2>/dev/null | grep -c "suoke_db" || echo "0")

if [ "$DB_EXISTS" -eq 0 ]; then
    echo -e "${YELLOW}创建索克生活数据库...${NC}"
    mysql -h127.0.0.1 -u$MYSQL_USER $MYSQL_PASSWORD_ARG -e "CREATE DATABASE suoke_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>/dev/null
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}数据库创建失败，请手动检查MySQL权限${NC}"
        exit 1
    fi
    echo -e "${GREEN}数据库创建成功${NC}"
else
    echo -e "${GREEN}数据库已存在${NC}"
fi

# 修改.env文件以使用正确的数据库连接信息
echo -e "${YELLOW}更新环境变量...${NC}"
sed -i '.bak' "s/^DB_USER=.*/DB_USER=$MYSQL_USER/" .env
sed -i '.bak' "s/^DB_PASSWORD=.*/DB_PASSWORD=$MYSQL_PASSWORD/" .env

# 启动开发环境容器
echo -e "${YELLOW}启动微服务容器...${NC}"
docker-compose -f docker-compose.dev.yml up --build -d

if [ $? -ne 0 ]; then
    echo -e "${RED}容器启动失败，请检查日志${NC}"
    exit 1
fi

echo -e "${GREEN}开发环境启动成功！${NC}"
echo -e "${YELLOW}API网关: http://localhost:${API_GATEWAY_PORT:-8080}${NC}"
echo -e "${YELLOW}认证服务: http://localhost:${AUTH_SERVICE_PORT:-8081}${NC}"
echo -e "${YELLOW}用户服务: http://localhost:${USER_SERVICE_PORT:-8082}${NC}"