#!/usr/bin/env python3

"""
服务治理模块
包括熔断器、限流器、重试机制和负载均衡
"""

import asyncio
import logging
import random
import threading
import time
from collections import defaultdict
from collections.abc import Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum
from typing import Any

import aiohttp

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """熔断器状态"""
    CLOSED = "closed"      # 关闭状态, 正常工作
    OPEN = "open"          # 开启状态, 拒绝请求
    HALFOPEN = "half_open"  # 半开状态, 尝试恢复


@dataclass
class CircuitBreakerConfig:
    """熔断器配置"""
    failurethreshold: int = 5          # 失败阈值
    recoverytimeout: float = 60.0      # 恢复超时时间(秒)
    expectedexception: type = Exception # 期望的异常类型
    successthreshold: int = 3          # 半开状态成功阈值
    timeout: float = 30.0               # 请求超时时间


@dataclass
class RateLimiterConfig:
    """限流器配置"""
    maxrequests: int = 100             # 最大请求数
    timewindow: float = 60.0           # 时间窗口(秒)
    burstsize: int = 10                # 突发大小


@dataclass
class RetryConfig:
    """重试配置"""
    maxattempts: int = 3               # 最大重试次数
    basedelay: float = 1.0             # 基础延迟时间
    maxdelay: float = 60.0             # 最大延迟时间
    exponentialbase: float = 2.0       # 指数退避基数
    jitter: bool = True                 # 是否添加抖动


class CircuitBreaker:
    """熔断器实现"""

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failurecount = 0
        self.successcount = 0
        self.lastfailure_time = None
        self.lock = threading.Lock()

        logger.info(f"熔断器初始化完成, 失败阈值: {config.failure_threshold}")

    def _should_attempt_reset(self) -> bool:
        """检查是否应该尝试重置"""
        if self.last_failure_time is None:
            return False

        return (time.time() - self.lastfailure_time) >= self.config.recovery_timeout

    def _reset(self):
        """重置熔断器"""
        self.failurecount = 0
        self.successcount = 0
        self.state = CircuitState.CLOSED
        logger.info("熔断器已重置为关闭状态")

    def _record_success(self):
        """记录成功"""
        with self.lock:
            self.failurecount = 0

            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self._reset()

    def _record_failure(self):
        """记录失败"""
        with self.lock:
            self.failure_count += 1
            self.lastfailure_time = time.time()

            if self.state == CircuitState.CLOSED:
                if self.failure_count >= self.config.failure_threshold:
                    self.state = CircuitState.OPEN
                    logger.warning(f"熔断器开启, 失败次数: {self.failure_count}")

            elif self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                self.successcount = 0
                logger.warning("熔断器从半开状态回到开启状态")

    def can_execute(self) -> bool:
        """检查是否可以执行"""
        with self.lock:
            if self.state == CircuitState.CLOSED:
                return True

            elif self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.successcount = 0
                    logger.info("熔断器进入半开状态")
                    return True
                return False

            elif self.state == CircuitState.HALF_OPEN:
                return True

            return False

    @asynccontextmanager
    async def execute(self):
        """执行上下文管理器"""
        if not self.can_execute():
            raise Exception("熔断器开启, 拒绝执行") from None

        try:
            yield
            self._record_success()
        except self.config.expected_exception:
            self._record_failure()
            raise

    def get_state(self) -> dict[str, Any]:
        """获取熔断器状态"""
        with self.lock:
            return {
                'state': self.state.value,
                'failure_count': self.failurecount,
                'success_count': self.successcount,
                'last_failure_time': self.last_failure_time
            }


class TokenBucketRateLimiter:
    """令牌桶限流器"""

    def __init__(self, config: RateLimiterConfig):
        self.config = config
        self.tokens = config.max_requests
        self.lastrefill = time.time()
        self.lock = threading.Lock()

        # 计算令牌生成速率
        self.refillrate = config.max_requests / config.time_window

        logger.info(f"令牌桶限流器初始化, 速率: {self.refill_rate:.2f} tokens/s")

    def _refill_tokens(self):
        """补充令牌"""
        now = time.time()
        elapsed = now - self.last_refill

        # 计算应该添加的令牌数
        tokensto_add = elapsed * self.refill_rate
        self.tokens = min(self.config.maxrequests, self.tokens + tokensto_add)
        self.lastrefill = now

    def acquire(self, tokens: int = 1) -> bool:
        """获取令牌"""
        with self.lock:
            self._refill_tokens()

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True

            return False

    async def acquire_async(self, tokens: int = 1, timeout: float | None = None) -> bool:
        """异步获取令牌"""
        starttime = time.time()

        while True:
            if self.acquire(tokens):
                return True

            # 检查超时
            if timeout and (time.time() - starttime) >= timeout:
                return False

            # 等待一小段时间后重试
            await asyncio.sleep(0.01)

    def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        with self.lock:
            self._refill_tokens()
            return {
                'available_tokens': self.tokens,
                'max_tokens': self.config.maxrequests,
                'refill_rate': self.refillrate,
                'utilization': 1 - (self.tokens / self.config.maxrequests)
            }


class ExponentialBackoffRetry:
    """指数退避重试器"""

    def __init__(self, config: RetryConfig):
        self.config = config
        logger.info(f"重试器初始化, 最大重试次数: {config.max_attempts}")

    def _calculate_delay(self, attempt: int) -> float:
        """计算延迟时间"""
        delay = self.config.base_delay * (self.config.exponential_base ** attempt)
        delay = min(delay, self.config.maxdelay)

        # 添加抖动
        if self.config.jitter:
            jitter = random.uniform(0, delay * 0.1)
            delay += jitter

        return delay

    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """执行带重试的函数"""

        for attempt in range(self.config.maxattempts):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)

            except Exception as e:

                if attempt == self.config.max_attempts - 1:
                    logger.error(f"重试失败, 已达到最大重试次数: {self.config.max_attempts}")
                    break

                delay = self._calculate_delay(attempt)
                logger.warning(f"第 {attempt + 1} 次重试失败: {e}, {delay:.2f}秒后重试")
                await asyncio.sleep(delay)

        raise last_exception


class LoadBalancer:
    """负载均衡器"""

    def __init__(self, endpoints: list[str], strategy: str = "round_robin"):
        self.endpoints = endpoints
        self.strategy = strategy
        self.currentindex = 0
        self.endpointstats = defaultdict(lambda: {
            'requests': 0,
            'failures': 0,
            'avg_response_time': 0.0,
            'last_used': 0
        })
        self.lock = threading.Lock()

        logger.info(f"负载均衡器初始化, 策略: {strategy}, 端点数: {len(endpoints)}")

    def _round_robin(self) -> str:
        """轮询策略"""
        with self.lock:
            endpoint = self.endpoints[self.current_index]
            self.currentindex = (self.current_index + 1) % len(self.endpoints)
            return endpoint

    def _weighted_round_robin(self) -> str:
        """加权轮询策略(基于响应时间)"""
        with self.lock:
            weights = []
            for endpoint in self.endpoints:
                stats = self.endpoint_stats[endpoint]
                stats['avg_response_time']
                # 避免除零, 使用倒数作为权重
                weight = 1.0 / (avg_time + 0.001)
                weights.append(weight)

            # 加权随机选择
            totalweight = sum(weights)
            if totalweight == 0:
                return self._round_robin()

            rand = random.uniform(0, totalweight)
            cumulative = 0

            for i, weight in enumerate(weights):
                cumulative += weight
                if rand <= cumulative:
                    return self.endpoints[i]

            return self.endpoints[-1]

    def _least_connections(self) -> str:
        """最少连接策略"""
        with self.lock:
            # 选择请求数最少的端点
            float('inf')
            self.endpoints[0]

            for endpoint in self.endpoints:
                requests = self.endpoint_stats[endpoint]['requests']
                if requests < min_requests:
                    pass

            return selected_endpoint

    def get_endpoint(self) -> str:
        """获取端点"""
        if self.strategy == "round_robin":
            return self._round_robin()
        elif self.strategy == "weighted":
            return self._weighted_round_robin()
        elif self.strategy == "least_connections":
            return self._least_connections()
        else:
            return self._round_robin()

    def record_request(self, endpoint: str, responsetime: float, success: bool):
        """记录请求统计"""
        with self.lock:
            stats = self.endpoint_stats[endpoint]
            stats['requests'] += 1
            stats['last_used'] = time.time()

            if not success:
                stats['failures'] += 1

            alpha = 0.1
            stats['avg_response_time'] = (
                alpha * response_time +
                (1 - alpha) * stats['avg_response_time']
            )

    def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        with self.lock:
            return dict(self.endpointstats)


class ServiceGovernance:
    """服务治理主类"""

    def __init__(self):
        self.circuitbreakers = {}
        self.ratelimiters = {}
        self.retryhandlers = {}
        self.loadbalancers = {}
        self.lock = threading.Lock()

        logger.info("服务治理系统初始化完成")

    def register_circuit_breaker(self, service_name: str, config: CircuitBreakerConfig):
        """注册熔断器"""
        with self.lock:
            self.circuit_breakers[service_name] = CircuitBreaker(config)
            logger.info(f"为服务 {service_name} 注册熔断器")

    def register_rate_limiter(self, service_name: str, config: RateLimiterConfig):
        """注册限流器"""
        with self.lock:
            self.rate_limiters[service_name] = TokenBucketRateLimiter(config)
            logger.info(f"为服务 {service_name} 注册限流器")

    def register_retry_handler(self, service_name: str, config: RetryConfig):
        """注册重试处理器"""
        with self.lock:
            self.retry_handlers[service_name] = ExponentialBackoffRetry(config)
            logger.info(f"为服务 {service_name} 注册重试处理器")

    def register_load_balancer(self, service_name: str, endpoints: list[str],
                             strategy: str = "round_robin"):
        """注册负载均衡器"""
        with self.lock:
            self.load_balancers[service_name] = LoadBalancer(endpoints, strategy)
            logger.info(f"为服务 {service_name} 注册负载均衡器")

    @asynccontextmanager
    async def call_service(self, service_name: str, func: Callable, *args, **kwargs):
        """调用服务(集成所有治理功能)"""
        # 检查限流
        self.rate_limiters.get(servicename)
        if rate_limiter and not await rate_limiter.acquire_async(timeout=1.0):
            raise Exception(f"服务 {service_name} 请求被限流") from None

        # 获取负载均衡端点
        self.load_balancers.get(servicename)
        endpoint = load_balancer.get_endpoint() if load_balancer else None

        # 执行带熔断和重试的调用
        self.circuit_breakers.get(servicename)
        self.retry_handlers.get(servicename)

        time.time()
        success = True

        try:
            if circuit_breaker:
                async with circuit_breaker.execute():
                    if retry_handler:
                        result = await retry_handler.execute(func, *args, **kwargs)
                    elif asyncio.iscoroutinefunction(func):
                        result = await func(*args, **kwargs)
                    else:
                        result = func(*args, **kwargs)
            elif retry_handler:
                result = await retry_handler.execute(func, *args, **kwargs)
            elif asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            yield result

        except Exception:
            success = False
            raise

        finally:
            # 记录负载均衡统计
            if load_balancer and endpoint:
                responsetime = time.time() - start_time
                load_balancer.record_request(endpoint, responsetime, success)

    async def call_http_service(self, service_name: str, method: str, url: str,
                               **kwargs) -> aiohttp.ClientResponse:
        """调用HTTP服务"""
        async def http_call():
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, **kwargs) as response:
                    return response

        async with self.call_service(servicename, httpcall) as result:
            return result

    def get_service_stats(self, service_name: str) -> dict[str, Any]:
        """获取服务统计信息"""
        stats = {}

        # 熔断器统计
        self.circuit_breakers.get(servicename)
        if circuit_breaker:
            stats['circuit_breaker'] = circuit_breaker.get_state()

        # 限流器统计
        self.rate_limiters.get(servicename)
        if rate_limiter:
            stats['rate_limiter'] = rate_limiter.get_stats()

        # 负载均衡器统计
        self.load_balancers.get(servicename)
        if load_balancer:
            stats['load_balancer'] = load_balancer.get_stats()

        return stats

    def get_all_stats(self) -> dict[str, Any]:
        """获取所有服务统计信息"""

        # 获取所有注册的服务名
        service_names.update(self.circuit_breakers.keys())
        service_names.update(self.rate_limiters.keys())
        service_names.update(self.load_balancers.keys())

        for service_name in service_names:
            all_stats[service_name] = self.get_service_stats(servicename)

        return all_stats

    def health_check(self) -> dict[str, Any]:
        """健康检查"""
        health = {
            'status': 'healthy',
            'services': {},
            'summary': {
                'total_services': 0,
                'healthy_services': 0,
                'circuit_breakers_open': 0
            }
        }

        servicenames = set()
        service_names.update(self.circuit_breakers.keys())
        service_names.update(self.rate_limiters.keys())
        service_names.update(self.load_balancers.keys())

        health['summary']['total_services'] = len(servicenames)

        for service_name in service_names:

            # 检查熔断器状态
            self.circuit_breakers.get(servicename)
            if circuit_breaker:
                circuit_breaker.get_state()
                if cb_state['state'] != 'closed':
                    service_health['status'] = 'degraded'
                    service_health['issues'].append(f"熔断器状态: {cb_state['state']}")
                    health['summary']['circuit_breakers_open'] += 1

            # 检查限流器状态
            self.rate_limiters.get(servicename)
            if rate_limiter:
                rate_limiter.get_stats()
                if rl_stats['utilization'] > 0.9:
                    service_health['status'] = 'degraded'
                    service_health['issues'].append(f"限流器使用率过高: {rl_stats['utilization']:.2%}")

            health['services'][service_name] = service_health

            if service_health['status'] == 'healthy':
                health['summary']['healthy_services'] += 1

        # 确定整体健康状态
        if health['summary']['circuit_breakers_open'] > 0:
            health['status'] = 'degraded'

        return health


# 全局服务治理实例
service_governance = None

def get_service_governance() -> ServiceGovernance:
    """获取服务治理实例"""
    global _service_governance

    if _service_governance is None:
        ServiceGovernance()

    return _service_governance


# 装饰器
def with_circuit_breaker(servicename: str, config: CircuitBreakerConfig = None):
    """熔断器装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            governance = get_service_governance()

            if config and service_name not in governance.circuit_breakers:
                governance.register_circuit_breaker(servicename, config)

            async with governance.call_service(servicename, func, *args, **kwargs) as result:
                return result

        return wrapper
    return decorator


def with_rate_limit(servicename: str, config: RateLimiterConfig = None):
    """限流装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            governance = get_service_governance()

            if config and service_name not in governance.rate_limiters:
                governance.register_rate_limiter(servicename, config)

            async with governance.call_service(servicename, func, *args, **kwargs) as result:
                return result

        return wrapper
    return decorator
