#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库会话管理模块
"""
import os
from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker

# 数据库配置
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://postgres:postgres@localhost:5432/auth_service"
)

# 创建异步引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
)

# 创建会话工厂
async_session_factory = async_sessionmaker(
    engine, 
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话
    
    Yields:
        AsyncSession: SQLAlchemy异步会话对象
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


# FastAPI 依赖注入函数
async def get_db() -> AsyncSession:
    """
    FastAPI依赖函数，用于注入数据库会话
    
    Returns:
        AsyncSession: SQLAlchemy异步会话对象
    """
    async for session in get_session():
        return session 