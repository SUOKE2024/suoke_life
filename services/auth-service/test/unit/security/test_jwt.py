#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JWT令牌工具单元测试
"""
import time
from datetime import datetime, timedelta

import jwt
import pytest

from internal.security.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
    create_token_pair
)
from internal.model.errors import InvalidTokenError, ConfigurationError


class TestJWTSecurity:
    """JWT安全功能测试"""
    
    # 测试密钥
    SECRET_KEY = "test_secret_key_for_jwt_tokens"
    
    def test_create_access_token(self):
        """测试创建访问令牌"""
        # 准备测试数据
        user_data = {
            "sub": "user123",
            "username": "testuser",
            "roles": ["user"],
            "permissions": ["read:data"]
        }
        
        # 创建令牌
        token = create_access_token(
            data=user_data,
            secret_key=self.SECRET_KEY,
            expires_delta=timedelta(minutes=15)
        )
        
        # 验证令牌不为空
        assert token is not None
        assert isinstance(token, str)
        
        # 解码并验证内容
        payload = jwt.decode(token, self.SECRET_KEY, algorithms=["HS256"])
        
        # 检查必要字段
        assert payload["sub"] == user_data["sub"]
        assert payload["username"] == user_data["username"]
        assert payload["roles"] == user_data["roles"]
        assert payload["permissions"] == user_data["permissions"]
        assert "jti" in payload  # 令牌ID
        assert "iat" in payload  # 发行时间
        assert "exp" in payload  # 过期时间
    
    def test_create_refresh_token(self):
        """测试创建刷新令牌"""
        # 准备测试数据
        user_data = {
            "sub": "user123",
            "username": "testuser"
        }
        
        # 创建令牌
        token = create_refresh_token(
            data=user_data,
            secret_key=self.SECRET_KEY,
            expires_delta=timedelta(days=7)
        )
        
        # 验证令牌不为空
        assert token is not None
        assert isinstance(token, str)
        
        # 解码并验证内容
        payload = jwt.decode(token, self.SECRET_KEY, algorithms=["HS256"])
        
        # 检查必要字段
        assert payload["sub"] == user_data["sub"]
        assert payload["username"] == user_data["username"]
        assert payload["token_type"] == "refresh"  # 确认是刷新令牌
        assert "jti" in payload  # 令牌ID
        assert "iat" in payload  # 发行时间
        assert "exp" in payload  # 过期时间
    
    def test_decode_token_valid(self):
        """测试解码有效令牌"""
        # 准备测试数据
        user_data = {
            "sub": "user123",
            "username": "testuser"
        }
        
        # 创建令牌
        token = create_access_token(
            data=user_data,
            secret_key=self.SECRET_KEY
        )
        
        # 解码令牌
        payload = decode_token(token, self.SECRET_KEY)
        
        # 检查解码结果
        assert payload["sub"] == user_data["sub"]
        assert payload["username"] == user_data["username"]
    
    def test_decode_token_expired(self):
        """测试解码过期令牌"""
        # 准备测试数据
        user_data = {
            "sub": "user123",
            "username": "testuser"
        }
        
        # 创建一个立即过期的令牌
        payload = {
            **user_data,
            "exp": datetime.utcnow() - timedelta(seconds=1)  # 已过期
        }
        token = jwt.encode(payload, self.SECRET_KEY, algorithm="HS256")
        
        # 尝试解码，应抛出异常
        with pytest.raises(InvalidTokenError) as exc_info:
            decode_token(token, self.SECRET_KEY)
        
        # 验证异常信息
        assert "过期" in str(exc_info.value)
    
    def test_decode_token_invalid(self):
        """测试解码无效令牌"""
        # 创建一个无效令牌
        invalid_token = "invalid.token.string"
        
        # 尝试解码，应抛出异常
        with pytest.raises(InvalidTokenError) as exc_info:
            decode_token(invalid_token, self.SECRET_KEY)
        
        # 验证异常信息
        assert "无效" in str(exc_info.value)
    
    def test_decode_token_wrong_secret(self):
        """测试使用错误密钥解码"""
        # 准备测试数据
        user_data = {
            "sub": "user123",
            "username": "testuser"
        }
        
        # 创建令牌
        token = create_access_token(
            data=user_data,
            secret_key=self.SECRET_KEY
        )
        
        # 使用错误密钥尝试解码，应抛出异常
        wrong_key = "wrong_secret_key"
        with pytest.raises(InvalidTokenError):
            decode_token(token, wrong_key)
    
    def test_create_token_pair(self):
        """测试创建令牌对"""
        # 准备测试数据
        user_id = "user123"
        username = "testuser"
        roles = ["user"]
        permissions = ["read:data"]
        
        # 创建令牌对
        access_token, refresh_token, expires_in = create_token_pair(
            user_id=user_id,
            username=username,
            roles=roles,
            permissions=permissions,
            secret_key=self.SECRET_KEY,
            access_token_expires=timedelta(minutes=30),
            refresh_token_expires=timedelta(days=7)
        )
        
        # 验证令牌不为空
        assert access_token is not None
        assert refresh_token is not None
        assert expires_in == 30 * 60  # 30分钟转换为秒
        
        # 解码访问令牌
        access_payload = jwt.decode(access_token, self.SECRET_KEY, algorithms=["HS256"])
        
        # 检查访问令牌内容
        assert access_payload["sub"] == user_id
        assert access_payload["username"] == username
        assert access_payload["roles"] == roles
        assert access_payload["permissions"] == permissions
        
        # 解码刷新令牌
        refresh_payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=["HS256"])
        
        # 检查刷新令牌内容
        assert refresh_payload["sub"] == user_id
        assert refresh_payload["username"] == username
        assert refresh_payload["token_type"] == "refresh"
        assert "roles" not in refresh_payload  # 刷新令牌不应包含角色
        assert "permissions" not in refresh_payload  # 刷新令牌不应包含权限
    
    def test_missing_secret_key(self):
        """测试缺少密钥的情况"""
        # 准备测试数据
        user_data = {
            "sub": "user123",
            "username": "testuser"
        }
        
        # 尝试创建令牌，应抛出异常
        with pytest.raises(ConfigurationError) as exc_info:
            create_access_token(user_data, "")
        
        # 验证异常信息
        assert "密钥未配置" in str(exc_info.value) 