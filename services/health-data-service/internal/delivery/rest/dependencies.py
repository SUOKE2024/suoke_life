#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API依赖项
"""

from typing import Dict, Any, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ...service.health_data_service import HealthDataService


security = HTTPBearer()


async def get_health_data_service(request: Request) -> HealthDataService:
    """获取健康数据服务实例"""
    service = request.app.state.health_data_service
    
    if not service.is_initialized:
        await service.initialize()
    
    return service


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    获取当前认证用户
    
    Args:
        request: 请求对象
        credentials: 认证凭证
        
    Returns:
        用户信息字典
    
    Raises:
        HTTPException: 认证失败时抛出
    """
    try:
        token = credentials.credentials
        
        # 在实际环境中，应该通过auth-service验证token
        # 这里简化处理，直接从token中提取用户信息
        
        # 仅开发环境使用
        if token == "dev-token":
            return {"id": "00000000-0000-0000-0000-000000000000", "role": "user"}
        
        # 正式环境应该解析JWT或调用认证服务验证token
        import aiohttp
        import json
        
        # 获取认证服务URL
        auth_service_url = request.app.state.config.get("integrations", {}).get(
            "auth_service", {}).get("url", "http://auth-service:8002")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{auth_service_url}/api/v1/auth/verify",
                headers={"Authorization": f"Bearer {token}"}
            ) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="无效的认证凭证"
                    )
                
                user_data = await response.json()
                return user_data
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"认证失败: {str(e)}"
        ) 