#!/usr/bin/env python3
"""
断路器模块

提供基于 pybreaker 库的断路器实现，用于增强望诊服务的弹性。
当某个服务或资源反复失败时，断路器会打开，暂时阻止对该服务的请求，
并在一定时间后自动重试，从而防止服务级联故障。
"""

import time
import logging
import functools
import pybreaker
import prometheus_client as prom
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar, cast

# 配置日志
logger = logging.getLogger(__name__)

# 定义类型变量
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])

# 断路器状态指标
CIRCUIT_STATE = prom.Gauge(
    'look_service_circuit_breaker_state',
    'Circuit breaker state (0=closed, 1=open, 0.5=half-open)',
    ['name']
)

# 断路器失败计数
CIRCUIT_FAILURES = prom.Counter(
    'look_service_circuit_breaker_failures_total',
    'Number of times the circuit breaker has failed',
    ['name']
)

# 断路器成功计数
CIRCUIT_SUCCESSES = prom.Counter(
    'look_service_circuit_breaker_successes_total',
    'Number of successful executions when the circuit is half-open',
    ['name']
)

# 断路器跳闸计数
CIRCUIT_TRIPS = prom.Counter(
    'look_service_circuit_breaker_trips_total',
    'Number of times the circuit breaker has tripped',
    ['name']
)


class CircuitBreakerFactory:
    """断路器工厂，用于创建和管理断路器实例"""
    
    def __init__(self):
        """初始化断路器工厂"""
        self._circuit_breakers: Dict[str, pybreaker.CircuitBreaker] = {}
    
    def get_circuit_breaker(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        expected_exceptions: Tuple[Exception, ...] = (Exception,)
    ) -> pybreaker.CircuitBreaker:
        """
        获取或创建断路器实例
        
        Args:
            name: 断路器名称，用于识别不同的断路器实例
            failure_threshold: 触发断路器跳闸所需的连续失败次数
            recovery_timeout: 断路器从打开状态到半开状态的等待时间（秒）
            expected_exceptions: 应视为失败的异常类型元组
            
        Returns:
            pybreaker.CircuitBreaker: 断路器实例
        """
        if name not in self._circuit_breakers:
            logger.info(f"创建新的断路器: {name}")
            cb = pybreaker.CircuitBreaker(
                fail_max=failure_threshold,
                reset_timeout=recovery_timeout,
                exclude=expected_exceptions,
                listeners=[
                    CircuitStateListener(name),
                    CircuitMetricsListener(name)
                ]
            )
            self._circuit_breakers[name] = cb
        
        return self._circuit_breakers[name]
    
    def get_all_breakers(self) -> Dict[str, pybreaker.CircuitBreaker]:
        """获取所有断路器实例"""
        return self._circuit_breakers


class CircuitStateListener(pybreaker.CircuitBreakerListener):
    """断路器状态变化监听器，用于记录状态变化日志"""
    
    def __init__(self, name: str):
        """
        初始化监听器
        
        Args:
            name: 断路器名称
        """
        self.name = name
    
    def state_change(self, cb: pybreaker.CircuitBreaker, old_state: str, new_state: str) -> None:
        """
        当断路器状态变化时调用
        
        Args:
            cb: 断路器实例
            old_state: 旧状态
            new_state: 新状态
        """
        logger.warning(f"断路器 '{self.name}' 状态从 {old_state} 变为 {new_state}")


class CircuitMetricsListener(pybreaker.CircuitBreakerListener):
    """断路器指标监听器，用于收集断路器状态和事件的指标"""
    
    def __init__(self, name: str):
        """
        初始化监听器
        
        Args:
            name: 断路器名称
        """
        self.name = name
    
    def state_change(self, cb: pybreaker.CircuitBreaker, old_state: str, new_state: str) -> None:
        """
        当断路器状态变化时更新指标
        
        Args:
            cb: 断路器实例
            old_state: 旧状态
            new_state: 新状态
        """
        # 设置当前状态指标
        if new_state == 'closed':
            CIRCUIT_STATE.labels(self.name).set(0)
        elif new_state == 'open':
            CIRCUIT_STATE.labels(self.name).set(1)
        elif new_state == 'half-open':
            CIRCUIT_STATE.labels(self.name).set(0.5)
    
    def failure(self, cb: pybreaker.CircuitBreaker, exc: Exception) -> None:
        """
        当断路器记录失败时增加失败计数
        
        Args:
            cb: 断路器实例
            exc: 导致失败的异常
        """
        CIRCUIT_FAILURES.labels(self.name).inc()
    
    def success(self, cb: pybreaker.CircuitBreaker) -> None:
        """
        当断路器处于半开状态并成功执行操作时增加成功计数
        
        Args:
            cb: 断路器实例
        """
        if cb.current_state == 'half-open':
            CIRCUIT_SUCCESSES.labels(self.name).inc()
    
    def before_call(self, cb: pybreaker.CircuitBreaker, func: Callable, *args: Any, **kwargs: Any) -> None:
        """在调用受保护函数前触发，当前未使用"""
        pass
    
    def after_call(self, cb: pybreaker.CircuitBreaker, func: Callable, *args: Any, **kwargs: Any) -> None:
        """在调用受保护函数后触发，当前未使用"""
        pass


def circuit_breaker(
    name: Optional[str] = None,
    failure_threshold: int = 5,
    recovery_timeout: float = 30.0,
    fallback_function: Optional[Callable[..., Any]] = None,
    expected_exceptions: Tuple[Exception, ...] = (Exception,)
) -> Callable[[F], F]:
    """
    断路器装饰器，用于保护函数调用
    
    Args:
        name: 断路器名称，默认为被装饰函数的名称
        failure_threshold: 触发断路器跳闸所需的连续失败次数
        recovery_timeout: 断路器从打开状态到半开状态的等待时间（秒）
        fallback_function: 当断路器打开时调用的备选函数
        expected_exceptions: 应视为失败的异常类型元组
    
    Returns:
        装饰器函数
    """
    circuit_factory = CircuitBreakerFactory()
    
    def decorator(func: F) -> F:
        breaker_name = name or func.__name__
        circuit = circuit_factory.get_circuit_breaker(
            breaker_name,
            failure_threshold,
            recovery_timeout,
            expected_exceptions
        )
        
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return circuit.call(func, *args, **kwargs)
            except pybreaker.CircuitBreakerError as e:
                logger.error(f"断路器 '{breaker_name}' 已打开，拒绝执行 {func.__name__}")
                if fallback_function:
                    logger.info(f"使用备选函数: {fallback_function.__name__}")
                    return fallback_function(*args, **kwargs)
                raise e
        
        return cast(F, wrapper)
    
    return decorator


# 用于缓存结果的简单内存字典
_result_cache: Dict[str, Tuple[Any, float]] = {}

def with_cache(
    cache_key_function: Callable[..., str],
    ttl_seconds: float = 300.0
) -> Callable[[F], F]:
    """
    缓存装饰器，缓存函数结果一段时间
    
    Args:
        cache_key_function: 根据函数参数生成缓存键的函数
        ttl_seconds: 缓存有效期（秒）
    
    Returns:
        装饰器函数
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache_key = cache_key_function(*args, **kwargs)
            current_time = time.time()
            
            # 检查缓存是否有效
            if cache_key in _result_cache:
                result, expiry_time = _result_cache[cache_key]
                if current_time < expiry_time:
                    logger.debug(f"缓存命中: {cache_key}")
                    return result
                else:
                    logger.debug(f"缓存过期: {cache_key}")
                    del _result_cache[cache_key]
            
            # 缓存未命中，执行函数
            result = func(*args, **kwargs)
            
            # 更新缓存
            _result_cache[cache_key] = (result, current_time + ttl_seconds)
            logger.debug(f"更新缓存: {cache_key}")
            
            return result
        
        return cast(F, wrapper)
    
    return decorator


# 示例使用方式
if __name__ == "__main__":
    # 配置断路器
    @circuit_breaker(
        name="external_api_call",
        failure_threshold=3,
        recovery_timeout=5.0,
        expected_exceptions=(ConnectionError, TimeoutError)
    )
    def call_external_api(api_url: str) -> str:
        """模拟外部API调用"""
        # 模拟故障场景
        if "error" in api_url:
            raise ConnectionError("连接失败")
        return f"来自 {api_url} 的响应"
    
    # 带缓存的函数
    @with_cache(
        cache_key_function=lambda user_id, analysis_type: f"{user_id}:{analysis_type}",
        ttl_seconds=60.0
    )
    def get_analysis_history(user_id: str, analysis_type: str) -> Dict[str, Any]:
        """模拟获取分析历史记录"""
        print(f"从数据库获取用户 {user_id} 的 {analysis_type} 历史记录")
        return {
            "user_id": user_id,
            "records": [{"id": "1", "type": analysis_type, "date": "2023-01-01"}],
            "timestamp": time.time()
        }
    
    # 测试断路器
    try:
        print(call_external_api("https://api.example.com"))
        print(call_external_api("https://api.example.com/error"))  # 将失败
    except Exception as e:
        print(f"调用失败: {e}")
    
    # 测试缓存
    print(get_analysis_history("user123", "tongue"))  # 从数据库获取
    print(get_analysis_history("user123", "tongue"))  # 从缓存获取
    print(get_analysis_history("user123", "face"))    # 从数据库获取，不同的分析类型 