"""
认证客户端模块

通过HTTP调用用户管理服务进行认证和用户信息获取
"""

import logging
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

import httpx
from fastapi import HTTPException, status

from ..config.settings import get_settings

logger = logging.getLogger(__name__)


class AuthClient:
    """认证服务客户端"""

    def __init__(self):
        self.settings = get_settings()
        self.user_management_url = getattr(
            self.settings, 'user_management_service_url', 
            'http://localhost:8001'  # 默认用户管理服务地址
        )
        self.timeout = 10.0
        self._token_cache = {}  # 简单的令牌缓存
        self.cache_ttl = 300  # 缓存5分钟

    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        验证JWT令牌
        
        Args:
            token: JWT令牌
            
        Returns:
            用户信息字典，如果令牌无效则返回None
        """
        try:
            # 检查缓存
            cache_key = f"token:{token[:20]}"
            if cache_key in self._token_cache:
                cached_data, cached_time = self._token_cache[cache_key]
                if datetime.now() - cached_time < timedelta(seconds=self.cache_ttl):
                    logger.debug("Token验证命中缓存")
                    return cached_data

            # 调用用户管理服务验证令牌
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.user_management_url}/api/v1/auth/verify-token",
                    headers={"Authorization": f"Bearer {token}"}
                )

                if response.status_code == 200:
                    user_data = response.json()
                    # 缓存结果
                    self._token_cache[cache_key] = (user_data, datetime.now())
                    logger.debug(f"Token验证成功，用户ID: {user_data.get('user_id')}")
                    return user_data
                elif response.status_code == 401:
                    logger.warning("Token验证失败：令牌无效或已过期")
                    return None
                else:
                    logger.error(f"Token验证失败，状态码: {response.status_code}")
                    return None

        except httpx.TimeoutException:
            logger.error("用户管理服务超时")
            return None
        except httpx.RequestError as e:
            logger.error(f"请求用户管理服务失败: {e}")
            return None
        except Exception as e:
            logger.error(f"Token验证异常: {e}")
            return None

    async def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户信息字典
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.user_management_url}/api/v1/users/{user_id}"
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"获取用户信息失败，状态码: {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"获取用户信息异常: {e}")
            return None

    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        获取用户档案
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户档案字典
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.user_management_url}/api/v1/users/{user_id}/profile"
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"获取用户档案失败，状态码: {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"获取用户档案异常: {e}")
            return None

    def clear_token_cache(self, token: str = None):
        """
        清理令牌缓存
        
        Args:
            token: 特定令牌，如果为None则清理所有缓存
        """
        if token:
            cache_key = f"token:{token[:20]}"
            self._token_cache.pop(cache_key, None)
            logger.debug("清理特定令牌缓存")
        else:
            self._token_cache.clear()
            logger.debug("清理所有令牌缓存")

    async def health_check(self) -> bool:
        """
        检查用户管理服务健康状态
        
        Returns:
            服务是否健康
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.user_management_url}/health"
                )
                return response.status_code == 200
        except Exception:
            return False


# 全局认证客户端实例
_auth_client: Optional[AuthClient] = None


def get_auth_client() -> AuthClient:
    """获取认证客户端实例"""
    global _auth_client
    if not _auth_client:
        _auth_client = AuthClient()
    return _auth_client


async def verify_token_dependency(token: str) -> Dict[str, Any]:
    """
    令牌验证依赖函数
    
    Args:
        token: JWT令牌
        
    Returns:
        用户信息
        
    Raises:
        HTTPException: 如果令牌无效
    """
    auth_client = get_auth_client()
    user_data = await auth_client.verify_token(token)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_data