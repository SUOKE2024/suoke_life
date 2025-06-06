
"""
API测试
"""

def test_health_check(client):
    """测试健康检查"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_service_info(client):
    """测试服务信息"""
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert "auth-service is running" in data["message"]
