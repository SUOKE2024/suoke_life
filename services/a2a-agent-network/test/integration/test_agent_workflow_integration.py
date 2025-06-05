#!/usr/bin/env python3
"""
智能体和工作流集成测试
Agent and Workflow Integration Tests
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest
import aiohttp

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from internal.model.agent import AgentInfo, AgentStatus
from internal.model.workflow import WorkflowDefinition, WorkflowStep
from internal.service.agent_manager import AgentManager
from internal.service.workflow_engine import WorkflowEngine


class TestAgentWorkflowIntegration:
    """智能体和工作流集成测试类"""

    @pytest.fixture
    def config(self):
        """测试配置"""
        return {
            "agents": {
                "xiaoai": {
                    "name": "小艾智能体",
                    "url": "http://localhost:5001",
                    "timeout": 30,
                    "retry_count": 3,
                    "health_check_interval": 60,
                    "capabilities": ["diagnosis", "consultation"],
                },
                "xiaoke": {
                    "name": "小克智能体",
                    "url": "http://localhost:5002",
                    "timeout": 30,
                    "retry_count": 3,
                    "health_check_interval": 60,
                    "capabilities": ["resource_management", "customization"],
                },
            }
        }

    @pytest.fixture
    async def agent_manager(self, config):
        """创建智能体管理器实例"""
        manager = AgentManager(config)
        await manager.start()
        yield manager
        await manager.stop()

    @pytest.fixture
    def workflow_engine(self, agent_manager):
        """创建工作流引擎实例"""
        return WorkflowEngine(agent_manager)

    @pytest.fixture
    def sample_workflow(self):
        """示例工作流定义"""
        steps = [
            WorkflowStep(
                id="step1",
                name="接收咨询",
                agent="xiaoai",
                action="receive_consultation",
                description="接收用户健康咨询",
                timeout=30,
                retry_count=2,
                parameters={"input_type": "text"},
                dependencies=[],
            ),
            WorkflowStep(
                id="step2",
                name="分析症状",
                agent="xiaoai",
                action="analyze_symptoms",
                description="分析用户症状",
                timeout=60,
                retry_count=2,
                parameters={"analysis_type": "comprehensive"},
                dependencies=["step1"],
            ),
            WorkflowStep(
                id="step3",
                name="资源调度",
                agent="xiaoke",
                action="schedule_resources",
                description="调度医疗资源",
                timeout=45,
                retry_count=2,
                parameters={"resource_type": "consultation"},
                dependencies=["step2"],
            ),
        ]

        return WorkflowDefinition(
            id="health_consultation",
            name="健康咨询工作流",
            description="完整的健康咨询处理流程",
            version="1.0.0",
            timeout=300,
            retry_count=2,
            steps=steps,
            metadata={"category": "health", "priority": "high"},
            tags=["health", "consultation"],
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_complete_workflow_execution(
        self, agent_manager, workflow_engine, sample_workflow
    ):
        """测试完整的工作流执行"""
        # 设置智能体为在线状态
        agent_manager.agents["xiaoai"].status = AgentStatus.ONLINE
        agent_manager.agents["xiaoke"].status = AgentStatus.ONLINE

        # 模拟智能体响应
        async def mock_send_request(request):
            from internal.model.agent import AgentResponse
            
            if request.action == "receive_consultation":
                return AgentResponse(
                    success=True,
                    data={"consultation_id": "cons_123", "status": "received"},
                    error=None,
                    agent_id=request.agent_id,
                    request_id=request.request_id,
                    execution_time=0.5,
                    timestamp="2024-01-15T10:30:00Z",
                )
            elif request.action == "analyze_symptoms":
                return AgentResponse(
                    success=True,
                    data={
                        "analysis": "轻度感冒症状",
                        "confidence": 0.85,
                        "recommendations": ["多休息", "多喝水"],
                    },
                    error=None,
                    agent_id=request.agent_id,
                    request_id=request.request_id,
                    execution_time=1.2,
                    timestamp="2024-01-15T10:30:01Z",
                )
            elif request.action == "schedule_resources":
                return AgentResponse(
                    success=True,
                    data={
                        "appointment_id": "apt_456",
                        "doctor": "张医生",
                        "time": "2024-01-16T14:00:00Z",
                    },
                    error=None,
                    agent_id=request.agent_id,
                    request_id=request.request_id,
                    execution_time=0.8,
                    timestamp="2024-01-15T10:30:02Z",
                )

        with patch.object(agent_manager, "send_request", side_effect=mock_send_request):
            # 注册工作流
            workflow_engine.register_workflow(sample_workflow)

            # 执行工作流
            execution = await workflow_engine.execute_workflow(
                workflow_id="health_consultation",
                parameters={"user_id": "user123", "symptoms": "头痛、发热"},
                user_id="user123",
                context={"session_id": "session_456"},
            )

            # 等待工作流完成
            await asyncio.sleep(2)

            # 验证执行结果
            assert execution.execution_id is not None
            assert execution.workflow_id == "health_consultation"
            assert execution.user_id == "user123"
            assert len(execution.steps) == 3

            # 检查最终状态
            final_execution = workflow_engine.get_execution(execution.execution_id)
            assert final_execution is not None
            
            # 验证所有步骤都已完成
            completed_steps = [
                step for step in final_execution.steps 
                if step.status.value == "completed"
            ]
            assert len(completed_steps) == 3

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_workflow_with_agent_failure(
        self, agent_manager, workflow_engine, sample_workflow
    ):
        """测试智能体失败时的工作流处理"""
        # 设置智能体状态
        agent_manager.agents["xiaoai"].status = AgentStatus.ONLINE
        agent_manager.agents["xiaoke"].status = AgentStatus.OFFLINE

        # 模拟智能体响应
        async def mock_send_request(request):
            from internal.model.agent import AgentResponse
            
            if request.agent_id == "xiaoai":
                return AgentResponse(
                    success=True,
                    data={"result": "success"},
                    error=None,
                    agent_id=request.agent_id,
                    request_id=request.request_id,
                    execution_time=0.5,
                    timestamp="2024-01-15T10:30:00Z",
                )
            else:  # xiaoke 离线
                return AgentResponse(
                    success=False,
                    data={},
                    error="智能体不在线",
                    agent_id=request.agent_id,
                    request_id=request.request_id,
                    execution_time=0.1,
                    timestamp="2024-01-15T10:30:00Z",
                )

        with patch.object(agent_manager, "send_request", side_effect=mock_send_request):
            # 注册工作流
            workflow_engine.register_workflow(sample_workflow)

            # 执行工作流
            execution = await workflow_engine.execute_workflow(
                workflow_id="health_consultation",
                parameters={"user_id": "user123", "symptoms": "头痛、发热"},
                user_id="user123",
            )

            # 等待工作流完成（包括重试时间）
            await asyncio.sleep(10)

            # 验证执行结果
            final_execution = workflow_engine.get_execution(execution.execution_id)
            assert final_execution is not None
            
            # 验证工作流失败
            from internal.model.workflow import WorkflowStatus
            assert final_execution.status == WorkflowStatus.FAILED
            assert final_execution.error is not None

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_concurrent_workflow_executions(
        self, agent_manager, workflow_engine, sample_workflow
    ):
        """测试并发工作流执行"""
        # 设置智能体为在线状态
        agent_manager.agents["xiaoai"].status = AgentStatus.ONLINE
        agent_manager.agents["xiaoke"].status = AgentStatus.ONLINE

        # 模拟智能体响应
        async def mock_send_request(request):
            from internal.model.agent import AgentResponse
            
            # 模拟处理时间
            await asyncio.sleep(0.1)
            
            return AgentResponse(
                success=True,
                data={"result": f"success_{request.request_id}"},
                error=None,
                agent_id=request.agent_id,
                request_id=request.request_id,
                execution_time=0.1,
                timestamp="2024-01-15T10:30:00Z",
            )

        with patch.object(agent_manager, "send_request", side_effect=mock_send_request):
            # 注册工作流
            workflow_engine.register_workflow(sample_workflow)

            # 并发执行多个工作流
            tasks = []
            for i in range(5):
                task = workflow_engine.execute_workflow(
                    workflow_id="health_consultation",
                    parameters={"user_id": f"user{i}", "symptoms": "头痛"},
                    user_id=f"user{i}",
                )
                tasks.append(task)

            executions = await asyncio.gather(*tasks)

            # 等待所有工作流完成
            await asyncio.sleep(3)

            # 验证所有执行都成功
            assert len(executions) == 5
            for execution in executions:
                assert execution.execution_id is not None
                final_execution = workflow_engine.get_execution(execution.execution_id)
                assert final_execution is not None

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_agent_health_check_integration(self, agent_manager):
        """测试智能体健康检查集成"""
        # 模拟健康检查响应
        mock_response = Mock()
        mock_response.status = 200
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        with patch("aiohttp.ClientSession.get", return_value=mock_response):
            # 执行健康检查
            health_check = await agent_manager._perform_health_check("xiaoai")

            # 验证结果
            assert health_check.agent_id == "xiaoai"
            assert health_check.status == AgentStatus.ONLINE
            assert health_check.response_time > 0
            assert health_check.error_message is None

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_agent_registration_integration(self, agent_manager):
        """测试智能体注册集成"""
        # 创建新智能体
        new_agent = AgentInfo(
            id="test_agent",
            name="测试智能体",
            description="用于测试的智能体",
            version="1.0.0",
            url="http://localhost:5999",
            status=AgentStatus.OFFLINE,
            last_heartbeat=None,
        )

        # 模拟连接测试
        with patch.object(agent_manager, "_test_agent_connection", return_value=True):
            # 注册智能体
            success = await agent_manager.register_agent(new_agent)

            # 验证注册成功
            assert success is True
            assert "test_agent" in agent_manager.agents
            assert agent_manager.agents["test_agent"].name == "测试智能体"

            # 注销智能体
            deregister_success = await agent_manager.deregister_agent("test_agent")
            assert deregister_success is True
            assert "test_agent" not in agent_manager.agents

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_workflow_progress_tracking(
        self, agent_manager, workflow_engine, sample_workflow
    ):
        """测试工作流进度跟踪"""
        # 设置智能体为在线状态
        agent_manager.agents["xiaoai"].status = AgentStatus.ONLINE
        agent_manager.agents["xiaoke"].status = AgentStatus.ONLINE

        # 模拟慢速智能体响应
        async def mock_send_request(request):
            from internal.model.agent import AgentResponse
            
            # 模拟处理时间
            await asyncio.sleep(0.5)
            
            return AgentResponse(
                success=True,
                data={"result": "success"},
                error=None,
                agent_id=request.agent_id,
                request_id=request.request_id,
                execution_time=0.5,
                timestamp="2024-01-15T10:30:00Z",
            )

        with patch.object(agent_manager, "send_request", side_effect=mock_send_request):
            # 注册工作流
            workflow_engine.register_workflow(sample_workflow)

            # 执行工作流
            execution = await workflow_engine.execute_workflow(
                workflow_id="health_consultation",
                parameters={"user_id": "user123", "symptoms": "头痛"},
                user_id="user123",
            )

            # 检查初始进度
            progress = workflow_engine.get_execution_progress(execution.execution_id)
            assert progress is not None
            assert progress["progress"]["total_steps"] == 3
            assert progress["progress"]["completed_steps"] == 0

            # 等待部分完成
            await asyncio.sleep(1)

            # 检查中间进度
            progress = workflow_engine.get_execution_progress(execution.execution_id)
            assert progress["progress"]["completed_steps"] > 0

            # 等待完全完成
            await asyncio.sleep(3)

            # 检查最终进度
            progress = workflow_engine.get_execution_progress(execution.execution_id)
            assert progress["progress"]["completed_steps"] == 3
            assert progress["progress"]["progress_percentage"] == 100.0 