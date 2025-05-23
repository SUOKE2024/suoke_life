#!/bin/bash

# 智能体服务启动脚本
# 用于本地开发环境启动所有智能体服务

set -e

echo "🚀 正在启动索克生活智能体服务..."

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

# 检查Docker是否运行
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker未运行，请先启动Docker"
        exit 1
    fi
    log_success "Docker运行正常"
}

# 检查端口是否被占用
check_port() {
    local port=$1
    local service=$2
    
    if lsof -i :$port > /dev/null 2>&1; then
        log_warning "端口 $port 已被占用 ($service)"
        read -p "是否要强制停止占用端口的进程? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            lsof -ti:$port | xargs kill -9
            log_success "已停止端口 $port 上的进程"
        else
            log_error "无法启动 $service，端口被占用"
            return 1
        fi
    fi
    return 0
}

# 检查所有必需端口
check_all_ports() {
    log_info "检查服务端口..."
    check_port 50051 "小艾服务"
    check_port 9083 "小克服务"
    check_port 8080 "老克服务"
    check_port 8054 "索儿服务"
    check_port 5432 "PostgreSQL"
    check_port 6379 "Redis"
}

# 启动基础设施服务
start_infrastructure() {
    log_info "启动基础设施服务..."
    
    # 创建网络
    docker network create suoke-network 2>/dev/null || true
    
    # 启动PostgreSQL
    log_info "启动PostgreSQL数据库..."
    docker run -d \
        --name suoke-postgres \
        --network suoke-network \
        -p 5432:5432 \
        -e POSTGRES_DB=suoke_db \
        -e POSTGRES_USER=suoke_user \
        -e POSTGRES_PASSWORD=suoke_password \
        -v suoke_postgres_data:/var/lib/postgresql/data \
        postgres:13 || log_warning "PostgreSQL可能已在运行"
    
    # 启动Redis
    log_info "启动Redis缓存..."
    docker run -d \
        --name suoke-redis \
        --network suoke-network \
        -p 6379:6379 \
        redis:7-alpine || log_warning "Redis可能已在运行"
    
    # 等待数据库启动
    log_info "等待数据库启动..."
    sleep 5
}

# 启动智能体服务
start_agent_services() {
    log_info "启动智能体服务..."
    
    # 小艾服务 - 四诊协调
    log_info "启动小艾服务 (端口: 50051)..."
    docker run -d \
        --name xiaoai-service \
        --network suoke-network \
        -p 50051:50051 \
        -e DB_HOST=suoke-postgres \
        -e REDIS_HOST=suoke-redis \
        -e SERVICE_PORT=50051 \
        suoke/xiaoai-service:latest || log_warning "小艾服务可能已在运行"
    
    # 小克服务 - 资源调度
    log_info "启动小克服务 (端口: 9083)..."
    docker run -d \
        --name xiaoke-service \
        --network suoke-network \
        -p 9083:9083 \
        -e DB_HOST=suoke-postgres \
        -e REDIS_HOST=suoke-redis \
        -e SERVICE_PORT=9083 \
        suoke/xiaoke-service:latest || log_warning "小克服务可能已在运行"
    
    # 老克服务 - 知识传播
    log_info "启动老克服务 (端口: 8080)..."
    docker run -d \
        --name laoke-service \
        --network suoke-network \
        -p 8080:8080 \
        -e DB_HOST=suoke-postgres \
        -e REDIS_HOST=suoke-redis \
        -e SERVICE_PORT=8080 \
        suoke/laoke-service:latest || log_warning "老克服务可能已在运行"
    
    # 索儿服务 - 生活管理
    log_info "启动索儿服务 (端口: 8054)..."
    docker run -d \
        --name soer-service \
        --network suoke-network \
        -p 8054:8054 \
        -e DB_HOST=suoke-postgres \
        -e REDIS_HOST=suoke-redis \
        -e SERVICE_PORT=8054 \
        suoke/soer-service:latest || log_warning "索儿服务可能已在运行"
}

# 等待服务启动
wait_for_services() {
    log_info "等待服务启动完成..."
    
    local services=("50051:小艾服务" "9083:小克服务" "8080:老克服务" "8054:索儿服务")
    local max_attempts=30
    local attempt=0
    
    for service in "${services[@]}"; do
        IFS=':' read -r port name <<< "$service"
        
        log_info "等待 $name 启动..."
        attempt=0
        while [ $attempt -lt $max_attempts ]; do
            if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
                log_success "$name 启动成功"
                break
            fi
            
            attempt=$((attempt + 1))
            echo -n "."
            sleep 2
        done
        
        if [ $attempt -eq $max_attempts ]; then
            log_error "$name 启动超时"
        fi
        echo
    done
}

# 显示服务状态
show_status() {
    echo
    echo "================================"
    echo "🎉 索克生活智能体服务状态"
    echo "================================"
    
    # 检查各服务状态
    local services=("50051:小艾服务:xiaoai-service" "9083:小克服务:xiaoke-service" "8080:老克服务:laoke-service" "8054:索儿服务:soer-service")
    
    for service in "${services[@]}"; do
        IFS=':' read -r port name container <<< "$service"
        
        if docker ps --filter "name=$container" --format "table {{.Names}}" | grep -q "$container"; then
            if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
                echo -e "✅ $name: ${GREEN}运行中${NC} (localhost:$port)"
            else
                echo -e "⚠️  $name: ${YELLOW}启动中${NC} (localhost:$port)"
            fi
        else
            echo -e "❌ $name: ${RED}未运行${NC} (localhost:$port)"
        fi
    done
    
    echo
    echo "📖 使用说明:"
    echo "- 运行 'npm run test:agents' 进行集成测试"
    echo "- 运行 'npm run stop:agents' 停止所有服务"
    echo "- 查看日志: docker logs [服务名]"
    echo
}

# 主函数
main() {
    log_info "开始启动索克生活智能体服务"
    
    # 检查环境
    check_docker
    check_all_ports
    
    # 启动服务
    start_infrastructure
    start_agent_services
    
    # 等待启动完成
    wait_for_services
    
    # 显示状态
    show_status
    
    log_success "智能体服务启动完成！"
}

# 执行主函数
main "$@"