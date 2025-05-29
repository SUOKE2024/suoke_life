"""
通用模块，包含基础类、异常、缓存、指标等
"""

from .base import (
    BaseExtractor,
    BaseMapper,
    BaseService,
    HealthRisk,
    ServiceRegistry,
    SymptomInfo,
    TCMPattern,
)
from .cache import CacheManager
from .config import ConfigManager
from .exceptions import (
    AuthenticationError,
    AuthorizationError,
    CacheError,
    ConfigurationError,
    ExternalServiceError,
    InquiryServiceError,
    ProcessingError,
    RateLimitError,
    ValidationError,
)
from .logging import get_logger, setup_logging
from .metrics import MetricsCollector, counter, timer
from .middleware import (
    CacheMiddleware,
    RateLimiter,
    RequestTracker,
    SecurityMiddleware,
    ValidationMiddleware,
    cached,
    circuit_breaker,
    rate_limit,
    track_request,
    validate_schema,
)
from .middleware import CircuitBreaker as MiddlewareCircuitBreaker
from .optimizer import (
    BatchProcessor,
    CacheOptimizer,
    MemoryOptimizer,
    ParallelProcessor,
    QueryOptimizer,
    batch_process,
    memory_optimized,
    parallel_process,
    query_optimized,
)
from .utils import (
    CircuitBreaker,
    calculate_confidence,
    parse_time_expression,
    retry_with_backoff,
    sanitize_text,
)

__all__ = [
    # 基础类
    "BaseService",
    "BaseExtractor",
    "BaseMapper",
    "ServiceRegistry",
    "SymptomInfo",
    "TCMPattern",
    "HealthRisk",
    # 异常类
    "InquiryServiceError",
    "ValidationError",
    "ProcessingError",
    "CacheError",
    "ConfigurationError",
    "ExternalServiceError",
    "RateLimitError",
    "AuthenticationError",
    "AuthorizationError",
    # 核心组件
    "CacheManager",
    "MetricsCollector",
    "ConfigManager",
    # 工具函数
    "sanitize_text",
    "calculate_confidence",
    "retry_with_backoff",
    "CircuitBreaker",
    "parse_time_expression",
    # 中间件
    "RateLimiter",
    "MiddlewareCircuitBreaker",
    "RequestTracker",
    "CacheMiddleware",
    "ValidationMiddleware",
    "SecurityMiddleware",
    # 优化器
    "BatchProcessor",
    "ParallelProcessor",
    "MemoryOptimizer",
    "CacheOptimizer",
    "QueryOptimizer",
    # 装饰器
    "timer",
    "counter",
    "rate_limit",
    "circuit_breaker",
    "track_request",
    "cached",
    "validate_schema",
    "batch_process",
    "parallel_process",
    "memory_optimized",
    "query_optimized",
    # 日志
    "get_logger",
    "setup_logging",
]
