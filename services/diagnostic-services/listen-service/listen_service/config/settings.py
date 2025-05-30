"""
现代化配置管理

使用 Pydantic Settings 进行配置管理，支持环境变量、配置文件和默认值。
专为 Python 3.13.3 和生产环境优化。
"""

from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """环境类型"""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """日志级别"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AudioProcessingSettings(BaseSettings):
    """音频处理配置"""

    model_config = SettingsConfigDict(
        env_prefix="AUDIO_",
        case_sensitive=False,
    )

    # 基础音频参数
    sample_rate: int = Field(default=16000, description="目标采样率")
    frame_length: int = Field(default=2048, description="帧长度")
    hop_length: int = Field(default=512, description="跳跃长度")
    n_mels: int = Field(default=128, description="梅尔频谱数量")
    n_mfcc: int = Field(default=13, description="MFCC 系数数量")

    # 音频限制
    max_duration: float = Field(default=300.0, description="最大音频时长（秒）")
    min_duration: float = Field(default=0.5, description="最小音频时长（秒）")
    max_file_size: int = Field(
        default=100 * 1024 * 1024, description="最大文件大小（字节）"
    )

    # 处理选项
    enable_gpu: bool = Field(default=True, description="启用GPU加速")
    enable_enhancement: bool = Field(default=True, description="启用音频增强")
    enable_vad: bool = Field(default=True, description="启用语音活动检测")
    batch_size: int = Field(default=32, description="批处理大小")
    max_concurrent_tasks: int = Field(default=8, description="最大并发任务数")

    # VAD 配置
    vad_aggressiveness: int = Field(default=2, ge=0, le=3, description="VAD 敏感度")
    vad_frame_duration: int = Field(default=30, description="VAD 帧时长（毫秒）")

    @field_validator("sample_rate")
    @classmethod
    def validate_sample_rate(cls, v):
        if v not in [8000, 16000, 22050, 44100, 48000]:
            raise ValueError("采样率必须是标准值之一")
        return v


class TCMAnalysisSettings(BaseSettings):
    """中医分析配置"""

    model_config = SettingsConfigDict(
        env_prefix="TCM_",
        case_sensitive=False,
    )

    # 中医分析开关
    enabled: bool = Field(default=True, description="启用中医分析")
    constitution_analysis: bool = Field(default=True, description="体质分析")
    emotion_analysis: bool = Field(default=True, description="情绪分析")
    organ_analysis: bool = Field(default=True, description="脏腑分析")

    # 体质类型
    constitution_types: list[str] = Field(
        default=[
            "平和质",
            "气虚质",
            "阳虚质",
            "阴虚质",
            "痰湿质",
            "湿热质",
            "血瘀质",
            "气郁质",
            "特禀质",
        ],
        description="支持的体质类型",
    )

    # 五志情绪
    emotion_types: list[str] = Field(
        default=["喜", "怒", "忧", "思", "恐"], description="五志情绪类型"
    )

    # 五脏六腑
    organ_types: list[str] = Field(
        default=[
            "心",
            "肝",
            "脾",
            "肺",
            "肾",
            "胆",
            "胃",
            "小肠",
            "大肠",
            "膀胱",
            "三焦",
        ],
        description="脏腑类型",
    )

    # 置信度阈值
    min_confidence: float = Field(default=0.6, ge=0.0, le=1.0, description="最小置信度")

    # 模型路径
    constitution_model_path: str | None = Field(
        default=None, description="体质分析模型路径"
    )
    emotion_model_path: str | None = Field(
        default=None, description="情绪分析模型路径"
    )


class CacheSettings(BaseSettings):
    """缓存配置"""

    model_config = SettingsConfigDict(
        env_prefix="CACHE_",
        case_sensitive=False,
    )

    # Redis 配置
    redis_url: str = Field(
        default="redis://localhost:6379/0", description="Redis 连接URL"
    )
    redis_password: str | None = Field(default=None, description="Redis 密码")
    redis_db: int = Field(default=0, description="Redis 数据库编号")

    # 缓存策略
    enabled: bool = Field(default=True, description="启用缓存")
    default_ttl: int = Field(default=3600, description="默认缓存时间（秒）")
    max_memory: str = Field(default="512mb", description="最大内存使用")

    # 缓存键前缀
    key_prefix: str = Field(default="listen_service:", description="缓存键前缀")

    # 连接池配置
    max_connections: int = Field(default=20, description="最大连接数")
    retry_on_timeout: bool = Field(default=True, description="超时重试")


class DatabaseSettings(BaseSettings):
    """数据库配置"""

    model_config = SettingsConfigDict(
        env_prefix="DB_",
        case_sensitive=False,
    )

    # MongoDB 配置
    mongodb_url: str = Field(
        default="mongodb://localhost:27017/listen_service",
        description="MongoDB 连接URL",
    )
    mongodb_username: str | None = Field(default=None, description="MongoDB 用户名")
    mongodb_password: str | None = Field(default=None, description="MongoDB 密码")

    # 连接池配置
    max_pool_size: int = Field(default=100, description="最大连接池大小")
    min_pool_size: int = Field(default=10, description="最小连接池大小")
    max_idle_time: int = Field(default=30000, description="最大空闲时间（毫秒）")

    # 集合名称
    audio_collection: str = Field(default="audio_analysis", description="音频分析集合")
    user_collection: str = Field(default="users", description="用户集合")
    session_collection: str = Field(default="sessions", description="会话集合")


class ServerSettings(BaseSettings):
    """服务器配置"""

    model_config = SettingsConfigDict(
        env_prefix="SERVER_",
        case_sensitive=False,
    )

    # 服务器基础配置
    host: str = Field(default="0.0.0.0", description="服务器主机")
    port: int = Field(default=50052, description="服务器端口")
    workers: int = Field(default=4, description="工作进程数")

    # gRPC 配置
    max_workers: int = Field(default=16, description="最大工作线程数")
    max_concurrent_rpcs: int = Field(default=200, description="最大并发RPC数")
    max_message_length: int = Field(
        default=100 * 1024 * 1024, description="最大消息长度"
    )

    # 超时配置
    request_timeout: int = Field(default=300, description="请求超时时间（秒）")
    keepalive_time: int = Field(default=30, description="保活时间（秒）")
    keepalive_timeout: int = Field(default=5, description="保活超时（秒）")

    # 安全配置
    enable_reflection: bool = Field(default=False, description="启用gRPC反射")
    enable_health_check: bool = Field(default=True, description="启用健康检查")

    # 优雅关闭
    grace_period: int = Field(default=10, description="优雅关闭等待时间（秒）")


class MonitoringSettings(BaseSettings):
    """监控配置"""

    model_config = SettingsConfigDict(
        env_prefix="MONITORING_",
        case_sensitive=False,
    )

    # Prometheus 配置
    prometheus_enabled: bool = Field(default=True, description="启用Prometheus指标")
    prometheus_port: int = Field(default=9090, description="Prometheus端口")
    metrics_path: str = Field(default="/metrics", description="指标路径")

    # 健康检查
    health_check_enabled: bool = Field(default=True, description="启用健康检查")
    health_check_interval: int = Field(default=30, description="健康检查间隔（秒）")

    # 性能监控
    performance_monitoring: bool = Field(default=True, description="启用性能监控")
    slow_request_threshold: float = Field(default=5.0, description="慢请求阈值（秒）")

    # 告警配置
    alert_enabled: bool = Field(default=False, description="启用告警")
    alert_webhook_url: str | None = Field(
        default=None, description="告警Webhook URL"
    )


class LoggingSettings(BaseSettings):
    """日志配置"""

    model_config = SettingsConfigDict(
        env_prefix="LOG_",
        case_sensitive=False,
    )

    # 日志级别
    level: LogLevel = Field(default=LogLevel.INFO, description="日志级别")

    # 日志格式
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式",
    )

    # 日志输出
    console_enabled: bool = Field(default=True, description="控制台输出")
    file_enabled: bool = Field(default=True, description="文件输出")

    # 文件配置
    file_path: str = Field(
        default="logs/listen_service.log", description="日志文件路径"
    )
    max_file_size: str = Field(default="100MB", description="最大文件大小")
    backup_count: int = Field(default=5, description="备份文件数量")

    # 结构化日志
    json_format: bool = Field(default=True, description="JSON格式输出")
    include_trace: bool = Field(default=False, description="包含堆栈跟踪")


class SecuritySettings(BaseSettings):
    """安全配置"""

    model_config = SettingsConfigDict(
        env_prefix="SECURITY_",
        case_sensitive=False,
    )

    # API 密钥
    api_key: str | None = Field(default=None, description="API密钥")
    api_key_header: str = Field(default="X-API-Key", description="API密钥头部")

    # JWT 配置
    jwt_secret: str | None = Field(default=None, description="JWT密钥")
    jwt_algorithm: str = Field(default="HS256", description="JWT算法")
    jwt_expiration: int = Field(default=3600, description="JWT过期时间（秒）")

    # 速率限制
    rate_limit_enabled: bool = Field(default=True, description="启用速率限制")
    rate_limit_requests: int = Field(default=100, description="速率限制请求数")
    rate_limit_window: int = Field(default=60, description="速率限制时间窗口（秒）")

    # CORS 配置
    cors_enabled: bool = Field(default=True, description="启用CORS")
    cors_origins: list[str] = Field(default=["*"], description="允许的源")

    # 数据加密
    encryption_enabled: bool = Field(default=False, description="启用数据加密")
    encryption_key: str | None = Field(default=None, description="加密密钥")


class Settings(BaseSettings):
    """主配置类"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # 环境配置
    environment: Environment = Field(
        default=Environment.DEVELOPMENT, description="运行环境"
    )
    debug: bool = Field(default=False, description="调试模式")

    # 应用信息
    app_name: str = Field(default="Listen Service", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    app_description: str = Field(
        default="索克生活闻诊服务 - 中医四诊中的听觉感知与音频分析微服务",
        description="应用描述",
    )

    # 子配置
    audio: AudioProcessingSettings = Field(default_factory=AudioProcessingSettings)
    tcm: TCMAnalysisSettings = Field(default_factory=TCMAnalysisSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    server: ServerSettings = Field(default_factory=ServerSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)

    @computed_field
    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.environment == Environment.PRODUCTION

    @computed_field
    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.environment == Environment.DEVELOPMENT

    @computed_field
    @property
    def log_config(self) -> dict[str, Any]:
        """日志配置字典"""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": self.logging.format,
                },
                "json": {
                    "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json" if self.logging.json_format else "default",
                    "level": self.logging.level.value,
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": self.logging.file_path,
                    "maxBytes": self._parse_size(self.logging.max_file_size),
                    "backupCount": self.logging.backup_count,
                    "formatter": "json" if self.logging.json_format else "default",
                    "level": self.logging.level.value,
                },
            },
            "root": {
                "level": self.logging.level.value,
                "handlers": self._get_log_handlers(),
            },
        }

    def _parse_size(self, size_str: str) -> int:
        """解析大小字符串"""
        size_str = size_str.upper()
        if size_str.endswith("KB"):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith("MB"):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith("GB"):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)

    def _get_log_handlers(self) -> list[str]:
        """获取日志处理器列表"""
        handlers = []
        if self.logging.console_enabled:
            handlers.append("console")
        if self.logging.file_enabled:
            handlers.append("file")
        return handlers

    def create_log_directory(self) -> None:
        """创建日志目录"""
        log_path = Path(self.logging.file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)

    def validate_settings(self) -> list[str]:
        """验证配置"""
        errors = []

        # 验证端口范围
        if not (1024 <= self.server.port <= 65535):
            errors.append("服务器端口必须在 1024-65535 范围内")

        # 验证Redis URL
        if self.cache.enabled and not self.cache.redis_url:
            errors.append("启用缓存时必须提供 Redis URL")

        # 验证生产环境配置
        if self.is_production:
            if self.debug:
                errors.append("生产环境不应启用调试模式")
            if not self.security.api_key:
                errors.append("生产环境必须设置 API 密钥")

        return errors


@lru_cache
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    settings = Settings()

    # 创建必要的目录
    settings.create_log_directory()

    # 验证配置
    errors = settings.validate_settings()
    if errors:
        raise ValueError(f"配置验证失败: {'; '.join(errors)}")

    return settings


def reload_settings() -> Settings:
    """重新加载配置"""
    get_settings.cache_clear()
    return get_settings()
