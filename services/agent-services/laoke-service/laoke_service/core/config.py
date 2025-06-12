"""老克智能体服务配置管理模块"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from loguru import logger
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseModel):
    """数据库配置"""

    type: str = "sqlite"
    sqlite_path: str = "data/laoke.db"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "laoke"
    postgres_password: str = ""
    postgres_database: str = "laoke_service"
    pool_size: int = 10
    ssl_mode: str = "disable"


class CacheConfig(BaseModel):
    """缓存配置"""

    backend: str = "memory"
    redis_url: str = "redis://localhost:6379"
    redis_db: int = 0
    redis_password: str = ""
    default_ttl: int = 3600
    max_memory_items: int = 10000
    key_prefix: str = "laoke:"


class AIModelConfig(BaseModel):
    """AI模型配置"""

    primary_model: str = "gpt-4o-mini"
    fallback_model: str = "llama-3-8b"
    api_key: str = ""
    base_url: str = "https://api.openai.com/v1"
    timeout: int = 30
    max_retries: int = 3
    temperature: float = 0.7
    max_tokens: int = 4096


class ConversationConfig(BaseModel):
    """对话配置"""

    system_prompt: str = """
你是老克，一位资深的中医专家和教育者，专注于中医知识传播、社群管理和教育内容创建。

你的核心职责：
1. 传播准确的中医知识，包括理论、诊断、治疗方法等
2. 管理中医学习社群，促进成员间的交流和学习
3. 创建高质量的中医教育内容，适合不同水平的学习者
4. 提供个性化的中医学习路径和建议

你的特点：
- 知识渊博，对中医经典和现代应用都有深入理解
- 善于教学，能够将复杂的概念简化为易懂的内容
- 耐心细致，关注每个学习者的需求和进步
- 严谨负责，确保传播的知识准确可靠

请始终保持专业、友善和耐心的态度，用通俗易懂的语言回答问题。
"""
    max_history_turns: int = 20
    max_tokens_per_message: int = 4096


class AgentConfig(BaseModel):
    """智能体配置"""

    models: AIModelConfig = Field(default_factory=AIModelConfig)
    conversation: ConversationConfig = Field(default_factory=ConversationConfig)
    session_timeout: int = 3600
    max_concurrent_sessions: int = 1000
    cleanup_interval: int = 300


class ServerConfig(BaseModel):
    """服务器配置"""

    grpc_host: str = "0.0.0.0"
    grpc_port: int = 50051
    grpc_max_workers: int = 10
    grpc_max_message_length: int = 4194304

    rest_host: str = "0.0.0.0"
    rest_port: int = 8080
    rest_workers: int = 4

    cors_allowed_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allowed_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_allowed_headers: List[str] = ["*"]


class RateLimitRule(BaseModel):
    """速率限制规则"""

    requests: int
    window: int
    algorithm: str = "sliding_window"
    burst: Optional[int] = None


class RateLimitConfig(BaseModel):
    """速率限制配置"""

    global_rules: List[RateLimitRule] = Field(
        default_factory=lambda: [
            RateLimitRule(requests=100, window=60),
            RateLimitRule(requests=1000, window=3600),
        ]
    )
    user_rules: Dict[str, RateLimitRule] = Field(default_factory=dict)


class LoggingConfig(BaseModel):
    """日志配置"""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_enabled: bool = True
    file_path: str = "logs/laoke-service.log"
    file_max_size: str = "100MB"
    file_backup_count: int = 5
    console_enabled: bool = True
    console_colored: bool = True


class MetricsConfig(BaseModel):
    """指标配置"""

    enabled: bool = True
    port: int = 9090
    path: str = "/metrics"


class HealthConfig(BaseModel):
    """健康检查配置"""

    enabled: bool = True
    path: str = "/health"
    database_timeout: int = 5
    cache_timeout: int = 3
    llm_api_timeout: int = 10


class SecurityConfig(BaseModel):
    """安全配置"""

    api_key_enabled: bool = False
    api_key_header_name: str = "X-API-Key"
    api_keys: List[str] = Field(default_factory=list)

    jwt_enabled: bool = False
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600

    max_request_size: int = 1048576
    sanitize_html: bool = True
    check_sql_injection: bool = True


class ExternalServiceConfig(BaseModel):
    """外部服务配置"""

    knowledge_service_enabled: bool = True
    knowledge_service_url: str = "http://localhost:8081"
    knowledge_service_timeout: int = 10
    knowledge_service_api_key: str = ""

    user_service_enabled: bool = True
    user_service_url: str = "http://localhost:8082"
    user_service_timeout: int = 5
    user_service_api_key: str = ""

    accessibility_service_enabled: bool = True
    accessibility_service_url: str = "http://localhost:8083"
    accessibility_service_timeout: int = 5
    accessibility_service_api_key: str = ""


class FeaturesConfig(BaseModel):
    """特性开关配置"""

    enable_caching: bool = True
    enable_rate_limiting: bool = True
    enable_metrics: bool = True
    enable_tracing: bool = False
    enable_content_moderation: bool = True
    enable_learning_analytics: bool = True
    enable_accessibility: bool = True


class ServiceConfig(BaseModel):
    """服务基本配置"""

    name: str = "laoke-service"
    version: str = "1.0.0"
    debug: bool = False
    environment: str = "production"


class Config(BaseSettings):
    """老克智能体服务配置"""

    service: ServiceConfig = Field(default_factory=ServiceConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    metrics: MetricsConfig = Field(default_factory=MetricsConfig)
    health: HealthConfig = Field(default_factory=HealthConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    external_services: ExternalServiceConfig = Field(
        default_factory=ExternalServiceConfig
    )
    features: FeaturesConfig = Field(default_factory=FeaturesConfig)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
        case_sensitive = False
        extra = "allow"  # 允许额外字段

    @validator("service")
    def validate_service(cls, v):
        """验证服务配置"""
        if v.environment not in ["development", "testing", "production"]:
            raise ValueError(
                "environment must be one of: development, testing, production"
            )
        return v

    @validator("database")
    def validate_database(cls, v):
        """验证数据库配置"""
        if v.type not in ["sqlite", "postgres"]:
            raise ValueError("database type must be sqlite or postgres")
        return v

    @validator("cache")
    def validate_cache(cls, v):
        """验证缓存配置"""
        if v.backend not in ["memory", "redis"]:
            raise ValueError("cache backend must be memory or redis")
        return v


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/config.yaml"
        self._config: Optional[Config] = None

    def load_config(self) -> Config:
        """加载配置"""
        if self._config is None:
            self._config = self._load_from_sources()
        return self._config

    def _load_from_sources(self) -> Config:
        """从多个源加载配置"""
        # 1. 从YAML文件加载基础配置
        yaml_config = self._load_from_yaml()

        # 2. 从环境变量覆盖配置
        config = Config(**yaml_config)

        logger.info(f"配置加载完成: environment={config.service.environment}")
        return config

    def _load_from_yaml(self) -> Dict[str, Any]:
        """从YAML文件加载配置"""
        config_file = Path(self.config_path)

        if not config_file.exists():
            logger.warning(f"配置文件不存在: {config_file}, 使用默认配置")
            return {}

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                yaml_content = yaml.safe_load(f)
                logger.info(f"从YAML文件加载配置: {config_file}")
                return yaml_content or {}
        except Exception as e:
            logger.error(f"加载YAML配置文件失败: {e}")
            return {}

    def validate_config(self) -> bool:
        """验证配置"""
        try:
            config = self.load_config()

            # 验证必要的配置项
            if config.agent.models.api_key == "":
                logger.warning("AI模型API密钥未配置")

            if (
                config.database.type == "postgres"
                and config.database.postgres_password == ""
            ):
                logger.warning("PostgreSQL密码未配置")

            if config.cache.backend == "redis" and config.cache.redis_password == "":
                logger.warning("Redis密码未配置")

            logger.info("配置验证通过")
            return True

        except Exception as e:
            logger.error(f"配置验证失败: {e}")
            return False

    def get_database_url(self) -> str:
        """获取数据库连接URL"""
        config = self.load_config()

        if config.database.type == "sqlite":
            return f"sqlite:///{config.database.sqlite_path}"
        elif config.database.type == "postgres":
            return (
                f"postgresql://{config.database.postgres_user}:"
                f"{config.database.postgres_password}@"
                f"{config.database.postgres_host}:{config.database.postgres_port}/"
                f"{config.database.postgres_database}"
            )
        else:
            raise ValueError(f"不支持的数据库类型: {config.database.type}")

    def get_redis_url(self) -> str:
        """获取Redis连接URL"""
        config = self.load_config()

        if config.cache.backend != "redis":
            raise ValueError("缓存后端不是Redis")

        redis_url = config.cache.redis_url
        if config.cache.redis_password:
            # 在URL中添加密码
            if "://" in redis_url:
                protocol, rest = redis_url.split("://", 1)
                redis_url = f"{protocol}://:{config.cache.redis_password}@{rest}"

        return redis_url


# 全局配置管理器实例
config_manager = ConfigManager()


def get_config() -> Config:
    """获取配置实例"""
    return config_manager.load_config()


def validate_config() -> bool:
    """验证配置"""
    return config_manager.validate_config()
