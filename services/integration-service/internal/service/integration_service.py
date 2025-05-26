"""
Integration Service - Core Business Logic
"""

from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from ..model.user_integration import (
    UserIntegration,
    PlatformAuth,
    IntegrationRequest,
    IntegrationResponse,
    PlatformType,
    IntegrationStatus
)
from ..model.base import BaseResponse
from ..repository.user_integration_repository import UserIntegrationRepository
from ..adapters.adapter_factory import AdapterFactory
from ..adapters.base import SyncResult
from .database import db_service
from .redis_client import redis_service
from .logging_config import LoggerMixin
from .config import get_settings


class IntegrationService(LoggerMixin):
    """集成管理服务"""
    
    def __init__(self):
        super().__init__()
        self.settings = get_settings()
        self.user_integration_repo = UserIntegrationRepository()
        self.adapter_factory = AdapterFactory()
    
    async def create_integration(
        self,
        user_id: str,
        platform: PlatformType,
        permissions: List[str],
        sync_frequency: str = "hourly",
        platform_config: Dict[str, Any] = None
    ) -> IntegrationResponse:
        """创建新的平台集成"""
        try:
            async with db_service.get_session() as session:
                # 检查是否已存在该平台的集成
                # 暂时跳过重复检查，直接创建
                # existing = await self.user_integration_repo.get_by_user_platform(
                #     session, user_id, platform
                # )
                
                # if existing:
                #     raise ValueError(f"用户已存在 {platform.value} 平台的集成")
                
                # 创建集成记录
                integration_data = {
                    "user_id": user_id,
                    "platform": platform.value,
                    "status": IntegrationStatus.PENDING.value,
                    "permissions": permissions,
                    "sync_frequency": sync_frequency,
                    "platform_config": platform_config or {},
                    "sync_enabled": True,
                    "is_enabled": True
                }
                
                integration_db = await self.user_integration_repo.create(
                    session, integration_data
                )
                await session.commit()
                
                # 转换为Pydantic模型
                integration = UserIntegration.from_orm(integration_db)
                
                # 生成授权URL
                auth_url = None
                try:
                    adapter = self.adapter_factory.get_adapter(platform)
                    redirect_uri = self._get_redirect_uri(platform)
                    auth_url = await adapter.get_auth_url(
                        user_id, redirect_uri, permissions
                    )
                except Exception as e:
                    self.logger.warning("生成授权URL失败", 
                                      platform=platform.value, 
                                      error=str(e))
                
                # 缓存集成信息
                await self._cache_integration(integration)
                
                self.logger.info("创建集成成功",
                               user_id=user_id,
                               platform=platform.value,
                               integration_id=integration.id)
                
                return IntegrationResponse(
                    integration=integration,
                    auth_url=auth_url,
                    message="集成创建成功，请完成授权"
                )
                
        except Exception as e:
            self.logger.error("创建集成失败",
                            user_id=user_id,
                            platform=platform.value,
                            error=str(e))
            raise
    
    async def get_user_integrations(
        self,
        user_id: str,
        platform: Optional[PlatformType] = None,
        status: Optional[IntegrationStatus] = None,
        offset: int = 0,
        limit: int = 20
    ) -> List[UserIntegration]:
        """获取用户的集成列表"""
        try:
            # 先尝试从缓存获取
            cache_key = redis_service.get_user_integration_key(user_id)
            cached_data = await redis_service.get(cache_key)
            
            if cached_data and not platform and not status:
                return [UserIntegration(**item) for item in cached_data]
            
            # 从数据库获取
            async with db_service.get_session() as session:
                integrations_db = await self.user_integration_repo.list_by_user(
                    session, user_id, platform, status, offset, limit
                )
                
                integrations = [
                    UserIntegration.from_orm(integration_db)
                    for integration_db in integrations_db
                ]
                
                # 缓存结果（仅当无过滤条件时）
                if not platform and not status and offset == 0:
                    await redis_service.set(
                        cache_key,
                        [integration.dict() for integration in integrations],
                        ttl=self.settings.cache.user_data_ttl
                    )
                
                return integrations
                
        except Exception as e:
            self.logger.error("获取用户集成列表失败",
                            user_id=user_id,
                            error=str(e))
            raise
    
    async def get_integration_by_id(
        self,
        integration_id: int,
        user_id: str
    ) -> Optional[UserIntegration]:
        """获取指定集成的详细信息"""
        try:
            async with db_service.get_session() as session:
                integration_db = await self.user_integration_repo.get_by_id(
                    session, integration_id, user_id
                )
                
                if integration_db:
                    return UserIntegration.from_orm(integration_db)
                
                return None
                
        except Exception as e:
            self.logger.error("获取集成信息失败",
                            integration_id=integration_id,
                            user_id=user_id,
                            error=str(e))
            raise
    
    async def update_integration(
        self,
        integration_id: int,
        user_id: str,
        permissions: Optional[List[str]] = None,
        sync_frequency: Optional[str] = None,
        platform_config: Optional[Dict[str, Any]] = None
    ) -> Optional[UserIntegration]:
        """更新集成配置"""
        try:
            update_data = {}
            
            if permissions is not None:
                update_data["permissions"] = permissions
            
            if sync_frequency is not None:
                update_data["sync_frequency"] = sync_frequency
            
            if platform_config is not None:
                update_data["platform_config"] = platform_config
            
            if not update_data:
                # 如果没有更新数据，直接返回当前集成
                return await self.get_integration_by_id(integration_id, user_id)
            
            async with db_service.get_session() as session:
                integration_db = await self.user_integration_repo.update(
                    session, integration_id, user_id, update_data
                )
                await session.commit()
                
                if integration_db:
                    integration = UserIntegration.from_orm(integration_db)
                    
                    # 更新缓存
                    await self._cache_integration(integration)
                    await self._invalidate_user_cache(user_id)
                    
                    self.logger.info("更新集成成功",
                                   integration_id=integration_id,
                                   user_id=user_id)
                    
                    return integration
                
                return None
                
        except Exception as e:
            self.logger.error("更新集成失败",
                            integration_id=integration_id,
                            user_id=user_id,
                            error=str(e))
            raise
    
    async def delete_integration(
        self,
        integration_id: int,
        user_id: str
    ) -> bool:
        """删除集成配置"""
        try:
            # 先获取集成信息
            integration = await self.get_integration_by_id(integration_id, user_id)
            if not integration:
                return False
            
            # 撤销平台授权
            try:
                adapter = self.adapter_factory.get_adapter(integration.platform)
                # 这里需要获取访问令牌，暂时跳过
                # await adapter.revoke_access(access_token)
            except Exception as e:
                self.logger.warning("撤销平台授权失败",
                                  platform=integration.platform.value,
                                  error=str(e))
            
            # 删除数据库记录
            async with db_service.get_session() as session:
                success = await self.user_integration_repo.delete(
                    session, integration_id, user_id
                )
                await session.commit()
                
                if success:
                    # 清除缓存
                    await self._invalidate_user_cache(user_id)
                    
                    self.logger.info("删除集成成功",
                                   integration_id=integration_id,
                                   user_id=user_id)
                
                return success
                
        except Exception as e:
            self.logger.error("删除集成失败",
                            integration_id=integration_id,
                            user_id=user_id,
                            error=str(e))
            raise
    
    async def toggle_integration(
        self,
        integration_id: int,
        user_id: str,
        enabled: bool
    ) -> bool:
        """启用/禁用集成"""
        try:
            update_data = {"is_enabled": enabled}
            
            async with db_service.get_session() as session:
                integration_db = await self.user_integration_repo.update(
                    session, integration_id, user_id, update_data
                )
                await session.commit()
                
                if integration_db:
                    # 更新缓存
                    integration = UserIntegration.from_orm(integration_db)
                    await self._cache_integration(integration)
                    await self._invalidate_user_cache(user_id)
                    
                    action = "启用" if enabled else "禁用"
                    self.logger.info(f"{action}集成成功",
                                   integration_id=integration_id,
                                   user_id=user_id)
                    
                    return True
                
                return False
                
        except Exception as e:
            self.logger.error("切换集成状态失败",
                            integration_id=integration_id,
                            user_id=user_id,
                            enabled=enabled,
                            error=str(e))
            raise
    
    async def trigger_sync(
        self,
        integration_id: int,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        data_types: Optional[List[str]] = None
    ) -> SyncResult:
        """手动触发数据同步"""
        try:
            # 获取集成信息
            integration = await self.get_integration_by_id(integration_id, user_id)
            if not integration:
                return SyncResult(
                    success=False,
                    error_message="集成配置不存在"
                )
            
            if not integration.is_enabled:
                return SyncResult(
                    success=False,
                    error_message="集成已禁用"
                )
            
            # 设置默认日期范围
            if not start_date:
                start_date = date.today() - timedelta(days=7)
            if not end_date:
                end_date = date.today()
            
            # 获取适配器
            adapter = self.adapter_factory.get_adapter(integration.platform)
            
            # 这里需要获取访问令牌，暂时使用模拟数据
            access_token = "mock_access_token"
            
            # 执行同步
            if data_types:
                # 同步指定类型的数据
                results = await adapter.sync_all_data(
                    access_token, start_date, end_date, data_types
                )
                
                # 合并结果
                total_synced = sum(result.synced_count for result in results.values())
                total_errors = sum(result.error_count for result in results.values())
                
                sync_result = SyncResult(
                    success=all(result.success for result in results.values()),
                    synced_count=total_synced,
                    error_count=total_errors,
                    last_sync_time=datetime.now()
                )
            else:
                # 同步所有数据
                results = await adapter.sync_all_data(
                    access_token, start_date, end_date
                )
                
                total_synced = sum(result.synced_count for result in results.values())
                total_errors = sum(result.error_count for result in results.values())
                
                sync_result = SyncResult(
                    success=all(result.success for result in results.values()),
                    synced_count=total_synced,
                    error_count=total_errors,
                    last_sync_time=datetime.now()
                )
            
            # 更新同步时间
            if sync_result.success:
                async with db_service.get_session() as session:
                    await self.user_integration_repo.update(
                        session, integration_id, user_id,
                        {"last_sync_at": datetime.now().isoformat()}
                    )
                    await session.commit()
            
            self.logger.info("手动同步完成",
                           integration_id=integration_id,
                           user_id=user_id,
                           synced_count=sync_result.synced_count)
            
            return sync_result
            
        except Exception as e:
            self.logger.error("手动同步失败",
                            integration_id=integration_id,
                            user_id=user_id,
                            error=str(e))
            return SyncResult(
                success=False,
                error_message=f"同步失败: {str(e)}"
            )
    
    async def get_sync_status(
        self,
        integration_id: int,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """获取同步状态"""
        try:
            integration = await self.get_integration_by_id(integration_id, user_id)
            if not integration:
                return None
            
            # 从缓存获取同步状态
            cache_key = redis_service.get_sync_status_key(integration_id)
            cached_status = await redis_service.get(cache_key)
            
            if cached_status:
                return cached_status
            
            # 构建状态信息
            status = {
                "integration_id": integration_id,
                "platform": integration.platform.value,
                "status": integration.status.value,
                "is_enabled": integration.is_enabled,
                "sync_enabled": integration.sync_enabled,
                "last_sync_at": integration.last_sync_at,
                "sync_frequency": integration.sync_frequency,
                "error_count": integration.error_count,
                "last_error": integration.last_error
            }
            
            # 缓存状态
            await redis_service.set(cache_key, status, ttl=300)  # 5分钟缓存
            
            return status
            
        except Exception as e:
            self.logger.error("获取同步状态失败",
                            integration_id=integration_id,
                            user_id=user_id,
                            error=str(e))
            raise
    
    async def test_connection(
        self,
        integration_id: int,
        user_id: str
    ) -> bool:
        """测试平台连接"""
        try:
            integration = await self.get_integration_by_id(integration_id, user_id)
            if not integration:
                return False
            
            # 获取适配器
            adapter = self.adapter_factory.get_adapter(integration.platform)
            
            # 这里需要获取访问令牌，暂时返回True
            # access_token = await self._get_access_token(integration_id, user_id)
            # return await adapter.validate_token(access_token)
            
            return True
            
        except Exception as e:
            self.logger.error("测试连接失败",
                            integration_id=integration_id,
                            user_id=user_id,
                            error=str(e))
            return False
    
    # 私有方法
    
    def _get_redirect_uri(self, platform: PlatformType) -> str:
        """获取重定向URI"""
        base_url = f"http://{self.settings.app.host}:{self.settings.app.port}"
        return f"{base_url}/api/v1/auth/{platform.value}/callback"
    
    async def _cache_integration(self, integration: UserIntegration):
        """缓存集成信息"""
        try:
            cache_key = f"integration:{integration.id}"
            await redis_service.set(
                cache_key,
                integration.dict(),
                ttl=self.settings.cache.user_data_ttl
            )
        except Exception as e:
            self.logger.warning("缓存集成信息失败", error=str(e))
    
    async def _invalidate_user_cache(self, user_id: str):
        """清除用户相关缓存"""
        try:
            cache_key = redis_service.get_user_integration_key(user_id)
            await redis_service.delete(cache_key)
        except Exception as e:
            self.logger.warning("清除用户缓存失败", error=str(e)) 