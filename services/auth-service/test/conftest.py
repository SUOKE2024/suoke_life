#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试配置文件
设置测试环境和共用测试夹具
"""
import os
import uuid
import asyncio
import pytest
import asyncpg
import redis
import sys
from typing import Dict, Any, Optional

# 添加mock模块路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "mocks")))

# Mock OpenTelemetry模块
sys.modules["opentelemetry.instrumentation.fastapi"] = __import__("opentelemetry.instrumentation.fastapi", fromlist=[""])
sys.modules["opentelemetry.instrumentation.redis"] = __import__("opentelemetry.instrumentation.redis", fromlist=[""])
sys.modules["opentelemetry.instrumentation.sqlalchemy"] = __import__("opentelemetry.instrumentation.sqlalchemy", fromlist=[""])

# 测试环境配置
TEST_DB_HOST = os.getenv("TEST_DB_HOST", "localhost")
TEST_DB_PORT = int(os.getenv("TEST_DB_PORT", "5432"))
TEST_DB_NAME = os.getenv("TEST_DB_NAME", "auth_test")
TEST_DB_USER = os.getenv("TEST_DB_USER", "postgres")
TEST_DB_PASSWORD = os.getenv("TEST_DB_PASSWORD", "postgres")

TEST_REDIS_HOST = os.getenv("TEST_REDIS_HOST", "localhost")
TEST_REDIS_PORT = int(os.getenv("TEST_REDIS_PORT", "6379"))
TEST_REDIS_DB = int(os.getenv("TEST_REDIS_DB", "1"))  # 使用不同的数据库，避免影响开发环境

# JWT配置
TEST_JWT_SECRET = "test_jwt_secret_for_testing_only"
TEST_JWT_ALGORITHM = "HS256"

# 注意：pytest-asyncio > 0.14.0 不再需要重写event_loop fixture
# asyncio模式已在pytest.ini中设置为"strict"

@pytest.fixture
async def pg_pool():
    """创建异步PostgreSQL连接池"""
    dsn = f"postgresql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"
    try:
        pool = await asyncpg.create_pool(dsn=dsn)
        yield pool
    finally:
        if 'pool' in locals():
            await pool.close()


@pytest.fixture
def redis_client():
    """创建Redis客户端"""
    client = redis.Redis(
        host=TEST_REDIS_HOST,
        port=TEST_REDIS_PORT,
        db=TEST_REDIS_DB,
        decode_responses=True  # 自动将字节解码为字符串
    )
    try:
        yield client
    finally:
        client.close()


@pytest.fixture
def test_user_data() -> Dict[str, Any]:
    """生成测试用户数据"""
    return {
        "id": str(uuid.uuid4()),
        "username": f"testuser_{uuid.uuid4().hex[:8]}",
        "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
        "password": "Test@123456",
        "phone_number": "13800138000",
    }


@pytest.fixture
def test_token_data() -> Dict[str, Any]:
    """生成测试令牌数据"""
    return {
        "sub": str(uuid.uuid4()),
        "username": "testuser",
        "email": "test@example.com",
        "roles": ["user"],
        "iat": 1630000000,
        "exp": 1630086400
    }


@pytest.fixture(scope="session")
async def db_pool():
    """创建数据库连接池"""
    # 构建连接字符串
    dsn = f"postgresql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"
    
    # 创建连接池
    pool = await asyncpg.create_pool(dsn=dsn, min_size=3, max_size=10)
    
    # 初始化测试数据库
    async with pool.acquire() as conn:
        # 清理现有表（如果存在）
        await conn.execute("""
        DROP TABLE IF EXISTS user_resource_permissions CASCADE;
        DROP TABLE IF EXISTS role_permissions CASCADE;
        DROP TABLE IF EXISTS user_roles CASCADE;
        DROP TABLE IF EXISTS permissions CASCADE;
        DROP TABLE IF EXISTS roles CASCADE;
        DROP TABLE IF EXISTS users CASCADE;
        DROP TABLE IF EXISTS audit_logs CASCADE;
        """)
        
        # 创建表结构
        await conn.execute("""
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
        """)
        
        # 插入测试角色和权限
        await conn.execute("""
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
        """)
    
    yield pool
    
    # 测试完成后关闭连接池
    await pool.close()


@pytest.fixture(scope="session")
def redis_pool():
    """创建Redis连接池"""
    # 创建Redis连接
    redis_client = redis.Redis(
        host=TEST_REDIS_HOST,
        port=TEST_REDIS_PORT,
        db=TEST_REDIS_DB,
        decode_responses=True
    )
    
    # 清空测试数据库
    redis_client.flushdb()
    
    yield redis_client
    
    # 测试完成后清空并关闭
    redis_client.flushdb()
    redis_client.close()


@pytest.fixture
def admin_user_data() -> Dict[str, Any]:
    """生成管理员测试用户数据"""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "username": f"admin_{unique_id}",
        "email": f"admin_{unique_id}@example.com",
        "password": "AdminP@ss123!",
        "phone_number": f"+8613900{unique_id}",
        "profile_data": {
            "display_name": "管理员",
            "role": "admin",
            "department": "IT"
        }
    } 