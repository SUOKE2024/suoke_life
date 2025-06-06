"""
middleware - 索克生活项目模块
"""

                    import re
            import uuid
        import hashlib
        import html
        import json
        import re
from .exceptions import InquiryServiceError, RateLimitError
from .logging import get_logger
from collections import defaultdict, deque
from collections.abc import Callable
from functools import wraps
from typing import Any
import asyncio
import time

#!/usr/bin/env python

"""
中间件模块
"""




class RateLimiter:
    """速率限制器"""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(deque)
        self.logger = get_logger(__name__)

    async def is_allowed(self, identifier: str) -> bool:
        """检查是否允许请求"""
        now = time.time()
        window_start = now - self.window_seconds

        # 清理过期请求
        request_times = self.requests[identifier]
        while request_times and request_times[0] < window_start:
            request_times.popleft()

        # 检查是否超过限制
        if len(request_times) >= self.max_requests:
            return False

        # 记录新请求
        request_times.append(now)
        return True

    def get_remaining_requests(self, identifier: str) -> int:
        """获取剩余请求数"""
        now = time.time()
        window_start = now - self.window_seconds

        request_times = self.requests[identifier]
        # 清理过期请求
        while request_times and request_times[0] < window_start:
            request_times.popleft()

        return max(0, self.max_requests - len(request_times))


class CircuitBreaker:
    """熔断器"""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.logger = get_logger(__name__)

    async def call(self, func: Callable, *args, **kwargs):
        """执行函数调用，带熔断保护"""
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
                self.logger.info("熔断器进入半开状态")
            else:
                raise InquiryServiceError("服务熔断中，请稍后重试")

        try:
            result = (
                await func(*args, **kwargs)
                if asyncio.iscoroutinefunction(func)
                else func(*args, **kwargs)
            )
            self._on_success()
            return result
        except self.expected_exception:
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        """检查是否应该尝试重置"""
        return (
            self.last_failure_time
            and time.time() - self.last_failure_time >= self.recovery_timeout
        )

    def _on_success(self):
        """成功时的处理"""
        self.failure_count = 0
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            self.logger.info("熔断器恢复到关闭状态")

    def _on_failure(self):
        """失败时的处理"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            self.logger.warning(f"熔断器开启，失败次数: {self.failure_count}")


class RequestTracker:
    """请求跟踪器"""

    def __init__(self):
        self.active_requests = {}
        self.request_history = deque(maxlen=1000)
        self.logger = get_logger(__name__)

    def start_request(
        self, request_id: str, metadata: dict[str, Any] = None
    ) -> dict[str, Any]:
        """开始跟踪请求"""
        request_info = {
            "request_id": request_id,
            "start_time": time.time(),
            "metadata": metadata or {},
            "status": "processing",
        }

        self.active_requests[request_id] = request_info
        return request_info

    def end_request(
        self,
        request_id: str,
        status: str = "completed",
        result: Any = None,
        error: str = None,
    ):
        """结束请求跟踪"""
        if request_id in self.active_requests:
            request_info = self.active_requests.pop(request_id)
            request_info.update(
                {
                    "end_time": time.time(),
                    "duration": time.time() - request_info["start_time"],
                    "status": status,
                    "result": result,
                    "error": error,
                }
            )

            self.request_history.append(request_info)
            return request_info

        return None

    def get_active_requests(self) -> list[dict[str, Any]]:
        """获取活跃请求"""
        return list(self.active_requests.values())

    def get_request_stats(self) -> dict[str, Any]:
        """获取请求统计"""
        total_requests = len(self.request_history)
        if total_requests == 0:
            return {"total_requests": 0}

        completed_requests = [
            r for r in self.request_history if r["status"] == "completed"
        ]
        failed_requests = [r for r in self.request_history if r["status"] == "failed"]

        avg_duration = sum(r["duration"] for r in self.request_history) / total_requests

        return {
            "total_requests": total_requests,
            "completed_requests": len(completed_requests),
            "failed_requests": len(failed_requests),
            "success_rate": len(completed_requests) / total_requests,
            "average_duration": avg_duration,
            "active_requests": len(self.active_requests),
        }


class CacheMiddleware:
    """缓存中间件"""

    def __init__(self, cache_manager, default_ttl: int = 300):
        self.cache_manager = cache_manager
        self.default_ttl = default_ttl
        self.logger = get_logger(__name__)

    def cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """生成缓存键"""

        # 创建参数的哈希
        params_str = json.dumps(
            {"args": str(args), "kwargs": sorted(kwargs.items())}, sort_keys=True
        )

        params_hash = hashlib.md5(params_str.encode()).hexdigest()
        return f"{func_name}:{params_hash}"

    async     @cache(timeout=300)  # 5分钟缓存
def get_or_set(
        self, key: str, func: Callable, *args, ttl: int = None, **kwargs
    ):
        """获取缓存或设置缓存"""
        ttl = ttl or self.default_ttl

        # 尝试从缓存获取
        cached_result = await self.cache_manager.get(key)
        if cached_result is not None:
            self.logger.debug(f"缓存命中: {key}")
            return cached_result

        # 执行函数并缓存结果
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            await self.cache_manager.set(key, result, ttl)
            self.logger.debug(f"缓存设置: {key}")
            return result

        except Exception as e:
            self.logger.error(f"函数执行失败: {e!s}")
            raise


class ValidationMiddleware:
    """验证中间件"""

    def __init__(self):
        self.logger = get_logger(__name__)

    async def validate_input(
        self, data: dict[str, Any], schema: dict[str, Any]
    ) -> dict[str, Any]:
        """验证输入数据"""
        errors = []
        validated_data = {}

        for field, rules in schema.items():
            value = data.get(field)

            # 检查必填字段
            if rules.get("required", False) and value is None:
                errors.append(f"字段 '{field}' 是必填的")
                continue

            if value is not None:
                # 类型验证
                expected_type = rules.get("type")
                if expected_type and not isinstance(value, expected_type):
                    errors.append(
                        f"字段 '{field}' 类型错误，期望 {expected_type.__name__}"
                    )
                    continue

                # 长度验证
                if "min_length" in rules and len(str(value)) < rules["min_length"]:
                    errors.append(f"字段 '{field}' 长度不能少于 {rules['min_length']}")

                if "max_length" in rules and len(str(value)) > rules["max_length"]:
                    errors.append(f"字段 '{field}' 长度不能超过 {rules['max_length']}")

                # 值范围验证
                if "min_value" in rules and value < rules["min_value"]:
                    errors.append(f"字段 '{field}' 值不能小于 {rules['min_value']}")

                if "max_value" in rules and value > rules["max_value"]:
                    errors.append(f"字段 '{field}' 值不能大于 {rules['max_value']}")

                # 正则验证
                if "pattern" in rules:

                    if not re.match(rules["pattern"], str(value)):
                        errors.append(f"字段 '{field}' 格式不正确")

                validated_data[field] = value

        if errors:
            raise InquiryServiceError(f"输入验证失败: {'; '.join(errors)}")

        return validated_data


class SecurityMiddleware:
    """安全中间件"""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.blocked_ips = set()
        self.suspicious_patterns = [
            r"<script.*?>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"eval\s*\(",
            r"exec\s*\(",
        ]

    async def sanitize_input(self, text: str) -> str:
        """清理输入文本"""

        # HTML转义
        sanitized = html.escape(text)

        # 移除可疑模式
        for pattern in self.suspicious_patterns:
            sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)

        return sanitized

    async def check_ip_whitelist(self, ip: str, whitelist: list[str] = None) -> bool:
        """检查IP白名单"""
        if not whitelist:
            return True

        return ip in whitelist

    async def detect_anomaly(self, request_data: dict[str, Any]) -> bool:
        """检测异常请求"""
        # 检查请求大小
        if len(str(request_data)) > 10000:  # 10KB限制
            self.logger.warning("请求数据过大")
            return True

        # 检查特殊字符
        text_content = str(request_data)
        suspicious_chars = ["<", ">", "script", "eval", "exec"]

        for char in suspicious_chars:
            if char in text_content.lower():
                self.logger.warning(f"检测到可疑字符: {char}")
                return True

        return False


# 装饰器函数
def rate_limit(max_requests: int = 100, window_seconds: int = 60):
    """速率限制装饰器"""
    limiter = RateLimiter(max_requests, window_seconds)

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 使用函数名作为标识符
            identifier = f"{func.__module__}.{func.__name__}"

            if not await limiter.is_allowed(identifier):
                raise RateLimitError("请求过于频繁，请稍后重试")

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def circuit_breaker(failure_threshold: int = 5, recovery_timeout: int = 60):
    """熔断器装饰器"""
    breaker = CircuitBreaker(failure_threshold, recovery_timeout)

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await breaker.call(func, *args, **kwargs)

        return wrapper

    return decorator


def track_request(tracker: RequestTracker):
    """请求跟踪装饰器"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):

            request_id = str(uuid.uuid4())

            # 开始跟踪
            tracker.start_request(
                request_id,
                {
                    "function": f"{func.__module__}.{func.__name__}",
                    "args_count": len(args),
                    "kwargs_count": len(kwargs),
                },
            )

            try:
                result = await func(*args, **kwargs)
                tracker.end_request(request_id, "completed", result)
                return result
            except Exception as e:
                tracker.end_request(request_id, "failed", error=str(e))
                raise

        return wrapper

    return decorator


def cached(cache_manager, ttl: int = 300):
    """缓存装饰器"""
    cache_middleware = CacheMiddleware(cache_manager, ttl)

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = cache_middleware.cache_key(
                f"{func.__module__}.{func.__name__}", args, kwargs
            )

            return await cache_middleware.get_or_set(
                cache_key, func, *args, ttl=ttl, **kwargs
            )

        return wrapper

    return decorator


def validate_schema(schema: dict[str, Any]):
    """输入验证装饰器"""
    validator = ValidationMiddleware()

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 假设第一个参数是要验证的数据
            if args:
                validated_data = await validator.validate_input(args[0], schema)
                args = (validated_data,) + args[1:]

            return await func(*args, **kwargs)

        return wrapper

    return decorator
