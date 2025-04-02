#!/bin/bash
set -e

# 打印启动信息
echo "启动小艾服务 - XiaoAI Service"
echo "NODE_ENV: $NODE_ENV"

# 检查必要的环境变量
required_vars=(
  "PORT"
  "MONGODB_URI"
  "REDIS_URL"
  "LOG_LEVEL"
)

for var in "${required_vars[@]}"; do
  if [ -z "${!var}" ]; then
    echo "错误: 环境变量 $var 未设置"
    exit 1
  fi
done

# 等待MongoDB连接
echo "检查MongoDB连接..."
max_retries=30
count=0
until mongo --eval "db.adminCommand('ping')" --host $(echo $MONGODB_URI | sed -e 's/.*@\(.*\):.*/\1/') --quiet; do
  echo "等待MongoDB可用... ($count/$max_retries)"
  sleep 2
  count=$((count+1))
  if [ $count -ge $max_retries ]; then
    echo "错误: 无法连接到MongoDB"
    exit 1
  fi
done
echo "MongoDB连接成功"

# 等待Redis连接
echo "检查Redis连接..."
max_retries=30
count=0
redis_host=$(echo $REDIS_URL | sed -e 's/.*@\(.*\):.*/\1/')
redis_port=$(echo $REDIS_URL | sed -e 's/.*:\(.*\)/\1/')

until redis-cli -h $redis_host -p $redis_port ping; do
  echo "等待Redis可用... ($count/$max_retries)"
  sleep 2
  count=$((count+1))
  if [ $count -ge $max_retries ]; then
    echo "错误: 无法连接到Redis"
    exit 1
  fi
done
echo "Redis连接成功"

# 应用数据库迁移
if [ "$NODE_ENV" != "test" ]; then
  echo "应用数据库迁移..."
  npm run migrate
  echo "数据库迁移完成"
fi

# 设置SIGTERM处理程序
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
echo "启动小艾服务..."
if [ "$NODE_ENV" = "production" ]; then
  node dist/index.js &
else
  npm run dev &
fi

# 获取子进程PID
child=$!

# 等待子进程完成
wait $child 