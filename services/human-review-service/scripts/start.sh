#!/bin/bash

# 人工审核服务启动脚本
# 用于快速启动开发环境

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
    
    # 检查UV
    if ! command -v uv &> /dev/null; then
        log_warning "UV 未安装，将使用 pip 安装依赖"
    fi
    
    log_success "依赖检查完成"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    mkdir -p logs
    mkdir -p storage
    mkdir -p models/text
    mkdir -p models/image
    mkdir -p config
    
    log_success "目录创建完成"
}

# 复制配置文件
setup_config() {
    log_info "设置配置文件..."
    
    if [ ! -f .env ]; then
        if [ -f env.example ]; then
            cp env.example .env
            log_success "已复制 env.example 到 .env"
            log_warning "请根据需要修改 .env 文件中的配置"
        else
            log_error "env.example 文件不存在"
            exit 1
        fi
    else
        log_info ".env 文件已存在，跳过复制"
    fi
}

# 创建Redis配置
create_redis_config() {
    log_info "创建Redis配置..."
    
    cat > config/redis.conf << EOF
# Redis配置文件
bind 0.0.0.0
port 6379
timeout 0
tcp-keepalive 300
daemonize no
supervised no
pidfile /var/run/redis_6379.pid
loglevel notice
logfile ""
databases 16
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir ./
maxmemory 256mb
maxmemory-policy allkeys-lru
EOF
    
    log_success "Redis配置创建完成"
}

# 安装Python依赖
install_dependencies() {
    log_info "安装Python依赖..."
    
    if command -v uv &> /dev/null; then
        log_info "使用UV安装依赖..."
        uv sync
    else
        log_info "使用pip安装依赖..."
        pip install -r requirements.txt
    fi
    
    log_success "Python依赖安装完成"
}

# 启动基础设施服务
start_infrastructure() {
    log_info "启动基础设施服务..."
    
    # 启动数据库、Redis等基础服务
    docker-compose up -d postgres redis rabbitmq minio
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    if docker-compose ps | grep -q "Up"; then
        log_success "基础设施服务启动成功"
    else
        log_error "基础设施服务启动失败"
        docker-compose logs
        exit 1
    fi
}

# 初始化数据库
init_database() {
    log_info "初始化数据库..."
    
    # 等待PostgreSQL完全启动
    log_info "等待PostgreSQL启动..."
    sleep 5
    
    # 检查数据库连接
    if docker-compose exec -T postgres pg_isready -U postgres; then
        log_success "数据库连接正常"
    else
        log_error "数据库连接失败"
        exit 1
    fi
    
    log_success "数据库初始化完成"
}

# 启动应用服务
start_application() {
    log_info "启动应用服务..."
    
    # 启动主应用和Worker
    docker-compose up -d human-review-service celery-review-worker celery-ai-worker celery-workflow-worker celery-beat
    
    # 等待应用启动
    log_info "等待应用启动..."
    sleep 15
    
    # 检查应用健康状态
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "应用服务启动成功"
    else
        log_warning "应用服务可能还在启动中，请稍后检查"
    fi
}

# 启动监控服务
start_monitoring() {
    log_info "启动监控服务..."
    
    # 启动监控相关服务
    docker-compose up -d prometheus grafana jaeger flower
    
    log_success "监控服务启动完成"
}

# 显示服务信息
show_services_info() {
    log_info "服务信息："
    echo ""
    echo "🚀 主要服务："
    echo "   - 人工审核API: http://localhost:8000"
    echo "   - API文档: http://localhost:8000/docs"
    echo "   - 健康检查: http://localhost:8000/health"
    echo ""
    echo "📊 监控服务："
    echo "   - Flower (Celery监控): http://localhost:5555"
    echo "   - Prometheus: http://localhost:9090"
    echo "   - Grafana: http://localhost:3000 (admin/admin123)"
    echo "   - Jaeger: http://localhost:16686"
    echo ""
    echo "🗄️ 数据服务："
    echo "   - PostgreSQL: localhost:5432 (postgres/password)"
    echo "   - Redis: localhost:6379"
    echo "   - RabbitMQ管理界面: http://localhost:15672 (admin/password)"
    echo "   - MinIO: http://localhost:9001 (minioadmin/minioadmin123)"
    echo ""
    echo "📝 日志查看："
    echo "   docker-compose logs -f [service_name]"
    echo ""
    echo "🛑 停止服务："
    echo "   docker-compose down"
    echo ""
}

# 主函数
main() {
    log_info "开始启动人工审核服务..."
    echo ""
    
    # 检查依赖
    check_dependencies
    
    # 创建目录和配置
    create_directories
    setup_config
    create_redis_config
    
    # 启动服务
    start_infrastructure
    init_database
    start_application
    start_monitoring
    
    echo ""
    log_success "🎉 人工审核服务启动完成！"
    echo ""
    
    # 显示服务信息
    show_services_info
}

# 处理命令行参数
case "${1:-}" in
    "stop")
        log_info "停止所有服务..."
        docker-compose down
        log_success "服务已停止"
        ;;
    "restart")
        log_info "重启服务..."
        docker-compose down
        sleep 2
        main
        ;;
    "logs")
        docker-compose logs -f "${2:-}"
        ;;
    "status")
        docker-compose ps
        ;;
    "clean")
        log_warning "清理所有数据和容器..."
        read -p "确定要清理所有数据吗？(y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down -v
            docker system prune -f
            log_success "清理完成"
        else
            log_info "取消清理"
        fi
        ;;
    "help"|"-h"|"--help")
        echo "人工审核服务启动脚本"
        echo ""
        echo "用法: $0 [命令]"
        echo ""
        echo "命令："
        echo "  (无参数)  启动所有服务"
        echo "  stop      停止所有服务"
        echo "  restart   重启所有服务"
        echo "  logs      查看日志 (可指定服务名)"
        echo "  status    查看服务状态"
        echo "  clean     清理所有数据和容器"
        echo "  help      显示此帮助信息"
        echo ""
        ;;
    *)
        main
        ;;
esac 