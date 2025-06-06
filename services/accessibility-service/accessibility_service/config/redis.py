"""
redis - 索克生活项目模块
"""

    from pydantic import BaseSettings
    from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import Any

"""
Redis configuration for accessibility service.
"""



try:
except ImportError:


class RedisConfig(BaseSettings):
    """Redis configuration settings."""

    # Connection settings
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        json_schema_extra={"env": "REDIS_URL"},
        description="Redis connection URL"
    )
    host: str = Field(default="localhost", json_schema_extra={"env": "REDIS_HOST"}, description="Redis host")
    port: int = Field(default=6379, json_schema_extra={"env": "REDIS_PORT"}, description="Redis port")
    database: int = Field(default=0, json_schema_extra={"env": "REDIS_DB"}, description="Redis database number")

    # Authentication
    password: str | None = Field(default=None, json_schema_extra={"env": "REDIS_PASSWORD"}, description="Redis password")
    username: str | None = Field(default=None, json_schema_extra={"env": "REDIS_USERNAME"}, description="Redis username")

    # Connection pool settings
    max_connections: int = Field(default=50, json_schema_extra={"env": "REDIS_MAX_CONNECTIONS"}, description="Maximum connections")
    retry_on_timeout: bool = Field(default=True, json_schema_extra={"env": "REDIS_RETRY_ON_TIMEOUT"}, description="Retry on timeout")
    health_check_interval: int = Field(
        default=30,
        json_schema_extra={"env": "REDIS_HEALTH_CHECK_INTERVAL"},
        description="Health check interval in seconds"
    )

    # Timeout settings
    socket_timeout: float = Field(default=5.0, json_schema_extra={"env": "REDIS_SOCKET_TIMEOUT"}, description="Socket timeout in seconds")
    socket_connect_timeout: float = Field(
        default=5.0,
        json_schema_extra={"env": "REDIS_CONNECT_TIMEOUT"},
        description="Connection timeout in seconds"
    )

    # SSL/TLS settings
    ssl_enabled: bool = Field(default=False, json_schema_extra={"env": "REDIS_SSL_ENABLED"}, description="Enable SSL/TLS")
    ssl_cert_reqs: str | None = Field(default=None, json_schema_extra={"env": "REDIS_SSL_CERT_REQS"}, description="SSL certificate requirements")
    ssl_ca_certs: str | None = Field(default=None, json_schema_extra={"env": "REDIS_SSL_CA_CERTS"}, description="SSL CA certificates path")
    ssl_certfile: str | None = Field(default=None, json_schema_extra={"env": "REDIS_SSL_CERTFILE"}, description="SSL certificate file")
    ssl_keyfile: str | None = Field(default=None, json_schema_extra={"env": "REDIS_SSL_KEYFILE"}, description="SSL key file")

    # Caching settings
    default_ttl: int = Field(default=3600, json_schema_extra={"env": "REDIS_DEFAULT_TTL"}, description="Default TTL in seconds")
    key_prefix: str = Field(default="accessibility:", json_schema_extra={"env": "REDIS_KEY_PREFIX"}, description="Key prefix")

    # Specific cache configurations
    analysis_cache_ttl: int = Field(
        default=7200,
        json_schema_extra={"env": "REDIS_ANALYSIS_CACHE_TTL"},
        description="Analysis results cache TTL in seconds"
    )
    user_cache_ttl: int = Field(
        default=1800,
        json_schema_extra={"env": "REDIS_USER_CACHE_TTL"},
        description="User data cache TTL in seconds"
    )
    session_cache_ttl: int = Field(
        default=3600,
        json_schema_extra={"env": "REDIS_SESSION_CACHE_TTL"},
        description="Session cache TTL in seconds"
    )

    # Performance settings
    decode_responses: bool = Field(default=True, json_schema_extra={"env": "REDIS_DECODE_RESPONSES"}, description="Decode responses")
    encoding: str = Field(default="utf-8", json_schema_extra={"env": "REDIS_ENCODING"}, description="Character encoding")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }
    @field_validator('port')
    @classmethod
    def validate_port(cls, v):
        """Validate Redis port."""
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v

    @field_validator('database')
    @classmethod
    def validate_database(cls, v):
        """Validate Redis database number."""
        if not 0 <= v <= 15:
            raise ValueError("Database number must be between 0 and 15")
        return v

    @field_validator('max_connections')
    @classmethod
    def validate_max_connections(cls, v):
        """Validate max connections."""
        if v < 1:
            raise ValueError("Max connections must be at least 1")
        if v > 1000:
            raise ValueError("Max connections should not exceed 1000")
        return v

    @property
    def connection_url(self) -> str:
        """Get Redis connection URL."""
        if self.redis_url and self.redis_url != "redis://localhost:6379/0":
            return self.redis_url

        # Build URL from components
        auth = ""
        if self.username and self.password:
            auth = f"{self.username}:{self.password}@"
        elif self.password:
            auth = f":{self.password}@"

        scheme = "rediss" if self.ssl_enabled else "redis"
        return f"{scheme}://{auth}{self.host}:{self.port}/{self.database}"

    def get_connection_config(self) -> dict[str, Any]:
        """Get Redis connection configuration."""
        config = {
            'host': self.host,
            'port': self.port,
            'db': self.database,
            'password': self.password,
            'username': self.username,
            'socket_timeout': self.socket_timeout,
            'socket_connect_timeout': self.socket_connect_timeout,
            'retry_on_timeout': self.retry_on_timeout,
            'health_check_interval': self.health_check_interval,
            'decode_responses': self.decode_responses,
            'encoding': self.encoding,
        }

        # Add SSL configuration if enabled
        if self.ssl_enabled:
            ssl_config = {
                'ssl': True,
                'ssl_cert_reqs': self.ssl_cert_reqs,
                'ssl_ca_certs': self.ssl_ca_certs,
                'ssl_certfile': self.ssl_certfile,
                'ssl_keyfile': self.ssl_keyfile,
            }
            config.update({k: v for k, v in ssl_config.items() if v is not None})

        return config

    def get_pool_config(self) -> dict[str, Any]:
        """Get Redis connection pool configuration."""
        return {
            'max_connections': self.max_connections,
            'retry_on_timeout': self.retry_on_timeout,
            'health_check_interval': self.health_check_interval,
        }

    def get_cache_config(self) -> dict[str, Any]:
        """Get cache configuration."""
        return {
            'default_ttl': self.default_ttl,
            'key_prefix': self.key_prefix,
            'analysis_cache_ttl': self.analysis_cache_ttl,
            'user_cache_ttl': self.user_cache_ttl,
            'session_cache_ttl': self.session_cache_ttl,
        }

    def get_key(self, key: str, category: str = "") -> str:
        """Get prefixed cache key."""
        if category:
            return f"{self.key_prefix}{category}:{key}"
        return f"{self.key_prefix}{key}"
