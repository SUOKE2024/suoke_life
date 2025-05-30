#!/usr/bin/env python3
"""
TCC（Try-Confirm-Cancel）模式分布式事务协调器
提供两阶段提交的优化实现
"""

from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import time
from typing import Any
import uuid

logger = logging.getLogger(__name__)


class TCCStatus(Enum):
    """TCC事务状态"""

    TRYING = "trying"
    CONFIRMING = "confirming"
    CANCELLING = "cancelling"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class TCCResource(ABC):
    """TCC资源接口"""

    @abstractmethod
    async def try_resource(self, request: dict[str, Any]) -> str:
        """
        尝试预留资源，返回预留ID

        Args:
            request: 资源请求参数

        Returns:
            str: 预留ID
        """
        pass

    @abstractmethod
    async def confirm_resource(self, reservation_id: str) -> bool:
        """
        确认资源预留

        Args:
            reservation_id: 预留ID

        Returns:
            bool: 是否成功确认
        """
        pass

    @abstractmethod
    async def cancel_resource(self, reservation_id: str) -> bool:
        """
        取消资源预留

        Args:
            reservation_id: 预留ID

        Returns:
            bool: 是否成功取消
        """
        pass


@dataclass
class TCCOperation:
    """TCC操作定义"""

    resource_name: str
    request: dict[str, Any]
    timeout: float = 30.0
    retry_count: int = 3

    # 运行时信息
    reservation_id: str | None = None
    status: str = "pending"
    error: Exception | None = None
    attempts: int = 0


@dataclass
class TCCTransaction:
    """TCC事务"""

    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    operations: list[TCCOperation] = field(default_factory=list)
    status: TCCStatus = TCCStatus.TRYING
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None

    # 已完成的操作
    tried_operations: list[TCCOperation] = field(default_factory=list)
    confirmed_operations: list[TCCOperation] = field(default_factory=list)
    cancelled_operations: list[TCCOperation] = field(default_factory=list)

    # 事件记录
    events: list[dict[str, Any]] = field(default_factory=list)


class TCCCoordinator:
    """TCC事务协调器"""

    def __init__(self):
        self.resources: dict[str, TCCResource] = {}
        self.transactions: dict[str, TCCTransaction] = {}
        self._lock = asyncio.Lock()

        # 统计信息
        self.stats = {
            "total_transactions": 0,
            "successful_transactions": 0,
            "failed_transactions": 0,
            "cancelled_transactions": 0,
        }

    def register_resource(self, name: str, resource: TCCResource):
        """注册TCC资源"""
        self.resources[name] = resource
        logger.info(f"注册TCC资源: {name}")

    async def begin_transaction(self) -> TCCTransaction:
        """开始新的TCC事务"""
        async with self._lock:
            transaction = TCCTransaction()
            self.transactions[transaction.transaction_id] = transaction
            self.stats["total_transactions"] += 1

            self._record_event(transaction, "transaction_started", {})
            logger.info(f"开始TCC事务: {transaction.transaction_id}")

            return transaction

    def add_operation(self, transaction: TCCTransaction, operation: TCCOperation):
        """添加操作到事务"""
        transaction.operations.append(operation)
        self._record_event(
            transaction,
            "operation_added",
            {"resource": operation.resource_name, "request": operation.request},
        )

    async def execute_transaction(
        self, transaction_id: str, operations: list[TCCOperation] | None = None
    ) -> bool:
        """
        执行TCC事务

        Args:
            transaction_id: 事务ID
            operations: 操作列表（如果提供，会添加到事务中）

        Returns:
            bool: 是否成功
        """
        transaction = self.transactions.get(transaction_id)
        if not transaction:
            raise ValueError(f"事务 {transaction_id} 不存在")

        # 添加操作
        if operations:
            for op in operations:
                self.add_operation(transaction, op)

        try:
            # Try阶段
            success = await self._try_phase(transaction)
            if not success:
                # Try失败，执行Cancel
                await self._cancel_phase(transaction)
                return False

            # Confirm阶段
            success = await self._confirm_phase(transaction)
            if not success:
                # Confirm失败，执行Cancel
                await self._cancel_phase(transaction)
                return False

            # 事务成功
            transaction.status = TCCStatus.CONFIRMED
            transaction.completed_at = datetime.now()
            self.stats["successful_transactions"] += 1

            self._record_event(
                transaction,
                "transaction_confirmed",
                {
                    "duration": (
                        transaction.completed_at - transaction.created_at
                    ).total_seconds()
                },
            )

            logger.info(f"TCC事务 {transaction_id} 执行成功")
            return True

        except Exception as e:
            # 异常，执行Cancel
            logger.error(f"TCC事务 {transaction_id} 执行失败: {e}")
            transaction.status = TCCStatus.FAILED
            self.stats["failed_transactions"] += 1

            await self._cancel_phase(transaction)
            return False

    async def _try_phase(self, transaction: TCCTransaction) -> bool:
        """Try阶段：尝试预留所有资源"""
        transaction.status = TCCStatus.TRYING
        self._record_event(transaction, "try_phase_started", {})

        for operation in transaction.operations:
            success = await self._try_operation(operation)

            if not success:
                self._record_event(
                    transaction,
                    "try_phase_failed",
                    {
                        "failed_operation": operation.resource_name,
                        "error": str(operation.error),
                    },
                )
                return False

            transaction.tried_operations.append(operation)

        self._record_event(
            transaction,
            "try_phase_completed",
            {"tried_count": len(transaction.tried_operations)},
        )

        return True

    async def _try_operation(self, operation: TCCOperation) -> bool:
        """执行单个Try操作"""
        resource = self.resources.get(operation.resource_name)
        if not resource:
            operation.error = ValueError(f"资源 {operation.resource_name} 未注册")
            return False

        for attempt in range(operation.retry_count):
            operation.attempts = attempt + 1

            try:
                logger.debug(
                    f"Try操作: {operation.resource_name} (尝试 {attempt + 1}/{operation.retry_count})"
                )

                # 执行Try
                reservation_id = await asyncio.wait_for(
                    resource.try_resource(operation.request), timeout=operation.timeout
                )

                operation.reservation_id = reservation_id
                operation.status = "tried"

                return True

            except TimeoutError:
                operation.error = TimeoutError(
                    f"Try操作 {operation.resource_name} 超时"
                )
                logger.warning(f"Try操作超时: {operation.resource_name}")

            except Exception as e:
                operation.error = e
                logger.warning(f"Try操作失败: {operation.resource_name}, 错误: {e}")

            # 重试延迟
            if attempt < operation.retry_count - 1:
                await asyncio.sleep(1.0 * (attempt + 1))

        operation.status = "try_failed"
        return False

    async def _confirm_phase(self, transaction: TCCTransaction) -> bool:
        """Confirm阶段：确认所有预留的资源"""
        transaction.status = TCCStatus.CONFIRMING
        self._record_event(transaction, "confirm_phase_started", {})

        # 并行确认所有资源
        confirm_tasks = []
        for operation in transaction.tried_operations:
            task = self._confirm_operation(operation)
            confirm_tasks.append(task)

        results = await asyncio.gather(*confirm_tasks, return_exceptions=True)

        # 检查结果
        all_confirmed = all(
            result is True for result in results if not isinstance(result, Exception)
        )

        if all_confirmed:
            transaction.confirmed_operations = transaction.tried_operations.copy()
            self._record_event(
                transaction,
                "confirm_phase_completed",
                {"confirmed_count": len(transaction.confirmed_operations)},
            )
            return True
        else:
            self._record_event(
                transaction, "confirm_phase_failed", {"results": str(results)}
            )
            return False

    async def _confirm_operation(self, operation: TCCOperation) -> bool:
        """执行单个Confirm操作"""
        if not operation.reservation_id:
            return False

        resource = self.resources.get(operation.resource_name)
        if not resource:
            return False

        try:
            logger.debug(
                f"Confirm操作: {operation.resource_name}, 预留ID: {operation.reservation_id}"
            )

            success = await asyncio.wait_for(
                resource.confirm_resource(operation.reservation_id),
                timeout=operation.timeout,
            )

            if success:
                operation.status = "confirmed"

            return success

        except Exception as e:
            logger.error(f"Confirm操作失败: {operation.resource_name}, 错误: {e}")
            operation.error = e
            operation.status = "confirm_failed"
            return False

    async def _cancel_phase(self, transaction: TCCTransaction) -> bool:
        """Cancel阶段：取消所有预留的资源"""
        transaction.status = TCCStatus.CANCELLING
        self._record_event(transaction, "cancel_phase_started", {})

        # 并行取消所有已尝试的资源
        cancel_tasks = []
        for operation in transaction.tried_operations:
            if operation.reservation_id:
                task = self._cancel_operation(operation)
                cancel_tasks.append(task)

        if cancel_tasks:
            results = await asyncio.gather(*cancel_tasks, return_exceptions=True)

            cancelled_count = sum(
                1
                for result in results
                if result is True and not isinstance(result, Exception)
            )

            self._record_event(
                transaction,
                "cancel_phase_completed",
                {"cancelled_count": cancelled_count, "total_count": len(cancel_tasks)},
            )

        transaction.status = TCCStatus.CANCELLED
        transaction.completed_at = datetime.now()
        self.stats["cancelled_transactions"] += 1

        return True

    async def _cancel_operation(self, operation: TCCOperation) -> bool:
        """执行单个Cancel操作"""
        if not operation.reservation_id:
            return True

        resource = self.resources.get(operation.resource_name)
        if not resource:
            return False

        try:
            logger.debug(
                f"Cancel操作: {operation.resource_name}, 预留ID: {operation.reservation_id}"
            )

            success = await asyncio.wait_for(
                resource.cancel_resource(operation.reservation_id),
                timeout=operation.timeout,
            )

            if success:
                operation.status = "cancelled"

            return success

        except Exception as e:
            logger.error(f"Cancel操作失败: {operation.resource_name}, 错误: {e}")
            operation.error = e
            operation.status = "cancel_failed"
            return False

    def _record_event(
        self, transaction: TCCTransaction, event_type: str, data: dict[str, Any]
    ):
        """记录事件"""
        event = {
            "timestamp": time.time(),
            "type": event_type,
            "transaction_id": transaction.transaction_id,
            "data": data,
        }
        transaction.events.append(event)
        logger.debug(f"TCC事件: {event}")

    def get_transaction_status(self, transaction_id: str) -> dict[str, Any] | None:
        """获取事务状态"""
        transaction = self.transactions.get(transaction_id)
        if not transaction:
            return None

        return {
            "transaction_id": transaction.transaction_id,
            "status": transaction.status.value,
            "created_at": transaction.created_at.isoformat(),
            "completed_at": transaction.completed_at.isoformat()
            if transaction.completed_at
            else None,
            "operations": [
                {
                    "resource": op.resource_name,
                    "status": op.status,
                    "reservation_id": op.reservation_id,
                    "attempts": op.attempts,
                    "error": str(op.error) if op.error else None,
                }
                for op in transaction.operations
            ],
            "events_count": len(transaction.events),
        }

    def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        return {
            **self.stats,
            "active_transactions": len(
                [
                    t
                    for t in self.transactions.values()
                    if t.status in [TCCStatus.TRYING, TCCStatus.CONFIRMING]
                ]
            ),
            "registered_resources": list(self.resources.keys()),
        }


# 全局TCC协调器
_global_coordinator = TCCCoordinator()


def get_tcc_coordinator() -> TCCCoordinator:
    """获取全局TCC协调器"""
    return _global_coordinator
