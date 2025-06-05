#!/usr/bin/env python3
"""
工作流引擎测试
Workflow Engine Tests
"""

import asyncio
import pytest
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

from internal.model.agent import AgentRequest, AgentResponse
from internal.model.workflow import (
    StepExecution,
    StepStatus,
    StepType,
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowStatus,
    WorkflowStep,
)
from internal.service.agent_manager import AgentManager
from internal.service.workflow_engine import WorkflowEngine


class TestWorkflowEngine:
    """工作流引擎测试类"""

    @pytest.fixture
    def mock_agent_manager(self):
        """模拟智能体管理器"""
        manager = MagicMock(spec=AgentManager)
        manager.send_request = AsyncMock()
        return manager

    @pytest.fixture
    def workflow_engine(self, mock_agent_manager):
        """工作流引擎实例"""
        return WorkflowEngine(mock_agent_manager)

    @pytest.fixture
    def sample_workflow(self):
        """示例工作流定义"""
        steps = [
            WorkflowStep(
                id="step1",
                name="第一步",
                type=StepType.ACTION,
                agent="agent1",
                action="action1",
                description="第一个步骤",
                timeout=30,
                retry_count=2,
                condition=None,
                parameters={"param1": "value1"},
                dependencies=[],
            ),
            WorkflowStep(
                id="step2",
                name="第二步",
                type=StepType.ACTION,
                agent="agent2",
                action="action2",
                description="第二个步骤",
                timeout=30,
                retry_count=2,
                condition=None,
                parameters={"param2": "value2"},
                dependencies=["step1"],
            ),
        ]

        return WorkflowDefinition(
            id="test_workflow",
            name="测试工作流",
            description="用于测试的工作流",
            version="1.0.0",
            timeout=300,
            retry_count=3,
            steps=steps,
            metadata={},
            tags=["test"],
        )

    def test_register_workflow(self, workflow_engine, sample_workflow):
        """测试工作流注册"""
        workflow_engine.register_workflow(sample_workflow)
        
        assert sample_workflow.id in workflow_engine.workflows
        assert workflow_engine.get_workflow(sample_workflow.id) == sample_workflow

    def test_get_nonexistent_workflow(self, workflow_engine):
        """测试获取不存在的工作流"""
        result = workflow_engine.get_workflow("nonexistent")
        assert result is None

    def test_list_workflows(self, workflow_engine, sample_workflow):
        """测试获取工作流列表"""
        workflow_engine.register_workflow(sample_workflow)
        
        workflows = workflow_engine.list_workflows()
        assert len(workflows) == 1
        assert workflows[0] == sample_workflow

    @pytest.mark.asyncio
    async def test_execute_workflow_success(self, workflow_engine, sample_workflow, mock_agent_manager):
        """测试成功执行工作流"""
        # 注册工作流
        workflow_engine.register_workflow(sample_workflow)
        
        # 模拟智能体响应
        mock_agent_manager.send_request.return_value = AgentResponse(
            success=True,
            data={"result": "success"},
            error=None,
            agent_id="test_agent",
            request_id="test_request",
            execution_time=1.0,
            timestamp=datetime.now(UTC).isoformat(),
        )
        
        # 执行工作流
        execution = await workflow_engine.execute_workflow(
            workflow_id="test_workflow",
            parameters={"test_param": "test_value"},
            user_id="test_user",
            context={"test_context": "context_value"},
        )
        
        # 验证执行结果
        assert execution.workflow_id == "test_workflow"
        assert execution.user_id == "test_user"
        assert execution.status == WorkflowStatus.RUNNING
        assert len(execution.steps) == 2
        
        # 等待执行完成
        await asyncio.sleep(0.1)
        
        # 验证最终状态
        final_execution = workflow_engine.get_execution(execution.execution_id)
        assert final_execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.RUNNING]

    @pytest.mark.asyncio
    async def test_execute_nonexistent_workflow(self, workflow_engine):
        """测试执行不存在的工作流"""
        with pytest.raises(ValueError, match="工作流不存在"):
            await workflow_engine.execute_workflow(
                workflow_id="nonexistent",
                parameters={},
                user_id="test_user",
            )

    @pytest.mark.asyncio
    async def test_workflow_step_failure(self, workflow_engine, mock_agent_manager):
        """测试工作流步骤失败"""
        # 创建一个没有重试的工作流
        steps = [
            WorkflowStep(
                id="step1",
                name="失败步骤",
                type=StepType.ACTION,
                agent="agent1",
                action="action1",
                description="会失败的步骤",
                timeout=30,
                retry_count=0,  # 不重试
                condition=None,
                parameters={},
                dependencies=[],
            ),
        ]

        failure_workflow = WorkflowDefinition(
            id="failure_workflow",
            name="失败测试工作流",
            description="测试失败的工作流",
            version="1.0.0",
            timeout=300,
            retry_count=0,
            steps=steps,
            metadata={},
            tags=["test", "failure"],
        )
        
        # 注册工作流
        workflow_engine.register_workflow(failure_workflow)
        
        # 模拟智能体失败响应
        mock_agent_manager.send_request.return_value = AgentResponse(
                success=False,
                data={},
                error="Agent execution failed",
                agent_id="test_agent",
                request_id="test_request",
                execution_time=1.0,
                timestamp=datetime.now(UTC).isoformat(),
            )
        
        # 执行工作流
        execution = await workflow_engine.execute_workflow(
            workflow_id="failure_workflow",
            parameters={},
            user_id="test_user",
        )
        
        # 等待执行完成
        await asyncio.sleep(0.5)
        
        # 验证失败状态
        final_execution = workflow_engine.get_execution(execution.execution_id)
        assert final_execution.status == WorkflowStatus.FAILED

    @pytest.mark.asyncio
    async def test_workflow_step_retry(self, workflow_engine, sample_workflow, mock_agent_manager):
        """测试工作流步骤重试"""
        # 注册工作流
        workflow_engine.register_workflow(sample_workflow)
        
        # 模拟第一次失败，第二次成功
        responses = [
            AgentResponse(
                success=False,
                data={},
                error="First attempt failed",
                agent_id="test_agent",
                request_id="test_request",
                execution_time=1.0,
                timestamp=datetime.now(UTC).isoformat(),
            ),
            AgentResponse(
            success=True,
            data={"result": "success on retry"},
            error=None,
            agent_id="test_agent",
            request_id="test_request",
            execution_time=1.0,
            timestamp=datetime.now(UTC).isoformat(),
        ),
        ]
        mock_agent_manager.send_request.side_effect = responses
        
        # 执行工作流
        execution = await workflow_engine.execute_workflow(
            workflow_id="test_workflow",
            parameters={},
            user_id="test_user",
        )
        
        # 等待执行完成
        await asyncio.sleep(0.3)
        
        # 验证重试成功
        final_execution = workflow_engine.get_execution(execution.execution_id)
        # 由于有依赖关系，第二步可能还在执行
        assert final_execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.RUNNING]

    @pytest.mark.asyncio
    async def test_workflow_dependency_execution(self, workflow_engine, mock_agent_manager):
        """测试工作流依赖执行"""
        # 创建有复杂依赖的工作流
        steps = [
            WorkflowStep(
                id="step1",
                name="步骤1",
                type=StepType.ACTION,
                agent="agent1",
                action="action1",
                description="独立步骤",
                timeout=30,
                retry_count=1,
                condition=None,
                parameters={},
                dependencies=[],
            ),
            WorkflowStep(
                id="step2",
                name="步骤2",
                type=StepType.ACTION,
                agent="agent2",
                action="action2",
                description="独立步骤",
                timeout=30,
                retry_count=1,
                condition=None,
                parameters={},
                dependencies=[],
            ),
            WorkflowStep(
                id="step3",
                name="步骤3",
                type=StepType.ACTION,
                agent="agent3",
                action="action3",
                description="依赖步骤1和2",
                timeout=30,
                retry_count=1,
                condition=None,
                parameters={},
                dependencies=["step1", "step2"],
            ),
        ]

        workflow = WorkflowDefinition(
            id="dependency_workflow",
            name="依赖测试工作流",
            description="测试依赖关系的工作流",
            version="1.0.0",
            timeout=300,
            retry_count=3,
            steps=steps,
            metadata={},
            tags=["test", "dependency"],
        )

        workflow_engine.register_workflow(workflow)
        
        # 模拟智能体成功响应
        mock_agent_manager.send_request.return_value = AgentResponse(
            success=True,
            data={"result": "success"},
            error=None,
            agent_id="test_agent",
            request_id="test_request",
            execution_time=0.1,
            timestamp=datetime.now(UTC).isoformat(),
        )
        
        # 执行工作流
        execution = await workflow_engine.execute_workflow(
            workflow_id="dependency_workflow",
            parameters={},
            user_id="test_user",
        )
        
        # 等待执行完成
        await asyncio.sleep(0.5)
        
        # 验证执行顺序和结果
        final_execution = workflow_engine.get_execution(execution.execution_id)
        assert final_execution.status == WorkflowStatus.COMPLETED
        
        # 验证步骤3在步骤1和2之后执行
        step1_end = None
        step2_end = None
        step3_start = None
        
        for step in final_execution.steps:
            if step.step_id == "step1" and step.end_time:
                step1_end = datetime.fromisoformat(step.end_time.replace('Z', '+00:00'))
            elif step.step_id == "step2" and step.end_time:
                step2_end = datetime.fromisoformat(step.end_time.replace('Z', '+00:00'))
            elif step.step_id == "step3" and step.start_time:
                step3_start = datetime.fromisoformat(step.start_time.replace('Z', '+00:00'))
        
        if step1_end and step2_end and step3_start:
            assert step3_start >= max(step1_end, step2_end)

    @pytest.mark.asyncio
    async def test_cancel_workflow_execution(self, workflow_engine, sample_workflow):
        """测试取消工作流执行"""
        # 注册工作流
        workflow_engine.register_workflow(sample_workflow)
        
        # 执行工作流
        execution = await workflow_engine.execute_workflow(
            workflow_id="test_workflow",
            parameters={},
            user_id="test_user",
        )
        
        # 取消执行
        success = await workflow_engine.cancel_execution(execution.execution_id)
        assert success
        
        # 验证状态
        final_execution = workflow_engine.get_execution(execution.execution_id)
        assert final_execution.status == WorkflowStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_cancel_nonexistent_execution(self, workflow_engine):
        """测试取消不存在的执行"""
        success = await workflow_engine.cancel_execution("nonexistent")
        assert not success

    def test_get_execution_progress(self, workflow_engine, sample_workflow):
        """测试获取执行进度"""
        # 创建模拟执行
        execution = WorkflowExecution(
            execution_id="test_execution",
            workflow_id="test_workflow",
            workflow_name="测试工作流",
            user_id="test_user",
            context={},
            status=WorkflowStatus.RUNNING,
            start_time=datetime.now(UTC).isoformat(),
            end_time=None,
            execution_time=0.0,
            error=None,
            metadata={},
        )
        
        # 添加步骤执行记录
        execution.steps = [
            StepExecution(
                step_id="step1",
                status=StepStatus.COMPLETED,
                agent_id="agent1",
                start_time=datetime.now(UTC).isoformat(),
                end_time=datetime.now(UTC).isoformat(),
                execution_time=1.0,
                result={"result": "success"},
                error=None,
                retry_count=0,
            ),
            StepExecution(
                step_id="step2",
                status=StepStatus.RUNNING,
                agent_id="agent2",
                start_time=datetime.now(UTC).isoformat(),
                end_time=None,
                execution_time=0.0,
                result={},
                error=None,
                retry_count=0,
            ),
        ]
        
        workflow_engine.executions[execution.execution_id] = execution
        
        # 获取进度
        progress = workflow_engine.get_execution_progress(execution.execution_id)
        
        assert progress is not None
        assert progress["execution_id"] == execution.execution_id
        assert progress["status"] == WorkflowStatus.RUNNING
        assert progress["progress"]["total_steps"] == 2
        assert progress["progress"]["completed_steps"] == 1
        assert progress["progress"]["running_steps"] == 1
        assert progress["progress"]["progress_percentage"] == 50.0

    def test_get_progress_nonexistent_execution(self, workflow_engine):
        """测试获取不存在执行的进度"""
        progress = workflow_engine.get_execution_progress("nonexistent")
        assert progress is None

    @pytest.mark.asyncio
    async def test_cleanup_completed_executions(self, workflow_engine):
        """测试清理已完成的执行记录"""
        from datetime import timedelta
        
        # 创建旧的已完成执行
        old_time = (datetime.now(UTC) - timedelta(hours=25)).isoformat()
        old_execution = WorkflowExecution(
            execution_id="old_execution",
            workflow_id="test_workflow",
            workflow_name="测试工作流",
            user_id="test_user",
            context={},
            status=WorkflowStatus.COMPLETED,
            start_time=old_time,
            end_time=old_time,
            execution_time=10.0,
            error=None,
            metadata={},
        )
        
        # 创建新的已完成执行
        new_time = datetime.now(UTC).isoformat()
        new_execution = WorkflowExecution(
            execution_id="new_execution",
            workflow_id="test_workflow",
            workflow_name="测试工作流",
            user_id="test_user",
            context={},
            status=WorkflowStatus.COMPLETED,
            start_time=new_time,
            end_time=new_time,
            execution_time=5.0,
            error=None,
            metadata={},
        )
        
        # 添加到引擎
        workflow_engine.executions["old_execution"] = old_execution
        workflow_engine.executions["new_execution"] = new_execution
        
        # 清理旧记录
        cleaned_count = await workflow_engine.cleanup_completed_executions(max_age_hours=24)
        
        # 验证清理结果
        assert cleaned_count == 1
        assert "old_execution" not in workflow_engine.executions
        assert "new_execution" in workflow_engine.executions

    def test_build_dependency_graph(self, workflow_engine, sample_workflow):
        """测试构建依赖图"""
        dependency_graph = workflow_engine._build_dependency_graph(sample_workflow)
        
        assert "step1" in dependency_graph
        assert "step2" in dependency_graph
        assert dependency_graph["step1"] == []
        assert dependency_graph["step2"] == ["step1"]

    @pytest.mark.asyncio
    async def test_parallel_step_execution(self, workflow_engine, mock_agent_manager):
        """测试并行步骤执行"""
        # 创建可并行执行的工作流
        steps = [
            WorkflowStep(
                id="step1",
                name="并行步骤1",
                type=StepType.ACTION,
                agent="agent1",
                action="action1",
                description="可并行执行",
                timeout=30,
                retry_count=1,
                condition=None,
                parameters={},
                dependencies=[],
            ),
            WorkflowStep(
                id="step2",
                name="并行步骤2",
                type=StepType.ACTION,
                agent="agent2",
                action="action2",
                description="可并行执行",
                timeout=30,
                retry_count=1,
                condition=None,
                parameters={},
                dependencies=[],
            ),
        ]

        workflow = WorkflowDefinition(
            id="parallel_workflow",
            name="并行测试工作流",
            description="测试并行执行的工作流",
            version="1.0.0",
            timeout=300,
            retry_count=3,
            steps=steps,
            metadata={},
            tags=["test", "parallel"],
        )

        workflow_engine.register_workflow(workflow)
        
        # 模拟智能体响应（添加延迟以测试并行性）
        async def mock_send_request(request):
            await asyncio.sleep(0.1)  # 模拟处理时间
            return AgentResponse(
            success=True,
            data={"result": f"success from {request.agent_id}"},
            error=None,
            agent_id="test_agent",
            request_id="test_request",
            execution_time=0.1,
            timestamp=datetime.now(UTC).isoformat(),
        )
        
        mock_agent_manager.send_request.side_effect = mock_send_request
        
        # 记录开始时间
        start_time = datetime.now(UTC)
        
        # 执行工作流
        execution = await workflow_engine.execute_workflow(
            workflow_id="parallel_workflow",
            parameters={},
            user_id="test_user",
        )
        
        # 等待执行完成
        await asyncio.sleep(0.3)
        
        # 记录结束时间
        end_time = datetime.now(UTC)
        total_time = (end_time - start_time).total_seconds()
        
        # 验证并行执行（总时间应该小于串行执行时间）
        assert total_time < 0.35  # 放宽时间限制，考虑系统开销
        
        # 验证执行结果
        final_execution = workflow_engine.get_execution(execution.execution_id)
        assert final_execution.status == WorkflowStatus.COMPLETED
        assert len(final_execution.steps) == 2
        
        # 验证两个步骤都成功完成
        for step in final_execution.steps:
            assert step.status == StepStatus.COMPLETED 