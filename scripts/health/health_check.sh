#!/bin/bash

# 索克生活 - 健康检查脚本

echo "🔍 开始健康检查..."

# 检查API网关
echo "检查API网关..."
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ API网关正常"
else
    echo "❌ API网关异常"
    exit 1
fi

# 检查数据库
echo "检查数据库..."
if pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "✅ 数据库正常"
else
    echo "❌ 数据库异常"
    exit 1
fi

# 检查Redis
echo "检查Redis..."
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis正常"
else
    echo "❌ Redis异常"
    exit 1
fi

echo "🎉 所有服务健康检查通过！"
