"""
conftest_simple - 索克生活项目模块
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

"""
简化的测试配置

避免复杂依赖的测试配置。
"""


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_blockchain_service():
    """Mock区块链服务"""
    service = MagicMock()
    service.encryption_service = AsyncMock()
    service.zk_proof_generator = AsyncMock()
    service.zk_proof_verifier = AsyncMock()
    service.ipfs_client = AsyncMock()
    return service


@pytest.fixture
def sample_health_data():
    """示例健康数据"""
    return {
        "heart_rate": 72,
        "blood_pressure": {"systolic": 120, "diastolic": 80},
        "timestamp": "2024-01-01T10:00:00Z"
    }
