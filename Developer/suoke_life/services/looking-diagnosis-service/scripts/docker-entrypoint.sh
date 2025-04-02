#!/bin/bash
# looking-diagnosis-service 容器启动脚本
# 提供环境变量检查、依赖健康检查、优雅启动和关闭

set -e

# 脚本版本
VERSION="1.0.0"

# 设置默认变量
DATA_DIR=${DATA_DIR:-"/app/data"}
LOG_DIR=${LOG_DIR:-"/app/logs"}
UPLOAD_DIR=${UPLOAD_DIR:-"/app/uploads"}
TEMP_DIR=${TEMP_DIR:-"/app/temp"}
CLEANUP_INTERVAL=${CLEANUP_INTERVAL:-60} # 清理临时文件间隔（分钟）

# 日志函数
log() {
  local level=$1
  shift
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] [${level}] $*"
}

log_info() {
  log "INFO" "$@"
}

log_warn() {
  log "WARN" "$@" >&2
}

log_error() {
  log "ERROR" "$@" >&2
}

# 检查必要环境变量
check_env_vars() {
  log_info "检查必要环境变量..."
  
  local missing_vars=0
  
  # 必需的环境变量列表
  local required_vars=(
    "PORT"
    "NODE_ENV"
    "API_PREFIX"
    "MONGODB_URI"
    "LOOKING_DIAGNOSIS_MODEL_PATH"
    "FOUR_DIAGNOSIS_COORDINATOR_URL"
  )
  
  # 检查每个必需的环境变量
  for var in "${required_vars[@]}"; do
    if [[ -z "${!var}" ]]; then
      log_warn "缺少必要的环境变量: $var"
      missing_vars=$((missing_vars + 1))
    fi
  done
  
  # 检查可选但推荐的环境变量
  local recommended_vars=(
    "LOG_LEVEL"
    "ENABLE_SWAGGER"
    "MAX_FILE_SIZE_MB"
  )
  
  for var in "${recommended_vars[@]}"; do
    if [[ -z "${!var}" ]]; then
      log_warn "推荐设置环境变量: $var"
    fi
  done
  
  # 如果有缺失的必需环境变量，退出
  if [[ $missing_vars -gt 0 ]]; then
    log_error "缺少 $missing_vars 个必要环境变量，无法启动服务"
    exit 1
  fi
  
  log_info "环境变量检查完成，所有必要变量已设置"
  return 0
}

# 检查依赖服务健康状态
check_dependencies() {
  log_info "检查依赖服务健康状态..."
  local all_healthy=true
  
  # 从MONGODB_URI提取MongoDB连接信息
  if [[ -n "$MONGODB_URI" ]]; then
    local mongo_host=$(echo $MONGODB_URI | sed -n 's/.*@\(.*\):.*/\1/p')
    local mongo_port=$(echo $MONGODB_URI | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    
    if [[ -z "$mongo_host" || -z "$mongo_port" ]]; then
      # 尝试另一种解析方式（无认证情况）
      mongo_host=$(echo $MONGODB_URI | sed -n 's/.*\/\/\(.*\):.*/\1/p')
      mongo_port=$(echo $MONGODB_URI | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    fi
    
    if [[ -n "$mongo_host" && -n "$mongo_port" ]]; then
      log_info "检查MongoDB连接: $mongo_host:$mongo_port"
      
      # 使用nc检查MongoDB端口是否开放
      if nc -z -w 5 $mongo_host $mongo_port; then
        log_info "MongoDB连接成功: $mongo_host:$mongo_port"
      else
        log_error "无法连接到MongoDB: $mongo_host:$mongo_port"
        all_healthy=false
      fi
    else
      log_warn "无法从MONGODB_URI解析主机和端口，跳过MongoDB健康检查"
    fi
  else
    log_warn "MONGODB_URI未设置，跳过MongoDB健康检查"
  fi
  
  # 检查四诊协调器服务
  if [[ -n "$FOUR_DIAGNOSIS_COORDINATOR_URL" ]]; then
    log_info "检查四诊协调器服务: $FOUR_DIAGNOSIS_COORDINATOR_URL"
    
    # 尝试检查四诊协调器健康端点
    if curl -s --head --fail "$FOUR_DIAGNOSIS_COORDINATOR_URL/health" > /dev/null; then
      log_info "四诊协调器服务可用"
    else
      log_warn "无法连接到四诊协调器服务，服务可能不可用"
      # 这里不将all_healthy设为false，因为四诊协调器可能是可选服务
    fi
  else
    log_warn "FOUR_DIAGNOSIS_COORDINATOR_URL未设置，跳过四诊协调器健康检查"
  fi
  
  # 检查望诊模型文件是否存在
  if [[ -n "$LOOKING_DIAGNOSIS_MODEL_PATH" ]]; then
    if [[ -f "$LOOKING_DIAGNOSIS_MODEL_PATH" ]]; then
      log_info "望诊模型文件存在: $LOOKING_DIAGNOSIS_MODEL_PATH"
    else
      log_error "望诊模型文件不存在: $LOOKING_DIAGNOSIS_MODEL_PATH"
      all_healthy=false
    fi
  else
    log_warn "LOOKING_DIAGNOSIS_MODEL_PATH未设置，跳过模型文件检查"
  fi
  
  if [[ "$all_healthy" != "true" ]]; then
    log_error "依赖服务健康检查失败"
    return 1
  fi
  
  log_info "所有依赖服务健康状态正常"
  return 0
}

# 创建必要目录
ensure_directories() {
  log_info "确保必要目录存在..."
  
  local dirs=(
    "$DATA_DIR"
    "$LOG_DIR"
    "$UPLOAD_DIR"
    "$TEMP_DIR"
    "$DATA_DIR/images"
    "$DATA_DIR/results"
    "$LOG_DIR/app"
    "$LOG_DIR/requests"
  )
  
  for dir in "${dirs[@]}"; do
    if [[ ! -d "$dir" ]]; then
      log_info "创建目录: $dir"
      mkdir -p "$dir"
    fi
    
    # 确保目录具有适当的权限
    chmod -R 755 "$dir"
  done
  
  log_info "目录检查和创建完成"
  return 0
}

# 清理临时文件
cleanup_temp_files() {
  log_info "清理临时文件..."
  
  # 查找和删除60分钟前的临时文件
  if [[ -d "$TEMP_DIR" ]]; then
    find "$TEMP_DIR" -type f -mmin +$CLEANUP_INTERVAL -exec rm -f {} \;
    log_info "已清理超过${CLEANUP_INTERVAL}分钟的临时文件"
  fi
  
  # 限制上传目录的大小
  if [[ -d "$UPLOAD_DIR" && -n "$MAX_UPLOAD_DIR_SIZE_MB" ]]; then
    local dir_size_kb=$(du -s "$UPLOAD_DIR" | awk '{print $1}')
    local dir_size_mb=$((dir_size_kb / 1024))
    local max_size_mb=${MAX_UPLOAD_DIR_SIZE_MB}
    
    if [[ $dir_size_mb -gt $max_size_mb ]]; then
      log_warn "上传目录大小($dir_size_mb MB)超过限制($max_size_mb MB)，清理最旧的文件"
      find "$UPLOAD_DIR" -type f -printf '%T+ %p\n' | sort | head -n 50 | awk '{print $2}' | xargs rm -f
    fi
  fi
  
  return 0
}

# 优雅关闭
graceful_shutdown() {
  log_info "接收到关闭信号，开始优雅关闭..."
  
  # 给应用程序一些时间来完成当前请求
  sleep 2
  
  # 执行额外的清理工作
  cleanup_temp_files
  
  log_info "服务已优雅关闭"
  exit 0
}

# 注册信号处理
trap graceful_shutdown SIGTERM SIGINT

# 主函数
main() {
  log_info "==== 望诊服务启动脚本 v${VERSION} ===="
  log_info "服务环境: $NODE_ENV"
  
  # 检查环境变量
  check_env_vars || exit 1
  
  # 创建必要目录
  ensure_directories || exit 1
  
  # 检查依赖服务
  check_dependencies
  # 我们不希望因为依赖检查失败而阻止服务启动，所以这里不退出
  
  # 清理临时文件
  cleanup_temp_files
  
  # 显示服务信息
  log_info "望诊服务准备就绪"
  log_info "API前缀: $API_PREFIX"
  log_info "监听端口: $PORT"
  log_info "==============================="
  
  # 执行实际的服务启动命令
  exec "$@"
}

# 执行主函数，传递所有参数
main "$@" 