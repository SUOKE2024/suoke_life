#!/bin/bash
set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示帮助信息
show_help() {
    echo -e "${GREEN}====== 索克生活知识库服务测试脚本 ======${NC}"
    echo "用法: $0 [选项]"
    echo "选项:"
    echo "  -u, --unit        运行单元测试"
    echo "  -i, --integration 运行集成测试"
    echo "  -e, --e2e         运行端到端测试"
    echo "  -b, --benchmark   运行性能基准测试"
    echo "  -c, --coverage    生成测试覆盖率报告"
    echo "  -r, --report      生成测试报告"
    echo "  -h, --help        显示帮助信息"
    echo "使用参数示例: $0 -u -c"
}

# 检查是否未提供任何参数
if [ $# -eq 0 ]; then
    show_help
    exit 1
fi

# 设置默认环境变量
export DB_CONNECTION_STRING="postgresql://testuser:testpassword@localhost:5432/knowledge_base_test?sslmode=disable"
export VECTOR_STORE_USE_MOCK="true"

# 解析参数
run_unit_tests=false
run_integration_tests=false
run_e2e_tests=false
run_benchmarks=false
generate_coverage=false
generate_report=false

# 处理参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--unit)
        run_unit_tests=true
        shift
        ;;
        -i|--integration)
        run_integration_tests=true
        shift
        ;;
        -e|--e2e)
        run_e2e_tests=true
        shift
        ;;
        -b|--benchmark)
        run_benchmarks=true
        shift
        ;;
        -c|--coverage)
        generate_coverage=true
        shift
        ;;
        -r|--report)
        generate_report=true
        shift
        ;;
        -h|--help)
        show_help
        exit 0
        ;;
        *)
        echo -e "${RED}错误: 未知参数 $1${NC}"
        show_help
        exit 1
        ;;
    esac
done

echo -e "${GREEN}====== 索克生活知识库服务测试脚本 ======${NC}"

# 确保工作目录是项目根目录
cd "$(dirname "$0")/.."

# 验证Go安装
if ! command -v go &> /dev/null; then
    echo -e "${RED}错误: Go未安装，请安装Go 1.24或更高版本${NC}"
    exit 1
fi

go_version=$(go version | cut -d ' ' -f 3 | cut -d'.' -f2)
if [[ ${go_version} -lt 24 ]]; then
    echo -e "${YELLOW}警告: Go版本过低，推荐使用Go 1.24或更高版本${NC}"
fi

# 确保输出目录存在
mkdir -p test-output

# 设置环境变量 - 使用已有的本地环境
export VECTOR_STORE_HOST="localhost" 
export VECTOR_STORE_PORT="19530"
export VECTOR_STORE_COLLECTION="test_documents"
export EMBEDDING_MODEL_URL="http://localhost:8000/embed"

# 更新依赖
echo -e "${YELLOW}=> 更新依赖...${NC}"
go mod tidy > /dev/null

# 运行单元测试
if [ "$run_unit_tests" = true ]; then
    echo -e "${YELLOW}=> 运行单元测试...${NC}"
    if [ "$generate_coverage" = true ]; then
        mkdir -p test-output
        go test -v -coverprofile=test-output/coverage.out ./internal/... ./pkg/...
    else
        go test -v ./internal/... ./pkg/...
    fi
fi

# 运行集成测试
if [ "$run_integration_tests" = true ]; then
    echo -e "${YELLOW}=> 运行集成测试...${NC}"
    # 需要具体实现
    echo "暂未实现集成测试"
fi

# 运行端到端测试
if [ "$run_e2e_tests" = true ]; then
    echo -e "${YELLOW}=> 运行端到端测试...${NC}"
    # 需要具体实现
    echo "暂未实现端到端测试"
fi

# 运行性能基准测试
if [ "$run_benchmarks" = true ]; then
    echo -e "${YELLOW}=> 运行性能基准测试...${NC}"
    go test -bench=. -benchmem ./internal/... ./pkg/...
fi

# 生成覆盖率报告
if [ "$generate_coverage" = true ] && [ -f "test-output/coverage.out" ]; then
    echo -e "${YELLOW}=> 生成覆盖率报告...${NC}"
    go tool cover -html=test-output/coverage.out -o test-output/coverage.html
    echo -e "${GREEN}覆盖率报告已生成: test-output/coverage.html${NC}"
fi

# 生成测试报告
if [ "$generate_report" = true ]; then
    echo -e "${YELLOW}=> 生成测试报告...${NC}"
    # 需要具体实现
    echo "暂未实现测试报告生成"
fi

echo -e "${GREEN}测试完成!${NC}"