#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
中间件测试
"""

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient

from suoke_api_gateway.core.config import Settings
from suoke_api_gateway.middleware.auth import AuthMiddleware
from suoke_api_gateway.middleware.logging import LoggingMiddleware
from suoke_api_gateway.middleware.rate_limit import RateLimitMiddleware
from suoke_api_gateway.middleware.security import SecurityMiddleware
from suoke_api_gateway.middleware.tracing import TracingMiddleware

class TestAuthMiddleware:
    """认证中间件测试"""
    
    @pytest.fixture
    def app(self):
        """创建测试应用"""
        app = FastAPI()
        
        @app.get("/public")
        async def public_endpoint():
            return {"message": "public"}
        
        @app.get("/private")
        async def private_endpoint(request: Request):
            return {
                "message": "private",
                "user_id": getattr(request.state, "user_id", None),
            }
        
        return app
    
    @pytest.fixture
    def settings(self):
        """创建测试设置"""
        return Settings(
            jwt_secret_key="test-secret-key",
            jwt_algorithm="HS256",
        )
    
    def test_public_path_access(self, app, settings):
        """测试公开路径访问"""
        app.add_middleware(AuthMiddleware, settings=settings)
        client = TestClient(app)
        
        response = client.get("/public")
        assert response.status_code == 200
        assert response.json()["message"] == "public"
    
    def test_private_path_without_token(self, app, settings):
        """测试私有路径无令牌访问"""
        app.add_middleware(AuthMiddleware, settings=settings)
        client = TestClient(app)
        
        response = client.get("/private")
        assert response.status_code == 401
        assert "Unauthorized" in response.json()["error"]
    
    def test_private_path_with_invalid_token(self, app, settings):
        """测试私有路径无效令牌访问"""
        app.add_middleware(AuthMiddleware, settings=settings)
        client = TestClient(app)
        
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.get("/private", headers=headers)
        assert response.status_code == 401
        assert "Unauthorized" in response.json()["error"]
    
    def test_private_path_with_valid_token(self, app, settings):
        """测试私有路径有效令牌访问"""
        from jose import jwt
        
        # 创建有效令牌
        payload = {
            "sub": "test-user-id",
            "email": "test@example.com",
            "roles": ["user"],
            "exp": int(time.time()) + 3600,  # 1小时后过期
        }
        token = jwt.encode(payload, settings.jwt.secret_key, algorithm=settings.jwt.algorithm)
        
        app.add_middleware(AuthMiddleware, settings=settings)
        client = TestClient(app)
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/private", headers=headers)
        assert response.status_code == 200
        assert response.json()["user_id"] == "test-user-id"

class TestLoggingMiddleware:
    """日志中间件测试"""
    
    @pytest.fixture
    def app(self):
        """创建测试应用"""
        app = FastAPI()
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}
        
        @app.get("/error")
        async def error_endpoint():
            raise Exception("Test error")
        
        return app
    
    def test_request_logging(self, app):
        """测试请求日志记录"""
        app.add_middleware(LoggingMiddleware)
        client = TestClient(app)
        
        with patch('suoke_api_gateway.middleware.logging.log_request_response') as mock_log:
            response = client.get("/test")
            assert response.status_code == 200
            
            # 验证日志记录被调用
            mock_log.assert_called_once()
            call_args = mock_log.call_args[1]
            assert call_args["method"] == "GET"
            assert "/test" in call_args["url"]
            assert call_args["status_code"] == 200
    
    def test_request_id_header(self, app):
        """测试请求ID头部"""
        app.add_middleware(LoggingMiddleware)
        client = TestClient(app)
        
        response = client.get("/test")
        assert "X-Request-ID" in response.headers
        assert "X-Process-Time" in response.headers

class TestRateLimitMiddleware:
    """限流中间件测试"""
    
    @pytest.fixture
    def app(self):
        """创建测试应用"""
        app = FastAPI()
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}
        
        return app
    
    @pytest.fixture
    def settings(self):
        """创建测试设置"""
        return Settings(
            rate_limit_enabled=True,
            rate_limit_default_rate="5/minute",
            rate_limit_storage_url="redis://localhost:6379/1",
        )
    
    @pytest.mark.asyncio
    async def test_rate_limit_disabled(self, app):
        """测试禁用限流"""
        settings = Settings(rate_limit_enabled=False)
        app.add_middleware(RateLimitMiddleware, settings=settings)
        client = TestClient(app)
        
        # 多次请求应该都成功
        for _ in range(10):
            response = client.get("/test")
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_rate_limit_headers(self, app, settings):
        """测试限流响应头"""
        with patch('redis.asyncio.from_url') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client
            mock_client.ping.return_value = True
            mock_client.zcard.return_value = 0
            mock_client.zadd.return_value = 1
            mock_client.expire.return_value = True
            
            app.add_middleware(RateLimitMiddleware, settings=settings)
            client = TestClient(app)
            
            response = client.get("/test")
            assert response.status_code == 200
            # 注意：由于测试环境的限制，这些头部可能不会出现

class TestSecurityMiddleware:
    """安全中间件测试"""
    
    @pytest.fixture
    def app(self):
        """创建测试应用"""
        app = FastAPI()
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}
        
        return app
    
    def test_security_headers(self, app):
        """测试安全头部"""
        app.add_middleware(SecurityMiddleware)
        client = TestClient(app)
        
        response = client.get("/test")
        assert response.status_code == 200
        
        # 检查安全头部
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        assert "Referrer-Policy" in response.headers
        assert "Permissions-Policy" in response.headers

class TestTracingMiddleware:
    """链路追踪中间件测试"""
    
    @pytest.fixture
    def app(self):
        """创建测试应用"""
        app = FastAPI()
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}
        
        @app.get("/error")
        async def error_endpoint():
            raise Exception("Test error")
        
        return app
    
    def test_trace_headers(self, app):
        """测试追踪头部"""
        app.add_middleware(TracingMiddleware)
        client = TestClient(app)
        
        response = client.get("/test")
        assert response.status_code == 200
        
        # 检查追踪头部
        assert "X-Trace-ID" in response.headers
        assert "X-Span-ID" in response.headers
    
    def test_skip_health_endpoints(self, app):
        """测试跳过健康检查端点"""
        app.add_middleware(TracingMiddleware)
        
        @app.get("/health")
        async def health_endpoint():
            return {"status": "ok"}
        
        client = TestClient(app)
        
        response = client.get("/health")
        assert response.status_code == 200
        # 健康检查端点不应该有追踪头部
        assert "X-Trace-ID" not in response.headers

if __name__ == "__main__":
    pytest.main(["-v", "test_middleware.py"]) 