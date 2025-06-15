#!/bin/bash

# Agentic AI 测试运行脚本
# 提供不同类型的测试运行选项

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

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

# 显示帮助信息
show_help() {
    echo "Agentic AI 测试运行脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help              显示此帮助信息"
    echo "  -a, --all               运行所有测试"
    echo "  -u, --unit              运行单元测试"
    echo "  -i, --integration       运行集成测试"
    echo "  -p, --performance       运行性能测试"
    echo "  -e, --e2e               运行端到端测试"
    echo "  -c, --coverage          生成覆盖率报告"
    echo "  -w, --watch             监视模式"
    echo "  -v, --verbose           详细输出"
    echo "  --ci                    CI模式（静默输出）"
    echo "  --parallel              并行运行测试"
    echo "  --update-snapshots      更新快照"
    echo "  --bail                  遇到错误时停止"
    echo ""
    echo "示例:"
    echo "  $0 --unit --coverage    运行单元测试并生成覆盖率报告"
    echo "  $0 --all --ci           在CI模式下运行所有测试"
    echo "  $0 --performance        仅运行性能测试"
}

# 检查依赖
check_dependencies() {
    log_info "检查测试依赖..."
    
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安装"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        log_error "npm 未安装"
        exit 1
    fi
    
    if [ ! -f "package.json" ]; then
        log_error "package.json 文件不存在"
        exit 1
    fi
    
    if [ ! -d "node_modules" ]; then
        log_warning "node_modules 目录不存在，正在安装依赖..."
        npm install
    fi
    
    log_success "依赖检查完成"
}

# 设置测试环境
setup_test_environment() {
    log_info "设置测试环境..."
    
    # 设置环境变量
    export NODE_ENV=test
    export AGENTIC_AI_TEST_MODE=true
    export LOG_LEVEL=error
    
    # 创建测试目录
    mkdir -p tests/reports
    mkdir -p tests/coverage
    mkdir -p tests/logs
    
    # 清理之前的测试结果
    rm -rf tests/reports/*
    rm -rf tests/coverage/*
    rm -rf tests/logs/*
    
    log_success "测试环境设置完成"
}

# 运行单元测试
run_unit_tests() {
    log_info "运行单元测试..."
    
    local jest_args="--testPathPattern=tests/agentic"
    
    if [ "$VERBOSE" = true ]; then
        jest_args="$jest_args --verbose"
    fi
    
    if [ "$CI_MODE" = true ]; then
        jest_args="$jest_args --silent --ci"
    fi
    
    if [ "$COVERAGE" = true ]; then
        jest_args="$jest_args --coverage"
    fi
    
    if [ "$PARALLEL" = true ]; then
        jest_args="$jest_args --maxWorkers=4"
    fi
    
    if [ "$UPDATE_SNAPSHOTS" = true ]; then
        jest_args="$jest_args --updateSnapshot"
    fi
    
    if [ "$BAIL" = true ]; then
        jest_args="$jest_args --bail"
    fi
    
    npx jest $jest_args
    
    if [ $? -eq 0 ]; then
        log_success "单元测试通过"
    else
        log_error "单元测试失败"
        return 1
    fi
}

# 运行集成测试
run_integration_tests() {
    log_info "运行集成测试..."
    
    local jest_args="--testPathPattern=tests/integration --testTimeout=60000"
    
    if [ "$VERBOSE" = true ]; then
        jest_args="$jest_args --verbose"
    fi
    
    if [ "$CI_MODE" = true ]; then
        jest_args="$jest_args --silent --ci"
    fi
    
    if [ "$PARALLEL" = true ]; then
        jest_args="$jest_args --maxWorkers=2"
    fi
    
    if [ "$BAIL" = true ]; then
        jest_args="$jest_args --bail"
    fi
    
    npx jest $jest_args
    
    if [ $? -eq 0 ]; then
        log_success "集成测试通过"
    else
        log_error "集成测试失败"
        return 1
    fi
}

# 运行性能测试
run_performance_tests() {
    log_info "运行性能测试..."
    
    local jest_args="--testPathPattern=tests/performance --testTimeout=120000"
    
    if [ "$VERBOSE" = true ]; then
        jest_args="$jest_args --verbose"
    fi
    
    if [ "$CI_MODE" = true ]; then
        jest_args="$jest_args --silent --ci"
    fi
    
    # 性能测试通常不并行运行以获得准确结果
    jest_args="$jest_args --maxWorkers=1"
    
    if [ "$BAIL" = true ]; then
        jest_args="$jest_args --bail"
    fi
    
    npx jest $jest_args
    
    if [ $? -eq 0 ]; then
        log_success "性能测试通过"
    else
        log_error "性能测试失败"
        return 1
    fi
}

# 运行端到端测试
run_e2e_tests() {
    log_info "运行端到端测试..."
    
    local jest_args="--testPathPattern=tests/e2e --testTimeout=180000"
    
    if [ "$VERBOSE" = true ]; then
        jest_args="$jest_args --verbose"
    fi
    
    if [ "$CI_MODE" = true ]; then
        jest_args="$jest_args --silent --ci"
    fi
    
    # E2E测试通常串行运行
    jest_args="$jest_args --maxWorkers=1"
    
    if [ "$BAIL" = true ]; then
        jest_args="$jest_args --bail"
    fi
    
    npx jest $jest_args
    
    if [ $? -eq 0 ]; then
        log_success "端到端测试通过"
    else
        log_error "端到端测试失败"
        return 1
    fi
}

# 运行所有测试
run_all_tests() {
    log_info "运行所有测试..."
    
    local failed_tests=()
    
    # 运行单元测试
    if ! run_unit_tests; then
        failed_tests+=("单元测试")
    fi
    
    # 运行集成测试
    if ! run_integration_tests; then
        failed_tests+=("集成测试")
    fi
    
    # 运行性能测试
    if ! run_performance_tests; then
        failed_tests+=("性能测试")
    fi
    
    # 运行端到端测试
    if ! run_e2e_tests; then
        failed_tests+=("端到端测试")
    fi
    
    if [ ${#failed_tests[@]} -eq 0 ]; then
        log_success "所有测试通过"
    else
        log_error "以下测试失败: ${failed_tests[*]}"
        return 1
    fi
}

# 监视模式
run_watch_mode() {
    log_info "启动监视模式..."
    
    local jest_args="--watch"
    
    if [ "$VERBOSE" = true ]; then
        jest_args="$jest_args --verbose"
    fi
    
    npx jest $jest_args
}

# 生成测试报告
generate_reports() {
    log_info "生成测试报告..."
    
    # 生成HTML报告
    if [ -f "tests/reports/test-report.html" ]; then
        log_success "HTML测试报告: tests/reports/test-report.html"
    fi
    
    # 生成JUnit报告
    if [ -f "tests/reports/junit.xml" ]; then
        log_success "JUnit报告: tests/reports/junit.xml"
    fi
    
    # 生成覆盖率报告
    if [ -d "tests/coverage" ] && [ "$(ls -A tests/coverage)" ]; then
        log_success "覆盖率报告: tests/coverage/lcov-report/index.html"
    fi
}

# 清理测试环境
cleanup() {
    log_info "清理测试环境..."
    
    # 清理临时文件
    rm -rf .jest-cache
    
    # 保留报告文件
    log_success "清理完成"
}

# 主函数
main() {
    local RUN_ALL=false
    local RUN_UNIT=false
    local RUN_INTEGRATION=false
    local RUN_PERFORMANCE=false
    local RUN_E2E=false
    local COVERAGE=false
    local WATCH=false
    local VERBOSE=false
    local CI_MODE=false
    local PARALLEL=false
    local UPDATE_SNAPSHOTS=false
    local BAIL=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -a|--all)
                RUN_ALL=true
                shift
                ;;
            -u|--unit)
                RUN_UNIT=true
                shift
                ;;
            -i|--integration)
                RUN_INTEGRATION=true
                shift
                ;;
            -p|--performance)
                RUN_PERFORMANCE=true
                shift
                ;;
            -e|--e2e)
                RUN_E2E=true
                shift
                ;;
            -c|--coverage)
                COVERAGE=true
                shift
                ;;
            -w|--watch)
                WATCH=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            --ci)
                CI_MODE=true
                shift
                ;;
            --parallel)
                PARALLEL=true
                shift
                ;;
            --update-snapshots)
                UPDATE_SNAPSHOTS=true
                shift
                ;;
            --bail)
                BAIL=true
                shift
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 如果没有指定测试类型，默认运行所有测试
    if [ "$RUN_ALL" = false ] && [ "$RUN_UNIT" = false ] && [ "$RUN_INTEGRATION" = false ] && [ "$RUN_PERFORMANCE" = false ] && [ "$RUN_E2E" = false ] && [ "$WATCH" = false ]; then
        RUN_ALL=true
    fi
    
    # 检查依赖和设置环境
    check_dependencies
    setup_test_environment
    
    # 设置错误处理
    trap cleanup EXIT
    
    local exit_code=0
    
    # 运行测试
    if [ "$WATCH" = true ]; then
        run_watch_mode
    elif [ "$RUN_ALL" = true ]; then
        if ! run_all_tests; then
            exit_code=1
        fi
    else
        if [ "$RUN_UNIT" = true ]; then
            if ! run_unit_tests; then
                exit_code=1
            fi
        fi
        
        if [ "$RUN_INTEGRATION" = true ]; then
            if ! run_integration_tests; then
                exit_code=1
            fi
        fi
        
        if [ "$RUN_PERFORMANCE" = true ]; then
            if ! run_performance_tests; then
                exit_code=1
            fi
        fi
        
        if [ "$RUN_E2E" = true ]; then
            if ! run_e2e_tests; then
                exit_code=1
            fi
        fi
    fi
    
    # 生成报告
    generate_reports
    
    if [ $exit_code -eq 0 ]; then
        log_success "测试运行完成"
    else
        log_error "测试运行失败"
    fi
    
    exit $exit_code
}

# 运行主函数
main "$@"