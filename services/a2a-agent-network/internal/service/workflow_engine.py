#!/usr/bin/env python3
"""
工作流引擎
Workflow Engine
"""

import asyncio
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from ..model.workflow import WorkflowDefinition, WorkflowExecution, WorkflowStatus
from .agent_manager import AgentManager

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """工作流引擎"""

    def __init__(self, agent_manager: AgentManager):
        """
        初始化工作流引擎

        Args:
            agent_manager: 智能体管理器
        """
        self.agent_manager = agent_manager
        self.workflows: dict[str, WorkflowDefinition] = {}
        self.executions: dict[str, WorkflowExecution] = {}

        logger.info("工作流引擎初始化完成")

    def register_workflow(self, workflow: WorkflowDefinition) -> None:
        """
        注册工作流定义

        Args:
            workflow: 工作流定义
        """
        self.workflows[workflow.id] = workflow
        logger.info(f"工作流已注册: {workflow.id}")

    def get_workflow(self, workflow_id: str) -> WorkflowDefinition | None:
        """
        获取工作流定义

        Args:
            workflow_id: 工作流ID

        Returns:
            工作流定义或None
        """
        return self.workflows.get(workflow_id)

    def list_workflows(self) -> list[WorkflowDefinition]:
        """
        获取所有工作流定义

        Returns:
            工作流定义列表
        """
        return list(self.workflows.values())

    async def execute_workflow(
        self,
        workflow_id: str,
        parameters: dict[str, Any],
        user_id: str,
        context: dict[str, Any] | None = None,
    ) -> WorkflowExecution:
        """
        执行工作流

        Args:
            workflow_id: 工作流ID
            parameters: 执行参数
            user_id: 用户ID
            context: 执行上下文

        Returns:
            工作流执行实例
        """
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"工作流不存在: {workflow_id}")

        execution_id = str(uuid.uuid4())
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow_id,
            workflow_name=workflow.name if workflow else workflow_id,
            user_id=user_id,
            context=context or {},
            status=WorkflowStatus.RUNNING,
            start_time=datetime.now(UTC).isoformat(),
            metadata={"parameters": parameters},
        )

        self.executions[execution_id] = execution
        logger.info(f"开始执行工作流: {workflow_id}, 执行ID: {execution_id}")

        try:
            # 异步执行工作流步骤
            asyncio.create_task(self._execute_workflow_steps(execution, workflow))
            return execution
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error = str(e)
            execution.end_time = datetime.now(UTC).isoformat()
            logger.error(f"工作流执行失败: {workflow_id}, 错误: {e}")
            raise

    async def _execute_workflow_steps(
        self, execution: WorkflowExecution, workflow: WorkflowDefinition
    ) -> None:
        """
        执行工作流步骤

        Args:
            execution: 工作流执行实例
            workflow: 工作流定义
        """
        try:
            for step in workflow.steps:
                logger.info(f"执行步骤: {step.id}")

                # 这里应该调用相应的智能体执行步骤
                # 目前是简化实现
                await asyncio.sleep(0.1)  # 模拟执行时间

                # 更新当前步骤（这里需要扩展模型来支持）
                # execution.current_step = step.id

            execution.status = WorkflowStatus.COMPLETED
            execution.end_time = datetime.now(UTC).isoformat()

            logger.info(f"工作流执行完成: {execution.workflow_id}")

        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error = str(e)
            execution.end_time = datetime.now(UTC).isoformat()
            logger.error(f"工作流步骤执行失败: {e}")

    def get_execution(self, execution_id: str) -> WorkflowExecution | None:
        """
        获取工作流执行实例

        Args:
            execution_id: 执行ID

        Returns:
            工作流执行实例或None
        """
        return self.executions.get(execution_id)

    def list_executions(self, user_id: str | None = None) -> list[WorkflowExecution]:
        """
        获取工作流执行列表

        Args:
            user_id: 用户ID（可选，用于过滤）

        Returns:
            工作流执行列表
        """
        executions = list(self.executions.values())
        if user_id:
            executions = [e for e in executions if e.user_id == user_id]
        return executions

    async def cancel_execution(self, execution_id: str) -> bool:
        """
        取消工作流执行

        Args:
            execution_id: 执行ID

        Returns:
            是否成功取消
        """
        execution = self.get_execution(execution_id)
        if not execution:
            return False

        if execution.status in [
            WorkflowStatus.COMPLETED,
            WorkflowStatus.FAILED,
            WorkflowStatus.CANCELLED,
        ]:
            return False

        execution.status = WorkflowStatus.CANCELLED
        execution.end_time = datetime.now(UTC).isoformat()

        logger.info(f"工作流执行已取消: {execution_id}")
        return True
