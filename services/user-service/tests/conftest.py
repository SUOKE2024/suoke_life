"""
pytest配置文件

提供测试夹具和配置。
"""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient
from httpx import AsyncClient

# 设置事件循环策略
@pytest.fixture(scope="session")
def event_loop_policy():
    return asyncio.get_event_loop_policy()

@pytest.fixture(scope="session")
def event_loop(event_loop_policy):
    loop = event_loop_policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """异步HTTP客户端夹具"""
    async with AsyncClient() as client:
        yield client

@pytest.fixture
def mock_user_repository():
    """模拟用户仓库"""
    return AsyncMock()

@pytest.fixture
def mock_user_service():
    """模拟用户服务"""
    return AsyncMock()

@pytest.fixture
def sample_user_data():
    """示例用户数据"""
    return {
        "id": "test-user-id",
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }

@pytest.fixture
def sample_health_data():
    """示例健康数据"""
    return {
        "user_id": "test-user-id",
        "height": 175.0,
        "weight": 70.0,
        "blood_type": "A+",
        "allergies": ["peanuts"],
        "medications": [],
        "medical_history": []
    }

# 测试标记
pytest_plugins = ["pytest_asyncio"]

# 配置异步测试
@pytest_asyncio.fixture
async def async_test_setup():
    """异步测试设置"""
    # 测试前设置
    yield
    # 测试后清理 