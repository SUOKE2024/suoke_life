"""
intelligent_task_scheduler - 索克生活项目模块
"""

import asyncio
import heapq
import json
import logging
import threading
import time
import uuid
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

import aioredis
import psutil
from numba import jit

#! / usr / bin / env python3
"""
索克生活 - 智能任务调度器
实现智能任务分配、负载均衡和优先级管理
"""


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """任务优先级"""

    CRITICAL = 1  # 紧急任务
    HIGH = 2  # 高优先级
    NORMAL = 3  # 普通优先级
    LOW = 4  # 低优先级
    BACKGROUND = 5  # 后台任务


class TaskStatus(Enum):
    """任务状态"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class AgentType(Enum):
    """智能体类型"""

    XIAOAI = "xiaoai"  # AI推理专家
    XIAOKE = "xiaoke"  # 健康监测专家
    LAOKE = "laoke"  # 中医养生专家
    SOER = "soer"  # 生活服务专家


@dataclass
class Task:
    """任务数据结构"""

    task_id: str
    task_type: str
    priority: TaskPriority
    agent_type: AgentType
    input_data: Dict[str, Any]
    user_id: Optional[str] = None
    timeout: float = 30.0
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    memory_usage: Optional[float] = None

    def __post_init__(self) -> None:
        """TODO: 添加文档字符串"""
        if self.created_at is None:
            self.created_at = datetime.now()

    def __lt__(self, other):
        """优先级比较（用于优先队列）"""
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        return self.created_at < other.created_at


@dataclass
class AgentInfo:
    """智能体信息"""

    agent_id: str
    agent_type: AgentType
    endpoint: str
    status: str = "active"
    current_load: int = 0
    max_capacity: int = 10
    avg_response_time: float = 0.0
    success_rate: float = 1.0
    last_heartbeat: datetime = None
    capabilities: List[str] = None

    def __post_init__(self) -> None:
        """TODO: 添加文档字符串"""
        if self.last_heartbeat is None:
            self.last_heartbeat = datetime.now()
        if self.capabilities is None:
            self.capabilities = []


class LoadBalancer:
    """负载均衡器"""

    def __init__(self) -> None:
        """TODO: 添加文档字符串"""
        self.agents: Dict[str, AgentInfo] = {}
        self.agent_metrics: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.lock = threading.Lock()

    def register_agent(self, agent_info: AgentInfo):
        """注册智能体"""
        with self.lock:
            self.agents[agent_info.agent_id] = agent_info
            logger.info(
                f"智能体已注册: {agent_info.agent_id} ({agent_info.agent_type.value})"
            )

    def unregister_agent(self, agent_id: str):
        """注销智能体"""
        with self.lock:
            if agent_id in self.agents:
                del self.agents[agent_id]
                logger.info(f"智能体已注销: {agent_id}")

    def update_agent_metrics(
        self, agent_id: str, response_time: float, success: bool, memory_usage: float
    ):
        """更新智能体指标"""
        with self.lock:
            if agent_id in self.agents:
                agent = self.agents[agent_id]

                # 更新平均响应时间
                if agent.avg_response_time == 0:
                    agent.avg_response_time = response_time
                else:
                    agent.avg_response_time = (
                        agent.avg_response_time * 0.8 + response_time * 0.2
                    )

                # 更新成功率
                metrics = self.agent_metrics[agent_id]
                total_requests = metrics.get("total_requests", 0) + 1
                successful_requests = metrics.get("successful_requests", 0)
                if success:
                    successful_requests += 1

                metrics["total_requests"] = total_requests
                metrics["successful_requests"] = successful_requests
                metrics["memory_usage"] = memory_usage

                agent.success_rate = successful_requests / total_requests
                agent.last_heartbeat = datetime.now()

    @jit(forceobj=True)
    def _calculate_agent_score(self, agent: AgentInfo, task_priority: int) -> float:
        """计算智能体评分（JIT优化）"""
        # 基础评分
        base_score = 100.0

        # 负载因子 (0 - 1, 越低越好)
        load_factor = agent.current_load / agent.max_capacity
        load_score = (1.0 - load_factor) * 30

        # 响应时间因子 (越低越好)
        response_score = max(0, 20 - agent.avg_response_time)

        # 成功率因子
        success_score = agent.success_rate * 25

        # 优先级匹配因子
        priority_score = 25 if task_priority <= 2 else 15

        total_score = (
            base_score + load_score + response_score + success_score + priority_score
        )
        return total_score

    def select_best_agent(
        self, agent_type: AgentType, task_priority: TaskPriority
    ) -> Optional[AgentInfo]:
        """选择最佳智能体"""
        with self.lock:
            available_agents = [
                agent
                for agent in self.agents.values()
                if (
                    agent.agent_type == agent_type
                    and agent.status == "active"
                    and agent.current_load < agent.max_capacity
                )
            ]

            if not available_agents:
                return None

            # 计算每个智能体的评分
            best_agent = None
            best_score = -1

            for agent in available_agents:
                score = self._calculate_agent_score(agent, task_priority.value)
                if score > best_score:
                    best_score = score
                    best_agent = agent

            return best_agent

    def get_agent_stats(self) -> Dict[str, Any]:
        """获取智能体统计信息"""
        with self.lock:
            stats = {}
            for agent_id, agent in self.agents.items():
                stats[agent_id] = {
                    "agent_type": agent.agent_type.value,
                    "status": agent.status,
                    "current_load": agent.current_load,
                    "max_capacity": agent.max_capacity,
                    "load_percentage": (agent.current_load / agent.max_capacity) * 100,
                    "avg_response_time": agent.avg_response_time,
                    "success_rate": agent.success_rate,
                    "last_heartbeat": agent.last_heartbeat.isoformat(),
                    "metrics": self.agent_metrics.get(agent_id, {}),
                }
            return stats


class TaskQueue:
    """智能任务队列"""

    def __init__(self) -> None:
        """TODO: 添加文档字符串"""
        self.priority_queues: Dict[TaskPriority, List[Task]] = {
            priority: [] for priority in TaskPriority
        }
        self.running_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, Task] = {}
        self.lock = threading.Lock()

    def add_task(self, task: Task):
        """添加任务到队列"""
        with self.lock:
            heapq.heappush(self.priority_queues[task.priority], task)
            logger.info(
                f"任务已添加到队列: {task.task_id} (优先级: {task.priority.name})"
            )

    def get_next_task(self, agent_type: AgentType) -> Optional[Task]:
        """获取下一个任务"""
        with self.lock:
            # 按优先级顺序检查队列
            for priority in TaskPriority:
                queue = self.priority_queues[priority]

                # 查找匹配的任务
                for i, task in enumerate(queue):
                    if task.agent_type == agent_type:
                        # 移除并返回任务
                        removed_task = queue.pop(i)
                        heapq.heapify(queue)  # 重新堆化

                        removed_task.status = TaskStatus.RUNNING
                        removed_task.started_at = datetime.now()
                        self.running_tasks[removed_task.task_id] = removed_task

                        return removed_task

            return None

    def complete_task(
        self,
        task_id: str,
        result: Dict[str, Any],
        execution_time: float,
        memory_usage: float,
    ):
        """完成任务"""
        with self.lock:
            if task_id in self.running_tasks:
                task = self.running_tasks.pop(task_id)
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                task.result = result
                task.execution_time = execution_time
                task.memory_usage = memory_usage

                self.completed_tasks[task_id] = task
                logger.info(f"任务已完成: {task_id}")

    def fail_task(self, task_id: str, error_message: str):
        """任务失败"""
        with self.lock:
            if task_id in self.running_tasks:
                task = self.running_tasks.pop(task_id)
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.now()
                task.error_message = error_message

                # 检查是否需要重试
                if task.retry_count < task.max_retries:
                    task.retry_count += 1
                    task.status = TaskStatus.PENDING
                    task.started_at = None
                    self.add_task(task)
                    logger.info(f"任务重试: {task_id} (第{task.retry_count}次)")
                else:
                    self.completed_tasks[task_id] = task
                    logger.error(f"任务失败: {task_id} - {error_message}")

    def get_queue_stats(self) -> Dict[str, Any]:
        """获取队列统计信息"""
        with self.lock:
            stats = {
                "pending_tasks": {
                    priority.name: len(queue)
                    for priority, queue in self.priority_queues.items()
                },
                "running_tasks": len(self.running_tasks),
                "completed_tasks": len(self.completed_tasks),
                "total_pending": sum(
                    len(queue) for queue in self.priority_queues.values()
                ),
            }
            return stats


class IntelligentTaskScheduler:
    """智能任务调度器"""

    def __init__(self, redis_url: Optional[str] = None):
        """TODO: 添加文档字符串"""
        self.load_balancer = LoadBalancer()
        self.task_queue = TaskQueue()
        self.redis_client: Optional[aioredis.Redis] = None
        self.redis_url = redis_url

        # 调度器状态
        self.is_running = False
        self.scheduler_task: Optional[asyncio.Task] = None

        # 性能统计
        self.stats = {
            "total_tasks_processed": 0,
            "total_tasks_failed": 0,
            "avg_processing_time": 0.0,
            "scheduler_start_time": None,
        }

        logger.info("智能任务调度器初始化完成")

    async def initialize(self) -> None:
        """异步初始化"""
        if self.redis_url:
            self.redis_client = await aioredis.from_url(self.redis_url)
            logger.info("Redis连接已建立")

        self.stats["scheduler_start_time"] = datetime.now()
        logger.info("智能任务调度器异步初始化完成")

    def register_agent(self, agent_info: AgentInfo):
        """注册智能体"""
        self.load_balancer.register_agent(agent_info)

    def unregister_agent(self, agent_id: str):
        """注销智能体"""
        self.load_balancer.unregister_agent(agent_id)

    async def submit_task(
        self,
        task_type: str,
        agent_type: AgentType,
        input_data: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        user_id: Optional[str] = None,
        timeout: float = 30.0,
    ) -> str:
        """提交任务"""
        task_id = str(uuid.uuid4())

        task = Task(
            task_id=task_id,
            task_type=task_type,
            priority=priority,
            agent_type=agent_type,
            input_data=input_data,
            user_id=user_id,
            timeout=timeout,
        )

        self.task_queue.add_task(task)

        # 缓存任务信息到Redis
        if self.redis_client:
            await self.redis_client.setex(
                f"task:{task_id}",
                3600,  # 1小时过期
                json.dumps(asdict(task), default=str),
            )

        logger.info(f"任务已提交: {task_id} -> {agent_type.value}")
        return task_id

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        # 先检查内存中的任务
        if task_id in self.task_queue.running_tasks:
            task = self.task_queue.running_tasks[task_id]
            return asdict(task)

        if task_id in self.task_queue.completed_tasks:
            task = self.task_queue.completed_tasks[task_id]
            return asdict(task)

        # 检查队列中的待处理任务
        with self.task_queue.lock:
            for priority_queue in self.task_queue.priority_queues.values():
                for task in priority_queue:
                    if task.task_id == task_id:
                        return asdict(task)

        # 从Redis获取
        if self.redis_client:
            task_data = await self.redis_client.get(f"task:{task_id}")
            if task_data:
                return json.loads(task_data)

        return None

    async def start_scheduler(self) -> None:
        """启动调度器"""
        if self.is_running:
            logger.warning("调度器已在运行")
            return

        self.is_running = True
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("智能任务调度器已启动")

    async def stop_scheduler(self) -> None:
        """停止调度器"""
        if not self.is_running:
            return

        self.is_running = False
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass

        logger.info("智能任务调度器已停止")

    async def _scheduler_loop(self) -> None:
        """调度器主循环"""
        logger.info("调度器主循环已启动")

        while self.is_running:
            try:
                # 为每种智能体类型调度任务
                for agent_type in AgentType:
                    await self._schedule_tasks_for_agent_type(agent_type)

                # 检查超时任务
                await self._check_timeout_tasks()

                # 更新统计信息
                await self._update_stats()

                # 短暂休眠
                await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"调度器循环错误: {e}")
                await asyncio.sleep(1)

    async def _schedule_tasks_for_agent_type(self, agent_type: AgentType):
        """为特定智能体类型调度任务"""
        # 获取下一个任务
        task = self.task_queue.get_next_task(agent_type)
        if not task:
            return

        # 选择最佳智能体
        best_agent = self.load_balancer.select_best_agent(agent_type, task.priority)
        if not best_agent:
            # 没有可用智能体，将任务放回队列
            task.status = TaskStatus.PENDING
            task.started_at = None
            self.task_queue.add_task(task)
            return

        # 增加智能体负载
        best_agent.current_load += 1

        # 异步执行任务
        asyncio.create_task(self._execute_task(task, best_agent))

    async def _execute_task(self, task: Task, agent: AgentInfo):
        """执行任务"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024

        try:
            # 模拟任务执行（实际应该调用智能体API）
            await asyncio.sleep(0.1)  # 模拟处理时间

            # 模拟结果
            result = {
                "task_id": task.task_id,
                "agent_id": agent.agent_id,
                "processed_at": datetime.now().isoformat(),
                "status": "success",
            }

            execution_time = time.time() - start_time
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            memory_usage = end_memory - start_memory

            # 完成任务
            self.task_queue.complete_task(
                task.task_id, result, execution_time, memory_usage
            )

            # 更新智能体指标
            self.load_balancer.update_agent_metrics(
                agent.agent_id, execution_time, True, memory_usage
            )

            # 更新统计
            self.stats["total_tasks_processed"] += 1

        except Exception as e:
            execution_time = time.time() - start_time
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            memory_usage = end_memory - start_memory

            # 任务失败
            self.task_queue.fail_task(task.task_id, str(e))

            # 更新智能体指标
            self.load_balancer.update_agent_metrics(
                agent.agent_id, execution_time, False, memory_usage
            )

            # 更新统计
            self.stats["total_tasks_failed"] += 1

        finally:
            # 减少智能体负载
            agent.current_load = max(0, agent.current_load - 1)

    async def _check_timeout_tasks(self) -> None:
        """检查超时任务"""
        current_time = datetime.now()
        timeout_tasks = []

        with self.task_queue.lock:
            for task_id, task in self.task_queue.running_tasks.items():
                if task.started_at:
                    elapsed = (current_time - task.started_at).total_seconds()
                    if elapsed > task.timeout:
                        timeout_tasks.append(task_id)

        # 处理超时任务
        for task_id in timeout_tasks:
            self.task_queue.fail_task(task_id, "Task timeout")
            logger.warning(f"任务超时: {task_id}")

    async def _update_stats(self) -> None:
        """更新统计信息"""
        if self.stats["total_tasks_processed"] > 0:
            # 计算平均处理时间
            total_time = 0.0
            count = 0

            with self.task_queue.lock:
                for task in self.task_queue.completed_tasks.values():
                    if task.execution_time:
                        total_time += task.execution_time
                        count += 1

            if count > 0:
                self.stats["avg_processing_time"] = total_time / count

    def get_scheduler_stats(self) -> Dict[str, Any]:
        """获取调度器统计信息"""
        return {
            "scheduler_stats": self.stats,
            "queue_stats": self.task_queue.get_queue_stats(),
            "agent_stats": self.load_balancer.get_agent_stats(),
            "timestamp": datetime.now().isoformat(),
        }


# 全局调度器实例
scheduler = IntelligentTaskScheduler()


async def initialize_scheduler(redis_url: Optional[str] = None):
    """初始化全局调度器"""
    global scheduler
    scheduler = IntelligentTaskScheduler(redis_url)
    await scheduler.initialize()
    await scheduler.start_scheduler()
    return scheduler


async def shutdown_scheduler() -> None:
    """关闭全局调度器"""
    global scheduler
    if scheduler:
        await scheduler.stop_scheduler()
