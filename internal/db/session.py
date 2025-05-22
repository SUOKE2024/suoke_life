#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库会话管理模块
提供数据库连接和会话获取功能
"""
import os
import logging
from typing import AsyncGenerator

import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

# 获取数据库配置
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "auth_service")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

# 构建连接字符串
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 测试环境使用不同的数据库
TEST_MODE = os.getenv("PYTEST_RUNNING", "0") == "1"
if TEST_MODE:
    # 使用测试数据库
    TEST_DB_NAME = os.getenv("TEST_DB_NAME", "auth_test")
    DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{TEST_DB_NAME}"

# 创建异步引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    poolclass=NullPool if TEST_MODE else None
)

# 创建会话工厂
async_session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

logger = logging.getLogger(__name__)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话，用于依赖注入
    
    Yields:
        AsyncSession: 异步数据库会话
    """
    session = async_session_factory()
    try:
        yield session
    except Exception as e:
        logger.exception("数据库会话异常: %s", str(e))
        await session.rollback()
        raise
    finally:
        await session.close()

# 数据库连接池（用于直接执行SQL）
_pool = None

async def get_db_pool():
    """
    获取数据库连接池
    
    Returns:
        asyncpg.Pool: 数据库连接池
    """
    global _pool
    if _pool is None:
        try:
            _pool = await asyncpg.create_pool(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME if not TEST_MODE else os.getenv("TEST_DB_NAME", "auth_test"),
                min_size=5,
                max_size=20
            )
        except Exception as e:
            logger.exception("创建数据库连接池失败: %s", str(e))
            raise
    
    return _pool 