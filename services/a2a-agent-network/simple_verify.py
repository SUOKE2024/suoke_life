#!/usr/bin/env python3
"""
A2A 智能体网络服务简化验证脚本
验证核心模块是否可以正常导入和初始化
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试核心模块导入"""
    print("🔍 测试核心模块导入...")
    
    try:
        # 测试模型导入
        from internal.model.agent import AgentInfo, AgentStatus, AgentRequest, AgentResponse
        from internal.model.workflow import WorkflowDefinition, WorkflowStep, WorkflowExecution
        print("✅ 模型模块导入成功")
        
        # 测试服务导入
        from internal.service.agent_manager import AgentManager
        from internal.service.workflow_engine import WorkflowEngine
        from internal.service.condition_evaluator import ConditionEvaluator
        print("✅ 服务模块导入成功")
        
        # 测试API导入
        from internal.delivery.rest_api import create_rest_api
        print("✅ API模块导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def main():
    """主验证流程"""
    print("🚀 开始 A2A 智能体网络服务简化验证")
    print("=" * 50)
    
    if test_imports():
        print("\n" + "=" * 50)
        print("🎉 验证成功！")
        print("✅ A2A 智能体网络服务核心模块正常")
        return 0
    else:
        print("\n" + "=" * 50)
        print("❌ 验证失败")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 