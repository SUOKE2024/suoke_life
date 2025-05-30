"""
测试配置文件
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock

@pytest.fixture
def client():
    """测试客户端"""
    from auth_service.api.main import create_app
    app = create_app()
    return TestClient(app)
