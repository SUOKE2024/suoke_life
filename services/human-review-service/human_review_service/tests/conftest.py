"""
测试配置文件
Test Configuration

为测试提供数据库会话、测试数据等
"""

import asyncio
import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from human_review_service.core.config import get_settings, settings
from human_review_service.core.database import (
    close_database,
    create_tables,
    drop_tables,
    get_session_factory,
    init_database,
)
from human_review_service.core.service import HumanReviewService


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def setup_database():
    """设置测试数据库"""
    # 确保使用测试环境
    os.environ["ENVIRONMENT"] = "testing"
    # 使用 SQLite 进行测试，确保使用异步驱动
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

    # 清除配置缓存并重新加载
    from human_review_service.core.config import get_settings

    get_settings.cache_clear()  # 清除 lru_cache
    settings = get_settings()

    # 初始化数据库
    await init_database()

    # 创建表
    await create_tables()

    yield

    # 清理
    await drop_tables()
    await close_database()

    # 删除测试数据库文件
    if os.path.exists("./test.db"):
        os.remove("./test.db")


@pytest_asyncio.fixture
async def db_session(setup_database) -> AsyncGenerator[AsyncSession, None]:
    """提供数据库会话"""
    session_factory = get_session_factory()

    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def human_review_service(db_session: AsyncSession) -> HumanReviewService:
    """提供人工审核服务实例"""
    return HumanReviewService(session=db_session)


@pytest.fixture
def sample_review_data():
    """提供示例审核数据"""
    return {
        "content_type": "user_profile",
        "content_id": "user_123",
        "content_data": {
            "username": "test_user",
            "email": "test@example.com",
            "profile_image": "https://example.com/image.jpg",
        },
        "risk_score": 0.7,
        "risk_factors": ["suspicious_email", "new_account"],
        "priority": "high",
        "agent_id": "xiaoai_agent",
        "estimated_duration": 1800,
    }


@pytest.fixture
def sample_reviewer_data():
    """提供示例审核员数据"""
    return {
        "reviewer_id": "reviewer_001",
        "name": "Test Reviewer",
        "email": "reviewer@example.com",
        "specialties": ["user_profiles", "content_moderation"],
        "max_concurrent_tasks": 5,
        "skill_level": "senior",
    }
