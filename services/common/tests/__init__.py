#!/usr/bin/env python3
"""
索克生活平台通用组件库测试包

这个包包含了所有的测试代码,分为以下几个部分:
- unit: 单元测试
- integration: 集成测试
- e2e: 端到端测试
"""

import asyncio
from collections.abc import Generator
from typing import Any

import pytest


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """创建事件循环用于异步测试"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_config() -> dict[str, Any]:
    """测试配置"""
    return {
        "security": {
            "encryption": {
                "algorithm": "AES-256-GCM",
                "key_size": 32,
            }
        },
        "messaging": {
            "kafka": {
                "bootstrap_servers": ["localhost:9092"],
                "client_id": "test_client",
            }
        },
        "governance": {
            "circuit_breaker": {
                "failure_threshold": 5,
                "recovery_timeout": 60,
            }
        },
    }


@pytest.fixture
async def mock_components():
    """提供模拟的组件实例"""
    from unittest.mock import AsyncMock, MagicMock

    components = {
        "config": {
            "manager": AsyncMock(),
            "center": AsyncMock(),
        },
        "security": {
            "encryption": AsyncMock(),
            "auth": AsyncMock(),
        },
        "messaging": {
            "queue": AsyncMock(),
            "kafka": AsyncMock(),
            "rabbitmq": AsyncMock(),
        },
        "governance": {
            "circuit_breaker": AsyncMock(),
            "rate_limiter": AsyncMock(),
        },
        "observability": {
            "metrics": AsyncMock(),
            "logging": AsyncMock(),
            "tracing": AsyncMock(),
        },
        "performance": {
            "cache": AsyncMock(),
            "database": AsyncMock(),
            "async": AsyncMock(),
        },
        "service_registry": {
            "registry": AsyncMock(),
        },
        "distributed_transaction": {
            "saga": AsyncMock(),
            "tcc": AsyncMock(),
            "event_sourcing": AsyncMock(),
        },
        "api_docs": {
            "generator": AsyncMock(),
            "decorators": AsyncMock(),
            "swagger": AsyncMock(),
        },
        "service_mesh": {
            "manager": AsyncMock(),
            "istio": AsyncMock(),
            "linkerd": AsyncMock(),
            "envoy": AsyncMock(),
        },
        "testing": {
            "framework": AsyncMock(),
        },
    }

    return components
