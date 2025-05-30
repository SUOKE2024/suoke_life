#!/usr/bin/env python3
"""
Saga模式分布式事务管理器
提供长事务的协调和补偿机制
"""

import asyncio
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import time
from typing import Any
import uuid

logger = logging.getLogger(__name__)


class SagaStatus(Enum):
    """Saga状态"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class SagaStep:
    """Saga步骤定义"""

    name: str
    action: Callable[..., Any]
    compensation: Callable[..., Any]
    timeout: float = 30.0
    retry_count: int = 3
    retry_delay: float = 1.0

    # 运行时信息
    status: str = "pending"
    result: Any = None
    error: Exception | None = None
    start_time: float | None = None
    end_time: float | None = None
    attempts: int = 0

    @property
    def execution_time(self) -> float:
        """执行时间"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0


@dataclass
class SagaContext:
    """Saga上下文"""

    saga_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def set(self, key: str, value: Any):
        """设置上下文数据"""
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """获取上下文数据"""
        return self.data.get(key, default)

    def update(self, data: dict[str, Any]):
        """更新上下文数据"""
        self.data.update(data)


class SagaManager:
    """Saga事务管理器"""

    def __init__(
        self,
        saga_id: str | None = None,
        context: SagaContext | None = None,
        persist_state: bool = True,
    ):
        self.saga_id = saga_id or str(uuid.uuid4())
        self.context = context or SagaContext(saga_id=self.saga_id)
        self.steps: list[SagaStep] = []
        self.completed_steps: list[str] = []
        self.status = SagaStatus.PENDING
        self.persist_state = persist_state

        # 事件记录
        self.events: list[dict[str, Any]] = []

        # 统计信息
        self.start_time: float | None = None
        self.end_time: float | None = None

        logger.info(f"创建Saga事务: {self.saga_id}")

    def add_step(self, step: SagaStep) -> "SagaManager":
        """添加Saga步骤"""
        self.steps.append(step)
        self._record_event("step_added", {"step_name": step.name})
        return self

    def add_steps(self, steps: list[SagaStep]) -> "SagaManager":
        """批量添加步骤"""
        for step in steps:
            self.add_step(step)
        return self

    async def execute(self) -> bool:
        """执行Saga事务"""
        self.status = SagaStatus.RUNNING
        self.start_time = time.time()
        self._record_event("saga_started", {})

        try:
            # 执行所有步骤
            for step in self.steps:
                success = await self._execute_step(step)

                if not success:
                    # 步骤失败，开始补偿
                    logger.error(f"步骤 {step.name} 执行失败，开始补偿流程")
                    await self._compensate()
                    return False

                self.completed_steps.append(step.name)

                # 持久化状态
                if self.persist_state:
                    await self._persist_state()

            # 所有步骤成功
            self.status = SagaStatus.COMPLETED
            self.end_time = time.time()
            self._record_event(
                "saga_completed", {"duration": self.end_time - self.start_time}
            )

            logger.info(f"Saga事务 {self.saga_id} 执行成功")
            return True

        except TimeoutError:
            self.status = SagaStatus.TIMEOUT
            logger.error(f"Saga事务 {self.saga_id} 超时")
            await self._compensate()
            return False

        except Exception as e:
            self.status = SagaStatus.FAILED
            logger.error(f"Saga事务 {self.saga_id} 执行失败: {e}")
            await self._compensate()
            return False

        finally:
            if self.persist_state:
                await self._persist_state()

    async def _execute_step(self, step: SagaStep) -> bool:
        """执行单个步骤"""
        step.status = "running"
        step.start_time = time.time()

        for attempt in range(step.retry_count):
            step.attempts = attempt + 1

            try:
                logger.info(
                    f"执行步骤: {step.name} (尝试 {attempt + 1}/{step.retry_count})"
                )

                # 执行步骤
                if asyncio.iscoroutinefunction(step.action):
                    result = await asyncio.wait_for(
                        step.action(self.context), timeout=step.timeout
                    )
                else:
                    result = await asyncio.wait_for(
                        asyncio.get_event_loop().run_in_executor(
                            None, step.action, self.context
                        ),
                        timeout=step.timeout,
                    )

                step.result = result
                step.status = "completed"
                step.end_time = time.time()

                self._record_event(
                    "step_completed",
                    {
                        "step_name": step.name,
                        "duration": step.execution_time,
                        "attempts": step.attempts,
                    },
                )

                return True

            except TimeoutError:
                step.error = TimeoutError(f"步骤 {step.name} 执行超时")
                logger.warning(f"步骤 {step.name} 执行超时")

            except Exception as e:
                step.error = e
                logger.warning(f"步骤 {step.name} 执行失败: {e}")

            # 重试延迟
            if attempt < step.retry_count - 1:
                await asyncio.sleep(step.retry_delay * (attempt + 1))

        # 所有重试都失败
        step.status = "failed"
        step.end_time = time.time()

        self._record_event(
            "step_failed",
            {
                "step_name": step.name,
                "error": str(step.error),
                "attempts": step.attempts,
            },
        )

        return False

    async def _compensate(self):
        """执行补偿事务"""
        self.status = SagaStatus.COMPENSATING
        self._record_event(
            "compensation_started", {"completed_steps": self.completed_steps}
        )

        # 反向执行补偿
        for step_name in reversed(self.completed_steps):
            step = next(s for s in self.steps if s.name == step_name)

            try:
                logger.info(f"执行补偿: {step.name}")

                if asyncio.iscoroutinefunction(step.compensation):
                    await asyncio.wait_for(
                        step.compensation(self.context), timeout=step.timeout
                    )
                else:
                    await asyncio.wait_for(
                        asyncio.get_event_loop().run_in_executor(
                            None, step.compensation, self.context
                        ),
                        timeout=step.timeout,
                    )

                self._record_event("compensation_completed", {"step_name": step.name})

            except Exception as e:
                logger.error(f"补偿步骤 {step.name} 失败: {e}")
                self._record_event(
                    "compensation_failed", {"step_name": step.name, "error": str(e)}
                )

        self.status = SagaStatus.COMPENSATED
        self.end_time = time.time()

        self._record_event(
            "saga_compensated",
            {"duration": self.end_time - self.start_time if self.start_time else 0},
        )

    def _record_event(self, event_type: str, data: dict[str, Any]):
        """记录事件"""
        event = {
            "timestamp": time.time(),
            "type": event_type,
            "saga_id": self.saga_id,
            "data": data,
        }
        self.events.append(event)

        # 可以在这里发送事件到事件总线
        logger.debug(f"Saga事件: {event}")

    async def _persist_state(self):
        """持久化状态（需要实现具体的存储逻辑）"""
        # 这里可以将状态保存到数据库或其他持久化存储
        pass

    def get_status(self) -> dict[str, Any]:
        """获取Saga状态"""
        return {
            "saga_id": self.saga_id,
            "status": self.status.value,
            "steps": [
                {
                    "name": step.name,
                    "status": step.status,
                    "attempts": step.attempts,
                    "execution_time": step.execution_time,
                    "error": str(step.error) if step.error else None,
                }
                for step in self.steps
            ],
            "completed_steps": self.completed_steps,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.end_time - self.start_time
            if self.end_time and self.start_time
            else None,
            "events_count": len(self.events),
        }


class SagaOrchestrator:
    """Saga编排器，管理多个Saga实例"""

    def __init__(self):
        self.sagas: dict[str, SagaManager] = {}
        self.completed_sagas: list[str] = []
        self._lock = asyncio.Lock()

    async def create_saga(
        self, saga_id: str | None = None, context: SagaContext | None = None
    ) -> SagaManager:
        """创建新的Saga"""
        async with self._lock:
            saga = SagaManager(saga_id, context)
            self.sagas[saga.saga_id] = saga
            return saga

    async def get_saga(self, saga_id: str) -> SagaManager | None:
        """获取Saga实例"""
        return self.sagas.get(saga_id)

    async def execute_saga(self, saga_id: str) -> bool:
        """执行指定的Saga"""
        saga = await self.get_saga(saga_id)
        if not saga:
            raise ValueError(f"Saga {saga_id} 不存在")

        result = await saga.execute()

        # 移到已完成列表
        async with self._lock:
            if saga_id in self.sagas:
                del self.sagas[saga_id]
                self.completed_sagas.append(saga_id)

        return result

    def get_active_sagas(self) -> list[dict[str, Any]]:
        """获取活跃的Saga列表"""
        return [saga.get_status() for saga in self.sagas.values()]

    def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        status_counts = {}
        for saga in self.sagas.values():
            status = saga.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "active_sagas": len(self.sagas),
            "completed_sagas": len(self.completed_sagas),
            "status_distribution": status_counts,
        }


# 全局Saga编排器
_global_orchestrator = SagaOrchestrator()


async def get_orchestrator() -> SagaOrchestrator:
    """获取全局Saga编排器"""
    return _global_orchestrator
