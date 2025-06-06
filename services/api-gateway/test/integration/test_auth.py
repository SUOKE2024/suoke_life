"""
test_auth - 索克生活项目模块
"""

from datetime import datetime, timedelta, UTC
from fastapi import Depends, FastAPI, HTTPException, Security, status, Request
from fastapi.testclient import TestClient
from internal.delivery.rest.middleware import AuthMiddleware, setup_middlewares
from internal.model.config import AuthConfig, JwtConfig, MiddlewareConfig
from pkg.utils.auth import JWTManager, TokenPayload
from typing import Dict, List, Optional, Tuple
import jwt
import os
import pytest
import sys
import time

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
认证中间件集成测试
"""



# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


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
    def protected_endpoint(request: Request):
        """受保护的端点"""
        user_id = getattr(request.state, "user_id", None)
        user_roles = getattr(request.state, "user_roles", [])
        return {"user_id": user_id, "roles": user_roles}
    
    @app.get("/api/admin")
    def admin_endpoint(request: Request):
        """管理员端点"""
        user_id = getattr(request.state, "user_id", None)
        user_roles = getattr(request.state, "user_roles", [])
        
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
    now = datetime.now(UTC)
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

@pytest.mark.asyncio
async def test_complex_public_path_matching():
    """测试复杂的公共路径匹配规则"""
    # 创建各种复杂的公共路径规则
    config = GatewayConfig(
        routes=[],
        middleware=MiddlewareConfig(
            auth=AuthConfig(
                enabled=True,
                jwt=JwtConfig(
                    secret_key="test-secret",
                    algorithm="HS256",
                    expire_minutes=30
                ),
                public_paths=[
                    "/api/public",  # 精确匹配
                    "/api/docs/*",  # 通配符匹配
                    "/api/v*/status",  # 中间通配符
                    "/health-*",   # 前缀匹配
                    "*.png",       # 文件扩展名匹配
                ]
            )
        )
    )
    
    app = FastAPI()
    auth_middleware = AuthMiddleware(app, config.middleware.auth)
    
    # 测试各种路径匹配情况
    test_cases = [
        # 精确匹配
        ("/api/public", True),
        ("/api/public/", False),  # 尾部斜杠不匹配精确路径
        
        # 通配符匹配
        ("/api/docs/index.html", True),
        ("/api/docs/swagger.json", True),
        ("/api/docs", False),  # 不匹配父路径
        
        # 中间通配符
        ("/api/v1/status", True),
        ("/api/v2/status", True),
        ("/api/vstatus", False),  # 不匹配缺少/的路径
        
        # 前缀匹配
        ("/health-check", True),
        ("/health-status", True),
        ("/health", False),  # 不匹配前缀
        
        # 文件扩展名匹配
        ("/assets/image.png", True),
        ("/deep/path/icon.png", True),
        ("/image.jpg", False)  # 不匹配其他扩展名
    ]
    
    for path, expected in test_cases:
        assert auth_middleware._is_public_path(path) == expected, f"Path {path} should be {'public' if expected else 'private'}"

@pytest.mark.asyncio
async def test_invalid_token_formats():
    """测试各种无效令牌格式"""
    config = GatewayConfig(
        routes=[],
        middleware=MiddlewareConfig(
            auth=AuthConfig(
                enabled=True,
                jwt=JwtConfig(
                    secret_key="test-secret",
                    algorithm="HS256",
                    expire_minutes=30
                ),
                public_paths=["/public"]
            )
        )
    )
    
    app = FastAPI()
    auth_middleware = AuthMiddleware(app, config.middleware.auth)
    
    # 测试各种无效令牌格式
    invalid_auth_headers = [
        "",                      # 空字符串
        "Bearer",                # 只有Bearer前缀
        "Bearer ",               # Bearer后面是空格
        "bearer token",          # 小写bearer
        "Basic dXNlcjpwYXNz",    # Basic认证格式
        "token",                 # 无前缀
        "Bearer\ttoken",         # 使用tab分隔
        "Bearer\ntoken",         # 使用换行分隔
        "Bearer token extra",    # 多余的部分
        f"Bearer {' ' * 1000}",  # 非常长的空格
        "Bearer " + "a" * 10000, # 非常长的令牌
    ]
    
    for header in invalid_auth_headers:
        request = Request(scope={
            "type": "http",
            "method": "GET",
            "path": "/api/private",
            "headers": [(b"authorization", header.encode())]
        })
        
        user = await auth_middleware._get_current_user(request)
        assert user is None, f"应该不能从无效授权头 '{header}' 中获取用户"

@pytest.mark.asyncio
async def test_token_with_missing_claims():
    """测试缺少必要声明的令牌"""
    config = GatewayConfig(
        routes=[],
        middleware=MiddlewareConfig(
            auth=AuthConfig(
                enabled=True,
                jwt=JwtConfig(
                    secret_key="test-secret",
                    algorithm="HS256",
                    expire_minutes=30
                ),
                public_paths=["/public"]
            )
        )
    )
    
    app = FastAPI()
    auth_middleware = AuthMiddleware(app, config.middleware.auth)
    
    # 创建JWT管理器
    jwt_manager = JWTManager(config.middleware.auth.jwt)
    
    # 测试缺少不同声明的情况
    test_cases = [
        # 缺少sub
        {"exp": time.time() + 3600, "roles": ["user"]},
        
        # 缺少exp
        {"sub": "user-123", "roles": ["user"]},
        
        # 缺少roles
        {"sub": "user-123", "exp": time.time() + 3600},
        
        # 空的sub
        {"sub": "", "exp": time.time() + 3600, "roles": ["user"]},
        
        # 无效的roles类型
        {"sub": "user-123", "exp": time.time() + 3600, "roles": "user"},
        
        # 完全空的payload
        {}
    ]
    
    for payload in test_cases:
        # 手动创建令牌
        token = jwt.encode(payload, config.middleware.auth.jwt.secret_key, algorithm=config.middleware.auth.jwt.algorithm)
        
        # 创建请求
        request = Request(scope={
            "type": "http",
            "method": "GET",
            "path": "/api/private",
            "headers": [(b"authorization", f"Bearer {token}".encode())]
        })
        
        # 尝试获取用户
        user = await auth_middleware._get_current_user(request)
        assert user is None, f"应该不能从缺少必要声明的令牌中获取用户: {payload}"

@pytest.mark.asyncio
async def test_expired_token_handling():
    """测试过期令牌处理"""
    config = GatewayConfig(
        routes=[],
        middleware=MiddlewareConfig(
            auth=AuthConfig(
                enabled=True,
                jwt=JwtConfig(
                    secret_key="test-secret",
                    algorithm="HS256",
                    expire_minutes=30
                ),
                public_paths=["/public"]
            )
        )
    )
    
    app = FastAPI()
    auth_middleware = AuthMiddleware(app, config.middleware.auth)
    
    # 创建一个已经过期的令牌
    payload = {
        "sub": "user-123",
        "exp": time.time() - 60,  # 过期时间为1分钟前
        "roles": ["user"]
    }
    
    token = jwt.encode(payload, config.middleware.auth.jwt.secret_key, algorithm=config.middleware.auth.jwt.algorithm)
    
    # 创建请求
    request = Request(scope={
        "type": "http",
        "method": "GET",
        "path": "/api/private",
        "headers": [(b"authorization", f"Bearer {token}".encode())]
    })
    
    # 尝试获取用户
    user = await auth_middleware._get_current_user(request)
    assert user is None, "应该不能从过期令牌中获取用户" 