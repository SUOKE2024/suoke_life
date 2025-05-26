#!/bin/bash

# Integration Service 启动脚本

set -e

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

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    log_success "依赖检查完成"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    mkdir -p logs
    mkdir -p data/postgres
    mkdir -p data/redis
    mkdir -p data/prometheus
    mkdir -p data/grafana
    
    log_success "目录创建完成"
}

# 检查配置文件
check_config() {
    log_info "检查配置文件..."
    
    if [ ! -f "config/config.yaml" ]; then
        log_warning "配置文件不存在，使用默认配置"
        cp config/config.yaml.example config/config.yaml 2>/dev/null || true
    fi
    
    log_success "配置检查完成"
}

# 构建镜像
build_image() {
    log_info "构建 Docker 镜像..."
    
    docker build -t integration-service:latest .
    
    log_success "镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    cd deploy/docker
    docker-compose up -d
    
    log_success "服务启动完成"
}

# 等待服务就绪
wait_for_services() {
    log_info "等待服务就绪..."
    
    # 等待数据库
    log_info "等待 PostgreSQL..."
    timeout 60 bash -c 'until docker-compose exec -T postgres pg_isready -U postgres; do sleep 2; done'
    
    # 等待Redis
    log_info "等待 Redis..."
    timeout 60 bash -c 'until docker-compose exec -T redis redis-cli ping; do sleep 2; done'
    
    # 等待应用服务
    log_info "等待 Integration Service..."
    timeout 120 bash -c 'until curl -f http://localhost:8090/health; do sleep 5; done'
    
    log_success "所有服务已就绪"
}

# 显示服务状态
show_status() {
    log_info "服务状态:"
    
    cd deploy/docker
    docker-compose ps
    
    echo ""
    log_info "服务访问地址:"
    echo "  - Integration Service API: http://localhost:8090"
    echo "  - API 文档: http://localhost:8090/docs"
    echo "  - 健康检查: http://localhost:8090/health"
    echo "  - Prometheus: http://localhost:9091"
    echo "  - Grafana: http://localhost:3000 (admin/admin)"
    echo "  - PostgreSQL: localhost:5432"
    echo "  - Redis: localhost:6379"
}

# 主函数
main() {
    log_info "开始启动 Integration Service..."
    
    check_dependencies
    create_directories
    check_config
    build_image
    start_services
    wait_for_services
    show_status
    
    log_success "Integration Service 启动完成！"
}

# 处理参数
case "${1:-}" in
    "stop")
        log_info "停止服务..."
        cd deploy/docker
        docker-compose down
        log_success "服务已停止"
        ;;
    "restart")
        log_info "重启服务..."
        cd deploy/docker
        docker-compose down
        cd ../..
        main
        ;;
    "logs")
        log_info "查看日志..."
        cd deploy/docker
        docker-compose logs -f integration-service
        ;;
    "status")
        cd deploy/docker
        show_status
        ;;
    *)
        main
        ;;
esac 