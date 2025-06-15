#!/bin/bash
# 运行安全模块测试脚本
# 包括JWT, MFA 和密码哈希等模块的测试

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
echo -e "${CYAN}                       安全模块测试                                ${NC}"
echo -e "${CYAN}==================================================================${NC}"

# 安装所有依赖
echo -e "${YELLOW}安装测试依赖...${NC}"
pip install pytest pytest-asyncio pytest-cov pytest-mock pytest-freezegun setuptools \
pyjwt grpcio asyncpg redis pyotp passlib cryptography pillow qrcode argon2_cffi

# 创建结果目录
mkdir -p test/results/security_coverage

# 加载测试环境变量
if [ -f "test/.env.test" ]; then
    echo -e "${YELLOW}加载测试环境配置...${NC}"
    # 导出环境变量而不输出它们
    set -a
    source test/.env.test
    set +a
else
    echo -e "${YELLOW}未找到测试环境配置文件，使用默认配置...${NC}"
    export TEST_JWT_SECRET="test_jwt_secret_for_testing_only"
    export TEST_JWT_ALGORITHM="HS256"
fi

# 开始运行测试
echo -e "${GREEN}开始运行安全模块测试...${NC}"

# 运行JWT测试
echo -e "${YELLOW}运行JWT安全模块测试...${NC}"
python -m pytest test/unit/security/test_jwt.py -v --cov=internal.security.jwt --cov-report=term --cov-report=html:test/results/security_coverage/jwt --timeout=60 || true

# 运行密码测试
echo -e "${YELLOW}运行密码安全模块测试...${NC}"
python -m pytest test/unit/security/test_password.py -v --cov=internal.security.password --cov-report=term --cov-report=html:test/results/security_coverage/password --timeout=60 || true

# 运行MFA测试
echo -e "${YELLOW}运行MFA安全模块测试...${NC}"
python -m pytest test/unit/security/test_mfa.py -v --cov=internal.security.mfa --cov-report=term --cov-report=html:test/results/security_coverage/mfa --timeout=60 || true

# 生成合并的覆盖率报告
echo -e "${YELLOW}生成安全模块覆盖率报告...${NC}"
python -m pytest test/unit/security/ -v --cov=internal.security --cov-report=term --cov-report=html:test/results/security_coverage/combined --timeout=60 || true

echo -e "${GREEN}安全模块测试完成！${NC}"
echo -e "测试覆盖率报告位于: ${PROJECT_ROOT}/test/results/security_coverage/" 