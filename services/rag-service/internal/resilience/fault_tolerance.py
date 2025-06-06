"""
fault_tolerance - 索克生活项目模块
"""

from ..observability.metrics import MetricsCollector
from dataclasses import dataclass, field
from enum import Enum
from loguru import logger
from typing import Dict, List, Any, Optional, Callable, Union
import asyncio
import random
import time
import uuid

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
故障恢复和容错机制 - 确保RAG服务的高可用性
"""



class HealthStatus(str, Enum):
    """健康状态"""
    HEALTHY = "healthy"         # 健康
    DEGRADED = "degraded"       # 降级
    UNHEALTHY = "unhealthy"     # 不健康
    CRITICAL = "critical"       # 严重
    UNKNOWN = "unknown"         # 未知

class FailureType(str, Enum):
    """故障类型"""
    TIMEOUT = "timeout"         # 超时
    CONNECTION = "connection"   # 连接失败
    RATE_LIMIT = "rate_limit"   # 限流
    SERVER_ERROR = "server_error"  # 服务器错误
    RESOURCE_EXHAUSTED = "resource_exhausted"  # 资源耗尽
    DEPENDENCY_FAILURE = "dependency_failure"  # 依赖失败

class RecoveryStrategy(str, Enum):
    """恢复策略"""
    RETRY = "retry"             # 重试
    FALLBACK = "fallback"       # 降级
    CIRCUIT_BREAKER = "circuit_breaker"  # 断路器
    BULKHEAD = "bulkhead"       # 舱壁隔离
    TIMEOUT = "timeout"         # 超时控制

@dataclass
class HealthCheck:
    """健康检查"""
    id: str
    name: str
    check_function: Callable
    interval: float = 30.0      # 检查间隔（秒）
    timeout: float = 5.0        # 超时时间（秒）
    enabled: bool = True
    last_check: Optional[float] = None
    last_status: HealthStatus = HealthStatus.UNKNOWN
    consecutive_failures: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "interval": self.interval,
            "timeout": self.timeout,
            "enabled": self.enabled,
            "last_check": self.last_check,
            "last_status": self.last_status.value,
            "consecutive_failures": self.consecutive_failures,
            "metadata": self.metadata
        }

@dataclass
class FailureRecord:
    """故障记录"""
    id: str
    service_name: str
    failure_type: FailureType
    timestamp: float = field(default_factory=time.time)
    error_message: str = ""
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolution_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "service_name": self.service_name,
            "failure_type": self.failure_type.value,
            "timestamp": self.timestamp,
            "error_message": self.error_message,
            "stack_trace": self.stack_trace,
            "context": self.context,
            "resolved": self.resolved,
            "resolution_time": self.resolution_time
        }

@dataclass
class RetryConfig:
    """重试配置"""
    max_attempts: int = 3
    base_delay: float = 1.0     # 基础延迟（秒）
    max_delay: float = 60.0     # 最大延迟（秒）
    exponential_base: float = 2.0  # 指数退避基数
    jitter: bool = True         # 是否添加随机抖动
    
    def calculate_delay(self, attempt: int) -> float:
        """计算延迟时间"""
        delay = self.base_delay * (self.exponential_base ** (attempt - 1))
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            delay *= (0.5 + random.random() * 0.5)  # 添加50%的随机抖动
        
        return delay

class RetryManager:
    """重试管理器"""
    
    def __init__(self, default_config: Optional[RetryConfig] = None):
        self.default_config = default_config or RetryConfig()
        self.retry_stats: Dict[str, Dict[str, int]] = {}
    
    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        retry_config: Optional[RetryConfig] = None,
        operation_name: str = "unknown",
        **kwargs
    ) -> Any:
        """带重试的执行函数"""
        config = retry_config or self.default_config
        last_exception = None
        
        for attempt in range(1, config.max_attempts + 1):
            try:
                result = await func(*args, **kwargs)
                
                # 记录成功统计
                self._record_retry_stat(operation_name, "success")
                
                if attempt > 1:
                    logger.info(f"重试成功: {operation_name}, 尝试次数: {attempt}")
                
                return result
                
            except Exception as e:
                last_exception = e
                
                # 记录失败统计
                self._record_retry_stat(operation_name, "failure")
                
                if attempt < config.max_attempts:
                    delay = config.calculate_delay(attempt)
                    logger.warning(f"重试 {operation_name} (尝试 {attempt}/{config.max_attempts}): {e}, 等待 {delay:.2f}s")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"重试失败 {operation_name} (最大尝试次数 {config.max_attempts}): {e}")
        
        # 所有重试都失败了
        raise last_exception
    
    def _record_retry_stat(self, operation_name: str, result: str):
        """记录重试统计"""
        if operation_name not in self.retry_stats:
            self.retry_stats[operation_name] = {"success": 0, "failure": 0}
        
        self.retry_stats[operation_name][result] += 1
    
    def get_retry_statistics(self) -> Dict[str, Dict[str, int]]:
        """获取重试统计"""
        return self.retry_stats.copy()

class FallbackManager:
    """降级管理器"""
    
    def __init__(self):
        self.fallback_handlers: Dict[str, Callable] = {}
        self.fallback_stats: Dict[str, int] = {}
    
    def register_fallback(self, service_name: str, fallback_handler: Callable):
        """注册降级处理器"""
        self.fallback_handlers[service_name] = fallback_handler
        logger.info(f"降级处理器已注册: {service_name}")
    
    async def execute_with_fallback(
        self,
        primary_func: Callable,
        service_name: str,
        *args,
        **kwargs
    ) -> Any:
        """带降级的执行函数"""
        try:
            return await primary_func(*args, **kwargs)
        
        except Exception as e:
            logger.warning(f"主服务失败，启用降级: {service_name} - {e}")
            
            # 记录降级统计
            self.fallback_stats[service_name] = self.fallback_stats.get(service_name, 0) + 1
            
            # 执行降级处理
            fallback_handler = self.fallback_handlers.get(service_name)
            if fallback_handler:
                try:
                    result = await fallback_handler(*args, **kwargs)
                    logger.info(f"降级处理成功: {service_name}")
                    return result
                except Exception as fallback_error:
                    logger.error(f"降级处理也失败: {service_name} - {fallback_error}")
                    raise fallback_error
            else:
                logger.error(f"未找到降级处理器: {service_name}")
                raise e
    
    def get_fallback_statistics(self) -> Dict[str, int]:
        """获取降级统计"""
        return self.fallback_stats.copy()

class TimeoutManager:
    """超时管理器"""
    
    def __init__(self, default_timeout: float = 30.0):
        self.default_timeout = default_timeout
        self.timeout_stats: Dict[str, int] = {}
    
    async def execute_with_timeout(
        self,
        func: Callable,
        *args,
        timeout: Optional[float] = None,
        operation_name: str = "unknown",
        **kwargs
    ) -> Any:
        """带超时的执行函数"""
        timeout_value = timeout or self.default_timeout
        
        try:
            result = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=timeout_value
            )
            return result
            
        except asyncio.TimeoutError:
            # 记录超时统计
            self.timeout_stats[operation_name] = self.timeout_stats.get(operation_name, 0) + 1
            
            logger.error(f"操作超时: {operation_name} (超时时间: {timeout_value}s)")
            raise
    
    def get_timeout_statistics(self) -> Dict[str, int]:
        """获取超时统计"""
        return self.timeout_stats.copy()

class BulkheadManager:
    """舱壁隔离管理器"""
    
    def __init__(self):
        self.resource_pools: Dict[str, asyncio.Semaphore] = {}
        self.pool_stats: Dict[str, Dict[str, int]] = {}
    
    def create_resource_pool(self, pool_name: str, max_concurrent: int):
        """创建资源池"""
        self.resource_pools[pool_name] = asyncio.Semaphore(max_concurrent)
        self.pool_stats[pool_name] = {"acquired": 0, "rejected": 0}
        logger.info(f"资源池已创建: {pool_name} (最大并发: {max_concurrent})")
    
    async def execute_with_bulkhead(
        self,
        func: Callable,
        pool_name: str,
        *args,
        **kwargs
    ) -> Any:
        """带舱壁隔离的执行函数"""
        if pool_name not in self.resource_pools:
            raise ValueError(f"资源池不存在: {pool_name}")
        
        semaphore = self.resource_pools[pool_name]
        
        # 尝试获取资源
        acquired = semaphore.acquire_nowait()
        if not acquired:
            # 资源池已满，拒绝请求
            self.pool_stats[pool_name]["rejected"] += 1
            raise Exception(f"资源池已满: {pool_name}")
        
        try:
            # 记录获取统计
            self.pool_stats[pool_name]["acquired"] += 1
            
            # 执行函数
            result = await func(*args, **kwargs)
            return result
            
        finally:
            # 释放资源
            semaphore.release()
    
    def get_bulkhead_statistics(self) -> Dict[str, Dict[str, int]]:
        """获取舱壁隔离统计"""
        return self.pool_stats.copy()

class HealthMonitor:
    """健康监控器"""
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        self.health_checks: Dict[str, HealthCheck] = {}
        self.metrics_collector = metrics_collector
        self.monitoring_task: Optional[asyncio.Task] = None
        self.is_monitoring = False
    
    def register_health_check(self, health_check: HealthCheck):
        """注册健康检查"""
        self.health_checks[health_check.id] = health_check
        logger.info(f"健康检查已注册: {health_check.name}")
    
    async def start_monitoring(self):
        """开始监控"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("健康监控已启动")
    
    async def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("健康监控已停止")
    
    async def _monitoring_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                # 执行所有健康检查
                for health_check in self.health_checks.values():
                    if health_check.enabled:
                        await self._execute_health_check(health_check)
                
                # 等待最小间隔
                await asyncio.sleep(1.0)
                
            except Exception as e:
                logger.error(f"健康监控循环错误: {e}")
                await asyncio.sleep(5.0)
    
    async def _execute_health_check(self, health_check: HealthCheck):
        """执行健康检查"""
        current_time = time.time()
        
        # 检查是否需要执行
        if (health_check.last_check and 
            current_time - health_check.last_check < health_check.interval):
            return
        
        try:
            # 执行健康检查
            result = await asyncio.wait_for(
                health_check.check_function(),
                timeout=health_check.timeout
            )
            
            # 更新状态
            if result:
                health_check.last_status = HealthStatus.HEALTHY
                health_check.consecutive_failures = 0
            else:
                health_check.last_status = HealthStatus.UNHEALTHY
                health_check.consecutive_failures += 1
            
        except asyncio.TimeoutError:
            health_check.last_status = HealthStatus.UNHEALTHY
            health_check.consecutive_failures += 1
            logger.warning(f"健康检查超时: {health_check.name}")
            
        except Exception as e:
            health_check.last_status = HealthStatus.UNHEALTHY
            health_check.consecutive_failures += 1
            logger.error(f"健康检查失败: {health_check.name} - {e}")
        
        finally:
            health_check.last_check = current_time
            
            # 记录指标
            if self.metrics_collector:
                await self.metrics_collector.record_gauge(
                    "health_check_status",
                    1 if health_check.last_status == HealthStatus.HEALTHY else 0,
                    {"check_name": health_check.name}
                )
    
    async def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        overall_status = HealthStatus.HEALTHY
        checks_status = {}
        
        for check_id, health_check in self.health_checks.items():
            checks_status[check_id] = health_check.to_dict()
            
            # 确定整体状态
            if health_check.last_status == HealthStatus.UNHEALTHY:
                if health_check.consecutive_failures >= 3:
                    overall_status = HealthStatus.CRITICAL
                elif overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
        
        return {
            "overall_status": overall_status.value,
            "checks": checks_status,
            "timestamp": time.time()
        }

class FailureDetector:
    """故障检测器"""
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        self.failure_records: List[FailureRecord] = []
        self.metrics_collector = metrics_collector
        self.failure_thresholds = {
            "error_rate": 0.1,      # 10%错误率
            "response_time": 5.0,   # 5秒响应时间
            "consecutive_failures": 5  # 连续5次失败
        }
    
    async def record_failure(
        self,
        service_name: str,
        failure_type: FailureType,
        error_message: str = "",
        stack_trace: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """记录故障"""
        failure_id = str(uuid.uuid4())
        
        failure_record = FailureRecord(
            id=failure_id,
            service_name=service_name,
            failure_type=failure_type,
            error_message=error_message,
            stack_trace=stack_trace,
            context=context or {}
        )
        
        self.failure_records.append(failure_record)
        
        # 记录指标
        if self.metrics_collector:
            await self.metrics_collector.increment_counter(
                "failures_total",
                {
                    "service": service_name,
                    "type": failure_type.value
                }
            )
        
        logger.error(f"故障已记录: {service_name} - {failure_type.value} - {error_message}")
        
        # 检查是否需要触发告警
        await self._check_failure_patterns(service_name)
        
        return failure_id
    
    async def resolve_failure(self, failure_id: str) -> bool:
        """解决故障"""
        for failure_record in self.failure_records:
            if failure_record.id == failure_id and not failure_record.resolved:
                failure_record.resolved = True
                failure_record.resolution_time = time.time()
                
                logger.info(f"故障已解决: {failure_record.service_name} - {failure_id}")
                return True
        
        return False
    
    async def _check_failure_patterns(self, service_name: str):
        """检查故障模式"""
        current_time = time.time()
        recent_window = 300  # 5分钟窗口
        
        # 获取最近的故障记录
        recent_failures = [
            f for f in self.failure_records
            if (f.service_name == service_name and 
                current_time - f.timestamp <= recent_window and
                not f.resolved)
        ]
        
        # 检查连续失败
        if len(recent_failures) >= self.failure_thresholds["consecutive_failures"]:
            logger.critical(f"检测到连续故障: {service_name} ({len(recent_failures)} 次)")
            
            # 这里可以触发自动恢复或告警
            await self._trigger_recovery_action(service_name, "consecutive_failures")
    
    async def _trigger_recovery_action(self, service_name: str, pattern_type: str):
        """触发恢复动作"""
        logger.info(f"触发恢复动作: {service_name} - {pattern_type}")
        
        # 这里可以实现自动恢复逻辑
        # 例如：重启服务、切换到备用实例、发送告警等
    
    def get_failure_statistics(self) -> Dict[str, Any]:
        """获取故障统计"""
        current_time = time.time()
        
        # 按服务分组统计
        service_stats = {}
        for failure in self.failure_records:
            service = failure.service_name
            if service not in service_stats:
                service_stats[service] = {
                    "total": 0,
                    "resolved": 0,
                    "unresolved": 0,
                    "types": {}
                }
            
            service_stats[service]["total"] += 1
            
            if failure.resolved:
                service_stats[service]["resolved"] += 1
            else:
                service_stats[service]["unresolved"] += 1
            
            failure_type = failure.failure_type.value
            if failure_type not in service_stats[service]["types"]:
                service_stats[service]["types"][failure_type] = 0
            service_stats[service]["types"][failure_type] += 1
        
        return {
            "total_failures": len(self.failure_records),
            "service_statistics": service_stats,
            "timestamp": current_time
        }

class FaultToleranceManager:
    """容错管理器"""
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        self.metrics_collector = metrics_collector
        
        # 初始化各个组件
        self.retry_manager = RetryManager()
        self.fallback_manager = FallbackManager()
        self.timeout_manager = TimeoutManager()
        self.bulkhead_manager = BulkheadManager()
        self.health_monitor = HealthMonitor(metrics_collector)
        self.failure_detector = FailureDetector(metrics_collector)
        
        # 容错策略配置
        self.strategies: Dict[str, List[RecoveryStrategy]] = {}
    
    def configure_service_strategies(
        self,
        service_name: str,
        strategies: List[RecoveryStrategy]
    ):
        """配置服务的容错策略"""
        self.strategies[service_name] = strategies
        logger.info(f"容错策略已配置: {service_name} - {[s.value for s in strategies]}")
    
    async def execute_with_fault_tolerance(
        self,
        func: Callable,
        service_name: str,
        *args,
        retry_config: Optional[RetryConfig] = None,
        timeout: Optional[float] = None,
        pool_name: Optional[str] = None,
        **kwargs
    ) -> Any:
        """带容错的执行函数"""
        strategies = self.strategies.get(service_name, [RecoveryStrategy.RETRY])
        
        # 构建执行链
        execution_func = func
        
        # 应用超时控制
        if RecoveryStrategy.TIMEOUT in strategies:
            async def timeout_wrapper(*args, **kwargs):
                return await self.timeout_manager.execute_with_timeout(
                    execution_func, *args, timeout=timeout, operation_name=service_name, **kwargs
                )
            execution_func = timeout_wrapper
        
        # 应用舱壁隔离
        if RecoveryStrategy.BULKHEAD in strategies and pool_name:
            async def bulkhead_wrapper(*args, **kwargs):
                return await self.bulkhead_manager.execute_with_bulkhead(
                    execution_func, pool_name, *args, **kwargs
                )
            execution_func = bulkhead_wrapper
        
        # 应用重试
        if RecoveryStrategy.RETRY in strategies:
            async def retry_wrapper(*args, **kwargs):
                return await self.retry_manager.execute_with_retry(
                    execution_func, *args, retry_config=retry_config, 
                    operation_name=service_name, **kwargs
                )
            execution_func = retry_wrapper
        
        # 应用降级
        if RecoveryStrategy.FALLBACK in strategies:
            async def fallback_wrapper(*args, **kwargs):
                return await self.fallback_manager.execute_with_fallback(
                    execution_func, service_name, *args, **kwargs
                )
            execution_func = fallback_wrapper
        
        try:
            result = await execution_func(*args, **kwargs)
            return result
            
        except Exception as e:
            # 记录故障
            await self.failure_detector.record_failure(
                service_name=service_name,
                failure_type=self._classify_failure(e),
                error_message=str(e),
                context={"args": str(args), "kwargs": str(kwargs)}
            )
            raise
    
    def _classify_failure(self, exception: Exception) -> FailureType:
        """分类故障类型"""
        if isinstance(exception, asyncio.TimeoutError):
            return FailureType.TIMEOUT
        elif isinstance(exception, ConnectionError):
            return FailureType.CONNECTION
        elif "rate limit" in str(exception).lower():
            return FailureType.RATE_LIMIT
        elif "resource" in str(exception).lower():
            return FailureType.RESOURCE_EXHAUSTED
        else:
            return FailureType.SERVER_ERROR
    
    async def start_monitoring(self):
        """启动监控"""
        await self.health_monitor.start_monitoring()
    
    async def stop_monitoring(self):
        """停止监控"""
        await self.health_monitor.stop_monitoring()
    
    def register_health_check(self, health_check: HealthCheck):
        """注册健康检查"""
        self.health_monitor.register_health_check(health_check)
    
    def register_fallback(self, service_name: str, fallback_handler: Callable):
        """注册降级处理器"""
        self.fallback_manager.register_fallback(service_name, fallback_handler)
    
    def create_resource_pool(self, pool_name: str, max_concurrent: int):
        """创建资源池"""
        self.bulkhead_manager.create_resource_pool(pool_name, max_concurrent)
    
    async def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        health_status = await self.health_monitor.get_health_status()
        failure_stats = self.failure_detector.get_failure_statistics()
        retry_stats = self.retry_manager.get_retry_statistics()
        fallback_stats = self.fallback_manager.get_fallback_statistics()
        timeout_stats = self.timeout_manager.get_timeout_statistics()
        bulkhead_stats = self.bulkhead_manager.get_bulkhead_statistics()
        
        return {
            "health": health_status,
            "failures": failure_stats,
            "retry": retry_stats,
            "fallback": fallback_stats,
            "timeout": timeout_stats,
            "bulkhead": bulkhead_stats,
            "timestamp": time.time()
        }

# 全局容错管理器实例
_fault_tolerance_manager: Optional[FaultToleranceManager] = None

def initialize_fault_tolerance_manager(
    metrics_collector: Optional[MetricsCollector] = None
) -> FaultToleranceManager:
    """初始化容错管理器"""
    global _fault_tolerance_manager
    _fault_tolerance_manager = FaultToleranceManager(metrics_collector)
    return _fault_tolerance_manager

def get_fault_tolerance_manager() -> Optional[FaultToleranceManager]:
    """获取容错管理器实例"""
    return _fault_tolerance_manager

# 容错装饰器
def fault_tolerant(
    service_name: str,
    strategies: Optional[List[RecoveryStrategy]] = None,
    retry_config: Optional[RetryConfig] = None,
    timeout: Optional[float] = None,
    pool_name: Optional[str] = None
):
    """容错装饰器"""
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            if not _fault_tolerance_manager:
                return await func(*args, **kwargs)
            
            # 配置策略
            if strategies:
                _fault_tolerance_manager.configure_service_strategies(service_name, strategies)
            
            return await _fault_tolerance_manager.execute_with_fault_tolerance(
                func, service_name, *args,
                retry_config=retry_config,
                timeout=timeout,
                pool_name=pool_name,
                **kwargs
            )
        
        return wrapper
    return decorator

def health_check(check_id: str, name: str, interval: float = 30.0, timeout: float = 5.0):
    """健康检查装饰器"""
    def decorator(func: Callable):
        if _fault_tolerance_manager:
            health_check_obj = HealthCheck(
                id=check_id,
                name=name,
                check_function=func,
                interval=interval,
                timeout=timeout
            )
            _fault_tolerance_manager.register_health_check(health_check_obj)
        
        return func
    
    return decorator

def fallback_handler(service_name: str):
    """降级处理器装饰器"""
    def decorator(func: Callable):
        if _fault_tolerance_manager:
            _fault_tolerance_manager.register_fallback(service_name, func)
        
        return func
    
    return decorator 