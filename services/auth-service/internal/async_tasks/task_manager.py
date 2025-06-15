"""
异步任务管理器

提供异步任务处理功能，包括邮件发送、日志记录和后台任务队列。
"""
import asyncio
import logging
import json
import time
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import uuid

from internal.config.settings import get_settings
from internal.cache.redis_cache import get_redis_cache

logger = logging.getLogger(__name__)
settings = get_settings()


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
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time: Optional[float] = None


@dataclass
class Task:
    """异步任务"""
    id: str
    name: str
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    scheduled_at: Optional[datetime] = None
    
    # 执行状态
    status: TaskStatus = TaskStatus.PENDING
    current_retry: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Any = None


class TaskQueue:
    """任务队列"""
    
    def __init__(self, name: str, max_workers: int = 5):
        self.name = name
        self.max_workers = max_workers
        self.tasks: asyncio.Queue = asyncio.Queue()
        self.workers: List[asyncio.Task] = []
        self.running_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, TaskResult] = {}
        self.is_running = False
        self._stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "retried_tasks": 0
        }
    
    async def start(self):
        """启动队列工作器"""
        if self.is_running:
            return
        
        self.is_running = True
        self.workers = [
            asyncio.create_task(self._worker(f"{self.name}-worker-{i}"))
            for i in range(self.max_workers)
        ]
        logger.info(f"任务队列 {self.name} 已启动，工作器数量: {self.max_workers}")
    
    async def stop(self):
        """停止队列工作器"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # 取消所有工作器
        for worker in self.workers:
            worker.cancel()
        
        # 等待工作器完成
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()
        
        logger.info(f"任务队列 {self.name} 已停止")
    
    async def add_task(self, task: Task) -> str:
        """添加任务到队列"""
        await self.tasks.put(task)
        self._stats["total_tasks"] += 1
        logger.debug(f"任务已添加到队列 {self.name}: {task.id}")
        return task.id
    
    async def _worker(self, worker_name: str):
        """工作器协程"""
        logger.info(f"工作器 {worker_name} 已启动")
        
        while self.is_running:
            try:
                # 获取任务（带超时）
                task = await asyncio.wait_for(self.tasks.get(), timeout=1.0)
                
                # 检查任务是否应该执行
                if task.scheduled_at and task.scheduled_at > datetime.utcnow():
                    # 重新放回队列
                    await self.tasks.put(task)
                    await asyncio.sleep(0.1)
                    continue
                
                # 执行任务
                await self._execute_task(task, worker_name)
                
            except asyncio.TimeoutError:
                # 超时是正常的，继续循环
                continue
            except Exception as e:
                logger.error(f"工作器 {worker_name} 发生错误: {str(e)}")
        
        logger.info(f"工作器 {worker_name} 已停止")
    
    async def _execute_task(self, task: Task, worker_name: str):
        """执行任务"""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        self.running_tasks[task.id] = task
        
        logger.info(f"开始执行任务 {task.id} ({task.name}) - 工作器: {worker_name}")
        
        try:
            # 设置超时
            if task.timeout:
                result = await asyncio.wait_for(
                    self._run_task_function(task),
                    timeout=task.timeout
                )
            else:
                result = await self._run_task_function(task)
            
            # 任务成功完成
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.result = result
            
            self._stats["completed_tasks"] += 1
            
            # 记录结果
            task_result = TaskResult(
                task_id=task.id,
                status=TaskStatus.COMPLETED,
                result=result,
                started_at=task.started_at,
                completed_at=task.completed_at,
                execution_time=(task.completed_at - task.started_at).total_seconds()
            )
            self.completed_tasks[task.id] = task_result
            
            logger.info(f"任务执行成功 {task.id} - 耗时: {task_result.execution_time:.3f}秒")
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"任务执行失败 {task.id}: {error_msg}")
            
            # 检查是否需要重试
            if task.current_retry < task.max_retries:
                task.current_retry += 1
                task.status = TaskStatus.RETRYING
                task.error_message = error_msg
                
                # 延迟后重新添加到队列
                delay = task.retry_delay * (2 ** (task.current_retry - 1))  # 指数退避
                task.scheduled_at = datetime.utcnow() + timedelta(seconds=delay)
                
                await self.tasks.put(task)
                self._stats["retried_tasks"] += 1
                
                logger.info(f"任务 {task.id} 将在 {delay} 秒后重试 (第 {task.current_retry} 次)")
            else:
                # 重试次数用完，标记为失败
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.utcnow()
                task.error_message = error_msg
                
                self._stats["failed_tasks"] += 1
                
                # 记录失败结果
                task_result = TaskResult(
                    task_id=task.id,
                    status=TaskStatus.FAILED,
                    error=error_msg,
                    started_at=task.started_at,
                    completed_at=task.completed_at,
                    execution_time=(task.completed_at - task.started_at).total_seconds() if task.started_at else None
                )
                self.completed_tasks[task.id] = task_result
        
        finally:
            # 从运行中任务列表移除
            self.running_tasks.pop(task.id, None)
    
    async def _run_task_function(self, task: Task) -> Any:
        """运行任务函数"""
        if asyncio.iscoroutinefunction(task.func):
            # 异步函数
            return await task.func(*task.args, **task.kwargs)
        else:
            # 同步函数，在线程池中执行
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                return await loop.run_in_executor(
                    executor, 
                    lambda: task.func(*task.args, **task.kwargs)
                )
    
    def get_stats(self) -> Dict[str, Any]:
        """获取队列统计信息"""
        return {
            "name": self.name,
            "max_workers": self.max_workers,
            "is_running": self.is_running,
            "pending_tasks": self.tasks.qsize(),
            "running_tasks": len(self.running_tasks),
            "completed_tasks_count": len(self.completed_tasks),
            **self._stats
        }


class TaskManager:
    """任务管理器"""
    
    def __init__(self):
        self.queues: Dict[str, TaskQueue] = {}
        self.cache = get_redis_cache()
        self.is_initialized = False
        
        # 预定义队列
        self.DEFAULT_QUEUES = {
            "email": {"max_workers": 3},
            "logging": {"max_workers": 2},
            "cleanup": {"max_workers": 1},
            "notifications": {"max_workers": 2},
            "analytics": {"max_workers": 1}
        }
    
    async def initialize(self):
        """初始化任务管理器"""
        if self.is_initialized:
            return
        
        # 创建默认队列
        for queue_name, config in self.DEFAULT_QUEUES.items():
            await self.create_queue(queue_name, **config)
        
        self.is_initialized = True
        logger.info("任务管理器初始化完成")
    
    async def create_queue(self, name: str, max_workers: int = 5) -> TaskQueue:
        """创建任务队列"""
        if name in self.queues:
            return self.queues[name]
        
        queue = TaskQueue(name, max_workers)
        await queue.start()
        self.queues[name] = queue
        
        logger.info(f"创建任务队列: {name}")
        return queue
    
    async def submit_task(
        self,
        queue_name: str,
        task_name: str,
        func: Callable,
        *args,
        priority: TaskPriority = TaskPriority.NORMAL,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        timeout: Optional[float] = None,
        delay: Optional[float] = None,
        **kwargs
    ) -> str:
        """提交任务"""
        if not self.is_initialized:
            await self.initialize()
        
        if queue_name not in self.queues:
            raise ValueError(f"队列不存在: {queue_name}")
        
        # 创建任务
        task_id = str(uuid.uuid4())
        scheduled_at = None
        if delay:
            scheduled_at = datetime.utcnow() + timedelta(seconds=delay)
        
        task = Task(
            id=task_id,
            name=task_name,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            max_retries=max_retries,
            retry_delay=retry_delay,
            timeout=timeout,
            scheduled_at=scheduled_at
        )
        
        # 添加到队列
        queue = self.queues[queue_name]
        await queue.add_task(task)
        
        logger.debug(f"任务已提交: {task_id} -> {queue_name}")
        return task_id
    
    async def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """获取任务结果"""
        for queue in self.queues.values():
            if task_id in queue.completed_tasks:
                return queue.completed_tasks[task_id]
            if task_id in queue.running_tasks:
                task = queue.running_tasks[task_id]
                return TaskResult(
                    task_id=task_id,
                    status=task.status,
                    started_at=task.started_at
                )
        return None
    
    async def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        for queue in self.queues.values():
            if task_id in queue.running_tasks:
                task = queue.running_tasks[task_id]
                task.status = TaskStatus.CANCELLED
                return True
        return False
    
    async def shutdown(self):
        """关闭任务管理器"""
        logger.info("正在关闭任务管理器...")
        
        # 停止所有队列
        for queue in self.queues.values():
            await queue.stop()
        
        self.queues.clear()
        self.is_initialized = False
        
        logger.info("任务管理器已关闭")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "total_queues": len(self.queues),
            "is_initialized": self.is_initialized,
            "queues": {
                name: queue.get_stats() 
                for name, queue in self.queues.items()
            }
        }
    
    # 便捷方法
    
    async def send_email_async(
        self,
        to_email: str,
        subject: str,
        content: str,
        template: Optional[str] = None,
        **template_vars
    ) -> str:
        """异步发送邮件"""
        return await self.submit_task(
            "email",
            "send_email",
            self._send_email,
            to_email=to_email,
            subject=subject,
            content=content,
            template=template,
            template_vars=template_vars,
            priority=TaskPriority.HIGH
        )
    
    async def log_async(
        self,
        level: str,
        message: str,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """异步记录日志"""
        return await self.submit_task(
            "logging",
            "log_message",
            self._log_message,
            level=level,
            message=message,
            extra_data=extra_data or {},
            priority=TaskPriority.LOW
        )
    
    async def cleanup_expired_data(self) -> str:
        """清理过期数据"""
        return await self.submit_task(
            "cleanup",
            "cleanup_expired",
            self._cleanup_expired_data,
            priority=TaskPriority.LOW,
            delay=60  # 延迟1分钟执行
        )
    
    async def send_notification(
        self,
        user_id: str,
        notification_type: str,
        content: Dict[str, Any]
    ) -> str:
        """发送通知"""
        return await self.submit_task(
            "notifications",
            "send_notification",
            self._send_notification,
            user_id=user_id,
            notification_type=notification_type,
            content=content,
            priority=TaskPriority.NORMAL
        )
    
    # 内部任务函数
    
    async def _send_email(
        self,
        to_email: str,
        subject: str,
        content: str,
        template: Optional[str] = None,
        template_vars: Optional[Dict[str, Any]] = None
    ):
        """发送邮件的内部实现"""
        # 这里应该集成实际的邮件服务
        logger.info(f"发送邮件: {to_email} - {subject}")
        
        # 模拟邮件发送
        await asyncio.sleep(0.5)  # 模拟网络延迟
        
        return {
            "status": "sent",
            "to": to_email,
            "subject": subject,
            "sent_at": datetime.utcnow().isoformat()
        }
    
    async def _log_message(
        self,
        level: str,
        message: str,
        extra_data: Dict[str, Any]
    ):
        """记录日志的内部实现"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "extra_data": extra_data
        }
        
        # 这里可以写入到日志文件或发送到日志服务
        logger.info(f"异步日志记录: {level} - {message}")
        
        return log_entry
    
    async def _cleanup_expired_data(self):
        """清理过期数据的内部实现"""
        logger.info("开始清理过期数据")
        
        # 清理过期的会话
        # 清理过期的令牌
        # 清理过期的验证码
        
        # 模拟清理过程
        await asyncio.sleep(2.0)
        
        return {
            "status": "completed",
            "cleaned_sessions": 10,
            "cleaned_tokens": 5,
            "cleaned_codes": 3
        }
    
    async def _send_notification(
        self,
        user_id: str,
        notification_type: str,
        content: Dict[str, Any]
    ):
        """发送通知的内部实现"""
        logger.info(f"发送通知: {user_id} - {notification_type}")
        
        # 这里应该集成实际的通知服务
        await asyncio.sleep(0.2)
        
        return {
            "status": "sent",
            "user_id": user_id,
            "type": notification_type,
            "sent_at": datetime.utcnow().isoformat()
        }


# 全局任务管理器实例
_task_manager: Optional[TaskManager] = None


def get_task_manager() -> TaskManager:
    """获取任务管理器实例"""
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskManager()
    return _task_manager


async def init_task_manager() -> None:
    """初始化任务管理器"""
    manager = get_task_manager()
    await manager.initialize()


async def shutdown_task_manager() -> None:
    """关闭任务管理器"""
    global _task_manager
    if _task_manager:
        await _task_manager.shutdown()
        _task_manager = None 