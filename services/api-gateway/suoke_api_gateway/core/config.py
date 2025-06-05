"""
配置管理模块

使用 Pydantic Settings 进行类型安全的配置管理，
支持环境变量、配置文件等多种配置源。
"""

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseConfig(BaseModel):
    """数据库配置"""
    
    url: str = Field(default="sqlite:///./gateway.db", description="数据库连接URL")
    pool_size: int = Field(default=10, description="连接池大小")
    max_overflow: int = Field(default=20, description="连接池最大溢出")
    pool_timeout: int = Field(default=30, description="连接池超时时间")
    pool_recycle: int = Field(default=3600, description="连接回收时间")

class RedisConfig(BaseModel):
    """Redis 配置"""
    
    url: str = Field(default="redis://localhost:6379/0", description="Redis连接URL")
    max_connections: int = Field(default=20, description="最大连接数")
    retry_on_timeout: bool = Field(default=True, description="超时重试")
    socket_timeout: int = Field(default=5, description="Socket超时时间")
    socket_connect_timeout: int = Field(default=5, description="连接超时时间")

class JWTConfig(BaseModel):
    """JWT 配置"""
    
    secret_key: str = Field(..., description="JWT密钥")
    algorithm: str = Field(default="HS256", description="加密算法")
    access_token_expire_minutes: int = Field(default=30, description="访问令牌过期时间(分钟)")
    refresh_token_expire_days: int = Field(default=7, description="刷新令牌过期时间(天)")

class CORSConfig(BaseModel):
    """CORS 配置"""
    
    allow_origins: List[str] = Field(default=["*"], description="允许的源")
    allow_credentials: bool = Field(default=True, description="允许凭证")
    allow_methods: List[str] = Field(default=["*"], description="允许的方法")
    allow_headers: List[str] = Field(default=["*"], description="允许的头部")

class RateLimitConfig(BaseModel):
    """限流配置"""
    
    enabled: bool = Field(default=True, description="是否启用限流")
    default_rate: str = Field(default="100/minute", description="默认限流速率")
    storage_url: str = Field(default="redis://localhost:6379/1", description="存储URL")

class MonitoringConfig(BaseModel):
    """监控配置"""
    
    enabled: bool = Field(default=True, description="是否启用监控")
    prometheus_port: int = Field(default=9090, description="Prometheus端口")
    jaeger_endpoint: Optional[str] = Field(default=None, description="Jaeger端点")
    log_level: str = Field(default="INFO", description="日志级别")

class ServiceConfig(BaseModel):
    """服务配置"""
    
    name: str = Field(..., description="服务名称")
    host: str = Field(..., description="服务主机")
    port: int = Field(..., description="服务端口")
    health_check_path: str = Field(default="/health", description="健康检查路径")
    timeout: int = Field(default=30, description="请求超时时间")
    retry_count: int = Field(default=3, description="重试次数")

class GRPCConfig(BaseModel):
    """gRPC 配置"""
    
    enabled: bool = Field(default=True, description="是否启用gRPC")
    host: str = Field(default="0.0.0.0", description="gRPC服务主机")
    port: int = Field(default=50051, description="gRPC服务端口")
    max_workers: int = Field(default=10, description="最大工作线程数")
    reflection: bool = Field(default=True, description="是否启用反射")

class Settings(BaseSettings):
    """应用程序设置"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )
    
    # 基本设置
    app_name: str = Field(default="Suoke API Gateway", description="应用名称")
    app_version: str = Field(default="0.1.0", description="应用版本")
    debug: bool = Field(default=False, description="调试模式")
    environment: str = Field(default="development", description="运行环境")
    
    # 服务器设置
    host: str = Field(default="0.0.0.0", description="服务器主机")
    port: int = Field(default=8000, description="服务器端口")
    workers: int = Field(default=1, description="工作进程数")
    
    # 安全设置
    secret_key: str = Field(..., description="应用密钥")
    allowed_hosts: List[str] = Field(default=["*"], description="允许的主机")
    
    # 数据库配置
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    
    # Redis配置
    redis: RedisConfig = Field(default_factory=RedisConfig)
    
    # JWT配置
    jwt: JWTConfig = Field(default_factory=lambda: JWTConfig(secret_key="your-secret-key"))
    
    # CORS配置
    cors: CORSConfig = Field(default_factory=CORSConfig)
    
    # 限流配置
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    
    # 监控配置
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    
    # gRPC配置
    grpc: GRPCConfig = Field(default_factory=GRPCConfig)
    
    # 服务注册表
    services: Dict[str, ServiceConfig] = Field(default_factory=dict)
    
    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_file: Optional[str] = Field(default=None, description="日志文件路径")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式"
    )
    
    @validator("secret_key")
    def validate_secret_key(cls, v: str) -> str:
        """验证密钥长度"""
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v
    
    @validator("environment")
    def validate_environment(cls, v: str) -> str:
        """验证环境设置"""
        allowed_envs = ["development", "testing", "staging", "production"]
        if v not in allowed_envs:
            raise ValueError(f"Environment must be one of {allowed_envs}")
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """验证日志级别"""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"Log level must be one of {allowed_levels}")
        return v.upper()
    
    def is_production(self) -> bool:
        """检查是否为生产环境"""
        return self.environment == "production"
    
    def is_development(self) -> bool:
        """检查是否为开发环境"""
        return self.environment == "development"
    
    def get_database_url(self) -> str:
        """获取数据库连接URL"""
        return self.database.url
    
    def get_redis_url(self) -> str:
        """获取Redis连接URL"""
        return self.redis.url
    
    def get_service_config(self, service_name: str) -> Optional[ServiceConfig]:
        """获取服务配置"""
        return self.services.get(service_name)
    
    def add_service(self, name: str, config: ServiceConfig) -> None:
        """添加服务配置"""
        self.services[name] = config
    
    def remove_service(self, name: str) -> None:
        """移除服务配置"""
        self.services.pop(name, None)
    
    def setup_default_services(self) -> None:
        """设置默认服务配置"""
        default_services = {
            "message-bus": ServiceConfig(
                name="message-bus",
                host="localhost",
                port=8004,
                health_check_path="/health",
                timeout=30,
                retry_count=3
            ),
            "auth": ServiceConfig(
                name="auth",
                host="localhost", 
                port=8001,
                health_check_path="/health"
            ),
            "user": ServiceConfig(
                name="user",
                host="localhost",
                port=8006, 
                health_check_path="/health"
            ),
            "health-data": ServiceConfig(
                name="health-data",
                host="localhost",
                port=8002,
                health_check_path="/health"
            ),
            "blockchain": ServiceConfig(
                name="blockchain",
                host="localhost",
                port=8003,
                health_check_path="/health"
            ),
            "rag": ServiceConfig(
                name="rag",
                host="localhost",
                port=8005,
                health_check_path="/health"
            ),
            "med-knowledge": ServiceConfig(
                name="med-knowledge",
                host="localhost",
                port=8007,
                health_check_path="/health"
            )
        }
        
        for service_name, config in default_services.items():
            if service_name not in self.services:
                self.services[service_name] = config

@lru_cache()
def get_settings() -> Settings:
    """获取应用程序设置（单例模式）"""
    settings = Settings()
    settings.setup_default_services()
    return settings

def load_config_from_file(config_path: Union[str, Path]) -> Dict[str, Any]:
    """从文件加载配置"""
    import yaml
    
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        if config_path.suffix in [".yaml", ".yml"]:
            return yaml.safe_load(f)
        elif config_path.suffix == ".json":
            import json
            return json.load(f)
        else:
            raise ValueError(f"Unsupported config file format: {config_path.suffix}")

def create_settings_from_file(config_path: Union[str, Path]) -> Settings:
    """从配置文件创建设置"""
    config_data = load_config_from_file(config_path)
    return Settings(**config_data) 