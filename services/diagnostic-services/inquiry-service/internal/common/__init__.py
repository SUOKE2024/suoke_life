"""
通用模块，包含基础类、异常、缓存、指标等
"""

from .base import (
    BaseService, BaseExtractor, BaseMapper, ServiceRegistry,
    SymptomInfo, TCMPattern, HealthRisk
)
from .exceptions import (
    InquiryServiceError, ValidationError, ProcessingError,
    CacheError, ConfigurationError, ExternalServiceError,
    RateLimitError, AuthenticationError, AuthorizationError
)
from .cache import CacheManager
from .metrics import MetricsCollector, timer, counter
from .config import ConfigManager
from .logging import get_logger, setup_logging
from .utils import (
    sanitize_text, calculate_confidence, retry_with_backoff,
    CircuitBreaker, parse_time_expression
)
from .middleware import (
    RateLimiter, CircuitBreaker as MiddlewareCircuitBreaker, RequestTracker,
    CacheMiddleware, ValidationMiddleware, SecurityMiddleware,
    rate_limit, circuit_breaker, track_request, cached, validate_schema
)
from .optimizer import (
    BatchProcessor, ParallelProcessor, MemoryOptimizer, CacheOptimizer, QueryOptimizer,
    batch_process, parallel_process, memory_optimized, query_optimized
)

__all__ = [
    # 基础类
    'BaseService', 'BaseExtractor', 'BaseMapper', 'ServiceRegistry',
    'SymptomInfo', 'TCMPattern', 'HealthRisk',
    
    # 异常类
    'InquiryServiceError', 'ValidationError', 'ProcessingError',
    'CacheError', 'ConfigurationError', 'ExternalServiceError',
    'RateLimitError', 'AuthenticationError', 'AuthorizationError',
    
    # 核心组件
    'CacheManager', 'MetricsCollector', 'ConfigManager',
    
    # 工具函数
    'sanitize_text', 'calculate_confidence', 'retry_with_backoff',
    'CircuitBreaker', 'parse_time_expression',
    
    # 中间件
    'RateLimiter', 'MiddlewareCircuitBreaker', 'RequestTracker',
    'CacheMiddleware', 'ValidationMiddleware', 'SecurityMiddleware',
    
    # 优化器
    'BatchProcessor', 'ParallelProcessor', 'MemoryOptimizer', 
    'CacheOptimizer', 'QueryOptimizer',
    
    # 装饰器
    'timer', 'counter', 'rate_limit', 'circuit_breaker', 'track_request',
    'cached', 'validate_schema', 'batch_process', 'parallel_process',
    'memory_optimized', 'query_optimized',
    
    # 日志
    'get_logger', 'setup_logging'
] 