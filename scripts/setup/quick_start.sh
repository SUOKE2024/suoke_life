#!/bin/bash

# 索克生活项目 - 快速启动脚本
# 用于快速启动基础设施和核心微服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$PROJECT_ROOT"

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

log_header() {
    echo -e "${PURPLE}$1${NC}"
}

# 打印横幅
print_banner() {
    echo -e "${CYAN}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║                    索克生活 (Suoke Life)                      ║
║                      快速启动脚本                            ║
║                                                              ║
║  🏥 AI驱动的健康管理平台                                      ║
║  🤖 四大智能体：小艾、小克、老克、索儿                        ║
║  🔬 中医辨证 + 现代预防医学                                   ║
╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# 检查前置条件
check_prerequisites() {
    log_header "🔍 检查启动前置条件..."
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    log_success "Docker: $(docker --version | cut -d' ' -f3 | cut -d',' -f1)"
    
    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    log_success "Docker Compose: $(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)"
    
    # 检查uv
    if ! command -v uv &> /dev/null; then
        log_error "uv 未安装，请先安装 uv"
        exit 1
    fi
    log_success "uv: $(uv --version | cut -d' ' -f2)"
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    log_success "Python: $(python3 --version | cut -d' ' -f2)"
    
    echo ""
}

# 启动基础设施
start_infrastructure() {
    log_header "🚀 启动基础设施服务..."
    
    # 创建部署目录
    mkdir -p deploy/docker/init-scripts
    
    # 创建Docker Compose配置
    cat > deploy/docker/docker-compose.yml << 'EOF'
version: '3.8'

services:
  # PostgreSQL数据库
  postgres:
    image: postgres:15
    container_name: suoke-postgres
    restart: unless-stopped
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=suoke_life
      - POSTGRES_USER=suoke
      - POSTGRES_PASSWORD=suoke123
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    networks:
      - suoke-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U suoke"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: suoke-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    command: redis-server --requirepass suoke123
    volumes:
      - redis_data:/data
    networks:
      - suoke-network
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "suoke123", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  # Consul服务发现
  consul:
    image: consul:1.15
    container_name: suoke-consul
    restart: unless-stopped
    ports:
      - "8500:8500"
    command: agent -server -bootstrap -ui -client=0.0.0.0
    volumes:
      - consul_data:/consul/data
    networks:
      - suoke-network

  # Prometheus监控
  prometheus:
    image: prom/prometheus:latest
    container_name: suoke-prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - suoke-network

  # Grafana仪表板
  grafana:
    image: grafana/grafana:latest
    container_name: suoke-grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=suoke123
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - suoke-network

networks:
  suoke-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
  consul_data:
  prometheus_data:
  grafana_data:
EOF

    # 创建数据库初始化脚本
    cat > deploy/docker/init-scripts/01-create-databases.sh << 'EOF'
#!/bin/bash
set -e

# 创建多个数据库
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE auth_service;
    CREATE DATABASE user_service;
    CREATE DATABASE health_data;
    CREATE DATABASE blockchain_service;
    CREATE DATABASE rag_service;
    CREATE DATABASE integration_service;
    CREATE DATABASE med_knowledge;
    CREATE DATABASE xiaoai_service;
    CREATE DATABASE xiaoke_service;
    CREATE DATABASE laoke_service;
    CREATE DATABASE soer_service;
    CREATE DATABASE inquiry_service;
    CREATE DATABASE look_service;
    CREATE DATABASE listen_service;
    CREATE DATABASE palpation_service;
    CREATE DATABASE medical_resources;
    CREATE DATABASE suoke_bench;
    CREATE DATABASE accessibility_service;
EOSQL
EOF

    # 创建Prometheus配置
    cat > deploy/docker/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'suoke-services'
    static_configs:
      - targets: ['host.docker.internal:8080', 'host.docker.internal:50051', 'host.docker.internal:50052', 'host.docker.internal:50053', 'host.docker.internal:50054', 'host.docker.internal:50055', 'host.docker.internal:50056', 'host.docker.internal:50057', 'host.docker.internal:50058', 'host.docker.internal:50059', 'host.docker.internal:50060', 'host.docker.internal:8000', 'host.docker.internal:8090', 'host.docker.internal:9000', 'host.docker.internal:9084']
EOF

    # 设置执行权限
    chmod +x deploy/docker/init-scripts/01-create-databases.sh
    
    # 启动基础设施
    log_info "启动Docker容器..."
    cd deploy/docker
    docker-compose up -d
    cd "$PROJECT_ROOT"
    
    # 等待服务就绪
    log_info "等待基础设施服务就绪..."
    sleep 15
    
    # 检查服务状态
    check_infrastructure_health
    
    log_success "基础设施启动完成"
    echo ""
}

# 检查基础设施健康状态
check_infrastructure_health() {
    log_info "检查基础设施健康状态..."
    
    # 检查PostgreSQL
    if docker exec suoke-postgres pg_isready -U suoke >/dev/null 2>&1; then
        log_success "PostgreSQL: 健康"
    else
        log_warning "PostgreSQL: 未就绪"
    fi
    
    # 检查Redis
    if docker exec suoke-redis redis-cli -a suoke123 ping 2>/dev/null | grep -q PONG; then
        log_success "Redis: 健康"
    else
        log_warning "Redis: 未就绪"
    fi
    
    # 检查Consul
    if curl -f http://localhost:8500/v1/status/leader >/dev/null 2>&1; then
        log_success "Consul: 健康"
    else
        log_warning "Consul: 未就绪"
    fi
}

# 启动核心服务
start_core_services() {
    log_header "🔧 启动核心微服务..."
    
    # 定义核心服务
    declare -A CORE_SERVICES=(
        ["auth-service"]="services/auth-service:50052"
        ["api-gateway"]="services/api-gateway:8080"
        ["user-service"]="services/user-service:50051"
        ["health-data-service"]="services/health-data-service:50056"
        ["med-knowledge"]="services/med-knowledge:8000"
    )
    
    # 启动核心服务
    for service_name in "${!CORE_SERVICES[@]}"; do
        IFS=':' read -r service_path service_port <<< "${CORE_SERVICES[$service_name]}"
        start_single_service "$service_name" "$service_path" "$service_port" &
    done
    
    # 等待所有服务启动
    wait
    
    log_success "核心服务启动完成"
    echo ""
}

# 启动单个服务
start_single_service() {
    local service_name="$1"
    local service_path="$2"
    local service_port="$3"
    
    if [ ! -d "$service_path" ]; then
        log_warning "服务路径不存在: $service_path"
        return 1
    fi
    
    if [ ! -f "$service_path/pyproject.toml" ]; then
        log_warning "缺少pyproject.toml: $service_name"
        return 1
    fi
    
    log_info "启动 $service_name (端口: $service_port)"
    
    cd "$service_path"
    
    # 根据服务类型选择启动命令
    if [[ "$service_name" == "api-gateway" || "$service_name" == "med-knowledge" ]]; then
        nohup uv run uvicorn main:app --host 0.0.0.0 --port "$service_port" > "logs/${service_name}.log" 2>&1 &
    else
        nohup uv run python -m cmd.server > "logs/${service_name}.log" 2>&1 &
    fi
    
    local pid=$!
    echo "$pid" > "/tmp/${service_name}.pid"
    
    cd "$PROJECT_ROOT"
    
    # 等待服务启动
    sleep 5
    
    if kill -0 "$pid" 2>/dev/null; then
        log_success "$service_name 启动成功 (PID: $pid)"
    else
        log_error "$service_name 启动失败"
    fi
}

# 显示服务状态
show_service_status() {
    log_header "📊 服务状态总览"
    
    echo ""
    log_info "基础设施服务:"
    cd deploy/docker
    docker-compose ps
    cd "$PROJECT_ROOT"
    
    echo ""
    log_info "应用服务:"
    for pid_file in /tmp/*.pid; do
        if [ -f "$pid_file" ]; then
            service_name=$(basename "$pid_file" .pid)
            pid=$(cat "$pid_file")
            if kill -0 "$pid" 2>/dev/null; then
                log_success "$service_name: 运行中 (PID: $pid)"
            else
                log_warning "$service_name: 已停止"
                rm -f "$pid_file"
            fi
        fi
    done
    
    echo ""
    log_info "服务访问地址:"
    echo "  🌐 API网关: http://localhost:8080"
    echo "  🔍 Consul UI: http://localhost:8500"
    echo "  📊 Grafana: http://localhost:3000 (admin/suoke123)"
    echo "  📈 Prometheus: http://localhost:9090"
    echo "  🗄️  PostgreSQL: localhost:5432 (suoke/suoke123)"
    echo "  🔴 Redis: localhost:6379 (密码: suoke123)"
    echo ""
}

# 停止所有服务
stop_all_services() {
    log_header "🛑 停止所有服务..."
    
    # 停止应用服务
    for pid_file in /tmp/*.pid; do
        if [ -f "$pid_file" ]; then
            service_name=$(basename "$pid_file" .pid)
            pid=$(cat "$pid_file")
            if kill -0 "$pid" 2>/dev/null; then
                log_info "停止 $service_name (PID: $pid)"
                kill "$pid"
                sleep 2
                if kill -0 "$pid" 2>/dev/null; then
                    log_warning "强制终止 $service_name"
                    kill -9 "$pid"
                fi
            fi
            rm -f "$pid_file"
        fi
    done
    
    # 停止基础设施
    if [ -f "deploy/docker/docker-compose.yml" ]; then
        log_info "停止基础设施服务..."
        cd deploy/docker
        docker-compose down
        cd "$PROJECT_ROOT"
    fi
    
    log_success "所有服务已停止"
}

# 显示帮助信息
show_help() {
    echo "索克生活快速启动脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  start         启动所有服务 (默认)"
    echo "  stop          停止所有服务"
    echo "  restart       重启所有服务"
    echo "  status        显示服务状态"
    echo "  infrastructure 仅启动基础设施"
    echo "  help          显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 start      # 启动所有服务"
    echo "  $0 status     # 查看服务状态"
    echo "  $0 stop       # 停止所有服务"
}

# 主函数
main() {
    local action="${1:-start}"
    
    print_banner
    
    case "$action" in
        "start")
            check_prerequisites
            start_infrastructure
            start_core_services
            show_service_status
            log_success "索克生活服务启动完成! 🎉"
            ;;
        "stop")
            stop_all_services
            ;;
        "restart")
            stop_all_services
            sleep 3
            check_prerequisites
            start_infrastructure
            start_core_services
            show_service_status
            log_success "索克生活服务重启完成! 🎉"
            ;;
        "status")
            show_service_status
            ;;
        "infrastructure")
            check_prerequisites
            start_infrastructure
            log_success "基础设施启动完成! 🎉"
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            log_error "未知选项: $action"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@" 