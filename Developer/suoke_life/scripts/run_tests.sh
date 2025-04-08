#!/bin/bash

# 测试运行脚本

set -e

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
    echo "  -c, --coverage          生成测试覆盖率报告"
    echo "  -v, --verbose           显示详细输出"
    echo "  -e, --error             运行错误情况测试"
    echo "  -y, --boundary          运行边界条件测试"
    echo "  -l, --lifecycle         运行生命周期测试"
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
echo "== 代理协调器服务测试 =="
echo "运行目录: $(pwd)"
echo ""

# 确保测试前的清理工作
go clean -testcache

# 运行单元测试
if [ "$RUN_UNIT" = true ]; then
    echo "正在运行单元测试..."
    if [ "$GEN_COVERAGE" = true ]; then
        go test $VERBOSE -coverprofile=coverage.out ./internal/handlers/...
        go tool cover -html=coverage.out -o coverage.html
        echo "测试覆盖率报告已生成：coverage.html"
    else
        go test $VERBOSE ./internal/handlers/...
    fi
    echo "单元测试完成"
    echo ""
fi

# 运行集成测试
if [ "$RUN_INTEGRATION" = true ]; then
    echo "正在运行集成测试..."
    go test $VERBOSE ./internal/tests/integration/...
    echo "集成测试完成"
    echo ""
fi

# 运行基准测试
if [ "$RUN_BENCHMARK" = true ]; then
    echo "正在运行基准测试..."
    go test -bench=. -benchmem ./internal/tests/benchmark/...
    echo "基准测试完成"
    echo ""
fi

# 运行错误情况测试
if [ "$RUN_ERROR" = true ]; then
    echo "正在运行错误情况测试..."
    go test $VERBOSE -run TestError ./internal/tests/integration/...
    echo "错误情况测试完成"
    echo ""
fi

# 运行边界条件测试
if [ "$RUN_BOUNDARY" = true ]; then
    echo "正在运行边界条件测试..."
    go test $VERBOSE -run TestBoundary ./internal/tests/integration/...
    echo "边界条件测试完成"
    echo ""
fi

# 运行生命周期测试
if [ "$RUN_LIFECYCLE" = true ]; then
    echo "正在运行生命周期测试..."
    go test $VERBOSE -run TestLifecycle ./internal/tests/integration/...
    echo "生命周期测试完成"
    echo ""
fi

echo "所有指定的测试已完成！"

# 运行完整的测试套件
if [ "$RUN_UNIT" = true ] && [ "$RUN_INTEGRATION" = true ] && [ "$RUN_BENCHMARK" = true ] && [ "$RUN_ERROR" = true ] && [ "$RUN_BOUNDARY" = true ] && [ "$RUN_LIFECYCLE" = true ]; then
    echo ""
    echo "== 测试摘要 =="
    echo "已完成所有测试套件的运行"
    
    # 如果生成了覆盖率报告
    if [ "$GEN_COVERAGE" = true ]; then
        total_coverage=$(go tool cover -func=coverage.out | grep total | awk '{print $3}')
        echo "总测试覆盖率: $total_coverage"
    fi
    
    echo "所有测试均已通过！"
fi 