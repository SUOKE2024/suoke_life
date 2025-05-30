#!/bin/bash

# 索克生活微服务启动脚本
# 用于启动所有后端微服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SERVICES_DIR="$PROJECT_ROOT/services"

# 默认配置
ENVIRONMENT=${ENVIRONMENT:-development}
START_MODE=${START_MODE:-docker}
PARALLEL=${PARALLEL:-true}

# 服务列表 (使用普通数组)
SERVICES=(
    "api-gateway:8000"
    "auth-service:8001"
    "health-data-service:8002"
    "blockchain-service:8003"
    "message-bus:8004"
    "rag-service:8005"
    "user-service:8006"
    "med-knowledge:8007"
    "xiaoai-service:8015"
    "xiaoke-service:8016"
    "laoke-service:8017"
    "soer-service:8018"
    "look-service:8019"
    "listen-service:8020"
    "inquiry-service:8021"
    "palpation-service:8022"
    "calculation-service:8023"
)

# 核心依赖服务
CORE_DEPENDENCIES=("postgresql" "redis" "rabbitmq")

# 获取服务端口
get_service_port() {
    local service_name=$1
    for service_entry in "${SERVICES[@]}"; do
        local name="${service_entry%:*}"
        local port="${service_entry#*:}"
        if [ "$name" = "$service_name" ]; then
            echo "$port"
            return
        fi
    done
    echo ""
}

# 日志函数
log_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
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

# 显示帮助信息
show_help() {
    cat << EOF
索克生活微服务启动脚本

用法: $0 [选项] [服务名...]

选项:
    -h, --help              显示此帮助信息
    -e, --env ENV          设置环境 (development|staging|production)
    -m, --mode MODE        启动模式 (docker|local|k8s)
    -p, --parallel         并行启动服务 (默认: true)
    -s, --sequential       顺序启动服务
    -c, --check            检查服务状态
    -l, --list             列出所有服务
    --stop                 停止所有服务
    --restart              重启所有服务

示例:
    $0                                    # 启动所有服务
    $0 api-gateway auth-service          # 启动指定服务
    $0 -e production -m k8s              # 生产环境K8s模式启动
    $0 --check                           # 检查服务状态
    $0 --stop                            # 停止所有服务

EOF
}

# 检查依赖
check_dependencies() {
    log_info "检查系统依赖..."
    
    local missing_deps=()
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        missing_deps+=("docker")
    fi
    
    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        missing_deps+=("docker-compose")
    fi
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    # 检查Node.js
    if ! command -v node &> /dev/null; then
        missing_deps+=("node")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "缺少以下依赖: ${missing_deps[*]}"
        exit 1
    fi
    
    log_success "系统依赖检查通过"
}

# 检查端口是否被占用
check_port() {
    local port=$1
    if command -v lsof &> /dev/null; then
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            return 0  # 端口被占用
        else
            return 1  # 端口空闲
        fi
    else
        # 如果没有lsof，使用netstat
        if command -v netstat &> /dev/null; then
            if netstat -an | grep ":$port " | grep LISTEN >/dev/null 2>&1; then
                return 0  # 端口被占用
            else
                return 1  # 端口空闲
            fi
        else
            log_warning "无法检查端口状态：缺少lsof或netstat命令"
            return 1
        fi
    fi
}

# 等待服务启动
wait_for_service() {
    local service_name=$1
    local port=$2
    local max_attempts=30
    local attempt=1
    
    log_info "等待 $service_name 启动 (端口: $port)..."
    
    while [ $attempt -le $max_attempts ]; do
        if check_port $port; then
            log_success "$service_name 启动成功"
            return 0
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    log_error "$service_name 启动超时"
    return 1
}

# 启动核心依赖服务
start_dependencies() {
    log_info "启动核心依赖服务..."
    
    cd "$PROJECT_ROOT"
    
    case $START_MODE in
        "docker")
            if [ -f "docker-compose.microservices.yml" ]; then
                docker-compose -f docker-compose.microservices.yml up -d postgresql redis rabbitmq
            else
                log_warning "docker-compose.microservices.yml 文件不存在"
            fi
            ;;
        "local")
            log_warning "本地模式需要手动启动 PostgreSQL, Redis, RabbitMQ"
            ;;
        "k8s")
            if [ -d "deploy/kubernetes/dependencies/" ]; then
                kubectl apply -f deploy/kubernetes/dependencies/
            else
                log_warning "Kubernetes依赖配置目录不存在"
            fi
            ;;
    esac
    
    # 等待依赖服务启动
    sleep 10
}

# 启动单个服务
start_service() {
    local service_name=$1
    local port=$(get_service_port "$service_name")
    
    if [ -z "$port" ]; then
        log_error "未知服务: $service_name"
        return 1
    fi
    
    log_info "启动服务: $service_name (端口: $port)"
    
    # 检查端口是否已被占用
    if check_port $port; then
        log_warning "$service_name 端口 $port 已被占用，跳过启动"
        return 0
    fi
    
    local service_dir="$SERVICES_DIR/$service_name"
    
    if [ ! -d "$service_dir" ]; then
        log_error "服务目录不存在: $service_dir"
        return 1
    fi
    
    case $START_MODE in
        "docker")
            cd "$PROJECT_ROOT"
            if [ -f "docker-compose.microservices.yml" ]; then
                docker-compose -f docker-compose.microservices.yml up -d $service_name
            else
                log_error "docker-compose.microservices.yml 文件不存在"
                return 1
            fi
            ;;
        "local")
            cd "$service_dir"
            if [ -f "requirements.txt" ]; then
                # Python服务
                if [ ! -d ".venv" ]; then
                    python3 -m venv .venv
                    source .venv/bin/activate
                    pip install -r requirements.txt
                else
                    source .venv/bin/activate
                fi
                mkdir -p logs
                nohup python -m ${service_name//-/_} > logs/${service_name}.log 2>&1 &
            elif [ -f "package.json" ]; then
                # Node.js服务
                npm install
                mkdir -p logs
                nohup npm start > logs/${service_name}.log 2>&1 &
            fi
            ;;
        "k8s")
            if [ -d "deploy/kubernetes/services/${service_name}/" ]; then
                kubectl apply -f deploy/kubernetes/services/${service_name}/
            else
                log_error "Kubernetes服务配置目录不存在: deploy/kubernetes/services/${service_name}/"
                return 1
            fi
            ;;
    esac
    
    # 等待服务启动
    if [ "$START_MODE" != "k8s" ]; then
        wait_for_service $service_name $port
    fi
}

# 启动所有服务
start_all_services() {
    log_info "启动所有微服务..."
    
    # 首先启动依赖服务
    start_dependencies
    
    # 获取服务列表
    local services_to_start=()
    if [ $# -eq 0 ]; then
        # 启动所有服务
        for service_entry in "${SERVICES[@]}"; do
            local service_name="${service_entry%:*}"
            services_to_start+=("$service_name")
        done
    else
        # 启动指定服务
        services_to_start=("$@")
    fi
    
    # 按优先级排序服务
    local priority_services=("api-gateway" "auth-service" "user-service")
    local agent_services=("xiaoai-service" "xiaoke-service" "laoke-service" "soer-service")
    local diagnosis_services=("look-service" "listen-service" "inquiry-service" "palpation-service" "calculation-service")
    local other_services=()
    
    # 分类服务
    for service in "${services_to_start[@]}"; do
        local is_priority=false
        local is_agent=false
        local is_diagnosis=false
        
        for priority_service in "${priority_services[@]}"; do
            if [ "$service" = "$priority_service" ]; then
                is_priority=true
                break
            fi
        done
        
        if [ "$is_priority" = false ]; then
            for agent_service in "${agent_services[@]}"; do
                if [ "$service" = "$agent_service" ]; then
                    is_agent=true
                    break
                fi
            done
        fi
        
        if [ "$is_priority" = false ] && [ "$is_agent" = false ]; then
            for diagnosis_service in "${diagnosis_services[@]}"; do
                if [ "$service" = "$diagnosis_service" ]; then
                    is_diagnosis=true
                    break
                fi
            done
        fi
        
        if [ "$is_priority" = false ] && [ "$is_agent" = false ] && [ "$is_diagnosis" = false ]; then
            other_services+=("$service")
        fi
    done
    
    # 按优先级启动
    local all_ordered_services=()
    for service in "${priority_services[@]}"; do
        for target_service in "${services_to_start[@]}"; do
            if [ "$service" = "$target_service" ]; then
                all_ordered_services+=("$service")
                break
            fi
        done
    done
    
    for service in "${other_services[@]}"; do
        all_ordered_services+=("$service")
    done
    
    for service in "${agent_services[@]}"; do
        for target_service in "${services_to_start[@]}"; do
            if [ "$service" = "$target_service" ]; then
                all_ordered_services+=("$service")
                break
            fi
        done
    done
    
    for service in "${diagnosis_services[@]}"; do
        for target_service in "${services_to_start[@]}"; do
            if [ "$service" = "$target_service" ]; then
                all_ordered_services+=("$service")
                break
            fi
        done
    done
    
    if [ "$PARALLEL" = "true" ]; then
        log_info "并行启动服务..."
        for service in "${all_ordered_services[@]}"; do
            start_service "$service" &
        done
        wait
    else
        log_info "顺序启动服务..."
        for service in "${all_ordered_services[@]}"; do
            start_service "$service"
        done
    fi
    
    log_success "所有服务启动完成"
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."
    
    local running_count=0
    local total_count=${#SERVICES[@]}
    
    printf "%-25s %-8s %-10s\n" "服务名称" "端口" "状态"
    echo "----------------------------------------"
    
    for service_entry in "${SERVICES[@]}"; do
        local service_name="${service_entry%:*}"
        local port="${service_entry#*:}"
        local status="停止"
        local color=$RED
        
        if check_port $port; then
            status="运行中"
            color=$GREEN
            ((running_count++))
        fi
        
        printf "%-25s %-8s " "$service_name" "$port"
        echo -e "${color}$status${NC}"
    done
    
    echo "----------------------------------------"
    echo -e "运行中: ${GREEN}$running_count${NC} / $total_count"
    
    if [ $running_count -eq $total_count ]; then
        log_success "所有服务运行正常"
        return 0
    else
        log_warning "部分服务未运行"
        return 1
    fi
}

# 停止所有服务
stop_services() {
    log_info "停止所有服务..."
    
    cd "$PROJECT_ROOT"
    
    case $START_MODE in
        "docker")
            if [ -f "docker-compose.microservices.yml" ]; then
                docker-compose -f docker-compose.microservices.yml down
            else
                log_warning "docker-compose.microservices.yml 文件不存在"
            fi
            ;;
        "local")
            # 杀死所有相关进程
            for service_entry in "${SERVICES[@]}"; do
                local service_name="${service_entry%:*}"
                local port="${service_entry#*:}"
                if command -v lsof &> /dev/null; then
                    local pid=$(lsof -ti:$port 2>/dev/null)
                    if [ -n "$pid" ]; then
                        kill -9 $pid 2>/dev/null || true
                        log_info "停止服务: $service_name (PID: $pid)"
                    fi
                fi
            done
            ;;
        "k8s")
            if [ -d "deploy/kubernetes/services/" ]; then
                kubectl delete -f deploy/kubernetes/services/ --recursive
            else
                log_warning "Kubernetes服务配置目录不存在"
            fi
            ;;
    esac
    
    log_success "所有服务已停止"
}

# 重启所有服务
restart_services() {
    log_info "重启所有服务..."
    stop_services
    sleep 5
    start_all_services "$@"
}

# 列出所有服务
list_services() {
    log_info "可用服务列表:"
    
    printf "%-25s %-8s %-15s\n" "服务名称" "端口" "类型"
    echo "----------------------------------------"
    
    for service_entry in "${SERVICES[@]}"; do
        local service_name="${service_entry%:*}"
        local port="${service_entry#*:}"
        local type="其他"
        
        if [[ $service_name == *"-service" ]]; then
            if [[ $service_name == "xiaoai-service" || $service_name == "xiaoke-service" || $service_name == "laoke-service" || $service_name == "soer-service" ]]; then
                type="智能体"
            elif [[ $service_name == "look-service" || $service_name == "listen-service" || $service_name == "inquiry-service" || $service_name == "palpation-service" || $service_name == "calculation-service" ]]; then
                type="诊断"
            else
                type="核心"
            fi
        elif [[ $service_name == "api-gateway" ]]; then
            type="网关"
        fi
        
        printf "%-25s %-8s %-15s\n" "$service_name" "$port" "$type"
    done
}

# 主函数
main() {
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -e|--env)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -m|--mode)
                START_MODE="$2"
                shift 2
                ;;
            -p|--parallel)
                PARALLEL=true
                shift
                ;;
            -s|--sequential)
                PARALLEL=false
                shift
                ;;
            -c|--check)
                check_services
                exit $?
                ;;
            -l|--list)
                list_services
                exit 0
                ;;
            --stop)
                stop_services
                exit 0
                ;;
            --restart)
                shift
                restart_services "$@"
                exit 0
                ;;
            -*)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
            *)
                break
                ;;
        esac
    done
    
    # 检查依赖
    check_dependencies
    
    # 设置环境变量
    export ENVIRONMENT
    
    log_info "启动配置:"
    log_info "  环境: $ENVIRONMENT"
    log_info "  模式: $START_MODE"
    log_info "  并行: $PARALLEL"
    
    # 启动服务
    start_all_services "$@"
}

# 执行主函数
main "$@" 