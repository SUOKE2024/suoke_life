#!/bin/bash

# 索克生活项目 - 本地服务启动脚本
# 启动不依赖外部基础设施的微服务

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
║                    本地服务启动脚本                          ║
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

# 启动单个服务
start_service() {
    local service_name="$1"
    local service_path="$2"
    local service_port="$3"
    local start_command="$4"
    
    if [ ! -d "$service_path" ]; then
        log_warning "服务路径不存在: $service_path"
        return 1
    fi
    
    log_info "启动 $service_name (端口: $service_port)"
    
    # 创建日志目录
    mkdir -p "$service_path/logs"
    
    cd "$service_path"
    
    # 启动服务
    if [ -n "$start_command" ]; then
        nohup $start_command > "logs/${service_name}.log" 2>&1 &
    else
        # 默认启动命令
        if [ -f "main.py" ]; then
            nohup uv run uvicorn main:app --host 0.0.0.0 --port "$service_port" > "logs/${service_name}.log" 2>&1 &
        elif [ -f "cmd/server.py" ] || [ -d "cmd" ]; then
            nohup uv run python -m cmd.server > "logs/${service_name}.log" 2>&1 &
        else
            log_warning "无法确定 $service_name 的启动方式"
            cd "$PROJECT_ROOT"
            return 1
        fi
    fi
    
    local pid=$!
    echo "$pid" > "/tmp/${service_name}.pid"
    
    cd "$PROJECT_ROOT"
    
    # 等待服务启动
    sleep 3
    
    if kill -0 "$pid" 2>/dev/null; then
        log_success "$service_name 启动成功 (PID: $pid)"
        return 0
    else
        log_error "$service_name 启动失败"
        return 1
    fi
}

# 启动可独立运行的服务
start_independent_services() {
    log_header "🚀 启动独立微服务..."
    
    # 定义可独立运行的服务（不依赖数据库）
    local services=(
        "api-gateway:services/api-gateway:8080:uv run python -m cmd.server.main"
        "med-knowledge:services/med-knowledge:8000:uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"
        "corn-maze-service:services/corn-maze-service:50057"
        "xiaoai-service:services/agent-services/xiaoai-service:50053"
        "laoke-service:services/agent-services/laoke-service:9000"
    )
    
    local success_count=0
    local total_count=${#services[@]}
    
    # 启动服务
    for service_config in "${services[@]}"; do
        IFS=':' read -r service_name service_path service_port custom_command <<< "$service_config"
        if start_service "$service_name" "$service_path" "$service_port" "$custom_command"; then
            ((success_count++))
        fi
        echo ""
    done
    
    log_info "成功启动 $success_count/$total_count 个服务"
    echo ""
}

# 显示服务状态
show_service_status() {
    log_header "📊 服务状态总览"
    
    echo ""
    log_info "运行中的服务:"
    local running_count=0
    
    for pid_file in /tmp/*.pid; do
        if [ -f "$pid_file" ]; then
            service_name=$(basename "$pid_file" .pid)
            pid=$(cat "$pid_file")
            if kill -0 "$pid" 2>/dev/null; then
                log_success "$service_name: 运行中 (PID: $pid)"
                ((running_count++))
            else
                log_warning "$service_name: 已停止"
                rm -f "$pid_file"
            fi
        fi
    done
    
    if [ $running_count -eq 0 ]; then
        log_warning "没有运行中的服务"
    fi
    
    echo ""
    log_info "服务访问地址:"
    echo "  🌐 API网关: http://localhost:8080"
    echo "  📚 医学知识服务: http://localhost:8000"
    echo "  🌽 玉米迷宫服务: http://localhost:50057"
    echo "  🤖 小艾服务: http://localhost:50053"
    echo "  👨‍⚕️ 老克服务: http://localhost:9000"
    echo ""
    
    log_info "注意: 数据库相关服务需要先启动PostgreSQL和Redis"
    echo ""
}

# 停止所有服务
stop_all_services() {
    log_header "🛑 停止所有服务..."
    
    local stopped_count=0
    
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
                ((stopped_count++))
            fi
            rm -f "$pid_file"
        fi
    done
    
    if [ $stopped_count -eq 0 ]; then
        log_info "没有运行中的服务需要停止"
    else
        log_success "已停止 $stopped_count 个服务"
    fi
}

# 显示帮助信息
show_help() {
    echo "索克生活本地服务启动脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  start         启动独立服务 (默认)"
    echo "  stop          停止所有服务"
    echo "  restart       重启所有服务"
    echo "  status        显示服务状态"
    echo "  help          显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 start      # 启动独立服务"
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
            start_independent_services
            show_service_status
            log_success "索克生活本地服务启动完成! 🎉"
            ;;
        "stop")
            stop_all_services
            ;;
        "restart")
            stop_all_services
            sleep 3
            check_prerequisites
            start_independent_services
            show_service_status
            log_success "索克生活本地服务重启完成! 🎉"
            ;;
        "status")
            show_service_status
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