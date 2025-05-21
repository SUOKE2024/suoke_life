#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JWT令牌处理工具

提供JWT令牌的生成、验证和解码功能
"""
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple

import jwt
from jwt.exceptions import PyJWTError

from internal.model.errors import InvalidTokenError, ConfigurationError


logger = logging.getLogger(__name__)


def create_access_token(
    data: Dict[str, Any],
    secret_key: str,
    algorithm: str = "HS256",
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建JWT访问令牌
    
    Args:
        data: 令牌载荷数据
        secret_key: 密钥
        algorithm: 算法，默认HS256
        expires_delta: 过期时间增量，默认30分钟
        
    Returns:
        str: JWT令牌
    """
    if not secret_key:
        raise ConfigurationError("JWT密钥未配置")
    
    to_encode = data.copy()
    
    # 添加令牌ID
    to_encode.update({"jti": str(uuid.uuid4())})
    
    # 设置发行时间
    now = datetime.utcnow()
    to_encode.update({"iat": now})
    
    # 设置过期时间
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=30)
    
    to_encode.update({"exp": expire})
    
    # 生成令牌
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any],
    secret_key: str,
    algorithm: str = "HS256",
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建JWT刷新令牌
    
    Args:
        data: 令牌载荷数据
        secret_key: 密钥
        algorithm: 算法，默认HS256
        expires_delta: 过期时间增量，默认7天
        
    Returns:
        str: JWT刷新令牌
    """
    if not secret_key:
        raise ConfigurationError("JWT密钥未配置")
    
    to_encode = data.copy()
    
    # 添加令牌ID
    to_encode.update({"jti": str(uuid.uuid4())})
    
    # 添加令牌类型
    to_encode.update({"token_type": "refresh"})
    
    # 设置发行时间
    now = datetime.utcnow()
    to_encode.update({"iat": now})
    
    # 设置过期时间
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=7)
    
    to_encode.update({"exp": expire})
    
    # 生成令牌
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def decode_token(
    token: str, 
    secret_key: str, 
    algorithms: List[str] = ["HS256"]
) -> Dict[str, Any]:
    """
    解码并验证JWT令牌
    
    Args:
        token: JWT令牌
        secret_key: 密钥
        algorithms: 允许的算法列表，默认["HS256"]
        
    Returns:
        Dict: 解码后的令牌数据
        
    Raises:
        InvalidTokenError: 令牌无效或已过期
    """
    if not secret_key:
        raise ConfigurationError("JWT密钥未配置")
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=algorithms)
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("令牌已过期")
        raise InvalidTokenError("令牌已过期")
    except jwt.InvalidTokenError as e:
        logger.warning(f"无效令牌: {str(e)}")
        raise InvalidTokenError(f"无效令牌: {str(e)}")
    except Exception as e:
        logger.exception("解码令牌时发生未预期的错误")
        raise InvalidTokenError(f"令牌处理失败: {str(e)}")


def create_token_pair(
    user_id: str,
    username: str,
    roles: List[str],
    permissions: List[str],
    secret_key: str,
    algorithm: str = "HS256",
    access_token_expires: Optional[timedelta] = None,
    refresh_token_expires: Optional[timedelta] = None
) -> Tuple[str, str, int]:
    """
    创建访问令牌和刷新令牌对
    
    Args:
        user_id: 用户ID
        username: 用户名
        roles: 角色列表
        permissions: 权限列表
        secret_key: 密钥
        algorithm: 算法，默认HS256
        access_token_expires: 访问令牌过期时间增量
        refresh_token_expires: 刷新令牌过期时间增量
        
    Returns:
        Tuple[str, str, int]: (访问令牌, 刷新令牌, 访问令牌过期时间(秒))
    """
    # 计算访问令牌过期时间
    if access_token_expires is None:
        access_token_expires = timedelta(minutes=30)
    
    # 计算刷新令牌过期时间
    if refresh_token_expires is None:
        refresh_token_expires = timedelta(days=7)
    
    # 准备令牌数据
    token_data = {
        "sub": user_id,
        "username": username,
        "roles": roles,
        "permissions": permissions
    }
    
    # 创建访问令牌
    access_token = create_access_token(
        data=token_data,
        secret_key=secret_key,
        algorithm=algorithm,
        expires_delta=access_token_expires
    )
    
    # 创建刷新令牌 (只包含必要数据)
    refresh_data = {
        "sub": user_id,
        "username": username
    }
    refresh_token = create_refresh_token(
        data=refresh_data,
        secret_key=secret_key,
        algorithm=algorithm,
        expires_delta=refresh_token_expires
    )
    
    # 计算过期时间(秒)
    expires_in = int(access_token_expires.total_seconds())
    
    return access_token, refresh_token, expires_in