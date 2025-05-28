"""
简单的应用测试 - 不依赖数据库连接
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


# 模拟数据库管理器
class MockDatabaseManager:
    async def initialize(self):
        pass

    async def close(self):
        pass


# 模拟健康检查器
class MockHealthChecker:
    async def initialize(self):
        pass

    async def check_health(self):
        return {"status": "healthy", "service": "xiaoke-service", "version": "1.0.0"}

    async def check_readiness(self):
        return {
            "status": "ready",
            "checks": {
                "database": {"status": "healthy"},
                "cache": {"status": "healthy"},
                "ai_service": {"status": "healthy"},
            },
        }

    async def close(self):
        pass


@pytest.fixture
def mock_app():
    """创建模拟的应用实例"""
    with (
        patch("xiaoke_service.services.database.DatabaseManager", MockDatabaseManager),
        patch("xiaoke_service.services.health.HealthChecker", MockHealthChecker),
    ):
        from xiaoke_service.main import create_app

        app = create_app()
        return app


@pytest.fixture
def client(mock_app):
    """创建测试客户端"""
    return TestClient(mock_app)


def test_health_check(client):
    """测试健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_readiness_check(client):
    """测试就绪检查端点"""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_api_health(client):
    """测试API健康检查"""
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "xiaoke-service"


def test_chat_endpoint(client):
    """测试对话端点"""
    response = client.post(
        "/api/v1/chat/", json={"message": "你好，小克", "session_id": "test-session"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["session_id"] == "test-session"


def test_knowledge_search(client):
    """测试知识库搜索"""
    response = client.post(
        "/api/v1/knowledge/search", json={"query": "中医理论", "limit": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert data["query"] == "中医理论"


def test_knowledge_categories(client):
    """测试知识库分类"""
    response = client.get("/api/v1/knowledge/categories")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert len(data["categories"]) > 0
