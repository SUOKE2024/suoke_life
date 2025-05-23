#!/bin/bash
# 测试环境设置脚本，启动PostgreSQL和Redis容器

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

# 测试环境配置
DB_HOST=localhost
DB_PORT=5433  # 使用非标准端口避免与系统PostgreSQL冲突
DB_NAME=auth_test_db
DB_USER=postgres
DB_PASSWORD=postgres

REDIS_HOST=localhost
REDIS_PORT=6380  # 使用非标准端口避免与系统Redis冲突
REDIS_DB=1

# 显示欢迎信息
echo -e "${CYAN}==================================================================${NC}"
echo -e "${CYAN}           索克生活认证服务测试环境配置                           ${NC}"
echo -e "${CYAN}==================================================================${NC}"

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker未安装，请先安装Docker${NC}"
    exit 1
fi

# 启动PostgreSQL容器
echo -e "${YELLOW}启动PostgreSQL测试容器...${NC}"
if [ "$(docker ps -q -f name=auth-test-postgres)" ]; then
    echo -e "${GREEN}PostgreSQL测试容器已经在运行${NC}"
else
    if [ "$(docker ps -aq -f status=exited -f name=auth-test-postgres)" ]; then
        echo -e "${YELLOW}启动已存在的PostgreSQL测试容器...${NC}"
        docker start auth-test-postgres
    else
        echo -e "${YELLOW}创建新的PostgreSQL测试容器...${NC}"
        docker run --name auth-test-postgres \
            -e POSTGRES_USER=$DB_USER \
            -e POSTGRES_PASSWORD=$DB_PASSWORD \
            -e POSTGRES_DB=$DB_NAME \
            -p $DB_PORT:5432 \
            -d postgres:13
    fi
fi

# 启动Redis容器
echo -e "${YELLOW}启动Redis测试容器...${NC}"
if [ "$(docker ps -q -f name=auth-test-redis)" ]; then
    echo -e "${GREEN}Redis测试容器已经在运行${NC}"
else
    if [ "$(docker ps -aq -f status=exited -f name=auth-test-redis)" ]; then
        echo -e "${YELLOW}启动已存在的Redis测试容器...${NC}"
        docker start auth-test-redis
    else
        echo -e "${YELLOW}创建新的Redis测试容器...${NC}"
        docker run --name auth-test-redis \
            -p $REDIS_PORT:6379 \
            -d redis:6
    fi
fi

# 等待PostgreSQL容器启动完成
echo -e "${YELLOW}等待PostgreSQL容器启动完成...${NC}"
sleep 5
MAX_RETRY=30
RETRY=0
while ! docker exec auth-test-postgres pg_isready -h localhost -U $DB_USER > /dev/null 2>&1; do
    RETRY=$((RETRY+1))
    if [ $RETRY -ge $MAX_RETRY ]; then
        echo -e "${RED}PostgreSQL容器启动超时!${NC}"
        exit 1
    fi
    echo -e "${YELLOW}PostgreSQL容器正在启动，等待中...${NC}"
    sleep 1
done

echo -e "${GREEN}PostgreSQL容器已就绪!${NC}"

# 等待Redis容器启动完成
echo -e "${YELLOW}等待Redis容器启动完成...${NC}"
sleep 2
MAX_RETRY=15
RETRY=0
while ! docker exec auth-test-redis redis-cli ping > /dev/null 2>&1; do
    RETRY=$((RETRY+1))
    if [ $RETRY -ge $MAX_RETRY ]; then
        echo -e "${RED}Redis容器启动超时!${NC}"
        exit 1
    fi
    echo -e "${YELLOW}Redis容器正在启动，等待中...${NC}"
    sleep 1
done

echo -e "${GREEN}Redis容器已就绪!${NC}"

# 创建环境变量文件
echo -e "${YELLOW}创建测试环境变量文件...${NC}"
cat > "$PROJECT_ROOT/test/.env.test" << EOF
# 测试数据库配置
DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD

# 测试Redis配置
REDIS_HOST=$REDIS_HOST
REDIS_PORT=$REDIS_PORT
REDIS_DB=$REDIS_DB

# JWT测试配置
JWT_SECRET=test_secret_key
JWT_ACCESS_EXPIRES=3600
JWT_REFRESH_EXPIRES=86400

# MFA测试配置
MFA_ISSUER=suoke_test
MFA_SECRET_KEY=test_mfa_secret

# 服务配置
SERVICE_PORT=8001
SERVICE_HOST=0.0.0.0
EOF

echo -e "${GREEN}测试环境变量文件已创建: ${PROJECT_ROOT}/test/.env.test${NC}"

# 创建测试环境停止脚本
echo -e "${YELLOW}创建测试环境停止脚本...${NC}"
cat > "$PROJECT_ROOT/test/stop_test_env.sh" << EOF
#!/bin/bash
# 停止测试环境

docker stop auth-test-postgres
docker stop auth-test-redis

echo "测试环境已停止"
EOF
chmod +x "$PROJECT_ROOT/test/stop_test_env.sh"

echo -e "${GREEN}测试环境停止脚本已创建: ${PROJECT_ROOT}/test/stop_test_env.sh${NC}"

# 打印测试环境信息
echo -e "\n${CYAN}==================================================================${NC}"
echo -e "${CYAN}                  测试环境已成功启动!                           ${NC}"
echo -e "${CYAN}==================================================================${NC}"
echo -e "${GREEN}PostgreSQL:${NC} $DB_HOST:$DB_PORT/$DB_NAME ($DB_USER/$DB_PASSWORD)"
echo -e "${GREEN}Redis:${NC} $REDIS_HOST:$REDIS_PORT"
echo -e "\n${YELLOW}使用以下命令运行测试:${NC}"
echo -e "${YELLOW}  source $PROJECT_ROOT/test/.env.test && ./scripts/run_integration_tests.sh${NC}"
echo -e "${YELLOW}使用以下命令停止测试环境:${NC}"
echo -e "${YELLOW}  ./test/stop_test_env.sh${NC}" 