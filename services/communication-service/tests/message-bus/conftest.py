from typing import Dict, List, Any, Optional, Union

"""
conftest - 索克生活项目模块
"""

from unittest.mock import MagicMock
import asyncio
import os
import pytest
import sys

"""
pytest配置文件
"""


# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置asyncio事件循环
@pytest.fixture(scope = "session")
def event_loop() -> None:
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# 模拟设置
@pytest.fixture
def mock_settings() -> None:
    """创建模拟设置"""
    settings = MagicMock()
    settings.server.host = "localhost"
    settings.server.port = 50051
    settings.server.max_workers = 10
    settings.kafka.bootstrap_servers = ["localhost:9092"]
    settings.kafka.topic_prefix = "test_"
    settings.redis.host = "localhost"
    settings.redis.port = 6379
    settings.enable_auth = False
    return settings