#!/usr/bin/env python3

"""
异步任务处理器模块

该模块提供异步任务处理功能，用于处理非关键的区块链操作，如事件监听、
数据同步、批量处理等，提高系统的响应性和吞吐量。
"""

import asyncio
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging
import traceback
from typing import Any
import uuid

from internal.model.config import AppConfig


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class TaskPriority(Enum):
    """任务优先级枚举"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Task:
    """任务数据类"""
    task_id: str
    task_type: str
    priority: TaskPriority
    payload: dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    retry_count: int = 0
    max_retries: int = 3
    error_message: str | None = None
    result: Any | None = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        # 转换枚举值
        data["status"] = self.status.value
        data["priority"] = self.priority.value
        # 转换日期时间
        for field in ["created_at", "started_at", "completed_at"]:
            if data[field]:
                data[field] = data[field].isoformat()
        return data


class TaskProcessor:
    """异步任务处理器"""

    def __init__(self, config: AppConfig):
        """
        初始化任务处理器
        
        Args:
            config: 应用配置对象
        """
        self.logger = logging.getLogger(__name__)
        self.config = config

        # 任务队列（按优先级分组）
        self.task_queues = {
            TaskPriority.CRITICAL: asyncio.Queue(),
            TaskPriority.HIGH: asyncio.Queue(),
            TaskPriority.NORMAL: asyncio.Queue(),
            TaskPriority.LOW: asyncio.Queue()
        }

        # 任务存储
        self.tasks: dict[str, Task] = {}

        # 任务处理器映射
        self.task_handlers: dict[str, Callable] = {}

        # 工作线程池
        self.executor = ThreadPoolExecutor(
            max_workers=config.server.max_workers,
            thread_name_prefix="task_processor"
        )

        # 处理器状态
        self.is_running = False
        self.worker_tasks: list[asyncio.Task] = []

        # 统计信息
        self.stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "retried_tasks": 0,
            "average_processing_time": 0.0
        }

        self.logger.info("任务处理器初始化完成")

    def register_handler(self, task_type: str, handler: Callable):
        """
        注册任务处理器
        
        Args:
            task_type: 任务类型
            handler: 处理函数
        """
        self.task_handlers[task_type] = handler
        self.logger.info(f"注册任务处理器: {task_type}")

    async def submit_task(
        self,
        task_type: str,
        payload: dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        max_retries: int = 3
    ) -> str:
        """
        提交任务
        
        Args:
            task_type: 任务类型
            payload: 任务载荷
            priority: 任务优先级
            max_retries: 最大重试次数
            
        Returns:
            任务ID
        """
        # 生成任务ID
        task_id = str(uuid.uuid4())

        # 创建任务
        task = Task(
            task_id=task_id,
            task_type=task_type,
            priority=priority,
            payload=payload,
            max_retries=max_retries
        )

        # 存储任务
        self.tasks[task_id] = task

        # 添加到相应的队列
        await self.task_queues[priority].put(task)

        # 更新统计
        self.stats["total_tasks"] += 1

        self.logger.info(f"提交任务: {task_id}, 类型: {task_type}, 优先级: {priority.name}")
        return task_id

    async def get_task_status(self, task_id: str) -> dict[str, Any] | None:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态信息
        """
        task = self.tasks.get(task_id)
        if task:
            return task.to_dict()
        return None

    async def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否取消成功
        """
        task = self.tasks.get(task_id)
        if task and task.status == TaskStatus.PENDING:
            task.status = TaskStatus.CANCELLED
            self.logger.info(f"任务已取消: {task_id}")
            return True
        return False

    async def start(self):
        """启动任务处理器"""
        if self.is_running:
            self.logger.warning("任务处理器已在运行")
            return

        self.is_running = True

        # 启动工作协程
        for priority in TaskPriority:
            worker_task = asyncio.create_task(
                self._worker(priority),
                name=f"worker_{priority.name.lower()}"
            )
            self.worker_tasks.append(worker_task)

        # 启动清理协程
        cleanup_task = asyncio.create_task(
            self._cleanup_completed_tasks(),
            name="cleanup_worker"
        )
        self.worker_tasks.append(cleanup_task)

        self.logger.info("任务处理器已启动")

    async def stop(self):
        """停止任务处理器"""
        if not self.is_running:
            return

        self.is_running = False

        # 取消所有工作协程
        for task in self.worker_tasks:
            task.cancel()

        # 等待所有协程完成
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)

        # 关闭线程池
        self.executor.shutdown(wait=True)

        self.logger.info("任务处理器已停止")

    async def _worker(self, priority: TaskPriority):
        """
        工作协程
        
        Args:
            priority: 处理的任务优先级
        """
        queue = self.task_queues[priority]

        while self.is_running:
            try:
                # 获取任务（带超时）
                task = await asyncio.wait_for(queue.get(), timeout=1.0)

                # 检查任务是否已取消
                if task.status == TaskStatus.CANCELLED:
                    continue

                # 处理任务
                await self._process_task(task)

            except TimeoutError:
                # 超时是正常的，继续循环
                continue
            except Exception as e:
                self.logger.error(f"工作协程错误 ({priority.name}): {e!s}")

    async def _process_task(self, task: Task):
        """
        处理单个任务
        
        Args:
            task: 要处理的任务
        """
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()

        try:
            # 获取任务处理器
            handler = self.task_handlers.get(task.task_type)
            if not handler:
                raise ValueError(f"未找到任务处理器: {task.task_type}")

            # 执行任务
            if asyncio.iscoroutinefunction(handler):
                result = await handler(task.payload)
            else:
                # 在线程池中执行同步函数
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(self.executor, handler, task.payload)

            # 任务完成
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = result

            # 更新统计
            self.stats["completed_tasks"] += 1
            self._update_average_processing_time(task)

            self.logger.info(f"任务完成: {task.task_id}")

        except Exception as e:
            # 任务失败
            task.error_message = str(e)

            # 检查是否需要重试
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.RETRYING

                # 计算重试延迟（指数退避）
                delay = min(2 ** task.retry_count, 60)  # 最大60秒

                self.logger.warning(
                    f"任务失败，将在 {delay} 秒后重试 "
                    f"({task.retry_count}/{task.max_retries}): {task.task_id}, 错误: {e!s}"
                )

                # 延迟后重新提交任务
                await asyncio.sleep(delay)
                await self.task_queues[task.priority].put(task)

                # 更新统计
                self.stats["retried_tasks"] += 1
            else:
                # 重试次数用尽，标记为失败
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.now()

                # 更新统计
                self.stats["failed_tasks"] += 1

                self.logger.error(
                    f"任务最终失败: {task.task_id}, 错误: {e!s}\n"
                    f"堆栈跟踪: {traceback.format_exc()}"
                )

    def _update_average_processing_time(self, task: Task):
        """
        更新平均处理时间
        
        Args:
            task: 已完成的任务
        """
        if task.started_at and task.completed_at:
            processing_time = (task.completed_at - task.started_at).total_seconds()

            # 计算移动平均
            current_avg = self.stats["average_processing_time"]
            completed_count = self.stats["completed_tasks"]

            if completed_count == 1:
                self.stats["average_processing_time"] = processing_time
            else:
                # 使用指数移动平均
                alpha = 0.1  # 平滑因子
                self.stats["average_processing_time"] = (
                    alpha * processing_time + (1 - alpha) * current_avg
                )

    async def _cleanup_completed_tasks(self):
        """清理已完成的任务"""
        while self.is_running:
            try:
                # 每5分钟清理一次
                await asyncio.sleep(300)

                current_time = datetime.now()
                cleanup_threshold = current_time - timedelta(hours=1)  # 保留1小时

                # 查找需要清理的任务
                tasks_to_remove = []
                for task_id, task in self.tasks.items():
                    if (task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED] and
                        task.completed_at and task.completed_at < cleanup_threshold):
                        tasks_to_remove.append(task_id)

                # 删除任务
                for task_id in tasks_to_remove:
                    del self.tasks[task_id]

                if tasks_to_remove:
                    self.logger.info(f"清理了 {len(tasks_to_remove)} 个已完成的任务")

            except Exception as e:
                self.logger.error(f"清理任务时出错: {e!s}")

    def get_stats(self) -> dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            统计信息
        """
        # 计算队列长度
        queue_lengths = {}
        for priority, queue in self.task_queues.items():
            queue_lengths[priority.name.lower()] = queue.qsize()

        # 计算任务状态分布
        status_counts = {}
        for status in TaskStatus:
            status_counts[status.value] = sum(
                1 for task in self.tasks.values() if task.status == status
            )

        return {
            "is_running": self.is_running,
            "total_tasks": self.stats["total_tasks"],
            "completed_tasks": self.stats["completed_tasks"],
            "failed_tasks": self.stats["failed_tasks"],
            "retried_tasks": self.stats["retried_tasks"],
            "average_processing_time": round(self.stats["average_processing_time"], 3),
            "queue_lengths": queue_lengths,
            "status_counts": status_counts,
            "active_tasks": len(self.tasks),
            "registered_handlers": list(self.task_handlers.keys())
        }

    def get_pending_tasks(self, limit: int = 100) -> list[dict[str, Any]]:
        """
        获取待处理任务列表
        
        Args:
            limit: 返回任务数量限制
            
        Returns:
            待处理任务列表
        """
        pending_tasks = [
            task.to_dict() for task in self.tasks.values()
            if task.status == TaskStatus.PENDING
        ]

        # 按优先级和创建时间排序
        pending_tasks.sort(
            key=lambda x: (x["priority"], x["created_at"]),
            reverse=True
        )

        return pending_tasks[:limit]

    def get_running_tasks(self) -> list[dict[str, Any]]:
        """
        获取正在运行的任务列表
        
        Returns:
            正在运行的任务列表
        """
        return [
            task.to_dict() for task in self.tasks.values()
            if task.status == TaskStatus.RUNNING
        ]


# 预定义的任务类型
class TaskTypes:
    """任务类型常量"""

    # 区块链相关任务
    BLOCKCHAIN_EVENT_SYNC = "blockchain_event_sync"
    BATCH_DATA_STORAGE = "batch_data_storage"
    BATCH_DATA_VERIFICATION = "batch_data_verification"
    CONTRACT_DEPLOYMENT = "contract_deployment"

    # 数据处理任务
    DATA_BACKUP = "data_backup"
    DATA_CLEANUP = "data_cleanup"
    CACHE_REFRESH = "cache_refresh"

    # 监控和维护任务
    HEALTH_CHECK = "health_check"
    METRICS_COLLECTION = "metrics_collection"
    LOG_ROTATION = "log_rotation"

    # 通知任务
    NOTIFICATION_SEND = "notification_send"
    EMAIL_SEND = "email_send"

    # 分析任务
    DATA_ANALYSIS = "data_analysis"
    REPORT_GENERATION = "report_generation"


# 任务处理器装饰器
def async_task(task_type: str, priority: TaskPriority = TaskPriority.NORMAL):
    """
    异步任务装饰器
    
    Args:
        task_type: 任务类型
        priority: 任务优先级
    """
    def decorator(func):
        async def wrapper(self, *args, **kwargs):
            # 检查是否有任务处理器
            if hasattr(self, "task_processor") and self.task_processor:
                # 准备任务载荷
                payload = {
                    "args": args,
                    "kwargs": kwargs,
                    "function_name": func.__name__
                }

                # 提交任务
                task_id = await self.task_processor.submit_task(
                    task_type=task_type,
                    payload=payload,
                    priority=priority
                )

                return {"task_id": task_id, "status": "submitted"}
            else:
                # 直接执行函数
                return await func(self, *args, **kwargs)

        return wrapper
    return decorator
