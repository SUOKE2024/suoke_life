"""
主应用测试
"""

from fastapi.testclient import TestClient

from xiaoke_service.main import app

client = TestClient(app)


def test_health_check():
    """测试健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_readiness_check():
    """测试就绪检查端点"""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_api_health():
    """测试API健康检查"""
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "xiaoke-service"


def test_chat_endpoint():
    """测试对话端点"""
    response = client.post(
        "/api/v1/chat/", json={"message": "你好，小克", "session_id": "test-session"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["session_id"] == "test-session"


def test_knowledge_search():
    """测试知识库搜索"""
    response = client.post(
        "/api/v1/knowledge/search", json={"query": "中医理论", "limit": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert data["query"] == "中医理论"


def test_knowledge_categories():
    """测试知识库分类"""
    response = client.get("/api/v1/knowledge/categories")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert len(data["categories"]) > 0
