#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库初始化模块

负责初始化数据库连接、创建表结构和初始化数据。
"""
import logging
from typing import Dict, Any

from sqlalchemy import create_engine, URL
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from internal.model.user import Base
from pkg.utils.database import run_migrations

import asyncpg

logger = logging.getLogger(__name__)

async def init_database(db_config: Dict[str, Any]) -> asyncpg.Pool:
    """
    初始化数据库，创建表和加载初始数据
    
    Args:
        db_config: 数据库配置信息
        
    Returns:
        asyncpg.Pool: 数据库连接池
    """
    # 连接配置
    dsn = f"postgresql://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    
    # 创建连接池
    pool = await asyncpg.create_pool(
        dsn=dsn,
        min_size=5,
        max_size=db_config.get('pool_size', 20)
    )
    
    # 创建表
    async with pool.acquire() as conn:
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
        
        -- 为用户表添加索引
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
        CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone_number);
        
        -- 为审计日志表添加索引
        CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id);
        CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
        CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
        """)
        
        # 检查是否需要插入初始数据
        roles_count = await conn.fetchval("SELECT COUNT(*) FROM roles")
        
        if roles_count == 0:
            logger.info("正在创建初始角色和权限...")
            
            # 插入默认角色
            await conn.execute("""
            INSERT INTO roles (id, name, description, created_at, updated_at)
            VALUES
                ('1', 'admin', '系统管理员，拥有所有权限', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
                ('2', 'user', '普通用户', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
                ('3', 'guest', '访客用户，仅有只读权限', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
            """)
            
            # 插入默认权限
            await conn.execute("""
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
            """)
            
            # 分配权限给角色
            # 管理员角色拥有所有权限
            await conn.execute("""
            INSERT INTO role_permissions (role_id, permission_id)
            SELECT '1', id FROM permissions;
            """)
            
            # 普通用户角色拥有查看用户和自身信息的权限
            await conn.execute("""
            INSERT INTO role_permissions (role_id, permission_id)
            VALUES
                ('2', '1'),  -- user:read
                ('3', '1');  -- guest也有user:read权限
            """)
            
            logger.info("初始角色和权限创建完成")
    
    return pool

async def get_db_session() -> AsyncSession:
    """
    获取数据库会话的依赖函数
    
    Returns:
        AsyncSession: 数据库会话对象
    """
    from fastapi import FastAPI
    app = FastAPI.lifespan_context.get_app()
    session_factory = app.state.db_session_factory
    
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise 