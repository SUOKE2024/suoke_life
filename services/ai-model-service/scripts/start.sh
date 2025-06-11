#!/bin/bash

# AI Model Service 启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 默认配置
DEFAULT_HOST="0.0.0.0"
DEFAULT_PORT="8080"
DEFAULT_WORKERS="1"
DEFAULT_LOG_LEVEL="INFO"

# 解析命令行参数
ENVIRONMENT="development"
HOST="$DEFAULT_HOST"
PORT="$DEFAULT_PORT"
WORKERS="$DEFAULT_WORKERS"
LOG_LEVEL="$DEFAULT_LOG_LEVEL"
CONFIG_FILE=""
RELOAD=false
DEBUG=false

usage() {
    cat << EOF
AI Model Service 启动脚本

用法: $0 [选项]

选项:
    -e, --env ENVIRONMENT       运行环境 (development|staging|production) [默认: development]
    -h, --host HOST            绑定主机地址 [默认: $DEFAULT_HOST]
    -p, --port PORT            绑定端口 [默认: $DEFAULT_PORT]
    -w, --workers WORKERS      工作进程数 [默认: $DEFAULT_WORKERS]
    -l, --log-level LEVEL      日志级别 (DEBUG|INFO|WARNING|ERROR) [默认: $DEFAULT_LOG_LEVEL]
    -c, --config CONFIG_FILE   配置文件路径
    -r, --reload               开发模式自动重载
    -d, --debug                调试模式
    --help                     显示此帮助信息

示例:
    $0                                    # 使用默认配置启动
    $0 -e production -p 8080 -w 4        # 生产环境启动
    $0 -r -d                             # 开发模式启动
    $0 -c config/production.yaml         # 使用指定配置文件启动

EOF
}

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -h|--host)
            HOST="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -w|--workers)
            WORKERS="$2"
            shift 2
            ;;
        -l|--log-level)
            LOG_LEVEL="$2"
            shift 2
            ;;
        -c|--config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -r|--reload)
            RELOAD=true
            shift
            ;;
        -d|--debug)
            DEBUG=true
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            log_error "未知参数: $1"
            usage
            exit 1
            ;;
    esac
done

# 验证环境
if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
    log_error "无效的环境: $ENVIRONMENT"
    exit 1
fi

# 切换到项目目录
cd "$PROJECT_DIR"

log_info "正在启动 AI Model Service..."
log_info "环境: $ENVIRONMENT"
log_info "主机: $HOST"
log_info "端口: $PORT"
log_info "工作进程数: $WORKERS"
log_info "日志级别: $LOG_LEVEL"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    log_error "Python3 未安装"
    exit 1
fi

# 检查UV包管理器
if ! command -v uv &> /dev/null; then
    log_warn "UV包管理器未安装，正在安装..."
    pip install uv
fi

# 检查虚拟环境
if [[ ! -d ".venv" ]]; then
    log_info "创建虚拟环境..."
    uv venv
fi

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
log_info "安装依赖..."
if [[ "$ENVIRONMENT" == "development" ]]; then
    uv sync --dev
else
    uv sync --no-dev
fi

# 设置环境变量
export PYTHONPATH="$PROJECT_DIR/src:$PYTHONPATH"
export APP_ENV="$ENVIRONMENT"
export HOST="$HOST"
export PORT="$PORT"
export LOG_LEVEL="$LOG_LEVEL"

if [[ "$DEBUG" == "true" ]]; then
    export DEBUG="true"
    export LOG_LEVEL="DEBUG"
fi

# 加载配置文件
if [[ -n "$CONFIG_FILE" ]]; then
    if [[ -f "$CONFIG_FILE" ]]; then
        export CONFIG_FILE="$CONFIG_FILE"
        log_info "使用配置文件: $CONFIG_FILE"
    else
        log_error "配置文件不存在: $CONFIG_FILE"
        exit 1
    fi
fi

# 加载环境变量文件
ENV_FILE=".env"
if [[ "$ENVIRONMENT" != "development" ]]; then
    ENV_FILE=".env.$ENVIRONMENT"
fi

if [[ -f "$ENV_FILE" ]]; then
    log_info "加载环境变量文件: $ENV_FILE"
    set -a
    source "$ENV_FILE"
    set +a
fi

# 健康检查函数
health_check() {
    local max_attempts=30
    local attempt=1
    
    log_info "等待服务启动..."
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f -s "http://$HOST:$PORT/health/live" > /dev/null 2>&1; then
            log_info "服务启动成功！"
            log_info "API文档: http://$HOST:$PORT/docs"
            log_info "健康检查: http://$HOST:$PORT/health"
            log_info "指标端点: http://$HOST:$PORT/metrics"
            return 0
        fi
        
        log_debug "健康检查失败，重试 $attempt/$max_attempts..."
        sleep 2
        ((attempt++))
    done
    
    log_error "服务启动失败或健康检查超时"
    return 1
}

# 信号处理
cleanup() {
    log_info "正在关闭服务..."
    if [[ -n "$SERVER_PID" ]]; then
        kill -TERM "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
    log_info "服务已关闭"
    exit 0
}

trap cleanup SIGINT SIGTERM

# 启动服务
log_info "启动AI Model Service..."

if [[ "$ENVIRONMENT" == "development" && "$RELOAD" == "true" ]]; then
    # 开发模式，使用uvicorn直接启动并支持热重载
    log_info "开发模式启动（支持热重载）"
    uvicorn ai_model_service.main:app \
        --host "$HOST" \
        --port "$PORT" \
        --reload \
        --reload-dir src \
        --log-level "${LOG_LEVEL,,}" &
    SERVER_PID=$!
else
    # 生产模式，使用应用内置的启动方式
    python -m ai_model_service.main &
    SERVER_PID=$!
fi

# 等待服务启动并进行健康检查
sleep 5
if health_check; then
    # 保持脚本运行
    wait "$SERVER_PID"
else
    log_error "服务启动失败"
    cleanup
    exit 1
fi 