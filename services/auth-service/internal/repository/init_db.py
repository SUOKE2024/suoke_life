#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库初始化模块

提供数据库连接池创建和初始化功能。
"""
import logging
from typing import Dict, Any

import asyncpg


async def init_database(config: Dict[str, Any]) -> asyncpg.Pool:
    """
    初始化数据库连接池
    
    Args:
        config: 数据库配置
        
    Returns:
        asyncpg.Pool: 数据库连接池
    """
    logging.info("初始化数据库连接池")
    
    # 提取配置
    host = config.get("host", "localhost")
    port = config.get("port", 5432)
    database = config.get("database", "auth_db")
    username = config.get("username", "postgres")
    password = config.get("password", "postgres")
    pool_size = config.get("pool_size", 10)
    
    # 创建连接池
    try:
        pool = await asyncpg.create_pool(
            host=host,
            port=port,
            database=database,
            user=username,
            password=password,
            min_size=2,
            max_size=pool_size
        )
        
        logging.info(f"数据库连接池初始化成功，连接到 {host}:{port}/{database}")
        
        # 初始化数据库表结构
        await init_tables(pool)
        
        return pool
    except Exception as e:
        logging.error(f"数据库连接池初始化失败: {str(e)}")
        raise


async def init_tables(pool: asyncpg.Pool) -> None:
    """
    初始化数据库表结构
    
    Args:
        pool: 数据库连接池
    """
    logging.info("初始化数据库表结构")
    
    # 在真实项目中，应该使用迁移工具(如Alembic)
    # 这里仅为示例实现简单建表逻辑
    
    # 定义建表SQL
    create_tables_sql = """
    -- 创建UUID扩展（如果不存在）
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    
    -- 用户表
    CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        phone_number VARCHAR(20) UNIQUE,
        status VARCHAR(20) NOT NULL DEFAULT 'pending',
        profile_data JSONB DEFAULT '{}',
        mfa_enabled BOOLEAN NOT NULL DEFAULT FALSE,
        mfa_type VARCHAR(20) NOT NULL DEFAULT 'none',
        mfa_secret VARCHAR(100),
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE,
        last_login TIMESTAMP WITH TIME ZONE
    );
    
    -- 为用户表添加索引
    CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
    CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone_number);
    
    -- 角色表
    CREATE TABLE IF NOT EXISTS roles (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        name VARCHAR(50) UNIQUE NOT NULL,
        description VARCHAR(255),
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE
    );
    
    -- 权限表
    CREATE TABLE IF NOT EXISTS permissions (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        name VARCHAR(100) UNIQUE NOT NULL,
        description VARCHAR(255),
        resource VARCHAR(50) NOT NULL,
        action VARCHAR(50) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE
    );
    
    -- 用户角色关联表
    CREATE TABLE IF NOT EXISTS user_roles (
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
        PRIMARY KEY (user_id, role_id)
    );
    
    -- 角色权限关联表
    CREATE TABLE IF NOT EXISTS role_permissions (
        role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
        permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (role_id, permission_id)
    );
    
    -- 刷新令牌表
    CREATE TABLE IF NOT EXISTS refresh_tokens (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        token_value VARCHAR(255) UNIQUE NOT NULL,
        expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
        is_revoked BOOLEAN NOT NULL DEFAULT FALSE,
        revoked_at TIMESTAMP WITH TIME ZONE,
        client_id VARCHAR(100),
        client_info JSONB,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    
    -- 登录尝试记录表
    CREATE TABLE IF NOT EXISTS login_attempts (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID REFERENCES users(id) ON DELETE SET NULL,
        ip_address VARCHAR(50) NOT NULL,
        user_agent VARCHAR(255),
        success BOOLEAN NOT NULL DEFAULT FALSE,
        attempt_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    
    -- 审计日志表
    CREATE TABLE IF NOT EXISTS audit_logs (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID REFERENCES users(id) ON DELETE SET NULL,
        action VARCHAR(50) NOT NULL,
        resource VARCHAR(50),
        resource_id VARCHAR(50),
        ip_address VARCHAR(50),
        user_agent VARCHAR(255),
        details TEXT,
        success BOOLEAN NOT NULL DEFAULT TRUE,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    
    -- OAuth连接表
    CREATE TABLE IF NOT EXISTS oauth_connections (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        provider VARCHAR(50) NOT NULL,
        provider_user_id VARCHAR(100) NOT NULL,
        access_token VARCHAR(1000) NOT NULL,
        refresh_token VARCHAR(1000),
        expires_at TIMESTAMP WITH TIME ZONE,
        scopes JSONB DEFAULT '[]',
        user_data JSONB DEFAULT '{}',
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE,
        UNIQUE(provider, provider_user_id)
    );
    """
    
    try:
        async with pool.acquire() as conn:
            await conn.execute(create_tables_sql)
            logging.info("数据库表结构初始化成功")
    except Exception as e:
        logging.error(f"数据库表结构初始化失败: {str(e)}")
        # 在真实项目中，根据具体情况决定是否抛出异常
        logging.warning("继续执行，但数据库功能可能不可用") 