#!/bin/bash

# 索克生活认证服务和用户服务启动脚本
# 作者: 索克生活开发团队
# 版本: 1.0.0

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

# 检查Docker和Docker Compose
check_dependencies() {
    log_info "检查依赖..."
    
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
    
    mkdir -p auth-service/logs
    mkdir -p user-service/logs
    mkdir -p user-service/models
    mkdir -p monitoring
    mkdir -p nginx
    mkdir -p init-scripts
    
    log_success "目录创建完成"
}

# 创建环境配置文件
create_env_files() {
    log_info "创建环境配置文件..."
    
    # Auth Service .env
    if [ ! -f "auth-service/.env" ]; then
        cat > auth-service/.env << EOF
# 数据库配置
DATABASE_URL=postgresql+asyncpg://suoke_user:suoke_password@postgres:5432/suoke_life

# Redis配置
REDIS_URL=redis://:redis_password@redis:6379/0

# JWT配置
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# 邮件配置
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@suokelife.com
EMAIL_FROM_NAME=索克生活

# 应用配置
APP_NAME=索克生活认证服务
APP_VERSION=1.0.0
DEBUG=false
ENVIRONMENT=development

# 安全配置
ALLOWED_HOSTS=*
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# 监控配置
ENABLE_METRICS=true
METRICS_PORT=9090
EOF
        log_success "Auth Service .env 文件已创建"
    fi
    
    # User Service .env
    if [ ! -f "user-service/.env" ]; then
        cat > user-service/.env << EOF
# 数据库配置
DATABASE_URL=postgresql+asyncpg://suoke_user:suoke_password@postgres:5432/suoke_life

# Redis配置
REDIS_URL=redis://:redis_password@redis:6379/1

# 认证服务配置
AUTH_SERVICE_URL=http://auth-service:8000
AUTH_SERVICE_TIMEOUT=30

# 应用配置
APP_NAME=索克生活用户服务
APP_VERSION=1.0.0
DEBUG=false
ENVIRONMENT=development

# 缓存配置
CACHE_TTL=300
CACHE_MAX_CONNECTIONS=20

# 性能配置
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# 监控配置
ENABLE_METRICS=true
METRICS_PORT=9090

# 分析配置
ENABLE_ANALYTICS=true
ML_MODEL_PATH=/app/models
EOF
        log_success "User Service .env 文件已创建"
    fi
}

# 创建Prometheus配置
create_prometheus_config() {
    if [ ! -f "monitoring/prometheus.yml" ]; then
        log_info "创建Prometheus配置..."
        
        cat > monitoring/prometheus.yml << EOF
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

  - job_name: 'auth-service'
    static_configs:
      - targets: ['auth-service:9090']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'user-service'
    static_configs:
      - targets: ['user-service:9090']
    metrics_path: '/metrics'
    scrape_interval: 5s
EOF
        log_success "Prometheus配置已创建"
    fi
}

# 创建Nginx配置
create_nginx_config() {
    if [ ! -f "nginx/nginx.conf" ]; then
        log_info "创建Nginx配置..."
        
        cat > nginx/nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    upstream auth_service {
        server auth-service:8000;
    }
    
    upstream user_service {
        server user-service:8000;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        # Auth Service
        location /auth/ {
            proxy_pass http://auth_service/;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
        
        # User Service
        location /users/ {
            proxy_pass http://user_service/;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
        
        # Health checks
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
EOF
        log_success "Nginx配置已创建"
    fi
}

# 创建数据库初始化脚本
create_init_scripts() {
    if [ ! -f "init-scripts/01-init.sql" ]; then
        log_info "创建数据库初始化脚本..."
        
        cat > init-scripts/01-init.sql << EOF
-- 索克生活数据库初始化脚本

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    is_superuser BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建用户档案表
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    date_of_birth DATE,
    gender VARCHAR(20),
    phone VARCHAR(20),
    avatar_url VARCHAR(500),
    bio TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建健康数据表
CREATE TABLE IF NOT EXISTS health_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    metric_type VARCHAR(50) NOT NULL,
    value JSONB NOT NULL,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_health_data_user_id ON health_data(user_id);
CREATE INDEX IF NOT EXISTS idx_health_data_metric_type ON health_data(metric_type);
CREATE INDEX IF NOT EXISTS idx_health_data_recorded_at ON health_data(recorded_at);

-- 创建更新时间触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS \$\$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
\$\$ language 'plpgsql';

-- 创建触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
EOF
        log_success "数据库初始化脚本已创建"
    fi
}

# 构建和启动服务
start_services() {
    log_info "构建和启动服务..."
    
    # 停止现有服务
    docker-compose -f docker-compose.auth-user-services.yml down
    
    # 构建镜像
    log_info "构建Docker镜像..."
    docker-compose -f docker-compose.auth-user-services.yml build
    
    # 启动服务
    log_info "启动服务..."
    docker-compose -f docker-compose.auth-user-services.yml up -d
    
    log_success "服务启动完成"
}

# 等待服务就绪
wait_for_services() {
    log_info "等待服务就绪..."
    
    # 等待数据库
    log_info "等待PostgreSQL..."
    while ! docker exec suoke_postgres pg_isready -U suoke_user -d suoke_life > /dev/null 2>&1; do
        sleep 2
    done
    log_success "PostgreSQL 已就绪"
    
    # 等待Redis
    log_info "等待Redis..."
    while ! docker exec suoke_redis redis-cli -a redis_password ping > /dev/null 2>&1; do
        sleep 2
    done
    log_success "Redis 已就绪"
    
    # 等待认证服务
    log_info "等待认证服务..."
    while ! curl -f http://localhost:8001/health > /dev/null 2>&1; do
        sleep 5
    done
    log_success "认证服务已就绪"
    
    # 等待用户服务
    log_info "等待用户服务..."
    while ! curl -f http://localhost:8002/health > /dev/null 2>&1; do
        sleep 5
    done
    log_success "用户服务已就绪"
}

# 显示服务信息
show_service_info() {
    log_success "所有服务已启动完成！"
    echo
    echo "服务访问地址:"
    echo "  认证服务:     http://localhost:8001"
    echo "  用户服务:     http://localhost:8002"
    echo "  Nginx代理:    http://localhost:80"
    echo "  Prometheus:   http://localhost:9090"
    echo "  Grafana:      http://localhost:3000 (admin/admin)"
    echo
    echo "API文档:"
    echo "  认证服务:     http://localhost:8001/docs"
    echo "  用户服务:     http://localhost:8002/docs"
    echo
    echo "监控指标:"
    echo "  认证服务:     http://localhost:9091/metrics"
    echo "  用户服务:     http://localhost:9092/metrics"
    echo
    echo "健康检查:"
    echo "  认证服务:     http://localhost:8001/health"
    echo "  用户服务:     http://localhost:8002/health"
    echo
    echo "查看日志: docker-compose -f docker-compose.auth-user-services.yml logs -f"
    echo "停止服务: docker-compose -f docker-compose.auth-user-services.yml down"
}

# 主函数
main() {
    echo "=========================================="
    echo "    索克生活认证服务和用户服务启动器"
    echo "=========================================="
    echo
    
    check_dependencies
    create_directories
    create_env_files
    create_prometheus_config
    create_nginx_config
    create_init_scripts
    start_services
    wait_for_services
    show_service_info
}

# 错误处理
trap 'log_error "脚本执行失败，请检查错误信息"; exit 1' ERR

# 执行主函数
main "$@" 