#!/bin/bash

# 索克生活 API 网关设置脚本
# 使用 UV 进行依赖管理和虚拟环境管理

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
check_python_version() {
    log_info "检查 Python 版本..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 未安装"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
    REQUIRED_VERSION="3.13.3"
    
    if [[ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]]; then
        log_error "Python 版本 $PYTHON_VERSION 不满足要求 (>= $REQUIRED_VERSION)"
        exit 1
    fi
    
    log_success "Python 版本检查通过: $PYTHON_VERSION"
}

# 检查并安装 UV
check_and_install_uv() {
    log_info "检查 UV 包管理器..."
    
    if ! command -v uv &> /dev/null; then
        log_warning "UV 未安装，正在安装..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source $HOME/.cargo/env
        
        if ! command -v uv &> /dev/null; then
            log_error "UV 安装失败"
            exit 1
        fi
    fi
    
    UV_VERSION=$(uv --version | cut -d' ' -f2)
    log_success "UV 版本: $UV_VERSION"
}

# 创建虚拟环境
create_virtual_environment() {
    log_info "创建虚拟环境..."
    
    if [ -d ".venv" ]; then
        log_warning "虚拟环境已存在，跳过创建"
    else
        uv venv --python 3.13
        log_success "虚拟环境创建完成"
    fi
}

# 安装依赖
install_dependencies() {
    log_info "安装项目依赖..."
    
    # 安装生产依赖
    uv pip install -e .
    
    # 安装开发依赖
    uv pip install -e ".[dev]"
    
    log_success "依赖安装完成"
}

# 设置 pre-commit
setup_pre_commit() {
    log_info "设置 pre-commit 钩子..."
    
    if [ -f ".pre-commit-config.yaml" ]; then
        source .venv/bin/activate
        pre-commit install
        log_success "pre-commit 钩子设置完成"
    else
        log_warning "未找到 .pre-commit-config.yaml，跳过 pre-commit 设置"
    fi
}

# 创建配置文件
create_config_files() {
    log_info "创建配置文件..."
    
    # 创建 .env 文件
    if [ ! -f ".env" ]; then
        if [ -f "config.env.example" ]; then
            cp config.env.example .env
            log_success "已创建 .env 文件，请根据需要修改配置"
        else
            log_warning "未找到 config.env.example 文件"
        fi
    else
        log_warning ".env 文件已存在，跳过创建"
    fi
    
    # 创建日志目录
    mkdir -p logs
    log_success "日志目录创建完成"
    
    # 创建配置目录
    mkdir -p config
    log_success "配置目录创建完成"
}

# 运行测试
run_tests() {
    log_info "运行测试..."
    
    source .venv/bin/activate
    
    if [ -d "tests" ]; then
        python -m pytest tests/ -v
        log_success "测试运行完成"
    else
        log_warning "未找到测试目录，跳过测试"
    fi
}

# 代码质量检查
run_quality_checks() {
    log_info "运行代码质量检查..."
    
    source .venv/bin/activate
    
    # Ruff 检查
    if command -v ruff &> /dev/null; then
        log_info "运行 Ruff 检查..."
        ruff check suoke_api_gateway/
        ruff format --check suoke_api_gateway/
        log_success "Ruff 检查完成"
    fi
    
    # MyPy 类型检查
    if command -v mypy &> /dev/null; then
        log_info "运行 MyPy 类型检查..."
        mypy suoke_api_gateway/
        log_success "MyPy 检查完成"
    fi
}

# 显示使用说明
show_usage() {
    log_info "设置完成！使用说明："
    echo ""
    echo "1. 激活虚拟环境:"
    echo "   source .venv/bin/activate"
    echo ""
    echo "2. 启动开发服务器:"
    echo "   uv run suoke-gateway dev"
    echo ""
    echo "3. 启动生产服务器:"
    echo "   uv run suoke-gateway run --host 0.0.0.0 --port 8000"
    echo ""
    echo "4. 运行测试:"
    echo "   uv run pytest"
    echo ""
    echo "5. 代码格式化:"
    echo "   uv run ruff format suoke_api_gateway/"
    echo ""
    echo "6. 类型检查:"
    echo "   uv run mypy suoke_api_gateway/"
    echo ""
}

# 主函数
main() {
    log_info "开始设置索克生活 API 网关项目..."
    
    check_python_version
    check_and_install_uv
    create_virtual_environment
    install_dependencies
    setup_pre_commit
    create_config_files
    
    # 可选步骤
    if [ "$1" = "--with-tests" ]; then
        run_tests
    fi
    
    if [ "$1" = "--with-checks" ]; then
        run_quality_checks
    fi
    
    show_usage
    log_success "项目设置完成！"
}

# 运行主函数
main "$@" 