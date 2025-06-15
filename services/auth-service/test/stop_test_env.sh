#!/bin/bash
# 停止测试环境

echo "停止测试环境..."

# 检查docker-compose配置文件是否存在
if [ ! -f "test/docker-compose.test.yml" ]; then
    echo "错误: 未找到docker-compose配置文件"
    exit 1
fi

# 关闭容器
docker-compose -f test/docker-compose.test.yml down

echo "测试环境已停止"
