#!/bin/bash

# 索克生活知识库服务 Docker测试脚本
# 该脚本用于在Docker环境中运行测试，包括设置测试数据库和执行各类测试

set -e

# 脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 项目根目录
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}====== 索克生活知识库服务Docker测试环境 ======${NC}"

# 检查Docker环境
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker未安装，请先安装Docker${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}错误: docker-compose未安装，请先安装docker-compose${NC}"
    exit 1
fi

# 定义测试数据库信息
TEST_DB_NAME="knowledge_base_test"
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="postgres"
POSTGRES_HOST="localhost"
POSTGRES_PORT="5432"

# 启动测试环境
start_test_env() {
    echo -e "${YELLOW}启动测试环境...${NC}"
    cd "$PROJECT_ROOT"
    
    # 检查是否已有容器在运行
    if docker-compose ps | grep -q "Up"; then
        echo -e "${GREEN}测试环境已运行${NC}"
    else
        # 启动所需服务，不包括milvus（因为可能有网络问题）
        echo -e "${YELLOW}启动PostgreSQL、etcd、minio和embedding-service...${NC}"
        docker-compose up -d postgres etcd minio embedding-service
        
        echo -e "${YELLOW}等待服务就绪...${NC}"
        sleep 5
    fi
}

# 初始化测试数据库
init_test_db() {
    echo -e "${YELLOW}初始化测试数据库...${NC}"
    cd "$PROJECT_ROOT"
    
    # 检查测试数据库是否存在
    if docker exec kb-postgres psql -U "$POSTGRES_USER" -lqt | grep -q "$TEST_DB_NAME"; then
        echo -e "${GREEN}测试数据库 $TEST_DB_NAME 已存在${NC}"
    else
        echo -e "${YELLOW}创建测试数据库 $TEST_DB_NAME...${NC}"
        docker exec kb-postgres psql -U "$POSTGRES_USER" -c "CREATE DATABASE $TEST_DB_NAME;"
        echo -e "${GREEN}测试数据库已创建${NC}"
    fi
    
    # 创建测试专用用户
    echo -e "${YELLOW}确保测试用户存在...${NC}"
    if ! docker exec kb-postgres psql -U "$POSTGRES_USER" -c "\du" | grep -q "testuser"; then
        echo -e "${YELLOW}创建测试用户...${NC}"
        docker exec kb-postgres psql -U "$POSTGRES_USER" -c "CREATE USER testuser WITH PASSWORD 'testpassword';"
        docker exec kb-postgres psql -U "$POSTGRES_USER" -c "GRANT ALL PRIVILEGES ON DATABASE $TEST_DB_NAME TO testuser;"
        echo -e "${GREEN}测试用户已创建${NC}"
    else
        echo -e "${GREEN}测试用户已存在${NC}"
    fi
    
    echo -e "${YELLOW}确认数据库连接信息...${NC}"
    docker exec kb-postgres psql -U "$POSTGRES_USER" -c "\conninfo"
    
    # 设置环境变量 - 使用testuser
    export DB_CONNECTION_STRING="postgresql://testuser:testpassword@localhost:5432/$TEST_DB_NAME?sslmode=disable"
    echo -e "${GREEN}数据库连接字符串: $DB_CONNECTION_STRING${NC}"
    
    export VECTOR_STORE_HOST="localhost"
    export VECTOR_STORE_PORT="19530"
    export VECTOR_STORE_COLLECTION="test_documents"
    export EMBEDDING_MODEL_URL="http://localhost:8000/embed"
    
    # 根据环境设置决定是否使用模拟向量存储
    if [ "$SKIP_VECTOR_TESTS" = true ]; then
        export VECTOR_STORE_USE_MOCK="true"
        echo -e "${YELLOW}使用模拟向量存储进行测试${NC}"
    else
        export VECTOR_STORE_USE_MOCK="false"
        echo -e "${YELLOW}尝试使用真实向量存储进行测试${NC}"
    fi
    
    # 打印环境变量，确认设置成功
    echo -e "${YELLOW}当前环境变量:${NC}"
    echo "DB_CONNECTION_STRING=$DB_CONNECTION_STRING"
    echo "VECTOR_STORE_USE_MOCK=$VECTOR_STORE_USE_MOCK"
}

# 运行单元测试
run_unit_tests() {
    echo -e "${YELLOW}运行单元测试...${NC}"
    cd "$PROJECT_ROOT"
    
    mkdir -p test-output
    
    if [ "$COVERAGE" = true ]; then
        go test -race -v -coverprofile=test-output/unit-coverage.out ./internal/domain/... ./pkg/...
    else
        go test -race -v ./internal/domain/... ./pkg/...
    fi
}

# 运行集成测试
run_integration_tests() {
    echo -e "${YELLOW}运行集成测试...${NC}"
    cd "$PROJECT_ROOT"
    
    mkdir -p test-output
    
    if [ "$COVERAGE" = true ]; then
        go test -race -v -coverprofile=test-output/integration-coverage.out ./internal/test/integration/...
    else
        go test -race -v ./internal/test/integration/...
    fi
}

# 运行端到端测试
run_e2e_tests() {
    echo -e "${YELLOW}运行端到端测试...${NC}"
    cd "$PROJECT_ROOT"
    
    mkdir -p test-output
    
    if [ "$COVERAGE" = true ]; then
        go test -race -v -coverprofile=test-output/e2e-coverage.out ./internal/test/e2e/...
    else
        go test -race -v ./internal/test/e2e/...
    fi
}

# 运行基准测试
run_benchmarks() {
    echo -e "${YELLOW}运行基准测试...${NC}"
    cd "$PROJECT_ROOT"
    
    mkdir -p benchmark_results
    
    # 运行文档存储库基准测试
    echo -e "${GREEN}运行文档存储库基准测试...${NC}"
    go test -bench=DocRepo ./internal/test/benchmark/real/ | tee benchmark_results/repository_bench.txt
    
    # 如果依赖于向量存储的测试
    echo -e "${GREEN}运行文档服务基准测试（使用模拟向量存储）...${NC}"
    VECTOR_STORE_USE_MOCK=true go test -bench=Real ./internal/test/benchmark/real/ | tee benchmark_results/service_bench.txt
}

# 生成覆盖率报告
generate_coverage_report() {
    echo -e "${YELLOW}生成测试覆盖率报告...${NC}"
    cd "$PROJECT_ROOT"
    
    # 合并覆盖率文件
    echo -e "${GREEN}合并覆盖率数据...${NC}"
    echo "mode: atomic" > test-output/coverage.out
    
    for profile in $(find test-output -name "*-coverage.out"); do
        tail -n +2 "$profile" >> test-output/coverage.out
    done
    
    # 生成HTML报告
    echo -e "${GREEN}生成HTML覆盖率报告...${NC}"
    go tool cover -html=test-output/coverage.out -o test-output/coverage.html
    
    # 显示覆盖率统计
    echo -e "${GREEN}覆盖率统计...${NC}"
    go tool cover -func=test-output/coverage.out
    
    echo -e "${GREEN}覆盖率报告已生成: test-output/coverage.html${NC}"
}

# 清理测试环境
cleanup() {
    echo -e "${YELLOW}是否要清理测试环境？ (y/n)${NC}"
    read -r answer
    if [ "$answer" != "${answer#[Yy]}" ]; then
        echo -e "${YELLOW}清理测试环境...${NC}"
        cd "$PROJECT_ROOT"
        
        # 停止容器
        docker-compose down
        
        echo -e "${GREEN}测试环境已清理${NC}"
    else
        echo -e "${GREEN}保留测试环境${NC}"
    fi
}

# 解析命令行参数
RUN_UNIT=false
RUN_INTEGRATION=false
RUN_E2E=false
RUN_BENCH=false
COVERAGE=false
CLEANUP=false
SKIP_VECTOR_TESTS=false

# 显示帮助信息
show_help() {
    echo "用法: $0 [options]"
    echo "选项:"
    echo "  -u  运行单元测试"
    echo "  -i  运行集成测试"
    echo "  -e  运行端到端测试"
    echo "  -b  运行基准测试"
    echo "  -c  生成测试覆盖率"
    echo "  -d  测试完成后清理环境"
    echo "  -a  运行所有测试"
    echo "  -s  跳过向量存储测试 (使用模拟实现)"
    echo "  -h  显示此帮助信息"
}

while getopts "uiebcdash" opt; do
  case $opt in
    u) RUN_UNIT=true ;;
    i) RUN_INTEGRATION=true ;;
    e) RUN_E2E=true ;;
    b) RUN_BENCH=true ;;
    c) COVERAGE=true ;;
    d) CLEANUP=true ;;
    a) RUN_UNIT=true; RUN_INTEGRATION=true; RUN_E2E=true; RUN_BENCH=true ;;
    s) SKIP_VECTOR_TESTS=true ;;
    h)
      show_help
      exit 0
      ;;
    \?) echo "无效选项: -$OPTARG" >&2; show_help; exit 1 ;;
  esac
done

# 如果没有指定任何选项，显示帮助
if [ "$RUN_UNIT" = false ] && [ "$RUN_INTEGRATION" = false ] && [ "$RUN_E2E" = false ] && [ "$RUN_BENCH" = false ]; then
    show_help
    exit 0
fi

# 主流程
echo -e "${GREEN}开始Docker测试流程${NC}"

# 启动测试环境
start_test_env

# 初始化测试数据库
init_test_db

# 运行测试
[ "$RUN_UNIT" = true ] && run_unit_tests
[ "$RUN_INTEGRATION" = true ] && run_integration_tests
[ "$RUN_E2E" = true ] && run_e2e_tests
[ "$RUN_BENCH" = true ] && run_benchmarks

# 生成覆盖率报告
[ "$COVERAGE" = true ] && generate_coverage_report

# 清理环境
[ "$CLEANUP" = true ] && cleanup

echo -e "${GREEN}测试完成!${NC}" 