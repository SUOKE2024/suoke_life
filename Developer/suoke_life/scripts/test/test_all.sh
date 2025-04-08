#!/bin/bash

# 代理协调器服务全面测试脚本

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

# 显示帮助信息
function show_help {
    echo "代理协调器服务测试运行脚本"
    echo ""
    echo "用法:"
    echo "  $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help              显示帮助信息"
    echo "  -a, --all               运行所有测试"
    echo "  -u, --unit              仅运行单元测试"
    echo "  -i, --integration       仅运行集成测试"
    echo "  -b, --benchmark         仅运行基准测试"
    echo "  -e, --error             运行错误情况测试"
    echo "  -y, --boundary          运行边界条件测试"
    echo "  -l, --lifecycle         运行生命周期测试"
    echo "  -c, --coverage          生成测试覆盖率报告"
    echo "  -v, --verbose           显示详细输出"
    echo ""
    exit 0
}

# 默认参数
RUN_UNIT=false
RUN_INTEGRATION=false
RUN_BENCHMARK=false
RUN_ERROR=false
RUN_BOUNDARY=false
RUN_LIFECYCLE=false
GEN_COVERAGE=false
VERBOSE=""

# 如果没有参数，显示帮助
if [ $# -eq 0 ]; then
    show_help
fi

# 解析参数
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -h|--help) show_help ;;
        -a|--all)
            RUN_UNIT=true
            RUN_INTEGRATION=true
            RUN_BENCHMARK=true
            RUN_ERROR=true
            RUN_BOUNDARY=true
            RUN_LIFECYCLE=true
            shift ;;
        -u|--unit)
            RUN_UNIT=true
            shift ;;
        -i|--integration)
            RUN_INTEGRATION=true
            shift ;;
        -b|--benchmark)
            RUN_BENCHMARK=true
            shift ;;
        -e|--error)
            RUN_ERROR=true
            shift ;;
        -y|--boundary)
            RUN_BOUNDARY=true
            shift ;;
        -l|--lifecycle)
            RUN_LIFECYCLE=true
            shift ;;
        -c|--coverage)
            GEN_COVERAGE=true
            shift ;;
        -v|--verbose)
            VERBOSE="-v"
            shift ;;
        *) echo "未知参数: $1"; exit 1 ;;
    esac
done

# 显示测试信息头部
log_info "== 代理协调器服务测试 =="
log_info "运行目录: $(pwd)"
echo ""

# 确保测试前的清理工作
go clean -testcache

# 运行单元测试
if [ "$RUN_UNIT" = true ]; then
    log_info "正在运行单元测试..."
    if [ "$GEN_COVERAGE" = true ]; then
        go test $VERBOSE -coverprofile=coverage.out ./internal/handlers/...
        go tool cover -html=coverage.out -o coverage.html
        log_success "测试覆盖率报告已生成：coverage.html"
    else
        go test $VERBOSE ./internal/handlers/...
    fi
    log_success "单元测试完成"
    echo ""
fi

# 运行集成测试
if [ "$RUN_INTEGRATION" = true ]; then
    log_info "正在运行集成测试..."
    go test $VERBOSE ./internal/tests/integration/...
    log_success "集成测试完成"
    echo ""
fi

# 运行基准测试
if [ "$RUN_BENCHMARK" = true ]; then
    log_info "正在运行基准测试..."
    go test -bench=. -benchmem ./internal/tests/benchmark/...
    log_success "基准测试完成"
    echo ""
fi

# 运行错误情况测试
if [ "$RUN_ERROR" = true ]; then
    log_info "正在运行错误情况测试..."
    go test $VERBOSE -run TestError ./internal/tests/integration/...
    log_success "错误情况测试完成"
    echo ""
fi

# 运行边界条件测试
if [ "$RUN_BOUNDARY" = true ]; then
    log_info "正在运行边界条件测试..."
    go test $VERBOSE -run TestBoundary ./internal/tests/integration/...
    log_success "边界条件测试完成"
    echo ""
fi

# 运行生命周期测试
if [ "$RUN_LIFECYCLE" = true ]; then
    log_info "正在运行生命周期测试..."
    go test $VERBOSE -run TestLifecycle ./internal/tests/integration/...
    log_success "生命周期测试完成"
    echo ""
fi

log_info "所有指定的测试已完成！"

# 运行完整的测试套件
if [ "$RUN_UNIT" = true ] && [ "$RUN_INTEGRATION" = true ] && [ "$RUN_BENCHMARK" = true ] && [ "$RUN_ERROR" = true ] && [ "$RUN_BOUNDARY" = true ] && [ "$RUN_LIFECYCLE" = true ]; then
    echo ""
    log_info "== 测试摘要 =="
    log_success "已完成所有测试套件的运行"
    
    # 如果生成了覆盖率报告
    if [ "$GEN_COVERAGE" = true ]; then
        total_coverage=$(go tool cover -func=coverage.out | grep total | awk '{print $3}')
        log_success "总测试覆盖率: $total_coverage"
    fi
    
    log_success "所有测试均已通过！"
fi 