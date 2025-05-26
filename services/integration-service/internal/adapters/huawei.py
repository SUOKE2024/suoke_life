"""
Huawei Platform Adapter
"""

from datetime import datetime, date
from typing import Dict, List, Any

from .base import BaseAdapter, AuthResult, SyncResult
from ..model.user_integration import PlatformType
from ..model.health_data import ActivityData, SleepData, HeartRateData, DataSource


class HuaweiAdapter(BaseAdapter):
    """华为运动健康平台适配器"""
    
    def _get_platform_type(self) -> PlatformType:
        return PlatformType.HUAWEI
    
    def _get_platform_name(self) -> str:
        return "华为运动健康"
    
    def get_required_scopes(self) -> List[str]:
        return ["health.read"]
    
    async def get_auth_url(self, user_id: str, redirect_uri: str, scopes: List[str]) -> str:
        return f"https://oauth-login.cloud.huawei.com/oauth2/v3/authorize?user_id={user_id}"
    
    async def handle_auth_callback(self, code: str, state: str) -> AuthResult:
        return AuthResult(success=True, access_token="huawei_mock_token")
    
    async def refresh_token(self, refresh_token: str) -> AuthResult:
        return AuthResult(success=True, access_token="huawei_refreshed_token")
    
    async def revoke_access(self, access_token: str) -> bool:
        return True
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        return {"id": "huawei_user_123", "platform": "huawei"}
    
    async def sync_activity_data(self, access_token: str, start_date: date, end_date: date) -> SyncResult:
        return SyncResult(success=True, synced_count=5, last_sync_time=datetime.now())
    
    async def sync_sleep_data(self, access_token: str, start_date: date, end_date: date) -> SyncResult:
        return SyncResult(success=True, synced_count=3, last_sync_time=datetime.now())
    
    async def sync_heart_rate_data(self, access_token: str, start_date: date, end_date: date) -> SyncResult:
        return SyncResult(success=True, synced_count=10, last_sync_time=datetime.now())
    
    def _normalize_activity_data(self, raw_data: Dict[str, Any], user_id: str) -> ActivityData:
        return ActivityData(user_id=user_id, source=DataSource.HUAWEI, record_date=date.today())
    
    def _normalize_sleep_data(self, raw_data: Dict[str, Any], user_id: str) -> SleepData:
        return SleepData(user_id=user_id, source=DataSource.HUAWEI, sleep_date=date.today())
    
    def _normalize_heart_rate_data(self, raw_data: Dict[str, Any], user_id: str) -> HeartRateData:
        return HeartRateData(user_id=user_id, source=DataSource.HUAWEI, record_date=date.today(), record_time=datetime.now(), heart_rate=70) 