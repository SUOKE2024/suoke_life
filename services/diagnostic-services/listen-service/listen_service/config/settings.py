"""
配置管理模块

管理应用程序的所有配置设置。
"""

import os
from functools import lru_cache
from typing import Any, Dict, List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """数据库配置"""
    # Redis配置
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_max_connections: int = Field(default=20, env="REDIS_MAX_CONNECTIONS")
    
    # MongoDB配置（可选）
    mongodb_url: Optional[str] = Field(default=None, env="MONGODB_URL")
    mongodb_database: str = Field(default="listen_service", env="MONGODB_DATABASE")


class CacheSettings(BaseSettings):
    """缓存配置"""
    backend: str = Field(default="memory", env="CACHE_BACKEND")  # memory, redis
    default_ttl: int = Field(default=3600, env="CACHE_DEFAULT_TTL")
    max_size: int = Field(default=1000, env="CACHE_MAX_SIZE")
    
    # Redis缓存配置
    redis_prefix: str = Field(default="listen_service:", env="CACHE_REDIS_PREFIX")
    
    @validator('backend')
    def validate_backend(cls, v):
        if v not in ['memory', 'redis']:
            raise ValueError('缓存后端必须是 memory 或 redis')
        return v


class LoggingSettings(BaseSettings):
    """日志配置"""
    level: str = Field(default="INFO", env="LOG_LEVEL")
    format: str = Field(default="json", env="LOG_FORMAT")  # json, console, plain
    file_path: Optional[str] = Field(default=None, env="LOG_FILE_PATH")
    max_file_size: str = Field(default="100MB", env="LOG_MAX_FILE_SIZE")
    backup_count: int = Field(default=5, env="LOG_BACKUP_COUNT")
    
    # 结构化日志配置
    include_timestamp: bool = Field(default=True, env="LOG_INCLUDE_TIMESTAMP")
    include_level: bool = Field(default=True, env="LOG_INCLUDE_LEVEL")
    include_logger_name: bool = Field(default=True, env="LOG_INCLUDE_LOGGER_NAME")
    include_thread_name: bool = Field(default=False, env="LOG_INCLUDE_THREAD_NAME")
    
    @validator('level')
    def validate_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'日志级别必须是: {", ".join(valid_levels)}')
        return v.upper()
    
    @validator('format')
    def validate_format(cls, v):
        if v not in ['json', 'console', 'plain']:
            raise ValueError('日志格式必须是 json, console 或 plain')
        return v


class SecuritySettings(BaseSettings):
    """安全配置"""
    auth_enabled: bool = Field(default=False, env="AUTH_ENABLED")
    secret_key: str = Field(default="your-secret-key-change-in-production", env="AUTH_SECRET_KEY")
    algorithm: str = Field(default="HS256", env="AUTH_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="AUTH_ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # API密钥配置
    api_keys: List[str] = Field(default_factory=list, env="API_KEYS")
    
    # CORS配置
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    cors_methods: List[str] = Field(default=["*"], env="CORS_METHODS")
    cors_headers: List[str] = Field(default=["*"], env="CORS_HEADERS")
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError('密钥长度至少为32个字符')
        return v


class AudioProcessingSettings(BaseSettings):
    """音频处理配置"""
    # 基本参数
    sample_rate: int = Field(default=22050, env="AUDIO_SAMPLE_RATE")
    n_mfcc: int = Field(default=13, env="AUDIO_N_MFCC")
    n_fft: int = Field(default=2048, env="AUDIO_N_FFT")
    hop_length: int = Field(default=512, env="AUDIO_HOP_LENGTH")
    n_mels: int = Field(default=128, env="AUDIO_N_MELS")
    
    # 文件限制
    max_file_size: int = Field(default=50*1024*1024, env="AUDIO_MAX_FILE_SIZE")  # 50MB
    max_duration: float = Field(default=300.0, env="AUDIO_MAX_DURATION")  # 5分钟
    min_duration: float = Field(default=0.5, env="AUDIO_MIN_DURATION")  # 0.5秒
    
    # 支持的格式
    supported_formats: List[str] = Field(
        default=["wav", "mp3", "flac", "aac", "ogg", "m4a"],
        env="AUDIO_SUPPORTED_FORMATS"
    )
    
    # 预处理选项
    normalize_audio: bool = Field(default=True, env="AUDIO_NORMALIZE")
    remove_silence: bool = Field(default=True, env="AUDIO_REMOVE_SILENCE")
    preemphasis_coeff: float = Field(default=0.97, env="AUDIO_PREEMPHASIS_COEFF")
    
    @validator('hop_length')
    def validate_hop_length(cls, v, values):
        if 'n_fft' in values and v >= values['n_fft']:
            raise ValueError('hop_length必须小于n_fft')
        return v


class TCMSettings(BaseSettings):
    """中医分析配置"""
    enable_constitution_analysis: bool = Field(default=True, env="TCM_ENABLE_CONSTITUTION")
    enable_emotion_analysis: bool = Field(default=True, env="TCM_ENABLE_EMOTION")
    enable_organ_analysis: bool = Field(default=True, env="TCM_ENABLE_ORGAN")
    
    # 分析阈值
    constitution_threshold: float = Field(default=0.6, env="TCM_CONSTITUTION_THRESHOLD")
    emotion_threshold: float = Field(default=0.5, env="TCM_EMOTION_THRESHOLD")
    organ_threshold: float = Field(default=0.4, env="TCM_ORGAN_THRESHOLD")
    
    # 置信度设置
    min_confidence: float = Field(default=0.3, env="TCM_MIN_CONFIDENCE")
    high_confidence: float = Field(default=0.8, env="TCM_HIGH_CONFIDENCE")
    
    # 知识库配置
    knowledge_base_path: Optional[str] = Field(default=None, env="TCM_KNOWLEDGE_BASE_PATH")
    use_external_knowledge: bool = Field(default=False, env="TCM_USE_EXTERNAL_KNOWLEDGE")


class PerformanceSettings(BaseSettings):
    """性能配置"""
    # 并发设置
    max_workers: int = Field(default=4, env="MAX_WORKERS")
    thread_pool_size: int = Field(default=8, env="THREAD_POOL_SIZE")
    
    # 超时设置
    request_timeout: float = Field(default=30.0, env="REQUEST_TIMEOUT")
    analysis_timeout: float = Field(default=60.0, env="ANALYSIS_TIMEOUT")
    
    # 内存限制
    max_memory_usage: int = Field(default=1024*1024*1024, env="MAX_MEMORY_USAGE")  # 1GB
    
    # 批处理设置
    batch_size: int = Field(default=10, env="BATCH_SIZE")
    max_batch_size: int = Field(default=50, env="MAX_BATCH_SIZE")
    
    # 监控设置
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")


class ServerSettings(BaseSettings):
    """服务器配置"""
    # HTTP服务器
    host: str = Field(default="0.0.0.0", env="LISTEN_SERVICE_HOST")
    port: int = Field(default=8004, env="LISTEN_SERVICE_PORT")
    
    # gRPC服务器
    grpc_host: str = Field(default="0.0.0.0", env="LISTEN_SERVICE_GRPC_HOST")
    grpc_port: int = Field(default=50051, env="LISTEN_SERVICE_GRPC_PORT")
    
    # 服务器选项
    reload: bool = Field(default=False, env="SERVER_RELOAD")
    debug: bool = Field(default=False, env="DEBUG")
    workers: int = Field(default=1, env="SERVER_WORKERS")
    
    # 健康检查
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    
    @validator('port', 'grpc_port')
    def validate_port(cls, v):
        if not 1024 <= v <= 65535:
            raise ValueError('端口号必须在1024-65535之间')
        return v


class MonitoringSettings(BaseSettings):
    """监控配置"""
    # Prometheus配置
    enable_prometheus: bool = Field(default=True, env="ENABLE_PROMETHEUS")
    prometheus_port: int = Field(default=9090, env="PROMETHEUS_PORT")
    
    # 健康检查配置
    health_check_enabled: bool = Field(default=True, env="HEALTH_CHECK_ENABLED")
    health_check_timeout: float = Field(default=5.0, env="HEALTH_CHECK_TIMEOUT")
    
    # 性能监控
    enable_performance_monitoring: bool = Field(default=True, env="ENABLE_PERFORMANCE_MONITORING")
    performance_sample_rate: float = Field(default=0.1, env="PERFORMANCE_SAMPLE_RATE")
    
    # 错误追踪
    enable_error_tracking: bool = Field(default=True, env="ENABLE_ERROR_TRACKING")
    error_reporting_url: Optional[str] = Field(default=None, env="ERROR_REPORTING_URL")


class Settings(BaseSettings):
    """主配置类"""
    # 应用信息
    app_name: str = Field(default="索克生活闻诊服务", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # 子配置
    database: DatabaseSettings = DatabaseSettings()
    cache: CacheSettings = CacheSettings()
    logging: LoggingSettings = LoggingSettings()
    security: SecuritySettings = SecuritySettings()
    audio: AudioProcessingSettings = AudioProcessingSettings()
    tcm: TCMSettings = TCMSettings()
    performance: PerformanceSettings = PerformanceSettings()
    server: ServerSettings = ServerSettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    
    # 开发配置
    debug: bool = Field(default=False, env="DEBUG")
    testing: bool = Field(default=False, env="TESTING")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @validator('environment')
    def validate_environment(cls, v):
        valid_envs = ['development', 'testing', 'staging', 'production']
        if v not in valid_envs:
            raise ValueError(f'环境必须是: {", ".join(valid_envs)}')
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
        return self.environment == "testing" or self.testing
    
    def get_database_url(self) -> str:
        """获取数据库URL"""
        return self.database.redis_url
    
    def get_cache_config(self) -> Dict[str, Any]:
        """获取缓存配置"""
        return {
            "backend": self.cache.backend,
            "default_ttl": self.cache.default_ttl,
            "max_size": self.cache.max_size,
            "redis_url": self.database.redis_url if self.cache.backend == "redis" else None,
            "redis_prefix": self.cache.redis_prefix
        }
    
    def get_audio_config(self) -> Dict[str, Any]:
        """获取音频处理配置"""
        return {
            "sample_rate": self.audio.sample_rate,
            "n_mfcc": self.audio.n_mfcc,
            "n_fft": self.audio.n_fft,
            "hop_length": self.audio.hop_length,
            "n_mels": self.audio.n_mels,
            "normalize": self.audio.normalize_audio,
            "remove_silence": self.audio.remove_silence,
            "preemphasis": self.audio.preemphasis_coeff
        }
    
    def get_tcm_config(self) -> Dict[str, Any]:
        """获取中医分析配置"""
        return {
            "enable_constitution": self.tcm.enable_constitution_analysis,
            "enable_emotion": self.tcm.enable_emotion_analysis,
            "enable_organ": self.tcm.enable_organ_analysis,
            "constitution_threshold": self.tcm.constitution_threshold,
            "emotion_threshold": self.tcm.emotion_threshold,
            "organ_threshold": self.tcm.organ_threshold,
            "min_confidence": self.tcm.min_confidence,
            "high_confidence": self.tcm.high_confidence
        }
    
    def get_cors_origins(self) -> List[str]:
        """获取CORS允许的源"""
        return self.security.cors_origins
    
    def get_upload_dir(self) -> str:
        """获取上传目录"""
        return os.path.join(os.getcwd(), "uploads")
    
    def get_log_dir(self) -> str:
        """获取日志目录"""
        return os.path.join(os.getcwd(), "logs")
    
    def get_cache_dir(self) -> str:
        """获取缓存目录"""
        return os.path.join(os.getcwd(), "cache")
    
    def get_temp_dir(self) -> str:
        """获取临时目录"""
        return os.path.join(os.getcwd(), "temp")
    
    def get_rest_config(self) -> Dict[str, Any]:
        """获取REST API配置"""
        return {
            "host": self.server.host,
            "port": self.server.port,
            "reload": self.server.reload,
            "workers": self.server.workers,
            "log_level": self.logging.level.lower()
        }
    
    def get_grpc_config(self) -> Dict[str, Any]:
        """获取gRPC配置"""
        return {
            "enabled": True,  # 默认启用gRPC
            "host": self.server.grpc_host,
            "port": self.server.grpc_port
        }
    
    def get_metrics_config(self) -> Dict[str, Any]:
        """获取监控配置"""
        return {
            "enabled": self.monitoring.enable_prometheus,
            "port": self.monitoring.prometheus_port,
            "enable_performance_monitoring": self.monitoring.enable_performance_monitoring,
            "performance_sample_rate": self.monitoring.performance_sample_rate
        }


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings()


def reload_settings() -> Settings:
    """重新加载配置"""
    get_settings.cache_clear()
    return get_settings()