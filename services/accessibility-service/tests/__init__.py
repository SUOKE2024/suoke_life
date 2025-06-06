"""
__init__ - 索克生活项目模块
"""

    from accessibility_service.models.accessibility import (
from collections.abc import Generator
import asyncio
import os
import pytest
import sys

"""
测试模块

包含无障碍服务的所有测试：
- unit: 单元测试
- integration: 集成测试
- e2e: 端到端测试
- performance: 性能测试
"""



# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

__all__ = []


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_accessibility_request():
    """Sample accessibility request for testing."""
        AccessibilityRequest,
        AccessibilityType,
    )

    return AccessibilityRequest(
        user_id="test_user_123",
        session_id="test_session_456",
        accessibility_types=[AccessibilityType.VISUAL, AccessibilityType.AUDIO],
        visual_data={"image_url": "https://example.com/test.jpg"},
        audio_data={"audio_url": "https://example.com/test.wav"},
        detailed_analysis=True,
        real_time=False
    )
