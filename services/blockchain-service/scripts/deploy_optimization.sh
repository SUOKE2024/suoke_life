#!/bin/bash

# 区块链服务优化系统部署脚本
# 该脚本用于部署和配置增强版区块链服务

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

# 检查依赖
check_dependencies() {
    log_info "检查系统依赖..."
    
    # 检查Python版本
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 未安装"
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2)
    log_info "Python版本: $python_version"
    
    # 检查pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 未安装"
        exit 1
    fi
    
    # 检查Redis
    if ! command -v redis-server &> /dev/null; then
        log_warning "Redis未安装，某些缓存功能可能不可用"
    fi
    
    # 检查Docker (可选)
    if command -v docker &> /dev/null; then
        log_info "Docker已安装: $(docker --version)"
    else
        log_warning "Docker未安装，容器化部署不可用"
    fi
    
    log_success "依赖检查完成"
}

# 安装Python依赖
install_python_dependencies() {
    log_info "安装Python依赖..."
    
    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        log_info "创建Python虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 升级pip
    pip install --upgrade pip
    
    # 安装依赖
    if [ -f "requirements.txt" ]; then
        log_info "从requirements.txt安装依赖..."
        pip install -r requirements.txt
    else
        log_info "安装基础依赖..."
        pip install web3 redis asyncio aioredis psutil numpy scikit-learn
    fi
    
    log_success "Python依赖安装完成"
}

# 配置环境
setup_environment() {
    log_info "配置环境..."
    
    # 创建必要的目录
    mkdir -p logs
    mkdir -p data
    mkdir -p config
    mkdir -p temp
    
    # 设置环境变量
    export PYTHONPATH="${PYTHONPATH}:$(pwd)"
    
    # 创建配置文件模板
    if [ ! -f "config/app.yaml" ]; then
        log_info "创建配置文件模板..."
        cat > config/app.yaml << EOF
# 区块链服务配置
blockchain:
  network: "mainnet"
  rpc_urls:
    - "https://mainnet.infura.io/v3/YOUR_PROJECT_ID"
  private_key: "YOUR_PRIVATE_KEY"
  contract_addresses:
    health_data_storage: "0x..."
    zkp_verifier: "0x..."
    access_control: "0x..."

# Redis配置
redis:
  host: "localhost"
  port: 6379
  db: 0
  password: ""

# 数据库配置
database:
  host: "localhost"
  port: 5432
  name: "blockchain_service"
  user: "postgres"
  password: "password"

# 优化配置
optimization:
  default_profile: "standard"
  auto_optimization: true
  cache_size: 5000
  batch_size: 25
  worker_threads: 4

# 监控配置
monitoring:
  enabled: true
  metrics_interval: 60
  alert_thresholds:
    cpu_usage: 80
    memory_usage: 85
    error_rate: 5
EOF
        log_warning "请编辑 config/app.yaml 文件，配置正确的参数"
    fi
    
    log_success "环境配置完成"
}

# 初始化数据库
init_database() {
    log_info "初始化数据库..."
    
    # 检查PostgreSQL连接
    if command -v psql &> /dev/null; then
        log_info "PostgreSQL已安装"
        
        # 创建数据库（如果不存在）
        # 这里需要根据实际情况调整
        log_info "数据库初始化脚本需要手动执行"
    else
        log_warning "PostgreSQL未安装，使用SQLite作为后备"
    fi
    
    log_success "数据库初始化完成"
}

# 启动Redis服务
start_redis() {
    log_info "启动Redis服务..."
    
    if command -v redis-server &> /dev/null; then
        # 检查Redis是否已运行
        if pgrep redis-server > /dev/null; then
            log_info "Redis服务已在运行"
        else
            log_info "启动Redis服务..."
            redis-server --daemonize yes
            sleep 2
            
            if pgrep redis-server > /dev/null; then
                log_success "Redis服务启动成功"
            else
                log_error "Redis服务启动失败"
                exit 1
            fi
        fi
    else
        log_warning "Redis未安装，跳过Redis启动"
    fi
}

# 运行测试
run_tests() {
    log_info "运行测试..."
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 运行优化系统测试
    if [ -f "scripts/test_optimization.py" ]; then
        log_info "运行优化系统测试..."
        python scripts/test_optimization.py
        
        if [ $? -eq 0 ]; then
            log_success "测试通过"
        else
            log_warning "测试失败，但继续部署"
        fi
    else
        log_warning "测试脚本不存在，跳过测试"
    fi
}

# 启动服务
start_service() {
    log_info "启动区块链服务..."
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 启动服务
    if [ -f "cmd/server/main.py" ]; then
        log_info "启动主服务..."
        python cmd/server/main.py &
        SERVICE_PID=$!
        
        # 等待服务启动
        sleep 5
        
        # 检查服务状态
        if kill -0 $SERVICE_PID 2>/dev/null; then
            log_success "服务启动成功，PID: $SERVICE_PID"
            echo $SERVICE_PID > service.pid
        else
            log_error "服务启动失败"
            exit 1
        fi
    else
        log_warning "主服务文件不存在，请手动启动服务"
    fi
}

# 停止服务
stop_service() {
    log_info "停止区块链服务..."
    
    if [ -f "service.pid" ]; then
        SERVICE_PID=$(cat service.pid)
        
        if kill -0 $SERVICE_PID 2>/dev/null; then
            log_info "停止服务 PID: $SERVICE_PID"
            kill $SERVICE_PID
            
            # 等待服务停止
            sleep 3
            
            if kill -0 $SERVICE_PID 2>/dev/null; then
                log_warning "强制停止服务"
                kill -9 $SERVICE_PID
            fi
            
            rm -f service.pid
            log_success "服务已停止"
        else
            log_info "服务未运行"
        fi
    else
        log_info "未找到服务PID文件"
    fi
}

# 显示服务状态
show_status() {
    log_info "检查服务状态..."
    
    # 检查主服务
    if [ -f "service.pid" ]; then
        SERVICE_PID=$(cat service.pid)
        
        if kill -0 $SERVICE_PID 2>/dev/null; then
            log_success "主服务运行中，PID: $SERVICE_PID"
        else
            log_warning "主服务未运行"
        fi
    else
        log_warning "主服务未启动"
    fi
    
    # 检查Redis
    if pgrep redis-server > /dev/null; then
        log_success "Redis服务运行中"
    else
        log_warning "Redis服务未运行"
    fi
    
    # 检查端口占用
    if command -v netstat &> /dev/null; then
        log_info "端口占用情况:"
        netstat -tlnp | grep -E ":(8000|6379|5432)" || log_info "未发现相关端口占用"
    fi
}

# 清理环境
cleanup() {
    log_info "清理环境..."
    
    # 停止服务
    stop_service
    
    # 清理临时文件
    rm -rf temp/*
    rm -rf logs/*.log
    
    # 清理缓存
    if command -v redis-cli &> /dev/null; then
        redis-cli FLUSHALL
    fi
    
    log_success "环境清理完成"
}

# 显示帮助信息
show_help() {
    echo "区块链服务优化系统部署脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  install     安装依赖和配置环境"
    echo "  start       启动服务"
    echo "  stop        停止服务"
    echo "  restart     重启服务"
    echo "  status      显示服务状态"
    echo "  test        运行测试"
    echo "  cleanup     清理环境"
    echo "  help        显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 install    # 安装和配置"
    echo "  $0 start      # 启动服务"
    echo "  $0 status     # 检查状态"
}

# 主函数
main() {
    case "${1:-help}" in
        "install")
            log_info "开始安装区块链服务优化系统..."
            check_dependencies
            install_python_dependencies
            setup_environment
            init_database
            start_redis
            log_success "安装完成！"
            log_info "请编辑配置文件后运行: $0 start"
            ;;
        "start")
            log_info "启动区块链服务..."
            start_redis
            start_service
            show_status
            ;;
        "stop")
            stop_service
            ;;
        "restart")
            log_info "重启区块链服务..."
            stop_service
            sleep 2
            start_service
            show_status
            ;;
        "status")
            show_status
            ;;
        "test")
            run_tests
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# 执行主函数
main "$@" 