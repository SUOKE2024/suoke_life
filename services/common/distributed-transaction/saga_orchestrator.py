#!/usr/bin/env python3
"""
Saga分布式事务管理器
实现分布式事务的编排、补偿和状态管理
"""

import asyncio
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
from typing import Any
import uuid

import aioredis

logger = logging.getLogger(__name__)


class SagaStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"


class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"


@dataclass
class SagaStep:
    """Saga步骤"""

    step_id: str
    service_name: str
    action: str
    compensation_action: str
    input_data: dict[str, Any]
    timeout: int = 30
    retry_count: int = 3
    status: StepStatus = StepStatus.PENDING
    result: dict[str, Any] = None
    error: str = None
    started_at: datetime = None
    completed_at: datetime = None


@dataclass
class SagaTransaction:
    """Saga事务"""

    saga_id: str
    name: str
    steps: list[SagaStep]
    status: SagaStatus = SagaStatus.PENDING
    current_step: int = 0
    context: dict[str, Any] = None
    created_at: datetime = None
    updated_at: datetime = None
    completed_at: datetime = None
    error: str = None


class SagaOrchestrator:
    """Saga编排器"""

    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.service_clients = {}
        self.running_sagas = {}

    def register_service_client(self, service_name: str, client):
        """注册服务客户端"""
        self.service_clients[service_name] = client
        logger.info(f"Registered service client: {service_name}")

    async def start_saga(self, saga: SagaTransaction) -> str:
        """启动Saga事务"""
        try:
            saga.saga_id = str(uuid.uuid4())
            saga.created_at = datetime.utcnow()
            saga.updated_at = datetime.utcnow()
            saga.status = SagaStatus.RUNNING

            # 保存Saga状态
            await self._save_saga_state(saga)

            # 启动执行任务
            task = asyncio.create_task(self._execute_saga(saga))
            self.running_sagas[saga.saga_id] = task

            logger.info(f"Started saga: {saga.name} ({saga.saga_id})")
            return saga.saga_id

        except Exception as e:
            logger.error(f"Failed to start saga {saga.name}: {e}")
            raise

    async def _execute_saga(self, saga: SagaTransaction):
        """执行Saga事务"""
        try:
            # 顺序执行所有步骤
            for i, step in enumerate(saga.steps):
                saga.current_step = i
                await self._save_saga_state(saga)

                success = await self._execute_step(saga, step)
                if not success:
                    # 步骤失败，开始补偿
                    await self._compensate_saga(saga, i)
                    return

            # 所有步骤成功完成
            saga.status = SagaStatus.COMPLETED
            saga.completed_at = datetime.utcnow()
            await self._save_saga_state(saga)

            logger.info(f"Saga completed successfully: {saga.saga_id}")

        except Exception as e:
            logger.error(f"Saga execution failed: {saga.saga_id}, error: {e}")
            saga.status = SagaStatus.FAILED
            saga.error = str(e)
            await self._save_saga_state(saga)

            # 尝试补偿
            await self._compensate_saga(saga, saga.current_step)

        finally:
            # 清理运行中的Saga
            if saga.saga_id in self.running_sagas:
                del self.running_sagas[saga.saga_id]

    async def _execute_step(self, saga: SagaTransaction, step: SagaStep) -> bool:
        """执行单个步骤"""
        step.status = StepStatus.RUNNING
        step.started_at = datetime.utcnow()

        for attempt in range(step.retry_count + 1):
            try:
                # 获取服务客户端
                client = self.service_clients.get(step.service_name)
                if not client:
                    raise Exception(f"Service client not found: {step.service_name}")

                # 准备输入数据（包含上下文）
                input_data = {
                    **step.input_data,
                    "saga_id": saga.saga_id,
                    "step_id": step.step_id,
                    "context": saga.context or {},
                }

                # 执行步骤
                result = await asyncio.wait_for(
                    client.execute_action(step.action, input_data), timeout=step.timeout
                )

                # 步骤成功
                step.status = StepStatus.COMPLETED
                step.completed_at = datetime.utcnow()
                step.result = result

                # 更新Saga上下文
                if result and isinstance(result, dict):
                    if saga.context is None:
                        saga.context = {}
                    saga.context.update(result.get("context", {}))

                await self._save_saga_state(saga)

                logger.info(f"Step completed: {step.step_id} (attempt {attempt + 1})")
                return True

            except TimeoutError:
                logger.warning(f"Step timeout: {step.step_id} (attempt {attempt + 1})")
                if attempt < step.retry_count:
                    await asyncio.sleep(2**attempt)  # 指数退避
                    continue
                else:
                    step.status = StepStatus.FAILED
                    step.error = "Timeout"
                    break

            except Exception as e:
                logger.error(
                    f"Step failed: {step.step_id} (attempt {attempt + 1}), error: {e}"
                )
                if attempt < step.retry_count:
                    await asyncio.sleep(2**attempt)
                    continue
                else:
                    step.status = StepStatus.FAILED
                    step.error = str(e)
                    break

        await self._save_saga_state(saga)
        return False

    async def _compensate_saga(self, saga: SagaTransaction, failed_step_index: int):
        """补偿Saga事务"""
        saga.status = SagaStatus.COMPENSATING
        await self._save_saga_state(saga)

        logger.info(f"Starting compensation for saga: {saga.saga_id}")

        # 逆序补偿已完成的步骤
        for i in range(failed_step_index - 1, -1, -1):
            step = saga.steps[i]

            if step.status == StepStatus.COMPLETED:
                await self._compensate_step(saga, step)

        saga.status = SagaStatus.COMPENSATED
        saga.completed_at = datetime.utcnow()
        await self._save_saga_state(saga)

        logger.info(f"Saga compensation completed: {saga.saga_id}")

    async def _compensate_step(self, saga: SagaTransaction, step: SagaStep):
        """补偿单个步骤"""
        step.status = StepStatus.COMPENSATING

        try:
            # 获取服务客户端
            client = self.service_clients.get(step.service_name)
            if not client:
                logger.error(
                    f"Service client not found for compensation: {step.service_name}"
                )
                return

            # 准备补偿数据
            compensation_data = {
                "saga_id": saga.saga_id,
                "step_id": step.step_id,
                "original_result": step.result,
                "context": saga.context or {},
            }

            # 执行补偿
            await asyncio.wait_for(
                client.execute_action(step.compensation_action, compensation_data),
                timeout=step.timeout,
            )

            step.status = StepStatus.COMPENSATED
            logger.info(f"Step compensated: {step.step_id}")

        except Exception as e:
            logger.error(f"Step compensation failed: {step.step_id}, error: {e}")
            # 补偿失败，但继续其他步骤的补偿

        await self._save_saga_state(saga)

    async def _save_saga_state(self, saga: SagaTransaction):
        """保存Saga状态"""
        try:
            saga.updated_at = datetime.utcnow()
            saga_data = asdict(saga)

            # 序列化datetime对象
            for key, value in saga_data.items():
                if isinstance(value, datetime):
                    saga_data[key] = value.isoformat()

            # 处理steps中的datetime对象
            for step_data in saga_data.get("steps", []):
                for key, value in step_data.items():
                    if isinstance(value, datetime):
                        step_data[key] = value.isoformat()

            await self.redis.setex(
                f"saga:{saga.saga_id}",
                86400,  # 24小时过期
                json.dumps(saga_data),
            )

        except Exception as e:
            logger.error(f"Failed to save saga state: {saga.saga_id}, error: {e}")

    async def get_saga_status(self, saga_id: str) -> SagaTransaction | None:
        """获取Saga状态"""
        try:
            data = await self.redis.get(f"saga:{saga_id}")
            if not data:
                return None

            saga_data = json.loads(data)

            # 反序列化datetime对象
            for key in ["created_at", "updated_at", "completed_at"]:
                if saga_data.get(key):
                    saga_data[key] = datetime.fromisoformat(saga_data[key])

            # 处理steps中的datetime对象
            for step_data in saga_data.get("steps", []):
                for key in ["started_at", "completed_at"]:
                    if step_data.get(key):
                        step_data[key] = datetime.fromisoformat(step_data[key])

                # 重建SagaStep对象
                step_data["status"] = StepStatus(step_data["status"])

            # 重建SagaTransaction对象
            saga_data["status"] = SagaStatus(saga_data["status"])
            saga_data["steps"] = [SagaStep(**step) for step in saga_data["steps"]]

            return SagaTransaction(**saga_data)

        except Exception as e:
            logger.error(f"Failed to get saga status: {saga_id}, error: {e}")
            return None

    async def cancel_saga(self, saga_id: str) -> bool:
        """取消Saga事务"""
        try:
            # 取消运行中的任务
            if saga_id in self.running_sagas:
                task = self.running_sagas[saga_id]
                task.cancel()
                del self.running_sagas[saga_id]

            # 获取Saga状态
            saga = await self.get_saga_status(saga_id)
            if not saga:
                return False

            # 如果Saga正在运行，开始补偿
            if saga.status == SagaStatus.RUNNING:
                await self._compensate_saga(saga, saga.current_step)

            return True

        except Exception as e:
            logger.error(f"Failed to cancel saga {saga_id}: {e}")
            return False

    async def retry_saga(self, saga_id: str) -> bool:
        """重试失败的Saga事务"""
        try:
            saga = await self.get_saga_status(saga_id)
            if not saga or saga.status not in [
                SagaStatus.FAILED,
                SagaStatus.COMPENSATED,
            ]:
                return False

            # 重置状态
            saga.status = SagaStatus.RUNNING
            saga.current_step = 0
            saga.error = None

            # 重置所有步骤状态
            for step in saga.steps:
                step.status = StepStatus.PENDING
                step.result = None
                step.error = None
                step.started_at = None
                step.completed_at = None

            # 重新启动执行
            task = asyncio.create_task(self._execute_saga(saga))
            self.running_sagas[saga.saga_id] = task

            logger.info(f"Retrying saga: {saga.saga_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to retry saga {saga_id}: {e}")
            return False

    def get_running_sagas(self) -> list[str]:
        """获取正在运行的Saga列表"""
        return list(self.running_sagas.keys())

    async def cleanup_completed_sagas(self, older_than_hours: int = 24):
        """清理已完成的Saga记录"""
        try:
            # 获取所有Saga键
            keys = await self.redis.keys("saga:*")

            for key in keys:
                data = await self.redis.get(key)
                if not data:
                    continue

                saga_data = json.loads(data)

                # 检查是否已完成且超过指定时间
                if saga_data.get("status") in ["completed", "failed", "compensated"]:
                    completed_at = saga_data.get("completed_at")
                    if completed_at:
                        completed_time = datetime.fromisoformat(completed_at)
                        if datetime.utcnow() - completed_time > timedelta(
                            hours=older_than_hours
                        ):
                            await self.redis.delete(key)
                            logger.info(f"Cleaned up saga: {saga_data.get('saga_id')}")

        except Exception as e:
            logger.error(f"Failed to cleanup completed sagas: {e}")


# 使用示例：健康诊断Saga
class HealthDiagnosisSaga:
    """健康诊断Saga示例"""

    def __init__(self, orchestrator: SagaOrchestrator):
        self.orchestrator = orchestrator

    async def create_diagnosis_saga(
        self, user_id: str, diagnosis_data: dict[str, Any]
    ) -> str:
        """创建诊断Saga"""
        steps = [
            SagaStep(
                step_id="validate_user",
                service_name="user-service",
                action="validate_user",
                compensation_action="no_compensation",
                input_data={"user_id": user_id},
            ),
            SagaStep(
                step_id="save_diagnosis_request",
                service_name="health-data-service",
                action="save_diagnosis_request",
                compensation_action="delete_diagnosis_request",
                input_data={"user_id": user_id, "data": diagnosis_data},
            ),
            SagaStep(
                step_id="coordinate_diagnosis",
                service_name="xiaoai-service",
                action="coordinate_diagnosis",
                compensation_action="cancel_diagnosis",
                input_data={"user_id": user_id, "diagnosis_data": diagnosis_data},
            ),
            SagaStep(
                step_id="save_diagnosis_result",
                service_name="health-data-service",
                action="save_diagnosis_result",
                compensation_action="delete_diagnosis_result",
                input_data={"user_id": user_id},
            ),
            SagaStep(
                step_id="generate_recommendations",
                service_name="recommendation-service",
                action="generate_recommendations",
                compensation_action="delete_recommendations",
                input_data={"user_id": user_id},
            ),
            SagaStep(
                step_id="send_notification",
                service_name="notification-service",
                action="send_diagnosis_notification",
                compensation_action="no_compensation",
                input_data={"user_id": user_id},
            ),
        ]

        saga = SagaTransaction(
            saga_id="",  # 将由orchestrator生成
            name="health_diagnosis",
            steps=steps,
            context={"user_id": user_id},
        )

        return await self.orchestrator.start_saga(saga)


class UserRegistrationSaga:
    """用户注册Saga示例"""

    def __init__(self, orchestrator: SagaOrchestrator):
        self.orchestrator = orchestrator

    async def create_registration_saga(self, user_data: dict[str, Any]) -> str:
        """创建用户注册Saga"""
        steps = [
            SagaStep(
                step_id="validate_user_data",
                service_name="user-service",
                action="validate_registration_data",
                compensation_action="no_compensation",
                input_data=user_data,
            ),
            SagaStep(
                step_id="create_user_account",
                service_name="user-service",
                action="create_user_account",
                compensation_action="delete_user_account",
                input_data=user_data,
            ),
            SagaStep(
                step_id="create_health_profile",
                service_name="health-data-service",
                action="create_health_profile",
                compensation_action="delete_health_profile",
                input_data={"user_id": user_data.get("user_id")},
            ),
            SagaStep(
                step_id="setup_blockchain_wallet",
                service_name="blockchain-service",
                action="create_wallet",
                compensation_action="delete_wallet",
                input_data={"user_id": user_data.get("user_id")},
            ),
            SagaStep(
                step_id="send_welcome_email",
                service_name="notification-service",
                action="send_welcome_email",
                compensation_action="no_compensation",
                input_data=user_data,
            ),
        ]

        saga = SagaTransaction(
            saga_id="",
            name="user_registration",
            steps=steps,
            context={"user_data": user_data},
        )

        return await self.orchestrator.start_saga(saga)
