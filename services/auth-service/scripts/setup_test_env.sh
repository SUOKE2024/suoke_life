#!/bin/bash
# 测试环境设置脚本
# 用于准备集成测试所需的环境

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # 无颜色

# 项目根目录
PROJECT_ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$PROJECT_ROOT" || exit 1

echo -e "${GREEN}开始设置测试环境...${NC}"

# 检查Docker是否可用
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: 未找到docker命令，请确保Docker已安装${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}错误: 未找到docker-compose命令，请确保已安装${NC}"
    exit 1
fi

# 检查测试目录
if [ ! -d "test" ]; then
    echo -e "${RED}错误: 未找到test目录${NC}"
    exit 1
fi

# 确保test/tmp目录存在
mkdir -p test/tmp

# 生成测试环境配置文件
cat > test/.env.test << EOF
# 测试环境配置
ENVIRONMENT=test

# 数据库配置
TEST_DB_HOST=localhost
TEST_DB_PORT=5433
TEST_DB_NAME=auth_test
TEST_DB_USER=postgres
TEST_DB_PASSWORD=postgres

# Redis配置
TEST_REDIS_HOST=localhost
TEST_REDIS_PORT=6380
TEST_REDIS_DB=1

# 服务配置
TEST_SERVER_HOST=localhost
TEST_SERVER_HTTP_PORT=8081
TEST_SERVER_GRPC_PORT=50052

# JWT配置
JWT_SECRET_KEY=test_jwt_secret_for_testing_only
JWT_ALGORITHM=HS256

# 日志配置
LOG_LEVEL=DEBUG
EOF

echo -e "${GREEN}已生成测试环境配置文件: test/.env.test${NC}"

# 生成测试用的docker-compose文件
cat > test/docker-compose.test.yml << EOF
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: auth_test_postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: auth_test
    ports:
      - "5433:5432"
    volumes:
      - auth_test_postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: auth_test_redis
    ports:
      - "6380:6379"
    volumes:
      - auth_test_redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  auth_test_postgres_data:
  auth_test_redis_data:
EOF

echo -e "${GREEN}已生成测试Docker Compose配置: test/docker-compose.test.yml${NC}"

# 生成初始化数据库脚本
cat > test/init_test_db.sh << EOF
#!/bin/bash
# 测试数据库初始化脚本

set -e

echo "初始化测试数据库..."

# 加载环境变量
if [ -f "test/.env.test" ]; then
    export \$(grep -v '^#' test/.env.test | xargs)
fi

# 等待PostgreSQL就绪
echo "等待PostgreSQL就绪..."
until PGPASSWORD=\$TEST_DB_PASSWORD psql -h \$TEST_DB_HOST -p \$TEST_DB_PORT -U \$TEST_DB_USER -d \$TEST_DB_NAME -c '\q'; do
  echo "PostgreSQL还未就绪 - 等待..."
  sleep 2
done

echo "PostgreSQL就绪，初始化表结构..."

# 创建表结构和初始数据
PGPASSWORD=\$TEST_DB_PASSWORD psql -h \$TEST_DB_HOST -p \$TEST_DB_PORT -U \$TEST_DB_USER -d \$TEST_DB_NAME << EOL
-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20) UNIQUE,
    profile_data JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    is_locked BOOLEAN DEFAULT FALSE,
    failed_login_attempts INT DEFAULT 0,
    lock_until TIMESTAMP,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_type VARCHAR(10),
    mfa_secret VARCHAR(100),
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    last_login_at TIMESTAMP
);

-- 角色表
CREATE TABLE IF NOT EXISTS roles (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- 权限表
CREATE TABLE IF NOT EXISTS permissions (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- 用户角色关联表
CREATE TABLE IF NOT EXISTS user_roles (
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE,
    role_id VARCHAR(36) REFERENCES roles(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, role_id)
);

-- 角色权限关联表
CREATE TABLE IF NOT EXISTS role_permissions (
    role_id VARCHAR(36) REFERENCES roles(id) ON DELETE CASCADE,
    permission_id VARCHAR(36) REFERENCES permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (role_id, permission_id)
);

-- 用户资源权限表(用于特定资源的访问控制)
CREATE TABLE IF NOT EXISTS user_resource_permissions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE,
    resource_id VARCHAR(36) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    permission VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, resource_id, permission)
);

-- 审计日志表
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(36),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(100),
    ip_address VARCHAR(45),
    user_agent TEXT,
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- OAuth连接表
CREATE TABLE IF NOT EXISTS oauth_connections (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(20) NOT NULL,
    provider_user_id VARCHAR(100) NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    expires_at TIMESTAMP,
    scopes TEXT[],
    user_data JSONB,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    UNIQUE (provider, provider_user_id)
);

-- 插入默认角色
INSERT INTO roles (id, name, description, created_at, updated_at)
VALUES
    ('1', 'admin', '系统管理员，拥有所有权限', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('2', 'user', '普通用户', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('3', 'guest', '访客用户，仅有只读权限', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
    
-- 插入默认权限
INSERT INTO permissions (id, name, description, created_at, updated_at)
VALUES
    ('1', 'user:read', '查看用户信息', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('2', 'user:create', '创建用户', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('3', 'user:update', '更新用户信息', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('4', 'user:delete', '删除用户', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('5', 'role:read', '查看角色', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('6', 'role:create', '创建角色', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('7', 'role:update', '更新角色', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('8', 'role:delete', '删除角色', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('9', 'permission:read', '查看权限', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('10', 'permission:assign', '分配权限', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
    
-- 分配权限给角色
-- 管理员角色拥有所有权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT '1', id FROM permissions;

-- 普通用户角色拥有查看用户和自身信息的权限
INSERT INTO role_permissions (role_id, permission_id)
VALUES
    ('2', '1'),  -- user:read
    ('3', '1');  -- guest也有user:read权限
EOL

echo "测试数据库初始化完成"
EOF

chmod +x test/init_test_db.sh
echo -e "${GREEN}已生成数据库初始化脚本: test/init_test_db.sh${NC}"

# 生成启动测试环境的脚本
cat > test/start_test_env.sh << EOF
#!/bin/bash
# 启动测试环境

set -e

echo "启动测试环境..."

# 检查docker-compose配置文件是否存在
if [ ! -f "test/docker-compose.test.yml" ]; then
    echo "错误: 未找到docker-compose配置文件"
    exit 1
fi

# 关闭可能正在运行的容器
echo "关闭旧的测试容器..."
docker-compose -f test/docker-compose.test.yml down || true

# 启动测试服务
echo "启动测试服务..."
docker-compose -f test/docker-compose.test.yml up -d

# 等待服务就绪
echo "等待服务就绪..."
sleep 5

# 初始化测试数据库
echo "初始化测试数据库..."
./test/init_test_db.sh

echo "测试环境已准备完毕!"
echo "PostgreSQL: localhost:5433"
echo "Redis: localhost:6380"
EOF

chmod +x test/start_test_env.sh
echo -e "${GREEN}已生成测试环境启动脚本: test/start_test_env.sh${NC}"

# 生成停止测试环境的脚本
cat > test/stop_test_env.sh << EOF
#!/bin/bash
# 停止测试环境

echo "停止测试环境..."

# 检查docker-compose配置文件是否存在
if [ ! -f "test/docker-compose.test.yml" ]; then
    echo "错误: 未找到docker-compose配置文件"
    exit 1
fi

# 关闭容器
docker-compose -f test/docker-compose.test.yml down

echo "测试环境已停止"
EOF

chmod +x test/stop_test_env.sh
echo -e "${GREEN}已生成测试环境停止脚本: test/stop_test_env.sh${NC}"

echo -e "${GREEN}测试环境设置完成!${NC}"
echo -e "${YELLOW}使用以下命令启动测试环境:${NC}"
echo -e "${YELLOW}  ./test/start_test_env.sh${NC}"
echo -e "${YELLOW}使用以下命令运行测试:${NC}"
echo -e "${YELLOW}  python3 scripts/run_tests.py unit    # 运行单元测试${NC}"
echo -e "${YELLOW}  python3 scripts/run_tests.py integration    # 运行集成测试${NC}"
echo -e "${YELLOW}使用以下命令停止测试环境:${NC}"
echo -e "${YELLOW}  ./test/stop_test_env.sh${NC}"

# 集成测试环境变量设置脚本

# 测试数据库配置
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=auth_test_db
export DB_USER=postgres
export DB_PASSWORD=postgres

# 测试Redis配置
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_DB=1

# JWT测试配置
export JWT_SECRET=test_secret_key
export JWT_ACCESS_EXPIRES=3600
export JWT_REFRESH_EXPIRES=86400

# MFA测试配置
export MFA_ISSUER=suoke_test
export MFA_SECRET_KEY=test_mfa_secret

# 服务配置
export SERVICE_PORT=8001
export SERVICE_HOST=0.0.0.0

echo "测试环境变量已设置" 