"""OAuth第三方登录API端点"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from auth_service.database import get_db
from auth_service.core.oauth import OAuthManager, OAuthProvider
from auth_service.core.auth import AuthManager
from auth_service.models.user import User
from auth_service.schemas.auth import TokenResponse

router = APIRouter()


class OAuthLoginRequest(BaseModel):
    """OAuth登录请求模型"""
    provider: str = Field(..., description="OAuth提供商")
    redirect_uri: Optional[str] = Field(None, description="重定向URI")
    state: Optional[str] = Field(None, description="状态参数")


class OAuthCallbackRequest(BaseModel):
    """OAuth回调请求模型"""
    provider: str = Field(..., description="OAuth提供商")
    code: str = Field(..., description="授权码")
    state: Optional[str] = Field(None, description="状态参数")


@router.get("/providers")
async def get_oauth_providers():
    """获取支持的OAuth提供商列表"""
    return {
        "providers": [
            {
                "name": "google",
                "display_name": "Google",
                "icon": "google",
                "enabled": True
            },
            {
                "name": "github",
                "display_name": "GitHub",
                "icon": "github",
                "enabled": True
            },
            {
                "name": "wechat",
                "display_name": "微信",
                "icon": "wechat",
                "enabled": True
            },
            {
                "name": "qq",
                "display_name": "QQ",
                "icon": "qq",
                "enabled": True
            },
            {
                "name": "weibo",
                "display_name": "微博",
                "icon": "weibo",
                "enabled": True
            }
        ]
    }


@router.get("/login/{provider}")
async def oauth_login(
    provider: str,
    redirect_uri: Optional[str] = Query(None, description="登录成功后的重定向URI"),
    state: Optional[str] = Query(None, description="状态参数"),
    oauth_manager: OAuthManager = Depends(lambda: OAuthManager())
):
    """发起OAuth登录"""
    try:
        # 验证提供商
        if not oauth_manager.is_provider_supported(provider):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的OAuth提供商: {provider}"
            )
        
        # 生成授权URL
        auth_url = oauth_manager.get_authorization_url(
            provider=provider,
            redirect_uri=redirect_uri,
            state=state
        )
        
        return {
            "authorization_url": auth_url,
            "provider": provider,
            "state": state
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成OAuth授权URL失败: {str(e)}"
        )


@router.post("/callback/{provider}", response_model=TokenResponse)
async def oauth_callback(
    provider: str,
    code: str = Query(..., description="授权码"),
    state: Optional[str] = Query(None, description="状态参数"),
    db: AsyncSession = Depends(get_db),
    oauth_manager: OAuthManager = Depends(lambda: OAuthManager()),
    auth_manager: AuthManager = Depends(lambda: AuthManager())
):
    """处理OAuth回调"""
    try:
        # 验证提供商
        if not oauth_manager.is_provider_supported(provider):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的OAuth提供商: {provider}"
            )
        
        # 交换访问令牌
        access_token = await oauth_manager.exchange_code_for_token(
            provider=provider,
            code=code,
            state=state
        )
        
        # 获取用户信息
        user_info = await oauth_manager.get_user_info(provider, access_token)
        
        # 查找或创建用户
        user = await find_or_create_oauth_user(db, provider, user_info)
        
        # 生成JWT令牌
        tokens = auth_manager.create_tokens(user)
        
        # 记录登录
        await auth_manager.record_login(db, user.user_id, "oauth", {
            "provider": provider,
            "oauth_user_id": user_info.get("id"),
            "ip_address": "unknown"  # 在实际实现中应该获取真实IP
        })
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer",
            expires_in=tokens["expires_in"],
            user_info={
                "user_id": str(user.user_id),
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "avatar_url": user.avatar_url,
                "is_verified": user.is_verified
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth回调处理失败: {str(e)}"
        )


@router.post("/bind/{provider}")
async def bind_oauth_account(
    provider: str,
    code: str = Query(..., description="授权码"),
    current_user: User = Depends(lambda: get_current_user()),
    db: AsyncSession = Depends(get_db),
    oauth_manager: OAuthManager = Depends(lambda: OAuthManager())
):
    """绑定OAuth账户到现有用户"""
    try:
        # 验证提供商
        if not oauth_manager.is_provider_supported(provider):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的OAuth提供商: {provider}"
            )
        
        # 交换访问令牌
        access_token = await oauth_manager.exchange_code_for_token(
            provider=provider,
            code=code
        )
        
        # 获取用户信息
        user_info = await oauth_manager.get_user_info(provider, access_token)
        
        # 检查OAuth账户是否已被其他用户绑定
        existing_binding = await get_oauth_binding(db, provider, user_info.get("id"))
        if existing_binding and existing_binding.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该OAuth账户已被其他用户绑定"
            )
        
        # 创建或更新绑定
        await create_or_update_oauth_binding(
            db, current_user.user_id, provider, user_info, access_token
        )
        
        return {
            "message": f"成功绑定{provider}账户",
            "provider": provider,
            "oauth_user_id": user_info.get("id"),
            "oauth_username": user_info.get("username") or user_info.get("name")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"绑定OAuth账户失败: {str(e)}"
        )


@router.delete("/unbind/{provider}")
async def unbind_oauth_account(
    provider: str,
    current_user: User = Depends(lambda: get_current_user()),
    db: AsyncSession = Depends(get_db)
):
    """解绑OAuth账户"""
    try:
        # 检查绑定是否存在
        binding = await get_oauth_binding_by_user(db, current_user.user_id, provider)
        if not binding:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"未找到{provider}账户绑定"
            )
        
        # 删除绑定
        await delete_oauth_binding(db, binding.binding_id)
        
        return {
            "message": f"成功解绑{provider}账户",
            "provider": provider
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"解绑OAuth账户失败: {str(e)}"
        )


@router.get("/bindings")
async def get_oauth_bindings(
    current_user: User = Depends(lambda: get_current_user()),
    db: AsyncSession = Depends(get_db)
):
    """获取用户的OAuth绑定列表"""
    try:
        bindings = await get_user_oauth_bindings(db, current_user.user_id)
        
        return {
            "user_id": str(current_user.user_id),
            "bindings": [
                {
                    "provider": binding.provider,
                    "oauth_user_id": binding.oauth_user_id,
                    "oauth_username": binding.oauth_username,
                    "bound_at": binding.created_at.isoformat(),
                    "last_used": binding.last_used_at.isoformat() if binding.last_used_at else None
                }
                for binding in bindings
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取OAuth绑定失败: {str(e)}"
        )


# 辅助函数（实际实现中应该在service层）
async def find_or_create_oauth_user(db: AsyncSession, provider: str, user_info: Dict[str, Any]) -> User:
    """查找或创建OAuth用户"""
    # 这里应该实现实际的用户查找和创建逻辑
    # 模拟实现
    from auth_service.models.user import User
    
    # 尝试通过邮箱查找现有用户
    email = user_info.get("email")
    if email:
        # 查找现有用户的逻辑
        pass
    
    # 如果没有找到，创建新用户
    user = User(
        username=user_info.get("username") or f"{provider}_{user_info.get('id')}",
        email=email,
        full_name=user_info.get("name"),
        avatar_url=user_info.get("avatar_url"),
        is_verified=True,  # OAuth用户默认已验证
        oauth_provider=provider,
        oauth_user_id=str(user_info.get("id"))
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user


async def get_oauth_binding(db: AsyncSession, provider: str, oauth_user_id: str):
    """获取OAuth绑定"""
    # 实际实现中应该查询数据库
    return None


async def create_or_update_oauth_binding(
    db: AsyncSession, 
    user_id: str, 
    provider: str, 
    user_info: Dict[str, Any], 
    access_token: str
):
    """创建或更新OAuth绑定"""
    # 实际实现中应该操作数据库
    pass


async def get_oauth_binding_by_user(db: AsyncSession, user_id: str, provider: str):
    """根据用户ID和提供商获取OAuth绑定"""
    # 实际实现中应该查询数据库
    return None


async def delete_oauth_binding(db: AsyncSession, binding_id: str):
    """删除OAuth绑定"""
    # 实际实现中应该操作数据库
    pass


async def get_user_oauth_bindings(db: AsyncSession, user_id: str):
    """获取用户的所有OAuth绑定"""
    # 实际实现中应该查询数据库
    return []


def get_current_user():
    """获取当前用户（占位符）"""
    # 实际实现中应该从JWT令牌解析用户信息
    pass 