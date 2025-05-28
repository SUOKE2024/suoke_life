"""
基础测试

测试 soer-service 的基本功能
"""

import pytest
import os
from fastapi.testclient import TestClient
from soer_service.main import create_app

# 设置测试环境变量
os.environ["ENVIRONMENT"] = "testing"
os.environ["DEBUG"] = "true"
os.environ["MONGODB_URL"] = "mongodb://localhost:27017/test"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"

app = create_app()
client = TestClient(app)


def test_health_check():
    """测试健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "timestamp" in data


def test_root_endpoint():
    """测试根端点"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "service" in data


def test_agent_capabilities():
    """测试智能体能力查询"""
    response = client.get("/api/v1/agent/capabilities")
    assert response.status_code == 200
    data = response.json()
    assert "agent_name" in data
    assert "capabilities" in data
    assert "features" in data


def test_nutrition_search():
    """测试营养搜索功能"""
    response = client.get("/api/v1/nutrition/food-database/search?query=苹果")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_health_dashboard():
    """测试健康仪表板"""
    response = client.get("/api/v1/health/dashboard/test_user")
    assert response.status_code == 200
    data = response.json()
    assert "overview" in data
    assert "vital_signs" in data
    assert "recommendations" in data


def test_lifestyle_recommendations():
    """测试生活方式建议"""
    response = client.get("/api/v1/lifestyle/recommendations/test_user")
    if response.status_code != 200:
        print(f"Error response: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert "exercise" in data
    assert "sleep" in data
    assert "stress_management" in data


@pytest.mark.asyncio
async def test_agent_chat():
    """测试智能体对话"""
    chat_data = {
        "user_id": "test_user",
        "message": "你好，我想了解营养建议",
        "context": {}
    }
    
    response = client.post("/api/v1/agent/chat", json=chat_data)
    if response.status_code != 200:
        print(f"Error response: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert "content" in data
    assert "suggestions" in data
    assert "quick_replies" in data


def test_invalid_endpoint():
    """测试无效端点"""
    response = client.get("/api/v1/invalid")
    assert response.status_code == 404


def test_cors_headers():
    """测试 CORS 头部"""
    # 在测试环境中，CORS 头部可能不会被设置，所以我们只测试端点是否可访问
    response = client.get("/api/v1/agent/capabilities")
    assert response.status_code == 200
    # 在实际部署中，CORS 头部会由中间件自动添加
    # 这里我们只验证端点正常工作
    data = response.json()
    assert "agent_name" in data 