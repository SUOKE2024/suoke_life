#!/bin/bash

# 索克生活人工审核微服务启动脚本
# Human Review Service Start Script

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

# 检查Python版本
check_python() {
    log_info "检查Python版本..."
    
    if ! command -v python3.13 &> /dev/null; then
        log_error "Python 3.13 未安装，请先安装Python 3.13"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3.13 --version | cut -d' ' -f2)
    log_success "Python版本: $PYTHON_VERSION"
}

# 检查UV包管理器
check_uv() {
    log_info "检查UV包管理器..."
    
    if ! command -v uv &> /dev/null; then
        log_warning "UV未安装，正在安装..."
        pip install uv
    fi
    
    UV_VERSION=$(uv --version | cut -d' ' -f2)
    log_success "UV版本: $UV_VERSION"
}

# 创建虚拟环境
setup_venv() {
    log_info "设置虚拟环境..."
    
    if [ ! -d ".venv" ]; then
        log_info "创建虚拟环境..."
        uv venv .venv --python python3.13
    fi
    
    log_info "激活虚拟环境..."
    source .venv/bin/activate
    
    log_success "虚拟环境已激活"
}

# 安装依赖
install_dependencies() {
    log_info "安装项目依赖..."
    
    # 安装项目依赖
    uv pip install -e .
    
    log_success "依赖安装完成"
}

# 检查环境变量
check_env() {
    log_info "检查环境配置..."
    
    if [ ! -f ".env" ]; then
        if [ -f "env.example" ]; then
            log_warning ".env文件不存在，从env.example复制..."
            cp env.example .env
            log_warning "请编辑.env文件配置正确的环境变量"
        else
            log_error ".env文件和env.example都不存在"
            exit 1
        fi
    fi
    
    log_success "环境配置检查完成"
}

# 检查数据库连接
check_database() {
    log_info "检查数据库连接..."
    
    # 使用CLI工具检查数据库状态
    if .venv/bin/python -m human_review_service.cli.main db status &> /dev/null; then
        log_success "数据库连接正常"
    else
        log_warning "数据库连接失败，尝试初始化数据库..."
        .venv/bin/python -m human_review_service.cli.main db init
        log_success "数据库初始化完成"
    fi
}

# 创建必要目录
create_directories() {
    log_info "创建必要目录..."
    
    mkdir -p logs
    mkdir -p uploads
    mkdir -p data
    
    log_success "目录创建完成"
}

# 启动服务
start_service() {
    local mode=${1:-"development"}
    local host=${2:-"0.0.0.0"}
    local port=${3:-"8000"}
    local workers=${4:-"1"}
    
    log_info "启动人工审核微服务..."
    log_info "模式: $mode"
    log_info "主机: $host"
    log_info "端口: $port"
    log_info "工作进程: $workers"
    
    if [ "$mode" = "production" ]; then
        # 生产模式：使用守护进程
        .venv/bin/python -m human_review_service.cli.main server start \
            --host "$host" \
            --port "$port" \
            --workers "$workers" \
            --daemon \
            --log-file "./logs/app.log"
    else
        # 开发模式：前台运行
        .venv/bin/python -m human_review_service.cli.main server start \
            --host "$host" \
            --port "$port" \
            --workers "$workers"
    fi
}

# 显示帮助信息
show_help() {
    echo "索克生活人工审核微服务启动脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help              显示帮助信息"
    echo "  -m, --mode MODE         运行模式 (development|production) [默认: development]"
    echo "  -H, --host HOST         服务器主机 [默认: 0.0.0.0]"
    echo "  -p, --port PORT         服务器端口 [默认: 8000]"
    echo "  -w, --workers WORKERS   工作进程数 [默认: 1]"
    echo "  --skip-checks           跳过环境检查"
    echo "  --init-only             仅初始化环境，不启动服务"
    echo ""
    echo "示例:"
    echo "  $0                                    # 开发模式启动"
    echo "  $0 -m production -p 8080 -w 4        # 生产模式启动"
    echo "  $0 --init-only                       # 仅初始化环境"
}

# 主函数
main() {
    local mode="development"
    local host="0.0.0.0"
    local port="8000"
    local workers="1"
    local skip_checks=false
    local init_only=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -m|--mode)
                mode="$2"
                shift 2
                ;;
            -H|--host)
                host="$2"
                shift 2
                ;;
            -p|--port)
                port="$2"
                shift 2
                ;;
            -w|--workers)
                workers="$2"
                shift 2
                ;;
            --skip-checks)
                skip_checks=true
                shift
                ;;
            --init-only)
                init_only=true
                shift
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 验证模式
    if [[ "$mode" != "development" && "$mode" != "production" ]]; then
        log_error "无效的运行模式: $mode"
        exit 1
    fi
    
    log_info "开始启动索克生活人工审核微服务..."
    
    # 环境检查
    if [ "$skip_checks" = false ]; then
        check_python
        check_uv
        setup_venv
        install_dependencies
        check_env
        create_directories
        check_database
    fi
    
    # 如果只是初始化，则退出
    if [ "$init_only" = true ]; then
        log_success "环境初始化完成"
        exit 0
    fi
    
    # 启动服务
    start_service "$mode" "$host" "$port" "$workers"
}

# 错误处理
trap 'log_error "脚本执行失败"; exit 1' ERR

# 执行主函数
main "$@" 