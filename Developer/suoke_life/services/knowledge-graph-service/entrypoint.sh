#!/bin/sh
set -e

# 打印服务版本和环境信息
echo "启动知识图谱服务..."
echo "环境: $APP_ENV"
echo "端口: $APP_PORT"
echo "日志级别: $LOG_LEVEL"

# 确保数据和日志目录存在
mkdir -p /app/data
mkdir -p /app/logs

# 检查服务可执行文件
if [ ! -f /app/server ]; then
  echo "错误: 服务可执行文件不存在"
  exit 1
fi

# 添加执行权限
chmod +x /app/server

# 执行服务
echo "启动知识图谱服务..."
exec /app/server
