#!/bin/bash

# 智能体服务停止脚本
# 用于停止所有运行的智能体服务

set -e

echo "🛑 正在停止索克生活智能体服务..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# 停止单个容器
stop_container() {
    local container_name=$1
    local service_name=$2
    
    if docker ps --filter "name=$container_name" --format "table {{.Names}}" | grep -q "$container_name"; then
        log_info "停止 $service_name..."
        docker stop "$container_name" > /dev/null 2>&1
        docker rm "$container_name" > /dev/null 2>&1
        log_success "$service_name 已停止"
    else
        log_warning "$service_name 未运行"
    fi
}

# 停止所有智能体服务
stop_agent_services() {
    log_info "停止智能体服务..."
    
    stop_container "xiaoai-service" "小艾服务"
    stop_container "xiaoke-service" "小克服务"
    stop_container "laoke-service" "老克服务"
    stop_container "soer-service" "索儿服务"
}

# 停止基础设施服务
stop_infrastructure() {
    log_info "停止基础设施服务..."
    
    stop_container "suoke-postgres" "PostgreSQL数据库"
    stop_container "suoke-redis" "Redis缓存"
}

# 清理网络和数据卷
cleanup() {
    log_info "清理网络和数据卷..."
    
    # 移除网络
    if docker network ls --filter "name=suoke-network" --format "table {{.Name}}" | grep -q "suoke-network"; then
        docker network rm suoke-network > /dev/null 2>&1
        log_success "已移除 suoke-network 网络"
    fi
    
    # 可选：清理数据卷
    read -p "是否要删除数据库数据卷? 这将永久删除所有数据 (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker volume rm suoke_postgres_data > /dev/null 2>&1 || true
        log_warning "已删除数据库数据卷"
    fi
}

# 显示停止状态
show_status() {
    echo
    echo "================================"
    echo "🔴 索克生活智能体服务状态"
    echo "================================"
    
    local services=("xiaoai-service:小艾服务" "xiaoke-service:小克服务" "laoke-service:老克服务" "soer-service:索儿服务" "suoke-postgres:PostgreSQL" "suoke-redis:Redis")
    
    for service in "${services[@]}"; do
        IFS=':' read -r container name <<< "$service"
        
        if docker ps --filter "name=$container" --format "table {{.Names}}" | grep -q "$container"; then
            echo -e "🟡 $name: ${YELLOW}仍在运行${NC}"
        else
            echo -e "⚫ $name: ${GREEN}已停止${NC}"
        fi
    done
    
    echo
    echo "📖 提示:"
    echo "- 运行 'npm run start:agents' 重新启动服务"
    echo "- 运行 'docker ps' 查看运行中的容器"
    echo
}

# 主函数
main() {
    log_info "开始停止智能体服务"
    
    # 停止服务
    stop_agent_services
    stop_infrastructure
    
    # 清理资源
    cleanup
    
    # 显示状态
    show_status
    
    log_success "智能体服务已全部停止！"
}

# 处理命令行参数
if [ "$1" = "--force" ]; then
    log_warning "强制模式：将停止所有相关容器"
    docker stop $(docker ps -q --filter "name=xiaoai-service") 2>/dev/null || true
    docker stop $(docker ps -q --filter "name=xiaoke-service") 2>/dev/null || true
    docker stop $(docker ps -q --filter "name=laoke-service") 2>/dev/null || true
    docker stop $(docker ps -q --filter "name=soer-service") 2>/dev/null || true
    docker stop $(docker ps -q --filter "name=suoke-postgres") 2>/dev/null || true
    docker stop $(docker ps -q --filter "name=suoke-redis") 2>/dev/null || true
    
    docker rm $(docker ps -aq --filter "name=xiaoai-service") 2>/dev/null || true
    docker rm $(docker ps -aq --filter "name=xiaoke-service") 2>/dev/null || true
    docker rm $(docker ps -aq --filter "name=laoke-service") 2>/dev/null || true
    docker rm $(docker ps -aq --filter "name=soer-service") 2>/dev/null || true
    docker rm $(docker ps -aq --filter "name=suoke-postgres") 2>/dev/null || true
    docker rm $(docker ps -aq --filter "name=suoke-redis") 2>/dev/null || true
    
    log_success "强制停止完成"
else
    # 执行主函数
    main "$@"
fi