#!/bin/bash

# 索克生活 - 服务管理脚本
# 用于管理后端微服务的启动、停止、重启等操作

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 服务配置
SERVICES=(
    "auth-service:8001"
    "user-service:8002"
    "health-data-service:8003"
    "xiaoai-service:50051"
    "xiaoke-service:9083"
    "laoke-service:8080"
    "soer-service:8054"
)

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查服务状态
check_service_status() {
    local service_name=$1
    local port=$2
    
    if curl -s -f "http://localhost:${port}/health" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# 启动单个服务
start_service() {
    local service_name=$1
    local port=$2
    
    log_info "启动服务: $service_name (端口: $port)"
    
    # 检查服务是否已经运行
    if check_service_status "$service_name" "$port"; then
        log_warning "服务 $service_name 已经在运行"
        return 0
    fi
    
    # 根据服务类型启动
    case $service_name in
        "auth-service"|"user-service"|"health-data-service")
            cd "services/$service_name"
            if [ -f "pyproject.toml" ]; then
                uv run python -m ${service_name//-/_}.cmd.server run &
            else
                python3 -m ${service_name//-/_} &
            fi
            cd - > /dev/null
            ;;
        "xiaoai-service"|"xiaoke-service"|"laoke-service"|"soer-service")
            cd "services/agent-services/$service_name"
            if [ -f "pyproject.toml" ]; then
                uv run python -m ${service_name//-/_}.cmd.server run &
            else
                python3 -m ${service_name//-/_} &
            fi
            cd - > /dev/null
            ;;
    esac
    
    # 等待服务启动
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if check_service_status "$service_name" "$port"; then
            log_success "服务 $service_name 启动成功"
            return 0
        fi
        sleep 1
        ((attempt++))
    done
    
    log_error "服务 $service_name 启动失败"
    return 1
}

# 停止单个服务
stop_service() {
    local service_name=$1
    local port=$2
    
    log_info "停止服务: $service_name (端口: $port)"
    
    # 查找并终止进程
    local pids=$(lsof -ti:$port 2>/dev/null || true)
    
    if [ -n "$pids" ]; then
        echo "$pids" | xargs kill -TERM 2>/dev/null || true
        sleep 2
        
        # 强制终止仍在运行的进程
        local remaining_pids=$(lsof -ti:$port 2>/dev/null || true)
        if [ -n "$remaining_pids" ]; then
            echo "$remaining_pids" | xargs kill -KILL 2>/dev/null || true
        fi
        
        log_success "服务 $service_name 已停止"
    else
        log_warning "服务 $service_name 未在运行"
    fi
}

# 启动所有服务
start_all() {
    log_info "启动所有服务..."
    
    for service_config in "${SERVICES[@]}"; do
        IFS=':' read -r service_name port <<< "$service_config"
        start_service "$service_name" "$port"
    done
    
    log_success "所有服务启动完成"
}

# 停止所有服务
stop_all() {
    log_info "停止所有服务..."
    
    for service_config in "${SERVICES[@]}"; do
        IFS=':' read -r service_name port <<< "$service_config"
        stop_service "$service_name" "$port"
    done
    
    log_success "所有服务已停止"
}

# 重启所有服务
restart_all() {
    log_info "重启所有服务..."
    stop_all
    sleep 3
    start_all
}

# 检查所有服务状态
status_all() {
    log_info "检查服务状态..."
    
    local all_running=true
    
    for service_config in "${SERVICES[@]}"; do
        IFS=':' read -r service_name port <<< "$service_config"
        
        if check_service_status "$service_name" "$port"; then
            echo -e "${GREEN}✓${NC} $service_name (端口: $port) - 运行中"
        else
            echo -e "${RED}✗${NC} $service_name (端口: $port) - 未运行"
            all_running=false
        fi
    done
    
    if $all_running; then
        log_success "所有服务运行正常"
    else
        log_warning "部分服务未运行"
    fi
}

# 查看服务日志
logs_service() {
    local service_name=$1
    
    if [ -z "$service_name" ]; then
        log_error "请指定服务名称"
        return 1
    fi
    
    log_info "查看服务日志: $service_name"
    
    # 查找服务进程并显示日志
    case $service_name in
        "auth"|"user"|"health-data")
            tail -f "services/${service_name}-service/logs/app.log" 2>/dev/null || \
            log_warning "日志文件不存在: services/${service_name}-service/logs/app.log"
            ;;
        "xiaoai"|"xiaoke"|"laoke"|"soer")
            tail -f "services/agent-services/${service_name}-service/logs/app.log" 2>/dev/null || \
            log_warning "日志文件不存在: services/agent-services/${service_name}-service/logs/app.log"
            ;;
        *)
            log_error "未知服务: $service_name"
            ;;
    esac
}

# 构建服务
build_all() {
    log_info "构建所有服务..."
    
    # 构建前端
    log_info "构建前端应用..."
    npm install
    npm run build 2>/dev/null || log_warning "前端构建失败或无构建脚本"
    
    # 构建后端服务
    for service_config in "${SERVICES[@]}"; do
        IFS=':' read -r service_name port <<< "$service_config"
        
        log_info "构建服务: $service_name"
        
        case $service_name in
            "auth-service"|"user-service"|"health-data-service")
                cd "services/$service_name"
                ;;
            "xiaoai-service"|"xiaoke-service"|"laoke-service"|"soer-service")
                cd "services/agent-services/$service_name"
                ;;
        esac
        
        if [ -f "pyproject.toml" ]; then
            uv sync 2>/dev/null || log_warning "服务 $service_name 依赖安装失败"
        elif [ -f "requirements.txt" ]; then
            pip install -r requirements.txt 2>/dev/null || log_warning "服务 $service_name 依赖安装失败"
        fi
        
        cd - > /dev/null
    done
    
    log_success "构建完成"
}

# 清理服务
cleanup() {
    log_info "清理服务..."
    
    stop_all
    
    # 清理临时文件
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    log_success "清理完成"
}

# 显示帮助信息
show_help() {
    echo "索克生活 - 服务管理脚本"
    echo ""
    echo "用法: $0 <命令> [参数]"
    echo ""
    echo "命令:"
    echo "  start     启动所有服务"
    echo "  stop      停止所有服务"
    echo "  restart   重启所有服务"
    echo "  status    检查所有服务状态"
    echo "  logs      查看服务日志 (需要指定服务名)"
    echo "  build     构建所有服务"
    echo "  cleanup   清理服务和临时文件"
    echo "  help      显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 start"
    echo "  $0 status"
    echo "  $0 logs auth"
    echo ""
}

# 主函数
main() {
    case "${1:-help}" in
        "start")
            start_all
            ;;
        "stop")
            stop_all
            ;;
        "restart")
            restart_all
            ;;
        "status")
            status_all
            ;;
        "logs")
            logs_service "$2"
            ;;
        "build")
            build_all
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@" 