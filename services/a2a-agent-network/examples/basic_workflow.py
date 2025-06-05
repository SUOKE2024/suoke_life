#!/usr/bin/env python3
"""
基础工作流示例
Basic Workflow Example

演示如何创建和执行一个简单的工作流
"""

import asyncio
import json
from typing import Dict, Any

from internal.model.workflow import (
    WorkflowDefinition,
    WorkflowStep,
    StepType,
    ConditionRule,
    ConditionOperator
)
from internal.service.agent_manager import AgentManager
from internal.service.workflow_engine import WorkflowEngine


async def create_basic_workflow() -> WorkflowDefinition:
    """创建基础工作流定义"""
    
    # 步骤1: 小艾进行初步分析
    step1 = WorkflowStep(
        id="initial_analysis",
        name="初步分析",
        type=StepType.ACTION,
        agent="xiaoai",
        action="analyze_symptoms",
        parameters={
            "analysis_type": "initial",
            "include_recommendations": True
        },
        timeout=30,
        retry_count=2,
        dependencies=[]
    )
    
    # 步骤2: 条件判断 - 是否需要进一步检查
    condition_rule = ConditionRule(
        field="step_initial_analysis_result.severity",
        operator=ConditionOperator.GREATER_THAN,
        value=5
    )
    
    step2 = WorkflowStep(
        id="severity_check",
        name="严重程度检查",
        type=StepType.CONDITION,
        condition=condition_rule,
        dependencies=["initial_analysis"]
    )
    
    # 步骤3a: 高严重程度 - 小克进行详细诊断
    step3a = WorkflowStep(
        id="detailed_diagnosis",
        name="详细诊断",
        type=StepType.ACTION,
        agent="xiaoke",
        action="detailed_diagnosis",
        parameters={
            "include_differential": True,
            "priority": "high"
        },
        timeout=60,
        retry_count=1,
        dependencies=["severity_check"],
        condition=ConditionRule(
            field="step_severity_check_condition",
            operator=ConditionOperator.EQUALS,
            value=True
        )
    )
    
    # 步骤3b: 低严重程度 - 索儿提供生活建议
    step3b = WorkflowStep(
        id="lifestyle_advice",
        name="生活建议",
        type=StepType.ACTION,
        agent="soer",
        action="provide_lifestyle_advice",
        parameters={
            "focus_areas": ["diet", "exercise", "sleep"]
        },
        timeout=30,
        retry_count=1,
        dependencies=["severity_check"],
        condition=ConditionRule(
            field="step_severity_check_condition",
            operator=ConditionOperator.EQUALS,
            value=False
        )
    )
    
    # 步骤4: 老克进行最终总结
    step4 = WorkflowStep(
        id="final_summary",
        name="最终总结",
        type=StepType.ACTION,
        agent="laoke",
        action="create_summary",
        parameters={
            "include_all_steps": True,
            "format": "comprehensive"
        },
        timeout=45,
        retry_count=1,
        dependencies=["detailed_diagnosis", "lifestyle_advice"]
    )
    
    # 创建工作流定义
    workflow = WorkflowDefinition(
        id="basic_health_consultation",
        name="基础健康咨询工作流",
        description="演示四个智能体协作进行健康咨询的基础工作流",
        version="1.0.0",
        steps=[step1, step2, step3a, step3b, step4],
        metadata={
            "author": "A2A Team",
            "category": "health_consultation",
            "estimated_duration": 180  # 3分钟
        }
    )
    
    return workflow


async def execute_workflow_example():
    """执行工作流示例"""
    
    print("🚀 A2A智能体网络 - 基础工作流示例")
    print("=" * 50)
    
    # 初始化组件
    agent_manager = AgentManager()
    workflow_engine = WorkflowEngine(agent_manager)
    
    # 创建工作流
    workflow = await create_basic_workflow()
    workflow_engine.register_workflow(workflow)
    
    print(f"✅ 工作流已注册: {workflow.name}")
    print(f"📋 工作流ID: {workflow.id}")
    print(f"🔧 步骤数量: {len(workflow.steps)}")
    print()
    
    # 准备执行参数
    parameters = {
        "patient_id": "patient_001",
        "symptoms": ["头痛", "疲劳", "失眠"],
        "duration": "3天",
        "severity": 6
    }
    
    print("📝 执行参数:")
    print(json.dumps(parameters, indent=2, ensure_ascii=False))
    print()
    
    try:
        # 执行工作流
        print("🏃 开始执行工作流...")
        execution = await workflow_engine.execute_workflow(
            workflow_id=workflow.id,
            parameters=parameters,
            user_id="user_001",
            context={"session_id": "session_001"}
        )
        
        print(f"✅ 工作流执行已启动")
        print(f"🆔 执行ID: {execution.execution_id}")
        print()
        
        # 监控执行进度
        print("📊 监控执行进度...")
        while execution.status.value in ["running", "pending"]:
            await asyncio.sleep(2)
            
            progress = workflow_engine.get_execution_progress(execution.execution_id)
            if progress:
                print(f"进度: {progress['progress']['progress_percentage']:.1f}% "
                      f"({progress['progress']['completed_steps']}/{progress['progress']['total_steps']})")
        
        # 显示最终结果
        final_execution = workflow_engine.get_execution(execution.execution_id)
        print()
        print("🎯 执行结果:")
        print(f"状态: {final_execution.status.value}")
        print(f"执行时间: {final_execution.execution_time:.2f}秒")
        
        if final_execution.error:
            print(f"❌ 错误: {final_execution.error}")
        else:
            print("✅ 执行成功!")
            
            # 显示各步骤结果
            print("\n📋 步骤执行详情:")
            for step in final_execution.steps:
                status_emoji = {
                    "completed": "✅",
                    "failed": "❌",
                    "skipped": "⏭️",
                    "pending": "⏳",
                    "running": "🏃"
                }.get(step.status.value, "❓")
                
                print(f"  {status_emoji} {step.step_id}: {step.status.value}")
                if step.execution_time:
                    print(f"    ⏱️ 执行时间: {step.execution_time:.2f}秒")
                if step.error:
                    print(f"    ❌ 错误: {step.error}")
    
    except Exception as e:
        print(f"❌ 执行失败: {e}")
    
    print("\n🏁 示例执行完成")


async def demonstrate_workflow_features():
    """演示工作流高级特性"""
    
    print("\n🔧 A2A工作流引擎特性演示")
    print("=" * 50)
    
    features = [
        "✅ 智能体动态注册和发现",
        "✅ 工作流步骤依赖管理",
        "✅ 条件分支执行",
        "✅ 循环控制",
        "✅ 并行步骤执行",
        "✅ 错误处理和重试机制",
        "✅ 执行进度跟踪",
        "✅ 上下文数据传递",
        "✅ 超时控制",
        "✅ 工作流取消",
        "✅ 性能监控",
        "✅ 分布式追踪"
    ]
    
    print("🚀 支持的特性:")
    for feature in features:
        print(f"  {feature}")
    
    print("\n📊 监控指标:")
    metrics = [
        "• 工作流执行次数",
        "• 步骤成功/失败率",
        "• 平均执行时间",
        "• 智能体响应时间",
        "• 系统资源使用",
        "• 错误分布统计"
    ]
    
    for metric in metrics:
        print(f"  {metric}")


if __name__ == "__main__":
    async def main():
        await execute_workflow_example()
        await demonstrate_workflow_features()
    
    asyncio.run(main()) 