#!/bin/bash

# 索克生活 - 优化服务部署脚本
# 自动化部署所有优化后的组件

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
    log_info "检查系统依赖..."
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3未安装，请先安装Python3"
        exit 1
    fi
    
    # 检查pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3未安装，请先安装pip3"
        exit 1
    fi
    
    log_success "所有依赖检查通过"
}

# 安装Python依赖
install_python_dependencies() {
    log_info "安装Python优化依赖..."
    
    # 创建虚拟环境（如果不存在）
    if [ ! -d "venv" ]; then
        log_info "创建Python虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 升级pip
    pip install --upgrade pip
    
    # 安装优化依赖
    if [ -f "requirements-optimized.txt" ]; then
        log_info "安装优化后的Python依赖..."
        pip install -r requirements-optimized.txt
    else
        log_warning "requirements-optimized.txt不存在，使用默认requirements.txt"
        pip install -r requirements.txt
    fi
    
    log_success "Python依赖安装完成"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录结构..."
    
    # 数据目录
    mkdir -p data/{xiaoai,xiaoke,laoke,soer}
    mkdir -p logs/{xiaoai,xiaoke,laoke,soer,api-gateway}
    
    # 配置目录
    mkdir -p config/{redis,postgres,nginx,monitoring}
    
    # 部署脚本目录
    mkdir -p deploy/init-scripts
    
    # 监控配置目录
    mkdir -p monitoring/{prometheus,grafana/{dashboards,datasources}}
    
    # Nginx配置目录
    mkdir -p nginx/{conf.d,ssl}
    
    log_success "目录结构创建完成"
}

# 生成配置文件
generate_configs() {
    log_info "生成配置文件..."
    
    # 生成Nginx配置
    cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream api_gateway {
        server api-gateway:8000;
    }
    
    upstream xiaoai_service {
        server xiaoai-service:8000;
    }
    
    upstream xiaoke_service {
        server xiaoke-service:8000;
    }
    
    upstream laoke_service {
        server laoke-service:8000;
    }
    
    upstream soer_service {
        server soer-service:8000;
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
        }
        
        location /xiaoai/ {
            proxy_pass http://xiaoai_service/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        location /xiaoke/ {
            proxy_pass http://xiaoke_service/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        location /laoke/ {
            proxy_pass http://laoke_service/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        location /soer/ {
            proxy_pass http://soer_service/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
EOF

    # 生成Prometheus配置
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

  - job_name: 'api-gateway'
    static_configs:
      - targets: ['api-gateway:8000']
    metrics_path: '/metrics'

  - job_name: 'xiaoai-service'
    static_configs:
      - targets: ['xiaoai-service:8000']
    metrics_path: '/metrics'

  - job_name: 'xiaoke-service'
    static_configs:
      - targets: ['xiaoke-service:8000']
    metrics_path: '/metrics'

  - job_name: 'laoke-service'
    static_configs:
      - targets: ['laoke-service:8000']
    metrics_path: '/metrics'

  - job_name: 'soer-service'
    static_configs:
      - targets: ['soer-service:8000']
    metrics_path: '/metrics'

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
EOF

    # 生成数据库初始化脚本
    cat > deploy/init-scripts/01-init-database.sql << 'EOF'
-- 索克生活数据库初始化脚本

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建健康数据表
CREATE TABLE IF NOT EXISTS health_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    data_type VARCHAR(50) NOT NULL,
    data_value JSONB NOT NULL,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建智能体会话表
CREATE TABLE IF NOT EXISTS agent_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    agent_type VARCHAR(20) NOT NULL,
    session_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_health_data_user_id ON health_data(user_id);
CREATE INDEX IF NOT EXISTS idx_health_data_type ON health_data(data_type);
CREATE INDEX IF NOT EXISTS idx_agent_sessions_user_id ON agent_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_agent_sessions_type ON agent_sessions(agent_type);

-- 插入测试数据
INSERT INTO users (username, email, password_hash) VALUES 
('test_user', 'test@suoke.life', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uDjO')
ON CONFLICT (email) DO NOTHING;
EOF

    log_success "配置文件生成完成"
}

# 构建Docker镜像
build_docker_images() {
    log_info "构建优化后的Docker镜像..."
    
    # 构建API网关镜像
    log_info "构建API网关镜像..."
    docker build -t suoke/api-gateway:optimized -f services/api-gateway/Dockerfile.optimized .
    
    # 构建智能体服务镜像
    for agent in xiaoai xiaoke laoke soer; do
        log_info "构建${agent}智能体镜像..."
        if [ -f "services/agent-services/${agent}-service/Dockerfile.optimized" ]; then
            docker build -t suoke/${agent}-service:optimized -f services/agent-services/${agent}-service/Dockerfile.optimized .
        else
            log_warning "${agent}服务的优化Dockerfile不存在，跳过构建"
        fi
    done
    
    # 构建其他服务镜像
    for service in auth user health-data medical-resource; do
        log_info "构建${service}服务镜像..."
        if [ -f "services/${service}-service/Dockerfile.optimized" ]; then
            docker build -t suoke/${service}-service:optimized -f services/${service}-service/Dockerfile.optimized .
        else
            log_warning "${service}服务的优化Dockerfile不存在，跳过构建"
        fi
    done
    
    log_success "Docker镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动优化后的服务..."
    
    # 停止现有服务
    log_info "停止现有服务..."
    docker-compose -f docker-compose.optimized-new.yml down
    
    # 清理旧的容器和网络
    docker system prune -f
    
    # 启动基础服务（Redis, PostgreSQL）
    log_info "启动基础服务..."
    docker-compose -f docker-compose.optimized-new.yml up -d redis postgres
    
    # 等待数据库启动
    log_info "等待数据库启动..."
    sleep 30
    
    # 启动应用服务
    log_info "启动应用服务..."
    docker-compose -f docker-compose.optimized-new.yml up -d api-gateway
    docker-compose -f docker-compose.optimized-new.yml up -d xiaoai-service xiaoke-service laoke-service soer-service
    docker-compose -f docker-compose.optimized-new.yml up -d auth-service user-service health-data-service medical-resource-service
    
    # 启动负载均衡器
    log_info "启动负载均衡器..."
    docker-compose -f docker-compose.optimized-new.yml up -d nginx
    
    # 启动监控服务
    log_info "启动监控服务..."
    docker-compose -f docker-compose.optimized-new.yml up -d prometheus grafana jaeger
    
    # 启动日志服务
    log_info "启动日志服务..."
    docker-compose -f docker-compose.optimized-new.yml up -d elasticsearch kibana
    
    log_success "所有服务启动完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 等待服务启动
    sleep 60
    
    # 检查服务状态
    services=("api-gateway:8000" "xiaoai-service:8001" "xiaoke-service:8002" "laoke-service:8003" "soer-service:8004")
    
    for service in "${services[@]}"; do
        service_name=$(echo $service | cut -d':' -f1)
        port=$(echo $service | cut -d':' -f2)
        
        log_info "检查${service_name}服务..."
        
        if curl -f -s "http://localhost:${port}/health" > /dev/null; then
            log_success "${service_name}服务健康"
        else
            log_error "${service_name}服务不健康"
        fi
    done
    
    # 检查监控服务
    log_info "检查监控服务..."
    
    if curl -f -s "http://localhost:9090" > /dev/null; then
        log_success "Prometheus服务健康"
    else
        log_warning "Prometheus服务可能未完全启动"
    fi
    
    if curl -f -s "http://localhost:3000" > /dev/null; then
        log_success "Grafana服务健康"
    else
        log_warning "Grafana服务可能未完全启动"
    fi
}

# 运行性能测试
run_performance_test() {
    log_info "运行性能基准测试..."
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 运行性能测试
    if [ -f "scripts/performance/optimization_benchmark.py" ]; then
        python scripts/performance/optimization_benchmark.py
        log_success "性能测试完成"
    else
        log_warning "性能测试脚本不存在，跳过测试"
    fi
}

# 显示服务信息
show_service_info() {
    log_info "服务访问信息："
    echo ""
    echo "🌐 Web服务："
    echo "  - API网关: http://localhost:8000"
    echo "  - 小艾智能体: http://localhost:8001"
    echo "  - 小克智能体: http://localhost:8002"
    echo "  - 老克智能体: http://localhost:8003"
    echo "  - 索儿智能体: http://localhost:8004"
    echo "  - 认证服务: http://localhost:8005"
    echo "  - 用户服务: http://localhost:8006"
    echo "  - 健康数据服务: http://localhost:8007"
    echo "  - 医疗资源服务: http://localhost:8008"
    echo ""
    echo "📊 监控服务："
    echo "  - Prometheus: http://localhost:9090"
    echo "  - Grafana: http://localhost:3000 (admin/admin)"
    echo "  - Jaeger: http://localhost:16686"
    echo "  - Kibana: http://localhost:5601"
    echo ""
    echo "💾 数据服务："
    echo "  - Redis: localhost:6379"
    echo "  - PostgreSQL: localhost:5432"
    echo "  - ElasticSearch: http://localhost:9200"
    echo ""
    echo "🔧 管理命令："
    echo "  - 查看日志: docker-compose -f docker-compose.optimized-new.yml logs -f [service_name]"
    echo "  - 停止服务: docker-compose -f docker-compose.optimized-new.yml down"
    echo "  - 重启服务: docker-compose -f docker-compose.optimized-new.yml restart [service_name]"
    echo ""
}

# 主函数
main() {
    echo "🚀 索克生活 - 优化服务部署脚本"
    echo "=================================="
    echo ""
    
    # 检查参数
    case "${1:-deploy}" in
        "check")
            check_dependencies
            ;;
        "install")
            check_dependencies
            install_python_dependencies
            ;;
        "config")
            create_directories
            generate_configs
            ;;
        "build")
            build_docker_images
            ;;
        "start")
            start_services
            ;;
        "test")
            run_performance_test
            ;;
        "health")
            health_check
            ;;
        "info")
            show_service_info
            ;;
        "deploy")
            check_dependencies
            install_python_dependencies
            create_directories
            generate_configs
            build_docker_images
            start_services
            health_check
            run_performance_test
            show_service_info
            ;;
        "clean")
            log_info "清理Docker资源..."
            docker-compose -f docker-compose.optimized-new.yml down -v
            docker system prune -f
            log_success "清理完成"
            ;;
        *)
            echo "用法: $0 {deploy|check|install|config|build|start|test|health|info|clean}"
            echo ""
            echo "命令说明："
            echo "  deploy  - 完整部署（默认）"
            echo "  check   - 检查依赖"
            echo "  install - 安装Python依赖"
            echo "  config  - 生成配置文件"
            echo "  build   - 构建Docker镜像"
            echo "  start   - 启动服务"
            echo "  test    - 运行性能测试"
            echo "  health  - 健康检查"
            echo "  info    - 显示服务信息"
            echo "  clean   - 清理资源"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@" 