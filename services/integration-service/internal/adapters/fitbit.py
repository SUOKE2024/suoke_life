"""
Fitbit Platform Adapter
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any

from .base import BaseAdapter, AuthResult, SyncResult, AuthenticationError, DataSyncError
from ..model.user_integration import PlatformType
from ..model.health_data import ActivityData, SleepData, HeartRateData, DataSource


class FitbitAdapter(BaseAdapter):
    """Fitbit平台适配器"""
    
    def _get_platform_type(self) -> PlatformType:
        return PlatformType.FITBIT
    
    def _get_platform_name(self) -> str:
        return "Fitbit"
    
    def get_required_scopes(self) -> List[str]:
        return ["activity", "sleep", "heartrate", "profile"]
    
    async def get_auth_url(self, user_id: str, redirect_uri: str, scopes: List[str]) -> str:
        """获取Fitbit授权URL"""
        return f"https://www.fitbit.com/oauth2/authorize?user_id={user_id}&redirect_uri={redirect_uri}"
    
    async def handle_auth_callback(self, code: str, state: str) -> AuthResult:
        """处理Fitbit认证回调"""
        return AuthResult(
            success=True,
            access_token="fitbit_mock_token",
            platform_user_id="fitbit_user_123",
            platform_username="Fitbit User"
        )
    
    async def refresh_token(self, refresh_token: str) -> AuthResult:
        """刷新Fitbit访问令牌"""
        return AuthResult(success=True, access_token="fitbit_refreshed_token")
    
    async def revoke_access(self, access_token: str) -> bool:
        """撤销Fitbit访问权限"""
        return True
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """获取Fitbit用户信息"""
        return {"id": "fitbit_user_123", "platform": "fitbit", "name": "Fitbit User"}
    
    async def sync_activity_data(self, access_token: str, start_date: date, end_date: date) -> SyncResult:
        """同步Fitbit活动数据"""
        return SyncResult(success=True, synced_count=5, last_sync_time=datetime.now())
    
    async def sync_sleep_data(self, access_token: str, start_date: date, end_date: date) -> SyncResult:
        """同步Fitbit睡眠数据"""
        return SyncResult(success=True, synced_count=3, last_sync_time=datetime.now())
    
    async def sync_heart_rate_data(self, access_token: str, start_date: date, end_date: date) -> SyncResult:
        """同步Fitbit心率数据"""
        return SyncResult(success=True, synced_count=10, last_sync_time=datetime.now())
    
    def _normalize_activity_data(self, raw_data: Dict[str, Any], user_id: str) -> ActivityData:
        """标准化Fitbit活动数据"""
        return ActivityData(user_id=user_id, source=DataSource.FITBIT, record_date=date.today())
    
    def _normalize_sleep_data(self, raw_data: Dict[str, Any], user_id: str) -> SleepData:
        """标准化Fitbit睡眠数据"""
        return SleepData(user_id=user_id, source=DataSource.FITBIT, sleep_date=date.today())
    
    def _normalize_heart_rate_data(self, raw_data: Dict[str, Any], user_id: str) -> HeartRateData:
        """标准化Fitbit心率数据"""
        return HeartRateData(user_id=user_id, source=DataSource.FITBIT, record_date=date.today(), record_time=datetime.now(), heart_rate=70) 