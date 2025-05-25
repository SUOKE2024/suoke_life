#!/bin/bash

# RAG服务启动脚本
# 用于启动索克生活RAG服务

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
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 默认配置
ENVIRONMENT=${ENVIRONMENT:-development}
CONFIG_FILE=${CONFIG_FILE:-"config/${ENVIRONMENT}.yaml"}
LOG_LEVEL=${LOG_LEVEL:-INFO}
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8080}
GRPC_PORT=${GRPC_PORT:-50051}
WORKERS=${WORKERS:-1}

# 显示启动信息
show_banner() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "        索克生活 RAG服务 (Suoke Life RAG)"
    echo "=================================================="
    echo -e "${NC}"
    echo "环境: $ENVIRONMENT"
    echo "配置文件: $CONFIG_FILE"
    echo "日志级别: $LOG_LEVEL"
    echo "HTTP端口: $PORT"
    echo "gRPC端口: $GRPC_PORT"
    echo "工作进程: $WORKERS"
    echo "=================================================="
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    # 检查pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 未安装"
        exit 1
    fi
    
    # 检查虚拟环境
    if [[ -z "$VIRTUAL_ENV" ]]; then
        log_warn "未检测到虚拟环境，建议使用虚拟环境"
    fi
    
    log_info "依赖检查完成"
}

# 安装依赖
install_dependencies() {
    log_info "安装Python依赖..."
    
    cd "$PROJECT_ROOT"
    
    # 检查是否存在pyproject.toml
    if [[ -f "pyproject.toml" ]]; then
        log_info "使用pyproject.toml安装依赖"
        pip3 install -e .
    elif [[ -f "requirements.txt" ]]; then
        log_info "使用requirements.txt安装依赖"
        pip3 install -r requirements.txt
    else
        log_error "未找到依赖文件 (pyproject.toml 或 requirements.txt)"
        exit 1
    fi
    
    log_info "依赖安装完成"
}

# 检查配置文件
check_config() {
    log_info "检查配置文件..."
    
    cd "$PROJECT_ROOT"
    
    if [[ ! -f "$CONFIG_FILE" ]]; then
        log_warn "配置文件 $CONFIG_FILE 不存在，使用默认配置"
        
        # 创建配置目录
        mkdir -p "$(dirname "$CONFIG_FILE")"
        
        # 创建默认配置
        cat > "$CONFIG_FILE" << EOF
# RAG服务配置文件
environment: $ENVIRONMENT

server:
  host: $HOST
  port: $PORT
  log_level: $LOG_LEVEL
  workers: $WORKERS

grpc:
  enabled: true
  port: $GRPC_PORT

database:
  host: localhost
  port: 5432
  username: postgres
  password: ""
  database: rag_service

vector_database:
  type: milvus
  host: localhost
  port: 19530

cache:
  type: redis
  host: localhost
  port: 6379

embedding:
  model: sentence-transformers/all-MiniLM-L6-v2
  device: cpu

generation:
  provider: openai
  model: gpt-3.5-turbo
  api_key: ""

logging:
  level: $LOG_LEVEL
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
EOF
        
        log_info "已创建默认配置文件: $CONFIG_FILE"
    fi
    
    log_info "配置文件检查完成"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    cd "$PROJECT_ROOT"
    
    # 创建日志目录
    mkdir -p logs
    
    # 创建数据目录
    mkdir -p data
    
    # 创建缓存目录
    mkdir -p cache
    
    # 创建临时目录
    mkdir -p tmp
    
    log_info "目录创建完成"
}

# 检查端口是否可用
check_ports() {
    log_info "检查端口可用性..."
    
    # 检查HTTP端口
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_error "端口 $PORT 已被占用"
        exit 1
    fi
    
    # 检查gRPC端口
    if lsof -Pi :$GRPC_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_error "端口 $GRPC_PORT 已被占用"
        exit 1
    fi
    
    log_info "端口检查完成"
}

# 设置环境变量
setup_environment() {
    log_info "设置环境变量..."
    
    export RAG_ENVIRONMENT=$ENVIRONMENT
    export RAG_CONFIG_FILE="$PROJECT_ROOT/$CONFIG_FILE"
    export RAG_LOG_LEVEL=$LOG_LEVEL
    export RAG_HOST=$HOST
    export RAG_PORT=$PORT
    export RAG_GRPC_PORT=$GRPC_PORT
    
    # Python路径
    export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
    
    log_info "环境变量设置完成"
}

# 启动服务
start_service() {
    log_info "启动RAG服务..."
    
    cd "$PROJECT_ROOT"
    
    # 设置Python路径
    export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
    
    # 启动服务
    if [[ "$WORKERS" -gt 1 ]]; then
        log_info "使用多进程模式启动服务 (workers: $WORKERS)"
        python3 -m uvicorn cmd.server.main:app \
            --host "$HOST" \
            --port "$PORT" \
            --workers "$WORKERS" \
            --log-level "$(echo $LOG_LEVEL | tr '[:upper:]' '[:lower:]')" \
            --access-log \
            --reload
    else
        log_info "使用单进程模式启动服务"
        python3 cmd/server/main.py
    fi
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f -s "http://$HOST:$PORT/health" > /dev/null 2>&1; then
            log_info "服务健康检查通过"
            return 0
        fi
        
        log_debug "健康检查失败，重试 $attempt/$max_attempts"
        sleep 2
        ((attempt++))
    done
    
    log_error "服务健康检查失败"
    return 1
}

# 停止服务
stop_service() {
    log_info "停止RAG服务..."
    
    # 查找并终止进程
    local pids=$(pgrep -f "cmd/server/main.py" || true)
    
    if [[ -n "$pids" ]]; then
        log_info "发现运行中的服务进程: $pids"
        
        # 发送SIGTERM信号
        echo "$pids" | xargs kill -TERM
        
        # 等待进程优雅退出
        sleep 5
        
        # 检查是否还有进程运行
        local remaining_pids=$(pgrep -f "cmd/server/main.py" || true)
        
        if [[ -n "$remaining_pids" ]]; then
            log_warn "强制终止剩余进程: $remaining_pids"
            echo "$remaining_pids" | xargs kill -KILL
        fi
        
        log_info "服务已停止"
    else
        log_info "未发现运行中的服务进程"
    fi
}

# 重启服务
restart_service() {
    log_info "重启RAG服务..."
    stop_service
    sleep 2
    start_service
}

# 显示服务状态
show_status() {
    log_info "检查服务状态..."
    
    local pids=$(pgrep -f "cmd/server/main.py" || true)
    
    if [[ -n "$pids" ]]; then
        log_info "服务正在运行 (PID: $pids)"
        
        # 检查HTTP端口
        if curl -f -s "http://$HOST:$PORT/health" > /dev/null 2>&1; then
            log_info "HTTP服务正常 (http://$HOST:$PORT)"
        else
            log_warn "HTTP服务异常"
        fi
        
        # 检查gRPC端口
        if nc -z "$HOST" "$GRPC_PORT" 2>/dev/null; then
            log_info "gRPC服务正常 (grpc://$HOST:$GRPC_PORT)"
        else
            log_warn "gRPC服务异常"
        fi
    else
        log_info "服务未运行"
    fi
}

# 显示日志
show_logs() {
    log_info "显示服务日志..."
    
    cd "$PROJECT_ROOT"
    
    if [[ -f "logs/rag-service.log" ]]; then
        tail -f logs/rag-service.log
    else
        log_warn "日志文件不存在"
    fi
}

# 清理
cleanup() {
    log_info "清理临时文件..."
    
    cd "$PROJECT_ROOT"
    
    # 清理临时目录
    rm -rf tmp/*
    
    # 清理缓存
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    log_info "清理完成"
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [命令] [选项]"
    echo ""
    echo "命令:"
    echo "  start       启动服务"
    echo "  stop        停止服务"
    echo "  restart     重启服务"
    echo "  status      显示服务状态"
    echo "  logs        显示服务日志"
    echo "  health      执行健康检查"
    echo "  install     安装依赖"
    echo "  cleanup     清理临时文件"
    echo "  help        显示帮助信息"
    echo ""
    echo "环境变量:"
    echo "  ENVIRONMENT    环境 (development/testing/staging/production)"
    echo "  CONFIG_FILE    配置文件路径"
    echo "  LOG_LEVEL      日志级别 (DEBUG/INFO/WARNING/ERROR)"
    echo "  HOST           监听主机"
    echo "  PORT           HTTP端口"
    echo "  GRPC_PORT      gRPC端口"
    echo "  WORKERS        工作进程数"
    echo ""
    echo "示例:"
    echo "  $0 start"
    echo "  ENVIRONMENT=production $0 start"
    echo "  PORT=8081 $0 start"
}

# 主函数
main() {
    local command=${1:-start}
    
    case "$command" in
        start)
            show_banner
            check_dependencies
            check_config
            create_directories
            check_ports
            setup_environment
            start_service
            ;;
        stop)
            stop_service
            ;;
        restart)
            restart_service
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        health)
            health_check
            ;;
        install)
            install_dependencies
            ;;
        cleanup)
            cleanup
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

# 信号处理
trap 'log_info "收到中断信号，正在停止服务..."; stop_service; exit 0' INT TERM

# 执行主函数
main "$@" 