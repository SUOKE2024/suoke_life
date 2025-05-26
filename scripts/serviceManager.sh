#!/bin/bash

# 索克生活微服务管理脚本
# 支持启动、停止、重启、状态检查、日志查看等功能

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 服务列表
SERVICES="api-gateway auth-service user-service health-data-service xiaoai-service xiaoke-service laoke-service soer-service look-service listen-service inquiry-service palpation-service"

# Docker Compose 文件路径
DOCKER_COMPOSE_FILE="docker/docker-compose.yml"

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

# 检查Docker是否运行
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# 检查Docker Compose文件是否存在
check_compose_file() {
    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        log_warning "Docker Compose file not found at $DOCKER_COMPOSE_FILE"
        log_info "Creating basic Docker Compose configuration..."
        create_docker_compose
    fi
}

# 创建基础Docker Compose配置
create_docker_compose() {
    mkdir -p docker
    cat > "$DOCKER_COMPOSE_FILE" << 'EOF'
version: '3.8'

services:
  # 基础设施服务
  consul:
    image: consul:1.15
    ports:
      - "8500:8500"
    command: agent -server -bootstrap -ui -client=0.0.0.0
    networks:
      - suoke-network

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=suoke_life
      - POSTGRES_USER=suoke
      - POSTGRES_PASSWORD=suoke123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - suoke-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - suoke-network

  # API网关 (模拟)
  api-gateway:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - consul
    networks:
      - suoke-network

  # 认证服务 (模拟)
  auth-service:
    image: python:3.9-slim
    ports:
      - "50052:50052"
    command: python -m http.server 50052
    working_dir: /app
    volumes:
      - ../services/auth-service:/app
    networks:
      - suoke-network

  # 用户服务 (模拟)
  user-service:
    image: python:3.9-slim
    ports:
      - "50051:50051"
    command: python -m http.server 50051
    working_dir: /app
    volumes:
      - ../services/user-service:/app
    networks:
      - suoke-network

networks:
  suoke-network:
    driver: bridge

volumes:
  postgres_data:
EOF

    # 创建基础nginx配置
    cat > "docker/nginx.conf" << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream auth_service {
        server auth-service:50052;
    }
    
    upstream user_service {
        server user-service:50051;
    }

    server {
        listen 80;
        
        location /health {
            return 200 '{"status":"ok","timestamp":"'$(date -Iseconds)'"}';
            add_header Content-Type application/json;
        }
        
        location /api/auth/ {
            proxy_pass http://auth_service/;
        }
        
        location /api/user/ {
            proxy_pass http://user_service/;
        }
        
        location / {
            return 200 '{"message":"Suoke Life API Gateway","version":"1.0.0"}';
            add_header Content-Type application/json;
        }
    }
}
EOF

    log_success "Created basic Docker Compose configuration"
}

# 启动服务
start_services() {
    log_info "Starting Suoke Life microservices..."
    
    check_docker
    check_compose_file
    
    # 启动基础设施服务
    log_info "Starting infrastructure services..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d consul postgres redis
    
    # 等待基础服务启动
    log_info "Waiting for infrastructure services to be ready..."
    sleep 10
    
    # 启动应用服务
    log_info "Starting application services..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    
    # 等待服务启动
    sleep 15
    
    log_success "All services started successfully!"
    log_info "Service endpoints:"
    log_info "  - API Gateway: http://localhost:8080"
    log_info "  - Consul UI: http://localhost:8500"
    log_info "  - PostgreSQL: localhost:5432"
    log_info "  - Redis: localhost:6379"
}

# 停止服务
stop_services() {
    log_info "Stopping Suoke Life microservices..."
    
    if [ -f "$DOCKER_COMPOSE_FILE" ]; then
        docker-compose -f "$DOCKER_COMPOSE_FILE" down
        log_success "All services stopped successfully!"
    else
        log_warning "Docker Compose file not found. Stopping all containers..."
        docker stop $(docker ps -q) 2>/dev/null || true
    fi
}

# 重启服务
restart_services() {
    log_info "Restarting Suoke Life microservices..."
    stop_services
    sleep 5
    start_services
}

# 检查服务状态
check_status() {
    log_info "Checking service status..."
    
    if [ -f "$DOCKER_COMPOSE_FILE" ]; then
        docker-compose -f "$DOCKER_COMPOSE_FILE" ps
    else
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    fi
    
    echo ""
    log_info "Health check results:"
    
    # 检查API网关
    if curl -s -f http://localhost:8080/health >/dev/null 2>&1; then
        log_success "API Gateway: ✓ Running"
    else
        log_error "API Gateway: ✗ Not responding"
    fi
    
    # 检查Consul
    if curl -s -f http://localhost:8500/v1/status/leader >/dev/null 2>&1; then
        log_success "Consul: ✓ Running"
    else
        log_error "Consul: ✗ Not responding"
    fi
    
    # 检查数据库连接
    if docker exec -it $(docker ps -q -f name=postgres) pg_isready -U suoke >/dev/null 2>&1; then
        log_success "PostgreSQL: ✓ Running"
    else
        log_error "PostgreSQL: ✗ Not responding"
    fi
    
    # 检查Redis
    if docker exec -it $(docker ps -q -f name=redis) redis-cli ping >/dev/null 2>&1; then
        log_success "Redis: ✓ Running"
    else
        log_error "Redis: ✗ Not responding"
    fi
}

# 查看日志
view_logs() {
    local service=$1
    
    if [ -z "$service" ]; then
        log_info "Showing logs for all services..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" logs -f --tail=100
    else
        log_info "Showing logs for $service..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" logs -f --tail=100 "$service"
    fi
}

# 构建服务
build_services() {
    log_info "Building Suoke Life microservices..."
    
    check_docker
    check_compose_file
    
    docker-compose -f "$DOCKER_COMPOSE_FILE" build
    log_success "All services built successfully!"
}

# 清理资源
cleanup() {
    log_info "Cleaning up Suoke Life resources..."
    
    # 停止并删除容器
    if [ -f "$DOCKER_COMPOSE_FILE" ]; then
        docker-compose -f "$DOCKER_COMPOSE_FILE" down -v --remove-orphans
    fi
    
    # 清理未使用的镜像和网络
    docker system prune -f
    
    log_success "Cleanup completed!"
}

# 显示帮助信息
show_help() {
    echo "Suoke Life Service Manager"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  start     Start all microservices"
    echo "  stop      Stop all microservices"
    echo "  restart   Restart all microservices"
    echo "  status    Check service status"
    echo "  logs      View service logs (optional: specify service name)"
    echo "  build     Build all service images"
    echo "  cleanup   Clean up all resources"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 logs api-gateway"
    echo "  $0 status"
}

# 主函数
main() {
    case "${1:-help}" in
        start)
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        status)
            check_status
            ;;
        logs)
            view_logs "$2"
            ;;
        build)
            build_services
            ;;
        cleanup)
            cleanup
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@" 