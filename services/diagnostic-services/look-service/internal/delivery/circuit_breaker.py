#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
熔断器模块 - 实现服务调用保护机制

本模块提供了基于pybreaker的熔断器实现，用于防止级联故障和提供服务降级机制。
支持自定义熔断策略、失败计数、回退逻辑以及熔断器状态监控，确保在微服务架构中
系统的稳定性和可用性。
"""

import time
import logging
import threading
import functools
from typing import Dict, List, Optional, Tuple, Any, Callable, Union
from datetime import datetime
from enum import Enum

import grpc
import pybreaker
from prometheus_client import Counter, Gauge, Histogram

logger = logging.getLogger(__name__)

# 定义熔断器相关指标
CIRCUIT_STATE = Gauge('circuit_breaker_state', 'Circuit Breaker State (0=open, 1=half-open, 2=closed)', ['service', 'method'])
CIRCUIT_FAILURES = Counter('circuit_breaker_failures', 'Circuit Breaker Failure Count', ['service', 'method'])
CIRCUIT_SUCCESSES = Counter('circuit_breaker_successes', 'Circuit Breaker Success Count', ['service', 'method'])
FALLBACK_CALLS = Counter('circuit_breaker_fallback_calls', 'Circuit Breaker Fallback Calls', ['service', 'method'])
CIRCUIT_EXECUTION_TIME = Histogram('circuit_breaker_execution_time', 'Circuit Breaker Execution Time', ['service', 'method'])

class CircuitBreakerState(Enum):
    """熔断器状态枚举"""
    OPEN = 0       # 开路状态，请求直接失败
    HALF_OPEN = 1  # 半开路状态，尝试少量请求
    CLOSED = 2     # 闭路状态，正常处理请求

class CircuitBreakerMonitor:
    """熔断器监控器，用于跟踪和记录熔断器状态"""
    
    def __init__(self):
        """初始化熔断器监控器"""
        self.breakers = {}
        self.lock = threading.RLock()
        
    def register_breaker(self, service_name: str, method_name: str, breaker: pybreaker.CircuitBreaker):
        """
        注册熔断器
        
        Args:
            service_name: 服务名称
            method_name: 方法名称
            breaker: 熔断器实例
        """
        with self.lock:
            key = f"{service_name}.{method_name}"
            self.breakers[key] = {
                'breaker': breaker,
                'service': service_name,
                'method': method_name,
                'last_state': breaker.current_state,
                'failures': 0,
                'successes': 0,
                'last_failure': None,
                'last_success': None,
                'total_calls': 0
            }
            
            # 设置监听器
            breaker.add_listener(self._create_listener(service_name, method_name))
            
            # 初始化指标
            CIRCUIT_STATE.labels(service=service_name, method=method_name).set(CircuitBreakerState.CLOSED.value)
    
    def get_breaker(self, service_name: str, method_name: str) -> Optional[pybreaker.CircuitBreaker]:
        """
        获取熔断器实例
        
        Args:
            service_name: 服务名称
            method_name: 方法名称
            
        Returns:
            Optional[pybreaker.CircuitBreaker]: 熔断器实例
        """
        with self.lock:
            key = f"{service_name}.{method_name}"
            return self.breakers.get(key, {}).get('breaker')
    
    def get_status(self, service_name: str, method_name: str) -> Dict:
        """
        获取熔断器状态
        
        Args:
            service_name: 服务名称
            method_name: 方法名称
            
        Returns:
            Dict: 熔断器状态信息
        """
        with self.lock:
            key = f"{service_name}.{method_name}"
            if key not in self.breakers:
                return {'error': f"Circuit breaker not found: {key}"}
                
            breaker_info = self.breakers[key]
            breaker = breaker_info['breaker']
            
            return {
                'service': service_name,
                'method': method_name,
                'state': breaker.current_state,
                'failures': breaker_info['failures'],
                'successes': breaker_info['successes'],
                'failure_threshold': breaker.fail_max,
                'reset_timeout': breaker.reset_timeout,
                'last_failure': breaker_info['last_failure'],
                'last_success': breaker_info['last_success'],
                'total_calls': breaker_info['total_calls']
            }
    
    def get_all_status(self) -> List[Dict]:
        """
        获取所有熔断器状态
        
        Returns:
            List[Dict]: 所有熔断器状态信息列表
        """
        with self.lock:
            result = []
            for key, breaker_info in self.breakers.items():
                service_name = breaker_info['service']
                method_name = breaker_info['method']
                result.append(self.get_status(service_name, method_name))
            return result
    
    def _create_listener(self, service_name: str, method_name: str) -> pybreaker.CircuitBreakerListener:
        """
        创建熔断器监听器
        
        Args:
            service_name: 服务名称
            method_name: 方法名称
            
        Returns:
            pybreaker.CircuitBreakerListener: 监听器实例
        """
        class StatusListener(pybreaker.CircuitBreakerListener):
            def __init__(self, monitor):
                self.monitor = monitor
                self.service = service_name
                self.method = method_name
            
            def state_change(self, cb, old_state, new_state):
                key = f"{self.service}.{self.method}"
                with self.monitor.lock:
                    if key in self.monitor.breakers:
                        self.monitor.breakers[key]['last_state'] = new_state
                
                # 更新指标
                if new_state == 'open':
                    state_value = CircuitBreakerState.OPEN.value
                elif new_state == 'half-open':
                    state_value = CircuitBreakerState.HALF_OPEN.value
                else:  # 'closed'
                    state_value = CircuitBreakerState.CLOSED.value
                
                CIRCUIT_STATE.labels(service=self.service, method=self.method).set(state_value)
                
                logger.info(f"Circuit breaker {key} changed from {old_state} to {new_state}")
            
            def failure(self, cb, exc):
                key = f"{self.service}.{self.method}"
                with self.monitor.lock:
                    if key in self.monitor.breakers:
                        self.monitor.breakers[key]['failures'] += 1
                        self.monitor.breakers[key]['last_failure'] = datetime.now().isoformat()
                        self.monitor.breakers[key]['total_calls'] += 1
                
                # 更新指标
                CIRCUIT_FAILURES.labels(service=self.service, method=self.method).inc()
                
                logger.warning(f"Circuit breaker {key} recorded a failure: {str(exc)}")
            
            def success(self, cb):
                key = f"{self.service}.{self.method}"
                with self.monitor.lock:
                    if key in self.monitor.breakers:
                        self.monitor.breakers[key]['successes'] += 1
                        self.monitor.breakers[key]['last_success'] = datetime.now().isoformat()
                        self.monitor.breakers[key]['total_calls'] += 1
                
                # 更新指标
                CIRCUIT_SUCCESSES.labels(service=self.service, method=self.method).inc()
                
                logger.debug(f"Circuit breaker {key} recorded a success")
        
        return StatusListener(self)

# 全局监控器实例
monitor = CircuitBreakerMonitor()

def circuit_breaker(
    service_name: str,
    method_name: str,
    failure_threshold: int = 5,
    reset_timeout: int = 30,
    fallback_function: Optional[Callable] = None,
    exclude_exceptions: Optional[List[Exception]] = None
):
    """
    熔断器装饰器
    
    Args:
        service_name: 服务名称
        method_name: 方法名称
        failure_threshold: 故障阈值
        reset_timeout: 重置超时(秒)
        fallback_function: 回退函数
        exclude_exceptions: 不计入故障的异常列表
        
    Returns:
        装饰器函数
    """
    # 创建熔断器
    breaker = pybreaker.CircuitBreaker(
        fail_max=failure_threshold,
        reset_timeout=reset_timeout,
        exclude=[exc for exc in (exclude_exceptions or [])]
    )
    
    # 注册到监控器
    monitor.register_breaker(service_name, method_name, breaker)
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 记录开始时间
            start_time = time.time()
            
            try:
                # 尝试通过熔断器调用函数
                result = breaker.call(func, *args, **kwargs)
                
                # 记录执行时间
                execution_time = time.time() - start_time
                CIRCUIT_EXECUTION_TIME.labels(
                    service=service_name, 
                    method=method_name
                ).observe(execution_time)
                
                return result
                
            except pybreaker.CircuitBreakerError as e:
                # 熔断器打开，调用回退函数
                logger.warning(
                    f"Circuit breaker for {service_name}.{method_name} is OPEN, "
                    f"falling back to alternative implementation"
                )
                
                FALLBACK_CALLS.labels(service=service_name, method=method_name).inc()
                
                if fallback_function:
                    return fallback_function(*args, **kwargs)
                raise
                
            except Exception as e:
                # 其他异常，直接抛出
                logger.error(
                    f"Error calling {service_name}.{method_name}: {str(e)}"
                )
                raise
                
        return wrapper
    
    return decorator

class CircuitBreakerInterceptor(grpc.UnaryUnaryClientInterceptor):
    """gRPC熔断器拦截器，用于自动为gRPC调用添加熔断保护"""
    
    def __init__(
        self, 
        service_name: str,
        failure_threshold: int = 5,
        reset_timeout: int = 30,
        fallback_function: Optional[Callable] = None,
        exclude_exceptions: Optional[List[Exception]] = None
    ):
        """
        初始化gRPC熔断器拦截器
        
        Args:
            service_name: 服务名称
            failure_threshold: 故障阈值
            reset_timeout: 重置超时(秒)
            fallback_function: 回退函数
            exclude_exceptions: 不计入故障的异常列表
        """
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.fallback_function = fallback_function
        self.exclude_exceptions = exclude_exceptions or [
            grpc.RpcError
        ]
        
        # 存储方法熔断器
        self.method_breakers = {}
    
    def _get_breaker(self, method_name: str) -> pybreaker.CircuitBreaker:
        """获取方法对应的熔断器"""
        if method_name not in self.method_breakers:
            # 创建新的熔断器
            breaker = pybreaker.CircuitBreaker(
                fail_max=self.failure_threshold,
                reset_timeout=self.reset_timeout,
                exclude=self.exclude_exceptions
            )
            
            # 注册到监控器
            monitor.register_breaker(self.service_name, method_name, breaker)
            
            self.method_breakers[method_name] = breaker
            
        return self.method_breakers[method_name]
    
    def intercept_unary_unary(self, continuation, client_call_details, request):
        """
        拦截一元gRPC调用
        
        Args:
            continuation: 继续调用的函数
            client_call_details: 调用详情
            request: 请求内容
            
        Returns:
            gRPC响应
        """
        method_name = client_call_details.method.decode('utf-8').split('/')[-1]
        breaker = self._get_breaker(method_name)
        
        # 记录开始时间
        start_time = time.time()
        
        try:
            # 尝试通过熔断器调用gRPC方法
            def call_rpc():
                return continuation(client_call_details, request)
                
            response_future = breaker.call(call_rpc)
            
            # 记录执行时间
            execution_time = time.time() - start_time
            CIRCUIT_EXECUTION_TIME.labels(
                service=self.service_name, 
                method=method_name
            ).observe(execution_time)
            
            return response_future
            
        except pybreaker.CircuitBreakerError as e:
            # 熔断器打开，调用回退函数
            logger.warning(
                f"Circuit breaker for {self.service_name}.{method_name} is OPEN, "
                f"falling back to alternative implementation"
            )
            
            FALLBACK_CALLS.labels(service=self.service_name, method=method_name).inc()
            
            if self.fallback_function:
                return self.fallback_function(method_name, request)
            raise
            
        except Exception as e:
            # 其他异常，直接抛出
            logger.error(
                f"Error calling {self.service_name}.{method_name}: {str(e)}"
            )
            raise

def create_circuit_breaker_channel(
    channel: grpc.Channel,
    service_name: str,
    failure_threshold: int = 5,
    reset_timeout: int = 30,
    fallback_function: Optional[Callable] = None
) -> grpc.Channel:
    """
    创建带熔断器的gRPC通道
    
    Args:
        channel: 原始gRPC通道
        service_name: 服务名称
        failure_threshold: 故障阈值
        reset_timeout: 重置超时(秒)
        fallback_function: 回退函数
        
    Returns:
        grpc.Channel: 带熔断器的gRPC通道
    """
    interceptor = CircuitBreakerInterceptor(
        service_name=service_name,
        failure_threshold=failure_threshold,
        reset_timeout=reset_timeout,
        fallback_function=fallback_function
    )
    
    return grpc.intercept_channel(channel, interceptor) 