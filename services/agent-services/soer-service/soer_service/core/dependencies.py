"""
依赖注入模块

提供FastAPI依赖注入函数
"""

from typing import Any, Dict
from fastapi import Depends, HTTPException, status, WebSocket, WebSocketException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..clients.auth_client import get_auth_client, AuthClient

# HTTP Bearer 认证
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_client: AuthClient = Depends(get_auth_client)
) -> Dict[str, Any]:
    """
    获取当前用户（依赖注入）
    
    Args:
        credentials: HTTP认证凭据
        auth_client: 认证客户端
        
    Returns:
        用户信息字典
        
    Raises:
        HTTPException: 如果令牌无效
    """
    user_data = await auth_client.verify_token(credentials.credentials)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_data


async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取当前活跃用户
    
    Args:
        current_user: 当前用户信息
        
    Returns:
        活跃用户信息
        
    Raises:
        HTTPException: 如果用户未激活
    """
    if not current_user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户已被禁用"
        )
    
    return current_user


async def get_current_verified_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取当前已验证用户
    
    Args:
        current_user: 当前用户信息
        
    Returns:
        已验证用户信息
        
    Raises:
        HTTPException: 如果用户未验证
    """
    if not current_user.get("is_verified", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户未验证"
        )
    
    return current_user


async def get_current_superuser(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取当前超级用户
    
    Args:
        current_user: 当前用户信息
        
    Returns:
        超级用户信息
        
    Raises:
        HTTPException: 如果用户不是超级用户
    """
    if not current_user.get("is_superuser", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要超级用户权限"
        )
    
    return current_user


def require_roles(*required_roles: str):
    """
    角色权限装饰器工厂
    
    Args:
        required_roles: 需要的角色列表
        
    Returns:
        依赖函数
    """
    async def check_roles(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        user_roles = current_user.get("roles", [])
        if isinstance(user_roles, str):
            user_roles = [user_roles]
            
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足，需要以下角色之一: {', '.join(required_roles)}"
            )
        
        return current_user
    
    return check_roles


async def get_websocket_user(
    websocket: WebSocket,
    token: str = None
) -> Dict[str, Any]:
    """
    WebSocket用户认证
    
    Args:
        websocket: WebSocket连接
        token: 认证令牌（从查询参数或头部获取）
        
    Returns:
        用户信息字典
        
    Raises:
        WebSocketException: 如果认证失败
    """
    auth_client = get_auth_client()
    
    # 从查询参数获取token
    if not token:
        token = websocket.query_params.get("token")
    
    # 从头部获取token
    if not token:
        auth_header = websocket.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
    
    if not token:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="缺少认证令牌")
    
    user_data = await auth_client.verify_token(token)
    
    if not user_data:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="无效的认证令牌")
    
    return user_data