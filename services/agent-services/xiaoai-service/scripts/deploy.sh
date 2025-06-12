#!/bin/bash

# 小艾智能体自动部署脚本
# 用于快速部署生产环境

set -e  # 遇到错误立即退出

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

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "请不要使用root用户运行此脚本"
        exit 1
    fi
}

# 检查系统要求
check_system_requirements() {
    log_info "检查系统要求..."
    
    # 检查操作系统
    if [[ ! -f /etc/os-release ]]; then
        log_error "不支持的操作系统"
        exit 1
    fi
    
    # 检查内存
    MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
    if [[ $MEMORY_GB -lt 4 ]]; then
        log_warning "内存不足4GB，建议至少8GB"
    fi
    
    # 检查磁盘空间
    DISK_SPACE=$(df -BG / | awk 'NR==2{print $4}' | sed 's/G//')
    if [[ $DISK_SPACE -lt 20 ]]; then
        log_error "磁盘空间不足20GB"
        exit 1
    fi
    
    log_success "系统要求检查通过"
}

# 安装Docker
install_docker() {
    if command -v docker &> /dev/null; then
        log_info "Docker已安装，版本: $(docker --version)"
        return
    fi
    
    log_info "安装Docker..."
    
    # 更新包索引
    sudo apt-get update
    
    # 安装必要的包
    sudo apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # 添加Docker官方GPG密钥
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # 设置稳定版仓库
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # 安装Docker Engine
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    
    # 将当前用户添加到docker组
    sudo usermod -aG docker $USER
    
    log_success "Docker安装完成"
}

# 安装Docker Compose
install_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        log_info "Docker Compose已安装，版本: $(docker-compose --version)"
        return
    fi
    
    log_info "安装Docker Compose..."
    
    # 下载Docker Compose
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    # 添加执行权限
    sudo chmod +x /usr/local/bin/docker-compose
    
    log_success "Docker Compose安装完成"
}

# 创建部署目录
create_deployment_directory() {
    DEPLOY_DIR="/opt/xiaoai-service"
    
    log_info "创建部署目录: $DEPLOY_DIR"
    
    if [[ ! -d $DEPLOY_DIR ]]; then
        sudo mkdir -p $DEPLOY_DIR
        sudo chown $USER:$USER $DEPLOY_DIR
    fi
    
    cd $DEPLOY_DIR
    log_success "部署目录创建完成"
}

# 生成配置文件
generate_config() {
    log_info "生成配置文件..."
    
    # 生成随机密钥
    SECRET_KEY=$(openssl rand -hex 32)
    JWT_SECRET=$(openssl rand -hex 32)
    ENCRYPTION_KEY=$(openssl rand -hex 16)
    DB_PASSWORD=$(openssl rand -hex 16)
    REDIS_PASSWORD=$(openssl rand -hex 16)
    
    # 创建.env文件
    cat > .env << EOF
# 生产环境配置文件
ENVIRONMENT=production
APP_NAME=xiaoai-service
APP_VERSION=1.0.0
DEBUG=false
LOG_LEVEL=INFO

# 服务端口
HTTP_PORT=8000
GRPC_PORT=50051

# 数据库配置
DATABASE_URL=postgresql://xiaoai:${DB_PASSWORD}@postgres:5432/xiaoai_db
DB_PASSWORD=${DB_PASSWORD}
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30

# Redis配置
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
REDIS_PASSWORD=${REDIS_PASSWORD}
REDIS_MAX_CONNECTIONS=50

# 安全配置
SECRET_KEY=${SECRET_KEY}
JWT_SECRET=${JWT_SECRET}
JWT_EXPIRE_HOURS=24
ENCRYPTION_KEY=${ENCRYPTION_KEY}

# AI模型配置
AI_MODEL_PATH=/app/models
MODEL_CACHE_SIZE=1000
MODEL_TIMEOUT=30

# 性能配置
WORKER_PROCESSES=4
MAX_REQUESTS=1000
REQUEST_TIMEOUT=30
KEEPALIVE_TIMEOUT=5

# 监控配置
ENABLE_METRICS=true
METRICS_PORT=9090
HEALTH_CHECK_INTERVAL=30

# 日志配置
LOG_FORMAT=json
LOG_FILE=/app/logs/xiaoai.log
LOG_MAX_SIZE=100MB
LOG_BACKUP_COUNT=10

# 限流配置
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# CORS配置
CORS_ORIGINS=*
CORS_METHODS=GET,POST,PUT,DELETE
CORS_HEADERS=Content-Type,Authorization

# 文件上传配置
MAX_FILE_SIZE=10MB
ALLOWED_FILE_TYPES=jpg,jpeg,png,wav,mp3,mp4

# 缓存配置
CACHE_TTL=3600
CACHE_MAX_SIZE=1000

# 外部服务配置
EXTERNAL_API_TIMEOUT=10
EXTERNAL_API_RETRIES=3
EOF
    
    log_success "配置文件生成完成"
}

# 生成SSL证书
generate_ssl_certificate() {
    log_info "生成SSL证书..."
    
    mkdir -p ssl
    
    # 生成自签名证书（生产环境建议使用Let's Encrypt）
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/key.pem -out ssl/cert.pem \
        -subj "/C=CN/ST=Beijing/L=Beijing/O=XiaoAI/CN=localhost" \
        2>/dev/null
    
    log_success "SSL证书生成完成"
    log_warning "生产环境请使用Let's Encrypt或购买正式证书"
}

# 创建必要目录
create_directories() {
    log_info "创建必要目录..."
    
    mkdir -p {logs,models,data,ssl}
    chmod 755 logs models data ssl
    
    log_success "目录创建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 构建并启动服务
    docker-compose -f docker-compose.prod.yml up -d --build
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 检查服务状态
    if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        log_success "服务启动成功"
    else
        log_error "服务启动失败"
        docker-compose -f docker-compose.prod.yml logs
        exit 1
    fi
}

# 初始化数据库
initialize_database() {
    log_info "初始化数据库..."
    
    # 等待数据库完全启动
    sleep 10
    
    # 运行数据库迁移
    docker-compose -f docker-compose.prod.yml exec -T xiaoai-service \
        python -m alembic upgrade head
    
    log_success "数据库初始化完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 等待服务完全启动
    sleep 10
    
    # 检查健康端点
    if curl -f http://localhost/health &>/dev/null; then
        log_success "健康检查通过"
    else
        log_error "健康检查失败"
        exit 1
    fi
}

# 显示部署信息
show_deployment_info() {
    log_success "部署完成！"
    echo
    echo "==================================="
    echo "小艾智能体部署信息"
    echo "==================================="
    echo "服务地址: https://localhost"
    echo "健康检查: https://localhost/health"
    echo "API文档: https://localhost/docs"
    echo "指标监控: http://localhost:9090/metrics"
    echo
    echo "配置文件: $(pwd)/.env"
    echo "日志目录: $(pwd)/logs"
    echo "数据目录: $(pwd)/data"
    echo
    echo "常用命令:"
    echo "  查看服务状态: docker-compose -f docker-compose.prod.yml ps"
    echo "  查看日志: docker-compose -f docker-compose.prod.yml logs -f"
    echo "  重启服务: docker-compose -f docker-compose.prod.yml restart"
    echo "  停止服务: docker-compose -f docker-compose.prod.yml down"
    echo "==================================="
}

# 主函数
main() {
    log_info "开始部署小艾智能体..."
    
    check_root
    check_system_requirements
    install_docker
    install_docker_compose
    create_deployment_directory
    generate_config
    generate_ssl_certificate
    create_directories
    start_services
    initialize_database
    health_check
    show_deployment_info
    
    log_success "部署完成！"
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi