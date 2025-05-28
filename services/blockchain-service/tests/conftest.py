"""
测试配置文件

包含所有测试的共享夹具和配置。
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from suoke_blockchain_service.config import Settings
from suoke_blockchain_service.database import Base
from suoke_blockchain_service.main import create_app


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop]:
    """创建事件循环用于整个测试会话"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """测试配置"""
    return Settings(
        environment="testing",
        debug=True,
        database=Settings.DatabaseSettings(
            host="localhost",
            port=5432,
            user="test",
            password="test",
            database="test_blockchain_service",
        ),
        redis=Settings.RedisSettings(
            host="localhost",
            port=6379,
            database=1,
        ),
        blockchain=Settings.BlockchainSettings(
            eth_node_url="http://localhost:8545",
            chain_id=1337,
        ),
        security=Settings.SecuritySettings(
            jwt_secret_key="test-secret-key",
        ),
        monitoring=Settings.MonitoringSettings(
            enable_metrics=False,
            enable_tracing=False,
            log_level="DEBUG",
        ),
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
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # 清理
    await engine.dispose()


@pytest_asyncio.fixture
async def test_db_session(test_db_engine) -> AsyncGenerator[AsyncSession]:
    """测试数据库会话"""
    from sqlalchemy.ext.asyncio import async_sessionmaker

    session_factory = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session


@pytest.fixture
def mock_web3():
    """模拟 Web3 实例"""
    mock = MagicMock()
    mock.eth.chain_id = 1337
    mock.eth.get_block_number.return_value = 100
    mock.eth.get_balance.return_value = 1000000000000000000  # 1 ETH
    mock.eth.gas_price = 20000000000  # 20 Gwei
    return mock


@pytest.fixture
def mock_redis():
    """模拟 Redis 客户端"""
    mock = AsyncMock()
    mock.ping.return_value = True
    mock.get.return_value = None
    mock.set.return_value = True
    mock.delete.return_value = 1
    return mock


@pytest.fixture
def test_app(test_settings, monkeypatch):
    """测试应用实例"""
    # 使用测试配置
    monkeypatch.setattr("suoke_blockchain_service.config.settings", test_settings)

    # 创建应用
    app = create_app()
    return app


@pytest.fixture
def test_client(test_app) -> TestClient:
    """测试客户端"""
    return TestClient(test_app)


@pytest_asyncio.fixture
async def async_test_client(test_app) -> AsyncGenerator[AsyncClient]:
    """异步测试客户端"""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_health_data():
    """示例健康数据"""
    return {
        "user_id": "test-user-123",
        "data_type": "blood_pressure",
        "data": {
            "systolic": 120,
            "diastolic": 80,
            "timestamp": "2024-01-01T10:00:00Z",
        },
        "metadata": {
            "device_id": "bp-monitor-001",
            "location": "home",
        },
    }


@pytest.fixture
def sample_blockchain_transaction():
    """示例区块链交易"""
    return {
        "hash": "0x1234567890abcdef",
        "block_number": 100,
        "gas_used": 21000,
        "status": 1,
        "from": "0xabcdef1234567890",
        "to": "0x1234567890abcdef",
    }


@pytest.fixture
def sample_jwt_token():
    """示例 JWT 令牌"""
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoidGVzdC11c2VyLTEyMyIsImV4cCI6MTY0MDk5NTIwMH0.test-signature"


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
