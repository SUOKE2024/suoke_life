#!/bin/bash
# A2A 智能体网络微服务启动脚本
# 使用 UV 包管理器和 Python 3.13.3

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  A2A 智能体网络微服务${NC}"
    echo -e "${BLUE}================================${NC}"
}

# 检查 Python 环境和 UV
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 未安装"
        exit 1
    fi
    
    if ! command -v uv &> /dev/null; then
        print_error "UV 包管理器未安装"
        print_message "请运行: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2)
    uv_version=$(uv --version)
    print_message "Python 版本: $python_version"
    print_message "UV 版本: $uv_version"
}

# 检查依赖和虚拟环境
check_dependencies() {
    print_message "检查依赖..."
    
    if [ ! -f "pyproject.toml" ]; then
        print_error "pyproject.toml 文件不存在"
        exit 1
    fi
    
    # 创建虚拟环境（如果不存在）
    if [ ! -d ".venv" ]; then
        print_message "创建虚拟环境..."
        uv venv .venv --python 3.13.3
    fi
    
    # 激活虚拟环境
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        print_message "激活虚拟环境..."
        source .venv/bin/activate
        export VIRTUAL_ENV="$(pwd)/.venv"
    fi
    
    print_message "使用虚拟环境: $VIRTUAL_ENV"
}

# 安装依赖
install_dependencies() {
    print_message "安装依赖..."
    uv pip install -e ".[production,monitoring]"
}

# 创建必要目录
create_directories() {
    print_message "创建必要目录..."
    mkdir -p logs
    mkdir -p config
}

# 启动服务
start_service() {
    print_message "启动 A2A 智能体网络微服务..."
    
    # 设置环境变量
    export PYTHONPATH=$(pwd)
    
    # 启动服务
    python cmd/server/main.py "$@"
}

# 主函数
main() {
    print_header
    
    # 检查当前目录
    if [ ! -f "cmd/server/main.py" ]; then
        print_error "请在项目根目录运行此脚本"
        exit 1
    fi
    
    check_python
    check_dependencies
    
    # 解析命令行参数
    INSTALL_DEPS=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --install-deps)
                INSTALL_DEPS=true
                shift
                ;;
            --help|-h)
                echo "用法: $0 [选项] [服务参数]"
                echo ""
                echo "选项:"
                echo "  --install-deps    安装依赖"
                echo "  --help, -h        显示帮助信息"
                echo ""
                echo "服务参数:"
                echo "  --config FILE     配置文件路径"
                echo "  --host HOST       服务器主机地址"
                echo "  --port PORT       服务器端口"
                echo "  --debug           启用调试模式"
                exit 0
                ;;
            *)
                break
                ;;
        esac
    done
    
    if [ "$INSTALL_DEPS" = true ]; then
        install_dependencies
    fi
    
    create_directories
    start_service "$@"
}

# 运行主函数
main "$@" 