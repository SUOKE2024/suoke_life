#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OAuth控制器模块

提供OAuth相关的REST API处理。
"""
import logging
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from internal.db.session import get_session
from internal.service.oauth_service import OAuthService
from internal.service.auth_service import get_current_user
from internal.model.errors import ValidationError, AuthServiceError

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/v1/oauth", tags=["oauth"])


def get_oauth_service(request: Request) -> OAuthService:
    """获取OAuth服务依赖"""
    return request.app.state.oauth_service


@router.get("/providers")
async def get_oauth_providers(
    oauth_service: OAuthService = Depends(get_oauth_service),
) -> Dict[str, List[str]]:
    """
    获取所有可用的OAuth提供商
    
    Returns:
        Dict[str, List[str]]: 可用OAuth提供商列表
    """
    providers = list(oauth_service.providers.keys())
    return {"providers": providers}


@router.get("/{provider}/authorize")
async def get_oauth_authorize_url(
    provider: str,
    redirect_uri: Optional[str] = None,
    oauth_service: OAuthService = Depends(get_oauth_service),
) -> Dict[str, str]:
    """
    获取OAuth授权URL
    
    Args:
        provider: OAuth提供商名称
        redirect_uri: 可选的重定向URI
        
    Returns:
        Dict[str, str]: 授权URL
    """
    try:
        # 获取提供商
        provider_instance = oauth_service.get_provider(provider)
        
        # 如果提供了重定向URI，则使用它替换默认的
        if redirect_uri:
            provider_instance.redirect_uri = redirect_uri
            
        # 获取授权URL
        authorize_url = provider_instance.get_authorize_url()
        
        return {"authorize_url": authorize_url}
    except ValidationError as e:
        logger.warning(f"无效的OAuth提供商: {provider}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的OAuth提供商: {provider}"
        )
    except Exception as e:
        logger.error(f"获取授权URL错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取授权URL失败"
        )


@router.get("/{provider}/callback")
async def oauth_callback(
    provider: str,
    code: str,
    error: Optional[str] = None,
    state: Optional[str] = None,
    oauth_service: OAuthService = Depends(get_oauth_service),
    session: AsyncSession = Depends(get_session),
    response: Response = None,
    redirect_to: Optional[str] = None,
) -> Dict[str, Any]:
    """
    处理OAuth回调
    
    Args:
        provider: OAuth提供商名称
        code: 授权码
        error: 错误信息(如果有)
        state: 状态值(用于防止CSRF)
        redirect_to: 登录成功后的重定向URL
        
    Returns:
        Dict[str, Any]: 用户信息和令牌
    """
    # 检查是否有错误
    if error:
        logger.error(f"OAuth回调错误: {error}, 提供商: {provider}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth认证错误: {error}"
        )
    
    try:
        # 处理OAuth回调
        user, tokens = await oauth_service.handle_callback(
            provider_name=provider,
            code=code,
            session=session
        )
        
        # 如果提供了重定向URL，则重定向
        if redirect_to:
            # 将令牌添加到重定向URL
            separator = "?" if "?" not in redirect_to else "&"
            redirect_url = f"{redirect_to}{separator}access_token={tokens.access_token}&refresh_token={tokens.refresh_token}"
            return RedirectResponse(url=redirect_url)
        
        # 否则返回用户信息和令牌
        return {
            "user_id": str(user.id),
            "username": user.username,
            "email": user.email,
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "token_type": tokens.token_type,
            "expires_in": tokens.expires_in
        }
    except ValidationError as e:
        logger.warning(f"OAuth验证错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except AuthServiceError as e:
        logger.error(f"OAuth服务错误: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"OAuth回调处理错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth认证处理失败"
        )


@router.get("/accounts")
async def get_oauth_accounts(
    user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Dict[str, List[Dict[str, Any]]]:
    """
    获取当前用户的OAuth关联账号
    
    Returns:
        Dict[str, List[Dict[str, Any]]]: 关联的OAuth账号
    """
    try:
        from internal.repository.user_repository import UserRepository
        
        # 获取用户仓储
        user_repo = UserRepository(session)
        
        # 获取用户的OAuth账号
        oauth_accounts = await user_repo.get_user_oauth_accounts(str(user.id))
        
        # 格式化响应
        accounts = []
        for account in oauth_accounts:
            accounts.append({
                "provider": account.provider,
                "provider_user_id": account.provider_user_id,
                "linked_at": account.created_at.isoformat()
            })
            
        return {"accounts": accounts}
    except Exception as e:
        logger.error(f"获取OAuth账号错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取OAuth账号失败"
        )


@router.delete("/{provider}/unlink")
async def unlink_oauth_account(
    provider: str,
    user = Depends(get_current_user),
    oauth_service: OAuthService = Depends(get_oauth_service),
    session: AsyncSession = Depends(get_session),
) -> Dict[str, bool]:
    """
    解除OAuth账号关联
    
    Args:
        provider: OAuth提供商名称
        
    Returns:
        Dict[str, bool]: 操作结果
    """
    try:
        # 解除关联
        success = await oauth_service.unlink_oauth(
            user_id=str(user.id),
            provider_name=provider,
            session=session
        )
        
        return {"success": success}
    except ValidationError as e:
        logger.warning(f"解除OAuth关联验证错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"解除OAuth关联错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="解除OAuth关联失败"
        ) 