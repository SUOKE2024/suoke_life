"""
Database configuration for accessibility service.
"""

from typing import Any

from pydantic import Field, field_validator

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class DatabaseConfig(BaseSettings):
    """Database configuration settings."""

    # Database connection
    database_url: str = Field(
        default="sqlite:///./accessibility.db",
        json_schema_extra={"env": "DATABASE_URL"},
        description="Database connection URL"
    )

    # Connection pool settings
    pool_size: int = Field(default=5, json_schema_extra={"env": "DB_POOL_SIZE"}, description="Connection pool size")
    max_overflow: int = Field(default=10, json_schema_extra={"env": "DB_MAX_OVERFLOW"}, description="Max overflow connections")
    pool_timeout: int = Field(default=30, json_schema_extra={"env": "DB_POOL_TIMEOUT"}, description="Pool timeout in seconds")
    pool_recycle: int = Field(default=3600, json_schema_extra={"env": "DB_POOL_RECYCLE"}, description="Pool recycle time in seconds")

    # Query settings
    echo: bool = Field(default=False, json_schema_extra={"env": "DB_ECHO"}, description="Echo SQL queries")
    echo_pool: bool = Field(default=False, json_schema_extra={"env": "DB_ECHO_POOL"}, description="Echo pool events")

    # Migration settings
    migration_directory: str = Field(
        default="migrations",
        json_schema_extra={"env": "DB_MIGRATION_DIR"},
        description="Migration directory"
    )

    # Backup settings
    backup_enabled: bool = Field(default=True, json_schema_extra={"env": "DB_BACKUP_ENABLED"}, description="Enable database backups")
    backup_interval: int = Field(default=86400, json_schema_extra={"env": "DB_BACKUP_INTERVAL"}, description="Backup interval in seconds")
    backup_retention: int = Field(default=7, json_schema_extra={"env": "DB_BACKUP_RETENTION"}, description="Backup retention in days")

    # Performance settings
    query_timeout: int = Field(default=30, json_schema_extra={"env": "DB_QUERY_TIMEOUT"}, description="Query timeout in seconds")
    slow_query_threshold: float = Field(
        default=1.0,
        json_schema_extra={"env": "DB_SLOW_QUERY_THRESHOLD"},
        description="Slow query threshold in seconds"
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }
    @field_validator('database_url')
    @classmethod
    def validate_database_url(cls, v):
        """Validate database URL format."""
        if not v:
            raise ValueError("Database URL cannot be empty")

        # Basic validation for common database schemes
        valid_schemes = ['sqlite', 'postgresql', 'mysql', 'oracle', 'mssql']
        scheme = v.split('://')[0].lower()

        if scheme not in valid_schemes:
            raise ValueError(f"Unsupported database scheme: {scheme}")

        return v

    @field_validator('pool_size')
    @classmethod
    def validate_pool_size(cls, v):
        """Validate pool size."""
        if v < 1:
            raise ValueError("Pool size must be at least 1")
        if v > 100:
            raise ValueError("Pool size should not exceed 100")
        return v

    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite database."""
        return self.database_url.startswith('sqlite')

    @property
    def is_postgresql(self) -> bool:
        """Check if using PostgreSQL database."""
        return self.database_url.startswith('postgresql')

    @property
    def is_mysql(self) -> bool:
        """Check if using MySQL database."""
        return self.database_url.startswith('mysql')

    def get_engine_config(self) -> dict[str, Any]:
        """Get SQLAlchemy engine configuration."""
        config = {
            'echo': self.echo,
            'echo_pool': self.echo_pool,
            'pool_timeout': self.pool_timeout,
            'pool_recycle': self.pool_recycle,
        }

        # Add pool settings for non-SQLite databases
        if not self.is_sqlite:
            config.update({
                'pool_size': self.pool_size,
                'max_overflow': self.max_overflow,
            })

        return config

    def get_session_config(self) -> dict[str, Any]:
        """Get SQLAlchemy session configuration."""
        return {
            'autocommit': False,
            'autoflush': False,
            'expire_on_commit': False,
        }

    def get_backup_config(self) -> dict[str, Any]:
        """Get backup configuration."""
        return {
            'enabled': self.backup_enabled,
            'interval': self.backup_interval,
            'retention': self.backup_retention,
        }
