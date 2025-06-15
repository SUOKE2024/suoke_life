#!/bin/bash

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
    if [[ "${DEBUG:-false}" == "true" ]]; then
        echo -e "${BLUE}[DEBUG]${NC} $1"
    fi
}

# 等待服务可用
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local timeout=${4:-30}
    
    log_info "等待 $service_name 服务可用 ($host:$port)..."
    
    for i in $(seq 1 $timeout); do
        if nc -z "$host" "$port" 2>/dev/null; then
            log_info "$service_name 服务已可用"
            return 0
        fi
        log_debug "等待 $service_name 服务... ($i/$timeout)"
        sleep 1
    done
    
    log_error "$service_name 服务在 $timeout 秒内未能启动"
    return 1
}

# 检查环境变量
check_environment() {
    log_info "检查环境变量..."
    
    # 必需的环境变量
    local required_vars=(
        "DATABASE_URL"
    )
    
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            missing_vars+=("$var")
        fi
    done
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log_error "缺少必需的环境变量: ${missing_vars[*]}"
        exit 1
    fi
    
    # 设置默认值
    export ENV=${ENV:-production}
    export LOG_LEVEL=${LOG_LEVEL:-INFO}
    export REDIS_URL=${REDIS_URL:-redis://localhost:6379/0}
    
    log_info "环境变量检查完成"
}

# 等待依赖服务
wait_for_dependencies() {
    log_info "等待依赖服务启动..."
    
    # 解析数据库URL
    if [[ $DATABASE_URL =~ postgresql.*://.*@([^:]+):([0-9]+)/.* ]]; then
        local db_host="${BASH_REMATCH[1]}"
        local db_port="${BASH_REMATCH[2]}"
        wait_for_service "$db_host" "$db_port" "PostgreSQL" 60
    fi
    
    # 解析Redis URL
    if [[ $REDIS_URL =~ redis://([^:]+):([0-9]+)/.* ]]; then
        local redis_host="${BASH_REMATCH[1]}"
        local redis_port="${BASH_REMATCH[2]}"
        wait_for_service "$redis_host" "$redis_port" "Redis" 30
    fi
    
    log_info "所有依赖服务已就绪"
}

# 运行数据库迁移
run_migrations() {
    log_info "运行数据库迁移..."
    
    if python migrations/init_db.py create; then
        log_info "数据库迁移完成"
    else
        log_warn "数据库迁移失败，可能表已存在"
    fi
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 检查配置文件
    if [[ ! -f "config/config.yaml" ]]; then
        log_error "配置文件不存在: config/config.yaml"
        exit 1
    fi
    
    # 检查数据目录
    if [[ ! -d "data" ]]; then
        log_warn "数据目录不存在，创建中..."
        mkdir -p data
    fi
    
    # 检查日志目录
    if [[ ! -d "logs" ]]; then
        log_warn "日志目录不存在，创建中..."
        mkdir -p logs
    fi
    
    log_info "健康检查完成"
}

# 启动服务
start_service() {
    local mode=${1:-both}
    
    log_info "启动问诊服务 (模式: $mode)..."
    
    case $mode in
        "grpc")
            log_info "启动gRPC服务..."
            exec python start_server.py --mode grpc
            ;;
        "rest")
            log_info "启动REST API服务..."
            exec python start_server.py --mode rest
            ;;
        "both")
            log_info "启动gRPC和REST API服务..."
            exec python start_server.py --mode both
            ;;
        *)
            log_error "未知的启动模式: $mode"
            log_info "支持的模式: grpc, rest, both"
            exit 1
            ;;
    esac
}

# 信号处理
cleanup() {
    log_info "接收到终止信号，正在清理..."
    
    # 这里可以添加清理逻辑
    # 例如：关闭数据库连接、保存状态等
    
    log_info "清理完成"
    exit 0
}

# 设置信号处理
trap cleanup SIGTERM SIGINT

# 主函数
main() {
    log_info "=== 索克生活问诊服务启动 ==="
    log_info "版本: $(cat VERSION 2>/dev/null || echo 'unknown')"
    log_info "环境: $ENV"
    log_info "时间: $(date)"
    
    # 检查是否为开发模式
    if [[ "$ENV" == "development" ]]; then
        export DEBUG=true
        log_debug "开发模式已启用"
    fi
    
    # 执行启动步骤
    check_environment
    wait_for_dependencies
    health_check
    run_migrations
    
    # 启动服务
    local mode=${1:-both}
    start_service "$mode"
}

# 如果脚本被直接执行
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 