#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
异步任务处理器

提供后台任务执行、任务队列管理、任务调度等功能。
"""

import asyncio
import time
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, List, Union
from dataclasses import dataclass, field
from enum import Enum
from contextlib import asynccontextmanager

from structlog import get_logger

logger = get_logger()


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class TaskPriority(Enum):
    """任务优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    duration: Optional[float] = None
    retry_count: int = 0
    
    @property
    def is_success(self) -> bool:
        """是否成功"""
        return self.status == TaskStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """是否失败"""
        return self.status == TaskStatus.FAILED


@dataclass
class Task:
    """任务定义"""
    task_id: str
    name: str
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: Optional[float] = None
    created_at: float = field(default_factory=time.time)
    scheduled_at: Optional[float] = None
    
    def __lt__(self, other):
        """用于优先级队列排序"""
        if self.priority.value != other.priority.value:
            return self.priority.value > other.priority.value
        return self.created_at < other.created_at


class TaskProcessor(ABC):
    """任务处理器抽象基类"""
    
    @abstractmethod
    async def submit_task(self, task: Task) -> str:
        """提交任务"""
        pass
    
    @abstractmethod
    async def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """获取任务结果"""
        pass
    
    @abstractmethod
    async def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        pass
    
    @abstractmethod
    async def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """获取任务状态"""
        pass


class AsyncTaskProcessor(TaskProcessor):
    """异步任务处理器实现"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.max_workers = config.get("max_workers", 10)
        self.queue_size = config.get("queue_size", 1000)
        self.enable_metrics = config.get("enable_metrics", True)
        
        # 任务队列和状态管理
        self.task_queue = asyncio.PriorityQueue(maxsize=self.queue_size)
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.task_results: Dict[str, TaskResult] = {}
        self.task_futures: Dict[str, asyncio.Future] = {}
        
        # 工作线程
        self.workers: List[asyncio.Task] = []
        self.running = False
        
        # 统计信息
        self.stats = {
            "submitted": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0,
            "retried": 0
        }
        
    async def initialize(self):
        """初始化任务处理器"""
        try:
            # 启动工作线程
            await self._start_workers()
            
            # 启动清理任务
            asyncio.create_task(self._cleanup_task())
            
            self.running = True
            logger.info("异步任务处理器初始化成功", max_workers=self.max_workers)
            
        except Exception as e:
            logger.error("异步任务处理器初始化失败", error=str(e))
            raise
    
    async def _start_workers(self):
        """启动工作线程"""
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)
        
        logger.info("任务工作线程已启动", worker_count=len(self.workers))
    
    async def _worker(self, worker_name: str):
        """工作线程"""
        logger.debug("工作线程启动", worker=worker_name)
        
        while self.running:
            try:
                # 从队列获取任务
                priority, task = await asyncio.wait_for(
                    self.task_queue.get(), 
                    timeout=1.0
                )
                
                # 执行任务
                await self._execute_task(task, worker_name)
                
                # 标记任务完成
                self.task_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error("工作线程异常", worker=worker_name, error=str(e))
                await asyncio.sleep(1)
        
        logger.debug("工作线程停止", worker=worker_name)
    
    async def _execute_task(self, task: Task, worker_name: str):
        """执行任务"""
        task_result = TaskResult(
            task_id=task.task_id,
            status=TaskStatus.RUNNING,
            start_time=time.time()
        )
        
        # 更新任务状态
        self.task_results[task.task_id] = task_result
        
        logger.debug(
            "开始执行任务",
            task_id=task.task_id,
            task_name=task.name,
            worker=worker_name
        )
        
        try:
            # 创建任务执行协程
            if asyncio.iscoroutinefunction(task.func):
                coro = task.func(*task.args, **task.kwargs)
            else:
                # 在线程池中执行同步函数
                loop = asyncio.get_event_loop()
                coro = loop.run_in_executor(None, task.func, *task.args, **task.kwargs)
            
            # 执行任务（带超时）
            if task.timeout:
                result = await asyncio.wait_for(coro, timeout=task.timeout)
            else:
                result = await coro
            
            # 任务成功完成
            task_result.status = TaskStatus.COMPLETED
            task_result.result = result
            task_result.end_time = time.time()
            task_result.duration = task_result.end_time - task_result.start_time
            
            self.stats["completed"] += 1
            
            logger.info(
                "任务执行成功",
                task_id=task.task_id,
                task_name=task.name,
                duration_ms=int(task_result.duration * 1000),
                worker=worker_name
            )
            
        except asyncio.TimeoutError:
            # 任务超时
            task_result.status = TaskStatus.FAILED
            task_result.error = f"任务执行超时 ({task.timeout}s)"
            task_result.end_time = time.time()
            task_result.duration = task_result.end_time - task_result.start_time
            
            self.stats["failed"] += 1
            
            logger.warning(
                "任务执行超时",
                task_id=task.task_id,
                task_name=task.name,
                timeout=task.timeout,
                worker=worker_name
            )
            
        except Exception as e:
            # 任务执行失败
            task_result.status = TaskStatus.FAILED
            task_result.error = str(e)
            task_result.end_time = time.time()
            task_result.duration = task_result.end_time - task_result.start_time
            
            # 检查是否需要重试
            if task_result.retry_count < task.max_retries:
                await self._retry_task(task, task_result)
            else:
                self.stats["failed"] += 1
                
                logger.error(
                    "任务执行失败",
                    task_id=task.task_id,
                    task_name=task.name,
                    error=str(e),
                    retry_count=task_result.retry_count,
                    worker=worker_name
                )
        
        finally:
            # 清理运行中的任务记录
            if task.task_id in self.running_tasks:
                del self.running_tasks[task.task_id]
            
            # 通知等待的Future
            if task.task_id in self.task_futures:
                future = self.task_futures[task.task_id]
                if not future.done():
                    future.set_result(task_result)
    
    async def _retry_task(self, task: Task, task_result: TaskResult):
        """重试任务"""
        task_result.retry_count += 1
        task_result.status = TaskStatus.RETRYING
        
        self.stats["retried"] += 1
        
        logger.info(
            "任务重试",
            task_id=task.task_id,
            task_name=task.name,
            retry_count=task_result.retry_count,
            max_retries=task.max_retries
        )
        
        # 延迟后重新提交任务
        await asyncio.sleep(task.retry_delay * task_result.retry_count)
        
        # 重新加入队列
        await self.task_queue.put((task.priority.value, task))
    
    async def submit_task(self, task: Task) -> str:
        """提交任务"""
        if not self.running:
            raise RuntimeError("任务处理器未运行")
        
        if self.task_queue.full():
            raise RuntimeError("任务队列已满")
        
        # 创建任务结果记录
        task_result = TaskResult(
            task_id=task.task_id,
            status=TaskStatus.PENDING
        )
        self.task_results[task.task_id] = task_result
        
        # 创建Future用于等待结果
        future = asyncio.Future()
        self.task_futures[task.task_id] = future
        
        # 加入队列
        await self.task_queue.put((task.priority.value, task))
        
        self.stats["submitted"] += 1
        
        logger.debug(
            "任务已提交",
            task_id=task.task_id,
            task_name=task.name,
            priority=task.priority.name,
            queue_size=self.task_queue.qsize()
        )
        
        return task.task_id
    
    async def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """获取任务结果"""
        return self.task_results.get(task_id)
    
    async def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> TaskResult:
        """等待任务完成"""
        if task_id not in self.task_futures:
            raise ValueError(f"任务不存在: {task_id}")
        
        future = self.task_futures[task_id]
        
        try:
            if timeout:
                result = await asyncio.wait_for(future, timeout=timeout)
            else:
                result = await future
            
            return result
            
        except asyncio.TimeoutError:
            raise TimeoutError(f"等待任务结果超时: {task_id}")
    
    async def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        # 取消运行中的任务
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            task.cancel()
            
            # 更新任务状态
            if task_id in self.task_results:
                self.task_results[task_id].status = TaskStatus.CANCELLED
            
            self.stats["cancelled"] += 1
            
            logger.info("任务已取消", task_id=task_id)
            return True
        
        # 标记待执行任务为取消状态
        if task_id in self.task_results:
            task_result = self.task_results[task_id]
            if task_result.status == TaskStatus.PENDING:
                task_result.status = TaskStatus.CANCELLED
                self.stats["cancelled"] += 1
                logger.info("待执行任务已取消", task_id=task_id)
                return True
        
        return False
    
    async def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """获取任务状态"""
        task_result = self.task_results.get(task_id)
        return task_result.status if task_result else None
    
    async def get_queue_size(self) -> int:
        """获取队列大小"""
        return self.task_queue.qsize()
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self.stats,
            "queue_size": self.task_queue.qsize(),
            "running_tasks": len(self.running_tasks),
            "total_results": len(self.task_results),
            "workers": len(self.workers)
        }
    
    async def _cleanup_task(self):
        """清理过期的任务结果"""
        cleanup_interval = self.config.get("cleanup_interval", 300)  # 5分钟
        max_result_age = self.config.get("max_result_age", 3600)  # 1小时
        
        while self.running:
            try:
                current_time = time.time()
                expired_tasks = []
                
                for task_id, result in self.task_results.items():
                    if (result.end_time and 
                        current_time - result.end_time > max_result_age):
                        expired_tasks.append(task_id)
                
                # 清理过期任务
                for task_id in expired_tasks:
                    del self.task_results[task_id]
                    if task_id in self.task_futures:
                        del self.task_futures[task_id]
                
                if expired_tasks:
                    logger.debug("清理过期任务结果", count=len(expired_tasks))
                
                await asyncio.sleep(cleanup_interval)
                
            except Exception as e:
                logger.error("清理任务异常", error=str(e))
                await asyncio.sleep(60)
    
    async def shutdown(self):
        """关闭任务处理器"""
        logger.info("开始关闭任务处理器")
        
        self.running = False
        
        # 等待队列处理完成
        await self.task_queue.join()
        
        # 取消所有工作线程
        for worker in self.workers:
            worker.cancel()
        
        # 等待工作线程完成
        if self.workers:
            await asyncio.gather(*self.workers, return_exceptions=True)
        
        # 取消所有运行中的任务
        for task in self.running_tasks.values():
            task.cancel()
        
        logger.info("任务处理器已关闭")


# 便捷函数
async def create_task(
    name: str,
    func: Callable,
    args: tuple = (),
    kwargs: dict = None,
    priority: TaskPriority = TaskPriority.NORMAL,
    max_retries: int = 3,
    timeout: Optional[float] = None
) -> Task:
    """创建任务"""
    return Task(
        task_id=str(uuid.uuid4()),
        name=name,
        func=func,
        args=args,
        kwargs=kwargs or {},
        priority=priority,
        max_retries=max_retries,
        timeout=timeout
    )


@asynccontextmanager
async def task_processor_context(config: Dict):
    """任务处理器上下文管理器"""
    processor = AsyncTaskProcessor(config)
    try:
        await processor.initialize()
        yield processor
    finally:
        await processor.shutdown() 