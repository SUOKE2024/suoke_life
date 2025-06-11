#!/bin/bash

# 索克生活 - 新增服务部署脚本
# Deploy Additional Services Script

set -e

echo "🚀 开始部署索克生活新增服务..."

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

# 检查Docker环境
check_docker() {
    log_info "检查Docker环境..."
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    log_success "Docker环境检查通过"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    directories=(
        "logs/five-diagnosis-orchestrator"
        "logs/diagnostic-gateway"
        "logs/service-registry"
        "logs/calculation-optimizer"
        "data/service-registry"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        log_info "创建目录: $dir"
    done
    
    log_success "目录创建完成"
}

# 构建Docker镜像
build_images() {
    log_info "构建Docker镜像..."
    
    # 构建五诊协调器
    log_info "构建五诊协调器镜像..."
    docker build -t suoke/five-diagnosis-orchestrator:latest \
        ./services/diagnostic-services/five-diagnosis-orchestrator/
    
    # 构建服务注册中心
    log_info "构建服务注册中心镜像..."
    docker build -t suoke/service-registry:latest \
        ./services/common/service-registry/
    
    # 构建诊断网关（如果存在Dockerfile）
    if [ -f "./services/diagnostic-services/common/gateway/Dockerfile" ]; then
        log_info "构建诊断网关镜像..."
        docker build -t suoke/diagnostic-gateway:latest \
            ./services/diagnostic-services/common/gateway/
    fi
    
    log_success "Docker镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动新增服务..."
    
    # 使用docker-compose启动服务
    docker-compose -f docker-compose.additional-services.yml up -d
    
    log_success "服务启动完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    services=(
        "http://localhost:8080/health:五诊协调器"
        "http://localhost:8500/health:服务注册中心"
        "http://localhost:8081/health:诊断网关"
        "http://localhost:8082/health:算诊优化器"
    )
    
    for service in "${services[@]}"; do
        url=$(echo $service | cut -d: -f1-3)
        name=$(echo $service | cut -d: -f4)
        
        log_info "检查 $name 健康状态..."
        
        # 等待服务启动
        sleep 10
        
        # 尝试健康检查
        if curl -f "$url" &> /dev/null; then
            log_success "$name 健康检查通过"
        else
            log_warning "$name 健康检查失败，可能仍在启动中"
        fi
    done
}

# 显示服务状态
show_status() {
    log_info "显示服务状态..."
    docker-compose -f docker-compose.additional-services.yml ps
}

# 主函数
main() {
    echo "======================================"
    echo "   索克生活 - 新增服务部署脚本"
    echo "======================================"
    echo ""
    
    check_docker
    create_directories
    build_images
    start_services
    health_check
    show_status
    
    echo ""
    log_success "🎉 新增服务部署完成！"
    echo ""
    echo "服务访问地址："
    echo "  - 五诊协调器: http://localhost:8080"
    echo "  - 服务注册中心: http://localhost:8500"
    echo "  - 诊断网关: http://localhost:8081"
    echo "  - 算诊优化器: http://localhost:8082"
    echo ""
    echo "查看日志："
    echo "  docker-compose -f docker-compose.additional-services.yml logs -f [service-name]"
    echo ""
    echo "停止服务："
    echo "  docker-compose -f docker-compose.additional-services.yml down"
}

# 执行主函数
main "$@" 