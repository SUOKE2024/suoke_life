"""
Configuration settings for accessibility service.
"""

from functools import lru_cache
from typing import Any

from pydantic import Field, validator

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = Field(default="accessibility-service", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")

    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8080, env="PORT")
    workers: int = Field(default=1, env="WORKERS")

    # Database
    database_url: str = Field(default="sqlite:///./accessibility.db", env="DATABASE_URL")
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_password: str | None = Field(default=None, env="REDIS_PASSWORD")

    # Security
    secret_key: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # AI/ML Models
    model_cache_dir: str = Field(default="./models", env="MODEL_CACHE_DIR")
    visual_model_name: str = Field(default="resnet50", env="VISUAL_MODEL_NAME")
    audio_model_name: str = Field(default="wav2vec2", env="AUDIO_MODEL_NAME")
    nlp_model_name: str = Field(default="bert-base-uncased", env="NLP_MODEL_NAME")

    # Processing
    max_file_size: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    max_processing_time: int = Field(default=300, env="MAX_PROCESSING_TIME")  # 5 minutes
    batch_size: int = Field(default=32, env="BATCH_SIZE")

    # Accessibility Analysis
    visual_analysis_enabled: bool = Field(default=True, env="VISUAL_ANALYSIS_ENABLED")
    audio_analysis_enabled: bool = Field(default=True, env="AUDIO_ANALYSIS_ENABLED")
    motor_analysis_enabled: bool = Field(default=True, env="MOTOR_ANALYSIS_ENABLED")
    cognitive_analysis_enabled: bool = Field(default=True, env="COGNITIVE_ANALYSIS_ENABLED")

    # Thresholds
    accessibility_score_threshold: float = Field(default=70.0, env="ACCESSIBILITY_SCORE_THRESHOLD")
    confidence_threshold: float = Field(default=0.8, env="CONFIDENCE_THRESHOLD")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    log_file: str | None = Field(default=None, env="LOG_FILE")

    # Monitoring
    metrics_enabled: bool = Field(default=True, env="METRICS_ENABLED")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")

    # External Services
    api_gateway_url: str | None = Field(default=None, env="API_GATEWAY_URL")
    auth_service_url: str | None = Field(default=None, env="AUTH_SERVICE_URL")
    user_service_url: str | None = Field(default=None, env="USER_SERVICE_URL")

    # Feature Flags
    feature_flags: dict[str, bool] = Field(
        default_factory=lambda: {
            "advanced_visual_analysis": True,
            "real_time_processing": False,
            "experimental_models": False,
            "detailed_reporting": True,
        },
        env="FEATURE_FLAGS"
    )

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=3600, env="RATE_LIMIT_WINDOW")  # 1 hour

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @validator('environment')
    def validate_environment(cls, v):
        """Validate environment setting."""
        allowed_environments = ['development', 'staging', 'production', 'testing']
        if v not in allowed_environments:
            raise ValueError(f"Environment must be one of: {allowed_environments}")
        return v

    @validator('log_level')
    def validate_log_level(cls, v):
        """Validate log level setting."""
        allowed_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed_levels:
            raise ValueError(f"Log level must be one of: {allowed_levels}")
        return v.upper()

    @validator('accessibility_score_threshold')
    def validate_score_threshold(cls, v):
        """Validate accessibility score threshold."""
        if not 0 <= v <= 100:
            raise ValueError("Accessibility score threshold must be between 0 and 100")
        return v

    @validator('confidence_threshold')
    def validate_confidence_threshold(cls, v):
        """Validate confidence threshold."""
        if not 0 <= v <= 1:
            raise ValueError("Confidence threshold must be between 0 and 1")
        return v

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.environment == "testing"

    def get_database_config(self) -> dict[str, Any]:
        """Get database configuration."""
        return {
            "url": self.database_url,
            "echo": self.database_echo,
        }

    def get_redis_config(self) -> dict[str, Any]:
        """Get Redis configuration."""
        config = {"url": self.redis_url}
        if self.redis_password:
            config["password"] = self.redis_password
        return config

    def get_model_config(self) -> dict[str, Any]:
        """Get AI/ML model configuration."""
        return {
            "cache_dir": self.model_cache_dir,
            "visual_model": self.visual_model_name,
            "audio_model": self.audio_model_name,
            "nlp_model": self.nlp_model_name,
            "batch_size": self.batch_size,
        }

    def get_analysis_config(self) -> dict[str, Any]:
        """Get analysis configuration."""
        return {
            "visual_enabled": self.visual_analysis_enabled,
            "audio_enabled": self.audio_analysis_enabled,
            "motor_enabled": self.motor_analysis_enabled,
            "cognitive_enabled": self.cognitive_analysis_enabled,
            "score_threshold": self.accessibility_score_threshold,
            "confidence_threshold": self.confidence_threshold,
        }

    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature flag is enabled."""
        return self.feature_flags.get(feature_name, False)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
