#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
认证服务模块

提供用户认证、令牌处理和授权管理功能。
"""
import logging
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from internal.model.user import User
from internal.config.settings import get_settings
from internal.repository.user_repository import UserRepository
from internal.security.password import PasswordManager
from internal.security.jwt_manager import get_jwt_key_manager
from internal.database.connection_manager import get_connection_manager
from internal.database.query_optimizer import get_query_optimizer
from internal.cache.redis_cache import get_redis_cache
from internal.async_tasks.task_manager import get_task_manager
from internal.validators import InputValidator, LoginValidator, sanitize_log_data
from internal.exceptions import (
    AuthenticationError, 
    TokenError, 
    TokenExpiredError, 
    TokenInvalidError,
    UserNotFoundError,
    UserInactiveError,
    PasswordInvalidError,
    ValidationError,
    DatabaseError
)

# 获取配置和服务实例
settings = get_settings()
jwt_key_manager = get_jwt_key_manager()
db_manager = get_connection_manager()
query_optimizer = get_query_optimizer()
cache = get_redis_cache()
task_manager = get_task_manager()

# 配置OAuth2密码授权
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

# 日志配置
logger = logging.getLogger(__name__)


async def authenticate_user(username: str, password: str) -> User:
    """
    认证用户
    
    Args:
        username: 用户名或邮箱
        password: 密码
        
    Returns:
        User: 认证成功的用户对象
        
    Raises:
        UserNotFoundError: 用户不存在
        UserInactiveError: 用户账户已禁用
        PasswordInvalidError: 密码错误
        DatabaseError: 数据库操作失败
    """
    # 输入验证和清理
    login_data = LoginValidator(username=username, password=password)
    cleaned_username = login_data.username
    cleaned_password = login_data.password
    
    # 脱敏用户名用于日志记录
    masked_username = sanitize_log_data(cleaned_username, max_length=50)
    
    try:
        user_repo = UserRepository(db_manager)
        password_manager = PasswordManager()
        
        logger.info(f"开始用户认证: {masked_username}")
        
        # 尝试从缓存获取用户信息
        cache_key = f"user_auth:{cleaned_username}"
        cached_user = await cache.get(cache_key)
        
        if cached_user:
            logger.debug(f"用户信息缓存命中: {masked_username}")
            user = User(**cached_user)
        else:
            # 使用优化查询从数据库获取用户
            if "@" in cleaned_username:
                result = await query_optimizer.execute_optimized_query(
                    "get_user_by_email", cleaned_username
                )
            else:
                result = await query_optimizer.execute_optimized_query(
                    "get_user_by_username", cleaned_username
                )
            
            if not result:
                logger.warning(f"用户不存在: {masked_username}")
                raise UserNotFoundError("用户名或密码错误")
            
            user_data = dict(result[0])
            user = User(**user_data)
            
            # 缓存用户信息（5分钟）
            await cache.set(cache_key, user_data, ttl=300)
        
        # 检查用户状态
        if not user.is_active:
            logger.warning(f"用户账户已禁用: {masked_username}")
            raise UserInactiveError("用户账户已禁用")
        
        # 验证密码
        if not password_manager.verify_password(cleaned_password, user.password_hash):
            logger.warning(f"密码验证失败: {masked_username}")
            
            # 异步记录登录失败
            await task_manager.log_async(
                "WARNING",
                f"登录失败: {masked_username}",
                {"ip": "unknown", "user_agent": "unknown"}
            )
            
            raise PasswordInvalidError("用户名或密码错误")
        
        logger.info(f"用户认证成功: {masked_username}")
        
        # 异步记录登录成功
        await task_manager.log_async(
            "INFO",
            f"登录成功: {masked_username}",
            {"user_id": str(user.id), "ip": "unknown"}
        )
        
        return user
        
    except (UserNotFoundError, UserInactiveError, PasswordInvalidError):
        # 重新抛出业务异常
        raise
    except Exception as e:
        logger.error(f"用户认证过程中发生错误: {str(e)}")
        raise DatabaseError("认证服务暂时不可用")


async def create_tokens(user: User) -> Dict[str, Any]:
    """
    为用户创建访问令牌和刷新令牌
    
    Args:
        user: 用户对象
    
    Returns:
        Dict[str, Any]: 包含令牌的字典
    
    Raises:
        TokenError: 令牌创建失败
    """
    logger.info(f"为用户创建令牌: {user.id}")
    
    try:
        # 创建访问令牌
        access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
        access_token = create_jwt_token(
            data={
                "sub": str(user.id), 
                "username": user.username, 
                "email": user.email,
                "type": "access",
                "iat": datetime.utcnow(),
                "iss": "suoke-auth-service"
            },
            expires_delta=access_token_expires
        )
        
        # 创建刷新令牌
        refresh_token_expires = timedelta(days=settings.jwt_refresh_token_expire_days)
        refresh_token = create_jwt_token(
            data={
                "sub": str(user.id), 
                "type": "refresh",
                "iat": datetime.utcnow(),
                "iss": "suoke-auth-service",
                "jti": secrets.token_urlsafe(32)  # JWT ID for revocation
            },
            expires_delta=refresh_token_expires
        )
        
        # 返回令牌信息
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.jwt_access_token_expire_minutes * 60,
            "refresh_expires_in": settings.jwt_refresh_token_expire_days * 24 * 60 * 60,
            "user_id": str(user.id),
            "username": user.username
        }
        
    except (jwt.InvalidKeyError, jwt.InvalidAlgorithmError) as e:
        logger.error(f"JWT配置错误: {str(e)}")
        raise TokenError("令牌配置错误")
    except Exception as e:
        logger.error(f"创建令牌失败: {str(e)}")
        raise TokenError("令牌创建失败")


def create_jwt_token(data: Dict[str, Any], expires_delta: timedelta) -> str:
    """
    创建JWT令牌
    
    Args:
        data: 令牌数据
        expires_delta: 有效期
    
    Returns:
        str: JWT令牌
    
    Raises:
        TokenError: 令牌创建失败
    """
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
        
        # 使用配置中的密钥和算法
        encoded_jwt = jwt.encode(
            to_encode, 
            jwt_key_manager.get_private_key(), 
            algorithm=settings.jwt_algorithm
        )
        return encoded_jwt
        
    except (jwt.InvalidKeyError, jwt.InvalidAlgorithmError) as e:
        logger.error(f"JWT配置错误: {str(e)}")
        raise TokenError("JWT配置错误")
    except Exception as e:
        logger.error(f"JWT令牌编码失败: {str(e)}")
        raise TokenError("JWT令牌创建失败")


async def refresh_tokens(
    refresh_token: str,
    user_repo: UserRepository
) -> Dict[str, Any]:
    """
    使用刷新令牌获取新的访问令牌
    
    Args:
        refresh_token: 刷新令牌
        user_repo: 用户仓储
    
    Returns:
        Dict[str, Any]: 包含新令牌的字典
    
    Raises:
        TokenError: 刷新令牌无效
    """
    logger.info("使用刷新令牌获取新的访问令牌")
    
    try:
        # 验证刷新令牌
        payload = jwt.decode(
            refresh_token, 
            jwt_key_manager.get_public_key(), 
            algorithms=[settings.jwt_algorithm]
        )
        user_id = payload.get("sub")
        token_type = payload.get("type")
        
        if user_id is None or token_type != "refresh":
            raise TokenInvalidError("无效的刷新令牌类型")
        
        # 从数据库获取用户
        user = await user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise UserNotFoundError("用户不存在或已禁用")
        
        # 创建新令牌
        return await create_tokens(user)
        
    except jwt.ExpiredSignatureError:
        logger.warning("刷新令牌已过期")
        raise TokenExpiredError("刷新令牌已过期")
    except jwt.InvalidTokenError as e:
        logger.warning(f"刷新令牌无效: {str(e)}")
        raise TokenInvalidError("无效的刷新令牌")
    except (TokenInvalidError, TokenExpiredError, UserNotFoundError):
        # 重新抛出业务异常
        raise
    except Exception as e:
        logger.error(f"刷新令牌处理失败: {str(e)}")
        raise TokenError("刷新令牌处理失败")


async def logout(user: User, token_repo=None) -> None:
    """
    用户登出，使当前令牌失效
    
    Args:
        user: 用户对象
        token_repo: 令牌仓储（可选）
    """
    logger.info(f"用户登出: {user.id}")
    
    try:
        # 如果有令牌仓储，将令牌加入黑名单
        if token_repo:
            await token_repo.revoke_user_tokens(user.id)
        
        # 记录登出事件
        logger.info(f"用户 {user.id} 成功登出")
        
    except Exception as e:
        logger.error(f"用户登出失败: {str(e)}")
        # 登出失败不应该抛出异常，只记录日志


async def verify_token(token: str, user_repo: UserRepository) -> User:
    """
    验证访问令牌有效性
    
    Args:
        token: 访问令牌
        user_repo: 用户仓储
    
    Returns:
        User: 用户对象
    
    Raises:
        TokenError: 令牌无效
    """
    logger.debug("验证访问令牌")
    
    try:
        # 验证令牌
        payload = jwt.decode(
            token, 
            jwt_key_manager.get_public_key(), 
            algorithms=[settings.jwt_algorithm]
        )
        user_id = payload.get("sub")
        token_type = payload.get("type")
        
        if user_id is None or token_type != "access":
            raise TokenError("无效的访问令牌类型")
        
        # 从数据库获取用户
        user = await user_repo.get_by_id(user_id)
        if not user:
            raise TokenError("用户不存在")
        
        if not user.is_active:
            raise TokenError("用户账户已禁用")
        
        return user
        
    except jwt.ExpiredSignatureError:
        logger.debug("访问令牌已过期")
        raise TokenError("访问令牌已过期")
    except jwt.InvalidTokenError as e:
        logger.warning(f"访问令牌无效: {str(e)}")
        raise TokenError("无效的访问令牌")
    except Exception as e:
        logger.error(f"访问令牌验证失败: {str(e)}")
        raise TokenError("访问令牌验证失败")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends()
) -> User:
    """
    从请求获取当前用户
    
    Args:
        token: 访问令牌
        user_repo: 用户仓储
    
    Returns:
        User: 当前用户
    
    Raises:
        HTTPException: 认证失败
    """
    try:
        user = await verify_token(token, user_repo)
        return user
    except TokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"获取当前用户失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器内部错误",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def send_password_reset(
    email: str, 
    user_repo: UserRepository,
    email_service
) -> bool:
    """
    发送密码重置邮件
    
    Args:
        email: 用户邮箱
        user_repo: 用户仓储
        email_service: 邮件服务
        
    Returns:
        bool: 是否发送成功
        
    Raises:
        ValueError: 用户不存在
    """
    logger.info(f"发送密码重置邮件: {email}")
    
    try:
        # 查找用户
        user = await user_repo.get_by_email(email)
        if not user:
            # 为了安全，不暴露用户是否存在
            logger.warning(f"尝试为不存在的邮箱发送重置邮件: {email}")
            return True  # 返回成功，但实际不发送
        
        # 生成重置令牌
        reset_token = secrets.token_urlsafe(32)
        reset_expires = datetime.utcnow() + timedelta(hours=1)
        
        # 保存重置令牌到数据库
        await user_repo.save_password_reset_token(user.id, reset_token, reset_expires)
        
        # 发送重置邮件
        reset_url = f"{settings.frontend_url}/reset-password?token={reset_token}"
        await email_service.send_password_reset_email(
            email=email,
            username=user.username,
            reset_url=reset_url,
            reset_token=reset_token
        )
        
        logger.info(f"密码重置邮件发送成功: {email}")
        return True
        
    except Exception as e:
        logger.error(f"发送密码重置邮件失败: {str(e)}")
        return False


async def reset_password(
    token: str, 
    new_password: str,
    user_repo: UserRepository,
    password_manager: PasswordManager
) -> bool:
    """
    重置密码
    
    Args:
        token: 重置令牌
        new_password: 新密码
        user_repo: 用户仓储
        password_manager: 密码管理器
        
    Returns:
        bool: 是否重置成功
        
    Raises:
        ValueError: 重置令牌无效或密码不符合要求
    """
    logger.info("重置密码")
    
    try:
        # 验证重置令牌
        user = await user_repo.get_by_reset_token(token)
        if not user:
            raise ValueError("无效的重置令牌")
        
        # 检查令牌是否过期
        if user.reset_token_expires and user.reset_token_expires < datetime.utcnow():
            raise ValueError("重置令牌已过期")
        
        # 验证新密码强度
        if not password_manager.validate_password_strength(new_password):
            raise ValueError("密码强度不符合要求")
        
        # 更新密码
        new_password_hash = password_manager.hash_password(new_password)
        await user_repo.update_password(user.id, new_password_hash)
        
        # 清除重置令牌
        await user_repo.clear_password_reset_token(user.id)
        
        logger.info(f"用户 {user.id} 密码重置成功")
        return True
        
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"密码重置失败: {str(e)}")
        raise ValueError("密码重置失败")


async def setup_mfa(user: User, mfa_type: str, mfa_service) -> Dict[str, Any]:
    """
    设置多因素认证
    
    Args:
        user: 用户对象
        mfa_type: 多因素认证类型（totp, sms等）
        mfa_service: MFA服务
        
    Returns:
        Dict[str, Any]: 设置信息
        
    Raises:
        ValueError: 不支持的MFA类型
    """
    logger.info(f"为用户{user.id}设置{mfa_type}多因素认证")
    
    try:
        if mfa_type == "totp":
            return await mfa_service.setup_totp(user.id)
        elif mfa_type == "sms":
            return await mfa_service.setup_sms(user.id)
        elif mfa_type == "email":
            return await mfa_service.setup_email(user.id)
        else:
            raise ValueError(f"不支持的MFA类型: {mfa_type}")
            
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"设置MFA失败: {str(e)}")
        raise ValueError("设置MFA失败")


async def verify_mfa(user: User, code: str, mfa_service) -> bool:
    """
    验证多因素认证代码
    
    Args:
        user: 用户对象
        code: 验证码
        mfa_service: MFA服务
        
    Returns:
        bool: 是否验证成功
    """
    logger.info(f"验证用户{user.id}的多因素认证代码")
    
    try:
        return await mfa_service.verify_mfa(user.id, code)
    except Exception as e:
        logger.error(f"MFA验证失败: {str(e)}")
        return False


async def disable_mfa(user: User, mfa_service) -> bool:
    """
    禁用多因素认证
    
    Args:
        user: 用户对象
        mfa_service: MFA服务
        
    Returns:
        bool: 是否禁用成功
    """
    logger.info(f"禁用用户{user.id}的多因素认证")
    
    try:
        await mfa_service.disable_mfa(user.id)
        return True
    except Exception as e:
        logger.error(f"禁用MFA失败: {str(e)}")
        return False 