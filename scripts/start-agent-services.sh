#!/bin/bash

# 索克生活 - 智能体服务启动脚本
# 启动四大智能体服务：小艾、小克、老克、索儿

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

# 检查服务状态
check_agent_status() {
    local service_name=$1
    local port=$2
    
    if curl -s -f "http://localhost:${port}/health" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# 启动智能体服务
start_agent_service() {
    local service_name=$1
    local port=$2
    
    log_info "启动智能体服务: $service_name (端口: $port)"
    
    # 检查服务是否已经运行
    if check_agent_status "$service_name" "$port"; then
        log_warning "智能体服务 $service_name 已经在运行"
        return 0
    fi
    
    # 进入服务目录
    local service_dir="services/agent-services/$service_name"
    
    if [ ! -d "$service_dir" ]; then
        log_error "服务目录不存在: $service_dir"
        return 1
    fi
    
    cd "$service_dir"
    
    # 检查并安装依赖
    if [ -f "pyproject.toml" ]; then
        log_info "使用 UV 安装依赖..."
        uv sync --quiet 2>/dev/null || log_warning "依赖安装失败"
        
        # 启动服务
        log_info "启动服务..."
        uv run python -m ${service_name//-/_}.cmd.server run > "logs/${service_name}.log" 2>&1 &
    elif [ -f "requirements.txt" ]; then
        log_info "使用 pip 安装依赖..."
        pip install -r requirements.txt --quiet 2>/dev/null || log_warning "依赖安装失败"
        
        # 启动服务
        log_info "启动服务..."
        python3 -m ${service_name//-/_} > "logs/${service_name}.log" 2>&1 &
    else
        log_warning "未找到依赖文件，尝试直接启动..."
        python3 -m ${service_name//-/_} > "logs/${service_name}.log" 2>&1 &
    fi
    
    cd - > /dev/null
    
    # 等待服务启动
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if check_agent_status "$service_name" "$port"; then
            log_success "智能体服务 $service_name 启动成功"
            return 0
        fi
        sleep 1
        ((attempt++))
    done
    
    log_error "智能体服务 $service_name 启动失败"
    return 1
}

# 创建日志目录
create_log_directories() {
    for service_config in "${AGENT_SERVICES[@]}"; do
        IFS=':' read -r service_name port <<< "$service_config"
        local log_dir="services/agent-services/$service_name/logs"
        
        if [ ! -d "$log_dir" ]; then
            mkdir -p "$log_dir"
            log_info "创建日志目录: $log_dir"
        fi
    done
}

# 主函数
main() {
    log_info "开始启动智能体服务..."
    
    # 创建日志目录
    create_log_directories
    
    # 启动所有智能体服务
    local success_count=0
    local total_count=${#AGENT_SERVICES[@]}
    
    for service_config in "${AGENT_SERVICES[@]}"; do
        IFS=':' read -r service_name port <<< "$service_config"
        
        if start_agent_service "$service_name" "$port"; then
            ((success_count++))
        fi
    done
    
    # 显示启动结果
    echo ""
    log_info "智能体服务启动完成"
    log_info "成功启动: $success_count/$total_count 个服务"
    
    if [ $success_count -eq $total_count ]; then
        log_success "所有智能体服务启动成功！"
        
        echo ""
        echo "智能体服务访问地址："
        for service_config in "${AGENT_SERVICES[@]}"; do
            IFS=':' read -r service_name port <<< "$service_config"
            echo "  - $service_name: http://localhost:$port"
        done
        
    else
        log_warning "部分智能体服务启动失败，请检查日志"
        echo ""
        echo "查看日志命令："
        for service_config in "${AGENT_SERVICES[@]}"; do
            IFS=':' read -r service_name port <<< "$service_config"
            echo "  tail -f services/agent-services/$service_name/logs/${service_name}.log"
        done
    fi
}

# 执行主函数
main "$@" 