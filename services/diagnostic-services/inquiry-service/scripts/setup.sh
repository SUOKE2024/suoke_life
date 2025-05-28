#!/bin/bash
# 问诊服务开发环境设置脚本

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
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 未安装"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    REQUIRED_VERSION="3.13.3"
    
    if [[ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]]; then
        log_warning "Python 版本 $PYTHON_VERSION 可能不兼容，推荐版本 $REQUIRED_VERSION"
    else
        log_success "Python 版本检查通过: $PYTHON_VERSION"
    fi
}

# 安装 UV
install_uv() {
    log_info "检查 UV 包管理器..."
    
    if ! command -v uv &> /dev/null; then
        log_info "安装 UV..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"
        log_success "UV 安装完成"
    else
        log_success "UV 已安装: $(uv --version)"
    fi
}

# 设置虚拟环境
setup_venv() {
    log_info "设置虚拟环境..."
    
    # 确保使用正确的 Python 版本
    uv python install 3.13.3
    
    # 同步依赖
    log_info "安装项目依赖..."
    uv sync --dev
    
    log_success "虚拟环境设置完成"
}

# 设置 pre-commit
setup_precommit() {
    log_info "设置 pre-commit hooks..."
    
    uv run pre-commit install
    
    log_success "Pre-commit hooks 设置完成"
}

# 创建配置文件
setup_config() {
    log_info "设置配置文件..."
    
    # 复制环境变量示例文件
    if [ ! -f ".env" ]; then
        if [ -f "env.example" ]; then
            cp env.example .env
            log_success "已创建 .env 文件"
        else
            log_warning "env.example 文件不存在"
        fi
    else
        log_info ".env 文件已存在"
    fi
    
    # 创建必要的目录
    mkdir -p logs data/tcm_knowledge temp
    log_success "目录结构创建完成"
}

# 运行初始检查
run_checks() {
    log_info "运行代码质量检查..."
    
    # 代码格式化
    log_info "格式化代码..."
    uv run ruff format .
    
    # 代码检查
    log_info "运行 linting..."
    uv run ruff check . --fix
    
    # 类型检查
    log_info "运行类型检查..."
    uv run mypy inquiry_service/ || log_warning "类型检查发现问题，请检查代码"
    
    log_success "代码质量检查完成"
}

# 主函数
main() {
    log_info "开始设置问诊服务开发环境..."
    
    check_python
    install_uv
    setup_venv
    setup_precommit
    setup_config
    run_checks
    
    log_success "开发环境设置完成！"
    echo ""
    log_info "下一步操作："
    echo "  1. 编辑 .env 文件配置数据库和其他服务"
    echo "  2. 运行 'make run-dev' 启动开发服务器"
    echo "  3. 运行 'make test' 执行测试"
    echo ""
    log_info "常用命令："
    echo "  make help          - 查看所有可用命令"
    echo "  make install-dev   - 安装开发依赖"
    echo "  make test          - 运行测试"
    echo "  make lint          - 代码检查"
    echo "  make format        - 代码格式化"
}

# 执行主函数
main "$@" 