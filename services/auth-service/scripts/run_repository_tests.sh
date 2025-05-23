#!/bin/bash
# 运行仓储模块测试脚本
# 包括用户仓储、令牌仓储等测试

set -e

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # 无颜色

# 脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 项目根目录
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 切换到项目根目录
cd "$PROJECT_ROOT"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}未找到虚拟环境，正在创建...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}虚拟环境创建成功${NC}"
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo -e "${YELLOW}安装测试依赖...${NC}"
pip install pytest pytest-asyncio pytest-cov pytest-mock pytest-freezegun setuptools pytest-asyncio sqlalchemy asyncpg redis

# 运行仓储模块测试
echo -e "${GREEN}开始运行仓储模块测试...${NC}"

# 创建结果目录
mkdir -p test/results

# 运行用户仓储测试
echo -e "${YELLOW}运行用户仓储模块测试...${NC}"
python -m pytest test/unit/repository/test_user_repository.py -v --cov=internal.repository.user_repository --cov-report=term --cov-report=html:test/results/user_repository_coverage || true

# 运行令牌仓储测试
echo -e "${YELLOW}运行令牌仓储模块测试...${NC}"
python -m pytest test/unit/repository/test_token_repository.py -v --cov=internal.repository.token_repository --cov-report=term --cov-report=html:test/results/token_repository_coverage || true

# 运行OAuth仓储测试
echo -e "${YELLOW}运行OAuth仓储模块测试...${NC}"
python -m pytest test/unit/repository/test_oauth_repository.py -v --cov=internal.repository.oauth_repository --cov-report=term --cov-report=html:test/results/oauth_repository_coverage || true

# 运行审计日志仓储测试
echo -e "${YELLOW}运行审计日志仓储模块测试...${NC}"
python -m pytest test/unit/repository/test_audit_repository.py -v --cov=internal.repository.audit_repository --cov-report=term --cov-report=html:test/results/audit_repository_coverage || true

# 运行所有仓储模块测试，生成总体覆盖率报告
echo -e "${YELLOW}生成仓储模块总体覆盖率报告...${NC}"
python -m pytest test/unit/repository/ -v --cov=internal.repository --cov-report=term --cov-report=html:test/results/repository_coverage || true

# 打印测试报告位置
echo -e "${GREEN}测试完成！${NC}"
echo -e "测试覆盖率报告位于: ${PROJECT_ROOT}/test/results/"

# 退出虚拟环境
deactivate 