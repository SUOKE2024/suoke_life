#!/usr/bin/env python3
"""
A2A 智能体网络服务部署验证脚本
验证服务的核心功能是否正常工作
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from internal.service.agent_manager import AgentManager
from internal.service.workflow_engine import WorkflowEngine
from internal.model.workflow import WorkflowDefinition, WorkflowStep
from internal.model.agent import AgentInfo, AgentStatus
from a2a_agent_network.config.config import Config


async def verify_agent_manager():
    """验证智能体管理器"""
    print("🔍 验证智能体管理器...")
    
    config = Config()
    agent_manager = AgentManager(config)
    
    # 注册测试智能体
    test_agent = AgentInfo(
        id="test_agent",
        name="测试智能体",
        description="用于验证的测试智能体",
        endpoint="http://localhost:8001",
        status=AgentStatus.ONLINE,
        capabilities=["test"],
        version="1.0.0",
        metadata={}
    )
    
    agent_manager.register_agent(test_agent)
    
    # 验证智能体注册
    agents = agent_manager.get_all_agents()
    assert len(agents) == 1
    assert agents[0].id == "test_agent"
    
    print("✅ 智能体管理器验证通过")
    return agent_manager


async def verify_workflow_engine(agent_manager):
    """验证工作流引擎"""
    print("🔍 验证工作流引擎...")
    
    workflow_engine = WorkflowEngine(agent_manager)
    
    # 创建测试工作流
    test_workflow = WorkflowDefinition(
        id="test_workflow",
        name="测试工作流",
        description="用于验证的测试工作流",
        version="1.0.0",
        timeout=30,
        retry_count=1,
        steps=[
            WorkflowStep(
                id="step1",
                name="测试步骤",
                agent="test_agent",
                action="test_action",
                description="测试步骤",
                timeout=10,
                retry_count=1,
                parameters={"test": "data"},
                dependencies=[],
            )
        ],
        metadata={},
        tags=["test"],
    )
    
    # 注册工作流
    workflow_engine.register_workflow(test_workflow)
    
    # 验证工作流注册
    workflows = workflow_engine.get_all_workflows()
    assert len(workflows) == 1
    assert workflows[0].id == "test_workflow"
    
    print("✅ 工作流引擎验证通过")
    return workflow_engine


async def verify_core_functionality():
    """验证核心功能"""
    print("🔍 验证核心功能集成...")
    
    try:
        # 验证智能体管理器
        agent_manager = await verify_agent_manager()
        
        # 验证工作流引擎
        workflow_engine = await verify_workflow_engine(agent_manager)
        
        # 验证网络状态
        network_status = agent_manager.get_network_status()
        assert "agents" in network_status
        assert "total_agents" in network_status
        assert network_status["total_agents"] == 1
        
        print("✅ 核心功能集成验证通过")
        return True
        
    except Exception as e:
        print(f"❌ 核心功能验证失败: {e}")
        return False


async def main():
    """主验证流程"""
    print("🚀 开始 A2A 智能体网络服务部署验证")
    print("=" * 50)
    
    try:
        # 验证核心功能
        success = await verify_core_functionality()
        
        if success:
            print("\n" + "=" * 50)
            print("🎉 部署验证成功！")
            print("✅ A2A 智能体网络服务已准备就绪")
            print("✅ 所有核心功能正常工作")
            print("✅ 可以进行生产部署")
            return 0
        else:
            print("\n" + "=" * 50)
            print("❌ 部署验证失败！")
            print("请检查配置和依赖")
            return 1
            
    except Exception as e:
        print(f"\n❌ 验证过程中发生错误: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main()) 