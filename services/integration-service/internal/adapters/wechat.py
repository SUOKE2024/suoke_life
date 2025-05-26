"""
WeChat Platform Adapter
"""

from datetime import datetime, date
from typing import Dict, List, Any

from .base import BaseAdapter, AuthResult, SyncResult
from ..model.user_integration import PlatformType
from ..model.health_data import ActivityData, SleepData, HeartRateData, DataSource


class WeChatAdapter(BaseAdapter):
    """微信运动平台适配器"""
    
    def _get_platform_type(self) -> PlatformType:
        return PlatformType.WECHAT
    
    def _get_platform_name(self) -> str:
        return "微信运动"
    
    def get_required_scopes(self) -> List[str]:
        return ["snsapi_base", "werun"]
    
    async def get_auth_url(self, user_id: str, redirect_uri: str, scopes: List[str]) -> str:
        return f"https://open.weixin.qq.com/connect/oauth2/authorize?user_id={user_id}"
    
    async def handle_auth_callback(self, code: str, state: str) -> AuthResult:
        return AuthResult(success=True, access_token="wechat_mock_token")
    
    async def refresh_token(self, refresh_token: str) -> AuthResult:
        return AuthResult(success=True, access_token="wechat_refreshed_token")
    
    async def revoke_access(self, access_token: str) -> bool:
        return True
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        return {"id": "wechat_user_123", "platform": "wechat"}
    
    async def sync_activity_data(self, access_token: str, start_date: date, end_date: date) -> SyncResult:
        return SyncResult(success=True, synced_count=5, last_sync_time=datetime.now())
    
    async def sync_sleep_data(self, access_token: str, start_date: date, end_date: date) -> SyncResult:
        return SyncResult(success=True, synced_count=0, last_sync_time=datetime.now())
    
    async def sync_heart_rate_data(self, access_token: str, start_date: date, end_date: date) -> SyncResult:
        return SyncResult(success=True, synced_count=0, last_sync_time=datetime.now())
    
    def _normalize_activity_data(self, raw_data: Dict[str, Any], user_id: str) -> ActivityData:
        return ActivityData(user_id=user_id, source=DataSource.WECHAT, record_date=date.today())
    
    def _normalize_sleep_data(self, raw_data: Dict[str, Any], user_id: str) -> SleepData:
        return SleepData(user_id=user_id, source=DataSource.WECHAT, sleep_date=date.today())
    
    def _normalize_heart_rate_data(self, raw_data: Dict[str, Any], user_id: str) -> HeartRateData:
        return HeartRateData(user_id=user_id, source=DataSource.WECHAT, record_date=date.today(), record_time=datetime.now(), heart_rate=70) 