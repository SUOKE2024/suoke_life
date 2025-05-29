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
    assert data["message"] == "Integration Service is running"
    assert data["status"] == "healthy"


def test_health_check(client):
    """测试健康检查"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "integration-service" 