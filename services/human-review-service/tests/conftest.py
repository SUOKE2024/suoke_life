"""
conftest - 索克生活项目模块
"""

    from human_review_service.api.main import create_app
from fastapi.testclient import TestClient
import pytest

"""
测试配置文件
"""


@pytest.fixture
def client():
    """测试客户端"""
    app = create_app()
    return TestClient(app)
