#!/bin/bash
# 索克生活用户服务启动脚本
# 遵循 Python 3.13.3、UV 和现代化最佳实践

set -euo pipefail

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
    log_info "检查依赖..."
    
    # 检查 UV
    if ! command -v uv &> /dev/null; then
        log_error "UV 未安装，请先安装 UV 包管理器"
        log_info "安装命令: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    
    # 检查 Python 版本
    python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    required_version="3.13"
    
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 13) else 1)"; then
        log_error "Python 版本不符合要求，需要 >= $required_version，当前版本: $python_version"
        exit 1
    fi
    
    log_success "依赖检查通过"
}

# 设置环境
setup_environment() {
    log_info "设置环境..."
    
    # 创建必要的目录
    mkdir -p logs data config
    
    # 设置环境变量
    export PYTHONPATH="${PWD}:${PYTHONPATH:-}"
    export USER_SERVICE_DB_PATH="${PWD}/data/users.db"
    export USER_SERVICE_REST_PORT="${USER_SERVICE_REST_PORT:-8000}"
    export USER_SERVICE_GRPC_PORT="${USER_SERVICE_GRPC_PORT:-50051}"
    export USER_SERVICE_DEBUG="${USER_SERVICE_DEBUG:-false}"
    
    log_success "环境设置完成"
}

# 安装依赖
install_dependencies() {
    log_info "安装依赖..."
    
    if [ ! -d ".venv" ]; then
        log_info "创建虚拟环境..."
        uv venv
    fi
    
    log_info "安装项目依赖..."
    uv pip install -e .
    
    if [ "${INSTALL_DEV:-false}" = "true" ]; then
        log_info "安装开发依赖..."
        uv pip install -e ".[dev]"
    fi
    
    log_success "依赖安装完成"
}

# 数据库迁移
run_migrations() {
    log_info "运行数据库迁移..."
    
    if [ -f "alembic.ini" ]; then
        source .venv/bin/activate
        alembic upgrade head
        log_success "数据库迁移完成"
    else
        log_warning "未找到 alembic.ini，跳过数据库迁移"
    fi
}

# 代码质量检查
run_quality_checks() {
    if [ "${SKIP_CHECKS:-false}" = "true" ]; then
        log_warning "跳过代码质量检查"
        return
    fi
    
    log_info "运行代码质量检查..."
    
    source .venv/bin/activate
    
    # Ruff 检查
    log_info "运行 Ruff 检查..."
    ruff check . || log_warning "Ruff 检查发现问题"
    
    # Black 格式检查
    log_info "运行 Black 格式检查..."
    black --check . || log_warning "Black 格式检查发现问题"
    
    # MyPy 类型检查
    log_info "运行 MyPy 类型检查..."
    mypy . || log_warning "MyPy 类型检查发现问题"
    
    log_success "代码质量检查完成"
}

# 运行测试
run_tests() {
    if [ "${SKIP_TESTS:-false}" = "true" ]; then
        log_warning "跳过测试"
        return
    fi
    
    log_info "运行测试..."
    
    source .venv/bin/activate
    pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing
    
    log_success "测试完成"
}

# 启动服务
start_service() {
    log_info "启动用户服务..."
    
    source .venv/bin/activate
    
    # 检查端口是否被占用
    if lsof -Pi :${USER_SERVICE_REST_PORT} -sTCP:LISTEN -t >/dev/null ; then
        log_error "端口 ${USER_SERVICE_REST_PORT} 已被占用"
        exit 1
    fi
    
    if lsof -Pi :${USER_SERVICE_GRPC_PORT} -sTCP:LISTEN -t >/dev/null ; then
        log_error "端口 ${USER_SERVICE_GRPC_PORT} 已被占用"
        exit 1
    fi
    
    # 启动服务
    log_success "用户服务启动中..."
    log_info "REST API: http://localhost:${USER_SERVICE_REST_PORT}"
    log_info "gRPC: localhost:${USER_SERVICE_GRPC_PORT}"
    log_info "健康检查: http://localhost:${USER_SERVICE_REST_PORT}/health"
    log_info "API 文档: http://localhost:${USER_SERVICE_REST_PORT}/docs"
    
    python cmd/server/main.py
}

# 清理函数
cleanup() {
    log_info "清理资源..."
    # 在这里添加清理逻辑
}

# 信号处理
trap cleanup EXIT

# 主函数
main() {
    log_info "索克生活用户服务启动脚本"
    log_info "================================"
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dev)
                export INSTALL_DEV=true
                export USER_SERVICE_DEBUG=true
                shift
                ;;
            --skip-checks)
                export SKIP_CHECKS=true
                shift
                ;;
            --skip-tests)
                export SKIP_TESTS=true
                shift
                ;;
            --port)
                export USER_SERVICE_REST_PORT="$2"
                shift 2
                ;;
            --grpc-port)
                export USER_SERVICE_GRPC_PORT="$2"
                shift 2
                ;;
            -h|--help)
                echo "用法: $0 [选项]"
                echo "选项:"
                echo "  --dev           开发模式，安装开发依赖"
                echo "  --skip-checks   跳过代码质量检查"
                echo "  --skip-tests    跳过测试"
                echo "  --port PORT     设置 REST API 端口 (默认: 8000)"
                echo "  --grpc-port PORT 设置 gRPC 端口 (默认: 50051)"
                echo "  -h, --help      显示帮助信息"
                exit 0
                ;;
            *)
                log_error "未知选项: $1"
                exit 1
                ;;
        esac
    done
    
    # 执行启动流程
    check_dependencies
    setup_environment
    install_dependencies
    run_migrations
    run_quality_checks
    run_tests
    start_service
}

# 执行主函数
main "$@" 