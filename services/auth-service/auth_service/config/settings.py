"""
settings - 索克生活项目模块
"""

from functools import lru_cache
from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any, Dict, List, Optional

"""应用配置设置"""



class DatabaseSettings(BaseSettings):
    """数据库配置"""
    
    host: str = Field(default="localhost", description="数据库主机")
    port: int = Field(default=5432, description="数据库端口")
    name: str = Field(default="auth_db", description="数据库名称")
    user: str = Field(default="auth_user", description="数据库用户")
    password: str = Field(default="auth_password", description="数据库密码")
    pool_size: int = Field(default=10, description="连接池大小")
    max_overflow: int = Field(default=20, description="连接池最大溢出")
    echo: bool = Field(default=False, description="是否打印SQL")
    
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
    db: int = Field(default=0, description="Redis数据库")
    password: Optional[str] = Field(default=None, description="Redis密码")
    max_connections: int = Field(default=10, description="最大连接数")
    
    @property
    def url(self) -> str:
        """获取Redis连接URL"""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"

class EmailSettings(BaseSettings):
    """邮件服务配置"""
    
    # SMTP配置
    smtp_host: str = Field(default="smtp.gmail.com", description="SMTP服务器主机")
    smtp_port: int = Field(default=587, description="SMTP服务器端口")
    smtp_username: str = Field(default="", description="SMTP用户名")
    smtp_password: str = Field(default="", description="SMTP密码")
    use_tls: bool = Field(default=True, description="是否使用TLS")
    use_ssl: bool = Field(default=False, description="是否使用SSL")
    
    # 发件人信息
    from_email: str = Field(default="noreply@suokelife.com", description="发件人邮箱")
    from_name: str = Field(default="索克生活", description="发件人名称")
    
    # 邮件模板配置
    template_dir: str = Field(default="templates/email", description="邮件模板目录")
    
    # 第三方邮件服务配置 (SendGrid, AWS SES等)
    provider: str = Field(default="smtp", description="邮件服务提供商")
    sendgrid_api_key: Optional[str] = Field(default=None, description="SendGrid API密钥")
    aws_access_key_id: Optional[str] = Field(default=None, description="AWS访问密钥ID")
    aws_secret_access_key: Optional[str] = Field(default=None, description="AWS秘密访问密钥")
    aws_region: str = Field(default="us-east-1", description="AWS区域")
    
    # 邮件发送配置
    max_retries: int = Field(default=3, description="最大重试次数")
    retry_delay: int = Field(default=60, description="重试延迟(秒)")
    rate_limit: int = Field(default=100, description="每小时发送限制")
    
    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """验证邮件服务提供商"""
        allowed = ["smtp", "sendgrid", "aws_ses"]
        if v not in allowed:
            raise ValueError(f"Email provider must be one of {allowed}")
        return v

class JWTSettings(BaseSettings):
    """JWT配置"""
    
    secret_key: str = Field(default="test-secret-key-for-testing-only-not-for-production", description="JWT密钥")
    algorithm: str = Field(default="HS256", description="JWT算法")
    access_token_expire_minutes: int = Field(default=60, description="访问令牌过期时间(分钟)")
    refresh_token_expire_days: int = Field(default=7, description="刷新令牌过期时间(天)")
    issuer: str = Field(default="suoke-auth-service", description="JWT发行者")
    audience: str = Field(default="suoke-life", description="JWT受众")

class SecuritySettings(BaseSettings):
    """安全配置"""
    
    password_min_length: int = Field(default=8, description="密码最小长度")
    password_require_uppercase: bool = Field(default=True, description="密码是否需要大写字母")
    password_require_lowercase: bool = Field(default=True, description="密码是否需要小写字母")
    password_require_numbers: bool = Field(default=True, description="密码是否需要数字")
    password_require_symbols: bool = Field(default=True, description="密码是否需要特殊字符")
    max_login_attempts: int = Field(default=5, description="最大登录尝试次数")
    lockout_duration_minutes: int = Field(default=30, description="账户锁定时间(分钟)")
    session_timeout_minutes: int = Field(default=60, description="会话超时时间(分钟)")
    mfa_issuer_name: str = Field(default="Suoke Life", description="MFA发行者名称")

class CacheSettings(BaseSettings):
    """缓存配置"""
    
    enabled: bool = Field(default=True, description="是否启用缓存")
    default_ttl: int = Field(default=3600, description="默认缓存时间(秒)")
    user_cache_ttl: int = Field(default=1800, description="用户缓存时间(秒)")
    session_cache_ttl: int = Field(default=900, description="会话缓存时间(秒)")
    max_memory: str = Field(default="256mb", description="最大内存使用")

class LoggingSettings(BaseSettings):
    """日志配置"""
    
    level: str = Field(default="INFO", description="日志级别")
    format: str = Field(default="json", description="日志格式")
    file_enabled: bool = Field(default=True, description="是否启用文件日志")
    file_path: str = Field(default="logs/auth-service.log", description="日志文件路径")
    max_file_size: str = Field(default="100MB", description="最大文件大小")
    backup_count: int = Field(default=5, description="备份文件数量")
    
    # 结构化日志配置
    include_request_id: bool = Field(default=True, description="是否包含请求ID")
    include_user_id: bool = Field(default=True, description="是否包含用户ID")
    include_ip_address: bool = Field(default=True, description="是否包含IP地址")

class MonitoringSettings(BaseSettings):
    """监控配置"""
    
    enabled: bool = Field(default=True, description="是否启用监控")
    prometheus_enabled: bool = Field(default=True, description="是否启用Prometheus")
    prometheus_port: int = Field(default=9090, description="Prometheus端口")
    health_check_interval: int = Field(default=30, description="健康检查间隔(秒)")
    
    # 性能监控
    slow_query_threshold: float = Field(default=1.0, description="慢查询阈值(秒)")
    request_timeout: int = Field(default=30, description="请求超时时间(秒)")

class ServerSettings(BaseSettings):
    """服务器配置"""
    
    host: str = Field(default="0.0.0.0", description="服务器主机")
    port: int = Field(default=8000, description="服务器端口")
    workers: int = Field(default=1, description="工作进程数")
    reload: bool = Field(default=False, description="是否自动重载")
    log_level: str = Field(default="info", description="日志级别")

class Settings(BaseSettings):
    """应用主配置"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_nested_delimiter="__",
        extra="ignore"
    )
    
    # 应用信息
    app_name: str = Field(default="索克生活认证服务", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    debug: bool = Field(default=False, description="调试模式")
    environment: str = Field(default="development", description="运行环境")
    
    # 子配置
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    email: EmailSettings = Field(default_factory=EmailSettings)
    jwt: JWTSettings = Field(default_factory=JWTSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    server: ServerSettings = Field(default_factory=ServerSettings)
    
    # CORS配置
    cors_origins: List[str] = Field(default=["*"], description="CORS允许的源")
    cors_methods: List[str] = Field(default=["*"], description="CORS允许的方法")
    cors_headers: List[str] = Field(default=["*"], description="CORS允许的头部")
    
    # OAuth配置
    base_url: str = Field(default="http://localhost:8000", description="应用基础URL")
    
    # Google OAuth
    google_client_id: str = Field(default="", description="Google OAuth客户端ID")
    google_client_secret: str = Field(default="", description="Google OAuth客户端密钥")
    
    # GitHub OAuth
    github_client_id: str = Field(default="", description="GitHub OAuth客户端ID")
    github_client_secret: str = Field(default="", description="GitHub OAuth客户端密钥")
    
    # 微信OAuth
    wechat_app_id: str = Field(default="", description="微信应用ID")
    wechat_app_secret: str = Field(default="", description="微信应用密钥")
    
    # QQ OAuth
    qq_app_id: str = Field(default="", description="QQ应用ID")
    qq_app_key: str = Field(default="", description="QQ应用密钥")
    
    # 微博OAuth
    weibo_app_key: str = Field(default="", description="微博应用密钥")
    weibo_app_secret: str = Field(default="", description="微博应用密钥")
    
    # OAuth通用配置
    oauth_state_expire_minutes: int = Field(default=10, description="OAuth状态参数过期时间(分钟)")
    oauth_callback_timeout_seconds: int = Field(default=300, description="OAuth回调超时时间(秒)")
    
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