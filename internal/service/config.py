"""
Configuration Management
"""

import os
import yaml
from functools import lru_cache
from typing import Dict, Any, List
from pydantic import BaseSettings, Field


class AppConfig(BaseSettings):
    """应用配置"""
    name: str = "integration-service"
    version: str = "1.0.0"
    description: str = "索克生活第三方健康平台集成服务"
    host: str = "0.0.0.0"
    port: int = 8090
    debug: bool = False
    log_level: str = "INFO"
    
    class Config:
        env_prefix = "APP_"


class RedisConfig(BaseSettings):
    """Redis配置"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: str = ""
    max_connections: int = 20
    socket_timeout: int = 30
    socket_connect_timeout: int = 30
    
    class Config:
        env_prefix = "REDIS_"


class DatabaseConfig(BaseSettings):
    """数据库配置"""
    url: str = "postgresql://postgres:password@localhost:5432/integration_db"
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20
    
    class Config:
        env_prefix = "DATABASE_"


class PlatformConfig(BaseSettings):
    """平台配置"""
    apple_health_enabled: bool = True
    apple_health_app_id: str = ""
    apple_health_team_id: str = ""
    apple_health_key_id: str = ""
    apple_health_private_key_path: str = ""
    
    google_fit_enabled: bool = True
    google_fit_client_id: str = ""
    google_fit_client_secret: str = ""
    google_fit_redirect_uri: str = "http://localhost:8090/auth/google/callback"
    
    fitbit_enabled: bool = True
    fitbit_client_id: str = ""
    fitbit_client_secret: str = ""
    fitbit_redirect_uri: str = "http://localhost:8090/auth/fitbit/callback"
    
    xiaomi_enabled: bool = True
    xiaomi_app_id: str = ""
    xiaomi_app_secret: str = ""
    
    huawei_enabled: bool = True
    huawei_app_id: str = ""
    huawei_app_secret: str = ""
    
    wechat_enabled: bool = True
    wechat_app_id: str = ""
    wechat_app_secret: str = ""
    
    alipay_enabled: bool = True
    alipay_app_id: str = ""
    alipay_private_key_path: str = ""
    alipay_public_key_path: str = ""
    
    class Config:
        env_prefix = "PLATFORM_"


class CacheConfig(BaseSettings):
    """缓存配置"""
    default_ttl: int = 3600
    user_data_ttl: int = 1800
    platform_token_ttl: int = 7200
    health_data_ttl: int = 900
    
    class Config:
        env_prefix = "CACHE_"


class RateLimitConfig(BaseSettings):
    """限流配置"""
    requests_per_minute: int = 100
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    
    class Config:
        env_prefix = "RATE_LIMIT_"


class MonitoringConfig(BaseSettings):
    """监控配置"""
    prometheus_enabled: bool = True
    prometheus_port: int = 9090
    sentry_enabled: bool = False
    sentry_dsn: str = ""
    
    class Config:
        env_prefix = "MONITORING_"


class LoggingConfig(BaseSettings):
    """日志配置"""
    level: str = "INFO"
    format: str = "json"
    file_path: str = "/var/log/integration-service.log"
    max_size: str = "100MB"
    backup_count: int = 5
    
    class Config:
        env_prefix = "LOGGING_"


class SecurityConfig(BaseSettings):
    """安全配置"""
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    class Config:
        env_prefix = "SECURITY_"


class HealthCheckConfig(BaseSettings):
    """健康检查配置"""
    enabled: bool = True
    interval: int = 30
    timeout: int = 10
    
    class Config:
        env_prefix = "HEALTH_CHECK_"


class SyncConfig(BaseSettings):
    """同步配置"""
    batch_size: int = 100
    max_retries: int = 3
    retry_delay: int = 5
    sync_interval: int = 300
    
    class Config:
        env_prefix = "SYNC_"


class Settings(BaseSettings):
    """主配置类"""
    app: AppConfig = AppConfig()
    redis: RedisConfig = RedisConfig()
    database: DatabaseConfig = DatabaseConfig()
    platforms: PlatformConfig = PlatformConfig()
    cache: CacheConfig = CacheConfig()
    rate_limit: RateLimitConfig = RateLimitConfig()
    monitoring: MonitoringConfig = MonitoringConfig()
    logging: LoggingConfig = LoggingConfig()
    security: SecurityConfig = SecurityConfig()
    health_check: HealthCheckConfig = HealthCheckConfig()
    sync: SyncConfig = SyncConfig()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_from_yaml()
    
    def _load_from_yaml(self):
        """从YAML文件加载配置"""
        config_file = os.getenv("CONFIG_FILE", "config/config.yaml")
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    yaml_config = yaml.safe_load(f)
                
                # 更新配置
                if yaml_config:
                    self._update_from_dict(yaml_config)
            except Exception as e:
                print(f"警告: 无法加载配置文件 {config_file}: {e}")
    
    def _update_from_dict(self, config_dict: Dict[str, Any]):
        """从字典更新配置"""
        for section_name, section_config in config_dict.items():
            if hasattr(self, section_name) and isinstance(section_config, dict):
                section_obj = getattr(self, section_name)
                for key, value in section_config.items():
                    if hasattr(section_obj, key):
                        setattr(section_obj, key, value)
    
    def get_platform_config(self, platform: str) -> Dict[str, Any]:
        """获取指定平台的配置"""
        platform_configs = {
            "apple_health": {
                "enabled": self.platforms.apple_health_enabled,
                "app_id": self.platforms.apple_health_app_id,
                "team_id": self.platforms.apple_health_team_id,
                "key_id": self.platforms.apple_health_key_id,
                "private_key_path": self.platforms.apple_health_private_key_path,
            },
            "google_fit": {
                "enabled": self.platforms.google_fit_enabled,
                "client_id": self.platforms.google_fit_client_id,
                "client_secret": self.platforms.google_fit_client_secret,
                "redirect_uri": self.platforms.google_fit_redirect_uri,
            },
            "fitbit": {
                "enabled": self.platforms.fitbit_enabled,
                "client_id": self.platforms.fitbit_client_id,
                "client_secret": self.platforms.fitbit_client_secret,
                "redirect_uri": self.platforms.fitbit_redirect_uri,
            },
            "xiaomi": {
                "enabled": self.platforms.xiaomi_enabled,
                "app_id": self.platforms.xiaomi_app_id,
                "app_secret": self.platforms.xiaomi_app_secret,
            },
            "huawei": {
                "enabled": self.platforms.huawei_enabled,
                "app_id": self.platforms.huawei_app_id,
                "app_secret": self.platforms.huawei_app_secret,
            },
            "wechat": {
                "enabled": self.platforms.wechat_enabled,
                "app_id": self.platforms.wechat_app_id,
                "app_secret": self.platforms.wechat_app_secret,
            },
            "alipay": {
                "enabled": self.platforms.alipay_enabled,
                "app_id": self.platforms.alipay_app_id,
                "private_key_path": self.platforms.alipay_private_key_path,
                "public_key_path": self.platforms.alipay_public_key_path,
            }
        }
        
        return platform_configs.get(platform, {})
    
    def get_enabled_platforms(self) -> List[str]:
        """获取启用的平台列表"""
        enabled_platforms = []
        
        if self.platforms.apple_health_enabled:
            enabled_platforms.append("apple_health")
        if self.platforms.google_fit_enabled:
            enabled_platforms.append("google_fit")
        if self.platforms.fitbit_enabled:
            enabled_platforms.append("fitbit")
        if self.platforms.xiaomi_enabled:
            enabled_platforms.append("xiaomi")
        if self.platforms.huawei_enabled:
            enabled_platforms.append("huawei")
        if self.platforms.wechat_enabled:
            enabled_platforms.append("wechat")
        if self.platforms.alipay_enabled:
            enabled_platforms.append("alipay")
        
        return enabled_platforms


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings() 