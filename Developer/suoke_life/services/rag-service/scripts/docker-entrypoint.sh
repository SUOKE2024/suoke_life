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
    "VECTOR_DB_URL"
    "KNOWLEDGE_BASE_URL"
    "NEO4J_URI"
    "NEO4J_USER"
    "NEO4J_PASSWORD"
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
  
  # 检查Vector数据库
  if [[ ! -z "$VECTOR_DB_URL" ]]; then
    log "检查向量数据库连接: $VECTOR_DB_URL"
    if curl -s -f -o /dev/null "${VECTOR_DB_URL}/health"; then
      log "向量数据库连接正常"
    else
      log "警告: 无法连接到向量数据库 $VECTOR_DB_URL"
    fi
  fi
  
  # 检查知识库服务
  if [[ ! -z "$KNOWLEDGE_BASE_URL" ]]; then
    log "检查知识库服务连接: $KNOWLEDGE_BASE_URL"
    if curl -s -f -o /dev/null "${KNOWLEDGE_BASE_URL}/health"; then
      log "知识库服务连接正常"
    else
      log "警告: 无法连接到知识库服务 $KNOWLEDGE_BASE_URL"
    fi
  fi
  
  # 检查Neo4j连接
  if [[ ! -z "$NEO4J_URI" ]]; then
    NEO4J_HOST=$(echo $NEO4J_URI | sed -e 's/^bolt:\/\///' -e 's/:.*//')
    NEO4J_PORT=$(echo $NEO4J_URI | sed -e 's/^bolt:\/\///' -e 's/.*://' -e 's/\/.*//')
    
    # 如果端口未指定，使用默认端口7687
    if [[ "$NEO4J_HOST" == "$NEO4J_PORT" ]]; then
      NEO4J_PORT=7687
    fi
    
    log "检查Neo4j连接 $NEO4J_HOST:$NEO4J_PORT..."
    if nc -z -w5 $NEO4J_HOST $NEO4J_PORT; then
      log "Neo4j连接正常"
    else
      log "警告: 无法连接到Neo4j $NEO4J_HOST:$NEO4J_PORT"
    fi
  fi
  
  # 检查Redis连接
  if [[ ! -z "$REDIS_HOST" ]] && [[ ! -z "$REDIS_PORT" ]]; then
    log "检查Redis连接 $REDIS_HOST:$REDIS_PORT..."
    if nc -z -w5 $REDIS_HOST $REDIS_PORT; then
      log "Redis连接正常"
    else
      log "警告: 无法连接到Redis $REDIS_HOST:$REDIS_PORT"
    fi
  fi
  
  # 检查是否启用了OpenTelemetry
  if [[ ! -z "$OTLP_ENDPOINT" ]]; then
    OTEL_HOST=$(echo $OTLP_ENDPOINT | sed -e 's/^http:\/\///' -e 's/^https:\/\///' -e 's/:.*//')
    OTEL_PORT=$(echo $OTLP_ENDPOINT | sed -e 's/^http:\/\///' -e 's/^https:\/\///' -e 's/.*://' -e 's/\/.*//')
    
    log "检查OpenTelemetry端点 $OTEL_HOST:$OTEL_PORT..."
    if nc -z -w5 $OTEL_HOST $OTEL_PORT; then
      log "OpenTelemetry端点连接正常"
    else
      log "警告: 无法连接到OpenTelemetry端点 $OTEL_HOST:$OTEL_PORT"
    fi
  fi
}

# 创建必要的目录
ensure_directories() {
  log "确保必要的目录存在..."
  
  # 数据目录
  if [[ ! -d "/app/data" ]]; then
    mkdir -p /app/data
    log "创建数据目录: /app/data"
  fi
  
  # 日志目录
  if [[ ! -d "/app/logs" ]]; then
    mkdir -p /app/logs
    log "创建日志目录: /app/logs"
  fi
  
  # 模型目录
  if [[ ! -d "/app/models" ]]; then
    mkdir -p /app/models
    log "创建模型目录: /app/models"
  fi
  
  # 缓存目录
  if [[ ! -d "/app/cache" ]]; then
    mkdir -p /app/cache
    log "创建缓存目录: /app/cache"
  fi
}

# 清理临时文件
cleanup() {
  log "清理临时文件..."
  
  # 清理超过7天的日志文件
  if [[ -d "/app/logs" ]]; then
    find /app/logs -name "*.log" -type f -mtime +7 -delete
    log "清理了超过7天的日志文件"
  fi
  
  # 清理缓存文件
  if [[ -d "/app/cache" ]]; then
    find /app/cache -type f -mtime +1 -delete
    log "清理了超过1天的缓存文件"
  fi
}

# 预热模型（如果存在预热脚本）
warmup_models() {
  if [[ -f "/app/scripts/warmup.py" ]]; then
    log "开始预热模型..."
    python /app/scripts/warmup.py
    log "模型预热完成"
  else
    log "未找到模型预热脚本，跳过预热步骤"
  fi
}

# 优雅关闭处理
graceful_shutdown() {
  log "接收到关闭信号，开始优雅关闭..."
  
  # 保存缓存（如果需要）
  log "保存缓存..."
  
  # 关闭数据库连接
  log "关闭数据库连接..."
  
  # 等待处理中的请求完成
  log "等待处理中的请求完成..."
  sleep 5
  
  log "服务关闭完成"
  exit 0
}

# 注册信号处理器
trap graceful_shutdown SIGTERM SIGINT

# 主函数
main() {
  log "RAG服务启动中..."
  log "环境: ${ENVIRONMENT:-production}"
  log "服务版本: ${SERVICE_VERSION:-latest}"
  
  # 运行必要的检查和准备
  check_env_vars
  check_dependencies
  ensure_directories
  cleanup
  warmup_models
  
  # 打印服务信息
  log "服务信息:"
  log "- 端口: ${PORT:-8000}"
  log "- Python版本: $(python --version)"
  log "- 操作系统: $(uname -a)"
  
  # 执行原始命令
  log "正在启动服务..."
  exec "$@"
}

# 执行主函数，并传递所有参数
main "$@" 