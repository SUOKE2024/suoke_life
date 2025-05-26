"""
Authentication API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from ...internal.model.user_integration import PlatformType, PlatformAuth
from ...internal.service.platform_service import PlatformService
from ...internal.service.dependencies import get_current_user, validate_platform_enabled

router = APIRouter(prefix="/auth", tags=["认证"])


@router.get("/platforms", summary="获取支持的平台列表")
async def get_supported_platforms(
    platform_service: PlatformService = Depends(lambda: PlatformService())
):
    """获取所有支持的第三方平台列表"""
    platforms = await platform_service.get_supported_platforms()
    return {
        "success": True,
        "data": platforms,
        "message": "获取平台列表成功"
    }


@router.get("/{platform}/url", summary="获取平台授权URL")
async def get_auth_url(
    platform: str,
    scopes: Optional[List[str]] = Query(None, description="权限范围"),
    user_id: str = Depends(get_current_user),
    _: str = Depends(validate_platform_enabled),
    platform_service: PlatformService = Depends(lambda: PlatformService())
):
    """获取指定平台的OAuth授权URL"""
    try:
        platform_type = PlatformType(platform)
        auth_url = await platform_service.get_auth_url(
            platform_type, user_id, scopes
        )
        
        return {
            "success": True,
            "data": {
                "auth_url": auth_url,
                "platform": platform,
                "user_id": user_id
            },
            "message": "获取授权URL成功"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取授权URL失败: {str(e)}")


@router.get("/{platform}/callback", summary="处理平台认证回调")
async def handle_auth_callback(
    platform: str,
    code: str = Query(..., description="授权码"),
    state: str = Query(..., description="状态参数"),
    user_id: str = Depends(get_current_user),
    _: str = Depends(validate_platform_enabled),
    platform_service: PlatformService = Depends(lambda: PlatformService())
):
    """处理第三方平台的OAuth认证回调"""
    try:
        platform_type = PlatformType(platform)
        platform_auth = await platform_service.handle_auth_callback(
            platform_type, code, state, user_id
        )
        
        return {
            "success": True,
            "data": platform_auth.dict(),
            "message": "认证成功"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"认证失败: {str(e)}")


@router.post("/{platform}/refresh", summary="刷新平台访问令牌")
async def refresh_platform_token(
    platform: str,
    user_id: str = Depends(get_current_user),
    _: str = Depends(validate_platform_enabled),
    platform_service: PlatformService = Depends(lambda: PlatformService())
):
    """刷新指定平台的访问令牌"""
    try:
        platform_type = PlatformType(platform)
        success = await platform_service.refresh_platform_token(user_id, platform_type)
        
        if success:
            return {
                "success": True,
                "message": "令牌刷新成功"
            }
        else:
            raise HTTPException(status_code=400, detail="令牌刷新失败")
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"令牌刷新失败: {str(e)}")


@router.delete("/{platform}/revoke", summary="撤销平台访问权限")
async def revoke_platform_access(
    platform: str,
    user_id: str = Depends(get_current_user),
    _: str = Depends(validate_platform_enabled),
    platform_service: PlatformService = Depends(lambda: PlatformService())
):
    """撤销指定平台的访问权限"""
    try:
        platform_type = PlatformType(platform)
        success = await platform_service.revoke_platform_access(user_id, platform_type)
        
        if success:
            return {
                "success": True,
                "message": "访问权限撤销成功"
            }
        else:
            raise HTTPException(status_code=400, detail="访问权限撤销失败")
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"访问权限撤销失败: {str(e)}")


@router.get("/{platform}/info", summary="获取平台认证信息")
async def get_platform_auth_info(
    platform: str,
    user_id: str = Depends(get_current_user),
    _: str = Depends(validate_platform_enabled),
    platform_service: PlatformService = Depends(lambda: PlatformService())
):
    """获取用户在指定平台的认证信息"""
    try:
        platform_type = PlatformType(platform)
        platform_auth = await platform_service.get_platform_auth(user_id, platform_type)
        
        if platform_auth:
            # 隐藏敏感信息
            auth_info = platform_auth.dict()
            auth_info.pop("access_token", None)
            auth_info.pop("refresh_token", None)
            
            return {
                "success": True,
                "data": auth_info,
                "message": "获取认证信息成功"
            }
        else:
            return {
                "success": False,
                "data": None,
                "message": "未找到认证信息"
            }
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取认证信息失败: {str(e)}") 