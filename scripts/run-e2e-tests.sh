#!/bin/bash

# 索克生活端到端测试运行脚本
# Suoke Life End-to-End Test Runner

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
    log_info "检查依赖..."
    
    # 检查Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安装"
        exit 1
    fi
    
    # 检查npm
    if ! command -v npm &> /dev/null; then
        log_error "npm 未安装"
        exit 1
    fi
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    # 检查Docker (可选)
    if command -v docker &> /dev/null; then
        log_success "Docker 可用"
    else
        log_warning "Docker 未安装，将跳过容器化测试"
    fi
    
    log_success "依赖检查完成"
}

# 安装依赖
install_dependencies() {
    log_info "安装测试依赖..."
    
    # 安装Node.js依赖
    npm install --silent
    
    # 安装Python依赖
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt --quiet
    fi
    
    log_success "依赖安装完成"
}

# 启动后端服务
start_backend_services() {
    log_info "启动后端服务..."
    
    # 启动API网关
    if [ -f "services/api-gateway/app.py" ]; then
        cd services/api-gateway
        python3 app.py &
        API_GATEWAY_PID=$!
        cd ../..
        log_success "API网关已启动 (PID: $API_GATEWAY_PID)"
    fi
    
    # 启动智能体服务
    for service in xiaoai xiaoke laoke soer; do
        service_path="services/agent-services/${service}-service"
        if [ -d "$service_path" ]; then
            cd "$service_path"
            if [ -f "app.py" ]; then
                python3 app.py &
                eval "${service^^}_PID=\$!"
                log_success "${service}服务已启动"
            fi
            cd ../../..
        fi
    done
    
    # 等待服务启动
    sleep 5
    log_success "后端服务启动完成"
}

# 停止后端服务
stop_backend_services() {
    log_info "停止后端服务..."
    
    # 停止所有后台进程
    if [ ! -z "$API_GATEWAY_PID" ]; then
        kill $API_GATEWAY_PID 2>/dev/null || true
    fi
    
    for service in XIAOAI XIAOKE LAOKE SOER; do
        pid_var="${service}_PID"
        pid=${!pid_var}
        if [ ! -z "$pid" ]; then
            kill $pid 2>/dev/null || true
        fi
    done
    
    # 清理端口
    pkill -f "python3.*app.py" 2>/dev/null || true
    
    log_success "后端服务已停止"
}

# 运行用户旅程测试
run_user_journey_tests() {
    log_info "运行用户旅程测试..."
    
    npx jest src/__tests__/e2e/user-journey.test.tsx \
        --verbose \
        --detectOpenHandles \
        --forceExit \
        --testTimeout=60000 \
        --reporters=default \
        --reporters=jest-html-reporters
    
    if [ $? -eq 0 ]; then
        log_success "用户旅程测试通过"
    else
        log_error "用户旅程测试失败"
        return 1
    fi
}

# 运行智能体协作测试
run_agent_collaboration_tests() {
    log_info "运行智能体协作测试..."
    
    npx jest src/__tests__/e2e/agent-collaboration.test.tsx \
        --verbose \
        --detectOpenHandles \
        --forceExit \
        --testTimeout=120000 \
        --reporters=default \
        --reporters=jest-html-reporters
    
    if [ $? -eq 0 ]; then
        log_success "智能体协作测试通过"
    else
        log_error "智能体协作测试失败"
        return 1
    fi
}

# 运行性能压力测试
run_performance_tests() {
    log_info "运行性能压力测试..."
    
    npx jest src/__tests__/e2e/performance-stress.test.tsx \
        --verbose \
        --detectOpenHandles \
        --forceExit \
        --testTimeout=180000 \
        --reporters=default \
        --reporters=jest-html-reporters
    
    if [ $? -eq 0 ]; then
        log_success "性能压力测试通过"
    else
        log_error "性能压力测试失败"
        return 1
    fi
}

# 运行综合测试
run_comprehensive_tests() {
    log_info "运行综合端到端测试..."
    
    npx jest src/__tests__/e2e/comprehensive-e2e.test.tsx \
        --verbose \
        --detectOpenHandles \
        --forceExit \
        --testTimeout=300000 \
        --reporters=default \
        --reporters=jest-html-reporters
    
    if [ $? -eq 0 ]; then
        log_success "综合端到端测试通过"
    else
        log_error "综合端到端测试失败"
        return 1
    fi
}

# 生成测试报告
generate_test_report() {
    log_info "生成测试报告..."
    
    # 创建报告目录
    mkdir -p reports/e2e
    
    # 生成覆盖率报告
    npx jest --coverage --coverageDirectory=reports/e2e/coverage
    
    # 生成HTML报告
    if [ -f "jest-html-reporters-attach/jest_html_reporters.html" ]; then
        cp jest-html-reporters-attach/jest_html_reporters.html reports/e2e/
        log_success "HTML测试报告已生成: reports/e2e/jest_html_reporters.html"
    fi
    
    log_success "测试报告生成完成"
}

# 清理环境
cleanup() {
    log_info "清理测试环境..."
    
    # 停止服务
    stop_backend_services
    
    # 清理临时文件
    rm -rf node_modules/.cache/jest
    rm -rf .jest-cache
    
    log_success "环境清理完成"
}

# 主函数
main() {
    log_info "开始索克生活端到端测试"
    
    # 设置错误处理
    trap cleanup EXIT
    
    # 解析命令行参数
    TEST_TYPE=${1:-"all"}
    
    case $TEST_TYPE in
        "user-journey")
            check_dependencies
            install_dependencies
            start_backend_services
            run_user_journey_tests
            ;;
        "agent-collaboration")
            check_dependencies
            install_dependencies
            start_backend_services
            run_agent_collaboration_tests
            ;;
        "performance")
            check_dependencies
            install_dependencies
            start_backend_services
            run_performance_tests
            ;;
        "comprehensive")
            check_dependencies
            install_dependencies
            start_backend_services
            run_comprehensive_tests
            ;;
        "all")
            check_dependencies
            install_dependencies
            start_backend_services
            
            # 运行所有测试
            run_user_journey_tests
            run_agent_collaboration_tests
            run_performance_tests
            run_comprehensive_tests
            
            generate_test_report
            ;;
        *)
            log_error "未知的测试类型: $TEST_TYPE"
            echo "用法: $0 [user-journey|agent-collaboration|performance|comprehensive|all]"
            exit 1
            ;;
    esac
    
    log_success "索克生活端到端测试完成"
}

# 运行主函数
main "$@" 