#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
认证中间件集成测试
"""

import base64
import json
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import jwt
import pytest
from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.testclient import TestClient

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from internal.delivery.rest.middleware import AuthMiddleware, setup_middlewares
from internal.model.config import AuthConfig, JwtConfig, MiddlewareConfig
from pkg.utils.auth import JWTManager, TokenPayload


# 测试密钥
TEST_SECRET_KEY = "test_secret_key_for_auth_integration_tests"
TEST_ALGORITHM = "HS256"
TEST_EXPIRE_MINUTES = 30


@pytest.fixture
def jwt_manager():
    """创建JWT管理器"""
    config = JwtConfig(
        secret_key=TEST_SECRET_KEY,
        algorithm=TEST_ALGORITHM,
        expire_minutes=TEST_EXPIRE_MINUTES,
        refresh_expire_minutes=60 * 24
    )
    return JWTManager(config)


@pytest.fixture
def auth_config():
    """创建认证配置"""
    return AuthConfig(
        enabled=True,
        public_paths=[
            "/health",
            "/api/auth/login",
            "/api/auth/register",
            "/public/*"
        ],
        jwt=JwtConfig(
            secret_key=TEST_SECRET_KEY,
            algorithm=TEST_ALGORITHM,
            expire_minutes=TEST_EXPIRE_MINUTES,
            refresh_expire_minutes=60 * 24
        )
    )


@pytest.fixture
def middleware_config(auth_config):
    """创建中间件配置"""
    return MiddlewareConfig(
        auth=auth_config
    )


@pytest.fixture
def test_app(middleware_config):
    """创建测试应用"""
    app = FastAPI()
    
    # 设置中间件
    setup_middlewares(app, middleware_config)
    
    # 添加测试路由
    @app.get("/health")
    def health_check():
        return {"status": "ok"}
    
    @app.get("/api/auth/login")
    def login():
        return {"token": "mock_token"}
    
    @app.get("/public/test")
    def public_test():
        return {"message": "public endpoint"}
    
    @app.get("/api/protected")
    def protected_endpoint():
        """受保护的端点"""
        user_id = getattr(app.state, "user_id", None)
        user_roles = getattr(app.state, "user_roles", [])
        return {"user_id": user_id, "roles": user_roles}
    
    @app.get("/api/admin")
    def admin_endpoint():
        """管理员端点"""
        user_id = getattr(app.state, "user_id", None)
        user_roles = getattr(app.state, "user_roles", [])
        
        if "admin" not in user_roles:
            raise HTTPException(status_code=403, detail="仅管理员可访问")
        
        return {"message": "管理员专属内容", "user_id": user_id}
    
    return app


@pytest.fixture
def client(test_app):
    """创建测试客户端"""
    return TestClient(test_app)


def create_token(user_id: str, roles: List[str] = None, expired: bool = False) -> str:
    """创建测试令牌"""
    now = datetime.utcnow()
    roles = roles or ["user"]
    
    payload = {
        "sub": user_id,
        "roles": roles,
        "type": "access",
        "iat": now.timestamp(),
        "nbf": now.timestamp(),
        "jti": "test_token_" + str(int(time.time()))
    }
    
    if expired:
        # 创建已过期的令牌
        payload["exp"] = (now - timedelta(minutes=5)).timestamp()
    else:
        payload["exp"] = (now + timedelta(minutes=TEST_EXPIRE_MINUTES)).timestamp()
    
    token = jwt.encode(payload, TEST_SECRET_KEY, algorithm=TEST_ALGORITHM)
    return token


class TestAuthMiddleware:
    """认证中间件测试"""
    
    def test_public_endpoints(self, client):
        """测试公共端点无需认证"""
        # 健康检查端点
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        
        # 登录端点
        response = client.get("/api/auth/login")
        assert response.status_code == 200
        assert "token" in response.json()
        
        # 通配符匹配的公共端点
        response = client.get("/public/test")
        assert response.status_code == 200
        assert response.json() == {"message": "public endpoint"}
    
    def test_protected_endpoint_no_token(self, client):
        """测试无令牌访问受保护端点"""
        response = client.get("/api/protected")
        assert response.status_code == 401
        assert "detail" in response.json()
        assert "未提供认证令牌" in response.json()["detail"]
    
    def test_protected_endpoint_invalid_token_format(self, client):
        """测试无效令牌格式"""
        headers = {"Authorization": "InvalidFormat token123"}
        response = client.get("/api/protected", headers=headers)
        assert response.status_code == 401
        assert "无效的认证令牌格式" in response.json()["detail"]
    
    def test_protected_endpoint_expired_token(self, client):
        """测试过期令牌"""
        token = create_token("user123", expired=True)
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/protected", headers=headers)
        assert response.status_code == 401
        assert "令牌已过期" in response.json()["detail"]
    
    def test_protected_endpoint_valid_token(self, client):
        """测试有效令牌"""
        token = create_token("user123", roles=["user"])
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/protected", headers=headers)
        assert response.status_code == 200
        assert response.json()["user_id"] == "user123"
        assert "user" in response.json()["roles"]
    
    def test_admin_endpoint_non_admin(self, client):
        """测试非管理员访问管理员端点"""
        token = create_token("user123", roles=["user"])
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/admin", headers=headers)
        assert response.status_code == 403
        assert "仅管理员可访问" in response.json()["detail"]
    
    def test_admin_endpoint_admin(self, client):
        """测试管理员访问管理员端点"""
        token = create_token("admin123", roles=["user", "admin"])
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/admin", headers=headers)
        assert response.status_code == 200
        assert response.json()["message"] == "管理员专属内容"
        assert response.json()["user_id"] == "admin123" 