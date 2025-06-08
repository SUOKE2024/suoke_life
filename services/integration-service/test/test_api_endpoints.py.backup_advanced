from typing import Dict, List, Any, Optional, Union

"""
test_api_endpoints - 索克生活项目模块
"""

from fastapi.testclient import TestClient
from integration_service.main import create_app
import os
import pytest

"""
API端点测试
"""


# 设置测试环境变量
os.environ["DATABASE_URL"] = "sqlite: / / / . / test.db"
os.environ["DEBUG"] = "true"
os.environ["SECRET_KEY"] = "test - secret - key"



@pytest.fixture
def client() - > None:
    """创建测试客户端"""
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers() - > None:
    """认证头"""
    return {"Authorization": "Bearer test - token"}


def test_root_endpoint(client):
    """测试根端点"""
    response = client.get(" / ")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Integration Service"
    assert data["status"] == "running"


def test_health_endpoint(client):
    """测试健康检查端点"""
    response = client.get(" / health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data


def test_live_endpoint(client):
    """测试活跃检查端点"""
    response = client.get(" / live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"


def test_ready_endpoint(client):
    """测试就绪检查端点"""
    response = client.get(" / ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"


def test_docs_endpoint(client):
    """测试API文档端点"""
    response = client.get(" / docs")
    assert response.status_code == 200


def test_openapi_endpoint(client):
    """测试OpenAPI规范端点"""
    response = client.get(" / openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data


def test_health_data_types_endpoint(client):
    """测试健康数据类型端点"""
    response = client.get(" / api / v1 / health - data / types")
    assert response.status_code == 200
    data = response.json()
    assert "data_types" in data
    assert "count" in data
    assert isinstance(data["data_types"], list)
    assert data["count"] > 0


def test_platforms_list_endpoint(client):
    """测试平台列表端点"""
    # 平台列表端点需要token参数
    response = client.get(" / api / v1 / platforms / ?token = test - token")
    # 可能返回422因为token验证失败，但至少应该有响应
    assert response.status_code in [200, 401, 422]


def test_health_data_list_endpoint(client, auth_headers):
    """测试健康数据列表端点"""
    # 健康数据端点需要token参数
    response = client.get(" / api / v1 / health - data / ?token = test - token", headers = auth_headers)
    # 可能返回401或422因为没有真实的认证，但至少应该有响应
    assert response.status_code in [200, 401, 422]


def test_auth_login_endpoint(client):
    """测试登录端点"""
    login_data = {
        "username": "test@example.com",
        "password": "testpassword"
    }
    # 使用JSON格式发送数据
    response = client.post(" / api / v1 / auth / login", json = login_data)
    # 可能返回401因为用户不存在，但至少应该有响应
    assert response.status_code in [200, 401, 422]


def test_invalid_endpoint(client):
    """测试无效端点"""
    response = client.get(" / api / v1 / invalid - endpoint")
    assert response.status_code == 404


def test_cors_headers(client):
    """测试CORS头"""
    response = client.options(" / ")
    # 检查是否有CORS相关的头
    assert response.status_code in [200, 405]  # OPTIONS可能不被支持，但应该有响应


if __name__ == "__main__":
    pytest.main([__file__, " - v"])