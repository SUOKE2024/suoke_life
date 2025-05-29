"""主应用测试"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from health_data_service.api.main import app


@pytest.fixture
def client():
    """测试客户端"""
    return TestClient(app)


def test_root_endpoint(client):
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "索克生活健康数据服务"
    assert data["status"] == "running"
    assert "version" in data
    assert "docs" in data


@patch('health_data_service.api.main.get_database')
def test_health_check(mock_get_database, client):
    """测试健康检查"""
    # 模拟数据库连接
    mock_db_gen = AsyncMock()
    mock_get_database.return_value = mock_db_gen
    
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "database" in data


def test_metrics_endpoint(client):
    """测试指标端点"""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    assert "http_requests_total" in response.text
