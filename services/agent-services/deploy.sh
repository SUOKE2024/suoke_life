#!/bin/bash

# 索克生活人工审核系统自动化部署脚本
# Suoke Life Human Review System Deployment Script
# 
# 使用方法: ./deploy.sh [环境] [操作]
# 环境: dev, staging, production
# 操作: deploy, update, rollback, stop, logs

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

# 配置变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="suoke-review"
ENVIRONMENT=${1:-production}
ACTION=${2:-deploy}

# 环境配置文件
ENV_FILE=".env.${ENVIRONMENT}"
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"

# 检查参数
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|production)$ ]]; then
    log_error "无效的环境参数: $ENVIRONMENT"
    log_info "支持的环境: dev, staging, production"
    exit 1
fi

if [[ ! "$ACTION" =~ ^(deploy|update|rollback|stop|logs|status|backup)$ ]]; then
    log_error "无效的操作参数: $ACTION"
    log_info "支持的操作: deploy, update, rollback, stop, logs, status, backup"
    exit 1
fi

# 检查依赖
check_dependencies() {
    log_info "检查系统依赖..."
    
    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    # 检查 Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    # 检查环境文件
    if [[ ! -f "$ENV_FILE" ]]; then
        log_error "环境配置文件不存在: $ENV_FILE"
        log_info "请创建环境配置文件，参考 .env.example"
        exit 1
    fi
    
    log_success "依赖检查通过"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    # 数据目录
    sudo mkdir -p /var/lib/suoke/{postgres,redis,prometheus,grafana}
    sudo mkdir -p /var/log/suoke
    sudo mkdir -p /etc/suoke
    
    # 项目目录
    mkdir -p {logs,backup,static,uploads,ssl}
    mkdir -p {nginx/conf.d,monitoring/grafana/{dashboards,datasources}}
    mkdir -p scripts
    
    # 设置权限
    sudo chown -R $USER:$USER /var/lib/suoke
    sudo chown -R $USER:$USER /var/log/suoke
    
    log_success "目录创建完成"
}

# 生成配置文件
generate_configs() {
    log_info "生成配置文件..."
    
    # Nginx 配置
    cat > nginx/nginx.conf << 'EOF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    
    # 基本设置
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 16M;
    
    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # 包含站点配置
    include /etc/nginx/conf.d/*.conf;
}
EOF

    # 站点配置
    cat > nginx/conf.d/suoke-review.conf << 'EOF'
# 审核系统主站点
server {
    listen 80;
    server_name review.suoke.life;
    
    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name review.suoke.life;
    
    # SSL 配置
    ssl_certificate /etc/nginx/ssl/suoke.crt;
    ssl_certificate_key /etc/nginx/ssl/suoke.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # 静态文件
    location /static/ {
        alias /var/www/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # API 代理
    location /api/ {
        proxy_pass http://review_agent:8080/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Web 界面
    location / {
        proxy_pass http://review_dashboard:5001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # 健康检查
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

    # Prometheus 配置
    cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node_exporter:9100']

  - job_name: 'review-agent'
    static_configs:
      - targets: ['review_agent:8080']
    metrics_path: '/metrics'

  - job_name: 'review-dashboard'
    static_configs:
      - targets: ['review_dashboard:5001']
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
EOF

    log_success "配置文件生成完成"
}

# 构建 Docker 镜像
build_images() {
    log_info "构建 Docker 镜像..."
    
    # 创建 Dockerfile for review agent
    cat > Dockerfile.review_agent << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY human_review_a2a_agent.py .
COPY production_config.py .
COPY review_integration_workflows.py .

# 创建必要目录
RUN mkdir -p logs uploads

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 启动命令
CMD ["python", "human_review_a2a_agent.py"]
EOF

    # 创建 Dockerfile for dashboard
    cat > Dockerfile.dashboard << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY human_review_dashboard.py .
COPY production_config.py .

# 创建必要目录
RUN mkdir -p static logs

# 暴露端口
EXPOSE 5001

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# 启动命令
CMD ["python", "human_review_dashboard.py"]
EOF

    # 创建 requirements.txt
    cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1
pydantic==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
flask==3.0.0
flask-socketio==5.3.6
python-socketio==5.10.0
requests==2.31.0
prometheus-client==0.19.0
structlog==23.2.0
python-dotenv==1.0.0
asyncpg==0.29.0
aioredis==2.0.1
celery==5.3.4
kombu==5.3.4
EOF

    # 构建镜像
    docker-compose -f $DOCKER_COMPOSE_FILE build
    
    log_success "镜像构建完成"
}

# 部署服务
deploy_services() {
    log_info "部署服务到 $ENVIRONMENT 环境..."
    
    # 加载环境变量
    export $(cat $ENV_FILE | xargs)
    
    # 停止现有服务
    docker-compose -f $DOCKER_COMPOSE_FILE down
    
    # 启动服务
    docker-compose -f $DOCKER_COMPOSE_FILE up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 检查服务状态
    check_services_health
    
    log_success "服务部署完成"
}

# 更新服务
update_services() {
    log_info "更新服务..."
    
    # 拉取最新镜像
    docker-compose -f $DOCKER_COMPOSE_FILE pull
    
    # 重新构建自定义镜像
    build_images
    
    # 滚动更新
    docker-compose -f $DOCKER_COMPOSE_FILE up -d --force-recreate
    
    log_success "服务更新完成"
}

# 检查服务健康状态
check_services_health() {
    log_info "检查服务健康状态..."
    
    local services=("postgres" "redis" "review_agent" "review_dashboard" "nginx")
    local failed_services=()
    
    for service in "${services[@]}"; do
        if docker-compose -f $DOCKER_COMPOSE_FILE ps $service | grep -q "Up"; then
            log_success "$service: 运行正常"
        else
            log_error "$service: 运行异常"
            failed_services+=($service)
        fi
    done
    
    if [ ${#failed_services[@]} -eq 0 ]; then
        log_success "所有服务运行正常"
        return 0
    else
        log_error "以下服务运行异常: ${failed_services[*]}"
        return 1
    fi
}

# 回滚服务
rollback_services() {
    log_warning "回滚服务..."
    
    # 这里应该实现具体的回滚逻辑
    # 例如：恢复到上一个版本的镜像
    log_info "回滚功能待实现"
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    docker-compose -f $DOCKER_COMPOSE_FILE down
    log_success "服务已停止"
}

# 查看日志
view_logs() {
    local service=${3:-}
    if [[ -n "$service" ]]; then
        docker-compose -f $DOCKER_COMPOSE_FILE logs -f $service
    else
        docker-compose -f $DOCKER_COMPOSE_FILE logs -f
    fi
}

# 查看状态
show_status() {
    log_info "服务状态:"
    docker-compose -f $DOCKER_COMPOSE_FILE ps
    
    log_info "系统资源使用:"
    docker stats --no-stream
}

# 备份数据
backup_data() {
    log_info "备份数据..."
    
    local backup_dir="backup/$(date +%Y%m%d_%H%M%S)"
    mkdir -p $backup_dir
    
    # 备份数据库
    docker-compose -f $DOCKER_COMPOSE_FILE exec -T postgres pg_dump -U suoke_user suoke_review > $backup_dir/database.sql
    
    # 备份配置文件
    cp -r nginx monitoring $backup_dir/
    
    # 压缩备份
    tar -czf $backup_dir.tar.gz $backup_dir
    rm -rf $backup_dir
    
    log_success "备份完成: $backup_dir.tar.gz"
}

# 主函数
main() {
    log_info "开始执行 $ACTION 操作 (环境: $ENVIRONMENT)"
    
    case $ACTION in
        deploy)
            check_dependencies
            create_directories
            generate_configs
            build_images
            deploy_services
            ;;
        update)
            check_dependencies
            update_services
            ;;
        rollback)
            rollback_services
            ;;
        stop)
            stop_services
            ;;
        logs)
            view_logs
            ;;
        status)
            show_status
            ;;
        backup)
            backup_data
            ;;
        *)
            log_error "未知操作: $ACTION"
            exit 1
            ;;
    esac
    
    log_success "操作完成!"
}

# 信号处理
trap 'log_error "脚本被中断"; exit 1' INT TERM

# 执行主函数
main "$@" 