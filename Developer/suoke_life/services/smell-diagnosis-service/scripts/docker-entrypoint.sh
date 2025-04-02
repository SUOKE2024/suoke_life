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
    "API_PREFIX"
    "MONGODB_URI"
    "FOUR_DIAGNOSIS_COORDINATOR_URL"
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
  
  # 从MONGODB_URI中提取主机和端口
  if [[ ! -z "$MONGODB_URI" ]]; then
    MONGO_HOST=$(echo $MONGODB_URI | sed -e 's/^mongodb:\/\///' -e 's/:.*//' -e 's/\/.*//')
    MONGO_PORT=$(echo $MONGODB_URI | sed -e 's/^mongodb:\/\///' -e 's/.*://' -e 's/\/.*//')
    
    # 如果端口未指定，使用默认端口27017
    if [[ "$MONGO_HOST" == "$MONGO_PORT" ]]; then
      MONGO_PORT=27017
    fi
    
    log "检查MongoDB连接 $MONGO_HOST:$MONGO_PORT..."
    if nc -z -w5 $MONGO_HOST $MONGO_PORT; then
      log "MongoDB连接正常"
    else
      log "警告: 无法连接到MongoDB $MONGO_HOST:$MONGO_PORT"
    fi
  fi
  
  # 检查四诊协调器服务
  if [[ ! -z "$FOUR_DIAGNOSIS_COORDINATOR_URL" ]]; then
    COORDINATOR_HOST=$(echo $FOUR_DIAGNOSIS_COORDINATOR_URL | sed -e 's/^http:\/\///' -e 's/^https:\/\///' -e 's/:.*//')
    COORDINATOR_PORT=$(echo $FOUR_DIAGNOSIS_COORDINATOR_URL | sed -e 's/^http:\/\///' -e 's/^https:\/\///' -e 's/.*://' -e 's/\/.*//')
    
    # 如果端口未指定，使用默认端口80（http）或443（https）
    if [[ "$COORDINATOR_HOST" == "$COORDINATOR_PORT" ]]; then
      if [[ $FOUR_DIAGNOSIS_COORDINATOR_URL == https* ]]; then
        COORDINATOR_PORT=443
      else
        COORDINATOR_PORT=80
      fi
    fi
    
    log "检查四诊协调器服务连接 $COORDINATOR_HOST:$COORDINATOR_PORT..."
    if nc -z -w5 $COORDINATOR_HOST $COORDINATOR_PORT; then
      log "四诊协调器服务连接正常"
    else
      log "警告: 无法连接到四诊协调器服务 $COORDINATOR_HOST:$COORDINATOR_PORT"
    fi
  fi
  
  # 检查是否启用了OpenTelemetry
  if [[ ! -z "$OTEL_EXPORTER_OTLP_ENDPOINT" ]]; then
    OTEL_HOST=$(echo $OTEL_EXPORTER_OTLP_ENDPOINT | sed -e 's/^http:\/\///' -e 's/^https:\/\///' -e 's/:.*//')
    OTEL_PORT=$(echo $OTEL_EXPORTER_OTLP_ENDPOINT | sed -e 's/^http:\/\///' -e 's/^https:\/\///' -e 's/.*://' -e 's/\/.*//')
    
    log "检查OpenTelemetry端点 $OTEL_HOST:$OTEL_PORT..."
    if nc -z -w5 $OTEL_HOST $OTEL_PORT; then
      log "OpenTelemetry端点连接正常"
    else
      log "警告: 无法连接到OpenTelemetry端点 $OTEL_HOST:$OTEL_PORT"
    fi
  fi
}

# 创建目录
ensure_directories() {
  log "确保必要的目录存在..."
  
  # 日志目录
  if [[ ! -z "$LOG_FILE_PATH" ]]; then
    LOG_DIR=$(dirname "$LOG_FILE_PATH")
    mkdir -p $LOG_DIR
    log "创建日志目录: $LOG_DIR"
  fi
  
  # 上传文件目录
  if [[ ! -z "$UPLOADED_FILES_PATH" ]]; then
    mkdir -p $UPLOADED_FILES_PATH
    log "创建上传文件目录: $UPLOADED_FILES_PATH"
  fi
}

# 清理临时文件
cleanup() {
  log "清理临时文件..."
  
  # 清理超过60分钟的临时文件
  if [[ -d "/tmp/uploads" ]]; then
    find /tmp/uploads -type f -mmin +60 -delete
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
  log "气味诊断服务启动中..."
  log "环境: $NODE_ENV"
  log "当前目录: $(pwd)"
  
  # 运行必要的检查
  check_env_vars
  check_dependencies
  ensure_directories
  cleanup
  
  # 打印服务信息
  log "服务信息:"
  log "- 版本: $(node -e "console.log(require('./package.json').version)")"
  log "- 端口: $PORT"
  log "- 指标端口: $METRICS_PORT"
  log "- API前缀: $API_PREFIX"
  log "- 节点版本: $(node -v)"
  log "- NPM版本: $(npm -v)"
  log "- 操作系统: $(uname -a)"
  
  # 执行原始命令
  log "正在启动服务..."
  exec "$@"
}

# 执行主函数，并传递所有参数
main "$@" 