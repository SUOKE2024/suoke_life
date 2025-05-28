#!/bin/bash

# 老克智能体服务启动脚本

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

# 检查 Python 版本
check_python() {
    log_info "检查 Python 版本..."
    
    if ! command -v python3.13 &> /dev/null; then
        log_error "Python 3.13 未找到，请先安装 Python 3.13.3"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3.13 --version | cut -d' ' -f2)
    log_success "Python 版本: $PYTHON_VERSION"
}

# 检查 UV
check_uv() {
    log_info "检查 UV 包管理器..."
    
    if ! command -v uv &> /dev/null; then
        log_warning "UV 未找到，正在安装..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source $HOME/.cargo/env
    fi
    
    UV_VERSION=$(uv --version)
    log_success "UV 版本: $UV_VERSION"
}

# 安装依赖
install_dependencies() {
    log_info "安装项目依赖..."
    
    # 创建虚拟环境（如果不存在）
    if [ ! -d ".venv" ]; then
        log_info "创建虚拟环境..."
        uv venv --python 3.13
    fi
    
    # 安装依赖
    log_info "安装核心依赖..."
    uv sync
    
    # 安装开发依赖（如果是开发环境）
    if [ "${ENVIRONMENT:-development}" = "development" ]; then
        log_info "安装开发依赖..."
        uv sync --extra dev --extra performance --extra monitoring
    fi
    
    log_success "依赖安装完成"
}

# 检查配置
check_config() {
    log_info "检查配置文件..."
    
    # 检查配置文件
    if [ ! -f "config/config.yaml" ] && [ ! -f ".env" ]; then
        log_warning "未找到配置文件，使用默认配置"
        log_info "建议复制 config/config.example.yaml 为 config/config.yaml"
    fi
    
    # 验证配置
    log_info "验证配置..."
    uv run laoke-cli config validate || {
        log_error "配置验证失败"
        exit 1
    }
    
    log_success "配置验证通过"
}

# 初始化数据库
init_database() {
    log_info "初始化数据库..."
    
    # 这里应该添加实际的数据库初始化逻辑
    # uv run laoke-cli db init
    
    log_success "数据库初始化完成"
}

# 启动服务
start_service() {
    local HOST=${HOST:-0.0.0.0}
    local PORT=${PORT:-8080}
    local WORKERS=${WORKERS:-1}
    local RELOAD=${RELOAD:-false}
    local LOG_LEVEL=${LOG_LEVEL:-info}
    
    log_info "启动老克智能体服务..."
    log_info "监听地址: $HOST:$PORT"
    log_info "工作进程: $WORKERS"
    log_info "日志级别: $LOG_LEVEL"
    
    if [ "$RELOAD" = "true" ]; then
        log_info "开发模式（自动重载）"
        uv run laoke-server --host $HOST --port $PORT --reload --log-level $LOG_LEVEL
    else
        uv run laoke-server --host $HOST --port $PORT --workers $WORKERS --log-level $LOG_LEVEL
    fi
}

# 主函数
main() {
    log_info "启动老克智能体服务..."
    
    # 切换到脚本所在目录的上级目录（项目根目录）
    cd "$(dirname "$0")/.."
    
    # 检查环境
    check_python
    check_uv
    
    # 安装依赖
    install_dependencies
    
    # 检查配置
    check_config
    
    # 初始化数据库
    if [ "${INIT_DB:-false}" = "true" ]; then
        init_database
    fi
    
    # 启动服务
    start_service
}

# 帮助信息
show_help() {
    echo "老克智能体服务启动脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help          显示帮助信息"
    echo "  --host HOST         监听地址 (默认: 0.0.0.0)"
    echo "  --port PORT         监听端口 (默认: 8080)"
    echo "  --workers WORKERS   工作进程数 (默认: 1)"
    echo "  --reload            开发模式自动重载"
    echo "  --log-level LEVEL   日志级别 (默认: info)"
    echo "  --init-db           初始化数据库"
    echo ""
    echo "环境变量:"
    echo "  HOST                监听地址"
    echo "  PORT                监听端口"
    echo "  WORKERS             工作进程数"
    echo "  RELOAD              是否自动重载 (true/false)"
    echo "  LOG_LEVEL           日志级别"
    echo "  INIT_DB             是否初始化数据库 (true/false)"
    echo "  ENVIRONMENT         运行环境 (development/production)"
    echo ""
    echo "示例:"
    echo "  $0                              # 使用默认配置启动"
    echo "  $0 --host 127.0.0.1 --port 8000 # 指定地址和端口"
    echo "  $0 --reload                     # 开发模式启动"
    echo "  INIT_DB=true $0                 # 初始化数据库后启动"
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --workers)
            WORKERS="$2"
            shift 2
            ;;
        --reload)
            RELOAD="true"
            shift
            ;;
        --log-level)
            LOG_LEVEL="$2"
            shift 2
            ;;
        --init-db)
            INIT_DB="true"
            shift
            ;;
        *)
            log_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
done

# 运行主函数
main 