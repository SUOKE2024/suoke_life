#!/bin/bash
# 运行基本测试脚本
# 只运行不需要数据库连接的安全模块测试

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
echo -e "${CYAN}                  运行基本安全模块测试                            ${NC}"
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

# 加载测试环境变量
if [ -f "test/.env.test" ]; then
    echo -e "${YELLOW}加载测试环境配置...${NC}"
    set -a
    source test/.env.test
    set +a
else
    echo -e "${YELLOW}未找到测试环境配置文件，使用默认配置...${NC}"
    export TEST_JWT_SECRET="test_jwt_secret_for_testing_only"
    export JWT_SECRET_KEY="test_jwt_secret_for_testing_only"
    export JWT_ALGORITHM="HS256"
    export ACCESS_TOKEN_EXPIRE_MINUTES="30"
    export REFRESH_TOKEN_EXPIRE_MINUTES="10080"
fi

# 创建结果目录
mkdir -p test/results/security_coverage

# 运行JWT安全测试
echo -e "${YELLOW}运行JWT安全模块测试...${NC}"
python -m pytest test/unit/security/test_jwt.py -v --cov=internal.security.jwt --cov-report=term --cov-report=html:test/results/security_coverage/jwt || true

# 运行密码安全测试
echo -e "${YELLOW}运行密码安全模块测试...${NC}"
python -m pytest test/unit/security/test_password.py -v --cov=internal.security.password --cov-report=term --cov-report=html:test/results/security_coverage/password || true

# 运行MFA安全测试
echo -e "${YELLOW}运行MFA安全模块测试...${NC}"
python -m pytest test/unit/security/test_mfa.py -v --cov=internal.security.mfa --cov-report=term --cov-report=html:test/results/security_coverage/mfa || true

# 生成安全模块整体覆盖率报告
echo -e "${YELLOW}生成安全模块整体覆盖率报告...${NC}"
python -m pytest test/unit/security/ -v --cov=internal.security --cov-report=term --cov-report=html:test/results/security_coverage/combined || true

# 计算测试运行时间
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

echo -e "\n${CYAN}==================================================================${NC}"
echo -e "${CYAN}                         测试完成                                 ${NC}"
echo -e "${CYAN}==================================================================${NC}"
echo -e "测试运行时间: ${YELLOW}$MINUTES 分 $SECONDS 秒${NC}"
echo -e "测试覆盖率报告位于: ${PROJECT_ROOT}/test/results/security_coverage/combined/index.html"

# 退出虚拟环境
deactivate 