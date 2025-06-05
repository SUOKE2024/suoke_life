#!/bin/bash

# RAG服务生产环境启动脚本
# 此脚本负责在生产环境中安全启动RAG服务

set -euo pipefail

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SERVICE_NAME="rag-service"
LOG_DIR="/var/log/${SERVICE_NAME}"
PID_FILE="/var/run/${SERVICE_NAME}.pid"
CONFIG_FILE="${PROJECT_ROOT}/config/production.yaml"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_debug() {
    if [[ "${DEBUG:-false}" == "true" ]]; then
        echo -e "${BLUE}[DEBUG]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
    fi
}

# 错误处理
error_exit() {
    log_error "$1"
    exit 1
}

# 清理函数
cleanup() {
    log_info "正在清理资源..."
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            log_info "正在停止服务 (PID: $pid)..."
            kill -TERM "$pid"
            
            # 等待进程优雅退出
            local count=0
            while kill -0 "$pid" 2>/dev/null && [[ $count -lt 30 ]]; do
                sleep 1
                ((count++))
            done
            
            # 如果进程仍在运行，强制杀死
            if kill -0 "$pid" 2>/dev/null; then
                log_warn "进程未能优雅退出，强制终止..."
                kill -KILL "$pid"
            fi
        fi
        rm -f "$PID_FILE"
    fi
}

# 注册信号处理
trap cleanup EXIT INT TERM

# 检查运行环境
check_environment() {
    log_info "检查运行环境..."
    
    # 检查Python版本
    if ! command -v python3 &> /dev/null; then
        error_exit "Python3 未安装"
    fi
    
    local python_version=$(python3 --version | cut -d' ' -f2)
    local required_version="3.13.0"
    
    if ! python3 -c "import sys; exit(0 if sys.version_info >= tuple(map(int, '$required_version'.split('.'))) else 1)"; then
        error_exit "Python版本过低，需要 >= $required_version，当前版本: $python_version"
    fi
    
    log_info "Python版本检查通过: $python_version"
    
    # 检查必要的系统包
    local required_packages=("curl" "jq" "netstat")
    for package in "${required_packages[@]}"; do
        if ! command -v "$package" &> /dev/null; then
            error_exit "缺少必要的系统包: $package"
        fi
    done
    
    # 检查内存
    local available_memory=$(free -m | awk 'NR==2{printf "%.0f", $7}')
    local required_memory=4096  # 4GB
    
    if [[ $available_memory -lt $required_memory ]]; then
        log_warn "可用内存不足，建议至少 ${required_memory}MB，当前可用: ${available_memory}MB"
    fi
    
    # 检查磁盘空间
    local available_disk=$(df "${PROJECT_ROOT}" | awk 'NR==2 {print $4}')
    local required_disk=10485760  # 10GB in KB
    
    if [[ $available_disk -lt $required_disk ]]; then
        log_warn "磁盘空间不足，建议至少 10GB，当前可用: $((available_disk/1024/1024))GB"
    fi
    
    log_info "环境检查完成"
}

# 检查配置文件
check_config() {
    log_info "检查配置文件..."
    
    if [[ ! -f "$CONFIG_FILE" ]]; then
        error_exit "配置文件不存在: $CONFIG_FILE"
    fi
    
    # 验证YAML格式
    if ! python3 -c "import yaml; yaml.safe_load(open('$CONFIG_FILE'))" 2>/dev/null; then
        error_exit "配置文件格式错误: $CONFIG_FILE"
    fi
    
    # 检查必要的环境变量
    local required_env_vars=(
        "DB_HOST" "DB_NAME" "DB_USER" "DB_PASSWORD"
        "MILVUS_HOST" "MILVUS_USER" "MILVUS_PASSWORD"
        "REDIS_HOST" "REDIS_PASSWORD"
        "OPENAI_API_KEY"
    )
    
    local missing_vars=()
    for var in "${required_env_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            missing_vars+=("$var")
        fi
    done
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        error_exit "缺少必要的环境变量: ${missing_vars[*]}"
    fi
    
    log_info "配置检查完成"
}

# 检查依赖服务
check_dependencies() {
    log_info "检查依赖服务..."
    
    # 检查数据库连接
    log_debug "检查数据库连接: $DB_HOST:5432"
    if ! timeout 10 bash -c "</dev/tcp/$DB_HOST/5432"; then
        error_exit "无法连接到数据库: $DB_HOST:5432"
    fi
    
    # 检查Milvus连接
    log_debug "检查Milvus连接: $MILVUS_HOST:19530"
    if ! timeout 10 bash -c "</dev/tcp/$MILVUS_HOST/19530"; then
        error_exit "无法连接到Milvus: $MILVUS_HOST:19530"
    fi
    
    # 检查Redis连接
    log_debug "检查Redis连接: $REDIS_HOST:6379"
    if ! timeout 10 bash -c "</dev/tcp/$REDIS_HOST/6379"; then
        error_exit "无法连接到Redis: $REDIS_HOST:6379"
    fi
    
    # 检查OpenAI API
    log_debug "检查OpenAI API连接"
    if ! curl -s --max-time 10 -H "Authorization: Bearer $OPENAI_API_KEY" \
         "https://api.openai.com/v1/models" > /dev/null; then
        log_warn "OpenAI API连接失败，将使用本地模型"
    fi
    
    log_info "依赖服务检查完成"
}

# 设置日志目录
setup_logging() {
    log_info "设置日志目录..."
    
    # 创建日志目录
    sudo mkdir -p "$LOG_DIR"
    sudo chown "$(whoami):$(whoami)" "$LOG_DIR"
    
    # 设置日志轮转
    local logrotate_config="/etc/logrotate.d/${SERVICE_NAME}"
    if [[ ! -f "$logrotate_config" ]]; then
        sudo tee "$logrotate_config" > /dev/null <<EOF
${LOG_DIR}/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $(whoami) $(whoami)
    postrotate
        if [ -f ${PID_FILE} ]; then
            kill -USR1 \$(cat ${PID_FILE})
        fi
    endscript
}
EOF
        log_info "已创建日志轮转配置: $logrotate_config"
    fi
    
    log_info "日志设置完成"
}

# 安装依赖
install_dependencies() {
    log_info "安装Python依赖..."
    
    cd "$PROJECT_ROOT"
    
    # 检查uv是否安装
    if ! command -v uv &> /dev/null; then
        log_info "安装uv包管理器..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source "$HOME/.cargo/env"
    fi
    
    # 安装依赖
    if [[ -f "pyproject.toml" ]]; then
        log_info "使用uv安装依赖..."
        uv sync --frozen
    elif [[ -f "requirements.txt" ]]; then
        log_info "使用pip安装依赖..."
        python3 -m pip install -r requirements.txt
    else
        error_exit "未找到依赖文件 (pyproject.toml 或 requirements.txt)"
    fi
    
    log_info "依赖安装完成"
}

# 数据库迁移
run_migrations() {
    log_info "运行数据库迁移..."
    
    cd "$PROJECT_ROOT"
    
    # 检查是否有迁移文件
    if [[ -d "migrations" ]]; then
        log_info "执行数据库迁移..."
        python3 -m alembic upgrade head
    else
        log_debug "未找到迁移目录，跳过数据库迁移"
    fi
    
    log_info "数据库迁移完成"
}

# 预热服务
warmup_service() {
    log_info "预热服务..."
    
    # 等待服务启动
    local max_attempts=30
    local attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        if curl -s --max-time 5 "http://localhost:8076/health" > /dev/null; then
            log_info "服务健康检查通过"
            break
        fi
        
        ((attempt++))
        log_debug "等待服务启动... ($attempt/$max_attempts)"
        sleep 2
    done
    
    if [[ $attempt -eq $max_attempts ]]; then
        error_exit "服务启动超时"
    fi
    
    # 预加载模型
    log_info "预加载模型..."
    curl -s --max-time 30 -X POST "http://localhost:8076/api/v1/warmup" \
         -H "Content-Type: application/json" \
         -H "X-API-Key: ${RAG_API_KEY:-warmup-key}" \
         -d '{"preload_models": true}' > /dev/null || log_warn "模型预加载失败"
    
    log_info "服务预热完成"
}

# 启动服务
start_service() {
    log_info "启动RAG服务..."
    
    cd "$PROJECT_ROOT"
    
    # 检查是否已经运行
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            error_exit "服务已在运行 (PID: $pid)"
        else
            log_warn "发现僵尸PID文件，正在清理..."
            rm -f "$PID_FILE"
        fi
    fi
    
    # 设置环境变量
    export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}"
    export RAG_CONFIG_FILE="$CONFIG_FILE"
    export RAG_LOG_DIR="$LOG_DIR"
    
    # 启动服务
    local start_command
    if command -v uv &> /dev/null && [[ -f "pyproject.toml" ]]; then
        start_command="uv run python -m rag_service.main"
    else
        start_command="python3 -m rag_service.main"
    fi
    
    log_info "执行启动命令: $start_command"
    
    # 使用nohup在后台启动
    nohup $start_command \
        --config "$CONFIG_FILE" \
        --log-dir "$LOG_DIR" \
        > "${LOG_DIR}/startup.log" 2>&1 &
    
    local pid=$!
    echo "$pid" > "$PID_FILE"
    
    log_info "服务已启动 (PID: $pid)"
    
    # 等待服务初始化
    sleep 5
    
    # 验证服务是否正常运行
    if ! kill -0 "$pid" 2>/dev/null; then
        error_exit "服务启动失败，请检查日志: ${LOG_DIR}/startup.log"
    fi
    
    log_info "服务启动成功"
}

# 监控服务状态
monitor_service() {
    log_info "开始监控服务状态..."
    
    local check_interval=30  # 30秒检查一次
    local failure_count=0
    local max_failures=3
    
    while true; do
        if [[ -f "$PID_FILE" ]]; then
            local pid=$(cat "$PID_FILE")
            
            # 检查进程是否存在
            if kill -0 "$pid" 2>/dev/null; then
                # 检查健康状态
                if curl -s --max-time 10 "http://localhost:8076/health" > /dev/null; then
                    failure_count=0
                    log_debug "服务运行正常 (PID: $pid)"
                else
                    ((failure_count++))
                    log_warn "健康检查失败 ($failure_count/$max_failures)"
                    
                    if [[ $failure_count -ge $max_failures ]]; then
                        log_error "服务健康检查连续失败，正在重启..."
                        cleanup
                        start_service
                        warmup_service
                        failure_count=0
                    fi
                fi
            else
                log_error "服务进程已退出，正在重启..."
                rm -f "$PID_FILE"
                start_service
                warmup_service
                failure_count=0
            fi
        else
            log_error "PID文件不存在，正在重启服务..."
            start_service
            warmup_service
            failure_count=0
        fi
        
        sleep $check_interval
    done
}

# 显示帮助信息
show_help() {
    cat << EOF
RAG服务生产环境启动脚本

用法: $0 [选项] [命令]

命令:
    start       启动服务 (默认)
    stop        停止服务
    restart     重启服务
    status      查看服务状态
    monitor     启动监控模式
    check       检查环境和配置
    logs        查看日志

选项:
    -h, --help      显示此帮助信息
    -d, --debug     启用调试模式
    -c, --config    指定配置文件 (默认: config/production.yaml)
    --no-warmup     跳过服务预热
    --no-monitor    启动后不进入监控模式

环境变量:
    DEBUG           启用调试输出 (true/false)
    RAG_CONFIG_FILE 配置文件路径
    RAG_LOG_DIR     日志目录路径

示例:
    $0 start                    # 启动服务
    $0 start --no-monitor       # 启动服务但不监控
    $0 restart                  # 重启服务
    $0 status                   # 查看状态
    DEBUG=true $0 check         # 调试模式检查环境

EOF
}

# 查看服务状态
show_status() {
    log_info "检查服务状态..."
    
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            log_info "服务正在运行 (PID: $pid)"
            
            # 检查健康状态
            if curl -s --max-time 5 "http://localhost:8076/health" > /dev/null; then
                log_info "服务健康状态: 正常"
            else
                log_warn "服务健康状态: 异常"
            fi
            
            # 显示资源使用情况
            local cpu_usage=$(ps -p "$pid" -o %cpu --no-headers | tr -d ' ')
            local mem_usage=$(ps -p "$pid" -o %mem --no-headers | tr -d ' ')
            log_info "CPU使用率: ${cpu_usage}%"
            log_info "内存使用率: ${mem_usage}%"
            
            # 显示端口监听情况
            if netstat -tlnp 2>/dev/null | grep -q ":8076.*$pid/"; then
                log_info "端口8076: 正在监听"
            else
                log_warn "端口8076: 未监听"
            fi
            
        else
            log_error "服务未运行 (PID文件存在但进程不存在)"
            rm -f "$PID_FILE"
        fi
    else
        log_info "服务未运行"
    fi
}

# 停止服务
stop_service() {
    log_info "停止RAG服务..."
    
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            log_info "正在停止服务 (PID: $pid)..."
            
            # 发送TERM信号
            kill -TERM "$pid"
            
            # 等待优雅退出
            local count=0
            while kill -0 "$pid" 2>/dev/null && [[ $count -lt 30 ]]; do
                sleep 1
                ((count++))
                log_debug "等待服务停止... ($count/30)"
            done
            
            # 如果仍在运行，强制终止
            if kill -0 "$pid" 2>/dev/null; then
                log_warn "服务未能优雅退出，强制终止..."
                kill -KILL "$pid"
                sleep 2
            fi
            
            if ! kill -0 "$pid" 2>/dev/null; then
                log_info "服务已停止"
            else
                error_exit "无法停止服务"
            fi
        else
            log_warn "PID文件存在但进程不存在"
        fi
        
        rm -f "$PID_FILE"
    else
        log_info "服务未运行"
    fi
}

# 查看日志
show_logs() {
    local log_file="${LOG_DIR}/app.log"
    
    if [[ -f "$log_file" ]]; then
        log_info "显示日志文件: $log_file"
        tail -f "$log_file"
    else
        log_error "日志文件不存在: $log_file"
        
        # 显示启动日志
        local startup_log="${LOG_DIR}/startup.log"
        if [[ -f "$startup_log" ]]; then
            log_info "显示启动日志: $startup_log"
            cat "$startup_log"
        fi
    fi
}

# 主函数
main() {
    local command="start"
    local enable_monitor=true
    local enable_warmup=true
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -d|--debug)
                export DEBUG=true
                ;;
            -c|--config)
                CONFIG_FILE="$2"
                shift
                ;;
            --no-warmup)
                enable_warmup=false
                ;;
            --no-monitor)
                enable_monitor=false
                ;;
            start|stop|restart|status|monitor|check|logs)
                command="$1"
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
        shift
    done
    
    # 执行命令
    case $command in
        start)
            check_environment
            check_config
            check_dependencies
            setup_logging
            install_dependencies
            run_migrations
            start_service
            
            if [[ "$enable_warmup" == "true" ]]; then
                warmup_service
            fi
            
            if [[ "$enable_monitor" == "true" ]]; then
                monitor_service
            else
                log_info "服务已启动，使用 '$0 monitor' 开始监控"
            fi
            ;;
        stop)
            stop_service
            ;;
        restart)
            stop_service
            sleep 2
            main start --no-monitor
            ;;
        status)
            show_status
            ;;
        monitor)
            monitor_service
            ;;
        check)
            check_environment
            check_config
            check_dependencies
            log_info "所有检查通过"
            ;;
        logs)
            show_logs
            ;;
        *)
            log_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@" 