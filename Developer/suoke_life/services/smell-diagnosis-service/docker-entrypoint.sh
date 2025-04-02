#!/bin/bash
set -e

# 日志函数
log() {
  local level="$1"
  local message="$2"
  local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  echo "[$timestamp] [$level] $message"
}

# 检查必要的环境变量
check_env_vars() {
  log "INFO" "检查环境变量..."
  local missing_vars=0
  
  # 必需的环境变量列表
  local required_vars=(
    "PORT"
    "NODE_ENV"
    "MONGODB_URI"
    "REDIS_HOST"
    "REDIS_PORT"
    "FOUR_DIAGNOSIS_COORDINATOR_URL"
  )
  
  for var in "${required_vars[@]}"; do
    if [[ -z "${!var}" ]]; then
      log "ERROR" "缺少必需的环境变量: $var"
      missing_vars=$((missing_vars + 1))
    fi
  done
  
  if [[ $missing_vars -gt 0 ]]; then
    log "WARN" "检测到 $missing_vars 个缺失的环境变量，服务可能无法正常工作"
  else
    log "INFO" "所有必需的环境变量已设置"
  fi
}

# 检查依赖服务
check_dependencies() {
  log "INFO" "检查依赖服务..."
  
  # 检查MongoDB
  if [[ ! -z "$MONGODB_URI" ]]; then
    log "INFO" "尝试连接MongoDB: $MONGODB_URI"
    if command -v mongosh &> /dev/null; then
      local mongo_check=$(mongosh --quiet --eval "db.serverStatus().ok" $MONGODB_URI || echo "0")
      if [[ "$mongo_check" == "1" ]]; then
        log "INFO" "MongoDB连接成功"
      else
        log "WARN" "MongoDB连接失败，服务可能无法正常工作"
      fi
    else
      log "WARN" "MongoDB客户端工具不可用，跳过连接检查"
    fi
  fi
  
  # 检查Redis
  if [[ ! -z "$REDIS_HOST" ]] && [[ ! -z "$REDIS_PORT" ]]; then
    log "INFO" "尝试连接Redis: $REDIS_HOST:$REDIS_PORT"
    if command -v redis-cli &> /dev/null; then
      local redis_check=$(redis-cli -h $REDIS_HOST -p $REDIS_PORT PING || echo "FAILED")
      if [[ "$redis_check" == "PONG" ]]; then
        log "INFO" "Redis连接成功"
      else
        log "WARN" "Redis连接失败，服务可能无法正常工作"
      fi
    else
      log "WARN" "Redis客户端工具不可用，跳过连接检查"
    fi
  fi
  
  # 检查四诊合参协调器服务
  if [[ ! -z "$FOUR_DIAGNOSIS_COORDINATOR_URL" ]]; then
    log "INFO" "尝试连接四诊合参协调器: $FOUR_DIAGNOSIS_COORDINATOR_URL"
    local coordinator_check=$(curl -s -o /dev/null -w "%{http_code}" "${FOUR_DIAGNOSIS_COORDINATOR_URL}/health" || echo "000")
    if [[ "$coordinator_check" == "200" ]]; then
      log "INFO" "四诊合参协调器连接成功"
    else
      log "WARN" "四诊合参协调器连接失败 (状态码: $coordinator_check)，可能影响服务功能"
    fi
  fi
}

# 执行数据库迁移
run_migrations() {
  if [[ "${RUN_MIGRATIONS}" == "true" ]]; then
    log "INFO" "执行数据库迁移..."
    if [[ -f "/app/scripts/migrate.js" ]]; then
      node /app/scripts/migrate.js
      local result=$?
      if [[ $result -eq 0 ]]; then
        log "INFO" "数据库迁移成功完成"
      else
        log "ERROR" "数据库迁移失败 (退出码: $result)"
      fi
    else
      log "WARN" "迁移脚本不存在，跳过迁移"
    fi
  else
    log "INFO" "跳过数据库迁移 (RUN_MIGRATIONS=${RUN_MIGRATIONS})"
  fi
}

# 清理临时文件
cleanup() {
  log "INFO" "清理临时文件..."
  if [[ -d "/app/tmp" ]]; then
    find /app/tmp -type f -mmin +60 -delete
    log "INFO" "已清理超过60分钟的临时文件"
  fi
}

# 优雅关闭处理
graceful_shutdown() {
  log "INFO" "接收到关闭信号，准备优雅退出..."
  
  # 这里可以添加任何特定的清理任务
  sleep 2  # 给应用一些时间完成当前请求
  
  # 关闭主进程
  if [[ -n "$child_pid" ]]; then
    log "INFO" "终止子进程 (PID: $child_pid)"
    kill -TERM "$child_pid" 2>/dev/null
    wait "$child_pid"
  fi
  
  log "INFO" "服务已优雅停止"
  exit 0
}

# 设置信号处理
trap graceful_shutdown SIGTERM SIGINT

# 执行启动前检查
check_env_vars
check_dependencies
run_migrations
cleanup

# 打印服务信息
log "INFO" "启动气味诊断服务..."
log "INFO" "环境: $NODE_ENV"
log "INFO" "服务端口: $PORT"
log "INFO" "服务版本: ${SERVICE_VERSION:-未知}"

# 执行主命令
log "INFO" "执行命令: $@"
exec "$@" &
child_pid=$!

# 等待子进程完成
wait $child_pid