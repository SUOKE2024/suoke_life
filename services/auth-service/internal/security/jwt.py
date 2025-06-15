#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JWT 令牌工具
提供JWT认证相关工具函数
"""
import logging
import os
import uuid
from datetime import datetime, timedelta, UTC
from typing import Dict, Any, Optional, Tuple

import jwt

from internal.model.errors import AuthenticationError, ConfigurationError

logger = logging.getLogger(__name__)


class JWTSecurity:
    """JWT安全工具类，封装JWT令牌相关功能"""
    
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_minutes: int = 10080  # 7天
    ):
        """
        初始化JWT安全工具
        
        Args:
            secret_key: JWT密钥
            algorithm: 加密算法
            access_token_expire_minutes: 访问令牌过期时间(分钟)
            refresh_token_expire_minutes: 刷新令牌过期时间(分钟)
        
        Raises:
            ConfigurationError: 配置错误，比如密钥未设置
        """
        if not secret_key:
            raise ConfigurationError("JWT密钥未配置")
        
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_minutes = refresh_token_expire_minutes
    
    def create_access_token(
        self,
        user_id: str,
        expires_delta: Optional[timedelta] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        创建访问令牌
        
        Args:
            user_id: 用户ID
            expires_delta: 过期时间增量，如果不提供则使用默认值
            additional_data: 额外数据
            
        Returns:
            str: JWT令牌
        """
        if expires_delta is None:
            expires_delta = timedelta(minutes=self.access_token_expire_minutes)
        
        expire = datetime.now(UTC) + expires_delta
        
        to_encode = {
            "sub": user_id,
            "type": "access",
            "iat": datetime.now(UTC),
            "exp": expire,
            "jti": str(uuid.uuid4())
        }
        
        if additional_data:
            to_encode.update(additional_data)
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(
        self,
        user_id: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        创建刷新令牌
        
        Args:
            user_id: 用户ID
            expires_delta: 过期时间增量，如果不提供则使用默认值
            
        Returns:
            str: JWT令牌
        """
        if expires_delta is None:
            expires_delta = timedelta(minutes=self.refresh_token_expire_minutes)
        
        expire = datetime.now(UTC) + expires_delta
        
        to_encode = {
            "sub": user_id,
            "type": "refresh",
            "iat": datetime.now(UTC),
            "exp": expire,
            "jti": str(uuid.uuid4())
        }
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        验证JWT令牌
        
        Args:
            token: JWT令牌
            
        Returns:
            Dict[str, Any]: 解码后的载荷
            
        Raises:
            AuthenticationError: 令牌验证失败
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # 验证必要字段
            if "sub" not in payload or "type" not in payload:
                raise AuthenticationError("无效的令牌载荷")
            
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("令牌已过期")
        except jwt.InvalidSignatureError:
            raise AuthenticationError("无效的令牌签名")
        except jwt.DecodeError:
            raise AuthenticationError("令牌格式错误")
        except Exception as e:
            logger.error(f"令牌验证失败: {str(e)}")
            raise AuthenticationError(f"令牌验证失败: {str(e)}")
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """
        使用刷新令牌创建新的访问令牌
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            str: 新的访问令牌
            
        Raises:
            AuthenticationError: 刷新令牌无效
        """
        payload = self.verify_token(refresh_token)
        
        # 检查是否为刷新令牌
        if payload.get("type") != "refresh":
            raise AuthenticationError("无效的刷新令牌")
        
        # 创建新的访问令牌
        user_id = payload["sub"]
        return self.create_access_token(user_id)
    
    def get_user_id_from_token(self, token: str) -> str:
        """
        从令牌中获取用户ID
        
        Args:
            token: JWT令牌
            
        Returns:
            str: 用户ID
            
        Raises:
            AuthenticationError: 令牌验证失败
        """
        payload = self.verify_token(token)
        return payload["sub"]


# 为兼容性保留旧的函数接口
def create_access_token(
    data: Dict[str, Any],
    secret_key: str = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建访问令牌
    
    Args:
        data: 包含用户信息的字典
        secret_key: JWT密钥
        expires_delta: 过期时间增量，如果不提供则使用默认值
        
    Returns:
        str: JWT令牌
        
    Raises:
        ConfigurationError: 配置错误，比如密钥未设置
    """
    if not secret_key:
        secret_key = os.environ.get("JWT_SECRET_KEY")
        if not secret_key:
            raise ConfigurationError("JWT密钥未配置")
    
    if expires_delta is None:
        expires_delta = timedelta(minutes=int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
    
    jwt_security = JWTSecurity(secret_key=secret_key)
    
    user_id = data.get("sub")
    if not user_id:
        raise ValueError("缺少用户ID")
    
    # 移除数据中的sub字段
    data_copy = data.copy()
    if "sub" in data_copy:
        del data_copy["sub"]
    
    return jwt_security.create_access_token(user_id, expires_delta, data_copy)


def create_refresh_token(
    data: Dict[str, Any],
    secret_key: str = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建刷新令牌
    
    Args:
        data: 包含用户信息的字典
        secret_key: JWT密钥
        expires_delta: 过期时间增量，如果不提供则使用默认值
        
    Returns:
        str: JWT令牌
        
    Raises:
        ConfigurationError: 配置错误，比如密钥未设置
    """
    if not secret_key:
        secret_key = os.environ.get("JWT_SECRET_KEY")
        if not secret_key:
            raise ConfigurationError("JWT密钥未配置")
    
    if expires_delta is None:
        expires_delta = timedelta(minutes=int(os.environ.get("REFRESH_TOKEN_EXPIRE_MINUTES", 10080)))
    
    jwt_security = JWTSecurity(secret_key=secret_key)
    
    user_id = data.get("sub")
    if not user_id:
        raise ValueError("缺少用户ID")
    
    return jwt_security.create_refresh_token(user_id, expires_delta)


def decode_token(token: str, secret_key: str = None) -> Dict[str, Any]:
    """
    解码JWT令牌
    
    Args:
        token: JWT令牌
        secret_key: JWT密钥
        
    Returns:
        Dict[str, Any]: 解码后的载荷
        
    Raises:
        InvalidTokenError: 令牌验证失败
        ConfigurationError: 配置错误，比如密钥未设置
    """
    if not secret_key:
        secret_key = os.environ.get("JWT_SECRET_KEY")
        if not secret_key:
            raise ConfigurationError("JWT密钥未配置")
    
    jwt_security = JWTSecurity(secret_key=secret_key)
    
    try:
        return jwt_security.verify_token(token)
    except AuthenticationError as e:
        # 转换异常类型以兼容旧代码
        from internal.model.errors import InvalidTokenError
        raise InvalidTokenError(str(e))


def create_token_pair(
    user_id: str,
    username: str,
    roles: list = None,
    permissions: list = None,
    secret_key: str = None,
    access_token_expires: timedelta = None,
    refresh_token_expires: timedelta = None
) -> Tuple[str, str, int]:
    """
    创建访问令牌和刷新令牌对
    
    Args:
        user_id: 用户ID
        username: 用户名
        roles: 用户角色列表
        permissions: 用户权限列表
        secret_key: JWT密钥
        access_token_expires: 访问令牌过期时间
        refresh_token_expires: 刷新令牌过期时间
        
    Returns:
        Tuple[str, str, int]: (访问令牌, 刷新令牌, 访问令牌过期时间(秒))
    """
    if not secret_key:
        secret_key = os.environ.get("JWT_SECRET_KEY")
        if not secret_key:
            raise ConfigurationError("JWT密钥未配置")
    
    if access_token_expires is None:
        access_token_expires = timedelta(minutes=int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
    
    if refresh_token_expires is None:
        refresh_token_expires = timedelta(minutes=int(os.environ.get("REFRESH_TOKEN_EXPIRE_MINUTES", 10080)))
    
    jwt_security = JWTSecurity(
        secret_key=secret_key,
        access_token_expire_minutes=int(access_token_expires.total_seconds() / 60),
        refresh_token_expire_minutes=int(refresh_token_expires.total_seconds() / 60)
    )
    
    # 创建访问令牌，包含更多信息
    additional_data = {
        "username": username
    }
    
    if roles:
        additional_data["roles"] = roles
    
    if permissions:
        additional_data["permissions"] = permissions
    
    access_token = jwt_security.create_access_token(
        user_id=user_id,
        additional_data=additional_data
    )
    
    # 创建刷新令牌，只包含必要信息
    refresh_token = jwt_security.create_refresh_token(user_id=user_id)
    
    # 计算访问令牌过期时间(秒)
    expires_in = int(access_token_expires.total_seconds())
    
    return access_token, refresh_token, expires_in