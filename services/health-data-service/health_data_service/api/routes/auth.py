"""
auth - 索克生活项目模块
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from health_data_service.core.exceptions import ValidationError, DatabaseError
from health_data_service.core.security import (
from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Any

"""认证API路由"""


    SecurityManager,
    Token,
    TokenData,
    RefreshTokenRequest,
    security_manager,
    get_current_user,
    require_auth,
)


router = APIRouter(prefix="/auth", tags=["认证"])


class UserLogin(BaseModel):
    """用户登录请求"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class UserRegister(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=8, description="密码")
    full_name: str = Field(None, max_length=100, description="全名")


class PasswordChange(BaseModel):
    """密码修改请求"""
    current_password: str = Field(..., description="当前密码")
    new_password: str = Field(..., min_length=8, description="新密码")


class UserProfile(BaseModel):
    """用户资料"""
    user_id: int
    username: str
    email: str
    full_name: str = None
    is_active: bool = True
    scopes: list[str] = []
    created_at: str
    updated_at: str


@router.post("/login", response_model=Token, summary="用户登录")
async def login(user_data: UserLogin) -> Token:
    """
    用户登录
    
    - **username**: 用户名或邮箱
    - **password**: 密码
    
    返回访问令牌和刷新令牌
    """
    try:
        # TODO: 这里需要实现用户验证逻辑
        # 目前使用模拟数据，实际应该查询用户服务
        
        # 模拟用户验证
        if user_data.username == "demo" and user_data.password == "demo123":
            user_info = {
                "sub": 1,
                "username": "demo",
                "email": "demo@example.com",
                "scopes": ["health_data:read", "health_data:write"]
            }
        elif user_data.username == "admin" and user_data.password == "admin123":
            user_info = {
                "sub": 2,
                "username": "admin",
                "email": "admin@example.com",
                "scopes": ["admin", "health_data:read", "health_data:write", "health_data:delete"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 创建令牌对
        token = security_manager.create_token_pair(user_info)
        return token
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
        )


@router.post("/register", response_model=Dict[str, Any], summary="用户注册")
async def register(user_data: UserRegister) -> Dict[str, Any]:
    """
    用户注册
    
    - **username**: 用户名（3-50字符）
    - **email**: 邮箱地址
    - **password**: 密码（至少8字符）
    - **full_name**: 全名（可选）
    """
    try:
        # 验证密码强度
        if not security_manager.validate_password_strength(user_data.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="密码强度不足，请确保密码包含大小写字母和数字"
            )
        
        # 哈希密码
        hashed_password = security_manager.hash_password(user_data.password)
        
        # TODO: 这里需要实现用户创建逻辑
        # 实际应该调用用户服务创建用户
        
        # 模拟用户创建
        user_id = 100  # 模拟生成的用户ID
        
        return {
            "success": True,
            "message": "用户注册成功",
            "data": {
                "user_id": user_id,
                "username": user_data.username,
                "email": user_data.email,
                "full_name": user_data.full_name
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )


@router.post("/refresh", response_model=Token, summary="刷新令牌")
async def refresh_token(request: RefreshTokenRequest) -> Token:
    """
    使用刷新令牌获取新的访问令牌
    
    - **refresh_token**: 刷新令牌
    """
    try:
        token = security_manager.refresh_access_token(request.refresh_token)
        return token
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"令牌刷新失败: {str(e)}"
        )


@router.get("/me", response_model=UserProfile, summary="获取当前用户信息")
async def get_current_user_profile(current_user: TokenData = Depends(require_auth)) -> UserProfile:
    """
    获取当前登录用户的资料信息
    
    需要有效的访问令牌
    """
    try:
        # TODO: 这里需要从用户服务获取完整的用户信息
        # 目前使用令牌中的基本信息
        
        return UserProfile(
            user_id=current_user.user_id,
            username=current_user.username or "",
            email=current_user.email or "",
            full_name="",  # 需要从用户服务获取
            is_active=True,
            scopes=current_user.scopes,
            created_at="2024-01-01T00:00:00Z",  # 需要从用户服务获取
            updated_at="2024-01-01T00:00:00Z"   # 需要从用户服务获取
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户信息失败: {str(e)}"
        )


@router.post("/change-password", response_model=Dict[str, Any], summary="修改密码")
async def change_password(
    password_data: PasswordChange,
    current_user: TokenData = Depends(require_auth)
) -> Dict[str, Any]:
    """
    修改当前用户密码
    
    - **current_password**: 当前密码
    - **new_password**: 新密码（至少8字符）
    
    需要有效的访问令牌
    """
    try:
        # 验证新密码强度
        if not security_manager.validate_password_strength(password_data.new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="新密码强度不足，请确保密码包含大小写字母和数字"
            )
        
        # TODO: 这里需要验证当前密码并更新密码
        # 实际应该调用用户服务验证和更新密码
        
        # 哈希新密码
        new_hashed_password = security_manager.hash_password(password_data.new_password)
        
        return {
            "success": True,
            "message": "密码修改成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"密码修改失败: {str(e)}"
        )


@router.post("/logout", response_model=Dict[str, Any], summary="用户登出")
async def logout(current_user: TokenData = Depends(require_auth)) -> Dict[str, Any]:
    """
    用户登出
    
    需要有效的访问令牌
    注意：由于JWT是无状态的，实际的令牌失效需要在客户端处理
    """
    try:
        # TODO: 这里可以实现令牌黑名单机制
        # 将令牌加入黑名单，防止继续使用
        
        return {
            "success": True,
            "message": "登出成功"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登出失败: {str(e)}"
        )


@router.get("/validate", response_model=Dict[str, Any], summary="验证令牌")
async def validate_token(current_user: TokenData = Depends(require_auth)) -> Dict[str, Any]:
    """
    验证当前令牌是否有效
    
    需要有效的访问令牌
    """
    return {
        "success": True,
        "message": "令牌有效",
        "data": {
            "user_id": current_user.user_id,
            "username": current_user.username,
            "scopes": current_user.scopes
        }
    }


# 导出路由器
auth_router = router