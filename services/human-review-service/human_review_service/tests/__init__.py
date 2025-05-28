"""
测试模块
Test Module

提供单元测试、集成测试和端到端测试
"""

import pytest
import asyncio
from typing import AsyncGenerator

from ..core.database import init_database, close_database, get_session
from ..core.config import settings


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_test_database():
    """设置测试数据库"""
    # 使用测试数据库
    settings.database.url = settings.test_database_url
    
    # 初始化数据库
    await init_database()
    
    yield
    
    # 清理
    await close_database()


@pytest.fixture
async def db_session(setup_test_database) -> AsyncGenerator:
    """提供数据库会话"""
    async with get_session() as session:
        yield session 