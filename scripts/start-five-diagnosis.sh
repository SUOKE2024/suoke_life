#!/bin/bash

# 索克生活 - 五诊服务启动脚本
# 启动完整的五诊系统，包括传统四诊和新增的算诊功能

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
    
    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    # 检查 Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安装，请先安装 Node.js"
        exit 1
    fi
    
    # 检查 npm
    if ! command -v npm &> /dev/null; then
        log_error "npm 未安装，请先安装 npm"
        exit 1
    fi
    
    log_success "所有依赖检查通过"
}

# 检查端口占用
check_ports() {
    log_info "检查端口占用情况..."
    
    local ports=(3000 8000 8001 8002 8003 8004 8005)
    local occupied_ports=()
    
    for port in "${ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            occupied_ports+=($port)
        fi
    done
    
    if [ ${#occupied_ports[@]} -gt 0 ]; then
        log_warning "以下端口已被占用: ${occupied_ports[*]}"
        read -p "是否继续启动？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "启动已取消"
            exit 0
        fi
    else
        log_success "所有端口可用"
    fi
}

# 启动后端服务
start_backend_services() {
    log_info "启动后端微服务..."
    
    # 启动 API Gateway
    log_info "启动 API Gateway..."
    cd services/api-gateway
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -r requirements.txt > /dev/null 2>&1
    python -m suoke_api_gateway.main &
    GATEWAY_PID=$!
    cd ../..
    
    # 等待 Gateway 启动
    sleep 3
    
    # 启动认证服务
    log_info "启动认证服务..."
    cd services/auth-service
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -r requirements.txt > /dev/null 2>&1
    python -m auth_service.main &
    AUTH_PID=$!
    cd ../..
    
    # 启动用户服务
    log_info "启动用户服务..."
    cd services/user-service
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -r requirements.txt > /dev/null 2>&1
    python -m user_service.main &
    USER_PID=$!
    cd ../..
    
    # 启动健康数据服务
    log_info "启动健康数据服务..."
    cd services/health-data-service
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -r requirements.txt > /dev/null 2>&1
    python -m health_data_service.main &
    HEALTH_PID=$!
    cd ../..
    
    # 启动五诊服务
    log_info "启动五诊诊断服务..."
    
    # 启动望诊服务
    cd services/diagnostic-services/look-service
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -r requirements.txt > /dev/null 2>&1
    python -m look_service.main &
    LOOK_PID=$!
    cd ../../..
    
    # 启动闻诊服务
    cd services/diagnostic-services/listen-service
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -r requirements.txt > /dev/null 2>&1
    python -m listen_service.main &
    LISTEN_PID=$!
    cd ../../..
    
    # 启动问诊服务
    cd services/diagnostic-services/inquiry-service
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -r requirements.txt > /dev/null 2>&1
    python -m inquiry_service.main &
    INQUIRY_PID=$!
    cd ../../..
    
    # 启动切诊服务
    cd services/diagnostic-services/palpation-service
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -r requirements.txt > /dev/null 2>&1
    python -m palpation_service.main &
    PALPATION_PID=$!
    cd ../../..
    
    # 启动算诊服务 (新增)
    log_info "启动算诊服务 (第五诊)..."
    cd services/diagnostic-services/calculation-service
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -r requirements.txt > /dev/null 2>&1
    python -m calculation_service.main &
    CALCULATION_PID=$!
    cd ../../..
    
    # 保存进程ID
    echo "$GATEWAY_PID" > .gateway.pid
    echo "$AUTH_PID" > .auth.pid
    echo "$USER_PID" > .user.pid
    echo "$HEALTH_PID" > .health.pid
    echo "$LOOK_PID" > .look.pid
    echo "$LISTEN_PID" > .listen.pid
    echo "$INQUIRY_PID" > .inquiry.pid
    echo "$PALPATION_PID" > .palpation.pid
    echo "$CALCULATION_PID" > .calculation.pid
    
    log_success "所有后端服务启动完成"
}

# 等待服务就绪
wait_for_services() {
    log_info "等待服务就绪..."
    
    local services=(
        "http://localhost:8000/health:API Gateway"
        "http://localhost:8001/health:认证服务"
        "http://localhost:8002/health:用户服务"
        "http://localhost:8003/health:健康数据服务"
        "http://localhost:8004/health:望诊服务"
        "http://localhost:8005/health:闻诊服务"
        "http://localhost:8006/health:问诊服务"
        "http://localhost:8007/health:切诊服务"
        "http://localhost:8008/health:算诊服务"
    )
    
    for service in "${services[@]}"; do
        IFS=':' read -r url name <<< "$service"
        log_info "等待 $name 就绪..."
        
        local max_attempts=30
        local attempt=1
        
        while [ $attempt -le $max_attempts ]; do
            if curl -s "$url" > /dev/null 2>&1; then
                log_success "$name 已就绪"
                break
            fi
            
            if [ $attempt -eq $max_attempts ]; then
                log_error "$name 启动失败"
                return 1
            fi
            
            sleep 2
            ((attempt++))
        done
    done
    
    log_success "所有服务已就绪"
}

# 启动前端应用
start_frontend() {
    log_info "启动前端应用..."
    
    # 安装依赖
    if [ ! -d "node_modules" ]; then
        log_info "安装前端依赖..."
        npm install > /dev/null 2>&1
    fi
    
    # 启动 React Native Metro bundler
    log_info "启动 Metro bundler..."
    npx react-native start &
    METRO_PID=$!
    echo "$METRO_PID" > .metro.pid
    
    # 等待 Metro 启动
    sleep 5
    
    log_success "前端应用启动完成"
}

# 显示服务状态
show_service_status() {
    log_info "五诊服务状态："
    echo
    echo "🌐 API Gateway:     http://localhost:8000"
    echo "🔐 认证服务:        http://localhost:8001"
    echo "👤 用户服务:        http://localhost:8002"
    echo "💊 健康数据服务:    http://localhost:8003"
    echo "👁️  望诊服务:        http://localhost:8004"
    echo "👂 闻诊服务:        http://localhost:8005"
    echo "💬 问诊服务:        http://localhost:8006"
    echo "🤚 切诊服务:        http://localhost:8007"
    echo "🧮 算诊服务:        http://localhost:8008 (新增)"
    echo "📱 前端应用:        http://localhost:3000"
    echo
    echo "📊 监控面板:        http://localhost:8000/admin"
    echo "📖 API文档:         http://localhost:8000/docs"
    echo
}

# 显示使用说明
show_usage_info() {
    log_info "五诊系统使用说明："
    echo
    echo "1. 传统四诊功能："
    echo "   - 望诊: 面部和舌部图像分析"
    echo "   - 闻诊: 语音和呼吸音分析"
    echo "   - 问诊: 症状和病史问卷"
    echo "   - 切诊: 脉象和触诊数据"
    echo
    echo "2. 新增算诊功能："
    echo "   - 子午流注分析: 基于十二时辰经络流注"
    echo "   - 八字体质分析: 根据出生八字分析体质"
    echo "   - 八卦配属分析: 运用八卦理论分析五行"
    echo "   - 五运六气分析: 结合时令分析气候影响"
    echo "   - 综合算诊分析: 多维度个性化分析"
    echo
    echo "3. 综合分析："
    echo "   - 五诊合参: 整合所有诊断结果"
    echo "   - 个性化建议: 基于综合分析的健康建议"
    echo "   - 跟踪管理: 健康状态跟踪和管理"
    echo
}

# 清理函数
cleanup() {
    log_info "正在停止所有服务..."
    
    # 停止所有后台进程
    if [ -f .gateway.pid ]; then
        kill $(cat .gateway.pid) 2>/dev/null || true
        rm .gateway.pid
    fi
    
    if [ -f .auth.pid ]; then
        kill $(cat .auth.pid) 2>/dev/null || true
        rm .auth.pid
    fi
    
    if [ -f .user.pid ]; then
        kill $(cat .user.pid) 2>/dev/null || true
        rm .user.pid
    fi
    
    if [ -f .health.pid ]; then
        kill $(cat .health.pid) 2>/dev/null || true
        rm .health.pid
    fi
    
    if [ -f .look.pid ]; then
        kill $(cat .look.pid) 2>/dev/null || true
        rm .look.pid
    fi
    
    if [ -f .listen.pid ]; then
        kill $(cat .listen.pid) 2>/dev/null || true
        rm .listen.pid
    fi
    
    if [ -f .inquiry.pid ]; then
        kill $(cat .inquiry.pid) 2>/dev/null || true
        rm .inquiry.pid
    fi
    
    if [ -f .palpation.pid ]; then
        kill $(cat .palpation.pid) 2>/dev/null || true
        rm .palpation.pid
    fi
    
    if [ -f .calculation.pid ]; then
        kill $(cat .calculation.pid) 2>/dev/null || true
        rm .calculation.pid
    fi
    
    if [ -f .metro.pid ]; then
        kill $(cat .metro.pid) 2>/dev/null || true
        rm .metro.pid
    fi
    
    log_success "所有服务已停止"
}

# 信号处理
trap cleanup EXIT INT TERM

# 主函数
main() {
    echo "=========================================="
    echo "    索克生活 - 五诊服务启动脚本"
    echo "=========================================="
    echo
    
    # 检查依赖
    check_dependencies
    
    # 检查端口
    check_ports
    
    # 启动后端服务
    start_backend_services
    
    # 等待服务就绪
    if ! wait_for_services; then
        log_error "服务启动失败，正在清理..."
        cleanup
        exit 1
    fi
    
    # 启动前端应用
    start_frontend
    
    # 显示状态
    show_service_status
    show_usage_info
    
    log_success "五诊系统启动完成！"
    log_info "按 Ctrl+C 停止所有服务"
    
    # 保持脚本运行
    while true; do
        sleep 1
    done
}

# 运行主函数
main "$@" 