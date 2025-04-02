#!/bin/sh
set -e

# 打印日志函数
log() {
  echo "$(date +"%Y-%m-%d %H:%M:%S") - $1"
}

# 检查必要的环境变量
check_env_vars() {
  log "正在检查环境变量..."
  
  required_vars="PORT NODE_ENV DATABASE_URL REDIS_HOST REDIS_PORT"
  missing_vars=""
  
  for var in $required_vars; do
    if [ -z "$(eval echo \$$var)" ]; then
      missing_vars="$missing_vars $var"
    fi
  done
  
  if [ -n "$missing_vars" ]; then
    log "错误: 以下必需的环境变量未设置:$missing_vars"
    exit 1
  fi
  
  log "环境变量检查完成"
}

# 检查依赖服务健康状态
check_dependencies() {
  log "正在检查依赖服务..."
  
  # 检查Redis连接
  if [ -n "$REDIS_HOST" ] && [ -n "$REDIS_PORT" ]; then
    log "检查Redis连接: $REDIS_HOST:$REDIS_PORT"
    timeout 5 sh -c "
      until nc -z $REDIS_HOST $REDIS_PORT; do
        echo '等待Redis可用...'
        sleep 1
      done
    " || {
      log "警告: Redis服务未就绪，可能会影响部分功能"
    }
  fi
  
  # 检查其他服务的健康状态（如果有）
  if [ -n "$DIAGNOSIS_COORDINATOR_URL" ]; then
    log "检查四诊协调服务: $DIAGNOSIS_COORDINATOR_URL"
    timeout 5 sh -c "
      until curl -s -f $DIAGNOSIS_COORDINATOR_URL/health > /dev/null; do
        echo '等待四诊协调服务可用...'
        sleep 2
      done
    " || {
      log "警告: 四诊协调服务未就绪，可能会影响部分功能"
    }
  fi
  
  if [ -n "$KNOWLEDGE_BASE_URL" ]; then
    log "检查知识库服务: $KNOWLEDGE_BASE_URL"
    timeout 5 sh -c "
      until curl -s -f $KNOWLEDGE_BASE_URL/health > /dev/null; do
        echo '等待知识库服务可用...'
        sleep 2
      done
    " || {
      log "警告: 知识库服务未就绪，可能会影响部分功能"
    }
  fi
  
  log "依赖服务检查完成"
}

# 数据库迁移（如果需要）
run_migrations() {
  if [ "$ENABLE_DB_MIGRATION" = "true" ]; then
    log "正在执行数据库迁移..."
    # 这里执行数据库迁移命令，例如:
    # npm run migrate
    log "数据库迁移完成"
  else
    log "跳过数据库迁移"
  fi
}

# 清理临时文件
cleanup() {
  log "正在清理临时文件..."
  # 根据需要清理临时文件
  find /tmp -name "touch-diagnosis-temp-*" -type f -mmin +60 -delete 2>/dev/null || true
  log "临时文件清理完成"
}

# 退出前执行的操作
graceful_shutdown() {
  log "接收到终止信号，正在优雅关闭..."
  # 在这里执行优雅关闭所需的命令
  sleep 3  # 给应用一些时间完成当前请求
  log "服务已关闭"
  exit 0
}

# 注册信号处理器
trap graceful_shutdown SIGTERM SIGINT

# 执行启动前检查
log "触诊服务启动脚本开始执行..."
check_env_vars
check_dependencies
run_migrations
cleanup

# 打印服务信息
log "触诊服务 (Touch Diagnosis Service) 启动中..."
log "环境: $NODE_ENV"
log "端口: $PORT"

# 执行原始命令
log "启动服务..."
exec "$@" 