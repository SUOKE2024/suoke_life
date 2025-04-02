#!/bin/bash
set -e

# 添加时间戳到日志输出
log() {
  TIMESTAMP=$(date -u "+%Y-%m-%dT%H:%M:%SZ")
  echo "[$TIMESTAMP] $*"
}

# 检查必要的环境变量
check_env_vars() {
  log "检查环境变量..."
  
  # 定义必要的环境变量列表
  REQUIRED_VARS=(
    "PORT"
    "NODE_ENV"
    "DB_HOST"
    "DB_PORT"
    "DB_USER"
    "DB_PASSWORD"
    "DB_NAME"
    "REDIS_HOST"
    "REDIS_PORT"
  )
  
  # 检查每个环境变量
  MISSING_VARS=0
  for VAR in "${REQUIRED_VARS[@]}"; do
    if [[ -z "${!VAR}" ]]; then
      log "错误: 缺少必要的环境变量: $VAR"
      MISSING_VARS=$((MISSING_VARS + 1))
    fi
  done
  
  # 如果有缺失的环境变量，打印警告但继续执行
  if [[ $MISSING_VARS -gt 0 ]]; then
    log "警告: 存在 $MISSING_VARS 个缺失的环境变量，服务可能无法正常工作"
  else
    log "环境变量检查通过"
  fi
}

# 检查依赖服务健康状态
check_dependencies() {
  log "检查依赖服务健康状态..."
  
  # 检查数据库连接
  if [[ ! -z "$DB_HOST" && ! -z "$DB_PORT" ]]; then
    log "检查数据库连接 $DB_HOST:$DB_PORT..."
    if nc -z -w5 $DB_HOST $DB_PORT; then
      log "数据库连接正常"
    else
      log "警告: 无法连接到数据库 $DB_HOST:$DB_PORT"
    fi
  fi
  
  # 检查Redis连接
  if [[ ! -z "$REDIS_HOST" && ! -z "$REDIS_PORT" ]]; then
    log "检查Redis连接 $REDIS_HOST:$REDIS_PORT..."
    if nc -z -w5 $REDIS_HOST $REDIS_PORT; then
      log "Redis连接正常"
    else
      log "警告: 无法连接到Redis $REDIS_HOST:$REDIS_PORT"
    fi
  fi
  
  # 检查其他可能的依赖服务
  if [[ ! -z "$METRICS_SERVICE" ]]; then
    log "检查指标服务 $METRICS_SERVICE..."
    if nc -z -w5 $(echo $METRICS_SERVICE | cut -d: -f1) $(echo $METRICS_SERVICE | cut -d: -f2); then
      log "指标服务连接正常"
    else
      log "警告: 无法连接到指标服务 $METRICS_SERVICE"
    fi
  fi
  
  # 检查是否启用了OpenTelemetry
  if [[ ! -z "$OTEL_EXPORTER_OTLP_ENDPOINT" ]]; then
    log "检查OpenTelemetry端点 $OTEL_EXPORTER_OTLP_ENDPOINT..."
    if nc -z -w5 $(echo $OTEL_EXPORTER_OTLP_ENDPOINT | sed -e 's|http://||' -e 's|https://||' | cut -d: -f1) $(echo $OTEL_EXPORTER_OTLP_ENDPOINT | sed -e 's|http://||' -e 's|https://||' | cut -d: -f2 | cut -d/ -f1); then
      log "OpenTelemetry端点连接正常"
    else
      log "警告: 无法连接到OpenTelemetry端点"
    fi
  fi
}

# 运行数据库迁移
run_migrations() {
  if [[ "$RUN_MIGRATIONS" == "true" ]]; then
    log "运行数据库迁移..."
    NODE_ENV=$NODE_ENV node src/scripts/migrate.js
    log "数据库迁移完成"
  else
    log "跳过数据库迁移 (RUN_MIGRATIONS != true)"
  fi
}

# 清理临时文件
cleanup() {
  log "清理临时文件..."
  
  # 清理超过60分钟的临时文件
  if [[ -d "/app/tmp" ]]; then
    find /app/tmp -type f -mmin +60 -delete
    log "临时文件清理完成"
  fi
}

# 优雅关闭处理
graceful_shutdown() {
  log "接收到关闭信号，开始优雅关闭..."
  
  # 此处可以实现特定的关闭逻辑，例如关闭数据库连接等
  
  log "服务关闭完成"
  exit 0
}

# 注册信号处理器
trap graceful_shutdown SIGTERM SIGINT

# 主函数
main() {
  log "索儿服务启动中..."
  log "环境: $NODE_ENV"
  log "当前目录: $(pwd)"
  
  # 运行必要的检查
  check_env_vars
  check_dependencies
  run_migrations
  cleanup
  
  # 打印服务信息
  log "服务信息:"
  log "- 版本: $(node -e "console.log(require('./package.json').version)")"
  log "- 节点版本: $(node -v)"
  log "- NPM版本: $(npm -v)"
  log "- 操作系统: $(uname -a)"
  
  # 执行原始命令
  log "正在启动服务..."
  exec "$@"
}

# 执行主函数，并传递所有参数
main "$@" 