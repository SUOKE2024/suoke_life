#!/bin/bash
set -e

# 打印启动信息
echo "启动用户服务 - User Service"
echo "NODE_ENV: $NODE_ENV"

# 检查必要的环境变量
required_vars=(
  "PORT"
  "REDIS_HOST"
  "REDIS_PORT"
  "JWT_SECRET"
  "LOG_LEVEL"
)

for var in "${required_vars[@]}"; do
  if [ -z "${!var}" ]; then
    echo "错误: 环境变量 $var 未设置"
    exit 1
  fi
done

# 等待Redis连接
echo "检查Redis连接..."
max_retries=30
count=0

until (exec 6<>/dev/tcp/${REDIS_HOST}/${REDIS_PORT}) 2>/dev/null; do
  echo "等待Redis可用... ($count/$max_retries)"
  sleep 2
  count=$((count+1))
  if [ $count -ge $max_retries ]; then
    echo "错误: 无法连接到Redis"
    exit 1
  fi
done
exec 6>&-
echo "Redis连接成功"

# 如果配置了MongoDB，等待MongoDB连接
if [ ! -z "$MONGODB_URI" ]; then
  echo "检查MongoDB连接..."
  max_retries=30
  count=0
  
  # 提取MongoDB主机和端口
  mongo_host=$(echo $MONGODB_URI | sed -e 's/.*@\(.*\):.*/\1/')
  mongo_port=$(echo $MONGODB_URI | sed -e 's/.*:\([0-9]*\).*/\1/')
  
  until (exec 6<>/dev/tcp/${mongo_host}/${mongo_port}) 2>/dev/null; do
    echo "等待MongoDB可用... ($count/$max_retries)"
    sleep 2
    count=$((count+1))
    if [ $count -ge $max_retries ]; then
      echo "错误: 无法连接到MongoDB"
      exit 1
    fi
  done
  exec 6>&-
  echo "MongoDB连接成功"
fi

# 应用数据库迁移（如果有）
if [ "$NODE_ENV" != "test" ] && [ ! -z "$DB_MIGRATION_ENABLED" ] && [ "$DB_MIGRATION_ENABLED" == "true" ]; then
  echo "应用数据库迁移..."
  npm run migrate
  echo "数据库迁移完成"
fi

# 创建必要的目录
mkdir -p /app/logs /app/tmp

# 确保目录权限正确
if [ "$(id -u)" = "0" ]; then
  chown -R appuser:appgroup /app/logs /app/tmp
fi

# 设置SIGTERM处理程序实现优雅关闭
term_handler() {
  echo "接收到停止信号，正在优雅关闭..."
  # 向Node进程发送SIGTERM信号
  kill -SIGTERM $child
  # 等待子进程完成
  wait $child
  echo "服务已优雅关闭"
  exit 0
}

# 设置信号处理
trap 'term_handler' SIGTERM SIGINT

# 启动主应用
echo "启动用户服务..."
if [ "$NODE_ENV" = "production" ]; then
  node server.js &
else
  if [ -x "$(command -v nodemon)" ]; then
    nodemon server.js &
  else
    node server.js &
  fi
fi

# 获取子进程PID
child=$!

# 等待子进程完成
wait $child 