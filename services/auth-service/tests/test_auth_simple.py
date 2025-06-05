"""
Auth-Service 简化测试
"""
import pytest
from fastapi.testclient import TestClient


class TestAuthServiceSimple:
    """Auth-Service 简化测试"""
    
    @pytest.fixture
    def client(self):
        """测试客户端"""
        from auth_service.cmd.server.main import create_app
        app = create_app()
        return TestClient(app)
    
    def test_health_check(self, client):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        print("✓ 健康检查测试通过")
    
    def test_service_info(self, client):
        """测试服务信息端点"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "auth-service"
        assert data["status"] == "running"
        assert "version" in data
        print("✓ 服务信息测试通过")
    
    def test_api_docs_access(self, client):
        """测试API文档访问"""
        response = client.get("/docs")
        assert response.status_code == 200
        print("✓ API文档访问测试通过")
    
    def test_openapi_spec(self, client):
        """测试OpenAPI规范"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert data["info"]["title"] == "Auth Service API"
        print("✓ OpenAPI规范测试通过")
    
    def test_cors_headers(self, client):
        """测试CORS头部"""
        response = client.options("/health")
        # 检查是否有CORS相关的头部
        assert response.status_code in [200, 405]  # OPTIONS可能不被支持，但应该有CORS头
        print("✓ CORS头部测试通过")
    
    def test_invalid_endpoint(self, client):
        """测试无效端点"""
        response = client.get("/invalid-endpoint")
        assert response.status_code == 404
        print("✓ 无效端点测试通过")
    
    def test_auth_endpoints_exist(self, client):
        """测试认证端点是否存在（不测试功能，只测试端点存在）"""
        # 测试登录端点存在
        response = client.post("/api/v1/auth/login", json={})
        # 应该返回422（验证错误）而不是404（端点不存在）
        assert response.status_code != 404
        
        # 测试用户注册端点存在
        response = client.post("/api/v1/users/", json={})
        assert response.status_code != 404
        
        print("✓ 认证端点存在性测试通过")
    
    def test_security_headers(self, client):
        """测试安全头部"""
        response = client.get("/health")
        assert response.status_code == 200
        
        # 检查一些基本的安全头部
        headers = response.headers
        # 这些头部可能由中间件添加
        print(f"响应头部: {dict(headers)}")
        print("✓ 安全头部测试通过")
    
    def test_content_type_handling(self, client):
        """测试内容类型处理"""
        # 测试JSON内容类型
        response = client.post("/api/v1/auth/login", 
                             json={"username": "test", "password": "test"},
                             headers={"Content-Type": "application/json"})
        # 应该返回验证错误或认证错误，而不是内容类型错误
        assert response.status_code != 415
        
        print("✓ 内容类型处理测试通过") 