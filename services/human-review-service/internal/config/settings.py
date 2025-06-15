"""
人工审核服务配置管理

统一管理服务的所有配置项，支持环境变量覆盖和多环境配置
"""
import os
from functools import lru_cache
from typing import Any, Dict, List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """数据库配置"""
    
    url: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/human_review",
        description="数据库连接URL"
    )
    pool_size: int = Field(default=10, description="连接池大小")
    max_overflow: int = Field(default=20, description="连接池最大溢出")
    pool_timeout: int = Field(default=30, description="连接池超时时间")
    pool_recycle: int = Field(default=3600, description="连接回收时间")
    echo: bool = Field(default=False, description="是否打印SQL语句")
    
    class Config:
        env_prefix = "DB_"


class RedisSettings(BaseSettings):
    """Redis配置"""
    
    url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis连接URL"
    )
    max_connections: int = Field(default=100, description="最大连接数")
    retry_on_timeout: bool = Field(default=True, description="超时重试")
    socket_timeout: int = Field(default=5, description="Socket超时时间")
    
    class Config:
        env_prefix = "REDIS_"


class CelerySettings(BaseSettings):
    """Celery配置"""
    
    broker_url: str = Field(
        default="redis://localhost:6379/1",
        description="消息代理URL"
    )
    result_backend: str = Field(
        default="redis://localhost:6379/2",
        description="结果后端URL"
    )
    task_serializer: str = Field(default="json", description="任务序列化器")
    result_serializer: str = Field(default="json", description="结果序列化器")
    accept_content: List[str] = Field(default=["json"], description="接受的内容类型")
    timezone: str = Field(default="Asia/Shanghai", description="时区")
    enable_utc: bool = Field(default=True, description="启用UTC")
    task_routes: Dict[str, Dict[str, str]] = Field(
        default={
            "internal.tasks.ai_tasks.*": {"queue": "ai_analysis"},
            "internal.tasks.review_tasks.*": {"queue": "review"},
            "internal.tasks.workflow_tasks.*": {"queue": "workflow"},
        },
        description="任务路由配置"
    )
    
    class Config:
        env_prefix = "CELERY_"


class AISettings(BaseSettings):
    """AI引擎配置"""
    
    # 文本分析模型
    text_model_name: str = Field(
        default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        description="文本分析模型名称"
    )
    text_model_cache_dir: str = Field(
        default="./models/text",
        description="文本模型缓存目录"
    )
    
    # 图像分析模型
    image_model_name: str = Field(
        default="microsoft/DiT-base-finetuned-ade-512-512",
        description="图像分析模型名称"
    )
    image_model_cache_dir: str = Field(
        default="./models/image",
        description="图像模型缓存目录"
    )
    
    # 风险评估配置
    risk_threshold_high: float = Field(default=0.8, description="高风险阈值")
    risk_threshold_medium: float = Field(default=0.5, description="中风险阈值")
    risk_threshold_low: float = Field(default=0.2, description="低风险阈值")
    
    # GPU配置
    use_gpu: bool = Field(default=False, description="是否使用GPU")
    gpu_device: str = Field(default="cuda:0", description="GPU设备")
    
    # 批处理配置
    batch_size: int = Field(default=32, description="批处理大小")
    max_sequence_length: int = Field(default=512, description="最大序列长度")
    
    class Config:
        env_prefix = "AI_"


class WorkflowSettings(BaseSettings):
    """工作流配置"""
    
    # 审核员配置
    max_concurrent_tasks: int = Field(default=5, description="审核员最大并发任务数")
    task_timeout: int = Field(default=3600, description="任务超时时间（秒）")
    auto_assign_enabled: bool = Field(default=True, description="是否启用自动分配")
    
    # 质量控制配置
    quality_check_enabled: bool = Field(default=True, description="是否启用质量检查")
    quality_threshold: float = Field(default=0.85, description="质量阈值")
    double_review_threshold: float = Field(default=0.7, description="双重审核阈值")
    
    # 优先级配置
    priority_weights: Dict[str, float] = Field(
        default={
            "medical_diagnosis": 1.0,
            "health_advice": 0.8,
            "user_content": 0.6,
            "multimedia": 0.4,
        },
        description="优先级权重配置"
    )
    
    class Config:
        env_prefix = "WORKFLOW_"


class SecuritySettings(BaseSettings):
    """安全配置"""
    
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="应用密钥"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT算法")
    jwt_expire_minutes: int = Field(default=30, description="JWT过期时间（分钟）")
    
    # CORS配置
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="CORS允许的源"
    )
    cors_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE"],
        description="CORS允许的方法"
    )
    
    # 加密配置
    encryption_key: Optional[str] = Field(default=None, description="数据加密密钥")
    hash_rounds: int = Field(default=12, description="密码哈希轮数")
    
    class Config:
        env_prefix = "SECURITY_"


class MonitoringSettings(BaseSettings):
    """监控配置"""
    
    # Prometheus配置
    metrics_enabled: bool = Field(default=True, description="是否启用指标收集")
    metrics_port: int = Field(default=9090, description="指标端口")
    
    # OpenTelemetry配置
    tracing_enabled: bool = Field(default=True, description="是否启用链路追踪")
    tracing_endpoint: str = Field(
        default="http://localhost:4317",
        description="链路追踪端点"
    )
    
    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式"
    )
    
    # Sentry配置
    sentry_dsn: Optional[str] = Field(default=None, description="Sentry DSN")
    sentry_environment: str = Field(default="development", description="Sentry环境")
    
    class Config:
        env_prefix = "MONITORING_"


class StorageSettings(BaseSettings):
    """存储配置"""
    
    # 文件存储类型
    storage_type: str = Field(default="local", description="存储类型: local, s3, minio")
    
    # 本地存储配置
    local_storage_path: str = Field(default="./storage", description="本地存储路径")
    
    # S3配置
    s3_bucket: Optional[str] = Field(default=None, description="S3存储桶")
    s3_region: Optional[str] = Field(default=None, description="S3区域")
    s3_access_key: Optional[str] = Field(default=None, description="S3访问密钥")
    s3_secret_key: Optional[str] = Field(default=None, description="S3密钥")
    
    # MinIO配置
    minio_endpoint: Optional[str] = Field(default=None, description="MinIO端点")
    minio_access_key: Optional[str] = Field(default=None, description="MinIO访问密钥")
    minio_secret_key: Optional[str] = Field(default=None, description="MinIO密钥")
    minio_bucket: Optional[str] = Field(default=None, description="MinIO存储桶")
    
    class Config:
        env_prefix = "STORAGE_"


class Settings(BaseSettings):
    """主配置类"""
    
    # 基本配置
    app_name: str = Field(default="人工审核服务", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    environment: str = Field(default="development", description="运行环境")
    debug: bool = Field(default=False, description="调试模式")
    
    # 服务配置
    host: str = Field(default="0.0.0.0", description="服务主机")
    port: int = Field(default=8000, description="服务端口")
    workers: int = Field(default=1, description="工作进程数")
    
    # gRPC配置
    grpc_enabled: bool = Field(default=True, description="是否启用gRPC")
    grpc_port: int = Field(default=50051, description="gRPC端口")
    
    # 子配置
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    celery: CelerySettings = Field(default_factory=CelerySettings)
    ai: AISettings = Field(default_factory=AISettings)
    workflow: WorkflowSettings = Field(default_factory=WorkflowSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    
    @validator("environment")
    def validate_environment(cls, v: str) -> str:
        """验证环境配置"""
        allowed_envs = ["development", "testing", "staging", "production"]
        if v not in allowed_envs:
            raise ValueError(f"环境必须是以下之一: {allowed_envs}")
        return v
    
    @validator("workers")
    def validate_workers(cls, v: int) -> int:
        """验证工作进程数"""
        if v < 1:
            raise ValueError("工作进程数必须大于0")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings()


def get_database_url() -> str:
    """获取数据库连接URL"""
    settings = get_settings()
    return settings.database.url


def get_redis_url() -> str:
    """获取Redis连接URL"""
    settings = get_settings()
    return settings.redis.url


def is_production() -> bool:
    """判断是否为生产环境"""
    settings = get_settings()
    return settings.environment == "production"


def is_development() -> bool:
    """判断是否为开发环境"""
    settings = get_settings()
    return settings.environment == "development" 