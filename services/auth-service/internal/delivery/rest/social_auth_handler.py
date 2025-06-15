#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
社交登录API处理器

提供OAuth2.0社交登录的REST API端点。
"""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field

from ...service.social_auth_service import SocialAuthService, get_social_auth_service
from ...security.jwt_manager import get_current_user
from ...model.user import User
from ...exceptions import (
    AuthenticationError,
    ValidationError,
    ExternalServiceError
)

router = APIRouter(prefix="/api/v1/auth/social", tags=["社交登录"])


# 请求/响应模型
class AuthorizationUrlRequest(BaseModel):
    """获取授权URL请求"""
    provider: str = Field(..., description="OAuth提供商 (google/github/wechat)")
    redirect_uri: str = Field(..., description="回调URI")
    state: str = Field(None, description="状态参数")


class AuthorizationUrlResponse(BaseModel):
    """授权URL响应"""
    authorization_url: str = Field(..., description="授权URL")
    state: str = Field(..., description="状态参数")
    provider: str = Field(..., description="提供商")


class OAuthCallbackRequest(BaseModel):
    """OAuth回调请求"""
    provider: str = Field(..., description="OAuth提供商")
    code: str = Field(..., description="授权码")
    state: str = Field(..., description="状态参数")
    redirect_uri: str = Field(..., description="回调URI")


class SocialLoginResponse(BaseModel):
    """社交登录响应"""
    user: Dict[str, Any] = Field(..., description="用户信息")
    tokens: Dict[str, str] = Field(..., description="JWT令牌")
    provider: str = Field(..., description="登录提供商")


class LinkedAccountResponse(BaseModel):
    """已绑定账号响应"""
    provider: str = Field(..., description="提供商")
    provider_user_id: str = Field(..., description="提供商用户ID")
    linked_at: str = Field(..., description="绑定时间")
    last_login_at: str = Field(None, description="最后登录时间")
    user_info: Dict[str, Any] = Field(..., description="用户信息")


@router.post("/authorization-url", response_model=AuthorizationUrlResponse)
async def get_authorization_url(
    request: AuthorizationUrlRequest,
    social_auth_service: SocialAuthService = Depends(get_social_auth_service)
):
    """
    获取OAuth授权URL
    
    支持的提供商:
    - google: Google OAuth2.0
    - github: GitHub OAuth
    - wechat: 微信开放平台
    """
    try:
        result = await social_auth_service.get_authorization_url(
            provider=request.provider,
            redirect_uri=request.redirect_uri,
            state=request.state
        )
        
        return AuthorizationUrlResponse(**result)
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取授权URL失败: {str(e)}"
        )


@router.post("/callback", response_model=SocialLoginResponse)
async def oauth_callback(
    request: OAuthCallbackRequest,
    social_auth_service: SocialAuthService = Depends(get_social_auth_service)
):
    """
    处理OAuth回调
    
    完成OAuth授权流程，创建或登录用户账号。
    """
    try:
        result = await social_auth_service.handle_oauth_callback(
            provider=request.provider,
            code=request.code,
            state=request.state,
            redirect_uri=request.redirect_uri
        )
        
        return SocialLoginResponse(**result)
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth回调处理失败: {str(e)}"
        )


@router.get("/linked-accounts", response_model=List[LinkedAccountResponse])
async def get_linked_accounts(
    current_user: User = Depends(get_current_user),
    social_auth_service: SocialAuthService = Depends(get_social_auth_service)
):
    """
    获取当前用户已绑定的社交账号
    """
    try:
        accounts = await social_auth_service.get_linked_accounts(current_user.id)
        
        return [LinkedAccountResponse(**account) for account in accounts]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取绑定账号失败: {str(e)}"
        )


@router.delete("/unlink/{provider}")
async def unlink_social_account(
    provider: str,
    current_user: User = Depends(get_current_user),
    social_auth_service: SocialAuthService = Depends(get_social_auth_service)
):
    """
    解除社交账号绑定
    
    注意: 如果用户没有设置密码且只绑定了一个社交账号，将无法解除绑定。
    """
    try:
        success = await social_auth_service.unlink_social_account(
            user_id=current_user.id,
            provider=provider
        )
        
        return {
            "success": success,
            "message": f"已成功解除{provider}账号绑定"
        }
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"解除绑定失败: {str(e)}"
        )


@router.get("/providers")
async def get_supported_providers():
    """
    获取支持的OAuth提供商列表
    """
    return {
        "providers": [
            {
                "name": "google",
                "display_name": "Google",
                "description": "使用Google账号登录",
                "icon": "google"
            },
            {
                "name": "github", 
                "display_name": "GitHub",
                "description": "使用GitHub账号登录",
                "icon": "github"
            },
            {
                "name": "wechat",
                "display_name": "微信",
                "description": "使用微信账号登录",
                "icon": "wechat"
            }
        ]
    }


# 便捷的GET端点用于直接重定向
@router.get("/login/{provider}")
async def social_login_redirect(
    provider: str,
    redirect_uri: str = Query(..., description="回调URI"),
    state: str = Query(None, description="状态参数"),
    social_auth_service: SocialAuthService = Depends(get_social_auth_service)
):
    """
    社交登录重定向端点
    
    直接返回重定向响应到OAuth提供商的授权页面。
    """
    try:
        result = await social_auth_service.get_authorization_url(
            provider=provider,
            redirect_uri=redirect_uri,
            state=state
        )
        
        from fastapi.responses import RedirectResponse
        return RedirectResponse(
            url=result['authorization_url'],
            status_code=status.HTTP_302_FOUND
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"社交登录重定向失败: {str(e)}"
        )