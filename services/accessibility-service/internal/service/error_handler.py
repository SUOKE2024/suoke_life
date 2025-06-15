#!/usr/bin/env python

"""
错误处理和重试机制
包含断路器模式、指数退避重试、错误分类和恢复策略
"""

import asyncio
import functools
import logging
import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """错误严重程度"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """错误类别"""

    NETWORK = "network"
    DATABASE = "database"
    EXTERNAL_API = "external_api"
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    RESOURCE = "resource"
    BUSINESS_LOGIC = "business_logic"
    SYSTEM = "system"
    UNKNOWN = "unknown"


class CircuitState(Enum):
    """断路器状态"""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class ErrorInfo:
    """错误信息"""

    exception: Exception
    category: ErrorCategory
    severity: ErrorSeverity
    timestamp: float = field(default_factory=time.time)
    context: dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    recoverable: bool = True


@dataclass
class RetryConfig:
    """重试配置"""

    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    backoff_strategy: str = "exponential"  # exponential, linear, fixed
    retry_on: list[type[Exception]] = field(default_factory=list)
    stop_on: list[type[Exception]] = field(default_factory=list)


@dataclass
class CircuitBreakerConfig:
    """断路器配置"""

    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    expected_exception: type[Exception] = Exception
    success_threshold: int = 3


class ErrorClassifier:
    """错误分类器"""

    def __init__(self) -> None:
        self._rules: list[dict[str, Any]] = []
        self._setup_default_rules()

    def _setup_default_rules(self) -> None:
        """设置默认分类规则"""
        self._rules = [
            # 网络错误
            {
                "exceptions": [ConnectionError, TimeoutError, OSError],
                "category": ErrorCategory.NETWORK,
                "severity": ErrorSeverity.MEDIUM,
                "recoverable": True,
            },
            # 数据库错误
            {
                "exceptions": [
                    "psycopg2.OperationalError",
                    "sqlalchemy.exc.OperationalError",
                ],
                "category": ErrorCategory.DATABASE,
                "severity": ErrorSeverity.HIGH,
                "recoverable": True,
            },
            # 验证错误
            {
                "exceptions": [ValueError, TypeError],
                "category": ErrorCategory.VALIDATION,
                "severity": ErrorSeverity.LOW,
                "recoverable": False,
            },
            # 认证错误
            {
                "exceptions": ["jwt.InvalidTokenError", "AuthenticationError"],
                "category": ErrorCategory.AUTHENTICATION,
                "severity": ErrorSeverity.MEDIUM,
                "recoverable": False,
            },
            # 资源错误
            {
                "exceptions": [MemoryError, FileNotFoundError],
                "category": ErrorCategory.RESOURCE,
                "severity": ErrorSeverity.HIGH,
                "recoverable": True,
            },
            # 系统错误
            {
                "exceptions": [SystemError, RuntimeError],
                "category": ErrorCategory.SYSTEM,
                "severity": ErrorSeverity.CRITICAL,
                "recoverable": True,
            },
        ]

    def classify(
        self, exception: Exception, context: dict[str, Any] = None
    ) -> ErrorInfo:
        """分类错误"""
        context = context or {}

        for rule in self._rules:
            if self._matches_rule(exception, rule):
                return ErrorInfo(
                    exception=exception,
                    category=rule["category"],
                    severity=rule["severity"],
                    context=context,
                    recoverable=rule["recoverable"],
                )

        # 默认分类
        return ErrorInfo(
            exception=exception,
            category=ErrorCategory.UNKNOWN,
            severity=ErrorSeverity.MEDIUM,
            context=context,
            recoverable=True,
        )

    def _matches_rule(self, exception: Exception, rule: dict[str, Any]) -> bool:
        """检查异常是否匹配规则"""
        for exc_type in rule["exceptions"]:
            if isinstance(exc_type, str):
                # 字符串类型，检查类名
                if exc_type in str(type(exception)):
                    return True
            elif isinstance(exception, exc_type):
                return True
        return False

    def add_rule(
        self,
        exceptions: list[type[Exception] | str],
        category: ErrorCategory,
        severity: ErrorSeverity,
        recoverable: bool = True,
    ):
        """添加分类规则"""
        self._rules.insert(
            0,
            {
                "exceptions": exceptions,
                "category": category,
                "severity": severity,
                "recoverable": recoverable,
            },
        )


class RetryStrategy:
    """重试策略"""

    @staticmethod
    def exponential_backoff(
        attempt: int,
        base_delay: float,
        max_delay: float,
        exponential_base: float,
        jitter: bool,
    ) -> float:
        """指数退避"""
        delay = min(base_delay * (exponential_base**attempt), max_delay)
        if jitter:
            delay *= 0.5 + secrets.SystemRandom().random() * 0.5
        return delay

    @staticmethod
    def linear_backoff(
        attempt: int, base_delay: float, max_delay: float, **kwargs
    ) -> float:
        """线性退避"""
        delay = min(base_delay * (attempt + 1), max_delay)
        return delay

    @staticmethod
    def fixed_delay(attempt: int, base_delay: float, **kwargs) -> float:
        """固定延迟"""
        return base_delay


class CircuitBreaker:
    """断路器"""

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = 0
        self._lock = threading.Lock()

    def __call__(self, func):
        """装饰器"""

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await self.call(func, *args, **kwargs)

        return wrapper

    async def call(self, func: Callable, *args, **kwargs):
        """调用函数"""
        with self._lock:
            if self._state == CircuitState.OPEN:
                if time.time() - self._last_failure_time < self.config.recovery_timeout:
                    raise Exception("断路器开启，拒绝请求")
                else:
                    self._state = CircuitState.HALF_OPEN
                    self._success_count = 0
                    logger.info("断路器进入半开状态")

        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            self._on_success()
            return result

        except self.config.expected_exception:
            self._on_failure()
            raise

    def _on_success(self) -> None:
        """成功回调"""
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.config.success_threshold:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    logger.info("断路器关闭")
            elif self._state == CircuitState.CLOSED:
                self._failure_count = 0

    def _on_failure(self) -> None:
        """失败回调"""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()

            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
                logger.warning("断路器重新开启")
            elif (
                self._state == CircuitState.CLOSED
                and self._failure_count >= self.config.failure_threshold
            ):
                self._state = CircuitState.OPEN
                logger.warning("断路器开启")

    @property
    def state(self) -> CircuitState:
        """获取状态"""
        return self._state

    def reset(self) -> None:
        """重置断路器"""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._last_failure_time = 0
            logger.info("断路器已重置")


class ErrorHandler:
    """错误处理器"""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self._classifier = ErrorClassifier()
        self._circuit_breakers: dict[str, CircuitBreaker] = {}
        self._error_stats: dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._recovery_strategies: dict[ErrorCategory, Callable] = {}

        # 设置默认恢复策略
        self._setup_recovery_strategies()

    def _setup_recovery_strategies(self) -> None:
        """设置恢复策略"""
        self._recovery_strategies = {
            ErrorCategory.NETWORK: self._recover_network_error,
            ErrorCategory.DATABASE: self._recover_database_error,
            ErrorCategory.EXTERNAL_API: self._recover_api_error,
            ErrorCategory.RESOURCE: self._recover_resource_error,
        }

    def retry(self, config: RetryConfig = None):
        """重试装饰器"""
        config = config or RetryConfig()

        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                return await self._retry_with_config(func, config, *args, **kwargs)

            return wrapper

        return decorator

    async def _retry_with_config(
        self, func: Callable, config: RetryConfig, *args, **kwargs
    ):
        """使用配置重试"""
        last_exception = None

        for attempt in range(config.max_attempts):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)

            except Exception as e:
                last_exception = e
                error_info = self._classifier.classify(e)

                # 记录错误统计
                self._record_error(func.__name__, error_info)

                # 检查是否应该停止重试
                if not self._should_retry(e, config, attempt):
                    break

                # 计算延迟
                if attempt < config.max_attempts - 1:
                    delay = self._calculate_delay(attempt, config)
                    logger.warning(
                        f"重试 {func.__name__} (第{attempt + 1}次), "
                        f"延迟 {delay:.2f}s, 错误: {e!s}"
                    )
                    await asyncio.sleep(delay)

        # 所有重试都失败了
        if last_exception:
            error_info = self._classifier.classify(last_exception)
            await self._handle_final_error(func.__name__, error_info)
            raise last_exception

    def _should_retry(
        self, exception: Exception, config: RetryConfig, attempt: int
    ) -> bool:
        """判断是否应该重试"""
        # 检查是否达到最大重试次数
        if attempt >= config.max_attempts - 1:
            return False

        # 检查停止重试的异常
        for stop_exc in config.stop_on:
            if isinstance(exception, stop_exc):
                return False

        # 检查允许重试的异常
        if config.retry_on:
            for retry_exc in config.retry_on:
                if isinstance(exception, retry_exc):
                    return True
            return False

        # 默认根据错误分类判断
        error_info = self._classifier.classify(exception)
        return error_info.recoverable

    def _calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        """计算延迟时间"""
        if config.backoff_strategy == "exponential":
            return RetryStrategy.exponential_backoff(
                attempt,
                config.base_delay,
                config.max_delay,
                config.exponential_base,
                config.jitter,
            )
        elif config.backoff_strategy == "linear":
            return RetryStrategy.linear_backoff(
                attempt, config.base_delay, config.max_delay
            )
        else:  # fixed
            return RetryStrategy.fixed_delay(attempt, config.base_delay)

    def circuit_breaker(self, name: str, config: CircuitBreakerConfig = None):
        """断路器装饰器"""
        config = config or CircuitBreakerConfig()

        if name not in self._circuit_breakers:
            self._circuit_breakers[name] = CircuitBreaker(config)

        return self._circuit_breakers[name]

    def _record_error(self, function_name: str, error_info: ErrorInfo):
        """记录错误统计"""
        self._error_stats[function_name].append(
            {
                "timestamp": error_info.timestamp,
                "category": error_info.category.value,
                "severity": error_info.severity.value,
                "exception_type": type(error_info.exception).__name__,
                "message": str(error_info.exception),
            }
        )

    async def _handle_final_error(self, function_name: str, error_info: ErrorInfo):
        """处理最终错误"""
        logger.error(
            f"函数 {function_name} 最终失败: "
            f"类别={error_info.category.value}, "
            f"严重程度={error_info.severity.value}, "
            f"错误={error_info.exception!s}"
        )

        # 尝试恢复策略
        if error_info.category in self._recovery_strategies:
            try:
                await self._recovery_strategies[error_info.category](error_info)
            except Exception as e:
                logger.error(f"恢复策略执行失败: {e!s}")

    async def _recover_network_error(self, error_info: ErrorInfo):
        """网络错误恢复"""
        logger.info("执行网络错误恢复策略")
        # 可以实现网络连接检查、DNS刷新等
        await asyncio.sleep(1)

    async def _recover_database_error(self, error_info: ErrorInfo):
        """数据库错误恢复"""
        logger.info("执行数据库错误恢复策略")
        # 可以实现连接池重置、连接重建等
        await asyncio.sleep(2)

    async def _recover_api_error(self, error_info: ErrorInfo):
        """API错误恢复"""
        logger.info("执行API错误恢复策略")
        # 可以实现API密钥刷新、端点切换等
        await asyncio.sleep(1)

    async def _recover_resource_error(self, error_info: ErrorInfo):
        """资源错误恢复"""
        logger.info("执行资源错误恢复策略")
        # 可以实现内存清理、文件清理等
        import gc

        gc.collect()
        await asyncio.sleep(1)

    def get_error_stats(self, function_name: str = None) -> dict[str, Any]:
        """获取错误统计"""
        if function_name:
            return {
                "function": function_name,
                "errors": list(self._error_stats.get(function_name, [])),
            }

        stats = {}
        for func_name, errors in self._error_stats.items():
            stats[func_name] = {
                "total_errors": len(errors),
                "recent_errors": list(errors)[-10:],  # 最近10个错误
                "error_rate": self._calculate_error_rate(errors),
            }

        return stats

    def _calculate_error_rate(self, errors: deque) -> float:
        """计算错误率"""
        if not errors:
            return 0.0

        # 计算最近1小时的错误率
        current_time = time.time()
        recent_errors = [e for e in errors if current_time - e["timestamp"] < 3600]

        return len(recent_errors) / 3600  # 每秒错误数

    def reset_circuit_breaker(self, name: str):
        """重置断路器"""
        if name in self._circuit_breakers:
            self._circuit_breakers[name].reset()

    def get_circuit_breaker_status(self) -> dict[str, dict[str, Any]]:
        """获取断路器状态"""
        status = {}
        for name, cb in self._circuit_breakers.items():
            status[name] = {
                "state": cb.state.value,
                "failure_count": cb._failure_count,
                "success_count": cb._success_count,
                "last_failure_time": cb._last_failure_time,
            }
        return status

    def add_recovery_strategy(self, category: ErrorCategory, strategy: Callable):
        """添加恢复策略"""
        self._recovery_strategies[category] = strategy

    async def cleanup(self) -> None:
        """清理资源"""
        logger.info("开始清理错误处理器")
        self._error_stats.clear()
        self._circuit_breakers.clear()
        logger.info("错误处理器清理完成")
