"""
简单的健康检查测试
"""
from unittest.mock import Mock, patch, AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

def test_health_check_simple():
    """测试简单的健康检查"""
    from app.api.rest.health import router as health_router
    
    # 创建一个简单的FastAPI应用
    app = FastAPI()
    app.include_router(health_router, prefix="/api/v1")
    
    # 模拟容器
    mock_container = Mock()
    mock_container.cache_service = Mock()
    mock_container.knowledge_service = Mock()
    mock_container.metrics_service = Mock()
    
    with patch("app.api.rest.deps.get_container", return_value=mock_container):
        client = TestClient(app)
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data

def test_health_check_direct():
    """直接测试健康检查函数"""
    from app.api.rest.health import health_check
    import asyncio
    
    # 直接调用健康检查函数
    result = asyncio.run(health_check())
    
    assert result["status"] == "healthy"
    assert "timestamp" in result
    assert "version" in result

def test_liveness_check_direct():
    """直接测试存活检查函数"""
    from app.api.rest.health import liveness_check
    import asyncio
    
    # 直接调用存活检查函数
    result = asyncio.run(liveness_check())
    
    assert result["alive"] is True
    assert "response_time" in result
    assert "timestamp" in result

if __name__ == "__main__":
    test_health_check_simple()
    test_health_check_direct()
    test_liveness_check_direct()
    print("所有简单测试通过！") 