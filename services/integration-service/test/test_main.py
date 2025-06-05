"""
主应用测试
"""

import pytest
from fastapi.testclient import TestClient
from integration_service.main import create_app


@pytest.fixture
def client():
    """测试客户端"""
    app = create_app()
    return TestClient(app)


def test_root_endpoint(client):
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Integration Service"
    assert data["status"] == "running"


def test_health_check(client):
    """测试健康检查"""
    response = client.get("/health")
    # 健康检查可能返回503如果数据库未连接，这在测试环境中是正常的
    assert response.status_code in [200, 503]
    data = response.json()
    assert "status" in data
    assert "timestamp" in data 