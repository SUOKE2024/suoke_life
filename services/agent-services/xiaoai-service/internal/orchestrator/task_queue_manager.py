#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
异步任务队列管理器
支持分布式任务处理、优先级队列、任务重试和工作流编排
"""

import asyncio
import json
import time
import uuid
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import heapq
from collections import defaultdict, deque
import pickle
import redis.asyncio as redis
from celery import Celery
from celery.result import AsyncResult

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
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: float = 300.0
    priority: TaskPriority = TaskPriority.NORMAL
    queue_name: str = "default"
    
@dataclass
class Task:
    """任务定义"""
    id: str
    name: str
    func_name: str
    args: tuple
    kwargs: dict
    config: TaskConfig
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = None
    started_at: datetime = None
    completed_at: datetime = None
    retry_count: int = 0
    result: Any = None
    error: str = None
    worker_id: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def __lt__(self, other):
        """用于优先级队列排序"""
        return self.config.priority.value > other.config.priority.value

class WorkflowStep:
    """工作流步骤"""
    
    def __init__(self, name: str, task_func: Callable, 
                 depends_on: List[str] = None, **kwargs):
        self.name = name
        self.task_func = task_func
        self.depends_on = depends_on or []
        self.kwargs = kwargs
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None

class Workflow:
    """工作流定义"""
    
    def __init__(self, name: str, steps: List[WorkflowStep]):
        self.id = str(uuid.uuid4())
        self.name = name
        self.steps = {step.name: step for step in steps}
        self.execution_order = self._calculate_execution_order()
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.results = {}
    
    def _calculate_execution_order(self) -> List[List[str]]:
        """计算执行顺序（拓扑排序）"""
        # 构建依赖图
        graph = defaultdict(list)
        in_degree = defaultdict(int)
        
        for step_name, step in self.steps.items():
            in_degree[step_name] = len(step.depends_on)
            for dep in step.depends_on:
                graph[dep].append(step_name)
        
        # 拓扑排序
        levels = []
        queue = deque([name for name, degree in in_degree.items() if degree == 0])
        
        while queue:
            current_level = []
            for _ in range(len(queue)):
                node = queue.popleft()
                current_level.append(node)
                
                for neighbor in graph[node]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
            
            if current_level:
                levels.append(current_level)
        
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
    
    def __init__(self, worker_id: str, task_registry: Dict[str, Callable]):
        self.worker_id = worker_id
        self.task_registry = task_registry
        self.running = False
        self.current_task = None
        self.processed_count = 0
        self.error_count = 0
        self.start_time = None
    
    async def start(self, queue: PriorityTaskQueue):
        """启动工作器"""
        self.running = True
        self.start_time = time.time()
        logger.info(f"任务工作器 {self.worker_id} 启动")
        
        while self.running:
            try:
                # 获取任务
                task = await queue.get()
                await self._process_task(task)
                
            except asyncio.QueueEmpty:
                # 队列为空，等待一段时间
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
        self.current_task = task
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        task.worker_id = self.worker_id
        
        logger.info(f"工作器 {self.worker_id} 开始处理任务 {task.id}")
        
        try:
            # 获取任务函数
            if task.func_name not in self.task_registry:
                raise ValueError(f"未注册的任务函数: {task.func_name}")
            
            func = self.task_registry[task.func_name]
            
            # 执行任务（带超时）
            result = await asyncio.wait_for(
                self._execute_function(func, task.args, task.kwargs),
                timeout=task.config.timeout
            )
            
            # 任务成功
            task.status = TaskStatus.SUCCESS
            task.result = result
            task.completed_at = datetime.now()
            self.processed_count += 1
            
            logger.info(f"任务 {task.id} 执行成功")
            
        except asyncio.TimeoutError:
            task.status = TaskStatus.FAILURE
            task.error = "任务执行超时"
            task.completed_at = datetime.now()
            self.error_count += 1
            logger.error(f"任务 {task.id} 执行超时")
            
        except Exception as e:
            task.status = TaskStatus.FAILURE
            task.error = str(e)
            task.completed_at = datetime.now()
            self.error_count += 1
            logger.error(f"任务 {task.id} 执行失败: {e}")
        
        finally:
            self.current_task = None
    
    async def _execute_function(self, func: Callable, args: tuple, kwargs: dict):
        """执行函数"""
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            # 在线程池中执行同步函数
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
    
    def get_stats(self) -> Dict[str, Any]:
        """获取工作器统计信息"""
        uptime = time.time() - self.start_time if self.start_time else 0
        
        return {
            'worker_id': self.worker_id,
            'running': self.running,
            'processed_count': self.processed_count,
            'error_count': self.error_count,
            'uptime': uptime,
            'current_task': self.current_task.id if self.current_task else None
        }

class DistributedTaskQueue:
    """分布式任务队列（基于Redis）"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
        self.queue_prefix = "xiaoai:task_queue:"
        self.result_prefix = "xiaoai:task_result:"
        self.lock_prefix = "xiaoai:task_lock:"
    
    async def initialize(self):
        """初始化Redis连接"""
        self.redis_client = redis.from_url(self.redis_url)
        await self.redis_client.ping()
        logger.info("分布式任务队列初始化完成")
    
    async def enqueue(self, task: Task, queue_name: str = "default"):
        """入队任务"""
        queue_key = f"{self.queue_prefix}{queue_name}"
        task_data = {
            'task': pickle.dumps(task),
            'priority': task.config.priority.value,
            'timestamp': time.time()
        }
        
        # 使用有序集合实现优先级队列
        await self.redis_client.zadd(
            queue_key, 
            {json.dumps(task_data): -task.config.priority.value}
        )
        
        logger.debug(f"任务 {task.id} 已入队到 {queue_name}")
    
    async def dequeue(self, queue_name: str = "default", timeout: float = 1.0) -> Optional[Task]:
        """出队任务"""
        queue_key = f"{self.queue_prefix}{queue_name}"
        
        # 使用BZPOPMAX获取最高优先级任务
        result = await self.redis_client.bzpopmax(queue_key, timeout=timeout)
        
        if result:
            _, task_json, _ = result
            task_data = json.loads(task_json)
            task = pickle.loads(task_data['task'])
            return task
        
        return None
    
    async def set_result(self, task_id: str, result: Any, ttl: int = 3600):
        """设置任务结果"""
        result_key = f"{self.result_prefix}{task_id}"
        await self.redis_client.setex(
            result_key, 
            ttl, 
            pickle.dumps(result)
        )
    
    async def get_result(self, task_id: str) -> Any:
        """获取任务结果"""
        result_key = f"{self.result_prefix}{task_id}"
        result_data = await self.redis_client.get(result_key)
        
        if result_data:
            return pickle.loads(result_data)
        
        return None
    
    async def acquire_lock(self, task_id: str, ttl: int = 300) -> bool:
        """获取任务锁"""
        lock_key = f"{self.lock_prefix}{task_id}"
        return await self.redis_client.set(lock_key, "locked", ex=ttl, nx=True)
    
    async def release_lock(self, task_id: str):
        """释放任务锁"""
        lock_key = f"{self.lock_prefix}{task_id}"
        await self.redis_client.delete(lock_key)
    
    async def get_queue_size(self, queue_name: str = "default") -> int:
        """获取队列大小"""
        queue_key = f"{self.queue_prefix}{queue_name}"
        return await self.redis_client.zcard(queue_key)
    
    async def close(self):
        """关闭连接"""
        if self.redis_client:
            await self.redis_client.close()

class TaskQueueManager:
    """任务队列管理器"""
    
    def __init__(self, redis_url: str = None):
        self.local_queues = {}
        self.distributed_queue = None
        self.workers = {}
        self.task_registry = {}
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
            self.distributed_queue = DistributedTaskQueue(redis_url)
    
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
    
    async def submit_task(self, name: str, func_name: str, *args, 
                         config: TaskConfig = None, use_distributed: bool = False, **kwargs) -> str:
        """提交任务"""
        task_id = str(uuid.uuid4())
        config = config or TaskConfig()
        
        task = Task(
            id=task_id,
            name=name,
            func_name=func_name,
            args=args,
            kwargs=kwargs,
            config=config
        )
        
        if use_distributed and self.distributed_queue:
            await self.distributed_queue.enqueue(task, config.queue_name)
        else:
            queue_name = config.queue_name
            if queue_name not in self.local_queues:
                await self.create_queue(queue_name)
            
            await self.local_queues[queue_name].put(task)
        
        self.stats['total_tasks'] += 1
        logger.info(f"任务 {task_id} 提交成功")
        return task_id
    
    async def start_worker(self, worker_id: str, queue_name: str = "default", 
                          use_distributed: bool = False):
        """启动工作器"""
        worker = TaskWorker(worker_id, self.task_registry)
        self.workers[worker_id] = worker
        
        if use_distributed and self.distributed_queue:
            # 分布式工作器
            asyncio.create_task(self._distributed_worker_loop(worker, queue_name))
        else:
            # 本地工作器
            if queue_name not in self.local_queues:
                await self.create_queue(queue_name)
            
            queue = self.local_queues[queue_name]
            asyncio.create_task(worker.start(queue))
        
        self.stats['active_workers'] += 1
        logger.info(f"工作器 {worker_id} 启动成功")
    
    async def _distributed_worker_loop(self, worker: TaskWorker, queue_name: str):
        """分布式工作器循环"""
        worker.running = True
        worker.start_time = time.time()
        
        while worker.running:
            try:
                task = await self.distributed_queue.dequeue(queue_name, timeout=1.0)
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
        
        logger.info(f"工作流 {workflow.name} 提交成功，ID: {workflow.id}")
        return workflow.id
    
    async def _execute_workflow(self, workflow: Workflow):
        """执行工作流"""
        workflow.status = TaskStatus.RUNNING
        workflow.started_at = datetime.now()
        
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
                failed_steps = [name for name in level 
                              if workflow.steps[name].status == TaskStatus.FAILURE]
                
                if failed_steps:
                    workflow.status = TaskStatus.FAILURE
                    logger.error(f"工作流 {workflow.name} 失败，失败步骤: {failed_steps}")
                    return
            
            workflow.status = TaskStatus.SUCCESS
            workflow.completed_at = datetime.now()
            logger.info(f"工作流 {workflow.name} 执行成功")
            
        except Exception as e:
            workflow.status = TaskStatus.FAILURE
            workflow.completed_at = datetime.now()
            logger.error(f"工作流 {workflow.name} 执行失败: {e}")
    
    async def _execute_workflow_step(self, workflow: Workflow, step: WorkflowStep):
        """执行工作流步骤"""
        try:
            # 检查依赖
            for dep_name in step.depends_on:
                dep_step = workflow.steps[dep_name]
                if dep_step.status != TaskStatus.SUCCESS:
                    raise Exception(f"依赖步骤 {dep_name} 未成功完成")
            
            step.status = TaskStatus.RUNNING
            
            # 执行步骤
            if asyncio.iscoroutinefunction(step.task_func):
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
    
    async def get_task_result(self, task_id: str, use_distributed: bool = False):
        """获取任务结果"""
        if use_distributed and self.distributed_queue:
            return await self.distributed_queue.get_result(task_id)
        else:
            # 本地任务结果需要从其他地方获取
            # 这里可以实现本地结果存储
            return None
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
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
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        worker_stats = [worker.get_stats() for worker in self.workers.values()]
        
        return {
            'global_stats': self.stats,
            'workers': worker_stats,
            'queues': {
                name: asyncio.create_task(queue.size()).result() 
                for name, queue in self.local_queues.items()
            },
            'workflows': len(self.workflows),
            'registered_tasks': len(self.task_registry)
        }
    
    async def health_check(self) -> Dict[str, Any]:
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
        healthy_workers = sum(1 for worker in self.workers.values() if worker.running)
        total_workers = len(self.workers)
        
        if total_workers > 0:
            worker_health_rate = healthy_workers / total_workers
            if worker_health_rate < 0.5:
                health['status'] = 'unhealthy'
                health['issues'].append(f"工作器健康率过低: {worker_health_rate:.2%}")
        
        health['components']['workers'] = f"{healthy_workers}/{total_workers}"
        
        return health
    
    async def close(self):
        """关闭管理器"""
        # 停止所有工作器
        for worker_id in list(self.workers.keys()):
            await self.stop_worker(worker_id)
        
        # 关闭分布式队列
        if self.distributed_queue:
            await self.distributed_queue.close()
        
        logger.info("任务队列管理器已关闭")

# 全局任务队列管理器实例
_task_manager = None

async def get_task_manager(redis_url: str = None) -> TaskQueueManager:
    """获取任务队列管理器实例"""
    global _task_manager
    
    if _task_manager is None:
        _task_manager = TaskQueueManager(redis_url)
        await _task_manager.initialize()
    
    return _task_manager

# 装饰器
def task(name: str = None, config: TaskConfig = None):
    """任务装饰器"""
    def decorator(func):
        task_name = name or func.__name__
        
        async def wrapper(*args, **kwargs):
            task_manager = await get_task_manager()
            task_manager.register_task(task_name, func)
            return await task_manager.submit_task(task_name, task_name, *args, config=config, **kwargs)
        
        # 注册任务函数
        wrapper._task_name = task_name
        wrapper._original_func = func
        
        return wrapper
    return decorator 