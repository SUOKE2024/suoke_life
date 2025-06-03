"""
测试配置文件

提供测试所需的 fixtures 和配置。
"""

import asyncio
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest
import pytest_asyncio
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool

from suoke_blockchain_service.config import Settings
from suoke_blockchain_service.main import create_app

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator

class TestBase(DeclarativeBase):
    """测试数据库模型基类"""

    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop]:
    """创建事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_settings() -> Settings:
    """测试设置"""
    return Settings(
        app_name="Test Blockchain Service",
        debug=True,
        environment="test",
    )

@pytest_asyncio.fixture
async def test_db_engine():
    """测试数据库引擎"""
    # 使用内存 SQLite 数据库进行测试
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=True,
    )

    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(TestBase.metadata.create_all)

    yield engine

    # 清理
    await engine.dispose()

@pytest_asyncio.fixture
async def test_db_session(test_db_engine) -> AsyncGenerator[AsyncSession]:
    """测试数据库会话"""
    session_factory = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session

@pytest.fixture
def test_app():
    """测试应用"""
    # 使用测试设置创建应用
    app = create_app()
    return app

@pytest.fixture
def test_client(test_app) -> TestClient:
    """同步测试客户端"""
    return TestClient(test_app)

@pytest_asyncio.fixture
async def async_test_client(test_app) -> AsyncGenerator[AsyncClient]:
    """异步测试客户端"""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client

@pytest.fixture
def mock_blockchain_client():
    """模拟区块链客户端"""
    mock_client = MagicMock()
    mock_client.is_connected.return_value = True
    mock_client.get_block_number.return_value = 12345
    mock_client.get_balance.return_value = 1000000000000000000  # 1 ETH in wei
    return mock_client

@pytest.fixture
def mock_redis_client():
    """模拟 Redis 客户端"""
    mock_client = AsyncMock()
    mock_client.ping.return_value = True
    mock_client.get.return_value = None
    mock_client.set.return_value = True
    mock_client.delete.return_value = 1
    return mock_client

@pytest.fixture
def mock_grpc_server():
    """模拟 gRPC 服务器"""
    mock_server = AsyncMock()
    mock_server.start.return_value = None
    mock_server.stop.return_value = None
    mock_server.wait_for_termination.return_value = None
    return mock_server

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """设置测试环境"""
    # 设置测试环境变量
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("DEBUG", "true")

@pytest.fixture
def sample_health_data():
    """示例健康数据"""
    return {
        "user_id": "test-user-123",
        "timestamp": "2024-01-01T00:00:00Z",
        "data_type": "heart_rate",
        "value": 72,
        "unit": "bpm",
        "metadata": {
            "device": "smartwatch",
            "accuracy": "high"
        }
    }

@pytest.fixture
def sample_zkp_proof():
    """示例零知识证明"""
    return {
        "proof": "0x1234567890abcdef",
        "public_inputs": ["0xabcdef", "0x123456"],
        "verification_key": "0xfedcba0987654321"
    }

# 测试标记
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.blockchain = pytest.mark.blockchain
pytest.mark.slow = pytest.mark.slow

# 测试工具函数
def assert_valid_uuid(uuid_string: str) -> None:
    """断言字符串是有效的 UUID"""
    import uuid
    try:
        uuid.UUID(uuid_string)
    except ValueError:
        pytest.fail(f"'{uuid_string}' is not a valid UUID")

def assert_valid_ethereum_address(address: str) -> None:
    """断言字符串是有效的以太坊地址"""
    if not address.startswith("0x") or len(address) != 42:
        pytest.fail(f"'{address}' is not a valid Ethereum address")

def assert_valid_transaction_hash(tx_hash: str) -> None:
    """断言字符串是有效的交易哈希"""
    if not tx_hash.startswith("0x") or len(tx_hash) != 66:
        pytest.fail(f"'{tx_hash}' is not a valid transaction hash")
