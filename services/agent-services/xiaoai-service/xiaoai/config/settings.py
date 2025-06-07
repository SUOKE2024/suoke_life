#!/usr/bin/env python3
"""
小艾智能体配置设置模块
提供应用程序配置管理和环境变量处理
"""

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """应用程序配置设置"""

    # 服务基础配置
    service_name: str = Field(default="xiaoai-service", env="SERVICE_NAME")
    service_version: str = Field(default="1.0.0", env="SERVICE_VERSION")
    debug: bool = Field(default=False, env="DEBUG")

    # 服务器配置
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")

    # 数据库配置
    database_url: str = Field(
        default="postgresql://user:password@localhost:5432/xiaoai_db",
        env="DATABASE_URL"
    )
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")

    # JWT配置
    jwt_secret_key: str = Field(
        default="xiaoai-secret-key-change-in-production", env="JWT_SECRET_KEY"
    )
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=30, env="JWT_EXPIRE_MINUTES")

    # AI模型配置
    openai_api_key: str | None = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: str | None = Field(default=None, env="ANTHROPIC_API_KEY")
    deepseek_api_key: str | None = Field(default=None, env="DEEPSEEK_API_KEY")

    # 中医诊断配置
    tcm_model_path: str = Field(default="./models/tcm", env="TCM_MODEL_PATH")
    tongue_analysis_model: str = Field(
        default="./models/tongue_analysis.onnx", env="TONGUE_ANALYSIS_MODEL"
    )
    voice_analysis_model: str = Field(
        default="./models/voice_analysis.onnx", env="VOICE_ANALYSIS_MODEL"
    )

    # 多模态配置
    max_image_size: int = Field(default=10 * 1024 * 1024, env="MAX_IMAGE_SIZE")  # 10MB
    max_audio_duration: int = Field(default=300, env="MAX_AUDIO_DURATION")  # 5分钟
    supported_image_formats: list[str] = Field(
        default=["jpg", "jpeg", "png", "bmp"], env="SUPPORTED_IMAGE_FORMATS"
    )
    supported_audio_formats: list[str] = Field(
        default=["wav", "mp3", "m4a", "flac"], env="SUPPORTED_AUDIO_FORMATS"
    )

    # 无障碍服务配置
    accessibility_enabled: bool = Field(default=True, env="ACCESSIBILITY_ENABLED")
    sign_language_model: str = Field(
        default="./models/sign_language.onnx", env="SIGN_LANGUAGE_MODEL"
    )
    tts_service_url: str = Field(
        default="http://localhost:8080/tts", env="TTS_SERVICE_URL"
    )

    # 性能配置
    max_concurrent_sessions: int = Field(default=100, env="MAX_CONCURRENT_SESSIONS")
    session_timeout: int = Field(default=3600, env="SESSION_TIMEOUT")  # 1小时
    request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")  # 30秒

    # 监控配置
    metrics_enabled: bool = Field(default=True, env="METRICS_ENABLED")
    prometheus_port: int = Field(default=9090, env="PROMETHEUS_PORT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # 服务发现配置
    consul_host: str = Field(default="localhost", env="CONSUL_HOST")
    consul_port: int = Field(default=8500, env="CONSUL_PORT")
    service_name: str = Field(default="xiaoai-service", env="SERVICE_NAME")

    # 健康检查配置
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    health_check_timeout: int = Field(default=5, env="HEALTH_CHECK_TIMEOUT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局配置实例
_settings: Settings | None = None


def get_settings() -> Settings:
    """获取配置实例(单例模式)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

def reload_settings() -> Settings:
    """重新加载配置"""
    global _settings
    _settings = Settings()
    return _settings
