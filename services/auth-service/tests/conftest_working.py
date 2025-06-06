"""
conftest_working - 索克生活项目模块
"""

    from httpx import AsyncClient
from auth_service.cmd.server.main import create_app
from auth_service.core.database import get_db
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from tests.test_database_manager import TestDatabaseManager, setup_test_database, teardown_test_database
import asyncio
import os
import pytest
import pytest_asyncio

"""
工作的测试配置文件
使用测试数据库管理器解决数据库初始化问题
"""


# 在模块级别设置环境变量，确保在任何导入之前就设置好
os.environ.update({
    "ENVIRONMENT": "testing",
    "JWT_SECRET_KEY": "test-secret-key-for-testing-only-not-for-production",
    "JWT_ALGORITHM": "HS256",
    "JWT_ACCESS_TOKEN_EXPIRE_MINUTES": "30",
    "JWT_REFRESH_TOKEN_EXPIRE_DAYS": "7",
    "DATABASE_URL": "sqlite+aiosqlite:///:memory:",
    "DATABASE_SYNC_URL": "sqlite:///:memory:",
    "DATABASE_ECHO": "false",
    "DATABASE_POOL_SIZE": "5",
    "DATABASE_MAX_OVERFLOW": "10",
    "REDIS_URL": "redis://localhost:6379/1",
    "REDIS_MAX_CONNECTIONS": "10",
    "EMAIL_PROVIDER": "mock",
    "EMAIL_FROM": "test@suoke.life",
    "SMTP_HOST": "localhost",
    "SMTP_PORT": "587",
    "SMTP_USERNAME": "test",
    "SMTP_PASSWORD": "test",
    "RATE_LIMIT_ENABLED": "false",
    "SECURITY_HEADERS_ENABLED": "true",
    "CORS_ENABLED": "true",
    "CORS_ORIGINS": "http://localhost:3000",
    "LOG_LEVEL": "INFO",
    "LOG_FORMAT": "json",
    "METRICS_ENABLED": "false",
    "HEALTH_CHECK_ENABLED": "true",
})



@pytest_asyncio.fixture(scope="session")
async def test_db_manager():
    """会话级别的测试数据库管理器"""
    db_manager = await setup_test_database()
    yield db_manager
    await teardown_test_database(db_manager)


@pytest_asyncio.fixture
async def db_session(test_db_manager):
    """数据库会话fixture"""
    async with test_db_manager.get_session() as session:
        yield session
        # 测试后回滚事务
        await session.rollback()


@pytest.fixture
def app(test_db_manager):
    """FastAPI应用fixture"""
    # 创建应用
    app = create_app()
    
    # 重写数据库依赖
    async def override_get_db():
        async with test_db_manager.get_session() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    return app


@pytest.fixture
def client(app):
    """测试客户端fixture"""
    return TestClient(app)


@pytest_asyncio.fixture
async def async_client(app):
    """异步测试客户端fixture"""
    
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac


# 测试数据fixtures
@pytest.fixture
def sample_user_data():
    """示例用户数据"""
    return {
        "username": "testuser",
        "email": "test@suoke.life",
        "password": "TestPassword123!",
        "confirm_password": "TestPassword123!",
        "full_name": "Test User",
        "phone": "+8613800138000"
    }


@pytest.fixture
def sample_login_data():
    """示例登录数据"""
    return {
        "username": "testuser",
        "password": "TestPassword123!"
    }


# 测试工具函数
def assert_response_success(response, expected_status=200):
    """断言响应成功"""
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}: {response.text}"


def assert_response_error(response, expected_status=400):
    """断言响应错误"""
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}: {response.text}"


def get_auth_headers(token: str) -> dict:
    """获取认证头"""
    return {"Authorization": f"Bearer {token}"}


# 测试配置
pytest_plugins = ["pytest_asyncio"]


def pytest_configure(config):
    """pytest配置"""
    # 设置异步测试模式
    config.option.asyncio_mode = "auto"


@pytest.fixture(autouse=True)
async def cleanup_after_test(test_db_manager):
    """每个测试后自动清理"""
    yield
    # 测试完成后重置数据库
    await test_db_manager.reset_database() 