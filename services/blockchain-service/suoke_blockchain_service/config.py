"""
config - 索克生活项目模块
"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Union, List, Optional

"""
配置管理模块

使用 Pydantic Settings 进行类型安全的配置管理。
"""


class DatabaseSettings(BaseSettings):
    """数据库配置"""

    host: str = Field(default="localhost", description="数据库主机")
    port: int = Field(default=5432, description="数据库端口")
    user: str = Field(default="postgres", description="数据库用户")
    password: str = Field(default="", description="数据库密码")
    database: str = Field(default="blockchain_service", description="数据库名称")

    # 连接池配置
    pool_size: int = Field(default=10, description="连接池大小")
    max_overflow: int = Field(default=20, description="最大溢出连接数")
    pool_timeout: int = Field(default=30, description="连接池超时时间")
    pool_recycle: int = Field(default=3600, description="连接回收时间")

    @property
    def url(self) -> str:
        """构建数据库连接 URL"""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

class RedisSettings(BaseSettings):
    """Redis 配置"""

    host: str = Field(default="localhost", description="Redis 主机")
    port: int = Field(default=6379, description="Redis 端口")
    password: Optional[str] = Field(default=None, description="Redis 密码")
    database: int = Field(default=0, description="Redis 数据库")

    # 连接池配置
    max_connections: int = Field(default=20, description="最大连接数")
    retry_on_timeout: bool = Field(default=True, description="超时重试")
    socket_timeout: int = Field(default=5, description="Socket 超时时间")

    @property
    def url(self) -> str:
        """构建 Redis 连接 URL"""
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.database}"

class BlockchainSettings(BaseSettings):
    """区块链配置"""

    # 以太坊节点配置
    eth_node_url: str = Field(
        default="http://localhost:8545",
        description="以太坊节点 URL"
    )
    chain_id: int = Field(default=1337, description="链 ID")

    # 智能合约地址
    health_data_storage_address: Optional[str] = Field(
        default=None,
        description="健康数据存储合约地址"
    )
    zkp_verifier_address: Optional[str] = Field(
        default=None,
        description="零知识证明验证合约地址"
    )
    access_control_address: Optional[str] = Field(
        default=None,
        description="访问控制合约地址"
    )

    # 私钥配置(用于部署和管理)
    deployer_private_key: Optional[str] = Field(
        default=None,
        description="部署者私钥"
    )

    # Gas 配置
    gas_limit: int = Field(default=6000000, description="Gas 限制")
    gas_price: int = Field(default=20000000000, description="Gas 价格 (wei)")

    # 确认配置
    confirmation_blocks: int = Field(default=1, description="确认区块数")
    transaction_timeout: int = Field(default=120, description="交易超时时间")
    
    # 数据限制
    max_data_size: int = Field(default=10 * 1024 * 1024, description="最大数据大小(字节)")  # 10MB

class GRPCSettings(BaseSettings):
    """gRPC 服务配置"""

    host: str = Field(default="0.0.0.0", description="gRPC 服务主机")
    port: int = Field(default=50055, description="gRPC 服务端口", ge=1, le=65535)

    # 服务器配置
    max_workers: int = Field(default=10, description="最大工作线程数")
    max_receive_message_length: int = Field(
        default=4 * 1024 * 1024,  # 4MB
        description="最大接收消息长度"
    )
    max_send_message_length: int = Field(
        default=4 * 1024 * 1024,  # 4MB
        description="最大发送消息长度"
    )

    # 健康检查
    enable_health_check: bool = Field(default=True, description="启用健康检查")
    enable_reflection: bool = Field(default=True, description="启用反射")

class SecuritySettings(BaseSettings):
    """安全配置"""

    # JWT 配置
    jwt_secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="JWT 密钥"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT 算法")
    jwt_expiration_hours: int = Field(default=24, description="JWT 过期时间(小时)")

    # 加密配置
    encryption_key: Optional[str] = Field(
        default=None,
        description="数据加密密钥"
    )

    # CORS 配置
    cors_origins: List[str] = Field(
        default=["*"],
        description="允许的 CORS 源"
    )

class IPFSSettings(BaseSettings):
    """IPFS配置"""

    node_url: str = Field(default="http://localhost:5001", description="IPFS节点URL")
    timeout: int = Field(default=30, description="请求超时时间")
    chunk_size: int = Field(default=1024 * 1024, description="数据块大小")  # 1MB

class MonitoringSettings(BaseSettings):
    """监控配置"""

    # Prometheus 配置
    enable_metrics: bool = Field(default=True, description="启用指标收集")
    metrics_port: int = Field(default=9090, description="指标端口")

    # OpenTelemetry 配置
    enable_tracing: bool = Field(default=True, description="启用链路追踪")
    jaeger_endpoint: Optional[str] = Field(
        default=None,
        description="Jaeger 端点"
    )

    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_format: str = Field(default="json", description="日志格式")
    log_file: Optional[str] = Field(default=None, description="日志文件路径")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """验证日志级别"""
        allowed_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in allowed_levels:
            raise ValueError(f"Log level must be one of {allowed_levels}")
        return v.upper()

class Settings(BaseSettings):
    """主配置类"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    # 应用基本信息
    app_name: str = Field(default="SuoKe Blockchain Service", description="应用名称")
    app_version: str = Field(default="0.1.0", description="应用版本")
    debug: bool = Field(default=False, description="调试模式")
    environment: str = Field(default="development", description="运行环境")

    # 子配置
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    blockchain: BlockchainSettings = Field(default_factory=BlockchainSettings)
    grpc: GRPCSettings = Field(default_factory=GRPCSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    ipfs: IPFSSettings = Field(default_factory=IPFSSettings)

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """验证环境配置"""
        allowed_envs = {"development", "testing", "staging", "production", "test"}
        if v.lower() not in allowed_envs:
            raise ValueError(f"Environment must be one of {allowed_envs}")
        return v.lower()

    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.environment == "development"

# 全局配置实例
settings = Settings()

def get_settings() -> Settings:
    """获取配置实例"""
    return settings
