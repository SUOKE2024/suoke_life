"""
config - 索克生活项目模块
"""

from functools import lru_cache
from pathlib import Path
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

"""Configuration management for look service."""




class DatabaseSettings(BaseSettings):
    """Database configuration."""

    # PostgreSQL
    postgres_host: str = Field(default="localhost", description="PostgreSQL host")
    postgres_port: int = Field(default=5432, description="PostgreSQL port")
    postgres_user: str = Field(default="postgres", description="PostgreSQL user")
    postgres_password: str = Field(default="", description="PostgreSQL password")
    postgres_db: str = Field(default="look_service", description="PostgreSQL database")

    # Redis
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_password: str | None = Field(default=None, description="Redis password")
    redis_db: int = Field(default=0, description="Redis database")

    # MongoDB
    mongo_host: str = Field(default="localhost", description="MongoDB host")
    mongo_port: int = Field(default=27017, description="MongoDB port")
    mongo_user: str | None = Field(default=None, description="MongoDB user")
    mongo_password: str | None = Field(default=None, description="MongoDB password")
    mongo_db: str = Field(default="look_service", description="MongoDB database")

    # Milvus
    milvus_host: str = Field(default="localhost", description="Milvus host")
    milvus_port: int = Field(default=19530, description="Milvus port")
    milvus_user: str | None = Field(default=None, description="Milvus user")
    milvus_password: str | None = Field(default=None, description="Milvus password")

    @property
    def postgres_url(self) -> str:
        """Get PostgreSQL connection URL."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        """Get Redis connection URL."""
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def mongo_url(self) -> str:
        """Get MongoDB connection URL."""
        if self.mongo_user and self.mongo_password:
            auth = f"{self.mongo_user}:{self.mongo_password}@"
        else:
            auth = ""
        return f"mongodb://{auth}{self.mongo_host}:{self.mongo_port}/{self.mongo_db}"


class MLSettings(BaseSettings):
    """Machine Learning configuration."""

    # Model paths
    face_model_path: str = Field(default="models/face_detection.onnx")
    tongue_model_path: str = Field(default="models/tongue_analysis.onnx")
    eye_model_path: str = Field(default="models/eye_analysis.onnx")

    # Processing settings
    max_image_size: int = Field(
        default=1024, description="Maximum image size for processing"
    )
    batch_size: int = Field(default=8, description="Batch size for inference")
    confidence_threshold: float = Field(default=0.7, description="Confidence threshold")

    # GPU settings
    use_gpu: bool = Field(default=False, description="Use GPU for inference")
    gpu_device_id: int = Field(default=0, description="GPU device ID")

    # Feature extraction
    feature_dim: int = Field(default=512, description="Feature vector dimension")
    similarity_threshold: float = Field(default=0.8, description="Similarity threshold")


class ServiceSettings(BaseSettings):
    """Service configuration."""

    # Basic service info
    service_name: str = Field(default="look-service", description="Service name")
    service_version: str = Field(default="1.0.0", description="Service version")
    environment: str = Field(default="development", description="Environment")

    # Server settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8080, description="Server port")
    workers: int = Field(default=1, description="Number of workers")

    # gRPC settings
    grpc_host: str = Field(default="0.0.0.0", description="gRPC server host")
    grpc_port: int = Field(default=50051, description="gRPC server port")
    grpc_max_workers: int = Field(default=10, description="gRPC max workers")

    # Security
    secret_key: str = Field(default="your-secret-key", description="Secret key")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Token expiration")

    # CORS
    cors_origins: list[str] = Field(default=["*"], description="CORS origins")
    cors_methods: list[str] = Field(default=["*"], description="CORS methods")
    cors_headers: list[str] = Field(default=["*"], description="CORS headers")


class MonitoringSettings(BaseSettings):
    """Monitoring and observability configuration."""

    # Logging
    log_level: str = Field(default="INFO", description="Log level")
    log_format: str = Field(default="json", description="Log format")
    log_file: str | None = Field(default=None, description="Log file path")

    # Metrics
    enable_metrics: bool = Field(default=True, description="Enable metrics")
    metrics_port: int = Field(default=9090, description="Metrics port")

    # Tracing
    enable_tracing: bool = Field(default=False, description="Enable tracing")
    jaeger_endpoint: str | None = Field(default=None, description="Jaeger endpoint")

    # Health checks
    health_check_interval: int = Field(default=30, description="Health check interval")

    # Circuit breaker
    circuit_breaker_failure_threshold: int = Field(
        default=5, description="Failure threshold"
    )
    circuit_breaker_recovery_timeout: int = Field(
        default=60, description="Recovery timeout"
    )


class Settings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Sub-configurations
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    ml: MLSettings = Field(default_factory=MLSettings)
    service: ServiceSettings = Field(default_factory=ServiceSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)

    # Global settings
    debug: bool = Field(default=False, description="Debug mode")
    testing: bool = Field(default=False, description="Testing mode")

    # File storage
    upload_dir: str = Field(default="uploads", description="Upload directory")
    max_file_size: int = Field(
        default=10 * 1024 * 1024, description="Max file size (10MB)"
    )
    allowed_extensions: list[str] = Field(
        default=["jpg", "jpeg", "png", "bmp", "tiff"],
        description="Allowed file extensions",
    )

    @validator("upload_dir")
    def create_upload_dir(cls, v: str) -> str:
        """Create upload directory if it doesn't exist."""
        Path(v).mkdir(parents=True, exist_ok=True)
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.service.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.service.environment.lower() == "development"

    def get_database_url(self, db_type: str = "postgres") -> str:
        """Get database URL by type."""
        if db_type == "postgres":
            return self.database.postgres_url
        elif db_type == "redis":
            return self.database.redis_url
        elif db_type == "mongo":
            return self.database.mongo_url
        else:
            raise ValueError(f"Unsupported database type: {db_type}")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
