#!/bin/bash

# 闻诊服务优化启动脚本
# 支持环境检查、依赖安装、配置验证和服务启动

set -e  # 遇到错误立即退出

# 颜色定义
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
    if [[ "${DEBUG}" == "true" ]]; then
        echo -e "${BLUE}[DEBUG]${NC} $1"
    fi
}

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$(dirname "$(dirname "$SERVICE_DIR")")")"

log_info "闻诊服务优化启动脚本"
log_info "服务目录: $SERVICE_DIR"
log_info "项目根目录: $PROJECT_ROOT"

# 默认配置
DEFAULT_CONFIG_FILE="$SERVICE_DIR/config/config_optimized.yaml"
DEFAULT_PORT=50052
DEFAULT_HOST="0.0.0.0"
DEFAULT_WORKERS=16
DEFAULT_ENV="development"

# 解析命令行参数
POSITIONAL=()
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -c|--config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -h|--host)
            HOST="$2"
            shift 2
            ;;
        -w|--workers)
            WORKERS="$2"
            shift 2
            ;;
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --debug)
            DEBUG="true"
            shift
            ;;
        --no-deps)
            NO_DEPS="true"
            shift
            ;;
        --no-check)
            NO_CHECK="true"
            shift
            ;;
        --help)
            echo "闻诊服务启动脚本"
            echo ""
            echo "用法: $0 [选项]"
            echo ""
            echo "选项:"
            echo "  -c, --config FILE    配置文件路径 (默认: $DEFAULT_CONFIG_FILE)"
            echo "  -p, --port PORT      服务端口 (默认: $DEFAULT_PORT)"
            echo "  -h, --host HOST      服务地址 (默认: $DEFAULT_HOST)"
            echo "  -w, --workers NUM    工作线程数 (默认: $DEFAULT_WORKERS)"
            echo "  -e, --env ENV        运行环境 (默认: $DEFAULT_ENV)"
            echo "      --debug          启用调试模式"
            echo "      --no-deps        跳过依赖检查和安装"
            echo "      --no-check       跳过环境检查"
            echo "      --help           显示此帮助信息"
            echo ""
            echo "环境变量:"
            echo "  LISTEN_SERVICE_CONFIG_FILE    配置文件路径"
            echo "  LISTEN_SERVICE_PORT           服务端口"
            echo "  LISTEN_SERVICE_HOST           服务地址"
            echo "  LISTEN_SERVICE_WORKERS        工作线程数"
            echo "  LISTEN_SERVICE_ENV            运行环境"
            echo ""
            exit 0
            ;;
        *)
            POSITIONAL+=("$1")
            shift
            ;;
    esac
done

# 恢复位置参数
set -- "${POSITIONAL[@]}"

# 设置默认值（优先使用环境变量）
CONFIG_FILE="${CONFIG_FILE:-${LISTEN_SERVICE_CONFIG_FILE:-$DEFAULT_CONFIG_FILE}}"
PORT="${PORT:-${LISTEN_SERVICE_PORT:-$DEFAULT_PORT}}"
HOST="${HOST:-${LISTEN_SERVICE_HOST:-$DEFAULT_HOST}}"
WORKERS="${WORKERS:-${LISTEN_SERVICE_WORKERS:-$DEFAULT_WORKERS}}"
ENVIRONMENT="${ENVIRONMENT:-${LISTEN_SERVICE_ENV:-$DEFAULT_ENV}}"

log_info "配置参数:"
log_info "  配置文件: $CONFIG_FILE"
log_info "  服务地址: $HOST:$PORT"
log_info "  工作线程: $WORKERS"
log_info "  运行环境: $ENVIRONMENT"
log_info "  调试模式: ${DEBUG:-false}"

# 检查Python环境
check_python() {
    log_info "检查Python环境..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    log_info "Python版本: $PYTHON_VERSION"
    
    # 检查Python版本（要求3.8+）
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        log_error "Python版本过低，要求3.8+"
        exit 1
    fi
    
    log_info "Python环境检查通过"
}

# 检查系统依赖
check_system_deps() {
    log_info "检查系统依赖..."
    
    # 检查必要的系统库
    local missing_deps=()
    
    # 检查音频处理库
    if ! ldconfig -p | grep -q libsndfile; then
        missing_deps+=("libsndfile1-dev")
    fi
    
    if ! ldconfig -p | grep -q libportaudio; then
        missing_deps+=("portaudio19-dev")
    fi
    
    # 检查FFmpeg
    if ! command -v ffmpeg &> /dev/null; then
        missing_deps+=("ffmpeg")
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_warn "缺少系统依赖: ${missing_deps[*]}"
        log_info "尝试安装系统依赖..."
        
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y "${missing_deps[@]}"
        elif command -v yum &> /dev/null; then
            sudo yum install -y "${missing_deps[@]}"
        elif command -v brew &> /dev/null; then
            brew install "${missing_deps[@]}"
        else
            log_error "无法自动安装系统依赖，请手动安装: ${missing_deps[*]}"
            exit 1
        fi
    fi
    
    log_info "系统依赖检查通过"
}

# 检查Python依赖
check_python_deps() {
    log_info "检查Python依赖..."
    
    cd "$SERVICE_DIR"
    
    # 检查requirements.txt
    if [[ ! -f "requirements.txt" ]]; then
        log_error "requirements.txt 文件不存在"
        exit 1
    fi
    
    # 检查虚拟环境
    if [[ -z "$VIRTUAL_ENV" ]]; then
        log_warn "未检测到虚拟环境，建议使用虚拟环境"
        
        # 尝试激活虚拟环境
        if [[ -f "venv/bin/activate" ]]; then
            log_info "激活虚拟环境..."
            source venv/bin/activate
        elif [[ -f "../../../venv/bin/activate" ]]; then
            log_info "激活项目虚拟环境..."
            source ../../../venv/bin/activate
        fi
    fi
    
    # 安装依赖
    log_info "安装Python依赖..."
    pip install -r requirements.txt
    
    log_info "Python依赖检查通过"
}

# 检查配置文件
check_config() {
    log_info "检查配置文件..."
    
    if [[ ! -f "$CONFIG_FILE" ]]; then
        log_warn "配置文件不存在: $CONFIG_FILE"
        
        # 尝试创建默认配置
        local config_dir=$(dirname "$CONFIG_FILE")
        mkdir -p "$config_dir"
        
        log_info "创建默认配置文件..."
        cat > "$CONFIG_FILE" << EOF
# 闻诊服务优化配置文件
server:
  host: "$HOST"
  port: $PORT
  max_workers: $WORKERS
  max_concurrent_rpcs: 200
  enable_reflection: true
  grace_period: 10

audio_processing:
  default_sample_rate: 16000
  default_channels: 1
  supported_formats: ["wav", "mp3", "flac", "m4a"]
  max_duration: 600
  min_duration: 0.3
  max_file_size: 100
  enable_gpu: true
  batch_processing: true
  cache_enabled: true
  max_concurrent_tasks: 8

tcm_features:
  enabled: true
  organ_sound_mapping:
    heart: ["高亢", "急促", "断续"]
    liver: ["弦急", "高亢", "怒声"]
    spleen: ["低沉", "缓慢", "思虑"]
    lung: ["清亮", "悲伤", "短促"]
    kidney: ["低沉", "恐惧", "微弱"]

monitoring:
  prometheus:
    enabled: true
    host: "0.0.0.0"
    port: 9090
  logging:
    level: "INFO"
    file: "listen_service.log"

development:
  debug_mode: ${DEBUG:-false}
  structured_logging: true
EOF
        
        log_info "默认配置文件已创建: $CONFIG_FILE"
    fi
    
    # 验证配置文件格式
    if ! python3 -c "import yaml; yaml.safe_load(open('$CONFIG_FILE'))" 2>/dev/null; then
        log_error "配置文件格式错误: $CONFIG_FILE"
        exit 1
    fi
    
    log_info "配置文件检查通过"
}

# 检查端口可用性
check_port() {
    log_info "检查端口可用性..."
    
    if netstat -tuln 2>/dev/null | grep -q ":$PORT "; then
        log_error "端口 $PORT 已被占用"
        log_info "正在使用端口 $PORT 的进程:"
        lsof -i :$PORT 2>/dev/null || netstat -tulnp 2>/dev/null | grep ":$PORT "
        exit 1
    fi
    
    log_info "端口 $PORT 可用"
}

# 检查GPU可用性
check_gpu() {
    log_info "检查GPU可用性..."
    
    if command -v nvidia-smi &> /dev/null; then
        if nvidia-smi &> /dev/null; then
            local gpu_count=$(nvidia-smi --list-gpus | wc -l)
            log_info "检测到 $gpu_count 个GPU设备"
            
            # 检查GPU内存
            local gpu_memory=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
            log_info "GPU内存: ${gpu_memory}MB"
        else
            log_warn "NVIDIA驱动未正确安装"
        fi
    else
        log_info "未检测到NVIDIA GPU"
    fi
}

# 设置环境变量
setup_environment() {
    log_info "设置环境变量..."
    
    # 设置Python路径
    export PYTHONPATH="$SERVICE_DIR:$PROJECT_ROOT:$PYTHONPATH"
    
    # 设置服务配置
    export LISTEN_SERVICE_CONFIG_FILE="$CONFIG_FILE"
    export LISTEN_SERVICE_PORT="$PORT"
    export LISTEN_SERVICE_HOST="$HOST"
    export LISTEN_SERVICE_WORKERS="$WORKERS"
    export LISTEN_SERVICE_ENV="$ENVIRONMENT"
    
    # 设置日志级别
    if [[ "$DEBUG" == "true" ]]; then
        export LISTEN_SERVICE_LOG_LEVEL="DEBUG"
    fi
    
    # 设置CUDA环境（如果可用）
    if command -v nvidia-smi &> /dev/null; then
        export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
    fi
    
    log_info "环境变量设置完成"
}

# 创建必要目录
create_directories() {
    log_info "创建必要目录..."
    
    local dirs=(
        "$SERVICE_DIR/logs"
        "$SERVICE_DIR/data"
        "$SERVICE_DIR/temp"
        "/tmp/listen_service"
    )
    
    for dir in "${dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            log_debug "创建目录: $dir"
        fi
    done
    
    log_info "目录创建完成"
}

# 启动服务
start_service() {
    log_info "启动闻诊服务..."
    
    cd "$SERVICE_DIR"
    
    # 构建启动命令
    local cmd="python3 cmd/server.py"
    cmd="$cmd --config $CONFIG_FILE"
    cmd="$cmd --port $PORT"
    cmd="$cmd --host $HOST"
    
    log_info "执行命令: $cmd"
    log_info "服务启动中..."
    log_info "访问地址: $HOST:$PORT"
    log_info "Prometheus指标: http://localhost:9090/metrics"
    log_info "按 Ctrl+C 停止服务"
    
    # 启动服务
    exec $cmd
}

# 清理函数
cleanup() {
    log_info "正在清理..."
    # 这里可以添加清理逻辑
}

# 注册清理函数
trap cleanup EXIT

# 主执行流程
main() {
    log_info "开始启动闻诊服务..."
    
    # 环境检查
    if [[ "$NO_CHECK" != "true" ]]; then
        check_python
        check_system_deps
        check_config
        check_port
        check_gpu
    fi
    
    # 依赖安装
    if [[ "$NO_DEPS" != "true" ]]; then
        check_python_deps
    fi
    
    # 环境设置
    setup_environment
    create_directories
    
    # 启动服务
    start_service
}

# 执行主函数
main "$@" 