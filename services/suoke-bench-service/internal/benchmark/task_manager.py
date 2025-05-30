"""
异步任务管理器
"""

import asyncio
import logging
import time
import uuid
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

import aiofiles
import orjson

# 配置日志
logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """任务状态枚举"""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"
    TIMEOUT = "TIMEOUT"


@dataclass
class TaskInfo:
    """任务信息"""

    id: str
    name: str
    status: TaskStatus
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: Any | None = None
    error: str | None = None
    progress: float = 0.0
    metadata: dict[str, Any] = None


class TaskManager:
    """异步任务管理器"""

    def __init__(self, max_workers: int = 4, results_dir: str = "data/results"):
        """初始化任务管理器"""
        self.tasks: dict[str, TaskInfo] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.results_dir = results_dir
        self.lock = asyncio.Lock()

    async def submit_task(
        self, task_id: str | None, name: str, func: Callable, *args, **kwargs
    ) -> str:
        """提交任务"""
        # 生成任务ID（如果未提供）
        if not task_id:
            task_id = str(uuid.uuid4())

        # 创建任务信息
        task = TaskInfo(
            id=task_id,
            name=name,
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            metadata=kwargs.get("metadata", {}),
        )

        # 添加到任务列表
        async with self.lock:
            self.tasks[task_id] = task

        # 保存任务信息
        await self._save_task_info(task)

        # 提交到线程池
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(
            self.executor,
            self._run_task,
            task_id,
            func,
            args,
            kwargs,
        )

        # 添加完成回调
        future.add_done_callback(
            lambda f: asyncio.create_task(self._handle_task_completion(task_id, f))
        )

        return task_id

    async def get_task(self, task_id: str) -> TaskInfo | None:
        """获取任务信息"""
        # 尝试从内存获取
        if task_id in self.tasks:
            return self.tasks[task_id]

        # 从文件加载
        return await self._load_task_info(task_id)

    async def get_all_tasks(self) -> list[TaskInfo]:
        """获取所有任务"""
        return list(self.tasks.values())

    async def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        task = await self.get_task(task_id)
        if not task:
            return False

        if task.status in (TaskStatus.RUNNING, TaskStatus.PENDING):
            task.status = TaskStatus.CANCELED
            task.completed_at = datetime.now()
            await self._save_task_info(task)
            return True

        return False

    async def update_progress(self, task_id: str, progress: float) -> bool:
        """更新任务进度"""
        task = await self.get_task(task_id)
        if not task:
            return False

        if task.status == TaskStatus.RUNNING:
            task.progress = max(0.0, min(1.0, progress))
            await self._save_task_info(task)
            return True

        return False

    def _run_task(self, task_id: str, func: Callable, args: tuple, kwargs: dict) -> Any:
        """执行任务（在线程池中运行）"""
        # 更新任务状态
        task = self.tasks[task_id]
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()

        # 保存任务信息（同步方式）
        self._save_task_info_sync(task)

        try:
            # 执行任务
            logger.info(f"开始执行任务 {task_id}: {task.name}")
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(f"任务 {task_id} 完成，耗时: {elapsed:.2f}秒")

            return result
        except Exception as e:
            logger.exception(f"任务 {task_id} 执行失败: {str(e)}")

            # 更新任务状态
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()

            # 保存任务信息
            self._save_task_info_sync(task)

            # 抛出异常
            raise

    async def _handle_task_completion(self, task_id: str, future) -> None:
        """处理任务完成"""
        try:
            # 获取结果（可能会引发异常）
            result = future.result()

            # 更新任务状态
            async with self.lock:
                if task_id in self.tasks:
                    task = self.tasks[task_id]
                    task.status = TaskStatus.COMPLETED
                    task.result = result
                    task.completed_at = datetime.now()

                    # 保存任务信息
                    await self._save_task_info(task)
        except Exception as e:
            logger.exception(f"处理任务 {task_id} 完成回调时出错: {str(e)}")

            async with self.lock:
                if task_id in self.tasks:
                    task = self.tasks[task_id]
                    task.status = TaskStatus.FAILED
                    task.error = str(e)
                    task.completed_at = datetime.now()

                    # 保存任务信息
                    await self._save_task_info(task)

    async def _save_task_info(self, task: TaskInfo) -> None:
        """保存任务信息到文件（异步方式）"""
        # 将TaskInfo转换为可序列化的字典
        task_dict = {
            "id": task.id,
            "name": task.name,
            "status": task.status,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat()
            if task.completed_at
            else None,
            "progress": task.progress,
            "metadata": task.metadata or {},
        }

        # 可选地包含结果和错误
        if task.status == TaskStatus.COMPLETED and task.result is not None:
            if isinstance(task.result, dict | list):
                task_dict["result"] = task.result
            else:
                task_dict["result"] = str(task.result)

        if task.status == TaskStatus.FAILED and task.error:
            task_dict["error"] = task.error

        # 写入文件
        file_path = f"{self.results_dir}/{task.id}.json"
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(orjson.dumps(task_dict))

    def _save_task_info_sync(self, task: TaskInfo) -> None:
        """保存任务信息到文件（同步方式）"""
        # 将TaskInfo转换为可序列化的字典
        task_dict = {
            "id": task.id,
            "name": task.name,
            "status": task.status,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat()
            if task.completed_at
            else None,
            "progress": task.progress,
            "metadata": task.metadata or {},
        }

        # 可选地包含结果和错误
        if task.status == TaskStatus.COMPLETED and task.result is not None:
            if isinstance(task.result, dict | list):
                task_dict["result"] = task.result
            else:
                task_dict["result"] = str(task.result)

        if task.status == TaskStatus.FAILED and task.error:
            task_dict["error"] = task.error

        # 写入文件
        file_path = f"{self.results_dir}/{task.id}.json"
        with open(file_path, "wb") as f:
            f.write(orjson.dumps(task_dict))

    async def _load_task_info(self, task_id: str) -> TaskInfo | None:
        """从文件加载任务信息"""
        file_path = f"{self.results_dir}/{task_id}.json"
        try:
            async with aiofiles.open(file_path, "rb") as f:
                data = await f.read()
                task_dict = orjson.loads(data)

            # 解析日期时间
            created_at = datetime.fromisoformat(task_dict["created_at"])
            started_at = (
                datetime.fromisoformat(task_dict["started_at"])
                if task_dict.get("started_at")
                else None
            )
            completed_at = (
                datetime.fromisoformat(task_dict["completed_at"])
                if task_dict.get("completed_at")
                else None
            )

            # 创建TaskInfo
            task = TaskInfo(
                id=task_dict["id"],
                name=task_dict["name"],
                status=TaskStatus(task_dict["status"]),
                created_at=created_at,
                started_at=started_at,
                completed_at=completed_at,
                result=task_dict.get("result"),
                error=task_dict.get("error"),
                progress=task_dict.get("progress", 0.0),
                metadata=task_dict.get("metadata", {}),
            )

            # 添加到任务列表
            async with self.lock:
                self.tasks[task_id] = task

            return task
        except (FileNotFoundError, orjson.JSONDecodeError):
            return None
