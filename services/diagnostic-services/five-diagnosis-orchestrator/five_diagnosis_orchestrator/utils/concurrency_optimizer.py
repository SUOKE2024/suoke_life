"""
并发优化器

优化五诊协同诊断系统的并发处理能力
"""

import asyncio
import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Awaitable, Union
from dataclasses import dataclass, field
from enum import Enum
import weakref
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp


logger = logging.getLogger(__name__)


class ExecutionMode(Enum):
    """执行模式"""
    ASYNC = "async"           # 异步执行
    THREAD = "thread"         # 线程池执行
    PROCESS = "process"       # 进程池执行
    HYBRID = "hybrid"         # 混合执行


class TaskPriority(Enum):
    """任务优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class TaskConfig:
    """任务配置"""
    priority: TaskPriority = TaskPriority.NORMAL
    timeout_seconds: Optional[float] = None
    retry_count: int = 0
    retry_delay: float = 1.0
    execution_mode: ExecutionMode = ExecutionMode.ASYNC
    max_concurrency: Optional[int] = None


@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    result: Any = None
    error: Optional[Exception] = None
    execution_time: float = 0.0
    retry_count: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    @property
    def is_success(self) -> bool:
        """是否成功"""
        return self.error is None
    
    @property
    def duration(self) -> Optional[float]:
        """执行时长"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


@dataclass
class ConcurrencyMetrics:
    """并发指标"""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    active_tasks: int = 0
    queued_tasks: int = 0
    average_execution_time: float = 0.0
    peak_concurrency: int = 0
    thread_pool_size: int = 0
    process_pool_size: int = 0


class ConcurrencyOptimizer:
    """并发优化器"""
    
    def __init__(
        self,
        max_async_tasks: int = 100,
        thread_pool_size: Optional[int] = None,
        process_pool_size: Optional[int] = None,
        enable_adaptive_scaling: bool = True
    ):
        self.max_async_tasks = max_async_tasks
        self.thread_pool_size = thread_pool_size or min(32, (mp.cpu_count() or 1) + 4)
        self.process_pool_size = process_pool_size or (mp.cpu_count() or 1)
        self.enable_adaptive_scaling = enable_adaptive_scaling
        
        # 执行器
        self.thread_executor: Optional[ThreadPoolExecutor] = None
        self.process_executor: Optional[ProcessPoolExecutor] = None
        
        # 任务管理
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.task_results: Dict[str, TaskResult] = {}
        self.task_semaphore = asyncio.Semaphore(max_async_tasks)
        
        # 指标
        self.metrics = ConcurrencyMetrics()
        self.metrics.thread_pool_size = self.thread_pool_size
        self.metrics.process_pool_size = self.process_pool_size
        
        # 控制
        self._shutdown = False
        self._worker_task: Optional[asyncio.Task] = None
        self._metrics_task: Optional[asyncio.Task] = None
        
        # 自适应缩放
        self._last_scale_time = time.time()
        self._scale_interval = 30  # 30秒检查一次
        
        # 锁
        self._task_lock = asyncio.Lock()
    
    async def initialize(self) -> None:
        """初始化并发优化器"""
        logger.info("初始化并发优化器...")
        
        try:
            # 创建线程池
            self.thread_executor = ThreadPoolExecutor(
                max_workers=self.thread_pool_size,
                thread_name_prefix="diagnosis_thread"
            )
            
            # 创建进程池
            self.process_executor = ProcessPoolExecutor(
                max_workers=self.process_pool_size
            )
            
            # 启动工作任务
            self._worker_task = asyncio.create_task(self._worker_loop())
            self._metrics_task = asyncio.create_task(self._metrics_loop())
            
            logger.info(f"并发优化器初始化完成 - 线程池: {self.thread_pool_size}, 进程池: {self.process_pool_size}")
            
        except Exception as e:
            logger.error(f"并发优化器初始化失败: {e}")
            raise
    
    async def submit_task(
        self,
        task_id: str,
        coro_or_func: Union[Callable[[], Awaitable[Any]], Callable[[], Any]],
        config: Optional[TaskConfig] = None
    ) -> str:
        """提交任务"""
        if config is None:
            config = TaskConfig()
        
        # 创建任务结果
        task_result = TaskResult(task_id=task_id)
        self.task_results[task_id] = task_result
        
        # 添加到队列
        priority = -config.priority.value  # 负数表示高优先级
        await self.task_queue.put((priority, time.time(), task_id, coro_or_func, config))
        
        self.metrics.total_tasks+=1
        self.metrics.queued_tasks+=1
        
        logger.debug(f"提交任务: {task_id}, 优先级: {config.priority.value}")
        return task_id
    
    async def _worker_loop(self) -> None:
        """工作循环"""
        logger.info("启动并发优化器工作循环...")
        
        while not self._shutdown:
            try:
                # 获取任务
                try:
                    priority, submit_time, task_id, coro_or_func, config = await asyncio.wait_for(
                        self.task_queue.get(), timeout=1.0
                    )
                except asyncio.TimeoutError:
                    # 检查自适应缩放
                    if self.enable_adaptive_scaling:
                        await self._check_adaptive_scaling()
                    continue
                
                self.metrics.queued_tasks-=1
                
                # 执行任务
                await self._execute_task(task_id, coro_or_func, config)
                
            except Exception as e:
                logger.error(f"工作循环异常: {e}")
                await asyncio.sleep(0.1)
    
    async def _execute_task(
        self,
        task_id: str,
        coro_or_func: Union[Callable[[], Awaitable[Any]], Callable[[], Any]],
        config: TaskConfig
    ) -> None:
        """执行任务"""
        task_result = self.task_results[task_id]
        task_result.started_at = datetime.utcnow()
        
        try:
            # 根据执行模式选择执行方式
            if config.execution_mode==ExecutionMode.ASYNC:
                await self._execute_async_task(task_id, coro_or_func, config)
            elif config.execution_mode==ExecutionMode.THREAD:
                await self._execute_thread_task(task_id, coro_or_func, config)
            elif config.execution_mode==ExecutionMode.PROCESS:
                await self._execute_process_task(task_id, coro_or_func, config)
            elif config.execution_mode==ExecutionMode.HYBRID:
                await self._execute_hybrid_task(task_id, coro_or_func, config)
            
        except Exception as e:
            task_result.error = e
            self.metrics.failed_tasks+=1
            logger.error(f"任务执行失败: {task_id}, 错误: {e}")
        finally:
            task_result.completed_at = datetime.utcnow()
            if task_result.is_success:
                self.metrics.completed_tasks+=1
            
            # 更新平均执行时间
            if task_result.duration:
                total_completed = self.metrics.completed_tasks + self.metrics.failed_tasks
                if total_completed==1:
                    self.metrics.average_execution_time = task_result.duration
                else:
                    current_avg = self.metrics.average_execution_time
                    self.metrics.average_execution_time = (
                        (current_avg * (total_completed - 1) + task_result.duration) / total_completed
                    )
    
    async def _execute_async_task(
        self,
        task_id: str,
        coro_or_func: Union[Callable[[], Awaitable[Any]], Callable[[], Any]],
        config: TaskConfig
    ) -> None:
        """执行异步任务"""
        async with self.task_semaphore:
            self.metrics.active_tasks+=1
            self.metrics.peak_concurrency = max(self.metrics.peak_concurrency, self.metrics.active_tasks)
            
            try:
                # 创建协程
                if asyncio.iscoroutinefunction(coro_or_func):
                    coro = coro_or_func()
                else:
                    # 包装同步函数
                    async def wrapper():
                        return coro_or_func()
                    coro = wrapper()
                
                # 执行任务
                task = asyncio.create_task(coro)
                self.active_tasks[task_id] = task
                
                try:
                    if config.timeout_seconds:
                        result = await asyncio.wait_for(task, timeout=config.timeout_seconds)
                    else:
                        result = await task
                    
                    self.task_results[task_id].result = result
                    
                except asyncio.TimeoutError:
                    task.cancel()
                    raise TimeoutError(f"任务超时: {task_id}")
                
                finally:
                    if task_id in self.active_tasks:
                        del self.active_tasks[task_id]
            
            finally:
                self.metrics.active_tasks-=1
    
    async def _execute_thread_task(
        self,
        task_id: str,
        coro_or_func: Union[Callable[[], Awaitable[Any]], Callable[[], Any]],
        config: TaskConfig
    ) -> None:
        """执行线程任务"""
        if not self.thread_executor:
            raise RuntimeError("线程池未初始化")
        
        loop = asyncio.get_event_loop()
        
        # 包装函数
        def wrapper():
            if asyncio.iscoroutinefunction(coro_or_func):
                # 在新的事件循环中运行协程
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(coro_or_func())
                finally:
                    new_loop.close()
            else:
                return coro_or_func()
        
        # 提交到线程池
        future = self.thread_executor.submit(wrapper)
        
        try:
            if config.timeout_seconds:
                result = await asyncio.wait_for(
                    loop.run_in_executor(None, future.result, config.timeout_seconds),
                    timeout=config.timeout_seconds
                )
            else:
                result = await loop.run_in_executor(None, future.result)
            
            self.task_results[task_id].result = result
            
        except Exception as e:
            future.cancel()
            raise e
    
    async def _execute_process_task(
        self,
        task_id: str,
        coro_or_func: Union[Callable[[], Awaitable[Any]], Callable[[], Any]],
        config: TaskConfig
    ) -> None:
        """执行进程任务"""
        if not self.process_executor:
            raise RuntimeError("进程池未初始化")
        
        # 进程池只能执行普通函数
        if asyncio.iscoroutinefunction(coro_or_func):
            raise ValueError("进程池不支持协程函数")
        
        loop = asyncio.get_event_loop()
        
        # 提交到进程池
        future = self.process_executor.submit(coro_or_func)
        
        try:
            if config.timeout_seconds:
                result = await asyncio.wait_for(
                    loop.run_in_executor(None, future.result, config.timeout_seconds),
                    timeout=config.timeout_seconds
                )
            else:
                result = await loop.run_in_executor(None, future.result)
            
            self.task_results[task_id].result = result
            
        except Exception as e:
            future.cancel()
            raise e
    
    async def _execute_hybrid_task(
        self,
        task_id: str,
        coro_or_func: Union[Callable[[], Awaitable[Any]], Callable[[], Any]],
        config: TaskConfig
    ) -> None:
        """执行混合任务（自动选择最佳执行方式）"""
        # 根据当前负载选择执行方式
        if self.metrics.active_tasks < self.max_async_tasks//2:
            # 负载较低，使用异步执行
            config.execution_mode = ExecutionMode.ASYNC
            await self._execute_async_task(task_id, coro_or_func, config)
        elif asyncio.iscoroutinefunction(coro_or_func):
            # 协程函数，使用线程执行
            config.execution_mode = ExecutionMode.THREAD
            await self._execute_thread_task(task_id, coro_or_func, config)
        else:
            # 普通函数，使用进程执行
            config.execution_mode = ExecutionMode.PROCESS
            await self._execute_process_task(task_id, coro_or_func, config)
    
    async def _check_adaptive_scaling(self) -> None:
        """检查自适应缩放"""
        current_time = time.time()
        if current_time - self._last_scale_time < self._scale_interval:
            return
        
        self._last_scale_time = current_time
        
        # 计算负载指标
        queue_load = self.metrics.queued_tasks / max(self.max_async_tasks, 1)
        active_load = self.metrics.active_tasks / max(self.max_async_tasks, 1)
        
        # 调整信号量大小
        if queue_load > 0.8 and active_load < 0.6:
            # 队列积压严重但活跃任务不多，增加并发
            new_limit = min(self.max_async_tasks * 2, 200)
            if new_limit > self.task_semaphore._value:
                logger.info(f"自适应增加并发限制: {self.max_async_tasks} -> {new_limit}")
                self.max_async_tasks = new_limit
                # 释放更多信号量
                for _ in range(new_limit - self.task_semaphore._value):
                    self.task_semaphore.release()
        
        elif queue_load < 0.2 and active_load < 0.3:
            # 负载较低，减少并发以节省资源
            new_limit = max(self.max_async_tasks//2, 10)
            if new_limit < self.max_async_tasks:
                logger.info(f"自适应减少并发限制: {self.max_async_tasks} -> {new_limit}")
                self.max_async_tasks = new_limit
    
    async def _metrics_loop(self) -> None:
        """指标收集循环"""
        while not self._shutdown:
            try:
                # 更新指标
                self.metrics.active_tasks = len(self.active_tasks)
                self.metrics.queued_tasks = self.task_queue.qsize()
                
                await asyncio.sleep(5)  # 每5秒更新一次
                
            except Exception as e:
                logger.error(f"指标收集异常: {e}")
                await asyncio.sleep(1)
    
    async def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> TaskResult:
        """等待任务完成"""
        start_time = time.time()
        
        while task_id in self.task_results:
            task_result = self.task_results[task_id]
            
            if task_result.completed_at is not None:
                return task_result
            
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"等待任务超时: {task_id}")
            
            await asyncio.sleep(0.1)
        
        raise ValueError(f"任务不存在: {task_id}")
    
    async def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        # 取消活跃任务
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.cancel()
            del self.active_tasks[task_id]
            
            # 更新任务结果
            if task_id in self.task_results:
                self.task_results[task_id].error = asyncio.CancelledError("任务被取消")
                self.task_results[task_id].completed_at = datetime.utcnow()
            
            return True
        
        return False
    
    async def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """获取任务结果"""
        return self.task_results.get(task_id)
    
    async def get_metrics(self) -> ConcurrencyMetrics:
        """获取并发指标"""
        return self.metrics
    
    async def get_active_tasks(self) -> List[str]:
        """获取活跃任务列表"""
        return list(self.active_tasks.keys())
    
    async def cleanup_completed_tasks(self, max_age_hours: int = 24) -> int:
        """清理已完成的任务"""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        tasks_to_remove = []
        for task_id, task_result in self.task_results.items():
            if (task_result.completed_at and 
                task_result.completed_at < cutoff_time and
                task_id not in self.active_tasks):
                tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            del self.task_results[task_id]
        
        logger.info(f"清理了 {len(tasks_to_remove)} 个已完成的任务")
        return len(tasks_to_remove)
    
    async def batch_submit(
        self,
        tasks: List[tuple],  # (task_id, coro_or_func, config)
        wait_for_completion: bool = False
    ) -> List[str]:
        """批量提交任务"""
        task_ids = []
        
        for task_id, coro_or_func, config in tasks:
            submitted_id = await self.submit_task(task_id, coro_or_func, config)
            task_ids.append(submitted_id)
        
        if wait_for_completion:
            # 等待所有任务完成
            results = []
            for task_id in task_ids:
                try:
                    result = await self.wait_for_task(task_id)
                    results.append(result)
                except Exception as e:
                    logger.error(f"等待任务失败: {task_id}, 错误: {e}")
        
        return task_ids
    
    async def close(self) -> None:
        """关闭并发优化器"""
        logger.info("关闭并发优化器...")
        
        self._shutdown = True
        
        # 取消所有活跃任务
        for task_id, task in self.active_tasks.items():
            task.cancel()
        
        # 等待工作任务完成
        if self._worker_task and not self._worker_task.done():
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        
        if self._metrics_task and not self._metrics_task.done():
            self._metrics_task.cancel()
            try:
                await self._metrics_task
            except asyncio.CancelledError:
                pass
        
        # 关闭执行器
        if self.thread_executor:
            self.thread_executor.shutdown(wait=True)
        
        if self.process_executor:
            self.process_executor.shutdown(wait=True)
        
        logger.info("并发优化器已关闭")


# 全局并发优化器实例
_global_concurrency_optimizer: Optional[ConcurrencyOptimizer] = None


async def get_concurrency_optimizer(**kwargs) -> ConcurrencyOptimizer:
    """获取全局并发优化器实例"""
    global _global_concurrency_optimizer
    if _global_concurrency_optimizer is None:
        _global_concurrency_optimizer = ConcurrencyOptimizer(**kwargs)
        await _global_concurrency_optimizer.initialize()
    return _global_concurrency_optimizer


async def close_global_concurrency_optimizer() -> None:
    """关闭全局并发优化器"""
    global _global_concurrency_optimizer
    if _global_concurrency_optimizer:
        await _global_concurrency_optimizer.close()
        _global_concurrency_optimizer = None


# 便捷函数
async def submit_concurrent_task(
    task_id: str,
    coro_or_func: Union[Callable[[], Awaitable[Any]], Callable[[], Any]],
    config: Optional[TaskConfig] = None
) -> str:
    """提交并发任务的便捷函数"""
    optimizer = await get_concurrency_optimizer()
    return await optimizer.submit_task(task_id, coro_or_func, config)


async def wait_for_concurrent_task(task_id: str, timeout: Optional[float] = None) -> TaskResult:
    """等待并发任务的便捷函数"""
    optimizer = await get_concurrency_optimizer()
    return await optimizer.wait_for_task(task_id, timeout)


def concurrent_task(
    task_id: Optional[str] = None,
    config: Optional[TaskConfig] = None
):
    """并发任务装饰器"""
    def decorator(func):
        async def wrapper(*args,**kwargs):
            nonlocal task_id
            if task_id is None:
                task_id = f"{func.__name__}_{int(time.time() * 1000)}"
            
            # 包装函数
            async def task_func():
                if asyncio.iscoroutinefunction(func):
                    return await func(*args,**kwargs)
                else:
                    return func(*args,**kwargs)
            
            # 提交任务
            optimizer = await get_concurrency_optimizer()
            submitted_id = await optimizer.submit_task(task_id, task_func, config)
            
            # 等待结果
            result = await optimizer.wait_for_task(submitted_id)
            if result.error:
                raise result.error
            return result.result
        
        return wrapper
    return decorator