#!/usr/bin/env python

"""
实时响应系统 - 高性能事件处理和快速响应机制
包含事件处理、优先级队列、负载均衡、缓存优化等功能
"""

import asyncio
import heapq
import json
import logging
import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class EventType(Enum):
    """事件类型枚举"""

    USER_INPUT = "user_input"
    SENSOR_DATA = "sensor_data"
    SYSTEM_ALERT = "system_alert"
    AI_DECISION = "ai_decision"
    ACCESSIBILITY_REQUEST = "accessibility_request"
    EMERGENCY = "emergency"
    MAINTENANCE = "maintenance"
    NOTIFICATION = "notification"


class Priority(Enum):
    """优先级枚举"""

    CRITICAL = 1  # 紧急事件，立即处理
    HIGH = 2  # 高优先级，快速处理
    NORMAL = 3  # 正常优先级
    LOW = 4  # 低优先级，可延迟处理
    BACKGROUND = 5  # 后台任务


class ResponseStatus(Enum):
    """响应状态枚举"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class Event:
    """事件数据结构"""

    event_id: str
    event_type: EventType
    priority: Priority
    data: dict[str, Any]
    timestamp: float
    source: str
    timeout: float | None = None
    retry_count: int = 0
    max_retries: int = 3
    callback: Callable | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Response:
    """响应数据结构"""

    response_id: str
    event_id: str
    status: ResponseStatus
    result: Any
    processing_time: float
    timestamp: float
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class EventQueue:
    """优先级事件队列"""

    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self._queue = []
        self._lock = threading.Lock()
        self._event_count = 0
        self._dropped_events = 0

    def put(self, event: Event) -> bool:
        """添加事件到队列"""
        with self._lock:
            if len(self._queue) >= self.max_size:
                # 队列满时，丢弃最低优先级的事件
                if self._queue and self._queue[0][0] > event.priority.value:
                    heapq.heappop(self._queue)
                    self._dropped_events += 1
                else:
                    self._dropped_events += 1
                    return False

            # 使用优先级和时间戳作为排序键
            priority_key = (event.priority.value, event.timestamp, self._event_count)
            heapq.heappush(self._queue, (priority_key, event))
            self._event_count += 1
            return True

    def get(self) -> Event | None:
        """从队列获取事件"""
        with self._lock:
            if self._queue:
                _, event = heapq.heappop(self._queue)
                return event
            return None

    def size(self) -> int:
        """获取队列大小"""
        with self._lock:
            return len(self._queue)

    def is_empty(self) -> bool:
        """检查队列是否为空"""
        with self._lock:
            return len(self._queue) == 0

    def get_stats(self) -> dict[str, Any]:
        """获取队列统计信息"""
        with self._lock:
            return {
                "current_size": len(self._queue),
                "max_size": self.max_size,
                "total_events": self._event_count,
                "dropped_events": self._dropped_events,
                "utilization": len(self._queue) / self.max_size,
            }


class EventProcessor:
    """事件处理器"""

    def __init__(self, processor_id: str, max_workers: int = 4):
        self.processor_id = processor_id
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.handlers = {}  # event_type -> handler function
        self.middleware = []  # 中间件列表
        self.stats = {
            "events_processed": 0,
            "events_failed": 0,
            "total_processing_time": 0.0,
            "average_processing_time": 0.0,
        }
        self.active_tasks = set()
        self.is_running = False

    def register_handler(self, event_type: EventType, handler: Callable):
        """注册事件处理器"""
        self.handlers[event_type] = handler
        logger.info(f"注册事件处理器: {event_type.value} -> {handler.__name__}")

    def add_middleware(self, middleware: Callable):
        """添加中间件"""
        self.middleware.append(middleware)
        logger.info(f"添加中间件: {middleware.__name__}")

    async def process_event(self, event: Event) -> Response:
        """处理单个事件"""
        start_time = time.time()
        response_id = f"resp_{event.event_id}_{int(start_time)}"

        try:
            # 应用中间件
            for middleware in self.middleware:
                event = await self._apply_middleware(middleware, event)
                if event is None:
                    return Response(
                        response_id=response_id,
                        event_id=event.event_id,
                        status=ResponseStatus.CANCELLED,
                        result=None,
                        processing_time=time.time() - start_time,
                        timestamp=time.time(),
                        error_message="Event cancelled by middleware",
                    )

            # 获取处理器
            handler = self.handlers.get(event.event_type)
            if not handler:
                raise ValueError(
                    f"No handler registered for event type: {event.event_type}"
                )

            # 检查超时
            if event.timeout and (time.time() - event.timestamp) > event.timeout:
                return Response(
                    response_id=response_id,
                    event_id=event.event_id,
                    status=ResponseStatus.TIMEOUT,
                    result=None,
                    processing_time=time.time() - start_time,
                    timestamp=time.time(),
                    error_message="Event timeout",
                )

            # 执行处理器
            if asyncio.iscoroutinefunction(handler):
                result = await handler(event)
            else:
                # 在线程池中执行同步处理器
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(self.executor, handler, event)

            processing_time = time.time() - start_time

            # 更新统计信息
            self.stats["events_processed"] += 1
            self.stats["total_processing_time"] += processing_time
            self.stats["average_processing_time"] = (
                self.stats["total_processing_time"] / self.stats["events_processed"]
            )

            # 执行回调
            if event.callback:
                try:
                    if asyncio.iscoroutinefunction(event.callback):
                        await event.callback(result)
                    else:
                        event.callback(result)
                except Exception as e:
                    logger.error(f"回调执行失败: {e!s}")

            return Response(
                response_id=response_id,
                event_id=event.event_id,
                status=ResponseStatus.COMPLETED,
                result=result,
                processing_time=processing_time,
                timestamp=time.time(),
            )

        except Exception as e:
            processing_time = time.time() - start_time
            self.stats["events_failed"] += 1

            logger.error(f"事件处理失败: {e!s}")

            return Response(
                response_id=response_id,
                event_id=event.event_id,
                status=ResponseStatus.FAILED,
                result=None,
                processing_time=processing_time,
                timestamp=time.time(),
                error_message=str(e),
            )

    async def _apply_middleware(
        self, middleware: Callable, event: Event
    ) -> Event | None:
        """应用中间件"""
        try:
            if asyncio.iscoroutinefunction(middleware):
                return await middleware(event)
            else:
                return middleware(event)
        except Exception as e:
            logger.error(f"中间件执行失败: {e!s}")
            return event

    def get_stats(self) -> dict[str, Any]:
        """获取处理器统计信息"""
        return {
            "processor_id": self.processor_id,
            "max_workers": self.max_workers,
            "active_tasks": len(self.active_tasks),
            "registered_handlers": len(self.handlers),
            "middleware_count": len(self.middleware),
            **self.stats,
        }


class LoadBalancer:
    """负载均衡器"""

    def __init__(self) -> None:
        self.processors = []
        self.current_index = 0
        self.processor_stats = defaultdict(dict)
        self.balancing_strategy = "round_robin"  # round_robin, least_loaded, weighted

    def add_processor(self, processor: EventProcessor, weight: float = 1.0):
        """添加处理器"""
        self.processors.append({"processor": processor, "weight": weight, "load": 0})
        logger.info(f"添加处理器: {processor.processor_id}")

    def remove_processor(self, processor_id: str):
        """移除处理器"""
        self.processors = [
            p for p in self.processors if p["processor"].processor_id != processor_id
        ]
        logger.info(f"移除处理器: {processor_id}")

    def select_processor(self, event: Event) -> EventProcessor | None:
        """选择处理器"""
        if not self.processors:
            return None

        if self.balancing_strategy == "round_robin":
            return self._round_robin_select()
        elif self.balancing_strategy == "least_loaded":
            return self._least_loaded_select()
        elif self.balancing_strategy == "weighted":
            return self._weighted_select()
        else:
            return self._round_robin_select()

    def _round_robin_select(self) -> EventProcessor:
        """轮询选择"""
        processor_info = self.processors[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.processors)
        return processor_info["processor"]

    def _least_loaded_select(self) -> EventProcessor:
        """最少负载选择"""
        min_load = float("inf")
        selected_processor = None

        for processor_info in self.processors:
            processor = processor_info["processor"]
            load = len(processor.active_tasks)

            if load < min_load:
                min_load = load
                selected_processor = processor

        return selected_processor

    def _weighted_select(self) -> EventProcessor:
        """加权选择"""
        total_weight = sum(p["weight"] for p in self.processors)
        if total_weight == 0:
            return self._round_robin_select()

        # 简化的加权选择：基于权重和当前负载
        best_score = float("-inf")
        selected_processor = None

        for processor_info in self.processors:
            processor = processor_info["processor"]
            weight = processor_info["weight"]
            load = len(processor.active_tasks)

            # 分数 = 权重 / (负载 + 1)
            score = weight / (load + 1)

            if score > best_score:
                best_score = score
                selected_processor = processor

        return selected_processor

    def get_stats(self) -> dict[str, Any]:
        """获取负载均衡器统计信息"""
        processor_stats = []
        for processor_info in self.processors:
            processor = processor_info["processor"]
            stats = processor.get_stats()
            stats["weight"] = processor_info["weight"]
            stats["current_load"] = len(processor.active_tasks)
            processor_stats.append(stats)

        return {
            "total_processors": len(self.processors),
            "balancing_strategy": self.balancing_strategy,
            "processors": processor_stats,
        }


class ResponseCache:
    """响应缓存"""

    def __init__(self, max_size: int = 1000, ttl: float = 300.0):
        self.max_size = max_size
        self.ttl = ttl  # 生存时间（秒）
        self.cache = {}  # key -> (response, timestamp)
        self.access_order = deque()  # LRU顺序
        self.lock = threading.Lock()
        self.stats = {"hits": 0, "misses": 0, "evictions": 0}

    def get(self, key: str) -> Response | None:
        """获取缓存响应"""
        with self.lock:
            if key in self.cache:
                response, timestamp = self.cache[key]

                # 检查是否过期
                if time.time() - timestamp > self.ttl:
                    del self.cache[key]
                    self.access_order.remove(key)
                    self.stats["misses"] += 1
                    return None

                # 更新访问顺序
                self.access_order.remove(key)
                self.access_order.append(key)
                self.stats["hits"] += 1
                return response

            self.stats["misses"] += 1
            return None

    def put(self, key: str, response: Response):
        """存储响应到缓存"""
        with self.lock:
            # 如果缓存已满，移除最久未使用的项
            if len(self.cache) >= self.max_size and key not in self.cache:
                oldest_key = self.access_order.popleft()
                del self.cache[oldest_key]
                self.stats["evictions"] += 1

            # 如果key已存在，更新访问顺序
            if key in self.cache:
                self.access_order.remove(key)

            self.cache[key] = (response, time.time())
            self.access_order.append(key)

    def invalidate(self, key: str):
        """使缓存失效"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                self.access_order.remove(key)

    def clear(self) -> None:
        """清空缓存"""
        with self.lock:
            self.cache.clear()
            self.access_order.clear()

    def get_stats(self) -> dict[str, Any]:
        """获取缓存统计信息"""
        with self.lock:
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0

            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hit_rate": hit_rate,
                "ttl": self.ttl,
                **self.stats,
            }


class RealtimeResponseSystem:
    """实时响应系统主类"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化实时响应系统

        Args:
            config: 服务配置
        """
        self.config = config
        self.enabled = config.get("realtime_response", {}).get("enabled", True)

        # 核心组件
        self.event_queue = EventQueue(
            max_size=config.get("realtime_response", {}).get("queue_size", 10000)
        )
        self.load_balancer = LoadBalancer()
        self.response_cache = ResponseCache(
            max_size=config.get("realtime_response", {}).get("cache_size", 1000),
            ttl=config.get("realtime_response", {}).get("cache_ttl", 300.0),
        )

        # 处理器池
        self.processors = {}
        self.default_processor_count = config.get("realtime_response", {}).get(
            "processor_count", 4
        )

        # 响应存储
        self.responses = {}  # event_id -> response
        self.response_history = deque(maxlen=1000)

        # 统计信息
        self.stats = {
            "events_received": 0,
            "events_processed": 0,
            "events_failed": 0,
            "average_response_time": 0.0,
            "total_response_time": 0.0,
            "system_start_time": time.time(),
        }

        # 控制标志
        self.is_running = False
        self._processing_task = None

        # 初始化默认处理器
        self._initialize_default_processors()

        logger.info(f"实时响应系统初始化完成 - 启用: {self.enabled}")

    def _initialize_default_processors(self) -> None:
        """初始化默认处理器"""
        for i in range(self.default_processor_count):
            processor = EventProcessor(f"processor_{i}")
            self.processors[processor.processor_id] = processor
            self.load_balancer.add_processor(processor)

            # 注册默认处理器
            self._register_default_handlers(processor)

    def _register_default_handlers(self, processor: EventProcessor):
        """注册默认事件处理器"""

        async def handle_user_input(event: Event) -> dict[str, Any]:
            """处理用户输入事件"""
            logger.info(f"处理用户输入: {event.data}")
            # 模拟处理时间
            await asyncio.sleep(0.01)
            return {
                "status": "processed",
                "input_type": event.data.get("type", "unknown"),
            }

        async def handle_sensor_data(event: Event) -> dict[str, Any]:
            """处理传感器数据事件"""
            logger.info(f"处理传感器数据: {event.data}")
            await asyncio.sleep(0.005)
            return {
                "status": "processed",
                "sensor_count": len(event.data.get("sensors", [])),
            }

        async def handle_system_alert(event: Event) -> dict[str, Any]:
            """处理系统警报事件"""
            logger.warning(f"处理系统警报: {event.data}")
            await asyncio.sleep(0.002)
            return {
                "status": "alert_processed",
                "severity": event.data.get("severity", "low"),
            }

        async def handle_accessibility_request(event: Event) -> dict[str, Any]:
            """处理无障碍请求事件"""
            logger.info(f"处理无障碍请求: {event.data}")
            await asyncio.sleep(0.02)
            return {
                "status": "accessibility_handled",
                "request_type": event.data.get("request_type"),
            }

        async def handle_emergency(event: Event) -> dict[str, Any]:
            """处理紧急事件"""
            logger.critical(f"处理紧急事件: {event.data}")
            await asyncio.sleep(0.001)  # 紧急事件快速处理
            return {"status": "emergency_handled", "action_taken": "immediate_response"}

        # 注册处理器
        processor.register_handler(EventType.USER_INPUT, handle_user_input)
        processor.register_handler(EventType.SENSOR_DATA, handle_sensor_data)
        processor.register_handler(EventType.SYSTEM_ALERT, handle_system_alert)
        processor.register_handler(
            EventType.ACCESSIBILITY_REQUEST, handle_accessibility_request
        )
        processor.register_handler(EventType.EMERGENCY, handle_emergency)

    async def submit_event(self, event: Event) -> str:
        """提交事件到系统"""
        if not self.enabled:
            return ""

        # 生成事件ID
        if not event.event_id:
            event.event_id = f"event_{int(time.time())}_{self.stats['events_received']}"

        # 检查缓存
        cache_key = self._generate_cache_key(event)
        cached_response = self.response_cache.get(cache_key)
        if cached_response:
            logger.info(f"从缓存返回响应: {event.event_id}")
            self.responses[event.event_id] = cached_response
            return event.event_id

        # 添加到队列
        if self.event_queue.put(event):
            self.stats["events_received"] += 1
            logger.info(
                f"事件已提交: {event.event_id} (优先级: {event.priority.value})"
            )
            return event.event_id
        else:
            logger.warning(f"事件队列已满，丢弃事件: {event.event_id}")
            return ""

    def _generate_cache_key(self, event: Event) -> str:
        """生成缓存键"""
        # 基于事件类型和数据生成缓存键
        data_hash = hash(json.dumps(event.data, sort_keys=True))
        return f"{event.event_type.value}_{data_hash}"

    async def get_response(
        self, event_id: str, timeout: float = 30.0
    ) -> Response | None:
        """获取事件响应"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            if event_id in self.responses:
                return self.responses[event_id]
            await asyncio.sleep(0.01)  # 10ms轮询间隔

        return None  # 超时

    async def start(self) -> None:
        """启动实时响应系统"""
        if not self.enabled or self.is_running:
            return

        logger.info("启动实时响应系统...")

        self.is_running = True
        self._processing_task = asyncio.create_task(self._processing_loop())

        logger.info("实时响应系统已启动")

    async def _processing_loop(self) -> None:
        """事件处理循环"""
        while self.is_running:
            try:
                # 从队列获取事件
                event = self.event_queue.get()

                if event is None:
                    await asyncio.sleep(0.001)  # 1ms等待
                    continue

                # 选择处理器
                processor = self.load_balancer.select_processor(event)
                if processor is None:
                    logger.error("没有可用的处理器")
                    continue

                # 创建处理任务
                task = asyncio.create_task(
                    self._process_event_with_processor(event, processor)
                )
                processor.active_tasks.add(task)

                # 清理完成的任务
                self._cleanup_completed_tasks()

            except Exception as e:
                logger.error(f"处理循环错误: {e!s}")
                await asyncio.sleep(0.1)

    async def _process_event_with_processor(
        self, event: Event, processor: EventProcessor
    ):
        """使用指定处理器处理事件"""
        try:
            start_time = time.time()

            # 处理事件
            response = await processor.process_event(event)

            # 更新统计信息
            processing_time = time.time() - start_time
            self.stats["events_processed"] += 1
            self.stats["total_response_time"] += processing_time
            self.stats["average_response_time"] = (
                self.stats["total_response_time"] / self.stats["events_processed"]
            )

            if response.status == ResponseStatus.FAILED:
                self.stats["events_failed"] += 1

            # 存储响应
            self.responses[event.event_id] = response
            self.response_history.append(response)

            # 缓存响应（如果成功）
            if response.status == ResponseStatus.COMPLETED:
                cache_key = self._generate_cache_key(event)
                self.response_cache.put(cache_key, response)

            logger.debug(
                f"事件处理完成: {event.event_id} (耗时: {processing_time:.3f}s)"
            )

        except Exception as e:
            logger.error(f"事件处理异常: {e!s}")
            self.stats["events_failed"] += 1
        finally:
            # 从活跃任务中移除
            processor.active_tasks.discard(asyncio.current_task())

    def _cleanup_completed_tasks(self) -> None:
        """清理已完成的任务"""
        for processor in self.processors.values():
            completed_tasks = [task for task in processor.active_tasks if task.done()]
            for task in completed_tasks:
                processor.active_tasks.remove(task)

    def register_custom_handler(
        self,
        event_type: EventType,
        handler: Callable,
        processor_id: str | None = None,
    ):
        """注册自定义事件处理器"""
        if processor_id:
            if processor_id in self.processors:
                self.processors[processor_id].register_handler(event_type, handler)
            else:
                logger.error(f"处理器不存在: {processor_id}")
        else:
            # 注册到所有处理器
            for processor in self.processors.values():
                processor.register_handler(event_type, handler)

    def add_middleware(self, middleware: Callable, processor_id: str | None = None):
        """添加中间件"""
        if processor_id:
            if processor_id in self.processors:
                self.processors[processor_id].add_middleware(middleware)
            else:
                logger.error(f"处理器不存在: {processor_id}")
        else:
            # 添加到所有处理器
            for processor in self.processors.values():
                processor.add_middleware(middleware)

    def get_system_stats(self) -> dict[str, Any]:
        """获取系统统计信息"""
        current_time = time.time()
        uptime = current_time - self.stats["system_start_time"]

        return {
            "enabled": self.enabled,
            "is_running": self.is_running,
            "uptime_seconds": uptime,
            "queue_stats": self.event_queue.get_stats(),
            "load_balancer_stats": self.load_balancer.get_stats(),
            "cache_stats": self.response_cache.get_stats(),
            "response_count": len(self.responses),
            "response_history_size": len(self.response_history),
            **self.stats,
        }

    def get_performance_metrics(self) -> dict[str, Any]:
        """获取性能指标"""
        # 计算最近响应时间
        recent_responses = list(self.response_history)[-100:]  # 最近100个响应
        recent_times = [
            r.processing_time
            for r in recent_responses
            if r.status == ResponseStatus.COMPLETED
        ]

        metrics = {
            "total_events": self.stats["events_received"],
            "processed_events": self.stats["events_processed"],
            "failed_events": self.stats["events_failed"],
            "success_rate": (
                self.stats["events_processed"] - self.stats["events_failed"]
            )
            / max(1, self.stats["events_processed"]),
            "average_response_time": self.stats["average_response_time"],
            "queue_utilization": self.event_queue.get_stats()["utilization"],
            "cache_hit_rate": self.response_cache.get_stats()["hit_rate"],
        }

        if recent_times:
            metrics.update(
                {
                    "recent_avg_response_time": sum(recent_times) / len(recent_times),
                    "recent_min_response_time": min(recent_times),
                    "recent_max_response_time": max(recent_times),
                }
            )

        return metrics

    async def shutdown(self) -> None:
        """关闭实时响应系统"""
        logger.info("正在关闭实时响应系统...")

        self.is_running = False

        # 等待处理任务完成
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass

        # 关闭所有处理器的线程池
        for processor in self.processors.values():
            processor.executor.shutdown(wait=True)

        logger.info("实时响应系统已关闭")


# 便捷函数
async def create_event(
    event_type: EventType,
    data: dict[str, Any],
    priority: Priority = Priority.NORMAL,
    source: str = "unknown",
    timeout: float | None = None,
    callback: Callable | None = None,
) -> Event:
    """创建事件的便捷函数"""
    return Event(
        event_id="",
        event_type=event_type,
        priority=priority,
        data=data,
        timestamp=time.time(),
        source=source,
        timeout=timeout,
        callback=callback,
    )


# 中间件示例
async def logging_middleware(event: Event) -> Event:
    """日志中间件"""
    logger.info(f"处理事件: {event.event_type.value} from {event.source}")
    return event


async def rate_limiting_middleware(event: Event) -> Event | None:
    """限流中间件"""
    # 简化的限流逻辑
    if hasattr(rate_limiting_middleware, "last_request_time"):
        time_diff = time.time() - rate_limiting_middleware.last_request_time
        if time_diff < 0.001:  # 1ms限流
            logger.warning(f"限流丢弃事件: {event.event_id}")
            return None

    rate_limiting_middleware.last_request_time = time.time()
    return event


async def authentication_middleware(event: Event) -> Event | None:
    """认证中间件"""
    # 检查事件是否包含认证信息
    if event.event_type in [EventType.EMERGENCY, EventType.SYSTEM_ALERT]:
        return event  # 紧急事件跳过认证

    auth_token = event.metadata.get("auth_token")
    if not auth_token:
        logger.warning(f"事件缺少认证信息: {event.event_id}")
        return None

    # 简化的认证逻辑
    if auth_token != "valid_token":
        logger.warning(f"事件认证失败: {event.event_id}")
        return None

    return event
