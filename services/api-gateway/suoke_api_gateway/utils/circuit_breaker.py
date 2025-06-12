"""
circuit_breaker - 索克生活项目模块
"""

import asyncio
import time
from enum import Enum
from typing import Any, Callable, Dict, Optional

from ..core.logging import get_logger

"""
熔断器模块

实现熔断器模式，防止级联故障。
"""



logger = get_logger(__name__)


class CircuitState(Enum):
    """熔断器状态"""
    CLOSED = "closed"      # 关闭状态，正常工作
    OPEN = "open"          # 开启状态，拒绝请求
    HALF_OPEN = "half_open"  # 半开状态，尝试恢复


class CircuitBreakerError(Exception):
    """熔断器异常"""
    pass


class CircuitBreaker:
    """熔断器实现"""

    def __init__(
self,
failure_threshold: int = 5,
recovery_timeout: float = 60.0,
success_threshold: int = 3,
timeout: float = 30.0,
expected_exception: type = Exception,
    ):
"""
初始化熔断器

Args:
            failure_threshold: 失败阈值，超过此值进入开启状态
            recovery_timeout: 恢复超时时间（秒）
            success_threshold: 成功阈值，半开状态下连续成功次数
            timeout: 请求超时时间（秒）
            expected_exception: 预期的异常类型
"""
self.failure_threshold = failure_threshold
self.recovery_timeout = recovery_timeout
self.success_threshold = success_threshold
self.timeout = timeout
self.expected_exception = expected_exception

# 状态管理
self.state = CircuitState.CLOSED
self.failure_count = 0
self.success_count = 0
self.last_failure_time = None

# 统计信息
self.total_requests = 0
self.total_failures = 0
self.total_successes = 0
self.total_timeouts = 0
self.total_circuit_breaker_errors = 0

    async def call(self, func: Callable, * args,**kwargs) -> Any:
"""
通过熔断器调用函数

Args:
            func: 要调用的函数
            * args: 函数参数
           **kwargs: 函数关键字参数

Returns:
            函数返回值

Raises:
            CircuitBreakerError: 熔断器开启时
"""
self.total_requests+=1

# 检查熔断器状态
if self.state==CircuitState.OPEN:
            if self._should_attempt_reset():
                self._reset_to_half_open()
            else:
                self.total_circuit_breaker_errors+=1
                raise CircuitBreakerError("Circuit breaker is OPEN")

try:
            # 执行函数调用
            if asyncio.iscoroutinefunction(func):
                result = await asyncio.wait_for(
                    func( * args,**kwargs),
                    timeout = self.timeout
                )
            else:
                result = func( * args,**kwargs)

            # 调用成功
            self._on_success()
            return result

except asyncio.TimeoutError:
            self.total_timeouts+=1
            self._on_failure()
            raise

except self.expected_exception as e:
            self._on_failure()
            raise

except Exception as e:
            # 非预期异常不计入失败
            logger.warning(
                "Unexpected exception in circuit breaker",
                exception = type(e).__name__,
                error = str(e),
            )
            raise

    def _should_attempt_reset(self) -> bool:
"""检查是否应该尝试重置熔断器"""
return (
            self.last_failure_time is not None and
            time.time() - self.last_failure_time >=self.recovery_timeout
)

    def _reset_to_half_open(self) -> None:
"""重置到半开状态"""
self.state = CircuitState.HALF_OPEN
self.success_count = 0
logger.info("Circuit breaker reset to HALF_OPEN")

    def _on_success(self) -> None:
"""处理成功调用"""
self.total_successes+=1

if self.state==CircuitState.HALF_OPEN:
            self.success_count+=1
            if self.success_count >=self.success_threshold:
                self._reset_to_closed()
elif self.state==CircuitState.CLOSED:
            # 重置失败计数
            self.failure_count = 0

    def _on_failure(self) -> None:
"""处理失败调用"""
self.total_failures+=1
self.failure_count+=1
self.last_failure_time = time.time()

if self.state==CircuitState.HALF_OPEN:
            # 半开状态下失败，直接回到开启状态
            self._trip_to_open()
elif (
            self.state==CircuitState.CLOSED and
            self.failure_count >=self.failure_threshold
):
            # 关闭状态下失败次数超过阈值，进入开启状态
            self._trip_to_open()

    def _reset_to_closed(self) -> None:
"""重置到关闭状态"""
self.state = CircuitState.CLOSED
self.failure_count = 0
self.success_count = 0
logger.info("Circuit breaker reset to CLOSED")

    def _trip_to_open(self) -> None:
"""跳闸到开启状态"""
self.state = CircuitState.OPEN
logger.warning(
            "Circuit breaker tripped to OPEN",
            failure_count = self.failure_count,
            failure_threshold = self.failure_threshold,
)

    def get_stats(self) -> Dict[str, Any]:
"""获取熔断器统计信息"""
return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "total_requests": self.total_requests,
            "total_failures": self.total_failures,
            "total_successes": self.total_successes,
            "total_timeouts": self.total_timeouts,
            "total_circuit_breaker_errors": self.total_circuit_breaker_errors,
            "failure_rate": (
                self.total_failures / self.total_requests * 100
                if self.total_requests > 0 else 0
            ),
            "last_failure_time": self.last_failure_time,
}

    def reset(self) -> None:
"""手动重置熔断器"""
self.state = CircuitState.CLOSED
self.failure_count = 0
self.success_count = 0
self.last_failure_time = None
logger.info("Circuit breaker manually reset")


class CircuitBreakerManager:
    """熔断器管理器"""

    def __init__(self) -> None:
"""TODO: 添加文档字符串"""
self.circuit_breakers: Dict[str, CircuitBreaker] = {}

    def get_circuit_breaker(
self,
name: str,
failure_threshold: int = 5,
recovery_timeout: float = 60.0,
success_threshold: int = 3,
timeout: float = 30.0,
expected_exception: type = Exception,
    ) -> CircuitBreaker:
"""获取或创建熔断器"""
if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker(
                failure_threshold = failure_threshold,
                recovery_timeout = recovery_timeout,
                success_threshold = success_threshold,
                timeout = timeout,
                expected_exception = expected_exception,
            )

return self.circuit_breakers[name]

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
"""获取所有熔断器的统计信息"""
return {
            name: breaker.get_stats()
            for name, breaker in self.circuit_breakers.items()
}

    def reset_all(self) -> None:
"""重置所有熔断器"""
for breaker in self.circuit_breakers.values():
            breaker.reset()
logger.info("All circuit breakers reset")


# 全局熔断器管理器实例
circuit_breaker_manager = CircuitBreakerManager()


def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    success_threshold: int = 3,
    timeout: float = 30.0,
    expected_exception: type = Exception,
):
    """熔断器装饰器"""
    def decorator(func: Callable):
"""TODO: 添加文档字符串"""
breaker = circuit_breaker_manager.get_circuit_breaker(
            name = name,
            failure_threshold = failure_threshold,
            recovery_timeout = recovery_timeout,
            success_threshold = success_threshold,
            timeout = timeout,
            expected_exception = expected_exception,
)

async def async_wrapper( * args,**kwargs):
            return await breaker.call(func, * args,**kwargs)

def sync_wrapper( * args,**kwargs):
            """TODO: 添加文档字符串"""
            return asyncio.run(breaker.call(func, * args,**kwargs))

if asyncio.iscoroutinefunction(func):
            return async_wrapper
else:
            return sync_wrapper

    return decorator