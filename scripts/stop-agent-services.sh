#!/bin/bash

# 索克生活 - 智能体服务停止脚本
# 停止四大智能体服务：小艾、小克、老克、索儿

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 智能体服务配置
AGENT_SERVICES=(
    "xiaoai-service:50051"
    "xiaoke-service:9083"
    "laoke-service:8080"
    "soer-service:8054"
)

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

# 停止智能体服务
stop_agent_service() {
    local service_name=$1
    local port=$2
    
    log_info "停止智能体服务: $service_name (端口: $port)"
    
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
        
        log_success "智能体服务 $service_name 已停止"
    else
        log_warning "智能体服务 $service_name 未在运行"
    fi
}

# 主函数
main() {
    log_info "开始停止智能体服务..."
    
    # 停止所有智能体服务
    for service_config in "${AGENT_SERVICES[@]}"; do
        IFS=':' read -r service_name port <<< "$service_config"
        stop_agent_service "$service_name" "$port"
    done
    
    log_success "所有智能体服务已停止"
}

# 执行主函数
main "$@"