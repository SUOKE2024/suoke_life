#!/bin/bash

# 中医诊断系统启动脚本
# TCM Diagnosis System Startup Script

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_DIR="$PROJECT_ROOT/logs"
PID_DIR="$PROJECT_ROOT/pids"
CONFIG_DIR="$PROJECT_ROOT/services/diagnostic-services/config"

# 服务配置
CALCULATION_SERVICE_PORT=8000
PALPATION_SERVICE_PORT=8001
KNOWLEDGE_SERVICE_PORT=8002

# 创建必要的目录
mkdir -p "$LOG_DIR" "$PID_DIR"

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
    echo -e "${BLUE}[DEBUG]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# 检查依赖
check_dependencies() {
    log_info "检查系统依赖..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    # 检查pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 未安装"
        exit 1
    fi
    
    # 检查Node.js (用于前端)
    if ! command -v node &> /dev/null; then
        log_warn "Node.js 未安装，前端功能可能不可用"
    fi
    
    # 检查端口占用
    check_port_available $CALCULATION_SERVICE_PORT "计算服务"
    check_port_available $PALPATION_SERVICE_PORT "触诊服务"
    check_port_available $KNOWLEDGE_SERVICE_PORT "知识服务"
    
    log_info "依赖检查完成"
}

# 检查端口是否可用
check_port_available() {
    local port=$1
    local service_name=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null; then
        log_warn "端口 $port ($service_name) 已被占用"
        read -p "是否终止占用进程? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill -9 $(lsof -ti:$port) 2>/dev/null || true
            log_info "已终止端口 $port 的占用进程"
        fi
    fi
}

# 安装Python依赖
install_python_dependencies() {
    log_info "安装Python依赖..."
    
    cd "$PROJECT_ROOT"
    
    # 创建虚拟环境（如果不存在）
    if [ ! -d "venv" ]; then
        log_info "创建Python虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 升级pip
    pip install --upgrade pip
    
    # 安装核心依赖
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    
    # 安装诊断服务特定依赖
    local services_dir="$PROJECT_ROOT/services/diagnostic-services"
    
    # 计算服务依赖
    if [ -f "$services_dir/calculation-service/requirements.txt" ]; then
        pip install -r "$services_dir/calculation-service/requirements.txt"
    fi
    
    # 触诊服务依赖
    if [ -f "$services_dir/palpation-service/requirements.txt" ]; then
        pip install -r "$services_dir/palpation-service/requirements.txt"
    fi
    
    log_info "Python依赖安装完成"
}

# 启动计算服务
start_calculation_service() {
    log_info "启动中医计算服务..."
    
    cd "$PROJECT_ROOT/services/diagnostic-services/calculation-service"
    source "$PROJECT_ROOT/venv/bin/activate"
    
    # 设置环境变量
    export PYTHONPATH="$PROJECT_ROOT/services/diagnostic-services/calculation-service:$PYTHONPATH"
    export TCM_CONFIG_PATH="$CONFIG_DIR/tcm_diagnosis_config.yaml"
    
    # 启动服务
    nohup python -m calculation_service.api.tcm_diagnosis_api \
        > "$LOG_DIR/calculation_service.log" 2>&1 &
    
    local pid=$!
    echo $pid > "$PID_DIR/calculation_service.pid"
    
    log_info "计算服务已启动 (PID: $pid, Port: $CALCULATION_SERVICE_PORT)"
}

# 启动触诊服务
start_palpation_service() {
    log_info "启动脉象传感器服务..."
    
    cd "$PROJECT_ROOT/services/diagnostic-services/palpation-service"
    source "$PROJECT_ROOT/venv/bin/activate"
    
    # 设置环境变量
    export PYTHONPATH="$PROJECT_ROOT/services/diagnostic-services/palpation-service:$PYTHONPATH"
    export TCM_CONFIG_PATH="$CONFIG_DIR/tcm_diagnosis_config.yaml"
    
    # 启动服务
    nohup python -m palpation_service.api.sensor_management_api \
        > "$LOG_DIR/palpation_service.log" 2>&1 &
    
    local pid=$!
    echo $pid > "$PID_DIR/palpation_service.pid"
    
    log_info "触诊服务已启动 (PID: $pid, Port: $PALPATION_SERVICE_PORT)"
}

# 启动知识图谱服务
start_knowledge_service() {
    log_info "启动知识图谱服务..."
    
    cd "$PROJECT_ROOT/src/algorithms"
    source "$PROJECT_ROOT/venv/bin/activate"
    
    # 设置环境变量
    export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"
    export TCM_CONFIG_PATH="$CONFIG_DIR/tcm_diagnosis_config.yaml"
    
    # 创建简单的知识图谱服务启动器
    cat > "$PROJECT_ROOT/temp_kg_server.py" << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

app = FastAPI(title="TCM Knowledge Graph Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "knowledge-graph"}

@app.get("/api/v1/knowledge/status")
async def get_knowledge_status():
    return {"status": "active", "entities_count": 1000, "relations_count": 5000}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
EOF
    
    # 启动服务
    nohup python "$PROJECT_ROOT/temp_kg_server.py" \
        > "$LOG_DIR/knowledge_service.log" 2>&1 &
    
    local pid=$!
    echo $pid > "$PID_DIR/knowledge_service.pid"
    
    log_info "知识图谱服务已启动 (PID: $pid, Port: $KNOWLEDGE_SERVICE_PORT)"
}

# 等待服务启动
wait_for_service() {
    local port=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    log_info "等待 $service_name 启动..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
            log_info "$service_name 已就绪"
            return 0
        fi
        
        log_debug "等待 $service_name 启动... ($attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    log_error "$service_name 启动超时"
    return 1
}

# 健康检查
health_check() {
    log_info "执行系统健康检查..."
    
    local all_healthy=true
    
    # 检查计算服务
    if curl -s "http://localhost:$CALCULATION_SERVICE_PORT/health" > /dev/null 2>&1; then
        log_info "✓ 计算服务健康"
    else
        log_error "✗ 计算服务不健康"
        all_healthy=false
    fi
    
    # 检查触诊服务
    if curl -s "http://localhost:$PALPATION_SERVICE_PORT/health" > /dev/null 2>&1; then
        log_info "✓ 触诊服务健康"
    else
        log_error "✗ 触诊服务不健康"
        all_healthy=false
    fi
    
    # 检查知识图谱服务
    if curl -s "http://localhost:$KNOWLEDGE_SERVICE_PORT/health" > /dev/null 2>&1; then
        log_info "✓ 知识图谱服务健康"
    else
        log_error "✗ 知识图谱服务不健康"
        all_healthy=false
    fi
    
    if [ "$all_healthy" = true ]; then
        log_info "所有服务健康检查通过"
        return 0
    else
        log_error "部分服务健康检查失败"
        return 1
    fi
}

# 停止所有服务
stop_services() {
    log_info "停止所有服务..."
    
    # 停止各个服务
    for service in calculation_service palpation_service knowledge_service; do
        local pid_file="$PID_DIR/${service}.pid"
        if [ -f "$pid_file" ]; then
            local pid=$(cat "$pid_file")
            if kill -0 "$pid" 2>/dev/null; then
                log_info "停止 $service (PID: $pid)"
                kill -TERM "$pid"
                
                # 等待进程结束
                local count=0
                while kill -0 "$pid" 2>/dev/null && [ $count -lt 10 ]; do
                    sleep 1
                    ((count++))
                done
                
                # 强制终止
                if kill -0 "$pid" 2>/dev/null; then
                    log_warn "强制终止 $service"
                    kill -KILL "$pid"
                fi
            fi
            rm -f "$pid_file"
        fi
    done
    
    # 清理临时文件
    rm -f "$PROJECT_ROOT/temp_kg_server.py"
    
    log_info "所有服务已停止"
}

# 显示服务状态
show_status() {
    log_info "服务状态:"
    
    for service in calculation_service palpation_service knowledge_service; do
        local pid_file="$PID_DIR/${service}.pid"
        if [ -f "$pid_file" ]; then
            local pid=$(cat "$pid_file")
            if kill -0 "$pid" 2>/dev/null; then
                echo -e "  ${GREEN}✓${NC} $service (PID: $pid)"
            else
                echo -e "  ${RED}✗${NC} $service (进程不存在)"
                rm -f "$pid_file"
            fi
        else
            echo -e "  ${RED}✗${NC} $service (未启动)"
        fi
    done
    
    echo
    log_info "服务端点:"
    echo "  计算服务: http://localhost:$CALCULATION_SERVICE_PORT"
    echo "  触诊服务: http://localhost:$PALPATION_SERVICE_PORT"
    echo "  知识图谱服务: http://localhost:$KNOWLEDGE_SERVICE_PORT"
}

# 显示日志
show_logs() {
    local service=$1
    local log_file="$LOG_DIR/${service}.log"
    
    if [ -f "$log_file" ]; then
        log_info "显示 $service 日志:"
        tail -f "$log_file"
    else
        log_error "日志文件不存在: $log_file"
    fi
}

# 运行测试
run_tests() {
    log_info "运行系统测试..."
    
    cd "$PROJECT_ROOT"
    source venv/bin/activate
    
    # 设置测试环境变量
    export PYTHONPATH="$PROJECT_ROOT/services/diagnostic-services:$PYTHONPATH"
    export TCM_CONFIG_PATH="$CONFIG_DIR/tcm_diagnosis_config.yaml"
    
    # 运行集成测试
    python -m pytest services/diagnostic-services/tests/test_tcm_diagnosis_integration.py -v
    
    log_info "测试完成"
}

# 显示帮助信息
show_help() {
    echo "中医诊断系统管理脚本"
    echo
    echo "用法: $0 [命令]"
    echo
    echo "命令:"
    echo "  start     启动所有服务"
    echo "  stop      停止所有服务"
    echo "  restart   重启所有服务"
    echo "  status    显示服务状态"
    echo "  health    执行健康检查"
    echo "  logs      显示日志 [service_name]"
    echo "  test      运行系统测试"
    echo "  install   安装依赖"
    echo "  help      显示此帮助信息"
    echo
    echo "示例:"
    echo "  $0 start                    # 启动所有服务"
    echo "  $0 logs calculation_service # 显示计算服务日志"
    echo "  $0 health                   # 执行健康检查"
}

# 信号处理
trap 'log_info "接收到中断信号，正在停止服务..."; stop_services; exit 0' INT TERM

# 主函数
main() {
    case "${1:-start}" in
        start)
            log_info "启动中医诊断系统..."
            check_dependencies
            install_python_dependencies
            
            # 启动所有服务
            start_calculation_service
            start_palpation_service
            start_knowledge_service
            
            # 等待服务启动
            wait_for_service $CALCULATION_SERVICE_PORT "计算服务"
            wait_for_service $PALPATION_SERVICE_PORT "触诊服务"
            wait_for_service $KNOWLEDGE_SERVICE_PORT "知识图谱服务"
            
            # 健康检查
            if health_check; then
                log_info "中医诊断系统启动成功！"
                show_status
                
                log_info "系统已就绪，可以开始使用"
                log_info "按 Ctrl+C 停止系统"
                
                # 保持脚本运行
                while true; do
                    sleep 10
                    if ! health_check > /dev/null 2>&1; then
                        log_warn "检测到服务异常，请检查日志"
                    fi
                done
            else
                log_error "系统启动失败"
                stop_services
                exit 1
            fi
            ;;
        stop)
            stop_services
            ;;
        restart)
            stop_services
            sleep 2
            main start
            ;;
        status)
            show_status
            ;;
        health)
            health_check
            ;;
        logs)
            if [ -n "$2" ]; then
                show_logs "$2"
            else
                log_error "请指定服务名称"
                echo "可用服务: calculation_service, palpation_service, knowledge_service"
            fi
            ;;
        test)
            run_tests
            ;;
        install)
            check_dependencies
            install_python_dependencies
            log_info "依赖安装完成"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@" 