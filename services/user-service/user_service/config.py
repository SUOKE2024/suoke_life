"""用户服务配置"""

from functools import lru_cache
from typing import Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """数据库配置"""
    
    # PostgreSQL配置
    host: str = Field(default="localhost", description="数据库主机")
    port: int = Field(default=5432, description="数据库端口")
    name: str = Field(default="user_db", description="数据库名称")
    user: str = Field(default="user_service", description="数据库用户")
    password: str = Field(default="user_password", description="数据库密码")
    
    # 连接池配置
    pool_size: int = Field(default=20, description="连接池大小")
    max_overflow: int = Field(default=30, description="连接池最大溢出")
    pool_timeout: int = Field(default=30, description="连接池超时时间")
    pool_recycle: int = Field(default=3600, description="连接回收时间")
    
    # 查询配置
    echo: bool = Field(default=False, description="是否打印SQL")
    echo_pool: bool = Field(default=False, description="是否打印连接池日志")
    
    @property
    def url(self) -> str:
        """获取数据库连接URL"""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
    
    @property
    def sync_url(self) -> str:
        """获取同步数据库连接URL"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class RedisSettings(BaseSettings):
    """Redis配置"""
    
    host: str = Field(default="localhost", description="Redis主机")
    port: int = Field(default=6379, description="Redis端口")
    db: int = Field(default=1, description="Redis数据库")
    password: Optional[str] = Field(default=None, description="Redis密码")
    max_connections: int = Field(default=20, description="最大连接数")
    
    @property
    def url(self) -> str:
        """获取Redis连接URL"""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


class CacheSettings(BaseSettings):
    """缓存配置"""
    
    enabled: bool = Field(default=True, description="是否启用缓存")
    default_ttl: int = Field(default=3600, description="默认缓存时间(秒)")
    user_cache_ttl: int = Field(default=1800, description="用户缓存时间(秒)")
    profile_cache_ttl: int = Field(default=3600, description="用户档案缓存时间(秒)")
    device_cache_ttl: int = Field(default=7200, description="设备缓存时间(秒)")


class AuthSettings(BaseSettings):
    """认证配置"""
    
    auth_service_url: str = Field(default="http://localhost:8000", description="认证服务URL")
    jwt_secret_key: str = Field(description="JWT密钥")
    jwt_algorithm: str = Field(default="HS256", description="JWT算法")
    token_cache_ttl: int = Field(default=300, description="令牌缓存时间(秒)")


class LoggingSettings(BaseSettings):
    """日志配置"""
    
    level: str = Field(default="INFO", description="日志级别")
    format: str = Field(default="json", description="日志格式")
    file_enabled: bool = Field(default=True, description="是否启用文件日志")
    file_path: str = Field(default="logs/user-service.log", description="日志文件路径")
    max_file_size: str = Field(default="100MB", description="最大文件大小")
    backup_count: int = Field(default=5, description="备份文件数量")
    
    # 结构化日志配置
    include_request_id: bool = Field(default=True, description="是否包含请求ID")
    include_user_id: bool = Field(default=True, description="是否包含用户ID")
    include_trace_id: bool = Field(default=True, description="是否包含链路追踪ID")


class MonitoringSettings(BaseSettings):
    """监控配置"""
    
    enabled: bool = Field(default=True, description="是否启用监控")
    prometheus_enabled: bool = Field(default=True, description="是否启用Prometheus")
    prometheus_port: int = Field(default=9091, description="Prometheus端口")
    health_check_interval: int = Field(default=30, description="健康检查间隔(秒)")
    
    # 性能监控
    slow_query_threshold: float = Field(default=1.0, description="慢查询阈值(秒)")
    request_timeout: int = Field(default=30, description="请求超时时间(秒)")


class ServerSettings(BaseSettings):
    """服务器配置"""
    
    host: str = Field(default="0.0.0.0", description="服务器主机")
    port: int = Field(default=8001, description="服务器端口")
    workers: int = Field(default=1, description="工作进程数")
    reload: bool = Field(default=False, description="是否自动重载")
    log_level: str = Field(default="info", description="日志级别")


class Settings(BaseSettings):
    """用户服务主配置"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_nested_delimiter="__",
        extra="ignore"
    )
    
    # 应用信息
    app_name: str = Field(default="索克生活用户服务", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    debug: bool = Field(default=False, description="调试模式")
    environment: str = Field(default="development", description="运行环境")
    
    # 子配置
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    auth: AuthSettings = Field(default_factory=AuthSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    server: ServerSettings = Field(default_factory=ServerSettings)
    
    # CORS配置
    cors_origins: List[str] = Field(default=["*"], description="CORS允许的源")
    cors_methods: List[str] = Field(default=["*"], description="CORS允许的方法")
    cors_headers: List[str] = Field(default=["*"], description="CORS允许的头部")
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """验证环境配置"""
        allowed = ["development", "testing", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v
    
    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.environment == "production"
    
    @property
    def is_testing(self) -> bool:
        """是否为测试环境"""
        return self.environment == "testing"


@lru_cache()
def get_settings() -> Settings:
    """获取应用配置单例"""
    return Settings() 