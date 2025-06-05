"""
测试配置文件
"""

import os
import asyncio
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# 在模块级别设置环境变量，确保在任何导入之前就设置好
os.environ.update({
    "ENVIRONMENT": "testing",
    "JWT_SECRET_KEY": "test-secret-key-for-testing-only-not-for-production",
    "JWT_ALGORITHM": "HS256",
    "JWT_ACCESS_TOKEN_EXPIRE_MINUTES": "30",
    "JWT_REFRESH_TOKEN_EXPIRE_DAYS": "7",
    "DATABASE_URL": "sqlite+aiosqlite:///./test.db",
    "DATABASE_SYNC_URL": "sqlite:///./test.db",
    "DATABASE_ECHO": "false",
    "DATABASE_POOL_SIZE": "5",
    "DATABASE_MAX_OVERFLOW": "10",
    "REDIS_URL": "redis://localhost:6379/1",
    "REDIS_MAX_CONNECTIONS": "10",
    "EMAIL_PROVIDER": "smtp",
    "EMAIL_SMTP_HOST": "localhost",
    "EMAIL_SMTP_PORT": "587",
    "EMAIL_SMTP_USERNAME": "test@example.com",
    "EMAIL_SMTP_PASSWORD": "test-password",
    "EMAIL_FROM_ADDRESS": "test@example.com",
    "EMAIL_FROM_NAME": "Test Service",
    "SECURITY_CORS_ORIGINS": '["http://localhost:3000"]',
    "SECURITY_ALLOWED_HOSTS": '["localhost", "127.0.0.1"]',
    "MONITORING_ENABLED": "false",
    "MONITORING_METRICS_PORT": "8001",
    "MONITORING_HEALTH_CHECK_INTERVAL": "30"
})


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """设置测试环境变量（已在模块级别设置）"""
    pass


# 全局数据库管理器，在模块级别初始化
_test_db_manager = None


def get_test_db_manager():
    """获取测试数据库管理器"""
    global _test_db_manager
    if _test_db_manager is None:
        from auth_service.config.settings import get_settings
        from auth_service.core.database import DatabaseManager, set_db_manager
        
        settings = get_settings()
        _test_db_manager = DatabaseManager(settings.database)
        
        # 使用事件循环初始化数据库
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_test_db_manager.initialize())
            loop.run_until_complete(_test_db_manager.create_tables())
        finally:
            loop.close()
        
        # 设置全局数据库管理器
        set_db_manager(_test_db_manager)
    
    return _test_db_manager


@pytest.fixture(scope="session")
def db_manager():
    """数据库管理器fixture"""
    manager = get_test_db_manager()
    yield manager
    
    # 清理
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(manager.close())
    finally:
        loop.close()


@pytest_asyncio.fixture
async def db_session(db_manager):
    """数据库会话fixture"""
    async with db_manager.get_async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def client():
    """测试客户端"""
    # 确保数据库管理器已初始化
    get_test_db_manager()
    
    from auth_service.cmd.server.main import create_app
    app = create_app()
    return TestClient(app)


@pytest_asyncio.fixture
async def async_client():
    """异步测试客户端"""
    from httpx import AsyncClient
    
    # 确保数据库管理器已初始化
    get_test_db_manager()
    
    from auth_service.cmd.server.main import create_app
    app = create_app()
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client
