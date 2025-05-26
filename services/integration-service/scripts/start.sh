#!/bin/bash

# Integration Service 启动脚本

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

# 检查Python环境
check_python() {
    log_info "检查Python环境..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装，请先安装 Python 3.11+"
        exit 1
    fi
    
    # 检查Python版本
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    log_info "Python版本: $python_version"
    
    log_success "Python环境检查完成"
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    # 检查pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 未安装"
        exit 1
    fi
    
    log_success "依赖检查完成"
}

# 安装Python依赖
install_dependencies() {
    log_info "安装Python依赖..."
    
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
        log_success "依赖安装完成"
    else
        log_warning "requirements.txt 不存在，跳过依赖安装"
    fi
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    mkdir -p logs
    mkdir -p data
    mkdir -p config
    
    log_success "目录创建完成"
}

# 检查配置文件
check_config() {
    log_info "检查配置文件..."
    
    if [ ! -f "config/config.yaml" ]; then
        log_warning "配置文件不存在，创建默认配置"
        # 这里可以创建默认配置文件
    fi
    
    log_success "配置检查完成"
}

# 启动服务
start_service() {
    log_info "启动 Integration Service..."
    
    # 设置环境变量
    export PYTHONPATH=$(pwd)
    export APP_DEBUG=true
    export APP_LOG_LEVEL=INFO
    
    # 启动服务
    python3 cmd/server/main.py
}

# 主函数
main() {
    log_info "开始启动 Integration Service..."
    
    check_python
    check_dependencies
    install_dependencies
    create_directories
    check_config
    start_service
    
    log_success "Integration Service 启动完成！"
}

# 处理参数
case "${1:-}" in
    "install")
        log_info "仅安装依赖..."
        check_python
        check_dependencies
        install_dependencies
        log_success "依赖安装完成"
        ;;
    "dev")
        log_info "开发模式启动..."
        export APP_DEBUG=true
        export APP_LOG_LEVEL=DEBUG
        main
        ;;
    *)
        main
        ;;
esac 