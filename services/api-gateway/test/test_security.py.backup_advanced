from typing import Dict, List, Any, Optional, Union

"""
test_security - 索克生活项目模块
"""

from datetime import datetime, timedelta, UTC
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from internal.delivery.rest.middleware import AuthMiddleware
from internal.model.config import JwtConfig, AuthConfig, MiddlewareConfig
from pkg.utils.auth import JWTManager, TokenPayload, extract_token_from_header
import jwt
import os
import pytest
import sys

#! / usr / bin / env python
# - * - coding: utf - 8 - * -

"""
安全性测试：JWT令牌和认证机制
"""



# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestSecurity:
    """安全测试类"""

    @pytest.fixture
    def jwt_config(self) - > None:
        """创建JWT配置"""
        return JwtConfig(
            secret_key = "test - jwt - secret - key - for - security - tests",
            algorithm = "HS256",
            expire_minutes = 30,
            refresh_expire_minutes = 60 * 24
        )

    @pytest.fixture
    def jwt_manager(self, jwt_config):
        """创建JWT管理器"""
        return JWTManager(jwt_config)

    @pytest.fixture
    def auth_config(self, jwt_config):
        """创建认证配置"""
        return AuthConfig(
            enabled = True,
            public_paths = [" / api / auth / login", " / api / auth / register", " / health", " / public / *"],
            jwt = jwt_config
        )

    @pytest.fixture
    def app(self, auth_config):
        """创建FastAPI应用"""
        app = FastAPI()

        # 添加认证中间件
        jwt_manager = JWTManager(auth_config.jwt)
        app.add_middleware(
            AuthMiddleware,
            config = auth_config,
            jwt_manager = jwt_manager
        )

        # 添加测试路由
        @app.get(" / health")
        def health_check() - > None:
            """TODO: 添加文档字符串"""
            return {"status": "ok"}

        @app.get(" / api / protected")
        def protected_route(request: Request):
            """TODO: 添加文档字符串"""
            user_id = request.state.user_id
            user_roles = request.state.user_roles
            return {"user_id": user_id, "roles": user_roles}

        @app.get(" / api / admin")
        def admin_route(request: Request):
            """TODO: 添加文档字符串"""
            user_roles = request.state.user_roles
            if "admin" not in user_roles:
                return JSONResponse(
                    status_code = 403,
                    content = {"detail": "仅限管理员访问"}
                )
            return {"message": "管理员内容"}

        return app

    @pytest.fixture
    def client(self, app):
        """创建测试客户端"""
        return TestClient(app)

    def test_create_access_token(self, jwt_manager):
        """测试创建访问令牌"""
        token = jwt_manager.create_access_token("user123", roles = ["user"])

        # 解码并验证令牌
        payload = jwt.decode(
            token,
            jwt_manager.config.secret_key,
            algorithms = [jwt_manager.config.algorithm]
        )

        assert payload["sub"] == "user123"
        assert payload["type"] == "access"
        assert "user" in payload["roles"]
        assert "exp" in payload
        assert "iat" in payload
        assert "nbf" in payload
        assert "jti" in payload

    def test_create_refresh_token(self, jwt_manager):
        """测试创建刷新令牌"""
        token = jwt_manager.create_refresh_token("user123")

        # 解码并验证令牌
        payload = jwt.decode(
            token,
            jwt_manager.config.secret_key,
            algorithms = [jwt_manager.config.algorithm]
        )

        assert payload["sub"] == "user123"
        assert payload["type"] == "refresh"
        assert "exp" in payload
        assert "iat" in payload
        assert "nbf" in payload
        assert "jti" in payload

    def test_validate_token_success(self, jwt_manager):
        """测试验证有效令牌"""
        token = jwt_manager.create_access_token("user123", roles = ["user"])

        # 验证令牌
        payload = jwt_manager.validate_token(token)

        assert isinstance(payload, TokenPayload)
        assert payload.sub == "user123"
        assert payload.type == "access"
        assert "user" in payload.roles

    def test_validate_token_expired(self, jwt_manager):
        """测试验证过期令牌"""
        # 创建立即过期的令牌
        now = datetime.now(UTC)
        expires = now - timedelta(minutes = 5)  # 过期时间设置为5分钟前

        payload = {
            "sub": "user123",
            "roles": ["user"],
            "type": "access",
            "exp": expires.timestamp(),
            "iat": now.timestamp(),
            "nbf": now.timestamp(),
            "jti": "test_expired_token"
        }

        token = jwt.encode(
            payload,
            jwt_manager.config.secret_key,
            algorithm = jwt_manager.config.algorithm
        )

        # 验证过期令牌
        with pytest.raises(ValueError) as excinfo:
            jwt_manager.validate_token(token)

        assert "已过期" in str(excinfo.value)

    def test_validate_token_invalid_signature(self, jwt_manager):
        """测试验证签名无效的令牌"""
        # 使用错误的密钥创建令牌
        wrong_secret = "wrong - secret - key"

        now = datetime.now(UTC)
        expires = now + timedelta(minutes = 30)

        payload = {
            "sub": "user123",
            "roles": ["user"],
            "type": "access",
            "exp": expires.timestamp(),
            "iat": now.timestamp(),
            "nbf": now.timestamp(),
            "jti": "test_invalid_signature"
        }

        token = jwt.encode(
            payload,
            wrong_secret,
            algorithm = "HS256"
        )

        # 验证无效签名
        with pytest.raises(ValueError) as excinfo:
            jwt_manager.validate_token(token)

        assert "签名无效" in str(excinfo.value) or "无效的令牌" in str(excinfo.value)

    def test_validate_token_missing_fields(self, jwt_manager):
        """测试验证缺失字段的令牌"""
        # 创建缺失必要字段的令牌
        now = datetime.now(UTC)
        expires = now + timedelta(minutes = 30)

        # 缺少sub字段
        payload = {
            "roles": ["user"],
            "type": "access",
            "exp": expires.timestamp(),
            "iat": now.timestamp(),
            "nbf": now.timestamp(),
            "jti": "test_missing_fields"
        }

        token = jwt.encode(
            payload,
            jwt_manager.config.secret_key,
            algorithm = jwt_manager.config.algorithm
        )

        # 验证缺失字段
        with pytest.raises(ValueError) as excinfo:
            jwt_manager.validate_token(token)

        assert "缺少必要字段" in str(excinfo.value) or "无效的令牌" in str(excinfo.value)

    def test_validate_token_not_active(self, jwt_manager):
        """测试验证尚未生效的令牌"""
        # 创建未来生效的令牌
        now = datetime.now(UTC)
        not_before = now + timedelta(minutes = 5)  # 5分钟后生效
        expires = now + timedelta(minutes = 30)

        payload = {
            "sub": "user123",
            "roles": ["user"],
            "type": "access",
            "exp": expires.timestamp(),
            "iat": now.timestamp(),
            "nbf": not_before.timestamp(),
            "jti": "test_not_active"
        }

        token = jwt.encode(
            payload,
            jwt_manager.config.secret_key,
            algorithm = jwt_manager.config.algorithm
        )

        # 验证未生效令牌
        with pytest.raises(ValueError) as excinfo:
            jwt_manager.validate_token(token)

        assert "尚未生效" in str(excinfo.value) or "无效的令牌" in str(excinfo.value)

    def test_extract_token_from_header_valid(self) - > None:
        """测试从有效头部提取令牌"""
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        auth_header = f"Bearer {token}"

        extracted_token = extract_token_from_header(auth_header)
        assert extracted_token == token

    def test_extract_token_from_header_invalid(self) - > None:
        """测试从无效头部提取令牌"""
        # 无效前缀
        auth_header = "Invalid eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        with pytest.raises(ValueError) as excinfo:
            extract_token_from_header(auth_header)
        assert "无效的认证头部格式" in str(excinfo.value)

        # 没有令牌部分
        auth_header = "Bearer "
        with pytest.raises(ValueError) as excinfo:
            extract_token_from_header(auth_header)
        assert "无效的认证头部格式" in str(excinfo.value)

    def test_auth_middleware_public_path(self, client):
        """测试认证中间件对公共路径的处理"""
        # 公共路径应该不需要认证
        response = client.get(" / health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_auth_middleware_protected_path_no_token(self, client):
        """测试认证中间件对保护路径无令牌的处理"""
        # 受保护路径没有令牌应该返回401
        response = client.get(" / api / protected")
        assert response.status_code == 401
        assert "未提供认证令牌" in response.json()["detail"]

    def test_auth_middleware_protected_path_invalid_token(self, client):
        """测试认证中间件对保护路径无效令牌的处理"""
        # 无效令牌格式
        headers = {"Authorization": "Invalid token123"}
        response = client.get(" / api / protected", headers = headers)
        assert response.status_code == 401
        assert "无效的认证令牌格式" in response.json()["detail"]

        # 无效令牌内容
        headers = {"Authorization": "Bearer invalid.token.format"}
        response = client.get(" / api / protected", headers = headers)
        assert response.status_code == 401
        assert "无效的认证令牌" in response.json()["detail"]

    def test_auth_middleware_protected_path_valid_token(self, client, jwt_manager):
        """测试认证中间件对保护路径有效令牌的处理"""
        # 创建有效令牌
        token = jwt_manager.create_access_token("test_user", roles = ["user"])
        headers = {"Authorization": f"Bearer {token}"}

        # 发送请求
        response = client.get(" / api / protected", headers = headers)

        # 验证响应
        assert response.status_code == 200
        assert response.json()["user_id"] == "test_user"
        assert "user" in response.json()["roles"]

    def test_auth_middleware_rbac(self, client, jwt_manager):
        """测试基于角色的访问控制"""
        # 创建普通用户令牌
        user_token = jwt_manager.create_access_token("user123", roles = ["user"])
        user_headers = {"Authorization": f"Bearer {user_token}"}

        # 创建管理员令牌
        admin_token = jwt_manager.create_access_token("admin123", roles = ["user", "admin"])
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # 普通用户访问管理员资源
        response = client.get(" / api / admin", headers = user_headers)
        assert response.status_code == 403
        assert "仅限管理员访问" in response.json()["detail"]

        # 管理员访问管理员资源
        response = client.get(" / api / admin", headers = admin_headers)
        assert response.status_code == 200
        assert response.json()["message"] == "管理员内容"

    def test_token_refresh(self, jwt_manager):
        """测试令牌刷新"""
        # 创建刷新令牌
        refresh_token = jwt_manager.create_refresh_token("user123")

        # 验证刷新令牌
        payload = jwt_manager.validate_token(refresh_token)
        assert payload.type == "refresh"
        assert payload.sub == "user123"

        # 使用刷新令牌创建新的访问令牌
        if payload.type == "refresh":
            new_access_token = jwt_manager.create_access_token(
                payload.sub,
                roles = payload.roles
            )

            # 验证新的访问令牌
            new_payload = jwt_manager.validate_token(new_access_token)
            assert new_payload.type == "access"
            assert new_payload.sub == "user123"

if __name__ == "__main__":
    pytest.main([" - v", "test_security.py"])