"""
Base Adapter for Third-party Health Platforms
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from ..model.health_data import ActivityData, HeartRateData, SleepData
from ..model.user_integration import PlatformType


class AdapterError(Exception):
    """适配器基础异常"""
    pass


class AuthenticationError(AdapterError):
    """认证异常"""
    pass


class DataSyncError(AdapterError):
    """数据同步异常"""
    pass


class RateLimitError(AdapterError):
    """API限流异常"""
    pass


@dataclass
class AuthResult:
    """认证结果"""
    success: bool
    access_token: str | None = None
    refresh_token: str | None = None
    expires_at: datetime | None = None
    platform_user_id: str | None = None
    platform_username: str | None = None
    scopes: list[str] = None
    error_message: str | None = None


@dataclass
class SyncResult:
    """同步结果"""
    success: bool
    synced_count: int = 0
    error_count: int = 0
    last_sync_time: datetime | None = None
    error_message: str | None = None
    data: list[dict[str, Any]] = None


class BaseAdapter(ABC):
    """第三方健康平台适配器基类"""

    def __init__(self, config: dict[str, Any], logger: logging.Logger | None = None):
        self.config = config
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.platform_type = self._get_platform_type()

    @abstractmethod
    def _get_platform_type(self) -> PlatformType:
        """获取平台类型"""
        pass

    @abstractmethod
    async def get_auth_url(self, user_id: str, redirect_uri: str, scopes: list[str]) -> str:
        """获取OAuth授权URL"""
        pass

    @abstractmethod
    async def handle_auth_callback(self, code: str, state: str) -> AuthResult:
        """处理OAuth回调"""
        pass

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> AuthResult:
        """刷新访问令牌"""
        pass

    @abstractmethod
    async def revoke_access(self, access_token: str) -> bool:
        """撤销访问权限"""
        pass

    @abstractmethod
    async def get_user_info(self, access_token: str) -> dict[str, Any]:
        """获取用户信息"""
        pass

    @abstractmethod
    async def sync_activity_data(
        self,
        access_token: str,
        start_date: date,
        end_date: date
    ) -> SyncResult:
        """同步活动数据"""
        pass

    @abstractmethod
    async def sync_sleep_data(
        self,
        access_token: str,
        start_date: date,
        end_date: date
    ) -> SyncResult:
        """同步睡眠数据"""
        pass

    @abstractmethod
    async def sync_heart_rate_data(
        self,
        access_token: str,
        start_date: date,
        end_date: date
    ) -> SyncResult:
        """同步心率数据"""
        pass

    async def sync_all_data(
        self,
        access_token: str,
        start_date: date,
        end_date: date,
        data_types: list[str] | None = None
    ) -> dict[str, SyncResult]:
        """同步所有数据"""
        results = {}

        # 默认同步所有类型的数据
        if not data_types:
            data_types = ["activity", "sleep", "heart_rate"]

        try:
            if "activity" in data_types:
                results["activity"] = await self.sync_activity_data(
                    access_token, start_date, end_date
                )

            if "sleep" in data_types:
                results["sleep"] = await self.sync_sleep_data(
                    access_token, start_date, end_date
                )

            if "heart_rate" in data_types:
                results["heart_rate"] = await self.sync_heart_rate_data(
                    access_token, start_date, end_date
                )

        except Exception as e:
            self.logger.error(f"同步数据失败: {str(e)}")
            raise DataSyncError(f"同步数据失败: {str(e)}")

        return results

    async def validate_token(self, access_token: str) -> bool:
        """验证访问令牌是否有效"""
        try:
            await self.get_user_info(access_token)
            return True
        except AuthenticationError:
            return False
        except Exception as e:
            self.logger.warning(f"验证令牌时发生错误: {str(e)}")
            return False

    def _handle_api_error(self, response_status: int, response_text: str) -> None:
        """处理API错误响应"""
        if response_status == 401:
            raise AuthenticationError("访问令牌无效或已过期")
        elif response_status == 403:
            raise AuthenticationError("访问被拒绝，权限不足")
        elif response_status == 429:
            raise RateLimitError("API调用频率超限")
        elif response_status >= 500:
            raise DataSyncError(f"服务器错误: {response_status}")
        else:
            raise AdapterError(f"API调用失败: {response_status} - {response_text}")

    def _normalize_activity_data(self, raw_data: dict[str, Any], user_id: str) -> ActivityData:
        """标准化活动数据格式"""
        # 子类需要实现具体的数据转换逻辑
        raise NotImplementedError("子类必须实现数据标准化方法")

    def _normalize_sleep_data(self, raw_data: dict[str, Any], user_id: str) -> SleepData:
        """标准化睡眠数据格式"""
        # 子类需要实现具体的数据转换逻辑
        raise NotImplementedError("子类必须实现数据标准化方法")

    def _normalize_heart_rate_data(self, raw_data: dict[str, Any], user_id: str) -> HeartRateData:
        """标准化心率数据格式"""
        # 子类需要实现具体的数据转换逻辑
        raise NotImplementedError("子类必须实现数据标准化方法")

    def get_supported_data_types(self) -> list[str]:
        """获取支持的数据类型"""
        return ["activity", "sleep", "heart_rate"]

    def get_required_scopes(self) -> list[str]:
        """获取所需的授权范围"""
        return []

    def get_platform_info(self) -> dict[str, Any]:
        """获取平台信息"""
        return {
            "platform": self.platform_type.value,
            "name": self._get_platform_name(),
            "supported_data_types": self.get_supported_data_types(),
            "required_scopes": self.get_required_scopes(),
            "auth_type": "oauth2"
        }

    @abstractmethod
    def _get_platform_name(self) -> str:
        """获取平台名称"""
        pass
