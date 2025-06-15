#!/bin/bash
# 测试数据库初始化脚本

set -e

echo "初始化测试数据库..."

# 加载环境变量
if [ -f "test/.env.test" ]; then
    export $(grep -v '^#' test/.env.test | xargs)
fi

# 等待PostgreSQL就绪
echo "等待PostgreSQL就绪..."
until PGPASSWORD=$TEST_DB_PASSWORD psql -h $TEST_DB_HOST -p $TEST_DB_PORT -U $TEST_DB_USER -d $TEST_DB_NAME -c '\q'; do
  echo "PostgreSQL还未就绪 - 等待..."
  sleep 2
done

echo "PostgreSQL就绪，初始化表结构..."

# 创建表结构和初始数据
PGPASSWORD=$TEST_DB_PASSWORD psql -h $TEST_DB_HOST -p $TEST_DB_PORT -U $TEST_DB_USER -d $TEST_DB_NAME << EOL
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
