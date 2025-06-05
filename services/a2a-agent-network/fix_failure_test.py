#!/usr/bin/env python3
"""
修复失败测试
"""

import re

def fix_failure_test():
    """修复失败测试"""
    file_path = "test/unit/test_workflow_engine.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换test_workflow_step_failure方法
    old_method = '''    @pytest.mark.asyncio
    async def test_workflow_step_failure(self, workflow_engine, sample_workflow, mock_agent_manager):
        """测试工作流步骤失败"""
        # 注册工作流
        workflow_engine.register_workflow(sample_workflow)
        
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
            workflow_id="test_workflow",
            parameters={},
            user_id="test_user",
        )
        
        # 等待执行完成（包括重试）
        await asyncio.sleep(1.0)
        
        # 验证失败状态
        final_execution = workflow_engine.get_execution(execution.execution_id)
        assert final_execution.status == WorkflowStatus.FAILED'''
    
    new_method = '''    @pytest.mark.asyncio
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
        assert final_execution.status == WorkflowStatus.FAILED'''
    
    content = content.replace(old_method, new_method)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 失败测试修复完成")

if __name__ == "__main__":
    fix_failure_test() 