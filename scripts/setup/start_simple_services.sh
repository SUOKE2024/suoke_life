#!/bin/bash

# 索克生活项目 - 简单服务启动脚本
# 使用现有虚拟环境启动微服务

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

# 虚拟环境路径
VENV_PATH="$PROJECT_ROOT/.venv"

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
║                  简单服务启动脚本                            ║
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
    
    # 检查虚拟环境
    if [ ! -d "$VENV_PATH" ]; then
        log_error "虚拟环境不存在: $VENV_PATH"
        exit 1
    fi
    log_success "虚拟环境: $VENV_PATH"
    
    # 检查Python
    if [ ! -f "$VENV_PATH/bin/python" ]; then
        log_error "Python解释器不存在"
        exit 1
    fi
    
    # 激活虚拟环境并检查版本
    source "$VENV_PATH/bin/activate"
    log_success "Python: $(python --version)"
    
    echo ""
}

# 启动测试服务
start_test_service() {
    log_header "🚀 启动测试服务..."
    
    # 激活虚拟环境
    source "$VENV_PATH/bin/activate"
    
    # 启动测试服务
    log_info "启动测试服务在端口 8888"
    nohup python test_service.py 8888 > test_service.log 2>&1 &
    local pid=$!
    echo "$pid" > "/tmp/test-service.pid"
    
    # 等待服务启动
    sleep 3
    
    if kill -0 "$pid" 2>/dev/null; then
        log_success "测试服务启动成功 (PID: $pid)"
        
        # 测试服务响应
        sleep 2
        if curl -s http://localhost:8888/health >/dev/null 2>&1; then
            log_success "服务健康检查通过"
        else
            log_warning "服务健康检查失败，但进程仍在运行"
        fi
    else
        log_error "测试服务启动失败"
        return 1
    fi
    
    echo ""
}

# 启动老克服务（已知可以启动的服务）
start_laoke_service() {
    log_header "🚀 启动老克服务..."
    
    local service_path="services/agent-services/laoke-service"
    
    if [ ! -d "$service_path" ]; then
        log_warning "老克服务路径不存在: $service_path"
        return 1
    fi
    
    # 激活虚拟环境
    source "$VENV_PATH/bin/activate"
    
    # 创建日志目录
    mkdir -p "$service_path/logs"
    
    cd "$service_path"
    
    log_info "启动老克服务在端口 9000"
    nohup python -m cmd.server > "logs/laoke-service.log" 2>&1 &
    local pid=$!
    echo "$pid" > "/tmp/laoke-service.pid"
    
    cd "$PROJECT_ROOT"
    
    # 等待服务启动
    sleep 3
    
    if kill -0 "$pid" 2>/dev/null; then
        log_success "老克服务启动成功 (PID: $pid)"
    else
        log_error "老克服务启动失败"
        return 1
    fi
    
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
    echo "  🧪 测试服务: http://localhost:8888"
    echo "  👨‍⚕️ 老克服务: http://localhost:9000"
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
    echo "索克生活简单服务启动脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  start         启动服务 (默认)"
    echo "  stop          停止所有服务"
    echo "  restart       重启所有服务"
    echo "  status        显示服务状态"
    echo "  test          仅启动测试服务"
    echo "  help          显示此帮助信息"
    echo ""
}

# 主函数
main() {
    local action="${1:-start}"
    
    print_banner
    
    case "$action" in
        "start")
            check_prerequisites
            start_test_service
            start_laoke_service
            show_service_status
            log_success "索克生活服务启动完成! 🎉"
            ;;
        "test")
            check_prerequisites
            start_test_service
            show_service_status
            log_success "测试服务启动完成! 🎉"
            ;;
        "stop")
            stop_all_services
            ;;
        "restart")
            stop_all_services
            sleep 3
            check_prerequisites
            start_test_service
            start_laoke_service
            show_service_status
            log_success "索克生活服务重启完成! 🎉"
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