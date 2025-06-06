"""
conftest - 索克生活项目模块
"""

    from human_review_service.core.database import get_session_dependency
from fastapi.testclient import TestClient
from human_review_service.api.main import create_app
from human_review_service.core.config import settings
from human_review_service.core.models import Base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
import asyncio
import os
import pytest
import pytest_asyncio

"""
pytest配置文件
Pytest Configuration

定义全局测试fixtures和配置
"""





@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """创建测试数据库引擎"""
    # 使用SQLite内存数据库进行测试
    test_db_url = "sqlite+aiosqlite:///:memory:"

    engine = create_async_engine(test_db_url, echo=False, future=True)

    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # 清理
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def test_session_factory(test_engine):
    """创建测试会话工厂"""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    return async_session


@pytest_asyncio.fixture
async def db_session(test_session_factory) -> AsyncGenerator[AsyncSession, None]:
    """提供数据库会话"""
    async with test_session_factory() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


@pytest.fixture
def test_client(test_session_factory):
    """创建测试客户端"""
    # 创建测试应用（跳过生命周期管理）
    app = create_app(skip_lifespan=True)

    # 覆盖数据库依赖 - 直接覆盖get_session_dependency
    async def override_get_session_dependency():
        async with test_session_factory() as session:
            try:
                yield session
            finally:
                await session.rollback()
                await session.close()

    # 导入正确的依赖函数

    app.dependency_overrides[get_session_dependency] = override_get_session_dependency

    # 创建测试客户端
    with TestClient(app) as client:
        yield client


@pytest.fixture(autouse=True)
def setup_test_environment():
    """设置测试环境"""
    # 设置测试环境变量
    os.environ["ENVIRONMENT"] = "testing"

    # 重新加载配置以使用测试设置
    settings.environment = "testing"

    yield

    # 清理环境变量
    if "ENVIRONMENT" in os.environ:
        del os.environ["ENVIRONMENT"]
