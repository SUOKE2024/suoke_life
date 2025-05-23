#!/bin/bash
# 运行所有测试脚本
# 包括安全模块测试和仓储模块测试等

set -e

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 项目根目录
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 切换到项目根目录
cd "$PROJECT_ROOT"

# 显示标题
echo -e "${CYAN}==================================================================${NC}"
echo -e "${CYAN}              索克生活认证服务 (Auth Service) 测试               ${NC}"
echo -e "${CYAN}==================================================================${NC}"

# 测试启动时间
START_TIME=$(date +%s)

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}未找到虚拟环境，正在创建...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}虚拟环境创建成功${NC}"
fi

# 激活虚拟环境
source venv/bin/activate

# 安装所有依赖
echo -e "${YELLOW}安装测试依赖...${NC}"
pip install pytest pytest-asyncio pytest-cov pytest-mock pytest-freezegun pytest-timeout pytest-env setuptools \
pyjwt grpcio asyncpg redis pyotp passlib cryptography pillow sqlalchemy qrcode argon2_cffi \
fastapi aiohttp psutil uvicorn starlette httpx pydantic tenacity pytest-xdist python-dotenv \
prometheus_client opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation \
structlog packaging typing-extensions email-validator

# 确保测试结果目录存在
mkdir -p test/results/all_coverage
mkdir -p test/results/security_coverage
mkdir -p test/results/repository_coverage
mkdir -p test/results/service_coverage
mkdir -p test/results/delivery_coverage
mkdir -p test/results/observability_coverage
mkdir -p test/results/integration

# 加载测试环境变量
if [ -f "test/.env.test" ]; then
    echo -e "${YELLOW}加载测试环境配置...${NC}"
    # 导出环境变量而不输出它们
    set -a
    source test/.env.test
    set +a
else
    echo -e "${YELLOW}未找到测试环境配置文件，使用默认配置...${NC}"
    # 设置默认测试环境变量
    export TEST_DB_HOST=localhost
    export TEST_DB_PORT=5432
    export TEST_DB_NAME=auth_test
    export TEST_DB_USER=postgres
    export TEST_DB_PASSWORD=postgres
    export TEST_REDIS_HOST=localhost
    export TEST_REDIS_PORT=6379
    export TEST_REDIS_DB=1
    export TEST_JWT_SECRET=test_jwt_secret_for_testing_only
    export TEST_JWT_ALGORITHM=HS256
fi

# 统计变量
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 运行安全模块测试
echo -e "\n${CYAN}==================================================================${NC}"
echo -e "${CYAN}                       运行安全模块测试                           ${NC}"
echo -e "${CYAN}==================================================================${NC}"
if "$SCRIPT_DIR/run_security_tests.sh"; then
    SECURITY_TESTS_RESULT=$?
    if [ $SECURITY_TESTS_RESULT -eq 0 ]; then
        echo -e "${GREEN}安全模块测试通过！${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}安全模块测试失败 (退出码: $SECURITY_TESTS_RESULT)${NC}"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
fi

# 运行仓储层测试
echo -e "\n${CYAN}==================================================================${NC}"
echo -e "${CYAN}                       运行仓储层测试                             ${NC}"
echo -e "${CYAN}==================================================================${NC}"
if "$SCRIPT_DIR/run_repository_tests.sh"; then
    REPO_TESTS_RESULT=$?
    if [ $REPO_TESTS_RESULT -eq 0 ]; then
        echo -e "${GREEN}仓储层测试通过！${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}仓储层测试失败 (退出码: $REPO_TESTS_RESULT)${NC}"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
fi

# 运行服务层测试（如果存在）
if [ -d "test/unit/service" ]; then
    echo -e "\n${CYAN}==================================================================${NC}"
    echo -e "${CYAN}                       运行服务层测试                           ${NC}"
    echo -e "${CYAN}==================================================================${NC}"
    
    if python -m pytest test/unit/service/ -v --cov=internal.service --cov-report=term --cov-report=html:test/results/service_coverage --timeout=60; then
        echo -e "${GREEN}服务层测试通过！${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}服务层测试失败${NC}"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
fi

# 运行可观测性层测试（如果存在）
if [ -d "test/unit/observability" ]; then
    echo -e "\n${CYAN}==================================================================${NC}"
    echo -e "${CYAN}                       运行可观测性层测试                       ${NC}"
    echo -e "${CYAN}==================================================================${NC}"
    
    if python -m pytest test/unit/observability/ -v --cov=internal.observability --cov-report=term --cov-report=html:test/results/observability_coverage --timeout=60; then
        echo -e "${GREEN}可观测性层测试通过！${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}可观测性层测试失败${NC}"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
fi

# 运行交付层测试（如果存在）
if [ -d "test/unit/delivery" ]; then
    echo -e "\n${CYAN}==================================================================${NC}"
    echo -e "${CYAN}                       运行交付层测试                           ${NC}"
    echo -e "${CYAN}==================================================================${NC}"
    
    if python -m pytest test/unit/delivery/ -v --cov=internal.delivery --cov-report=term --cov-report=html:test/results/delivery_coverage --timeout=60; then
        echo -e "${GREEN}交付层测试通过！${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}交付层测试失败${NC}"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
fi

# 生成整体覆盖率报告
echo -e "\n${CYAN}==================================================================${NC}"
echo -e "${CYAN}                       生成整体覆盖率报告                         ${NC}"
echo -e "${CYAN}==================================================================${NC}"

python -m pytest test/unit/ -v --cov=internal --cov-report=term --cov-report=html:test/results/all_coverage --timeout=120 || true

# 计算测试运行时间
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

# 打印测试报告位置
echo -e "\n${CYAN}==================================================================${NC}"
echo -e "${CYAN}                           测试结果摘要                           ${NC}"
echo -e "${CYAN}==================================================================${NC}"
echo -e "总测试模块数: ${BLUE}$TOTAL_TESTS${NC}"
echo -e "通过模块数: ${GREEN}$PASSED_TESTS${NC}"
echo -e "失败模块数: ${RED}$FAILED_TESTS${NC}"
echo -e "测试运行时间: ${BLUE}$MINUTES 分 $SECONDS 秒${NC}"
echo -e "\n测试覆盖率报告位于: ${PROJECT_ROOT}/test/results/"
echo -e "整体覆盖率报告: ${PROJECT_ROOT}/test/results/all_coverage/index.html"

# 检查是否有测试失败
if [ $FAILED_TESTS -gt 0 ]; then
    echo -e "\n${RED}警告: 有 $FAILED_TESTS 个测试模块失败${NC}"
    echo -e "请查看测试日志获取详细信息"
else
    echo -e "\n${GREEN}所有测试模块都通过了！${NC}"
fi

# 退出虚拟环境
deactivate 

# 如果有测试失败，返回非零退出码
if [ $FAILED_TESTS -gt 0 ]; then
    exit 1
fi 