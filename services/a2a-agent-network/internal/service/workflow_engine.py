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

from ..model.agent import AgentRequest
from ..model.workflow import (
    StepExecution,
    StepStatus,
    StepType,
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowStatus,
)
from .agent_manager import AgentManager
from .condition_evaluator import ConditionEvaluator, LoopController

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """工作流引擎"""

    def __init__(self, agent_manager: AgentManager) -> None:
        """
        初始化工作流引擎

        Args:
            agent_manager: 智能体管理器
        """
        self.agent_manager = agent_manager
        self.workflows: dict[str, WorkflowDefinition] = {}
        self.executions: dict[str, WorkflowExecution] = {}
        self._execution_tasks: dict[str, asyncio.Task] = {}
        
        # 条件评估器和循环控制器
        self.condition_evaluator = ConditionEvaluator()
        self.loop_controller = LoopController(self.condition_evaluator)

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
            workflow_name=workflow.name,
            user_id=user_id,
            context=context or {},
            status=WorkflowStatus.RUNNING,
            start_time=datetime.now(UTC).isoformat(),
            end_time=None,
            execution_time=0.0,
            error=None,
            metadata={"parameters": parameters},
        )

        # 初始化步骤执行记录
        for step in workflow.steps:
            step_execution = StepExecution(
                step_id=step.id,
                status=StepStatus.PENDING,
                agent_id=step.agent,
                start_time=None,
                end_time=None,
                execution_time=0.0,
                result={},
                error=None,
                retry_count=0,
            )
            execution.steps.append(step_execution)

        self.executions[execution_id] = execution
        logger.info(f"开始执行工作流: {workflow_id}, 执行ID: {execution_id}")

        # 异步执行工作流
        task = asyncio.create_task(self._execute_workflow_async(execution, workflow))
        self._execution_tasks[execution_id] = task

        return execution

    async def _execute_workflow_async(
        self, execution: WorkflowExecution, workflow: WorkflowDefinition
    ) -> None:
        """
        异步执行工作流

        Args:
            execution: 工作流执行实例
            workflow: 工作流定义
        """
        start_time = datetime.now(UTC)
        
        try:
            # 构建依赖图
            dependency_graph = self._build_dependency_graph(workflow)
            
            # 按依赖顺序执行步骤
            await self._execute_steps_with_dependencies(execution, workflow, dependency_graph)
            
            # 检查执行结果
            failed_steps = [step for step in execution.steps if step.status == StepStatus.FAILED]
            
            if failed_steps:
                execution.status = WorkflowStatus.FAILED
                execution.error = f"步骤执行失败: {[step.step_id for step in failed_steps]}"
                logger.error(f"工作流执行失败: {execution.workflow_id}, 失败步骤: {[step.step_id for step in failed_steps]}")
            else:
                execution.status = WorkflowStatus.COMPLETED
                logger.info(f"工作流执行完成: {execution.workflow_id}")

        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error = str(e)
            logger.error(f"工作流执行异常: {execution.workflow_id}, 错误: {e}")

        finally:
            execution.end_time = datetime.now(UTC).isoformat()
            execution.execution_time = (datetime.now(UTC) - start_time).total_seconds()
            
            # 清理任务
            if execution.execution_id in self._execution_tasks:
                del self._execution_tasks[execution.execution_id]

    def _build_dependency_graph(self, workflow: WorkflowDefinition) -> dict[str, list[str]]:
        """
        构建步骤依赖图

        Args:
            workflow: 工作流定义

        Returns:
            依赖图字典
        """
        dependency_graph = {}
        
        for step in workflow.steps:
            dependency_graph[step.id] = step.dependencies.copy()
        
        return dependency_graph

    async def _execute_steps_with_dependencies(
        self,
        execution: WorkflowExecution,
        workflow: WorkflowDefinition,
        dependency_graph: dict[str, list[str]]
    ) -> None:
        """
        按依赖关系执行步骤

        Args:
            execution: 工作流执行实例
            workflow: 工作流定义
            dependency_graph: 依赖图
        """
        completed_steps = set()
        step_map = {step.id: step for step in workflow.steps}
        step_execution_map = {step.step_id: step for step in execution.steps}
        
        while len(completed_steps) < len(workflow.steps):
            # 找到可以执行的步骤（依赖已完成）
            ready_steps = []
            
            for step_id, dependencies in dependency_graph.items():
                if step_id not in completed_steps:
                    if all(dep in completed_steps for dep in dependencies):
                        ready_steps.append(step_id)
            
            if not ready_steps:
                # 检查是否有循环依赖或其他问题
                remaining_steps = set(dependency_graph.keys()) - completed_steps
                raise RuntimeError(f"无法继续执行，剩余步骤: {remaining_steps}")
            
            # 并行执行准备好的步骤
            tasks = []
            for step_id in ready_steps:
                step = step_map[step_id]
                step_execution = step_execution_map[step_id]
                task = asyncio.create_task(
                    self._execute_single_step(execution, step, step_execution)
                )
                tasks.append((step_id, task))
            
            # 等待所有步骤完成
            for step_id, task in tasks:
                try:
                    await task
                    completed_steps.add(step_id)
                except Exception as e:
                    logger.error(f"步骤 {step_id} 执行失败: {e}")
                    step_execution_map[step_id].status = StepStatus.FAILED
                    step_execution_map[step_id].error = str(e)
                    completed_steps.add(step_id)  # 标记为已完成（虽然失败）
                    
                    # 如果步骤失败，停止整个工作流
                    raise Exception(f"工作流因步骤 {step_id} 失败而终止: {e}")

    async def _execute_single_step(
        self,
        execution: WorkflowExecution,
        step: Any,  # WorkflowStep from workflow model
        step_execution: StepExecution
    ) -> None:
        """
        执行单个步骤

        Args:
            execution: 工作流执行实例
            step: 工作流步骤定义
            step_execution: 步骤执行记录
        """
        step_execution.status = StepStatus.RUNNING
        step_execution.start_time = datetime.now(UTC).isoformat()
        
        logger.info(f"开始执行步骤: {step.id} (类型: {step.type})")
        
        try:
            # 检查执行条件
            if step.condition and not self.condition_evaluator.evaluate(step.condition, execution.context):
                step_execution.status = StepStatus.SKIPPED
                step_execution.end_time = datetime.now(UTC).isoformat()
                logger.info(f"步骤 {step.id} 因条件不满足被跳过")
                return

            # 根据步骤类型执行不同逻辑
            if step.type == StepType.ACTION:
                await self._execute_action_step(execution, step, step_execution)
            elif step.type == StepType.CONDITION:
                await self._execute_condition_step(execution, step, step_execution)
            elif step.type == StepType.LOOP:
                await self._execute_loop_step(execution, step, step_execution)
            elif step.type == StepType.PARALLEL:
                await self._execute_parallel_step(execution, step, step_execution)
            elif step.type == StepType.WAIT:
                await self._execute_wait_step(execution, step, step_execution)
            else:
                raise ValueError(f"不支持的步骤类型: {step.type}")

        except Exception as e:
            step_execution.status = StepStatus.FAILED
            step_execution.error = str(e)
            step_execution.end_time = datetime.now(UTC).isoformat()
            logger.error(f"步骤 {step.id} 执行失败: {e}")
            raise

    async def _execute_action_step(
        self,
        execution: WorkflowExecution,
        step: Any,
        step_execution: StepExecution
    ) -> None:
        """执行动作步骤"""
        if not step.agent or not step.action:
            raise ValueError(f"动作步骤 {step.id} 缺少智能体或动作定义")

        max_retries = step.retry_count
        retry_count = 0
        
        while retry_count <= max_retries:
            try:
                # 准备请求参数
                request_params = step.parameters.copy()
                request_params.update(execution.context)
                
                # 创建智能体请求
                agent_request = AgentRequest(
                    agent_id=step.agent,
                    action=step.action,
                    parameters=request_params,
                    user_id=execution.user_id,
                    request_id=f"{execution.execution_id}_{step.id}",
                    timeout=step.timeout,
                )
                
                # 执行请求
                start_time = datetime.now(UTC)
                response = await self.agent_manager.send_request(agent_request)
                execution_time = (datetime.now(UTC) - start_time).total_seconds()
                
                if response.success:
                    step_execution.status = StepStatus.COMPLETED
                    step_execution.result = response.data
                    step_execution.execution_time = execution_time
                    step_execution.end_time = datetime.now(UTC).isoformat()
                    
                    # 将结果添加到执行上下文
                    execution.context[f"step_{step.id}_result"] = response.data
                    
                    logger.info(f"动作步骤 {step.id} 执行成功")
                    return
                else:
                    raise Exception(response.error or "智能体执行失败")
                    
            except Exception as e:
                retry_count += 1
                step_execution.retry_count = retry_count
                
                if retry_count <= max_retries:
                    logger.warning(f"动作步骤 {step.id} 执行失败，重试 {retry_count}/{max_retries}: {e}")
                    await asyncio.sleep(2 ** retry_count)  # 指数退避
                else:
                    raise

    async def _execute_condition_step(
        self,
        execution: WorkflowExecution,
        step: Any,
        step_execution: StepExecution
    ) -> None:
        """执行条件分支步骤"""
        if not step.condition:
            raise ValueError(f"条件步骤 {step.id} 缺少条件定义")

        # 评估条件
        condition_result = self.condition_evaluator.evaluate(step.condition, execution.context)
        
        step_execution.status = StepStatus.COMPLETED
        step_execution.result = {"condition_result": condition_result}
        step_execution.end_time = datetime.now(UTC).isoformat()
        
        # 将条件结果添加到上下文
        execution.context[f"step_{step.id}_condition"] = condition_result
        
        # 根据条件结果执行相应的步骤
        if condition_result and step.if_steps:
            execution.context[f"step_{step.id}_branch"] = "if"
            logger.info(f"条件步骤 {step.id} 条件为真，将执行 if 分支")
        elif not condition_result and step.else_steps:
            execution.context[f"step_{step.id}_branch"] = "else"
            logger.info(f"条件步骤 {step.id} 条件为假，将执行 else 分支")
        else:
            execution.context[f"step_{step.id}_branch"] = "none"
            logger.info(f"条件步骤 {step.id} 无匹配分支")

    async def _execute_loop_step(
        self,
        execution: WorkflowExecution,
        step: Any,
        step_execution: StepExecution
    ) -> None:
        """执行循环步骤"""
        if not step.loop_config:
            raise ValueError(f"循环步骤 {step.id} 缺少循环配置")

        iteration = 0
        loop_results = []
        
        while self.loop_controller.should_continue_loop(step.loop_config, execution.context, iteration):
            try:
                # 准备循环上下文
                loop_context = self.loop_controller.prepare_loop_context(
                    step.loop_config, execution.context, iteration
                )
                
                # 更新执行上下文
                original_context = execution.context.copy()
                execution.context.update(loop_context)
                
                # 执行循环体（这里简化处理，实际应该执行 loop_steps）
                iteration_result = {
                    "iteration": iteration,
                    "context": loop_context,
                    "timestamp": datetime.now(UTC).isoformat()
                }
                loop_results.append(iteration_result)
                
                # 恢复原始上下文
                execution.context = original_context
                
                iteration += 1
                
                # 避免无限循环
                if iteration > 1000:
                    logger.warning(f"循环步骤 {step.id} 达到最大迭代次数限制")
                    break
                    
            except Exception as e:
                if step.loop_config.break_on_error:
                    logger.error(f"循环步骤 {step.id} 在第 {iteration} 次迭代时出错，中断循环: {e}")
                    break
                else:
                    logger.warning(f"循环步骤 {step.id} 在第 {iteration} 次迭代时出错，继续循环: {e}")
                    iteration += 1

        step_execution.status = StepStatus.COMPLETED
        step_execution.result = {
            "total_iterations": iteration,
            "loop_results": loop_results
        }
        step_execution.end_time = datetime.now(UTC).isoformat()
        
        # 将循环结果添加到上下文
        execution.context[f"step_{step.id}_iterations"] = iteration
        execution.context[f"step_{step.id}_results"] = loop_results
        
        logger.info(f"循环步骤 {step.id} 执行完成，共 {iteration} 次迭代")

    async def _execute_parallel_step(
        self,
        execution: WorkflowExecution,
        step: Any,
        step_execution: StepExecution
    ) -> None:
        """执行并行步骤"""
        if not step.parallel_steps:
            raise ValueError(f"并行步骤 {step.id} 缺少并行步骤定义")

        # 这里简化处理，实际应该并行执行 parallel_steps
        step_execution.status = StepStatus.COMPLETED
        step_execution.result = {
            "parallel_steps": step.parallel_steps,
            "execution_mode": "parallel"
        }
        step_execution.end_time = datetime.now(UTC).isoformat()
        
        execution.context[f"step_{step.id}_parallel_completed"] = True
        
        logger.info(f"并行步骤 {step.id} 执行完成")

    async def _execute_wait_step(
        self,
        execution: WorkflowExecution,
        step: Any,
        step_execution: StepExecution
    ) -> None:
        """执行等待步骤"""
        if step.wait_duration:
            # 等待指定时间
            logger.info(f"等待步骤 {step.id} 等待 {step.wait_duration} 秒")
            await asyncio.sleep(step.wait_duration)
        elif step.wait_condition:
            # 等待条件满足
            max_wait_time = step.timeout
            wait_interval = 1  # 每秒检查一次
            waited_time = 0
            
            while waited_time < max_wait_time:
                if self.condition_evaluator.evaluate(step.wait_condition, execution.context):
                    logger.info(f"等待步骤 {step.id} 条件已满足")
                    break
                
                await asyncio.sleep(wait_interval)
                waited_time += wait_interval
            else:
                raise TimeoutError(f"等待步骤 {step.id} 超时")
        else:
            raise ValueError(f"等待步骤 {step.id} 缺少等待时间或等待条件")

        step_execution.status = StepStatus.COMPLETED
        step_execution.result = {"wait_completed": True}
        step_execution.end_time = datetime.now(UTC).isoformat()
        
        execution.context[f"step_{step.id}_wait_completed"] = True
        
        logger.info(f"等待步骤 {step.id} 执行完成")

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

        # 取消执行任务
        if execution_id in self._execution_tasks:
            task = self._execution_tasks[execution_id]
            task.cancel()
            del self._execution_tasks[execution_id]

        execution.status = WorkflowStatus.CANCELLED
        execution.end_time = datetime.now(UTC).isoformat()

        logger.info(f"工作流执行已取消: {execution_id}")
        return True

    def get_execution_progress(self, execution_id: str) -> dict[str, Any] | None:
        """
        获取工作流执行进度

        Args:
            execution_id: 执行ID

        Returns:
            执行进度信息
        """
        execution = self.get_execution(execution_id)
        if not execution:
            return None

        total_steps = len(execution.steps)
        completed_steps = len([s for s in execution.steps if s.status == StepStatus.COMPLETED])
        failed_steps = len([s for s in execution.steps if s.status == StepStatus.FAILED])
        running_steps = len([s for s in execution.steps if s.status == StepStatus.RUNNING])

        return {
            "execution_id": execution_id,
            "status": execution.status,
            "progress": {
                "total_steps": total_steps,
                "completed_steps": completed_steps,
                "failed_steps": failed_steps,
                "running_steps": running_steps,
                "progress_percentage": (completed_steps / total_steps * 100) if total_steps > 0 else 0,
            },
            "current_steps": [
                {
                    "step_id": step.step_id,
                    "status": step.status,
                    "agent_id": step.agent_id,
                    "execution_time": step.execution_time,
                }
                for step in execution.steps
            ],
        }

    async def cleanup_completed_executions(self, max_age_hours: int = 24) -> int:
        """
        清理已完成的工作流执行记录

        Args:
            max_age_hours: 最大保留时间（小时）

        Returns:
            清理的记录数
        """
        from datetime import timedelta

        cutoff_time = datetime.now(UTC) - timedelta(hours=max_age_hours)
        cleaned_count = 0

        execution_ids_to_remove = []
        for execution_id, execution in self.executions.items():
            if execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
                if execution.end_time:
                    end_time = datetime.fromisoformat(execution.end_time.replace('Z', '+00:00'))
                    if end_time < cutoff_time:
                        execution_ids_to_remove.append(execution_id)

        for execution_id in execution_ids_to_remove:
            del self.executions[execution_id]
            cleaned_count += 1

        if cleaned_count > 0:
            logger.info(f"清理了 {cleaned_count} 个已完成的工作流执行记录")

        return cleaned_count
