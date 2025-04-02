#!/bin/sh
set -e

# 打印启动信息
echo "正在启动玉米迷宫服务..."
echo "环境: $NODE_ENV"
echo "监听端口: $PORT"
echo "WebSocket端口: $WS_PORT"

# 等待数据库连接
if [ ! -z "$MONGODB_URI" ]; then
  echo "等待数据库连接..."
  MONGO_HOST=$(echo $MONGODB_URI | sed -n 's/.*@\([^:]*\).*/\1/p')
  
  if [ ! -z "$MONGO_HOST" ]; then
    until nc -z $MONGO_HOST 27017; do
      echo "MongoDB还未就绪 - 等待..."
      sleep 2
    done
    echo "MongoDB连接已就绪"
  fi
fi

# 等待Redis连接
if [ ! -z "$REDIS_URL" ]; then
  echo "等待Redis连接..."
  REDIS_HOST=$(echo $REDIS_URL | sed -n 's/.*@\([^:]*\).*/\1/p')
  if [ -z "$REDIS_HOST" ]; then
    REDIS_HOST=$(echo $REDIS_URL | sed -n 's/.*redis:\/\/\([^:]*\).*/\1/p')
  fi
  
  if [ ! -z "$REDIS_HOST" ]; then
    until nc -z $REDIS_HOST 6379; do
      echo "Redis还未就绪 - 等待..."
      sleep 2
    done
    echo "Redis连接已就绪"
  fi
fi

# 执行命令
exec "$@" 