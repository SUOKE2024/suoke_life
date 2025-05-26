"""
Platform Service - Platform Management
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from ..model.user_integration import PlatformType, PlatformAuth
from ..adapters.adapter_factory import AdapterFactory
from ..repository.platform_auth_repository import PlatformAuthRepository
from .database import db_service
from .redis_client import redis_service
from .logging_config import LoggerMixin
from .config import get_settings


class PlatformService(LoggerMixin):
    """平台管理服务"""
    
    def __init__(self):
        super().__init__()
        self.settings = get_settings()
        self.adapter_factory = AdapterFactory()
        self.platform_auth_repo = PlatformAuthRepository()
    
    async def get_supported_platforms(self) -> List[Dict[str, Any]]:
        """获取支持的平台列表"""
        try:
            platforms_info = []
            
            for platform in PlatformType:
                try:
                    adapter = self.adapter_factory.get_adapter(platform)
                    platform_info = adapter.get_platform_info()
                    platform_info.update({
                        "platform": platform.value,
                        "enabled": True,
                        "required_scopes": adapter.get_required_scopes()
                    })
                    platforms_info.append(platform_info)
                except Exception as e:
                    # 平台未启用或配置错误
                    platforms_info.append({
                        "platform": platform.value,
                        "enabled": False,
                        "error": str(e)
                    })
            
            return platforms_info
            
        except Exception as e:
            self.logger.error("获取支持平台列表失败", error=str(e))
            raise
    
    async def get_platform_info(self, platform: PlatformType) -> Dict[str, Any]:
        """获取特定平台信息"""
        try:
            adapter = self.adapter_factory.get_adapter(platform)
            platform_info = adapter.get_platform_info()
            platform_info.update({
                "platform": platform.value,
                "enabled": True,
                "required_scopes": adapter.get_required_scopes()
            })
            
            return platform_info
            
        except Exception as e:
            self.logger.error("获取平台信息失败",
                            platform=platform.value,
                            error=str(e))
            return {
                "platform": platform.value,
                "enabled": False,
                "error": str(e)
            }
    
    async def get_auth_url(
        self,
        platform: PlatformType,
        user_id: str,
        scopes: Optional[List[str]] = None
    ) -> str:
        """获取平台授权URL"""
        try:
            adapter = self.adapter_factory.get_adapter(platform)
            
            # 使用默认权限范围如果未指定
            if not scopes:
                scopes = adapter.get_required_scopes()
            
            # 生成重定向URI
            redirect_uri = self._get_redirect_uri(platform)
            
            # 获取授权URL
            auth_url = await adapter.get_auth_url(user_id, redirect_uri, scopes)
            
            self.logger.info("生成授权URL成功",
                           platform=platform.value,
                           user_id=user_id)
            
            return auth_url
            
        except Exception as e:
            self.logger.error("生成授权URL失败",
                            platform=platform.value,
                            user_id=user_id,
                            error=str(e))
            raise
    
    async def handle_auth_callback(
        self,
        platform: PlatformType,
        code: str,
        state: str,
        user_id: str
    ) -> PlatformAuth:
        """处理平台认证回调"""
        try:
            adapter = self.adapter_factory.get_adapter(platform)
            
            # 处理认证回调
            auth_result = await adapter.handle_auth_callback(code, state)
            
            if not auth_result.success:
                raise ValueError(f"认证失败: {auth_result.error_message}")
            
            # 存储认证信息
            auth_data = {
                "user_id": user_id,
                "platform": platform.value,
                "access_token": auth_result.access_token,
                "refresh_token": auth_result.refresh_token,
                "platform_user_id": auth_result.platform_user_id,
                "platform_username": auth_result.platform_username,
                "scopes": auth_result.scopes or [],
                "expires_at": auth_result.expires_at
            }
            
            async with db_service.get_session() as session:
                # 检查是否已存在认证记录
                existing_auth = await self.platform_auth_repo.get_by_user_platform(
                    session, user_id, platform
                )
                
                if existing_auth:
                    # 更新现有记录
                    await self.platform_auth_repo.update_tokens(
                        session, user_id, platform,
                        auth_result.access_token,
                        auth_result.refresh_token,
                        auth_result.expires_at
                    )
                    auth_db = existing_auth
                else:
                    # 创建新记录
                    auth_db = await self.platform_auth_repo.create(session, auth_data)
                
                await session.commit()
            
            # 转换为Pydantic模型
            platform_auth = PlatformAuth.from_orm(auth_db)
            
            # 缓存认证信息
            await self._cache_platform_auth(user_id, platform, platform_auth)
            
            self.logger.info("处理认证回调成功",
                           platform=platform.value,
                           user_id=user_id)
            
            return platform_auth
            
        except Exception as e:
            self.logger.error("处理认证回调失败",
                            platform=platform.value,
                            user_id=user_id,
                            error=str(e))
            raise
    
    async def refresh_platform_token(
        self,
        user_id: str,
        platform: PlatformType
    ) -> bool:
        """刷新平台访问令牌"""
        try:
            # 获取当前认证信息
            async with db_service.get_session() as session:
                auth_db = await self.platform_auth_repo.get_by_user_platform(
                    session, user_id, platform
                )
                
                if not auth_db or not auth_db.refresh_token:
                    return False
                
                # 刷新令牌
                adapter = self.adapter_factory.get_adapter(platform)
                auth_result = await adapter.refresh_token(auth_db.refresh_token)
                
                if not auth_result.success:
                    self.logger.warning("刷新令牌失败",
                                      platform=platform.value,
                                      user_id=user_id,
                                      error=auth_result.error_message)
                    return False
                
                # 更新数据库
                success = await self.platform_auth_repo.update_tokens(
                    session, user_id, platform,
                    auth_result.access_token,
                    auth_result.refresh_token,
                    auth_result.expires_at
                )
                
                await session.commit()
                
                if success:
                    # 更新缓存
                    auth_db.access_token = auth_result.access_token
                    if auth_result.refresh_token:
                        auth_db.refresh_token = auth_result.refresh_token
                    if auth_result.expires_at:
                        auth_db.expires_at = auth_result.expires_at
                    
                    platform_auth = PlatformAuth.from_orm(auth_db)
                    await self._cache_platform_auth(user_id, platform, platform_auth)
                
                self.logger.info("刷新平台令牌成功",
                               platform=platform.value,
                               user_id=user_id)
                
                return success
                
        except Exception as e:
            self.logger.error("刷新平台令牌失败",
                            platform=platform.value,
                            user_id=user_id,
                            error=str(e))
            return False
    
    async def revoke_platform_access(
        self,
        user_id: str,
        platform: PlatformType
    ) -> bool:
        """撤销平台访问权限"""
        try:
            # 获取认证信息
            async with db_service.get_session() as session:
                auth_db = await self.platform_auth_repo.get_by_user_platform(
                    session, user_id, platform
                )
                
                if not auth_db:
                    return True  # 已经不存在认证信息
                
                # 撤销平台访问权限
                try:
                    adapter = self.adapter_factory.get_adapter(platform)
                    await adapter.revoke_access(auth_db.access_token)
                except Exception as e:
                    self.logger.warning("撤销平台访问权限失败",
                                      platform=platform.value,
                                      error=str(e))
                
                # 删除认证记录
                success = await self.platform_auth_repo.delete(session, user_id, platform)
                await session.commit()
                
                if success:
                    # 清除缓存
                    await self._invalidate_platform_auth_cache(user_id, platform)
                
                self.logger.info("撤销平台访问权限成功",
                               platform=platform.value,
                               user_id=user_id)
                
                return success
                
        except Exception as e:
            self.logger.error("撤销平台访问权限失败",
                            platform=platform.value,
                            user_id=user_id,
                            error=str(e))
            return False
    
    async def get_platform_auth(
        self,
        user_id: str,
        platform: PlatformType
    ) -> Optional[PlatformAuth]:
        """获取平台认证信息"""
        try:
            # 先尝试从缓存获取
            cache_key = redis_service.get_platform_auth_key(user_id, platform.value)
            cached_auth = await redis_service.get(cache_key)
            
            if cached_auth:
                return PlatformAuth(**cached_auth)
            
            # 从数据库获取
            async with db_service.get_session() as session:
                auth_db = await self.platform_auth_repo.get_by_user_platform(
                    session, user_id, platform
                )
                
                if auth_db:
                    platform_auth = PlatformAuth.from_orm(auth_db)
                    
                    # 缓存认证信息
                    await self._cache_platform_auth(user_id, platform, platform_auth)
                    
                    return platform_auth
                
                return None
                
        except Exception as e:
            self.logger.error("获取平台认证信息失败",
                            platform=platform.value,
                            user_id=user_id,
                            error=str(e))
            raise
    
    # 私有方法
    
    def _get_redirect_uri(self, platform: PlatformType) -> str:
        """获取重定向URI"""
        base_url = f"http://{self.settings.app.host}:{self.settings.app.port}"
        return f"{base_url}/api/v1/auth/{platform.value}/callback"
    
    async def _cache_platform_auth(
        self,
        user_id: str,
        platform: PlatformType,
        platform_auth: PlatformAuth
    ):
        """缓存平台认证信息"""
        try:
            cache_key = redis_service.get_platform_auth_key(user_id, platform.value)
            await redis_service.set(
                cache_key,
                platform_auth.dict(),
                ttl=self.settings.cache.auth_ttl
            )
        except Exception as e:
            self.logger.warning("缓存平台认证信息失败", error=str(e))
    
    async def _invalidate_platform_auth_cache(
        self,
        user_id: str,
        platform: PlatformType
    ):
        """清除平台认证缓存"""
        try:
            cache_key = redis_service.get_platform_auth_key(user_id, platform.value)
            await redis_service.delete(cache_key)
        except Exception as e:
            self.logger.warning("清除平台认证缓存失败", error=str(e)) 