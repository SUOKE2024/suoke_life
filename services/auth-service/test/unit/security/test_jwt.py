#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JWT安全模块单元测试
"""
import pytest
import jwt
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, UTC
import time
import base64

from internal.security.jwt import JWTSecurity
from internal.model.errors import AuthenticationError


class TestJWTSecurity:
    """JWT安全模块测试"""
    
    @pytest.fixture
    def jwt_security(self):
        """创建JWT安全实例"""
        return JWTSecurity(
            secret_key="test_secret_key",
            algorithm="HS256",
            access_token_expire_minutes=30,
            refresh_token_expire_minutes=60*24*7
        )
    
    def test_init(self, jwt_security):
        """测试初始化"""
        assert jwt_security.secret_key == "test_secret_key"
        assert jwt_security.algorithm == "HS256"
        assert jwt_security.access_token_expire_minutes == 30
        assert jwt_security.refresh_token_expire_minutes == 60*24*7
    
    def test_create_access_token(self, jwt_security):
        """测试创建访问令牌"""
        user_id = "user123"
        token = jwt_security.create_access_token(user_id)
        
        # 解码并验证令牌
        payload = jwt.decode(token, "test_secret_key", algorithms=["HS256"])
        
        assert payload["sub"] == user_id
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload
        assert "jti" in payload
    
    def test_create_access_token_with_additional_data(self, jwt_security):
        """测试创建带有额外数据的访问令牌"""
        user_id = "user123"
        additional_data = {"username": "testuser", "roles": ["admin"]}
        token = jwt_security.create_access_token(user_id, additional_data=additional_data)
        
        # 解码并验证令牌
        payload = jwt.decode(token, "test_secret_key", algorithms=["HS256"])
        
        assert payload["sub"] == user_id
        assert payload["type"] == "access"
        assert payload["username"] == "testuser"
        assert payload["roles"] == ["admin"]
    
    def test_create_access_token_with_expires(self, jwt_security):
        """测试创建带有自定义过期时间的访问令牌"""
        user_id = "user123"
        expires_delta = timedelta(minutes=5)
        token = jwt_security.create_access_token(user_id, expires_delta=expires_delta)
        
        # 解码并验证令牌
        payload = jwt.decode(token, "test_secret_key", algorithms=["HS256"])
        
        now = datetime.now(UTC).timestamp()
        assert payload["exp"] - now <= 5 * 60 + 1  # 允许1秒误差
    
    def test_create_refresh_token(self, jwt_security):
        """测试创建刷新令牌"""
        user_id = "user123"
        token = jwt_security.create_refresh_token(user_id)
        
        # 解码并验证令牌
        payload = jwt.decode(token, "test_secret_key", algorithms=["HS256"])
        
        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"
        assert "exp" in payload
        assert "iat" in payload
        assert "jti" in payload
    
    def test_verify_token_valid(self, jwt_security):
        """测试验证有效令牌"""
        user_id = "user123"
        token = jwt_security.create_access_token(user_id)
        
        payload = jwt_security.verify_token(token)
        
        assert payload["sub"] == user_id
        assert payload["type"] == "access"
    
    def test_verify_token_expired(self, jwt_security):
        """测试验证过期令牌"""
        user_id = "user123"
        # 创建一个已经过期的令牌
        expires_delta = timedelta(seconds=-1)
        token = jwt_security.create_access_token(user_id, expires_delta=expires_delta)
        
        with pytest.raises(AuthenticationError, match="令牌已过期"):
            jwt_security.verify_token(token)
    
    def test_verify_token_invalid_signature(self, jwt_security):
        """测试验证签名无效的令牌"""
        # 创建一个有效的令牌
        token = jwt_security.create_access_token("user123")
        
        # 创建一个具有有效格式但签名错误的令牌
        header, payload, _ = token.split(".")
        # 使用不同的密钥创建令牌
        different_jwt = JWTSecurity(secret_key="different_key")
        different_token = different_jwt.create_access_token("user123")
        _, _, signature = different_token.split(".")
        
        # 组合出有效格式但签名错误的令牌
        invalid_token = f"{header}.{payload}.{signature}"
        
        with pytest.raises(AuthenticationError, match="无效的令牌签名"):
            jwt_security.verify_token(invalid_token)
    
    def test_verify_token_malformed(self, jwt_security):
        """测试验证格式错误的令牌"""
        with pytest.raises(AuthenticationError, match="令牌格式错误"):
            jwt_security.verify_token("not.a.valid.token")
    
    def test_refresh_access_token(self, jwt_security):
        """测试刷新访问令牌"""
        user_id = "user123"
        refresh_token = jwt_security.create_refresh_token(user_id)
        
        new_access_token = jwt_security.refresh_access_token(refresh_token)
        
        # 验证新令牌
        payload = jwt.decode(new_access_token, "test_secret_key", algorithms=["HS256"])
        assert payload["sub"] == user_id
        assert payload["type"] == "access"
    
    def test_refresh_access_token_with_access_token(self, jwt_security):
        """测试使用访问令牌刷新访问令牌 (应该失败)"""
        user_id = "user123"
        access_token = jwt_security.create_access_token(user_id)
        
        with pytest.raises(AuthenticationError, match="无效的刷新令牌"):
            jwt_security.refresh_access_token(access_token)
    
    def test_get_user_id_from_token(self, jwt_security):
        """测试从令牌中获取用户ID"""
        user_id = "user123"
        token = jwt_security.create_access_token(user_id)
        
        extracted_user_id = jwt_security.get_user_id_from_token(token)
        
        assert extracted_user_id == user_id


class TestLegacyJWTFunctions:
    """兼容性函数测试"""
    
    @pytest.fixture
    def patched_env(self, monkeypatch):
        """模拟环境变量"""
        monkeypatch.setenv("JWT_SECRET_KEY", "test_env_secret")
        monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15")
        monkeypatch.setenv("REFRESH_TOKEN_EXPIRE_MINUTES", "10080")
    
    def test_create_access_token(self, patched_env):
        """测试创建访问令牌"""
        from internal.security.jwt import create_access_token
        
        user_id = "user123"
        token = create_access_token({"sub": user_id})
        
        # 解码验证
        payload = jwt.decode(token, "test_env_secret", algorithms=["HS256"])
        assert payload["sub"] == user_id
    
    def test_create_refresh_token(self, patched_env):
        """测试创建刷新令牌"""
        from internal.security.jwt import create_refresh_token
        
        user_id = "user123"
        token = create_refresh_token({"sub": user_id})
        
        # 解码验证
        payload = jwt.decode(token, "test_env_secret", algorithms=["HS256"])
        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"
    
    def test_decode_token(self, patched_env):
        """测试解码令牌"""
        from internal.security.jwt import create_access_token, decode_token
        
        user_id = "user123"
        token = create_access_token({"sub": user_id})
        
        payload = decode_token(token)
        assert payload["sub"] == user_id
    
    def test_create_token_pair(self, patched_env):
        """测试创建令牌对"""
        from internal.security.jwt import create_token_pair
        
        user_id = "user123"
        username = "testuser"
        roles = ["admin"]
        permissions = ["read", "write"]
        
        access_token, refresh_token, expires_in = create_token_pair(
            user_id, username, roles, permissions
        )
        
        # 验证访问令牌
        access_payload = jwt.decode(access_token, "test_env_secret", algorithms=["HS256"])
        assert access_payload["sub"] == user_id
        assert access_payload["username"] == username
        assert access_payload["roles"] == roles
        assert access_payload["permissions"] == permissions
        
        # 验证刷新令牌
        refresh_payload = jwt.decode(refresh_token, "test_env_secret", algorithms=["HS256"])
        assert refresh_payload["sub"] == user_id
        
        # 验证过期时间
        assert expires_in == 15 * 60  # 15分钟 