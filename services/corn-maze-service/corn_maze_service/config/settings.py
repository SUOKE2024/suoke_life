"""
应用配置设置

使用 Pydantic Settings 进行类型安全的配置管理。
"""

from functools import lru_cache
from typing import Any

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseModel):
    """数据库配置"""

    url: str = Field(default="sqlite:///./data/corn_maze.db", description="数据库连接URL")
    echo: bool = Field(default=False, description="是否输出SQL日志")
    pool_size: int = Field(default=10, description="连接池大小")
    max_overflow: int = Field(default=20, description="连接池最大溢出")
    pool_timeout: int = Field(default=30, description="连接池超时时间")
    pool_recycle: int = Field(default=3600, description="连接回收时间")

class RedisConfig(BaseModel):
    """Redis配置"""

    url: str = Field(default="redis://localhost:6379/0", description="Redis连接URL")
    max_connections: int = Field(default=10, description="最大连接数")
    retry_on_timeout: bool = Field(default=True, description="超时重试")
    socket_timeout: float = Field(default=5.0, description="Socket超时时间")
    socket_connect_timeout: float = Field(default=5.0, description="连接超时时间")

class GRPCConfig(BaseModel):
    """gRPC服务配置"""

    host: str = Field(default="0.0.0.0", description="gRPC服务主机")
    port: int = Field(default=50057, description="gRPC服务端口")
    max_workers: int = Field(default=10, description="最大工作线程数")
    max_receive_message_length: int = Field(default=4 * 1024 * 1024, description="最大接收消息长度")
    max_send_message_length: int = Field(default=4 * 1024 * 1024, description="最大发送消息长度")
    enable_reflection: bool = Field(default=True, description="启用gRPC反射")
    enable_health_check: bool = Field(default=True, description="启用健康检查")

class HTTPConfig(BaseModel):
    """HTTP服务配置"""

    host: str = Field(default="0.0.0.0", description="HTTP服务主机")
    port: int = Field(default=51057, description="HTTP服务端口")
    reload: bool = Field(default=False, description="开发模式自动重载")
    workers: int = Field(default=1, description="工作进程数")
    access_log: bool = Field(default=True, description="访问日志")

class MonitoringConfig(BaseModel):
    """监控配置"""

    enable_prometheus: bool = Field(default=True, description="启用Prometheus指标")
    prometheus_port: int = Field(default=51058, description="Prometheus指标端口")
    enable_tracing: bool = Field(default=True, description="启用链路追踪")
    jaeger_endpoint: str | None = Field(default=None, description="Jaeger端点")
    enable_logging: bool = Field(default=True, description="启用结构化日志")
    log_level: str = Field(default="INFO", description="日志级别")

class MazeConfig(BaseModel):
    """迷宫配置"""

    default_size: int = Field(default=20, description="默认迷宫大小")
    max_size: int = Field(default=100, description="最大迷宫大小")
    min_size: int = Field(default=5, description="最小迷宫大小")
    knowledge_node_density: float = Field(default=0.1, description="知识节点密度")
    challenge_node_density: float = Field(default=0.05, description="挑战节点密度")
    max_user_mazes: int = Field(default=10, description="用户最大迷宫数量")

class AIConfig(BaseModel):
    """AI配置"""

    openai_api_key: str | None = Field(default=None, description="OpenAI API密钥")
    openai_base_url: str | None = Field(default=None, description="OpenAI API基础URL")
    model_name: str = Field(default="gpt-3.5-turbo", description="默认模型名称")
    max_tokens: int = Field(default=1000, description="最大令牌数")
    temperature: float = Field(default=0.7, description="生成温度")

class SecurityConfig(BaseModel):
    """安全配置"""

    secret_key: str = Field(default="your-secret-key-here", description="应用密钥")
    algorithm: str = Field(default="HS256", description="JWT算法")
    access_token_expire_minutes: int = Field(default=30, description="访问令牌过期时间(分钟)")
    cors_origins: list[str] = Field(default=["*"], description="CORS允许的源")
    cors_methods: list[str] = Field(default=["*"], description="CORS允许的方法")
    cors_headers: list[str] = Field(default=["*"], description="CORS允许的头部")

class Settings(BaseSettings):
    """应用设置"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    # 基本设置
    app_name: str = Field(default="Corn Maze Service", description="应用名称")
    app_version: str = Field(default="0.2.0", description="应用版本")
    debug: bool = Field(default=False, description="调试模式")
    environment: str = Field(default="development", description="运行环境")

    # 各模块配置
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    grpc: GRPCConfig = Field(default_factory=GRPCConfig)
    http: HTTPConfig = Field(default_factory=HTTPConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    maze: MazeConfig = Field(default_factory=MazeConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """验证环境配置"""
        allowed_envs = {"development", "testing", "staging", "production"}
        if v.lower() not in allowed_envs:
            raise ValueError(f"Environment must be one of {allowed_envs}")
        return v.lower()

    @field_validator("monitoring")
    @classmethod
    def validate_monitoring_log_level(cls, v: MonitoringConfig) -> MonitoringConfig:
        """验证日志级别"""
        allowed_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.log_level.upper() not in allowed_levels:
            raise ValueError(f"Log level must be one of {allowed_levels}")
        v.log_level = v.log_level.upper()
        return v

    def get_database_url(self) -> str:
        """获取数据库连接URL"""
        return self.database.url

    def get_redis_url(self) -> str:
        """获取Redis连接URL"""
        return self.redis.url

    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.environment == "production"

    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.environment == "development"

    def get_log_config(self) -> dict[str, Any]:
        """获取日志配置"""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
                "detailed": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
                "detailed": {
                    "formatter": "detailed",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {
                "level": self.monitoring.log_level,
                "handlers": ["default"],
            },
            "loggers": {
                "corn_maze_service": {
                    "level": self.monitoring.log_level,
                    "handlers": ["detailed"],
                    "propagate": False,
                },
                "uvicorn": {
                    "level": "INFO",
                    "handlers": ["default"],
                    "propagate": False,
                },
                "grpc": {
                    "level": "INFO",
                    "handlers": ["default"],
                    "propagate": False,
                },
            },
        }

@lru_cache
def get_settings() -> Settings:
    """获取应用设置单例"""
    return Settings()
