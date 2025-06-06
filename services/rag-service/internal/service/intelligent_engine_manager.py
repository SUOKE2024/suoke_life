"""
intelligent_engine_manager - 索克生活项目模块
"""

from ..cache.advanced_cache import AdvancedCacheManager
from ..observability.metrics import MetricsCollector
from ..observability.tracing import trace_operation, SpanKind
from ..resilience.circuit_breaker import CircuitBreaker
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Type, Callable, Union
import asyncio
import logging
import threading

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能引擎管理器

统一管理和协调所有智能引擎，提供：
- 引擎注册与发现
- 生命周期管理
- 数据共享与缓存
- 性能监控与优化
- 引擎间协同工作
- 统一配置管理
"""



class EngineStatus(str, Enum):
    """引擎状态"""
    INITIALIZING = "initializing"           # 初始化中
    READY = "ready"                         # 就绪
    RUNNING = "running"                     # 运行中
    PAUSED = "paused"                       # 暂停
    ERROR = "error"                         # 错误
    STOPPED = "stopped"                     # 已停止

class EngineType(str, Enum):
    """引擎类型"""
    NUTRITION = "nutrition"                 # 营养管理
    ENVIRONMENT_HEALTH = "environment_health"  # 环境健康
    RECOMMENDATION = "recommendation"       # 推荐引擎
    LEARNING = "learning"                   # 学习引擎
    HEALTH_MONITORING = "health_monitoring" # 健康监测
    DIAGNOSTIC = "diagnostic"               # 诊断辅助
    PREVENTION = "prevention"               # 预防医学
    MULTIMODAL = "multimodal"              # 多模态处理
    KNOWLEDGE_GRAPH = "knowledge_graph"     # 知识图谱
    ROUTING = "routing"                     # 智能路由

class EngineCapability(str, Enum):
    """引擎能力"""
    ASSESSMENT = "assessment"               # 评估能力
    RECOMMENDATION = "recommendation"       # 推荐能力
    MONITORING = "monitoring"               # 监控能力
    ANALYSIS = "analysis"                   # 分析能力
    PREDICTION = "prediction"               # 预测能力
    OPTIMIZATION = "optimization"           # 优化能力
    LEARNING = "learning"                   # 学习能力
    INTEGRATION = "integration"             # 集成能力

@dataclass
class EngineMetadata:
    """引擎元数据"""
    engine_id: str
    engine_type: EngineType
    name: str
    description: str
    version: str
    capabilities: List[EngineCapability] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    config_schema: Dict[str, Any] = field(default_factory=dict)
    health_check_interval: int = 30  # 健康检查间隔（秒）
    max_concurrent_requests: int = 100
    timeout_seconds: int = 30
    priority: int = 1  # 优先级，数字越大优先级越高

@dataclass
class EngineInstance:
    """引擎实例"""
    metadata: EngineMetadata
    instance: Any
    status: EngineStatus = EngineStatus.INITIALIZING
    created_at: datetime = field(default_factory=datetime.now)
    last_health_check: Optional[datetime] = None
    error_count: int = 0
    request_count: int = 0
    total_processing_time: float = 0.0
    circuit_breaker: Optional[CircuitBreaker] = None
    
    @property
    def average_processing_time(self) -> float:
        """平均处理时间"""
        if self.request_count == 0:
            return 0.0
        return self.total_processing_time / self.request_count
    
    @property
    def error_rate(self) -> float:
        """错误率"""
        if self.request_count == 0:
            return 0.0
        return self.error_count / self.request_count

@dataclass
class EngineRequest:
    """引擎请求"""
    request_id: str
    engine_id: str
    method_name: str
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1
    timeout: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EngineResponse:
    """引擎响应"""
    request_id: str
    engine_id: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    processing_time: float = 0.0
    completed_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

class EngineRegistry:
    """引擎注册表"""
    
    def __init__(self):
        self._engines: Dict[str, EngineInstance] = {}
        self._engine_types: Dict[EngineType, List[str]] = defaultdict(list)
        self._capabilities: Dict[EngineCapability, List[str]] = defaultdict(list)
        self._lock = threading.RLock()
    
    def register_engine(self, metadata: EngineMetadata, instance: Any) -> bool:
        """注册引擎"""
        with self._lock:
            if metadata.engine_id in self._engines:
                return False
            
            # 创建断路器
            circuit_breaker = CircuitBreaker(
                failure_threshold=5,
                recovery_timeout=60,
                expected_exception=Exception
            )
            
            engine_instance = EngineInstance(
                metadata=metadata,
                instance=instance,
                circuit_breaker=circuit_breaker
            )
            
            self._engines[metadata.engine_id] = engine_instance
            self._engine_types[metadata.engine_type].append(metadata.engine_id)
            
            for capability in metadata.capabilities:
                self._capabilities[capability].append(metadata.engine_id)
            
            return True
    
    def unregister_engine(self, engine_id: str) -> bool:
        """注销引擎"""
        with self._lock:
            if engine_id not in self._engines:
                return False
            
            engine_instance = self._engines[engine_id]
            metadata = engine_instance.metadata
            
            # 从类型映射中移除
            if engine_id in self._engine_types[metadata.engine_type]:
                self._engine_types[metadata.engine_type].remove(engine_id)
            
            # 从能力映射中移除
            for capability in metadata.capabilities:
                if engine_id in self._capabilities[capability]:
                    self._capabilities[capability].remove(engine_id)
            
            # 移除引擎实例
            del self._engines[engine_id]
            return True
    
    def get_engine(self, engine_id: str) -> Optional[EngineInstance]:
        """获取引擎实例"""
        with self._lock:
            return self._engines.get(engine_id)
    
    def get_engines_by_type(self, engine_type: EngineType) -> List[EngineInstance]:
        """根据类型获取引擎"""
        with self._lock:
            engine_ids = self._engine_types.get(engine_type, [])
            return [self._engines[eid] for eid in engine_ids if eid in self._engines]
    
    def get_engines_by_capability(self, capability: EngineCapability) -> List[EngineInstance]:
        """根据能力获取引擎"""
        with self._lock:
            engine_ids = self._capabilities.get(capability, [])
            return [self._engines[eid] for eid in engine_ids if eid in self._engines]
    
    def list_all_engines(self) -> List[EngineInstance]:
        """列出所有引擎"""
        with self._lock:
            return list(self._engines.values())
    
    def update_engine_status(self, engine_id: str, status: EngineStatus):
        """更新引擎状态"""
        with self._lock:
            if engine_id in self._engines:
                self._engines[engine_id].status = status

class EngineLoadBalancer:
    """引擎负载均衡器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def select_engine(
        self,
        engines: List[EngineInstance],
        strategy: str = "round_robin"
    ) -> Optional[EngineInstance]:
        """选择引擎"""
        
        # 过滤可用引擎
        available_engines = [
            engine for engine in engines
            if engine.status == EngineStatus.READY and
            (not engine.circuit_breaker or not engine.circuit_breaker.is_open())
        ]
        
        if not available_engines:
            return None
        
        if strategy == "round_robin":
            return self._round_robin_select(available_engines)
        elif strategy == "least_connections":
            return self._least_connections_select(available_engines)
        elif strategy == "fastest_response":
            return self._fastest_response_select(available_engines)
        elif strategy == "priority":
            return self._priority_select(available_engines)
        else:
            return available_engines[0]
    
    def _round_robin_select(self, engines: List[EngineInstance]) -> EngineInstance:
        """轮询选择"""
        # 简化实现，实际应该维护轮询状态
        return min(engines, key=lambda e: e.request_count)
    
    def _least_connections_select(self, engines: List[EngineInstance]) -> EngineInstance:
        """最少连接选择"""
        return min(engines, key=lambda e: e.request_count)
    
    def _fastest_response_select(self, engines: List[EngineInstance]) -> EngineInstance:
        """最快响应选择"""
        return min(engines, key=lambda e: e.average_processing_time)
    
    def _priority_select(self, engines: List[EngineInstance]) -> EngineInstance:
        """优先级选择"""
        return max(engines, key=lambda e: e.metadata.priority)

class EngineDataBus:
    """引擎数据总线"""
    
    def __init__(self, cache_manager: AdvancedCacheManager):
        self.cache_manager = cache_manager
        self.logger = logging.getLogger(__name__)
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._lock = threading.RLock()
    
    async def publish_data(self, topic: str, data: Any, ttl: int = 3600):
        """发布数据"""
        try:
            # 缓存数据
            cache_key = f"databus:{topic}"
            await self.cache_manager.set(cache_key, data, ttl=ttl)
            
            # 通知订阅者
            with self._lock:
                subscribers = self._subscribers.get(topic, [])
                for callback in subscribers:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(topic, data)
                        else:
                            callback(topic, data)
                    except Exception as e:
                        self.logger.error(f"数据总线通知订阅者失败: {e}")
            
        except Exception as e:
            self.logger.error(f"发布数据失败: {e}")
    
    async def get_data(self, topic: str) -> Optional[Any]:
        """获取数据"""
        try:
            cache_key = f"databus:{topic}"
            return await self.cache_manager.get(cache_key)
        except Exception as e:
            self.logger.error(f"获取数据失败: {e}")
            return None
    
    def subscribe(self, topic: str, callback: Callable):
        """订阅数据"""
        with self._lock:
            self._subscribers[topic].append(callback)
    
    def unsubscribe(self, topic: str, callback: Callable):
        """取消订阅"""
        with self._lock:
            if topic in self._subscribers and callback in self._subscribers[topic]:
                self._subscribers[topic].remove(callback)

class IntelligentEngineManager:
    """智能引擎管理器"""
    
    def __init__(
        self,
        config: Dict[str, Any],
        metrics_collector: Optional[MetricsCollector] = None,
        cache_manager: Optional[AdvancedCacheManager] = None
    ):
        self.config = config
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.cache_manager = cache_manager or AdvancedCacheManager(config.get("cache", {}))
        self.logger = logging.getLogger(__name__)
        
        # 核心组件
        self.registry = EngineRegistry()
        self.load_balancer = EngineLoadBalancer()
        self.data_bus = EngineDataBus(self.cache_manager)
        
        # 请求处理
        self.request_queue = asyncio.Queue(maxsize=1000)
        self.executor = ThreadPoolExecutor(max_workers=config.get("max_workers", 10))
        
        # 健康检查
        self.health_check_task: Optional[asyncio.Task] = None
        self.health_check_interval = config.get("health_check_interval", 30)
        
        # 状态管理
        self.is_running = False
        self.startup_time: Optional[datetime] = None
        
        # 性能统计
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.request_history = deque(maxlen=1000)
        
        # 注册指标
        self._register_metrics()
    
    def _register_metrics(self):
        """注册指标"""
        self.metrics_collector.register_counter(
            "engine_requests_total",
            "Total number of engine requests"
        )
        self.metrics_collector.register_counter(
            "engine_requests_failed_total",
            "Total number of failed engine requests"
        )
        self.metrics_collector.register_histogram(
            "engine_request_duration_seconds",
            "Engine request duration in seconds"
        )
        self.metrics_collector.register_gauge(
            "engine_instances_total",
            "Total number of registered engine instances"
        )
        self.metrics_collector.register_gauge(
            "engine_queue_size",
            "Current size of the engine request queue"
        )
    
    async def start(self):
        """启动引擎管理器"""
        try:
            if self.is_running:
                return
            
            self.is_running = True
            self.startup_time = datetime.now()
            
            # 启动缓存管理器
            await self.cache_manager.initialize()
            
            # 启动健康检查任务
            self.health_check_task = asyncio.create_task(self._health_check_loop())
            
            # 启动请求处理任务
            asyncio.create_task(self._process_requests())
            
            self.logger.info("智能引擎管理器启动完成")
            
        except Exception as e:
            self.logger.error(f"引擎管理器启动失败: {e}")
            raise
    
    async def stop(self):
        """停止引擎管理器"""
        try:
            self.is_running = False
            
            # 停止健康检查
            if self.health_check_task:
                self.health_check_task.cancel()
                try:
                    await self.health_check_task
                except asyncio.CancelledError:
                    pass
            
            # 关闭线程池
            self.executor.shutdown(wait=True)
            
            # 停止所有引擎
            for engine_instance in self.registry.list_all_engines():
                await self._stop_engine(engine_instance.metadata.engine_id)
            
            self.logger.info("智能引擎管理器已停止")
            
        except Exception as e:
            self.logger.error(f"引擎管理器停止失败: {e}")
    
    @trace_operation("engine_manager.register_engine", SpanKind.INTERNAL)
    async def register_engine(
        self,
        metadata: EngineMetadata,
        instance: Any,
        auto_start: bool = True
    ) -> bool:
        """注册引擎"""
        try:
            # 注册到注册表
            if not self.registry.register_engine(metadata, instance):
                self.logger.warning(f"引擎 {metadata.engine_id} 已存在")
                return False
            
            # 自动启动引擎
            if auto_start:
                await self._start_engine(metadata.engine_id)
            
            # 更新指标
            self.metrics_collector.set_gauge(
                "engine_instances_total",
                len(self.registry.list_all_engines())
            )
            
            self.logger.info(f"引擎 {metadata.engine_id} 注册成功")
            return True
            
        except Exception as e:
            self.logger.error(f"注册引擎失败: {e}")
            return False
    
    async def unregister_engine(self, engine_id: str) -> bool:
        """注销引擎"""
        try:
            # 停止引擎
            await self._stop_engine(engine_id)
            
            # 从注册表移除
            if not self.registry.unregister_engine(engine_id):
                self.logger.warning(f"引擎 {engine_id} 不存在")
                return False
            
            # 更新指标
            self.metrics_collector.set_gauge(
                "engine_instances_total",
                len(self.registry.list_all_engines())
            )
            
            self.logger.info(f"引擎 {engine_id} 注销成功")
            return True
            
        except Exception as e:
            self.logger.error(f"注销引擎失败: {e}")
            return False
    
    @trace_operation("engine_manager.execute_request", SpanKind.INTERNAL)
    async def execute_request(
        self,
        engine_type: EngineType,
        method_name: str,
        *args,
        capability: Optional[EngineCapability] = None,
        engine_id: Optional[str] = None,
        user_id: Optional[str] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> EngineResponse:
        """执行引擎请求"""
        
        request_id = f"req_{int(datetime.now().timestamp() * 1000000)}"
        start_time = datetime.now()
        
        try:
            # 选择引擎
            if engine_id:
                engine_instance = self.registry.get_engine(engine_id)
                if not engine_instance:
                    raise ValueError(f"引擎 {engine_id} 不存在")
            else:
                # 根据类型或能力选择引擎
                if capability:
                    engines = self.registry.get_engines_by_capability(capability)
                else:
                    engines = self.registry.get_engines_by_type(engine_type)
                
                engine_instance = self.load_balancer.select_engine(engines)
                if not engine_instance:
                    raise ValueError(f"没有可用的 {engine_type.value} 引擎")
            
            # 检查断路器
            if engine_instance.circuit_breaker and engine_instance.circuit_breaker.is_open():
                raise Exception("引擎断路器已打开")
            
            # 创建请求
            request = EngineRequest(
                request_id=request_id,
                engine_id=engine_instance.metadata.engine_id,
                method_name=method_name,
                args=args,
                kwargs=kwargs,
                timeout=timeout or engine_instance.metadata.timeout_seconds,
                user_id=user_id
            )
            
            # 执行请求
            result = await self._execute_engine_method(engine_instance, request)
            
            # 记录成功
            processing_time = (datetime.now() - start_time).total_seconds()
            engine_instance.request_count += 1
            engine_instance.total_processing_time += processing_time
            
            self.total_requests += 1
            self.successful_requests += 1
            
            # 记录指标
            self.metrics_collector.increment_counter("engine_requests_total")
            self.metrics_collector.record_histogram(
                "engine_request_duration_seconds",
                processing_time
            )
            
            return EngineResponse(
                request_id=request_id,
                engine_id=engine_instance.metadata.engine_id,
                success=True,
                result=result,
                processing_time=processing_time
            )
            
        except Exception as e:
            # 记录失败
            processing_time = (datetime.now() - start_time).total_seconds()
            
            if 'engine_instance' in locals():
                engine_instance.error_count += 1
                engine_instance.request_count += 1
                engine_instance.total_processing_time += processing_time
                
                # 触发断路器
                if engine_instance.circuit_breaker:
                    engine_instance.circuit_breaker.record_failure()
            
            self.total_requests += 1
            self.failed_requests += 1
            
            # 记录指标
            self.metrics_collector.increment_counter("engine_requests_failed_total")
            
            self.logger.error(f"执行引擎请求失败: {e}")
            
            return EngineResponse(
                request_id=request_id,
                engine_id=engine_instance.metadata.engine_id if 'engine_instance' in locals() else "unknown",
                success=False,
                error=str(e),
                processing_time=processing_time
            )
    
    async def _execute_engine_method(
        self,
        engine_instance: EngineInstance,
        request: EngineRequest
    ) -> Any:
        """执行引擎方法"""
        
        instance = engine_instance.instance
        method = getattr(instance, request.method_name, None)
        
        if not method:
            raise AttributeError(f"引擎 {engine_instance.metadata.engine_id} 没有方法 {request.method_name}")
        
        if not callable(method):
            raise TypeError(f"方法 {request.method_name} 不可调用")
        
        # 执行方法
        if asyncio.iscoroutinefunction(method):
            result = await asyncio.wait_for(
                method(*request.args, **request.kwargs),
                timeout=request.timeout
            )
        else:
            # 在线程池中执行同步方法
            result = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: method(*request.args, **request.kwargs)
            )
        
        # 记录成功
        if engine_instance.circuit_breaker:
            engine_instance.circuit_breaker.record_success()
        
        return result
    
    async def _start_engine(self, engine_id: str):
        """启动引擎"""
        engine_instance = self.registry.get_engine(engine_id)
        if not engine_instance:
            return
        
        try:
            self.registry.update_engine_status(engine_id, EngineStatus.INITIALIZING)
            
            # 如果引擎有初始化方法，调用它
            if hasattr(engine_instance.instance, 'initialize'):
                if asyncio.iscoroutinefunction(engine_instance.instance.initialize):
                    await engine_instance.instance.initialize()
                else:
                    engine_instance.instance.initialize()
            
            self.registry.update_engine_status(engine_id, EngineStatus.READY)
            self.logger.info(f"引擎 {engine_id} 启动成功")
            
        except Exception as e:
            self.registry.update_engine_status(engine_id, EngineStatus.ERROR)
            self.logger.error(f"启动引擎 {engine_id} 失败: {e}")
    
    async def _stop_engine(self, engine_id: str):
        """停止引擎"""
        engine_instance = self.registry.get_engine(engine_id)
        if not engine_instance:
            return
        
        try:
            self.registry.update_engine_status(engine_id, EngineStatus.STOPPED)
            
            # 如果引擎有清理方法，调用它
            if hasattr(engine_instance.instance, 'cleanup'):
                if asyncio.iscoroutinefunction(engine_instance.instance.cleanup):
                    await engine_instance.instance.cleanup()
                else:
                    engine_instance.instance.cleanup()
            
            self.logger.info(f"引擎 {engine_id} 停止成功")
            
        except Exception as e:
            self.logger.error(f"停止引擎 {engine_id} 失败: {e}")
    
    async def _health_check_loop(self):
        """健康检查循环"""
        while self.is_running:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"健康检查失败: {e}")
                await asyncio.sleep(5)
    
    async def _perform_health_checks(self):
        """执行健康检查"""
        for engine_instance in self.registry.list_all_engines():
            try:
                # 检查引擎是否有健康检查方法
                if hasattr(engine_instance.instance, 'health_check'):
                    if asyncio.iscoroutinefunction(engine_instance.instance.health_check):
                        is_healthy = await engine_instance.instance.health_check()
                    else:
                        is_healthy = engine_instance.instance.health_check()
                    
                    if is_healthy:
                        if engine_instance.status == EngineStatus.ERROR:
                            self.registry.update_engine_status(
                                engine_instance.metadata.engine_id,
                                EngineStatus.READY
                            )
                    else:
                        self.registry.update_engine_status(
                            engine_instance.metadata.engine_id,
                            EngineStatus.ERROR
                        )
                
                engine_instance.last_health_check = datetime.now()
                
            except Exception as e:
                self.logger.error(f"引擎 {engine_instance.metadata.engine_id} 健康检查失败: {e}")
                self.registry.update_engine_status(
                    engine_instance.metadata.engine_id,
                    EngineStatus.ERROR
                )
    
    async def _process_requests(self):
        """处理请求队列"""
        while self.is_running:
            try:
                # 更新队列大小指标
                self.metrics_collector.set_gauge(
                    "engine_queue_size",
                    self.request_queue.qsize()
                )
                
                await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"处理请求队列失败: {e}")
    
    async def get_engine_statistics(self) -> Dict[str, Any]:
        """获取引擎统计信息"""
        try:
            engines = self.registry.list_all_engines()
            
            stats = {
                "total_engines": len(engines),
                "engine_status_distribution": {},
                "engine_type_distribution": {},
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "failed_requests": self.failed_requests,
                "success_rate": self.successful_requests / max(self.total_requests, 1),
                "uptime_seconds": (datetime.now() - self.startup_time).total_seconds() if self.startup_time else 0,
                "engines": []
            }
            
            # 统计引擎状态分布
            status_counts = {}
            type_counts = {}
            
            for engine in engines:
                # 状态统计
                status = engine.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
                
                # 类型统计
                engine_type = engine.metadata.engine_type.value
                type_counts[engine_type] = type_counts.get(engine_type, 0) + 1
                
                # 引擎详细信息
                stats["engines"].append({
                    "engine_id": engine.metadata.engine_id,
                    "name": engine.metadata.name,
                    "type": engine_type,
                    "status": status,
                    "request_count": engine.request_count,
                    "error_count": engine.error_count,
                    "error_rate": engine.error_rate,
                    "average_processing_time": engine.average_processing_time,
                    "created_at": engine.created_at.isoformat(),
                    "last_health_check": engine.last_health_check.isoformat() if engine.last_health_check else None
                })
            
            stats["engine_status_distribution"] = status_counts
            stats["engine_type_distribution"] = type_counts
            
            return stats
            
        except Exception as e:
            self.logger.error(f"获取引擎统计失败: {e}")
            return {"error": str(e)}
    
    async def get_engine_health(self, engine_id: str) -> Dict[str, Any]:
        """获取引擎健康状态"""
        try:
            engine_instance = self.registry.get_engine(engine_id)
            if not engine_instance:
                return {"error": "引擎不存在"}
            
            return {
                "engine_id": engine_id,
                "status": engine_instance.status.value,
                "request_count": engine_instance.request_count,
                "error_count": engine_instance.error_count,
                "error_rate": engine_instance.error_rate,
                "average_processing_time": engine_instance.average_processing_time,
                "last_health_check": engine_instance.last_health_check.isoformat() if engine_instance.last_health_check else None,
                "circuit_breaker_open": engine_instance.circuit_breaker.is_open() if engine_instance.circuit_breaker else False
            }
            
        except Exception as e:
            self.logger.error(f"获取引擎健康状态失败: {e}")
            return {"error": str(e)}

def initialize_engine_manager(
    config: Dict[str, Any],
    metrics_collector: Optional[MetricsCollector] = None,
    cache_manager: Optional[AdvancedCacheManager] = None
) -> IntelligentEngineManager:
    """初始化智能引擎管理器"""
    return IntelligentEngineManager(config, metrics_collector, cache_manager)

# 全局引擎管理器实例
_engine_manager: Optional[IntelligentEngineManager] = None

def get_engine_manager() -> Optional[IntelligentEngineManager]:
    """获取全局引擎管理器实例"""
    return _engine_manager

def set_engine_manager(manager: IntelligentEngineManager):
    """设置全局引擎管理器实例"""
    global _engine_manager
    _engine_manager = manager 