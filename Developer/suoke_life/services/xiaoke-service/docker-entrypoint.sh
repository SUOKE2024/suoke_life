#!/bin/sh
set -e

# 等待依赖服务准备就绪
wait_for_service() {
  echo "Waiting for $1 at $2..."
  until nc -z $2 $3; do
    echo "Waiting for $1 at $2:$3..."
    sleep 2
  done
  echo "$1 is available!"
}

# 检查必要的环境变量
if [ -z "$MONGODB_URI" ]; then
  echo "Error: MONGODB_URI environment variable is not set"
  exit 1
fi

# 等待MongoDB准备就绪
MONGO_HOST=$(echo $MONGODB_URI | sed -n 's/.*@\(.*\):.*/\1/p')
MONGO_PORT=$(echo $MONGODB_URI | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
if [ ! -z "$MONGO_HOST" ] && [ ! -z "$MONGO_PORT" ]; then
  wait_for_service "MongoDB" $MONGO_HOST $MONGO_PORT
fi

# 等待Redis准备就绪
if [ ! -z "$REDIS_HOST" ] && [ ! -z "$REDIS_PORT" ]; then
  wait_for_service "Redis" $REDIS_HOST $REDIS_PORT
fi

# 创建必要的目录
mkdir -p /app/data /app/logs /app/cache

# 设置目录权限
if [ "$(id -u)" = "0" ]; then
  chown -R xiaoke:xiaoke /app/data /app/logs /app/cache
fi

# 打印服务信息
echo "Starting xiaoke-service..."
echo "Node.js version: $(node -v)"
echo "NPM version: $(npm -v)"
echo "Environment: $NODE_ENV"

# 执行命令
exec "$@" 