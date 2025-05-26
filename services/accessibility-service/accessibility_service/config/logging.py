"""
Logging configuration for accessibility service.
"""

import os
import logging
import logging.config
from typing import Optional, Dict, Any
from pydantic import Field, validator
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class LoggingConfig(BaseSettings):
    """Logging configuration settings."""
    
    # Basic logging settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL", description="Logging level")
    log_format: str = Field(default="json", env="LOG_FORMAT", description="Log format (json or text)")
    
    # File logging
    log_file: Optional[str] = Field(default=None, env="LOG_FILE", description="Log file path")
    log_file_max_size: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        env="LOG_FILE_MAX_SIZE",
        description="Maximum log file size in bytes"
    )
    log_file_backup_count: int = Field(
        default=5,
        env="LOG_FILE_BACKUP_COUNT",
        description="Number of backup log files to keep"
    )
    
    # Console logging
    console_enabled: bool = Field(default=True, env="LOG_CONSOLE_ENABLED", description="Enable console logging")
    console_level: str = Field(default="INFO", env="LOG_CONSOLE_LEVEL", description="Console log level")
    
    # Structured logging
    structured_logging: bool = Field(default=True, env="LOG_STRUCTURED", description="Enable structured logging")
    include_timestamp: bool = Field(default=True, env="LOG_INCLUDE_TIMESTAMP", description="Include timestamp")
    include_level: bool = Field(default=True, env="LOG_INCLUDE_LEVEL", description="Include log level")
    include_logger_name: bool = Field(default=True, env="LOG_INCLUDE_LOGGER", description="Include logger name")
    include_module: bool = Field(default=True, env="LOG_INCLUDE_MODULE", description="Include module name")
    include_function: bool = Field(default=False, env="LOG_INCLUDE_FUNCTION", description="Include function name")
    include_line_number: bool = Field(default=False, env="LOG_INCLUDE_LINE", description="Include line number")
    
    # Request logging
    request_logging_enabled: bool = Field(
        default=True,
        env="LOG_REQUESTS_ENABLED",
        description="Enable request logging"
    )
    request_log_body: bool = Field(default=False, env="LOG_REQUEST_BODY", description="Log request body")
    request_log_headers: bool = Field(default=False, env="LOG_REQUEST_HEADERS", description="Log request headers")
    
    # Performance logging
    performance_logging_enabled: bool = Field(
        default=True,
        env="LOG_PERFORMANCE_ENABLED",
        description="Enable performance logging"
    )
    slow_request_threshold: float = Field(
        default=1.0,
        env="LOG_SLOW_REQUEST_THRESHOLD",
        description="Slow request threshold in seconds"
    )
    
    # Error logging
    error_logging_enabled: bool = Field(default=True, env="LOG_ERRORS_ENABLED", description="Enable error logging")
    error_include_traceback: bool = Field(
        default=True,
        env="LOG_ERROR_TRACEBACK",
        description="Include traceback in error logs"
    )
    
    # External logging services
    sentry_enabled: bool = Field(default=False, env="SENTRY_ENABLED", description="Enable Sentry logging")
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN", description="Sentry DSN")
    sentry_environment: str = Field(default="development", env="SENTRY_ENVIRONMENT", description="Sentry environment")
    
    # Log filtering
    filter_sensitive_data: bool = Field(
        default=True,
        env="LOG_FILTER_SENSITIVE",
        description="Filter sensitive data from logs"
    )
    sensitive_fields: list = Field(
        default_factory=lambda: ["password", "token", "secret", "key", "authorization"],
        env="LOG_SENSITIVE_FIELDS",
        description="Fields to filter from logs"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @validator('log_level', 'console_level')
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()
    
    @validator('log_format')
    def validate_log_format(cls, v):
        """Validate log format."""
        valid_formats = ['json', 'text', 'structured']
        if v.lower() not in valid_formats:
            raise ValueError(f"Log format must be one of: {valid_formats}")
        return v.lower()
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration dictionary."""
        config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': self._get_formatters(),
            'handlers': self._get_handlers(),
            'loggers': self._get_loggers(),
            'root': {
                'level': self.log_level,
                'handlers': self._get_root_handlers(),
            }
        }
        return config
    
    def _get_formatters(self) -> Dict[str, Any]:
        """Get log formatters configuration."""
        formatters = {}
        
        if self.log_format == 'json':
            formatters['json'] = {
                'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                'format': self._get_json_format(),
            }
        else:
            formatters['standard'] = {
                'format': self._get_text_format(),
                'datefmt': '%Y-%m-%d %H:%M:%S',
            }
        
        return formatters
    
    def _get_handlers(self) -> Dict[str, Any]:
        """Get log handlers configuration."""
        handlers = {}
        
        # Console handler
        if self.console_enabled:
            handlers['console'] = {
                'class': 'logging.StreamHandler',
                'level': self.console_level,
                'formatter': 'json' if self.log_format == 'json' else 'standard',
                'stream': 'ext://sys.stdout',
            }
        
        # File handler
        if self.log_file:
            handlers['file'] = {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': self.log_level,
                'formatter': 'json' if self.log_format == 'json' else 'standard',
                'filename': self.log_file,
                'maxBytes': self.log_file_max_size,
                'backupCount': self.log_file_backup_count,
                'encoding': 'utf-8',
            }
        
        return handlers
    
    def _get_loggers(self) -> Dict[str, Any]:
        """Get loggers configuration."""
        loggers = {
            'accessibility_service': {
                'level': self.log_level,
                'handlers': self._get_root_handlers(),
                'propagate': False,
            },
            'uvicorn': {
                'level': 'INFO',
                'handlers': self._get_root_handlers(),
                'propagate': False,
            },
            'sqlalchemy': {
                'level': 'WARNING',
                'handlers': self._get_root_handlers(),
                'propagate': False,
            },
        }
        return loggers
    
    def _get_root_handlers(self) -> list:
        """Get root handlers list."""
        handlers = []
        if self.console_enabled:
            handlers.append('console')
        if self.log_file:
            handlers.append('file')
        return handlers
    
    def _get_json_format(self) -> str:
        """Get JSON log format string."""
        fields = []
        
        if self.include_timestamp:
            fields.append('%(asctime)s')
        if self.include_level:
            fields.append('%(levelname)s')
        if self.include_logger_name:
            fields.append('%(name)s')
        if self.include_module:
            fields.append('%(module)s')
        if self.include_function:
            fields.append('%(funcName)s')
        if self.include_line_number:
            fields.append('%(lineno)d')
        
        fields.append('%(message)s')
        return ' '.join(fields)
    
    def _get_text_format(self) -> str:
        """Get text log format string."""
        format_parts = []
        
        if self.include_timestamp:
            format_parts.append('%(asctime)s')
        if self.include_level:
            format_parts.append('[%(levelname)s]')
        if self.include_logger_name:
            format_parts.append('%(name)s')
        if self.include_module:
            format_parts.append('(%(module)s')
            if self.include_function:
                format_parts[-1] += '.%(funcName)s'
            if self.include_line_number:
                format_parts[-1] += ':%(lineno)d'
            format_parts[-1] += ')'
        
        format_parts.append('%(message)s')
        return ' - '.join(format_parts)
    
    def setup_logging(self) -> None:
        """Setup logging configuration."""
        config = self.get_logging_config()
        logging.config.dictConfig(config)
        
        # Setup Sentry if enabled
        if self.sentry_enabled and self.sentry_dsn:
            try:
                import sentry_sdk
                from sentry_sdk.integrations.logging import LoggingIntegration
                
                sentry_logging = LoggingIntegration(
                    level=logging.INFO,
                    event_level=logging.ERROR
                )
                
                sentry_sdk.init(
                    dsn=self.sentry_dsn,
                    environment=self.sentry_environment,
                    integrations=[sentry_logging],
                )
            except ImportError:
                logging.warning("Sentry SDK not installed, skipping Sentry setup") 