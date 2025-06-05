#!/usr/bin/env python3
"""
高级工作流示例
Advanced Workflow Example

演示条件分支、循环控制和并行执行等高级特性
"""

import asyncio
import json
from typing import Dict, Any, List

from internal.model.workflow import (
    WorkflowDefinition,
    WorkflowStep,
    StepType,
    ConditionRule,
    ConditionOperator,
    LoopConfig,
    LoopType
)
from internal.service.agent_manager import AgentManager
from internal.service.workflow_engine import WorkflowEngine


async def create_advanced_workflow() -> WorkflowDefinition:
    """创建高级工作流定义"""
    
    # 步骤1: 并行收集多个智能体的初步评估
    parallel_steps = [
        WorkflowStep(
            id="xiaoai_assessment",
            name="小艾评估",
            type=StepType.ACTION,
            agent="xiaoai",
            action="initial_assessment",
            parameters={"focus": "symptoms_analysis"},
            timeout=30
        ),
        WorkflowStep(
            id="xiaoke_assessment", 
            name="小克评估",
            type=StepType.ACTION,
            agent="xiaoke",
            action="initial_assessment",
            parameters={"focus": "medical_history"},
            timeout=30
        ),
        WorkflowStep(
            id="soer_assessment",
            name="索儿评估", 
            type=StepType.ACTION,
            agent="soer",
            action="initial_assessment",
            parameters={"focus": "lifestyle_factors"},
            timeout=30
        )
    ]
    
    step1 = WorkflowStep(
        id="parallel_assessment",
        name="并行初步评估",
        type=StepType.PARALLEL,
        parallel_steps=parallel_steps,
        timeout=45,
        dependencies=[]
    )
    
    # 步骤2: 循环进行多轮诊断
    loop_config = LoopConfig(
        loop_type=LoopType.FOR,
        max_iterations=3,
        condition=ConditionRule(
            field="diagnosis_confidence",
            operator=ConditionOperator.LESS_THAN,
            value=0.8
        ),
        break_on_error=False
    )
    
    loop_steps = [
        WorkflowStep(
            id="diagnostic_iteration",
            name="诊断迭代",
            type=StepType.ACTION,
            agent="xiaoke",
            action="iterative_diagnosis",
            parameters={"iteration": "{{loop_iteration}}"},
            timeout=60
        )
    ]
    
    step2 = WorkflowStep(
        id="iterative_diagnosis",
        name="迭代诊断",
        type=StepType.LOOP,
        loop_config=loop_config,
        loop_steps=loop_steps,
        dependencies=["parallel_assessment"]
    )
    
    # 步骤3: 条件分支 - 根据诊断结果选择治疗方案
    step3 = WorkflowStep(
        id="treatment_decision",
        name="治疗决策",
        type=StepType.CONDITION,
        condition=ConditionRule(
            field="step_iterative_diagnosis_result.treatment_required",
            operator=ConditionOperator.EQUALS,
            value=True
        ),
        dependencies=["iterative_diagnosis"]
    )
    
    # 步骤4a: 需要治疗 - 制定治疗方案
    step4a = WorkflowStep(
        id="treatment_plan",
        name="制定治疗方案",
        type=StepType.ACTION,
        agent="xiaoke",
        action="create_treatment_plan",
        parameters={
            "include_medications": True,
            "include_procedures": True
        },
        timeout=90,
        dependencies=["treatment_decision"],
        condition=ConditionRule(
            field="step_treatment_decision_condition",
            operator=ConditionOperator.EQUALS,
            value=True
        )
    )
    
    # 步骤4b: 不需要治疗 - 预防建议
    step4b = WorkflowStep(
        id="prevention_advice",
        name="预防建议",
        type=StepType.ACTION,
        agent="soer",
        action="provide_prevention_advice",
        parameters={
            "focus_areas": ["nutrition", "exercise", "stress_management"]
        },
        timeout=45,
        dependencies=["treatment_decision"],
        condition=ConditionRule(
            field="step_treatment_decision_condition",
            operator=ConditionOperator.EQUALS,
            value=False
        )
    )
    
    # 步骤5: 等待用户确认
    step5 = WorkflowStep(
        id="user_confirmation",
        name="等待用户确认",
        type=StepType.WAIT,
        wait_condition=ConditionRule(
            field="user_confirmed",
            operator=ConditionOperator.EQUALS,
            value=True
        ),
        timeout=300,  # 5分钟超时
        dependencies=["treatment_plan", "prevention_advice"]
    )
    
    # 步骤6: 老克生成最终报告
    step6 = WorkflowStep(
        id="final_report",
        name="生成最终报告",
        type=StepType.ACTION,
        agent="laoke",
        action="generate_comprehensive_report",
        parameters={
            "include_timeline": True,
            "include_recommendations": True,
            "format": "detailed"
        },
        timeout=60,
        dependencies=["user_confirmation"]
    )
    
    # 创建工作流定义
    workflow = WorkflowDefinition(
        id="advanced_health_consultation",
        name="高级健康咨询工作流",
        description="演示条件分支、循环控制和并行执行的高级工作流",
        version="2.0.0",
        steps=[step1, step2, step3, step4a, step4b, step5, step6],
        metadata={
            "author": "A2A Team",
            "category": "advanced_consultation",
            "estimated_duration": 600,  # 10分钟
            "features": ["parallel", "loop", "condition", "wait"]
        }
    )
    
    return workflow


async def create_monitoring_workflow() -> WorkflowDefinition:
    """创建监控工作流"""
    
    # 健康监控循环
    monitoring_loop = LoopConfig(
        loop_type=LoopType.WHILE,
        condition=ConditionRule(
            field="monitoring_active",
            operator=ConditionOperator.EQUALS,
            value=True
        ),
        max_iterations=100,
        break_on_error=True
    )
    
    monitoring_steps = [
        WorkflowStep(
            id="collect_vitals",
            name="收集生命体征",
            type=StepType.ACTION,
            agent="xiaoai",
            action="collect_vital_signs",
            timeout=30
        ),
        WorkflowStep(
            id="analyze_trends",
            name="分析趋势",
            type=StepType.ACTION,
            agent="xiaoke",
            action="analyze_health_trends",
            timeout=45
        ),
        WorkflowStep(
            id="wait_interval",
            name="等待间隔",
            type=StepType.WAIT,
            wait_duration=3600,  # 1小时
            timeout=3700
        )
    ]
    
    step1 = WorkflowStep(
        id="continuous_monitoring",
        name="持续健康监控",
        type=StepType.LOOP,
        loop_config=monitoring_loop,
        loop_steps=monitoring_steps,
        dependencies=[]
    )
    
    # 异常检测
    step2 = WorkflowStep(
        id="anomaly_detection",
        name="异常检测",
        type=StepType.CONDITION,
        condition=ConditionRule(
            field="step_continuous_monitoring_result.anomaly_detected",
            operator=ConditionOperator.EQUALS,
            value=True
        ),
        dependencies=["continuous_monitoring"]
    )
    
    # 紧急响应
    step3 = WorkflowStep(
        id="emergency_response",
        name="紧急响应",
        type=StepType.ACTION,
        agent="xiaoke",
        action="emergency_assessment",
        parameters={"priority": "urgent"},
        timeout=120,
        dependencies=["anomaly_detection"],
        condition=ConditionRule(
            field="step_anomaly_detection_condition",
            operator=ConditionOperator.EQUALS,
            value=True
        )
    )
    
    workflow = WorkflowDefinition(
        id="health_monitoring",
        name="健康监控工作流",
        description="持续监控用户健康状态并在异常时触发响应",
        version="1.0.0",
        steps=[step1, step2, step3],
        metadata={
            "author": "A2A Team",
            "category": "monitoring",
            "estimated_duration": -1,  # 持续运行
            "features": ["continuous", "loop", "condition", "emergency"]
        }
    )
    
    return workflow


async def execute_advanced_workflow_example():
    """执行高级工作流示例"""
    
    print("🚀 A2A智能体网络 - 高级工作流示例")
    print("=" * 50)
    
    # 初始化组件
    agent_manager = AgentManager()
    workflow_engine = WorkflowEngine(agent_manager)
    
    # 创建并注册工作流
    advanced_workflow = await create_advanced_workflow()
    monitoring_workflow = await create_monitoring_workflow()
    
    workflow_engine.register_workflow(advanced_workflow)
    workflow_engine.register_workflow(monitoring_workflow)
    
    print("✅ 工作流已注册:")
    print(f"  📋 {advanced_workflow.name} (ID: {advanced_workflow.id})")
    print(f"  📋 {monitoring_workflow.name} (ID: {monitoring_workflow.id})")
    print()
    
    # 演示高级工作流
    print("🔧 演示高级工作流特性:")
    print("  ✅ 并行步骤执行")
    print("  ✅ 循环控制 (for/while/foreach)")
    print("  ✅ 条件分支")
    print("  ✅ 等待机制")
    print("  ✅ 复杂依赖关系")
    print()
    
    # 执行参数
    parameters = {
        "patient_id": "patient_002",
        "symptoms": ["胸痛", "呼吸困难", "心悸"],
        "severity": 8,
        "medical_history": ["高血压", "糖尿病"],
        "monitoring_active": True
    }
    
    print("📝 执行参数:")
    print(json.dumps(parameters, indent=2, ensure_ascii=False))
    print()
    
    try:
        # 执行高级工作流
        print("🏃 执行高级健康咨询工作流...")
        execution = await workflow_engine.execute_workflow(
            workflow_id=advanced_workflow.id,
            parameters=parameters,
            user_id="user_002",
            context={"priority": "high"}
        )
        
        print(f"✅ 工作流执行已启动: {execution.execution_id}")
        
        # 模拟用户确认
        await asyncio.sleep(5)
        execution.context["user_confirmed"] = True
        print("✅ 模拟用户确认完成")
        
        # 等待执行完成
        while execution.status.value in ["running", "pending"]:
            await asyncio.sleep(2)
            progress = workflow_engine.get_execution_progress(execution.execution_id)
            if progress:
                print(f"📊 进度: {progress['progress']['progress_percentage']:.1f}%")
        
        # 显示结果
        final_execution = workflow_engine.get_execution(execution.execution_id)
        print(f"\n🎯 执行结果: {final_execution.status.value}")
        print(f"⏱️ 执行时间: {final_execution.execution_time:.2f}秒")
        
    except Exception as e:
        print(f"❌ 执行失败: {e}")


async def demonstrate_workflow_patterns():
    """演示工作流设计模式"""
    
    print("\n🎨 A2A工作流设计模式")
    print("=" * 50)
    
    patterns = [
        {
            "name": "🔄 管道模式 (Pipeline)",
            "description": "顺序执行一系列处理步骤",
            "use_case": "数据处理、诊断流程"
        },
        {
            "name": "🌳 分支模式 (Branch)",
            "description": "根据条件选择不同的执行路径",
            "use_case": "个性化治疗方案、风险评估"
        },
        {
            "name": "🔁 循环模式 (Loop)",
            "description": "重复执行直到满足条件",
            "use_case": "迭代优化、持续监控"
        },
        {
            "name": "⚡ 并行模式 (Parallel)",
            "description": "同时执行多个独立任务",
            "use_case": "多维度评估、并发检查"
        },
        {
            "name": "⏳ 等待模式 (Wait)",
            "description": "等待外部事件或条件",
            "use_case": "用户交互、异步处理"
        },
        {
            "name": "🎯 聚合模式 (Aggregation)",
            "description": "收集和合并多个结果",
            "use_case": "综合诊断、多源数据融合"
        }
    ]
    
    for pattern in patterns:
        print(f"{pattern['name']}")
        print(f"  📝 描述: {pattern['description']}")
        print(f"  🎯 应用: {pattern['use_case']}")
        print()


if __name__ == "__main__":
    async def main():
        await execute_advanced_workflow_example()
        await demonstrate_workflow_patterns()
    
    asyncio.run(main()) 