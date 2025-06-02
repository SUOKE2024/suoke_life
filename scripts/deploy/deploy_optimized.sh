#!/bin/bash

# 索克生活 - 优化部署脚本
# 自动化部署所有优化的服务

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
    log_info "检查部署依赖..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    log_success "依赖检查完成"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    mkdir -p config/postgres
    mkdir -p nginx/conf.d
    mkdir -p nginx/ssl
    mkdir -p monitoring/prometheus
    mkdir -p monitoring/grafana/dashboards
    mkdir -p monitoring/grafana/datasources
    mkdir -p logs
    
    log_success "目录创建完成"
}

# 生成配置文件
generate_configs() {
    log_info "生成配置文件..."
    
    # PostgreSQL初始化脚本
    cat > config/postgres/init.sql << 'EOF'
-- 索克生活数据库初始化脚本

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建健康数据表
CREATE TABLE IF NOT EXISTS health_data (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    data_type VARCHAR(50) NOT NULL,
    data_value JSONB NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建智能体会话表
CREATE TABLE IF NOT EXISTS agent_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    agent_type VARCHAR(20) NOT NULL,
    session_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_health_data_user_id ON health_data(user_id);
CREATE INDEX IF NOT EXISTS idx_health_data_type ON health_data(data_type);
CREATE INDEX IF NOT EXISTS idx_agent_sessions_user_id ON agent_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_agent_sessions_type ON agent_sessions(agent_type);
EOF

    # Nginx配置
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
    
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    gzip on;
    gzip_vary on;
    gzip_min_length 10240;
    gzip_proxied expired no-cache no-store private must-revalidate;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/x-javascript
        application/xml+rss
        application/json;
    
    include /etc/nginx/conf.d/*.conf;
}
EOF

    cat > nginx/conf.d/suoke.conf << 'EOF'
upstream api_gateway {
    server api-gateway:8000;
}

server {
    listen 80;
    server_name localhost;
    
    location / {
        proxy_pass http://api_gateway;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

    # Prometheus配置
    cat > monitoring/prometheus/prometheus.yml << 'EOF'
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

  - job_name: 'api-gateway'
    static_configs:
      - targets: ['api-gateway:8000']
    metrics_path: '/metrics'

  - job_name: 'xiaoai-service'
    static_configs:
      - targets: ['xiaoai-service:8001']
    metrics_path: '/metrics'

  - job_name: 'xiaoke-service'
    static_configs:
      - targets: ['xiaoke-service:8002']
    metrics_path: '/metrics'

  - job_name: 'laoke-service'
    static_configs:
      - targets: ['laoke-service:8003']
    metrics_path: '/metrics'

  - job_name: 'soer-service'
    static_configs:
      - targets: ['soer-service:8004']
    metrics_path: '/metrics'
EOF

    log_success "配置文件生成完成"
}

# 构建Docker镜像
build_images() {
    log_info "构建Docker镜像..."
    
    # 构建API网关
    log_info "构建API网关镜像..."
    docker build -t suoke/api-gateway:optimized -f services/api-gateway/Dockerfile.optimized services/api-gateway/
    
    # 构建智能体服务
    log_info "构建小艾智能体镜像..."
    docker build -t suoke/xiaoai-service:optimized -f services/agent-services/xiaoai-service/Dockerfile.optimized services/agent-services/xiaoai-service/
    
    log_info "构建小克智能体镜像..."
    docker build -t suoke/xiaoke-service:optimized -f services/agent-services/xiaoke-service/Dockerfile.optimized services/agent-services/xiaoke-service/
    
    log_info "构建老克智能体镜像..."
    docker build -t suoke/laoke-service:optimized -f services/agent-services/laoke-service/Dockerfile.optimized services/agent-services/laoke-service/
    
    log_info "构建索儿智能体镜像..."
    docker build -t suoke/soer-service:optimized -f services/agent-services/soer-service/Dockerfile.optimized services/agent-services/soer-service/
    
    # 构建其他服务
    log_info "构建认证服务镜像..."
    docker build -t suoke/auth-service:optimized -f services/auth-service/Dockerfile.optimized services/auth-service/
    
    log_info "构建用户服务镜像..."
    docker build -t suoke/user-service:optimized -f services/user-service/Dockerfile.optimized services/user-service/
    
    log_info "构建健康数据服务镜像..."
    docker build -t suoke/health-data-service:optimized -f services/health-data-service/Dockerfile.optimized services/health-data-service/
    
    log_info "构建医疗资源服务镜像..."
    docker build -t suoke/medical-resource-service:optimized -f services/medical-resource-service/Dockerfile.optimized services/medical-resource-service/
    
    log_success "Docker镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动优化服务..."
    
    # 停止现有服务
    docker-compose -f docker-compose.optimized-complete.yml down
    
    # 启动新服务
    docker-compose -f docker-compose.optimized-complete.yml up -d
    
    log_success "服务启动完成"
}

# 等待服务就绪
wait_for_services() {
    log_info "等待服务就绪..."
    
    services=(
        "http://localhost:8000/health"  # API网关
        "http://localhost:8001/health"  # 小艾
        "http://localhost:8002/health"  # 小克
        "http://localhost:8003/health"  # 老克
        "http://localhost:8004/health"  # 索儿
    )
    
    for service in "${services[@]}"; do
        log_info "检查服务: $service"
        
        max_attempts=30
        attempt=1
        
        while [ $attempt -le $max_attempts ]; do
            if curl -f -s "$service" > /dev/null 2>&1; then
                log_success "服务就绪: $service"
                break
            fi
            
            if [ $attempt -eq $max_attempts ]; then
                log_error "服务启动超时: $service"
                return 1
            fi
            
            log_info "等待服务启动... (尝试 $attempt/$max_attempts)"
            sleep 10
            ((attempt++))
        done
    done
    
    log_success "所有服务已就绪"
}

# 运行健康检查
health_check() {
    log_info "运行健康检查..."
    
    # 检查容器状态
    log_info "检查容器状态..."
    docker-compose -f docker-compose.optimized-complete.yml ps
    
    # 检查服务响应
    log_info "检查服务响应..."
    
    echo "API网关状态:"
    curl -s http://localhost:8000/health || log_warning "API网关健康检查失败"
    
    echo -e "\n小艾智能体状态:"
    curl -s http://localhost:8001/health || log_warning "小艾智能体健康检查失败"
    
    echo -e "\n小克智能体状态:"
    curl -s http://localhost:8002/health || log_warning "小克智能体健康检查失败"
    
    echo -e "\n老克智能体状态:"
    curl -s http://localhost:8003/health || log_warning "老克智能体健康检查失败"
    
    echo -e "\n索儿智能体状态:"
    curl -s http://localhost:8004/health || log_warning "索儿智能体健康检查失败"
    
    log_success "健康检查完成"
}

# 显示部署信息
show_deployment_info() {
    log_success "索克生活优化部署完成！"
    
    echo -e "\n${GREEN}服务访问地址:${NC}"
    echo "  主应用: http://localhost"
    echo "  API网关: http://localhost:8000"
    echo "  小艾智能体: http://localhost:8001"
    echo "  小克智能体: http://localhost:8002"
    echo "  老克智能体: http://localhost:8003"
    echo "  索儿智能体: http://localhost:8004"
    echo "  Prometheus监控: http://localhost:9090"
    echo "  Grafana可视化: http://localhost:3000 (admin/admin)"
    
    echo -e "\n${GREEN}管理命令:${NC}"
    echo "  查看日志: docker-compose -f docker-compose.optimized-complete.yml logs -f [service_name]"
    echo "  停止服务: docker-compose -f docker-compose.optimized-complete.yml down"
    echo "  重启服务: docker-compose -f docker-compose.optimized-complete.yml restart [service_name]"
    echo "  查看状态: docker-compose -f docker-compose.optimized-complete.yml ps"
}

# 主函数
main() {
    log_info "开始索克生活优化部署..."
    
    check_dependencies
    create_directories
    generate_configs
    build_images
    start_services
    wait_for_services
    health_check
    show_deployment_info
    
    log_success "部署完成！"
}

# 错误处理
trap 'log_error "部署过程中发生错误，请检查日志"; exit 1' ERR

# 执行主函数
main "$@" 