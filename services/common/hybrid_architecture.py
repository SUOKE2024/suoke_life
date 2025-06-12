"""
hybrid_architecture - 索克生活项目模块
"""

import asyncio
import json
import logging
import multiprocessing
import threading
import time
import uuid
from collections import defaultdict, deque
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import aioredis
import psutil

#! / usr / bin / env python3
"""
索克生活 - 混合架构设计
实现同步 / 异步、本地 / 分布式混合处理架构
"""


# 配置日志
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

class ProcessingMode(Enum):
    """处理模式"""
    SYNC_LOCAL = "sync_local"           # 同步本地处理
    ASYNC_LOCAL = "async_local"         # 异步本地处理
    SYNC_DISTRIBUTED = "sync_distributed"   # 同步分布式处理
    ASYNC_DISTRIBUTED = "async_distributed" # 异步分布式处理
    HYBRID = "hybrid"                   # 混合模式

class TaskType(Enum):
    """任务类型"""
    CPU_INTENSIVE = "cpu_intensive"     # CPU密集型
    IO_INTENSIVE = "io_intensive"       # I / O密集型
    MEMORY_INTENSIVE = "memory_intensive" # 内存密集型
    NETWORK_INTENSIVE = "network_intensive" # 网络密集型
    MIXED = "mixed"                     # 混合型

class Priority(Enum):
    """优先级"""
    URGENT = 1      # 紧急
    HIGH = 2        # 高
    NORMAL = 3      # 普通
    LOW = 4         # 低

@dataclass
class HybridTask:
    """混合架构任务"""
    task_id: str
    task_type: TaskType
    processing_mode: ProcessingMode
    priority: Priority
    input_data: Dict[str, Any]
    timeout: float = 30.0
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    memory_usage: Optional[float] = None
    worker_id: Optional[str] = None

    def __post_init__(self) -> None:
        """TODO: 添加文档字符串"""
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class WorkerNode:
    """工作节点信息"""
    node_id: str
    endpoint: str
    capabilities: List[TaskType]
    current_load: int = 0
    max_capacity: int = 10
    avg_response_time: float = 0.0
    success_rate: float = 1.0
    last_heartbeat: datetime = None
    status: str = "active"

    def __post_init__(self) -> None:
        """TODO: 添加文档字符串"""
        if self.last_heartbeat is None:
            self.last_heartbeat = datetime.now()

class LocalProcessor:
    """本地处理器"""

    def __init__(self, max_workers: Optional[int] = None):
        """TODO: 添加文档字符串"""
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.thread_pool = ThreadPoolExecutor(max_workers = self.max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers = self.max_workers)
        self.active_tasks: Dict[str, HybridTask] = {}
        self.lock = threading.Lock()

        # 性能统计
        self.stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'avg_execution_time': 0.0,
            'peak_memory_usage': 0.0
        }

        logger.info(f"本地处理器初始化，最大工作线程: {self.max_workers}")

    async def process_task_async(self, task: HybridTask) -> Dict[str, Any]:
        """异步处理任务"""
        start_time = time.time()
        task.started_at = datetime.now()

        try:
            with self.lock:
                self.active_tasks[task.task_id] = task
                self.stats['total_tasks']+=1

            # 根据任务类型选择处理方式
            if task.task_type==TaskType.IO_INTENSIVE:
                result = await self._process_io_intensive_async(task)
            elif task.task_type==TaskType.CPU_INTENSIVE:
                result = await self._process_cpu_intensive_async(task)
            elif task.task_type==TaskType.MEMORY_INTENSIVE:
                result = await self._process_memory_intensive_async(task)
            else:
                result = await self._process_mixed_async(task)

            # 更新任务状态
            task.completed_at = datetime.now()
            task.execution_time = time.time() - start_time
            task.result = result

            with self.lock:
                self.stats['completed_tasks']+=1
                self._update_avg_execution_time(task.execution_time)

            logger.info(f"任务完成: {task.task_id}, 耗时: {task.execution_time:.2f}s")
            return result

        except Exception as e:
            task.error_message = str(e)
            with self.lock:
                self.stats['failed_tasks']+=1
            logger.error(f"任务失败: {task.task_id}, 错误: {e}")
            raise
        finally:
            with self.lock:
                self.active_tasks.pop(task.task_id, None)

    def process_task_sync(self, task: HybridTask) -> Dict[str, Any]:
        """同步处理任务"""
        start_time = time.time()
        task.started_at = datetime.now()

        try:
            with self.lock:
                self.active_tasks[task.task_id] = task
                self.stats['total_tasks']+=1

            # 根据任务类型选择处理方式
            if task.task_type==TaskType.IO_INTENSIVE:
                result = self._process_io_intensive_sync(task)
            elif task.task_type==TaskType.CPU_INTENSIVE:
                result = self._process_cpu_intensive_sync(task)
            elif task.task_type==TaskType.MEMORY_INTENSIVE:
                result = self._process_memory_intensive_sync(task)
            else:
                result = self._process_mixed_sync(task)

            # 更新任务状态
            task.completed_at = datetime.now()
            task.execution_time = time.time() - start_time
            task.result = result

            with self.lock:
                self.stats['completed_tasks']+=1
                self._update_avg_execution_time(task.execution_time)

            logger.info(f"任务完成: {task.task_id}, 耗时: {task.execution_time:.2f}s")
            return result

        except Exception as e:
            task.error_message = str(e)
            with self.lock:
                self.stats['failed_tasks']+=1
            logger.error(f"任务失败: {task.task_id}, 错误: {e}")
            raise
        finally:
            with self.lock:
                self.active_tasks.pop(task.task_id, None)

    async def _process_io_intensive_async(self, task: HybridTask) -> Dict[str, Any]:
        """异步处理I / O密集型任务"""
        loop = asyncio.get_event_loop()

        def io_work() -> None:
            """TODO: 添加文档字符串"""
            # 模拟I / O操作
            time.sleep(0.1)  # 模拟文件读写或网络请求
            return {
                'task_id': task.task_id,
                'type': 'io_intensive',
                'data_processed': len(str(task.input_data)),
                'timestamp': datetime.now().isoformat()
            }

        result = await loop.run_in_executor(self.thread_pool, io_work)
        return result

    def _process_io_intensive_sync(self, task: HybridTask) -> Dict[str, Any]:
        """同步处理I / O密集型任务"""
        # 模拟I / O操作
        time.sleep(0.1)
        return {
            'task_id': task.task_id,
            'type': 'io_intensive',
            'data_processed': len(str(task.input_data)),
            'timestamp': datetime.now().isoformat()
        }

    async def _process_cpu_intensive_async(self, task: HybridTask) -> Dict[str, Any]:
        """异步处理CPU密集型任务"""
        loop = asyncio.get_event_loop()

        def cpu_work() -> None:
            """TODO: 添加文档字符串"""
            # 模拟CPU密集型计算
            data = np.random.rand(1000, 1000)
            result_matrix = np.dot(data, data.T)
            return {
                'task_id': task.task_id,
                'type': 'cpu_intensive',
                'matrix_size': result_matrix.shape,
                'computation_result': float(np.sum(result_matrix)),
                'timestamp': datetime.now().isoformat()
            }

        result = await loop.run_in_executor(self.process_pool, cpu_work)
        return result

    def _process_cpu_intensive_sync(self, task: HybridTask) -> Dict[str, Any]:
        """同步处理CPU密集型任务"""
        # 模拟CPU密集型计算
        data = np.random.rand(1000, 1000)
        result_matrix = np.dot(data, data.T)
        return {
            'task_id': task.task_id,
            'type': 'cpu_intensive',
            'matrix_size': result_matrix.shape,
            'computation_result': float(np.sum(result_matrix)),
            'timestamp': datetime.now().isoformat()
        }

    async def _process_memory_intensive_async(self, task: HybridTask) -> Dict[str, Any]:
        """异步处理内存密集型任务"""
        loop = asyncio.get_event_loop()

        def memory_work() -> None:
            """TODO: 添加文档字符串"""
            # 模拟内存密集型操作
            large_data = [np.random.rand(100, 100) for _ in range(100)]
            processed_data = [np.mean(arr) for arr in large_data]
            return {
                'task_id': task.task_id,
                'type': 'memory_intensive',
                'arrays_processed': len(large_data),
                'average_values': processed_data[:10],  # 只返回前10个
                'timestamp': datetime.now().isoformat()
            }

        result = await loop.run_in_executor(self.thread_pool, memory_work)
        return result

    def _process_memory_intensive_sync(self, task: HybridTask) -> Dict[str, Any]:
        """同步处理内存密集型任务"""
        # 模拟内存密集型操作
        large_data = [np.random.rand(100, 100) for _ in range(100)]
        processed_data = [np.mean(arr) for arr in large_data]
        return {
            'task_id': task.task_id,
            'type': 'memory_intensive',
            'arrays_processed': len(large_data),
            'average_values': processed_data[:10],
            'timestamp': datetime.now().isoformat()
        }

    async def _process_mixed_async(self, task: HybridTask) -> Dict[str, Any]:
        """异步处理混合型任务"""
        # 组合多种处理方式
        io_result = await self._process_io_intensive_async(task)
        cpu_result = await self._process_cpu_intensive_async(task)

        return {
            'task_id': task.task_id,
            'type': 'mixed',
            'io_result': io_result,
            'cpu_result': cpu_result,
            'timestamp': datetime.now().isoformat()
        }

    def _process_mixed_sync(self, task: HybridTask) -> Dict[str, Any]:
        """同步处理混合型任务"""
        # 组合多种处理方式
        io_result = self._process_io_intensive_sync(task)
        cpu_result = self._process_cpu_intensive_sync(task)

        return {
            'task_id': task.task_id,
            'type': 'mixed',
            'io_result': io_result,
            'cpu_result': cpu_result,
            'timestamp': datetime.now().isoformat()
        }

    def _update_avg_execution_time(self, execution_time: float):
        """更新平均执行时间"""
        if self.stats['avg_execution_time']==0:
            self.stats['avg_execution_time'] = execution_time
        else:
            self.stats['avg_execution_time'] = (
                self.stats['avg_execution_time'] * 0.8 + execution_time * 0.2
            )

    def get_stats(self) -> Dict[str, Any]:
        """获取处理器统计信息"""
        with self.lock:
            return {
               ***self.stats,
                'active_tasks': len(self.active_tasks),
                'thread_pool_size': self.thread_pool._max_workers,
                'process_pool_size': self.process_pool._max_workers
            }

    def shutdown(self) -> None:
        """关闭处理器"""
        self.thread_pool.shutdown(wait = True)
        self.process_pool.shutdown(wait = True)
        logger.info("本地处理器已关闭")

class DistributedProcessor:
    """分布式处理器"""

    def __init__(self, redis_url: Optional[str] = None):
        """TODO: 添加文档字符串"""
        self.redis_url = redis_url or "redis: / /localhost:6379"
        self.redis_client: Optional[aioredis.Redis] = None
        self.worker_nodes: Dict[str, WorkerNode] = {}
        self.task_queue = "hybrid_task_queue"
        self.result_queue = "hybrid_result_queue"
        self.lock = threading.Lock()

        # 统计信息
        self.stats = {
            'total_distributed_tasks': 0,
            'completed_distributed_tasks': 0,
            'failed_distributed_tasks': 0,
            'avg_network_latency': 0.0
        }

        logger.info("分布式处理器初始化")

    async def initialize(self) -> None:
        """初始化Redis连接"""
        try:
            self.redis_client = aioredis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("Redis连接成功")
        except Exception as e:
            logger.warning(f"Redis连接失败: {e}")
            self.redis_client = None

    def register_worker_node(self, node: WorkerNode):
        """注册工作节点"""
        with self.lock:
            self.worker_nodes[node.node_id] = node
            logger.info(f"工作节点已注册: {node.node_id}")

    def unregister_worker_node(self, node_id: str):
        """注销工作节点"""
        with self.lock:
            if node_id in self.worker_nodes:
                del self.worker_nodes[node_id]
                logger.info(f"工作节点已注销: {node_id}")

    async def process_task_distributed(self, task: HybridTask) -> Dict[str, Any]:
        """分布式处理任务"""
        if not self.redis_client:
            raise RuntimeError("Redis未连接，无法进行分布式处理")

        start_time = time.time()

        try:
            with self.lock:
                self.stats['total_distributed_tasks']+=1

            # 选择最佳工作节点
            worker_node = self._select_best_worker(task.task_type)
            if not worker_node:
                raise RuntimeError("没有可用的工作节点")

            task.worker_id = worker_node.node_id

            # 将任务发送到队列
            task_data = {
                'task': asdict(task),
                'worker_id': worker_node.node_id,
                'timestamp': datetime.now().isoformat()
            }

            await self.redis_client.lpush(
                self.task_queue,
                json.dumps(task_data, default = str)
            )

            # 等待结果
            result = await self._wait_for_result(task.task_id, task.timeout)

            # 更新统计
            network_latency = time.time() - start_time
            self._update_network_latency(network_latency)

            with self.lock:
                self.stats['completed_distributed_tasks']+=1

            return result

        except Exception as e:
            with self.lock:
                self.stats['failed_distributed_tasks']+=1
            logger.error(f"分布式任务失败: {task.task_id}, 错误: {e}")
            raise

    def _select_best_worker(self, task_type: TaskType) -> Optional[WorkerNode]:
        """选择最佳工作节点"""
        with self.lock:
            available_workers = [
                worker for worker in self.worker_nodes.values()
                if (task_type in worker.capabilities and
                    worker.status=="active" and
                    worker.current_load < worker.max_capacity)
            ]

            if not available_workers:
                return None

            # 选择负载最低的节点
            best_worker = min(available_workers,
                            key = lambda w: (w.current_load / w.max_capacity,
                                        w.avg_response_time))

            best_worker.current_load+=1
            return best_worker

    async def _wait_for_result(self, task_id: str, timeout: float) -> Dict[str, Any]:
        """等待任务结果"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            # 从结果队列中查找结果
            result_data = await self.redis_client.brpop(
                self.result_queue, timeout = 1
            )

            if result_data:
                try:
                    result = json.loads(result_data[1])
                    if result.get('task_id')==task_id:
                        return result
                    else:
                        # 不是我们要的结果，放回队列
                        await self.redis_client.lpush(
                            self.result_queue,
                            result_data[1]
                        )
                except json.JSONDecodeError:
                    continue

            await asyncio.sleep(0.1)

        raise TimeoutError(f"任务超时: {task_id}")

    def _update_network_latency(self, latency: float):
        """更新网络延迟"""
        if self.stats['avg_network_latency']==0:
            self.stats['avg_network_latency'] = latency
        else:
            self.stats['avg_network_latency'] = (
                self.stats['avg_network_latency'] * 0.8 + latency * 0.2
            )

    def get_stats(self) -> Dict[str, Any]:
        """获取分布式处理器统计信息"""
        with self.lock:
            return {
               ***self.stats,
                'worker_nodes': len(self.worker_nodes),
                'active_workers': len([w for w in self.worker_nodes.values()
                                    if w.status=="active"])
            }

class TaskRouter:
    """任务路由器"""

    def __init__(self) -> None:
        """TODO: 添加文档字符串"""
        self.routing_rules: Dict[TaskType, ProcessingMode] = {
            TaskType.CPU_INTENSIVE: ProcessingMode.SYNC_LOCAL,
            TaskType.IO_INTENSIVE: ProcessingMode.ASYNC_LOCAL,
            TaskType.MEMORY_INTENSIVE: ProcessingMode.SYNC_LOCAL,
            TaskType.NETWORK_INTENSIVE: ProcessingMode.ASYNC_DISTRIBUTED,
            TaskType.MIXED: ProcessingMode.HYBRID
        }

        self.load_thresholds = {
            'cpu_threshold': 80.0,      # CPU使用率阈值
            'memory_threshold': 80.0,   # 内存使用率阈值
            'network_threshold': 70.0   # 网络使用率阈值
        }

        logger.info("任务路由器初始化")

    def route_task(self, task: HybridTask) -> ProcessingMode:
        """路由任务到合适的处理模式"""
        # 获取系统负载
        cpu_percent = psutil.cpu_percent(interval = 0.1)
        memory_percent = psutil.virtual_memory().percent

        # 基于系统负载调整路由策略
        if cpu_percent > self.load_thresholds['cpu_threshold']:
            if task.task_type==TaskType.CPU_INTENSIVE:
                return ProcessingMode.ASYNC_DISTRIBUTED

        if memory_percent > self.load_thresholds['memory_threshold']:
            if task.task_type==TaskType.MEMORY_INTENSIVE:
                return ProcessingMode.ASYNC_DISTRIBUTED

        # 基于优先级调整
        if task.priority==Priority.URGENT:
            return ProcessingMode.SYNC_LOCAL

        # 返回默认路由
        return self.routing_rules.get(task.task_type, ProcessingMode.ASYNC_LOCAL)

    def update_routing_rules(self, new_rules: Dict[TaskType, ProcessingMode]):
        """更新路由规则"""
        self.routing_rules.update(new_rules)
        logger.info("路由规则已更新")

    def get_routing_stats(self) -> Dict[str, Any]:
        """获取路由统计信息"""
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent

        return {
            'routing_rules': {k.value: v.value for k, v in self.routing_rules.items()},
            'load_thresholds': self.load_thresholds,
            'current_load': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent
            }
        }

class PerformanceMonitor:
    """性能监控器"""

    def __init__(self, monitoring_interval: float = 5.0):
        """TODO: 添加文档字符串"""
        self.monitoring_interval = monitoring_interval
        self.metrics_history: deque = deque(maxlen = 1000)
        self.is_monitoring = False
        self.monitor_task: Optional[asyncio.Task] = None

        logger.info("性能监控器初始化")

    async def start_monitoring(self) -> None:
        """开始监控"""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.monitor_task = asyncio.create_task(self._monitoring_loop())
        logger.info("性能监控已启动")

    async def stop_monitoring(self) -> None:
        """停止监控"""
        if not self.is_monitoring:
            return

        self.is_monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass

        logger.info("性能监控已停止")

    async def _monitoring_loop(self) -> None:
        """监控循环"""
        while self.is_monitoring:
            try:
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)
                await asyncio.sleep(self.monitoring_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"监控错误: {e}")
                await asyncio.sleep(1)

    def _collect_metrics(self) -> Dict[str, Any]:
        """收集系统指标"""
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage(' / ')

        return {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_gb': memory.available / (1024***3),
            'disk_percent': disk.percent,
            'disk_free_gb': disk.free / (1024***3)
        }

    def get_current_metrics(self) -> Dict[str, Any]:
        """获取当前指标"""
        return self._collect_metrics()

    def get_metrics_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取指标历史"""
        return list(self.metrics_history)[ - limit:]

    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        if not self.metrics_history:
            return {}

        recent_metrics = list(self.metrics_history)[ - 10:]  # 最近10个数据点

        avg_cpu = np.mean([m['cpu_percent'] for m in recent_metrics])
        avg_memory = np.mean([m['memory_percent'] for m in recent_metrics])

        return {
            'avg_cpu_percent': avg_cpu,
            'avg_memory_percent': avg_memory,
            'metrics_count': len(self.metrics_history),
            'monitoring_duration_minutes': len(self.metrics_history) * self.monitoring_interval / 60
        }

class HybridArchitecture:
    """混合架构主类"""

    def __init__(self, redis_url: Optional[str] = None,
                max_local_workers: Optional[int] = None,
                max_memory_gb: float = 4.0):
        self.local_processor = LocalProcessor(max_local_workers)
        self.distributed_processor = DistributedProcessor(redis_url)
        self.task_router = TaskRouter()
        self.performance_monitor = PerformanceMonitor()

        self.active_tasks: Dict[str, HybridTask] = {}
        self.lock = threading.Lock()

        # 架构统计
        self.stats = {
            'total_tasks': 0,
            'local_tasks': 0,
            'distributed_tasks': 0,
            'hybrid_tasks': 0,
            'avg_task_time': 0.0
        }

        logger.info("混合架构初始化完成")

    async def initialize(self) -> None:
        """初始化架构"""
        await self.distributed_processor.initialize()
        await self.performance_monitor.start_monitoring()
        logger.info("混合架构初始化完成")

    async def submit_task(self, task_type: TaskType, input_data: Dict[str, Any],
                        priority: Priority = Priority.NORMAL,
                        timeout: float = 30.0,
                        preferred_mode: Optional[ProcessingMode] = None) -> str:
        """提交任务"""
        task_id = str(uuid.uuid4())

        # 确定处理模式
        if preferred_mode:
            processing_mode = preferred_mode
        else:
            processing_mode = self.task_router.route_task(
                HybridTask(task_id, task_type, ProcessingMode.HYBRID, priority, input_data)
            )

        # 创建任务
        task = HybridTask(
            task_id = task_id,
            task_type = task_type,
            processing_mode = processing_mode,
            priority = priority,
            input_data = input_data,
            timeout = timeout
        )

        with self.lock:
            self.active_tasks[task_id] = task
            self.stats['total_tasks']+=1

        # 异步处理任务
        asyncio.create_task(self._process_task(task))

        logger.info(f"任务已提交: {task_id}, 模式: {processing_mode.value}")
        return task_id

    async def _process_task(self, task: HybridTask):
        """处理任务"""
        try:
            if task.processing_mode==ProcessingMode.SYNC_LOCAL:
                result = self.local_processor.process_task_sync(task)
                with self.lock:
                    self.stats['local_tasks']+=1

            elif task.processing_mode==ProcessingMode.ASYNC_LOCAL:
                result = await self.local_processor.process_task_async(task)
                with self.lock:
                    self.stats['local_tasks']+=1

            elif task.processing_mode in [ProcessingMode.SYNC_DISTRIBUTED,
                                        ProcessingMode.ASYNC_DISTRIBUTED]:
                result = await self.distributed_processor.process_task_distributed(task)
                with self.lock:
                    self.stats['distributed_tasks']+=1

            elif task.processing_mode==ProcessingMode.HYBRID:
                # 混合模式：根据系统负载动态选择
                cpu_percent = psutil.cpu_percent()
                if cpu_percent > 80:
                    result = await self.distributed_processor.process_task_distributed(task)
                    with self.lock:
                        self.stats['distributed_tasks']+=1
                else:
                    result = await self.local_processor.process_task_async(task)
                    with self.lock:
                        self.stats['local_tasks']+=1

                with self.lock:
                    self.stats['hybrid_tasks']+=1

            # 更新平均任务时间
            if task.execution_time:
                self._update_avg_task_time(task.execution_time)

        except Exception as e:
            logger.error(f"任务处理失败: {task.task_id}, 错误: {e}")
        finally:
            with self.lock:
                self.active_tasks.pop(task.task_id, None)

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        with self.lock:
            task = self.active_tasks.get(task_id)
            if task:
                return asdict(task)
        return None

    def _update_avg_task_time(self, execution_time: float):
        """更新平均任务时间"""
        if self.stats['avg_task_time']==0:
            self.stats['avg_task_time'] = execution_time
        else:
            self.stats['avg_task_time'] = (
                self.stats['avg_task_time'] * 0.8 + execution_time * 0.2
            )

    def get_architecture_stats(self) -> Dict[str, Any]:
        """获取架构统计信息"""
        with self.lock:
            return {
                'architecture_stats': self.stats.copy(),
                'local_processor_stats': self.local_processor.get_stats(),
                'distributed_processor_stats': self.distributed_processor.get_stats(),
                'routing_stats': self.task_router.get_routing_stats(),
                'performance_summary': self.performance_monitor.get_performance_summary(),
                'active_tasks': len(self.active_tasks)
            }

    async def shutdown(self) -> None:
        """关闭架构"""
        await self.performance_monitor.stop_monitoring()
        self.local_processor.shutdown()
        logger.info("混合架构已关闭")

# 全局实例
_hybrid_architecture: Optional[HybridArchitecture] = None

async def initialize_hybrid_architecture(redis_url: Optional[str] = None,
                                    max_local_workers: Optional[int] = None,
                                    max_memory_gb: float = 4.0) -> HybridArchitecture:
    """初始化混合架构"""
    global _hybrid_architecture

    if _hybrid_architecture is None:
        _hybrid_architecture = HybridArchitecture(
            redis_url = redis_url,
            max_local_workers = max_local_workers,
            max_memory_gb = max_memory_gb
        )
        await _hybrid_architecture.initialize()

    return _hybrid_architecture

async def get_hybrid_architecture() -> Optional[HybridArchitecture]:
    """获取混合架构实例"""
    return _hybrid_architecture

async def shutdown_hybrid_architecture() -> None:
    """关闭混合架构"""
    global _hybrid_architecture

    if _hybrid_architecture:
        await _hybrid_architecture.shutdown()
        _hybrid_architecture = None