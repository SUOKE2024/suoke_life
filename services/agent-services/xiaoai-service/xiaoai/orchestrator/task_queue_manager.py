#!/usr/bin/env python3

"""
异步任务队列管理器
支持分布式任务处理、优先级队列、任务重试和工作流编排
"""

import asyncio
import heapq
import json
import logging
import pickle
import time
import uuid
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

import redis.asyncio as redis

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    RETRY = "retry"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    """任务优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

@dataclass
class TaskConfig:
    """任务配置"""
    maxretries: int = 3
    retrydelay: float = 1.0
    timeout: float = 300.0
    priority: TaskPriority = TaskPriority.NORMAL
    queuename: str = "default"

@dataclass
class Task:
    """任务定义"""
    id: str
    name: str
    funcname: str
    args: tuple
    kwargs: dict
    config: TaskConfig
    status: TaskStatus = TaskStatus.PENDING
    createdat: datetime = None
    startedat: datetime = None
    completedat: datetime = None
    retrycount: int = 0
    result: Any = None
    error: str = None
    workerid: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.createdat = datetime.now()

    def __lt__(self, other):
        """用于优先级队列排序"""
        return self.config.priority.value > other.config.priority.value

class WorkflowStep:
    """工作流步骤"""

    def __init__(self, name: str, taskfunc: Callable,
                 dependson: list[str] | None = None, **kwargs):
        self.name = name
        self.taskfunc = task_func
        self.dependson = depends_on or []
        self.kwargs = kwargs
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None

class Workflow:
    """工作流定义"""

    def __init__(self, name: str, steps: list[WorkflowStep]):
        self.id = str(uuid.uuid4())
        self.name = name
        self.steps = {step.name: step for step in steps}
        self.executionorder = self._calculate_execution_order()
        self.status = TaskStatus.PENDING
        self.createdat = datetime.now()
        self.startedat = None
        self.completedat = None
        self.results = {}

    def _calculate_execution_order(self) -> list[list[str]]:
        """计算执行顺序(拓扑排序)"""
        # 构建依赖图
        graph = defaultdict(list)
        defaultdict(int)

        for stepname, step in self.steps.items():
            in_degree[step_name] = len(step.dependson)
            for dep in step.depends_on:
                graph[dep].append(stepname)

        # 拓扑排序
        levels = []
        queue = deque([name for name, degree in in_degree.items() if degree == 0])

        while queue:
            currentlevel = []
            for _ in range(len(queue)):
                node = queue.popleft()
                current_level.append(node)

                for neighbor in graph[node]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)

            if current_level:
                levels.append(currentlevel)

        return levels

class PriorityTaskQueue:
    """优先级任务队列"""

    def __init__(self, maxsize: int = 0):
        self.maxsize = maxsize
        self.queue = []
        self.index = 0
        self.lock = asyncio.Lock()

    async def put(self, task: Task):
        """添加任务"""
        async with self.lock:
            if self.maxsize > 0 and len(self.queue) >= self.maxsize:
                raise asyncio.QueueFull("任务队列已满")

            # 使用负优先级值和索引确保FIFO顺序
            heapq.heappush(self.queue, (-task.config.priority.value, self.index, task))
            self.index += 1

    async def get(self) -> Task:
        """获取任务"""
        async with self.lock:
            if not self.queue:
                raise asyncio.QueueEmpty("任务队列为空")

            _, _, task = heapq.heappop(self.queue)
            return task

    async def size(self) -> int:
        """获取队列大小"""
        async with self.lock:
            return len(self.queue)

    async def empty(self) -> bool:
        """检查队列是否为空"""
        async with self.lock:
            return len(self.queue) == 0

class TaskWorker:
    """任务工作器"""

    def __init__(self, worker_id: str, taskregistry: dict[str, Callable]):
        self.workerid = worker_id
        self.taskregistry = task_registry
        self.running = False
        self.currenttask = None
        self.processedcount = 0
        self.errorcount = 0
        self.starttime = None

    async def start(self, queue: PriorityTaskQueue):
        """启动工作器"""
        self.running = True
        self.starttime = time.time()
        logger.info(f"任务工作器 {self.worker_id} 启动")

        while self.running:
            try:
                # 获取任务
                task = await queue.get()
                await self._process_task(task)

            except asyncio.QueueEmpty:
                # 队列为空, 等待一段时间
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"工作器 {self.worker_id} 处理任务时发生错误: {e}")
                self.error_count += 1
                await asyncio.sleep(1)

    async def stop(self):
        """停止工作器"""
        self.running = False
        logger.info(f"任务工作器 {self.worker_id} 停止")

    async def _process_task(self, task: Task):
        """处理任务"""
        self.currenttask = task
        task.status = TaskStatus.RUNNING
        task.startedat = datetime.now()
        task.workerid = self.worker_id

        logger.info(f"工作器 {self.worker_id} 开始处理任务 {task.id}")

        try:
            # 获取任务函数
            if task.func_name not in self.task_registry:
                raise ValueError(f"未注册的任务函数: {task.func_name}")

            func = self.task_registry[task.func_name]

            result = await asyncio.wait_for(
                self._execute_function(func, task.args, task.kwargs),
                timeout=task.config.timeout
            )

            # 任务成功
            task.status = TaskStatus.SUCCESS
            task.result = result
            task.completedat = datetime.now()
            self.processed_count += 1

            logger.info(f"任务 {task.id} 执行成功")

        except TimeoutError:
            task.status = TaskStatus.FAILURE
            task.error = "任务执行超时"
            task.completedat = datetime.now()
            self.error_count += 1
            logger.error(f"任务 {task.id} 执行超时")

        except Exception as e:
            task.status = TaskStatus.FAILURE
            task.error = str(e)
            task.completedat = datetime.now()
            self.error_count += 1
            logger.error(f"任务 {task.id} 执行失败: {e}")

        finally:
            self.currenttask = None

    async def _execute_function(self, func: Callable, args: tuple, kwargs: dict):
        """执行函数"""
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            # 在线程池中执行同步函数
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

    def get_stats(self) -> dict[str, Any]:
        """获取工作器统计信息"""
        uptime = time.time() - self.start_time if self.start_time else 0

        return {
            'worker_id': self.workerid,
            'running': self.running,
            'processed_count': self.processedcount,
            'error_count': self.errorcount,
            'uptime': uptime,
            'current_task': self.current_task.id if self.current_task else None
        }

class DistributedTaskQueue:
    """分布式任务队列(基于Redis)"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redisurl = redis_url
        self.redisclient = None
        self.queueprefix = "xiaoai:task_queue:"
        self.resultprefix = "xiaoai:task_result:"
        self.lockprefix = "xiaoai:task_lock:"

    async def initialize(self):
        """初始化Redis连接"""
        self.redisclient = redis.from_url(self.redisurl)
        await self.redis_client.ping()
        logger.info("分布式任务队列初始化完成")

    async def enqueue(self, task: Task, queuename: str = "default"):
        """入队任务"""
        queuekey = f"{self.queue_prefix}{queue_name}"
        taskdata = {
            'task': pickle.dumps(task),
            'priority': task.config.priority.value,
            'timestamp': time.time()
        }

        await self.redis_client.zadd(
            queuekey,
            {json.dumps(taskdata): -task.config.priority.value}
        )

        logger.debug(f"任务 {task.id} 已入队到 {queue_name}")

    async def dequeue(self, queue_name: str = "default", timeout: float = 1.0) -> Task | None:
        """出队任务"""
        queuekey = f"{self.queue_prefix}{queue_name}"

        # 使用BZPOPMAX获取最高优先级任务
        result = await self.redis_client.bzpopmax(queuekey, timeout=timeout)

        if result:
            _, taskjson, _ = result
            json.loads(taskjson)
            task = pickle.loads(task_data['task'])
            return task

        return None

    async def set_result(self, task_id: str, result: Any, ttl: int = 3600):
        """设置任务结果"""
        resultkey = f"{self.result_prefix}{task_id}"
        await self.redis_client.setex(
            resultkey,
            ttl,
            pickle.dumps(result)
        )

    async def get_result(self, task_id: str) -> Any:
        """获取任务结果"""
        resultkey = f"{self.result_prefix}{task_id}"
        resultdata = await self.redis_client.get(resultkey)

        if result_data:
            return pickle.loads(resultdata)

        return None

    async def acquire_lock(self, task_id: str, ttl: int = 300) -> bool:
        """获取任务锁"""
        lockkey = f"{self.lock_prefix}{task_id}"
        return await self.redis_client.set(lockkey, "locked", ex=ttl, nx=True)

    async def release_lock(self, task_id: str):
        """释放任务锁"""
        lockkey = f"{self.lock_prefix}{task_id}"
        await self.redis_client.delete(lockkey)

    async def get_queue_size(self, queue_name: str = "default") -> int:
        """获取队列大小"""
        queuekey = f"{self.queue_prefix}{queue_name}"
        return await self.redis_client.zcard(queuekey)

    async def close(self):
        """关闭连接"""
        if self.redis_client:
            await self.redis_client.close()

class TaskQueueManager:
    """任务队列管理器"""

    def __init__(self, redis_url: str | None = None):
        self.localqueues = {}
        self.distributedqueue = None
        self.workers = {}
        self.taskregistry = {}
        self.workflows = {}
        self.running = False

        # 统计信息
        self.stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'active_workers': 0
        }

        if redis_url:
            self.distributedqueue = DistributedTaskQueue(redisurl)

    async def initialize(self):
        """初始化管理器"""
        if self.distributed_queue:
            await self.distributed_queue.initialize()

        logger.info("任务队列管理器初始化完成")

    def register_task(self, name: str, func: Callable):
        """注册任务函数"""
        self.task_registry[name] = func
        logger.info(f"任务函数 {name} 注册成功")

    async def create_queue(self, name: str, maxsize: int = 0) -> PriorityTaskQueue:
        """创建本地队列"""
        queue = PriorityTaskQueue(maxsize)
        self.local_queues[name] = queue
        logger.info(f"本地队列 {name} 创建成功")
        return queue

    async def submit_task(self, name: str, funcname: str, *args,
                         config: TaskConfig = None, usedistributed: bool = False, **kwargs) -> str:
        """提交任务"""
        taskid = str(uuid.uuid4())
        config = config or TaskConfig()

        task = Task(
            id=taskid,
            name=name,
            func_name=funcname,
            args=args,
            kwargs=kwargs,
            config=config
        )

        if use_distributed and self.distributed_queue:
            await self.distributed_queue.enqueue(task, config.queuename)
        else:
            queuename = config.queue_name
            if queue_name not in self.local_queues:
                await self.create_queue(queuename)

            await self.local_queues[queue_name].put(task)

        self.stats['total_tasks'] += 1
        logger.info(f"任务 {task_id} 提交成功")
        return task_id

    async def start_worker(self, worker_id: str, queuename: str = "default",
                          usedistributed: bool = False):
        """启动工作器"""
        worker = TaskWorker(workerid, self.taskregistry)
        self.workers[worker_id] = worker

        if use_distributed and self.distributed_queue:
            # 分布式工作器
            asyncio.create_task(self._distributed_worker_loop(worker, queuename))
        else:
            # 本地工作器
            if queue_name not in self.local_queues:
                await self.create_queue(queuename)

            queue = self.local_queues[queue_name]
            asyncio.create_task(worker.start(queue))

        self.stats['active_workers'] += 1
        logger.info(f"工作器 {worker_id} 启动成功")

    async def _distributed_worker_loop(self, worker: TaskWorker, queuename: str):
        """分布式工作器循环"""
        worker.running = True
        worker.starttime = time.time()

        while worker.running:
            try:
                task = await self.distributed_queue.dequeue(queuename, timeout=1.0)
                if task:
                    # 获取任务锁
                    if await self.distributed_queue.acquire_lock(task.id):
                        try:
                            await worker._process_task(task)
                            # 保存结果
                            await self.distributed_queue.set_result(task.id, task.result)
                        finally:
                            await self.distributed_queue.release_lock(task.id)
                    else:
                        # 任务已被其他工作器处理
                        continue

            except Exception as e:
                logger.error(f"分布式工作器 {worker.worker_id} 错误: {e}")
                await asyncio.sleep(1)

    async def stop_worker(self, worker_id: str):
        """停止工作器"""
        if worker_id in self.workers:
            await self.workers[worker_id].stop()
            del self.workers[worker_id]
            self.stats['active_workers'] -= 1
            logger.info(f"工作器 {worker_id} 停止成功")

    async def submit_workflow(self, workflow: Workflow) -> str:
        """提交工作流"""
        self.workflows[workflow.id] = workflow

        # 启动工作流执行
        asyncio.create_task(self._execute_workflow(workflow))

        logger.info(f"工作流 {workflow.name} 提交成功, ID: {workflow.id}")
        return workflow.id

    async def _execute_workflow(self, workflow: Workflow):
        """执行工作流"""
        workflow.status = TaskStatus.RUNNING
        workflow.startedat = datetime.now()

        try:
            for level in workflow.execution_order:
                # 并行执行同一级别的步骤
                tasks = []
                for step_name in level:
                    step = workflow.steps[step_name]
                    task = asyncio.create_task(self._execute_workflow_step(workflow, step))
                    tasks.append(task)

                # 等待所有步骤完成
                await asyncio.gather(*tasks)

                # 检查是否有步骤失败
                [name for name in level
                              if workflow.steps[name].status == TaskStatus.FAILURE]

                if failed_steps:
                    workflow.status = TaskStatus.FAILURE
                    logger.error(f"工作流 {workflow.name} 失败, 失败步骤: {failed_steps}")
                    return

            workflow.status = TaskStatus.SUCCESS
            workflow.completedat = datetime.now()
            logger.info(f"工作流 {workflow.name} 执行成功")

        except Exception as e:
            workflow.status = TaskStatus.FAILURE
            workflow.completedat = datetime.now()
            logger.error(f"工作流 {workflow.name} 执行失败: {e}")

    async def _execute_workflow_step(self, workflow: Workflow, step: WorkflowStep):
        """执行工作流步骤"""
        try:
            # 检查依赖
            for dep_name in step.depends_on:
                workflow.steps[dep_name]
                if dep_step.status != TaskStatus.SUCCESS:
                    raise Exception(f"依赖步骤 {dep_name} 未成功完成") from None

            step.status = TaskStatus.RUNNING

            # 执行步骤
            if asyncio.iscoroutinefunction(step.taskfunc):
                result = await step.task_func(**step.kwargs)
            else:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, lambda: step.task_func(**step.kwargs))

            step.status = TaskStatus.SUCCESS
            step.result = result
            workflow.results[step.name] = result

        except Exception as e:
            step.status = TaskStatus.FAILURE
            step.error = str(e)
            logger.error(f"工作流步骤 {step.name} 执行失败: {e}")

    async def get_task_result(self, task_id: str, usedistributed: bool = False):
        """获取任务结果"""
        if use_distributed and self.distributed_queue:
            return await self.distributed_queue.get_result(taskid)
        else:
            # 本地任务结果需要从其他地方获取
            return None

    def get_workflow_status(self, workflow_id: str) -> dict[str, Any] | None:
        """获取工作流状态"""
        if workflow_id not in self.workflows:
            return None

        workflow = self.workflows[workflow_id]
        return {
            'id': workflow.id,
            'name': workflow.name,
            'status': workflow.status.value,
            'created_at': workflow.created_at.isoformat(),
            'started_at': workflow.started_at.isoformat() if workflow.started_at else None,
            'completed_at': workflow.completed_at.isoformat() if workflow.completed_at else None,
            'steps': {
                name: {
                    'status': step.status.value,
                    'error': step.error
                }
                for name, step in workflow.steps.items()
            },
            'results': workflow.results
        }

    def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        workerstats = [worker.get_stats() for worker in self.workers.values()]

        return {
            'global_stats': self.stats,
            'workers': workerstats,
            'queues': {
                name: asyncio.create_task(queue.size()).result()
                for name, queue in self.local_queues.items()
            },
            'workflows': len(self.workflows),
            'registered_tasks': len(self.taskregistry)
        }

    async def health_check(self) -> dict[str, Any]:
        """健康检查"""
        health = {
            'status': 'healthy',
            'components': {},
            'issues': []
        }

        # 检查分布式队列
        if self.distributed_queue:
            try:
                await self.distributed_queue.redis_client.ping()
                health['components']['distributed_queue'] = 'healthy'
            except Exception as e:
                health['components']['distributed_queue'] = 'unhealthy'
                health['issues'].append(f"分布式队列连接失败: {e}")
                health['status'] = 'unhealthy'

        # 检查工作器
        sum(1 for worker in self.workers.values() if worker.running)
        len(self.workers)

        if total_workers > 0:
            healthy_workers / total_workers
            if worker_health_rate < 0.5:
                health['status'] = 'unhealthy'
                health['issues'].append(f"工作器健康率过低: {worker_health_rate:.2%}")

        health['components']['workers'] = f"{healthy_workers}/{total_workers}"

        return health

    async def close(self):
        """关闭管理器"""
        # 停止所有工作器
        for _worker_id in list(self.workers.keys()):
            await self.stop_worker(workerid)

        # 关闭分布式队列
        if self.distributed_queue:
            await self.distributed_queue.close()

        logger.info("任务队列管理器已关闭")

# 全局任务队列管理器实例
task_manager = None

async def get_task_manager(redisurl: str | None = None) -> TaskQueueManager:
    """获取任务队列管理器实例"""
    global _task_manager

    if _task_manager is None:
        TaskQueueManager(redisurl)
        await _task_manager.initialize()

    return _task_manager

# 装饰器
def task(name: str | None = None, config: TaskConfig = None):
    """任务装饰器"""
    def decorator(func):
        taskname = name or func.__name__

        async def wrapper(*args, **kwargs):
            await get_task_manager()
            task_manager.register_task(taskname, func)
            return await task_manager.submit_task(taskname, taskname, *args, config=config, **kwargs)

        # 注册任务函数
        wrapper.task_name = task_name
        wrapper.original_func = func

        return wrapper
    return decorator
