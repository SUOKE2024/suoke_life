#!/bin/bash
# 启动测试环境

set -e

echo "启动测试环境..."

# 检查docker-compose配置文件是否存在
if [ ! -f "test/docker-compose.test.yml" ]; then
    echo "错误: 未找到docker-compose配置文件"
    exit 1
fi

# 关闭可能正在运行的容器
echo "关闭旧的测试容器..."
docker-compose -f test/docker-compose.test.yml down || true

# 启动测试服务
echo "启动测试服务..."
docker-compose -f test/docker-compose.test.yml up -d

# 等待服务就绪
echo "等待服务就绪..."
sleep 5

# 初始化测试数据库
echo "初始化测试数据库..."
./test/init_test_db.sh

echo "测试环境已准备完毕!"
echo "PostgreSQL: localhost:5433"
echo "Redis: localhost:6380"
