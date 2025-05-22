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
        # 创建令牌
        user_id = "test_user_id"
        token = jwt_security.create_access_token(user_id)
        
        # 验证令牌
        payload = jwt.decode(token, "test_secret_key", algorithms=["HS256"])
        assert payload["sub"] == user_id
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload
        
        # 验证过期时间
        now = datetime.now(UTC).timestamp()
        assert payload["exp"] > now
        assert payload["exp"] <= now + 30*60 + 5  # 允许5秒误差
    
    def test_create_refresh_token(self, jwt_security):
        """测试创建刷新令牌"""
        # 创建令牌
        user_id = "test_user_id"
        token = jwt_security.create_refresh_token(user_id)
        
        # 验证令牌
        payload = jwt.decode(token, "test_secret_key", algorithms=["HS256"])
        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"
        assert "exp" in payload
        assert "iat" in payload
        
        # 验证过期时间
        now = datetime.now(UTC).timestamp()
        assert payload["exp"] > now
        assert payload["exp"] <= now + 60*60*24*7 + 5  # 允许5秒误差
    
    def test_create_token_with_custom_expires(self, jwt_security):
        """测试创建带自定义过期时间的令牌"""
        # 创建令牌，10分钟过期
        user_id = "test_user_id"
        expires = timedelta(minutes=10)
        token = jwt_security.create_access_token(user_id, expires_delta=expires)
        
        # 验证令牌
        payload = jwt.decode(token, "test_secret_key", algorithms=["HS256"])
        assert payload["sub"] == user_id
        
        # 验证过期时间
        now = datetime.now(UTC).timestamp()
        assert payload["exp"] > now
        assert payload["exp"] <= now + 10*60 + 5  # 允许5秒误差
    
    def test_verify_token_valid(self, jwt_security):
        """测试验证有效令牌"""
        # 创建令牌
        user_id = "test_user_id"
        token = jwt_security.create_access_token(user_id)
        
        # 验证令牌
        claims = jwt_security.verify_token(token)
        assert claims["sub"] == user_id
        assert claims["type"] == "access"
    
    def test_verify_token_invalid_signature(self, jwt_security):
        """测试验证无效签名"""
        # 创建令牌
        user_id = "test_user_id"
        token = jwt_security.create_access_token(user_id)
        
        # 修改令牌使签名无效
        token_parts = token.split(".")
        token_parts[2] = "invalid_signature"
        invalid_token = ".".join(token_parts)
        
        # 验证令牌
        with pytest.raises(AuthenticationError, match="无效的令牌签名"):
            jwt_security.verify_token(invalid_token)
    
    def test_verify_token_expired(self, jwt_security):
        """测试验证已过期令牌"""
        # 创建已过期的令牌
        user_id = "test_user_id"
        expires = timedelta(seconds=-1)
        token = jwt_security.create_access_token(user_id, expires_delta=expires)
        
        # 验证令牌
        with pytest.raises(AuthenticationError, match="令牌已过期"):
            jwt_security.verify_token(token)
    
    def test_verify_token_invalid_payload(self, jwt_security):
        """测试验证无效载荷"""
        # 创建无效载荷的令牌
        payload = {"invalid": "payload"}
        token = jwt.encode(payload, "test_secret_key", algorithm="HS256")
        
        # 验证令牌
        with pytest.raises(AuthenticationError, match="无效的令牌载荷"):
            jwt_security.verify_token(token)
    
    def test_verify_token_malformed(self, jwt_security):
        """测试验证格式错误的令牌"""
        # 创建格式错误的令牌
        token = "not.a.jwt.token"
        
        # 验证令牌
        with pytest.raises(AuthenticationError, match="令牌格式错误"):
            jwt_security.verify_token(token)
    
    def test_refresh_access_token_valid(self, jwt_security):
        """测试使用有效刷新令牌刷新访问令牌"""
        # 创建刷新令牌
        user_id = "test_user_id"
        refresh_token = jwt_security.create_refresh_token(user_id)
        
        # 刷新访问令牌
        access_token = jwt_security.refresh_access_token(refresh_token)
        
        # 验证新的访问令牌
        payload = jwt.decode(access_token, "test_secret_key", algorithms=["HS256"])
        assert payload["sub"] == user_id
        assert payload["type"] == "access"
    
    def test_refresh_access_token_invalid(self, jwt_security):
        """测试使用无效刷新令牌刷新访问令牌"""
        # 创建访问令牌而不是刷新令牌
        user_id = "test_user_id"
        access_token = jwt_security.create_access_token(user_id)
        
        # 尝试刷新访问令牌
        with pytest.raises(AuthenticationError, match="无效的刷新令牌"):
            jwt_security.refresh_access_token(access_token)
    
    def test_get_user_id_from_token(self, jwt_security):
        """测试从令牌中获取用户ID"""
        # 创建令牌
        user_id = "test_user_id"
        token = jwt_security.create_access_token(user_id)
        
        # 获取用户ID
        extracted_user_id = jwt_security.get_user_id_from_token(token)
        assert extracted_user_id == user_id 