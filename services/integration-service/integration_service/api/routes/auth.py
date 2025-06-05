"""
认证相关的API路由
"""

import logging
from datetime import timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.security import (
    create_token_pair,
    verify_password,
    verify_refresh_token,
    Token,
    TokenData
)
from ...models.user import User
from ...services.user_service import UserService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["认证"])


class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求模型"""
    refresh_token: str


class LoginResponse(BaseModel):
    """登录响应模型"""
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    user_info: Dict[str, Any]


@router.post("/login", response_model=LoginResponse, summary="用户登录")
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
) -> LoginResponse:
    """
    用户登录接口
    
    - **username**: 用户名或邮箱
    - **password**: 密码
    """
    try:
        user_service = UserService(db)
        
        # 验证用户凭据
        user = user_service.authenticate_user(login_data.username, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户账户已被禁用"
            )
        
        # 创建令牌对
        token = create_token_pair(
            user_id=user.id,
            username=user.username,
            scopes=["read", "write"]
        )
        
        # 用户信息
        user_info = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "profile": user.profile
        }
        
        logger.info(f"用户 {user.username} 登录成功")
        
        return LoginResponse(
            access_token=token.access_token,
            token_type=token.token_type,
            expires_in=token.expires_in,
            refresh_token=token.refresh_token,
            user_info=user_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"登录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录过程中发生错误"
        )


@router.post("/token", response_model=Token, summary="OAuth2令牌获取")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Token:
    """
    OAuth2兼容的令牌获取接口
    
    - **username**: 用户名
    - **password**: 密码
    """
    try:
        user_service = UserService(db)
        
        user = user_service.authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户账户已被禁用"
            )
        
        # 处理作用域
        scopes = form_data.scopes if form_data.scopes else ["read", "write"]
        
        token = create_token_pair(
            user_id=user.id,
            username=user.username,
            scopes=scopes
        )
        
        logger.info(f"用户 {user.username} 通过OAuth2获取令牌成功")
        
        return token
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OAuth2令牌获取失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="令牌获取过程中发生错误"
        )


@router.post("/refresh", response_model=Token, summary="刷新访问令牌")
async def refresh_access_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
) -> Token:
    """
    使用刷新令牌获取新的访问令牌
    
    - **refresh_token**: 刷新令牌
    """
    try:
        # 验证刷新令牌
        token_data = verify_refresh_token(refresh_data.refresh_token)
        
        # 验证用户是否仍然存在且活跃
        user_service = UserService(db)
        user = user_service.get_user_by_id(token_data.user_id)
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在或已被禁用"
            )
        
        # 创建新的令牌对
        new_token = create_token_pair(
            user_id=user.id,
            username=user.username,
            scopes=["read", "write"]
        )
        
        logger.info(f"用户 {user.username} 刷新令牌成功")
        
        return new_token
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"刷新令牌失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="刷新令牌过程中发生错误"
        )


@router.post("/logout", summary="用户登出")
async def logout(
    current_user: TokenData = Depends(verify_refresh_token)
) -> Dict[str, str]:
    """
    用户登出接口
    
    注意：在无状态JWT系统中，登出主要是客户端删除令牌
    服务端可以维护黑名单来实现真正的令牌撤销
    """
    try:
        # 这里可以将令牌加入黑名单
        # 为了简化，这里只是记录日志
        logger.info(f"用户 {current_user.username} 登出")
        
        return {"message": "登出成功"}
        
    except Exception as e:
        logger.error(f"登出失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登出过程中发生错误"
        )


@router.get("/me", summary="获取当前用户信息")
async def get_current_user_info(
    current_user: TokenData = Depends(verify_refresh_token),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取当前登录用户的详细信息
    """
    try:
        user_service = UserService(db)
        user = user_service.get_user_by_id(current_user.user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "is_active": user.is_active,
            "profile": user.profile,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户信息失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户信息过程中发生错误"
        ) 