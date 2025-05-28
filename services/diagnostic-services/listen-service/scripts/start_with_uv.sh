#!/bin/bash

# 索克生活闻诊服务启动脚本 (UV 版本)
# 基于 Python 3.13.3 和 UV 包管理器的现代化启动脚本

set -euo pipefail

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SERVICE_NAME="listen-service"
PYTHON_VERSION="3.13.3"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    if [[ "${DEBUG:-false}" == "true" ]]; then
        echo -e "${BLUE}[DEBUG]${NC} $1"
    fi
}

# 检查系统要求
check_system_requirements() {
    log_info "检查系统要求..."
    
    # 检查操作系统
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_info "检测到 Linux 系统"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        log_info "检测到 macOS 系统"
    else
        log_error "不支持的操作系统: $OSTYPE"
        exit 1
    fi
    
    # 检查 Python 版本
    if command -v python3 &> /dev/null; then
        PYTHON_VER=$(python3 --version | cut -d' ' -f2)
        log_info "检测到 Python 版本: $PYTHON_VER"
        
        # 检查是否为 3.13+
        if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 13) else 1)" 2>/dev/null; then
            log_warn "建议使用 Python 3.13.3 或更高版本，当前版本: $PYTHON_VER"
        fi
    else
        log_error "未找到 Python 3，请先安装 Python 3.13.3+"
        exit 1
    fi
    
    # 检查 UV
    if ! command -v uv &> /dev/null; then
        log_error "未找到 UV 包管理器，请先安装 UV"
        log_info "安装命令: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    else
        UV_VER=$(uv --version | cut -d' ' -f2)
        log_info "检测到 UV 版本: $UV_VER"
    fi
    
    # 检查系统依赖
    check_system_dependencies
}

# 检查系统依赖
check_system_dependencies() {
    log_info "检查系统依赖..."
    
    local missing_deps=()
    
    # 音频处理依赖
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux 系统依赖
        local deps=("libsndfile1-dev" "libffi-dev" "libasound2-dev" "portaudio19-dev")
        for dep in "${deps[@]}"; do
            if ! dpkg -l | grep -q "^ii  $dep "; then
                missing_deps+=("$dep")
            fi
        done
        
        if [[ ${#missing_deps[@]} -gt 0 ]]; then
            log_warn "缺少系统依赖: ${missing_deps[*]}"
            log_info "请运行: sudo apt-get install ${missing_deps[*]}"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS 系统依赖
        if ! command -v brew &> /dev/null; then
            log_warn "建议安装 Homebrew 以管理系统依赖"
        else
            local deps=("libsndfile" "portaudio")
            for dep in "${deps[@]}"; do
                if ! brew list "$dep" &> /dev/null; then
                    missing_deps+=("$dep")
                fi
            done
            
            if [[ ${#missing_deps[@]} -gt 0 ]]; then
                log_warn "缺少系统依赖: ${missing_deps[*]}"
                log_info "请运行: brew install ${missing_deps[*]}"
            fi
        fi
    fi
}

# 检查 GPU 支持
check_gpu_support() {
    log_info "检查 GPU 支持..."
    
    if command -v nvidia-smi &> /dev/null; then
        local gpu_info=$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits 2>/dev/null || echo "")
        if [[ -n "$gpu_info" ]]; then
            log_info "检测到 NVIDIA GPU: $gpu_info"
            export CUDA_AVAILABLE=true
        else
            log_warn "未检测到可用的 NVIDIA GPU"
            export CUDA_AVAILABLE=false
        fi
    else
        log_info "未安装 NVIDIA 驱动，将使用 CPU 模式"
        export CUDA_AVAILABLE=false
    fi
}

# 设置环境
setup_environment() {
    log_info "设置项目环境..."
    
    cd "$PROJECT_ROOT"
    
    # 检查 pyproject.toml
    if [[ ! -f "pyproject.toml" ]]; then
        log_error "未找到 pyproject.toml 文件"
        exit 1
    fi
    
    # 创建必要的目录
    mkdir -p logs
    mkdir -p data
    mkdir -p models
    mkdir -p temp
    
    # 设置环境变量
    export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
    export ENVIRONMENT="${ENVIRONMENT:-development}"
    export LOG_LEVEL="${LOG_LEVEL:-INFO}"
    
    log_info "项目根目录: $PROJECT_ROOT"
    log_info "运行环境: $ENVIRONMENT"
}

# 安装依赖
install_dependencies() {
    log_info "使用 UV 安装项目依赖..."
    
    cd "$PROJECT_ROOT"
    
    # 检查 uv.lock 文件
    if [[ ! -f "uv.lock" ]]; then
        log_info "未找到 uv.lock，将创建新的锁文件..."
        uv lock
    fi
    
    # 安装依赖
    log_info "安装生产依赖..."
    uv sync --frozen
    
    # 根据环境安装额外依赖
    if [[ "$ENVIRONMENT" == "development" ]]; then
        log_info "安装开发依赖..."
        uv sync --frozen --group dev
    fi
    
    # 安装 GPU 支持（如果可用）
    if [[ "${CUDA_AVAILABLE:-false}" == "true" ]]; then
        log_info "安装 CUDA 支持..."
        uv add torch torchaudio --index-url https://download.pytorch.org/whl/cu121
    fi
    
    log_info "依赖安装完成"
}

# 验证安装
verify_installation() {
    log_info "验证安装..."
    
    # 检查关键模块
    local modules=("numpy" "librosa" "torch" "grpcio" "pydantic")
    
    for module in "${modules[@]}"; do
        if uv run python -c "import $module" 2>/dev/null; then
            log_debug "模块 $module 安装正常"
        else
            log_error "模块 $module 安装失败"
            exit 1
        fi
    done
    
    # 检查音频处理能力
    if uv run python -c "
import librosa
import numpy as np
# 测试基本音频处理
y = np.random.randn(16000)
mfcc = librosa.feature.mfcc(y=y, sr=16000)
print(f'MFCC shape: {mfcc.shape}')
" 2>/dev/null; then
        log_info "音频处理功能验证通过"
    else
        log_error "音频处理功能验证失败"
        exit 1
    fi
    
    # 检查 GPU 功能（如果可用）
    if [[ "${CUDA_AVAILABLE:-false}" == "true" ]]; then
        if uv run python -c "
import torch
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU count: {torch.cuda.device_count()}')
    print(f'Current device: {torch.cuda.current_device()}')
" 2>/dev/null; then
            log_info "GPU 功能验证通过"
        else
            log_warn "GPU 功能验证失败，将使用 CPU 模式"
            export CUDA_AVAILABLE=false
        fi
    fi
}

# 配置验证
validate_configuration() {
    log_info "验证配置文件..."
    
    # 检查配置文件
    local config_files=("config/config.yaml" ".env.example")
    
    for config_file in "${config_files[@]}"; do
        if [[ -f "$config_file" ]]; then
            log_debug "找到配置文件: $config_file"
        else
            log_warn "未找到配置文件: $config_file"
        fi
    done
    
    # 创建 .env 文件（如果不存在）
    if [[ ! -f ".env" && -f ".env.example" ]]; then
        log_info "创建 .env 文件..."
        cp .env.example .env
        log_warn "请根据需要修改 .env 文件中的配置"
    fi
    
    # 验证配置
    if uv run python -c "
from listen_service.config.settings import get_settings
try:
    settings = get_settings()
    print(f'配置验证通过，环境: {settings.environment.value}')
except Exception as e:
    print(f'配置验证失败: {e}')
    exit(1)
" 2>/dev/null; then
        log_info "配置验证通过"
    else
        log_error "配置验证失败"
        exit 1
    fi
}

# 启动服务
start_service() {
    log_info "启动闻诊服务..."
    
    # 设置运行时环境变量
    export PYTHONUNBUFFERED=1
    export GRPC_VERBOSITY=INFO
    export GRPC_TRACE=all
    
    # 根据环境选择启动方式
    if [[ "$ENVIRONMENT" == "development" ]]; then
        log_info "开发模式启动..."
        export DEBUG=true
        export LOG_LEVEL=DEBUG
        
        # 使用 UV 运行服务
        uv run python -m listen_service.cmd.server
        
    elif [[ "$ENVIRONMENT" == "production" ]]; then
        log_info "生产模式启动..."
        export DEBUG=false
        export LOG_LEVEL=INFO
        
        # 生产模式可以考虑使用进程管理器
        uv run python -m listen_service.cmd.server
        
    else
        log_info "默认模式启动..."
        uv run python -m listen_service.cmd.server
    fi
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    local max_attempts=30
    local attempt=1
    local port="${SERVER_PORT:-50052}"
    
    while [[ $attempt -le $max_attempts ]]; do
        if nc -z localhost "$port" 2>/dev/null; then
            log_info "服务健康检查通过 (端口 $port)"
            return 0
        fi
        
        log_debug "健康检查尝试 $attempt/$max_attempts..."
        sleep 2
        ((attempt++))
    done
    
    log_error "服务健康检查失败"
    return 1
}

# 显示帮助信息
show_help() {
    cat << EOF
索克生活闻诊服务启动脚本 (UV 版本)

用法: $0 [选项]

选项:
    -h, --help              显示此帮助信息
    -e, --env ENV          设置运行环境 (development|testing|staging|production)
    -d, --debug            启用调试模式
    -c, --check-only       仅执行检查，不启动服务
    -s, --skip-deps        跳过依赖安装
    --health-check         执行健康检查
    --gpu                  强制启用 GPU 支持
    --no-gpu               禁用 GPU 支持

环境变量:
    ENVIRONMENT            运行环境 (默认: development)
    LOG_LEVEL             日志级别 (默认: INFO)
    SERVER_PORT           服务端口 (默认: 50052)
    DEBUG                 调试模式 (默认: false)

示例:
    $0                     # 默认启动
    $0 -e production       # 生产环境启动
    $0 -d                  # 调试模式启动
    $0 --check-only        # 仅执行检查
    $0 --health-check      # 健康检查

EOF
}

# 主函数
main() {
    local check_only=false
    local skip_deps=false
    local health_check_only=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -e|--env)
                export ENVIRONMENT="$2"
                shift 2
                ;;
            -d|--debug)
                export DEBUG=true
                export LOG_LEVEL=DEBUG
                shift
                ;;
            -c|--check-only)
                check_only=true
                shift
                ;;
            -s|--skip-deps)
                skip_deps=true
                shift
                ;;
            --health-check)
                health_check_only=true
                shift
                ;;
            --gpu)
                export CUDA_AVAILABLE=true
                shift
                ;;
            --no-gpu)
                export CUDA_AVAILABLE=false
                shift
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 仅健康检查
    if [[ "$health_check_only" == "true" ]]; then
        health_check
        exit $?
    fi
    
    # 执行启动流程
    log_info "开始启动 $SERVICE_NAME..."
    
    check_system_requirements
    check_gpu_support
    setup_environment
    
    if [[ "$skip_deps" != "true" ]]; then
        install_dependencies
        verify_installation
    fi
    
    validate_configuration
    
    if [[ "$check_only" == "true" ]]; then
        log_info "检查完成，所有组件正常"
        exit 0
    fi
    
    # 启动服务
    start_service
}

# 错误处理
trap 'log_error "脚本执行失败，退出码: $?"' ERR

# 执行主函数
main "$@" 