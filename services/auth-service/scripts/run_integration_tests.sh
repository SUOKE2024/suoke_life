#!/bin/bash
# 运行集成测试脚本
# 这些测试需要外部依赖如数据库和Redis

set -e

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # 无颜色

# 脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 项目根目录
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 切换到项目根目录
cd "$PROJECT_ROOT"

# 显示标题
echo -e "${CYAN}==================================================================${NC}"
echo -e "${CYAN}            索克生活认证服务 (Auth Service) 集成测试              ${NC}"
echo -e "${CYAN}==================================================================${NC}"

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
pip install pytest pytest-asyncio pytest-cov pytest-mock pytest-freezegun setuptools pyjwt grpcio asyncpg redis pyotp passlib cryptography pillow sqlalchemy pytest-dotenv qrcode argon2_cffi

# 创建结果目录
mkdir -p test/results/integration

# 检查测试环境是否准备好（数据库、Redis等）
echo -e "${YELLOW}检查测试环境...${NC}"

# 检查环境变量文件是否存在
if [ -f "test/.env.test" ]; then
    echo -e "${YELLOW}加载测试环境变量...${NC}"
    source test/.env.test
else
    echo -e "${YELLOW}未找到环境变量文件，将尝试设置测试环境...${NC}"
    ./scripts/setup_test_environment.sh
    source test/.env.test
fi

# 检查PostgreSQL连接
echo -e "${YELLOW}检查PostgreSQL连接...${NC}"
if pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; then
    echo -e "${GREEN}PostgreSQL连接正常${NC}"
else
    echo -e "${RED}PostgreSQL连接失败，请检查数据库是否启动或环境变量是否正确设置${NC}"
    echo -e "${YELLOW}您可以使用以下命令启动测试环境:${NC}"
    echo -e "  ./scripts/setup_test_environment.sh"
    exit 1
fi

# 检查Redis连接
echo -e "${YELLOW}检查Redis连接...${NC}"
if redis-cli -h $REDIS_HOST -p $REDIS_PORT ping | grep -q "PONG"; then
    echo -e "${GREEN}Redis连接正常${NC}"
else
    echo -e "${RED}Redis连接失败，请检查Redis是否启动或环境变量是否正确设置${NC}"
    echo -e "${YELLOW}您可以使用以下命令启动测试环境:${NC}"
    echo -e "  ./scripts/setup_test_environment.sh"
    exit 1
fi

# 运行测试前的准备工作（如创建测试数据库架构）
echo -e "${YELLOW}准备测试数据库...${NC}"
python -m pytest test/integration/setup.py -v

# 运行集成测试
echo -e "\n${CYAN}==================================================================${NC}"
echo -e "${CYAN}                       运行仓储层集成测试                         ${NC}"
echo -e "${CYAN}==================================================================${NC}"
python -m pytest test/integration/repository/ -v --cov=internal.repository --cov-report=term --cov-report=html:test/results/integration/repository_coverage || true

echo -e "\n${CYAN}==================================================================${NC}"
echo -e "${CYAN}                       运行服务层集成测试                         ${NC}"
echo -e "${CYAN}==================================================================${NC}"
python -m pytest test/integration/service/ -v --cov=internal.service --cov-report=term --cov-report=html:test/results/integration/service_coverage || true

echo -e "\n${CYAN}==================================================================${NC}"
echo -e "${CYAN}                       运行交付层集成测试                         ${NC}"
echo -e "${CYAN}==================================================================${NC}"
python -m pytest test/integration/delivery/ -v --cov=internal.delivery --cov-report=term --cov-report=html:test/results/integration/delivery_coverage || true

# 生成整体集成测试覆盖率报告
echo -e "\n${CYAN}==================================================================${NC}"
echo -e "${CYAN}                       生成整体集成测试覆盖率报告                 ${NC}"
echo -e "${CYAN}==================================================================${NC}"
python -m pytest test/integration/ -v --cov=internal --cov-report=term --cov-report=html:test/results/integration/all_coverage || true

# 清理测试数据
echo -e "${YELLOW}清理测试数据...${NC}"
python -m pytest test/integration/cleanup.py -v

# 打印测试报告位置
echo -e "\n${GREEN}集成测试完成！${NC}"
echo -e "测试覆盖率报告位于: ${PROJECT_ROOT}/test/results/integration/"
echo -e "整体覆盖率报告: ${PROJECT_ROOT}/test/results/integration/all_coverage/index.html"

# 退出虚拟环境
deactivate 