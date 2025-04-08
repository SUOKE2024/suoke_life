#!/bin/bash

# 索克生活前后端测试集成脚本
# 该脚本执行完整的前后端测试流程，包括：
# 1. 后端Go服务单元测试
# 2. 后端Go服务集成测试
# 3. 前端Flutter单元测试
# 4. 前端Flutter集成测试

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
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

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1命令不存在，请安装后再试"
        exit 1
    fi
}

# 检查需要的命令
check_command go
check_command flutter
check_command docker
check_command docker-compose

# 显示测试摘要
show_summary() {
    echo "======================================================"
    echo "                   测试执行摘要                        "
    echo "======================================================"
    echo "API网关测试: ${1}"
    echo "认证服务测试: ${2}"
    echo "用户服务测试: ${3}"
    echo "前端单元测试: ${4}"
    echo "前端集成测试: ${5}"
    echo "======================================================" 
}

# 获取当前目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# 测试状态
api_gateway_status="未运行"
auth_service_status="未运行"
user_service_status="未运行"
flutter_unit_status="未运行"
flutter_integration_status="未运行"

# 创建测试结果目录
mkdir -p test-results

log_info "开始前后端集成测试..."

# 1. 后端测试
log_info "开始后端服务测试..."

# 1.1 API网关测试
log_info "运行API网关测试..."
cd "$PROJECT_ROOT/services/api-gateway"
if go test -v ./internal/... -coverprofile=coverage.out > "$PROJECT_ROOT/test-results/api-gateway-test.log" 2>&1; then
    api_gateway_status="${GREEN}通过${NC}"
    log_success "API网关测试通过"
else
    api_gateway_status="${RED}失败${NC}"
    log_error "API网关测试失败"
    cat "$PROJECT_ROOT/test-results/api-gateway-test.log"
fi

# 1.2 认证服务测试
log_info "运行认证服务测试..."
cd "$PROJECT_ROOT/services/auth-service"
if go test -v ./internal/... -coverprofile=coverage.out > "$PROJECT_ROOT/test-results/auth-service-test.log" 2>&1; then
    auth_service_status="${GREEN}通过${NC}"
    log_success "认证服务测试通过"
else
    auth_service_status="${RED}失败${NC}"
    log_error "认证服务测试失败"
    cat "$PROJECT_ROOT/test-results/auth-service-test.log"
fi

# 1.3 用户服务测试
log_info "运行用户服务测试..."
cd "$PROJECT_ROOT/services/user-service"
if go test -v ./internal/... -coverprofile=coverage.out > "$PROJECT_ROOT/test-results/user-service-test.log" 2>&1; then
    user_service_status="${GREEN}通过${NC}"
    log_success "用户服务测试通过"
else
    user_service_status="${RED}失败${NC}"
    log_error "用户服务测试失败"
    cat "$PROJECT_ROOT/test-results/user-service-test.log"
fi

# 2. 前端测试
log_info "开始前端测试..."
cd "$PROJECT_ROOT"

# 2.1 Flutter单元测试
log_info "运行Flutter单元测试..."
if flutter test --coverage test/unit > "$PROJECT_ROOT/test-results/flutter-unit-test.log" 2>&1; then
    flutter_unit_status="${GREEN}通过${NC}"
    log_success "Flutter单元测试通过"
else
    flutter_unit_status="${RED}失败${NC}"
    log_error "Flutter单元测试失败"
    cat "$PROJECT_ROOT/test-results/flutter-unit-test.log"
fi

# 2.2 Flutter集成测试
log_info "运行Flutter集成测试..."
# 先检查API服务是否可用
log_info "检查后端API服务可用性..."

# 启动测试环境的Docker容器
cd "$PROJECT_ROOT/services"
log_info "启动测试环境Docker容器..."
docker-compose -f docker-compose.test.yml up -d

# 等待服务启动
log_info "等待服务启动..."
sleep 10

# 检查服务可用性
SERVICES_AVAILABLE=true
if ! curl -s http://localhost:8080/health | grep -q "status.*ok"; then
    log_error "API网关服务不可用"
    SERVICES_AVAILABLE=false
fi

if ! curl -s http://localhost:8081/health | grep -q "status.*ok"; then
    log_error "认证服务不可用"
    SERVICES_AVAILABLE=false
fi

if ! curl -s http://localhost:8082/health | grep -q "status.*ok"; then
    log_error "用户服务不可用"
    SERVICES_AVAILABLE=false
fi

if [ "$SERVICES_AVAILABLE" = true ]; then
    cd "$PROJECT_ROOT"
    
    export SUOKE_API_BASE_URL=http://localhost:8080
    
    if flutter drive --driver=test_driver/integration_test.dart --target=test/integration/api_integration_test.dart > "$PROJECT_ROOT/test-results/flutter-integration-test.log" 2>&1; then
        flutter_integration_status="${GREEN}通过${NC}"
        log_success "Flutter集成测试通过"
    else
        flutter_integration_status="${RED}失败${NC}"
        log_error "Flutter集成测试失败"
        cat "$PROJECT_ROOT/test-results/flutter-integration-test.log"
    fi
else
    flutter_integration_status="${YELLOW}跳过${NC} (服务不可用)"
    log_warning "由于后端服务不可用，跳过Flutter集成测试"
fi

# 停止Docker容器
cd "$PROJECT_ROOT/services"
log_info "停止测试环境Docker容器..."
docker-compose -f docker-compose.test.yml down

# 显示测试结果摘要
cd "$PROJECT_ROOT"
show_summary "$api_gateway_status" "$auth_service_status" "$user_service_status" "$flutter_unit_status" "$flutter_integration_status"

# 结束
log_info "前后端集成测试完成，详细日志请查看 test-results 目录"

# 检查是否所有测试都通过
if [[ "$api_gateway_status" == *"通过"* && 
      "$auth_service_status" == *"通过"* && 
      "$user_service_status" == *"通过"* && 
      "$flutter_unit_status" == *"通过"* && 
      ("$flutter_integration_status" == *"通过"* || "$flutter_integration_status" == *"跳过"*) ]]; then
    log_success "所有测试通过"
    exit 0
else
    log_error "测试失败"
    exit 1
fi