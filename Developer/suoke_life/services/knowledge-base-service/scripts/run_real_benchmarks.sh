#!/bin/bash

# 实际环境基准测试脚本
# 该脚本用于启动测试环境并运行实际数据库和向量存储的基准测试

set -e

# 脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 项目根目录
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 确保 docker-compose 存在
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}错误: 找不到 docker-compose 命令${NC}"
    echo "请先安装 Docker 和 docker-compose"
    exit 1
fi

# 检查测试环境
check_test_env() {
    echo -e "${YELLOW}检查测试环境...${NC}"
    cd "$PROJECT_ROOT"
    
    # 检查是否已有测试环境运行
    if docker-compose ps | grep -q "Up"; then
        echo -e "${GREEN}测试环境已经在运行中${NC}"
        return 0
    else
        echo -e "${RED}测试环境未运行，请先启动测试环境${NC}"
        echo "可以使用命令: docker-compose up -d"
        return 1
    fi
}

# 运行基准测试
run_benchmarks() {
    echo -e "${YELLOW}运行实际环境基准测试...${NC}"
    cd "$PROJECT_ROOT"
    
    # 设置环境变量 - 更新为与实际容器配置一致
    export DB_CONNECTION_STRING="postgresql://postgres:postgres@localhost:5432/knowledge_base?sslmode=disable"
    export VECTOR_STORE_HOST="localhost"
    export VECTOR_STORE_PORT="19530"
    export VECTOR_STORE_COLLECTION="test_documents"
    export EMBEDDING_MODEL_URL="http://localhost:8000/embed"
    
    # 创建输出目录
    mkdir -p benchmark_results
    
    # 运行基准测试
    echo -e "${GREEN}运行文档存储库基准测试...${NC}"
    go test -v -bench=DocRepo ./internal/test/benchmark/real/ | tee benchmark_results/repository_bench.txt
    
    echo -e "${GREEN}运行向量存储基准测试...${NC}"
    go test -v -bench=VectorStore ./internal/test/benchmark/real/ | tee benchmark_results/vectorstore_bench.txt
    
    echo -e "${GREEN}运行文档服务基准测试...${NC}"
    go test -v -bench=Real ./internal/test/benchmark/real/ | tee benchmark_results/service_bench.txt
    
    echo -e "${GREEN}所有基准测试结果已保存到 benchmark_results 目录${NC}"
}

# 主流程
echo -e "${GREEN}开始运行实际环境基准测试${NC}"

# 检查测试环境
if ! check_test_env; then
    exit 1
fi

# 运行基准测试
run_benchmarks

echo -e "${GREEN}基准测试完成${NC}"

exit 0