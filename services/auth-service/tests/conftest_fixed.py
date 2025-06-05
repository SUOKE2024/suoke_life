"""
修复的测试配置文件 - 解决数据库初始化问题
"""

import os
import asyncio
import tempfile
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

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
    "EMAIL_PROVIDER": "console",
    "EMAIL_FROM": "test@suoke.life",
    "EMAIL_SMTP_HOST": "localhost",
    "EMAIL_SMTP_PORT": "587",
    "EMAIL_SMTP_USERNAME": "test",
    "EMAIL_SMTP_PASSWORD": "test",
    "EMAIL_USE_TLS": "true",
    "RATE_LIMIT_ENABLED": "false",
    "RATE_LIMIT_REQUESTS": "100",
    "RATE_LIMIT_WINDOW": "60",
    "SECURITY_ALLOWED_HOSTS": "*",
    "SECURITY_CORS_ORIGINS": "*",
    "MONITORING_ENABLED": "false",
    "LOG_LEVEL": "INFO",
    "LOG_FORMAT": "json"
})

# 导入应用模块
from auth_service.core.database import DatabaseManager, set_db_manager, BaseModel
from auth_service.config.settings import DatabaseSettings
from auth_service.cmd.server.main import create_app


class TestDatabaseManager:
    """测试专用数据库管理器"""
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self._async_engine = None
        self._async_session_factory = None
        self._initialized = False
        
    async def initialize(self) -> None:
        """初始化测试数据库"""
        if self._initialized:
            return
            
        try:
            # 创建异步引擎，使用SQLite内存数据库
            self._async_engine = create_async_engine(
                self.db_url,
                poolclass=StaticPool,
                connect_args={
                    "check_same_thread": False,
                },
                echo=False,
            )
            
            # 创建会话工厂
            self._async_session_factory = async_sessionmaker(
                bind=self._async_engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
            
            # 创建所有表
            async with self._async_engine.begin() as conn:
                await conn.run_sync(BaseModel.metadata.create_all)
            
            self._initialized = True
            
        except Exception as e:
            print(f"测试数据库初始化失败: {e}")
            raise
    
    async def get_async_session(self):
        """获取异步数据库会话"""
        if not self._async_session_factory:
            raise RuntimeError("测试数据库未初始化")
        
        async with self._async_session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def close(self) -> None:
        """关闭数据库连接"""
        if self._async_engine:
            await self._async_engine.dispose()
        self._initialized = False
    
    async def cleanup(self) -> None:
        """清理测试数据"""
        if self._async_engine:
            async with self._async_engine.begin() as conn:
                await conn.run_sync(BaseModel.metadata.drop_all)
                await conn.run_sync(BaseModel.metadata.create_all)


@pytest_asyncio.fixture(scope="function")
async def test_db_manager():
    """测试数据库管理器fixture"""
    # 创建临时数据库文件
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    db_url = f"sqlite+aiosqlite:///{temp_db.name}"
    
    # 创建测试数据库管理器
    test_manager = TestDatabaseManager(db_url)
    await test_manager.initialize()
    
    # 设置全局数据库管理器
    set_db_manager(test_manager)
    
    yield test_manager
    
    # 清理
    await test_manager.close()
    try:
        os.unlink(temp_db.name)
    except:
        pass


@pytest_asyncio.fixture
async def db_session(test_db_manager):
    """数据库会话fixture"""
    async with test_db_manager.get_async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def client(test_db_manager):
    """测试客户端fixture"""
    app = create_app()
    
    # 重写数据库依赖
    from auth_service.core.database import get_db
    
    async def override_get_db():
        async for session in test_db_manager.get_async_session():
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client


@pytest_asyncio.fixture
async def authenticated_client(client, db_session):
    """认证客户端fixture"""
    # 创建测试用户
    from auth_service.repositories.user_repository import UserRepository
    from auth_service.core.auth import get_password_hash
    
    user_repo = UserRepository(db_session)
    
    # 创建测试用户
    test_user = await user_repo.create_user(
        username="testuser",
        email="test@suoke.life",
        password_hash=get_password_hash("testpassword123"),
        full_name="Test User"
    )
    
    # 登录获取token
    login_response = client.post("/api/v1/auth/login", json={
        "username": "testuser",
        "password": "testpassword123"
    })
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        access_token = token_data["access_token"]
        
        # 设置认证头
        client.headers.update({"Authorization": f"Bearer {access_token}"})
    
    yield client, test_user


# 性能测试相关fixture
@pytest.fixture
def performance_config():
    """性能测试配置"""
    return {
        "concurrent_users": 10,
        "test_duration": 30,  # 秒
        "max_response_time": 1000,  # 毫秒
        "min_throughput": 100,  # 请求/秒
    }


@pytest_asyncio.fixture
async def load_test_users(db_session):
    """负载测试用户数据"""
    from auth_service.repositories.user_repository import UserRepository
    from auth_service.core.auth import get_password_hash
    
    user_repo = UserRepository(db_session)
    users = []
    
    # 创建100个测试用户
    for i in range(100):
        user = await user_repo.create_user(
            username=f"loadtest_user_{i}",
            email=f"loadtest_{i}@suoke.life",
            password_hash=get_password_hash("testpassword123"),
            full_name=f"Load Test User {i}"
        )
        users.append(user)
    
    yield users
    
    # 清理测试用户
    for user in users:
        try:
            await user_repo.delete_user(user.id)
        except:
            pass 