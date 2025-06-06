"""
queue_manager - 索克生活项目模块
"""

from aio_pika import DeliveryMode, Message
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any
import aio_pika
import aioredis
import asyncio
import json
import logging
import time
import uuid

#!/usr/bin/env python3
"""
消息队列和异步任务管理器
支持Redis、RabbitMQ等多种消息队列，提供任务调度、延迟队列、死信队列等功能
"""



logger = logging.getLogger(__name__)


class QueueType(Enum):
    """队列类型枚举"""

    REDIS = "redis"
    RABBITMQ = "rabbitmq"


class TaskStatus(Enum):
    """任务状态枚举"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


@dataclass
class TaskConfig:
    """任务配置"""

    max_retries: int = 3
    retry_delay: float = 60.0  # 重试延迟（秒）
    timeout: float = 300.0  # 任务超时（秒）
    priority: int = 0  # 优先级，数字越大优先级越高
    delay: float = 0.0  # 延迟执行（秒）
    ttl: float | None = None  # 任务生存时间


@dataclass
class Task:
    """任务数据结构"""

    id: str
    name: str
    payload: dict[str, Any]
    config: TaskConfig
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    retry_count: int = 0
    error_message: str | None = None
    result: Any | None = None


class QueueManager:
    """消息队列管理器"""

    def __init__(
        self,
        queue_type: QueueType = QueueType.REDIS,
        redis_url: str = "redis://localhost:6379",
        rabbitmq_url: str = "amqp://localhost/",
    ):
        """
        初始化队列管理器

        Args:
            queue_type: 队列类型
            redis_url: Redis连接URL
            rabbitmq_url: RabbitMQ连接URL
        """
        self.queue_type = queue_type
        self.redis_url = redis_url
        self.rabbitmq_url = rabbitmq_url

        # 连接对象
        self.redis_client: aioredis.Redis | None = None
        self.rabbitmq_connection: aio_pika.Connection | None = None
        self.rabbitmq_channel: aio_pika.Channel | None = None

        # 任务处理器注册表
        self.task_handlers: dict[str, Callable] = {}

        # 工作进程
        self.workers: list[asyncio.Task] = []
        self.is_running = False

        # 统计信息
        self.stats = {
            "tasks_enqueued": 0,
            "tasks_processed": 0,
            "tasks_failed": 0,
            "tasks_retried": 0,
            "workers_active": 0,
        }

        logger.info("队列管理器初始化完成，类型: %s", queue_type.value)

    async def initialize(self):
        """初始化连接"""
        if self.queue_type == QueueType.REDIS:
            await self._init_redis()
        elif self.queue_type == QueueType.RABBITMQ:
            await self._init_rabbitmq()

        logger.info("队列管理器连接初始化完成")

    async def _init_redis(self):
        """初始化Redis连接"""
        try:
            self.redis_client = aioredis.from_url(
                self.redis_url, encoding="utf-8", decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Redis队列连接建立成功")
        except Exception as e:
            logger.error("Redis队列连接失败: %s", str(e))
            raise

    async def _init_rabbitmq(self):
        """初始化RabbitMQ连接"""
        try:
            self.rabbitmq_connection = await aio_pika.connect_robust(self.rabbitmq_url)
            self.rabbitmq_channel = await self.rabbitmq_connection.channel()
            await self.rabbitmq_channel.set_qos(prefetch_count=10)
            logger.info("RabbitMQ队列连接建立成功")
        except Exception as e:
            logger.error("RabbitMQ队列连接失败: %s", str(e))
            raise

    def register_handler(self, task_name: str, handler: Callable):
        """
        注册任务处理器

        Args:
            task_name: 任务名称
            handler: 处理函数
        """
        self.task_handlers[task_name] = handler
        logger.info("注册任务处理器: %s", task_name)

    async def enqueue_task(
        self,
        task_name: str,
        payload: dict[str, Any],
        config: TaskConfig = None,
        queue_name: str = "default",
    ) -> str:
        """
        将任务加入队列

        Args:
            task_name: 任务名称
            payload: 任务载荷
            config: 任务配置
            queue_name: 队列名称

        Returns:
            任务ID
        """
        config = config or TaskConfig()
        task_id = str(uuid.uuid4())

        task = Task(id=task_id, name=task_name, payload=payload, config=config)

        if self.queue_type == QueueType.REDIS:
            await self._enqueue_redis(task, queue_name)
        elif self.queue_type == QueueType.RABBITMQ:
            await self._enqueue_rabbitmq(task, queue_name)

        self.stats["tasks_enqueued"] += 1
        logger.info("任务已入队: %s, ID: %s", task_name, task_id)

        return task_id

    async def _enqueue_redis(self, task: Task, queue_name: str):
        """Redis队列入队"""
        task_data = {
            "id": task.id,
            "name": task.name,
            "payload": task.payload,
            "config": {
                "max_retries": task.config.max_retries,
                "retry_delay": task.config.retry_delay,
                "timeout": task.config.timeout,
                "priority": task.config.priority,
                "delay": task.config.delay,
                "ttl": task.config.ttl,
            },
            "status": task.status.value,
            "created_at": task.created_at.isoformat(),
            "retry_count": task.retry_count,
        }

        # 如果有延迟，使用延迟队列
        if task.config.delay > 0:
            execute_at = time.time() + task.config.delay
            await self.redis_client.zadd(
                f"delayed:{queue_name}", {json.dumps(task_data): execute_at}
            )
        # 根据优先级入队
        elif task.config.priority > 0:
            await self.redis_client.lpush(
                f"priority:{queue_name}", json.dumps(task_data)
            )
        else:
            await self.redis_client.lpush(
                f"queue:{queue_name}", json.dumps(task_data)
            )

        # 存储任务详情
        await self.redis_client.hset(f"task:{task.id}", mapping=task_data)

        # 设置TTL
        if task.config.ttl:
            await self.redis_client.expire(f"task:{task.id}", int(task.config.ttl))

    async def _enqueue_rabbitmq(self, task: Task, queue_name: str):
        """RabbitMQ队列入队"""
        # 声明队列
        await self.rabbitmq_channel.declare_queue(queue_name, durable=True)

        task_data = {
            "id": task.id,
            "name": task.name,
            "payload": task.payload,
            "config": {
                "max_retries": task.config.max_retries,
                "retry_delay": task.config.retry_delay,
                "timeout": task.config.timeout,
                "priority": task.config.priority,
                "delay": task.config.delay,
                "ttl": task.config.ttl,
            },
            "status": task.status.value,
            "created_at": task.created_at.isoformat(),
            "retry_count": task.retry_count,
        }

        message = Message(
            json.dumps(task_data).encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
            priority=task.config.priority,
        )

        # 如果有延迟，使用延迟交换机
        if task.config.delay > 0:
            message.headers = {"x-delay": int(task.config.delay * 1000)}
            # 这里需要配置延迟交换机

        await self.rabbitmq_channel.default_exchange.publish(
            message, routing_key=queue_name
        )

    async def start_workers(self, num_workers: int = 4, queue_names: list[str] | None = None):
        """
        启动工作进程

        Args:
            num_workers: 工作进程数量
            queue_names: 要处理的队列名称列表
        """
        if self.is_running:
            logger.warning("工作进程已在运行")
            return

        queue_names = queue_names or ["default"]
        self.is_running = True

        # 启动延迟任务处理器
        if self.queue_type == QueueType.REDIS:
            self.workers.append(asyncio.create_task(self._delayed_task_processor()))

        # 启动工作进程
        for i in range(num_workers):
            for queue_name in queue_names:
                worker_task = asyncio.create_task(
                    self._worker(f"worker-{i}-{queue_name}", queue_name)
                )
                self.workers.append(worker_task)

        self.stats["workers_active"] = len(self.workers)
        logger.info(
            "启动了 %d 个工作进程，处理队列: %s", len(self.workers), queue_names
        )

    async def _worker(self, worker_name: str, queue_name: str):
        """工作进程"""
        logger.info("工作进程 %s 开始处理队列 %s", worker_name, queue_name)

        while self.is_running:
            try:
                if self.queue_type == QueueType.REDIS:
                    task_data = await self._dequeue_redis(queue_name)
                elif self.queue_type == QueueType.RABBITMQ:
                    task_data = await self._dequeue_rabbitmq(queue_name)
                else:
                    task_data = None

                if task_data:
                    await self._process_task(task_data, worker_name)
                else:
                    await asyncio.sleep(1)  # 没有任务时短暂休眠

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("工作进程 %s 处理错误: %s", worker_name, str(e))
                await asyncio.sleep(5)  # 错误后休眠

        logger.info("工作进程 %s 已停止", worker_name)

    async def _dequeue_redis(self, queue_name: str) -> dict[str, Any] | None:
        """Redis队列出队"""
        # 优先处理高优先级队列
        task_json = await self.redis_client.brpop(
            [f"priority:{queue_name}", f"queue:{queue_name}"], timeout=1
        )

        if task_json:
            return json.loads(task_json[1])
        return None

    async def _dequeue_rabbitmq(self, queue_name: str) -> dict[str, Any] | None:
        """RabbitMQ队列出队"""
        queue = await self.rabbitmq_channel.declare_queue(queue_name, durable=True)

        try:
            message = await queue.get(timeout=1)
            if message:
                task_data = json.loads(message.body.decode())
                await message.ack()
                return task_data
        except TimeoutError:
            pass

        return None

    async def _delayed_task_processor(self):
        """延迟任务处理器（仅Redis）"""
        while self.is_running:
            try:
                current_time = time.time()

                # 获取所有延迟队列
                delayed_queues = await self.redis_client.keys("delayed:*")

                for delayed_queue in delayed_queues:
                    # 获取到期的任务
                    tasks = await self.redis_client.zrangebyscore(
                        delayed_queue, 0, current_time, withscores=True
                    )

                    for task_json, _score in tasks:
                        # 移动到正常队列
                        queue_name = delayed_queue.replace("delayed:", "")
                        await self.redis_client.lpush(f"queue:{queue_name}", task_json)
                        await self.redis_client.zrem(delayed_queue, task_json)

                await asyncio.sleep(1)  # 每秒检查一次

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("延迟任务处理器错误: %s", str(e))
                await asyncio.sleep(5)

    async def _process_task(self, task_data: dict[str, Any], worker_name: str):
        """处理任务"""
        task_id = task_data["id"]
        task_name = task_data["name"]

        logger.info(
            "工作进程 %s 开始处理任务: %s (%s)", worker_name, task_name, task_id
        )

        # 检查是否有处理器
        if task_name not in self.task_handlers:
            logger.error("未找到任务处理器: %s", task_name)
            await self._mark_task_failed(task_id, "未找到任务处理器")
            return

        # 更新任务状态
        await self._update_task_status(task_id, TaskStatus.PROCESSING)

        try:
            # 执行任务
            handler = self.task_handlers[task_name]

            # 设置超时
            timeout = task_data["config"].get("timeout", 300)
            result = await asyncio.wait_for(
                handler(task_data["payload"]), timeout=timeout
            )

            # 标记任务完成
            await self._mark_task_completed(task_id, result)
            self.stats["tasks_processed"] += 1

            logger.info("任务处理完成: %s (%s)", task_name, task_id)

        except TimeoutError:
            logger.error("任务超时: %s (%s)", task_name, task_id)
            await self._handle_task_failure(task_data, "任务执行超时")

        except Exception as e:
            logger.error("任务处理失败: %s (%s), 错误: %s", task_name, task_id, str(e))
            await self._handle_task_failure(task_data, str(e))

    async def _handle_task_failure(self, task_data: dict[str, Any], error_message: str):
        """处理任务失败"""
        task_id = task_data["id"]
        retry_count = task_data.get("retry_count", 0)
        max_retries = task_data["config"].get("max_retries", 3)

        if retry_count < max_retries:
            # 重试任务
            retry_count += 1
            task_data["retry_count"] = retry_count
            task_data["status"] = TaskStatus.RETRYING.value

            # 计算重试延迟
            retry_delay = task_data["config"].get("retry_delay", 60)
            delay = retry_delay * (2 ** (retry_count - 1))  # 指数退避

            # 重新入队
            if self.queue_type == QueueType.REDIS:
                execute_at = time.time() + delay
                queue_name = "default"  # 这里可以从任务数据中获取
                await self.redis_client.zadd(
                    f"delayed:{queue_name}", {json.dumps(task_data): execute_at}
                )

            self.stats["tasks_retried"] += 1
            logger.info("任务重试: %s, 第 %d 次重试", task_id, retry_count)

        else:
            # 标记为失败
            await self._mark_task_failed(task_id, error_message)
            self.stats["tasks_failed"] += 1

    async def _update_task_status(self, task_id: str, status: TaskStatus):
        """更新任务状态"""
        if self.queue_type == QueueType.REDIS:
            await self.redis_client.hset(f"task:{task_id}", "status", status.value)

            if status == TaskStatus.PROCESSING:
                await self.redis_client.hset(
                    f"task:{task_id}", "started_at", datetime.now().isoformat()
                )

    async def _mark_task_completed(self, task_id: str, result: Any):
        """标记任务完成"""
        if self.queue_type == QueueType.REDIS:
            await self.redis_client.hset(
                f"task:{task_id}",
                mapping={
                    "status": TaskStatus.COMPLETED.value,
                    "completed_at": datetime.now().isoformat(),
                    "result": json.dumps(result) if result else "",
                },
            )

    async def _mark_task_failed(self, task_id: str, error_message: str):
        """标记任务失败"""
        if self.queue_type == QueueType.REDIS:
            await self.redis_client.hset(
                f"task:{task_id}",
                mapping={
                    "status": TaskStatus.FAILED.value,
                    "completed_at": datetime.now().isoformat(),
                    "error_message": error_message,
                },
            )

    async def get_task_status(self, task_id: str) -> dict[str, Any] | None:
        """获取任务状态"""
        if self.queue_type == QueueType.REDIS:
            task_data = await self.redis_client.hgetall(f"task:{task_id}")
            return task_data if task_data else None
        return None

    async def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        if self.queue_type == QueueType.REDIS:
            # 更新状态为取消
            result = await self.redis_client.hset(
                f"task:{task_id}", "status", TaskStatus.CANCELLED.value
            )
            return result > 0
        return False

    async def get_queue_stats(self) -> dict[str, Any]:
        """获取队列统计信息"""
        stats = self.stats.copy()

        if self.queue_type == QueueType.REDIS and self.redis_client:
            # 获取队列长度
            queue_lengths = {}
            queues = await self.redis_client.keys("queue:*")
            for queue in queues:
                length = await self.redis_client.llen(queue)
                queue_lengths[queue] = length

            stats["queue_lengths"] = queue_lengths

        return stats

    async def stop_workers(self):
        """停止工作进程"""
        self.is_running = False

        # 取消所有工作任务
        for worker in self.workers:
            worker.cancel()

        # 等待所有任务完成
        if self.workers:
            await asyncio.gather(*self.workers, return_exceptions=True)

        self.workers.clear()
        self.stats["workers_active"] = 0

        logger.info("所有工作进程已停止")

    async def close(self):
        """关闭队列管理器"""
        await self.stop_workers()

        if self.redis_client:
            await self.redis_client.close()

        if self.rabbitmq_connection:
            await self.rabbitmq_connection.close()

        logger.info("队列管理器已关闭")


# 装饰器函数
def async_task(task_name: str, config: TaskConfig = None, queue_name: str = "default"):
    """
    异步任务装饰器

    Args:
        task_name: 任务名称
        config: 任务配置
        queue_name: 队列名称
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            queue_manager = get_queue_manager()

            # 将函数参数作为载荷
            payload = {"args": args, "kwargs": kwargs}

            return await queue_manager.enqueue_task(
                task_name, payload, config, queue_name
            )

        return wrapper

    return decorator


# 全局队列管理器实例
_queue_manager: QueueManager | None = None


async def get_queue_manager(queue_type: QueueType = QueueType.REDIS) -> QueueManager:
    """获取队列管理器实例"""
    global _queue_manager

    if _queue_manager is None:
        _queue_manager = QueueManager(queue_type)
        await _queue_manager.initialize()

    return _queue_manager


async def close_queue_manager():
    """关闭队列管理器"""
    global _queue_manager

    if _queue_manager:
        await _queue_manager.close()
        _queue_manager = None
