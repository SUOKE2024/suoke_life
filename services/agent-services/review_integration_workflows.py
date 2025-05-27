#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
索克生活人工审核集成工作流
Suoke Life Human Review Integrated Workflows

将人工审核集成到现有工作流中，确保关键环节的安全性
"""

import asyncio
import json
import logging
from typing import Dict, Any, List
from datetime import datetime

from human_review_a2a_agent import create_human_review_a2a_agent, ReviewType

logger = logging.getLogger(__name__)


class ReviewIntegratedWorkflows:
    """集成人工审核的工作流管理器"""
    
    def __init__(self):
        """初始化工作流管理器"""
        self.review_agent = create_human_review_a2a_agent()
        self.workflows = {}
        self._define_review_integrated_workflows()
        
        logger.info("人工审核集成工作流管理器初始化完成")
    
    def _define_review_integrated_workflows(self):
        """定义集成人工审核的工作流"""
        
        # 1. 增强版健康咨询工作流（含人工审核）
        enhanced_health_consultation_workflow = {
            "name": "增强版健康咨询工作流",
            "description": "包含人工审核的完整健康咨询流程",
            "steps": [
                {
                    "id": "reception",
                    "agent": "xiaoai",
                    "action": "接收用户咨询",
                    "description": "小艾接收用户的健康咨询请求",
                    "review_required": False
                },
                {
                    "id": "risk_assessment",
                    "agent": "human_review",
                    "action": "风险评估",
                    "description": "评估咨询内容的风险等级",
                    "review_required": True,
                    "review_type": "general_advice",
                    "auto_conditions": ["一般咨询", "常见问题"]
                },
                {
                    "id": "diagnosis_routing",
                    "agent": "xiaoai",
                    "action": "路由诊断请求",
                    "description": "根据风险评估结果决定处理路径",
                    "review_required": False
                },
                {
                    "id": "tcm_diagnosis",
                    "agent": "xiaoke",
                    "action": "中医诊断",
                    "description": "小克进行中医体质辨识和诊断",
                    "condition": "需要诊断",
                    "review_required": True,
                    "review_type": "medical_diagnosis",
                    "priority": "high"
                },
                {
                    "id": "diagnosis_review",
                    "agent": "human_review",
                    "action": "诊断审核",
                    "description": "专业医师审核诊断结果",
                    "review_required": True,
                    "review_type": "medical_diagnosis",
                    "mandatory": True,
                    "reviewer_specialty": ["中医诊断", "医疗建议"]
                },
                {
                    "id": "health_plan",
                    "agent": "soer",
                    "action": "制定健康计划",
                    "description": "索儿基于审核通过的诊断结果制定个性化健康计划",
                    "review_required": True,
                    "review_type": "health_plan",
                    "priority": "normal"
                },
                {
                    "id": "plan_review",
                    "agent": "human_review",
                    "action": "健康计划审核",
                    "description": "营养师审核健康计划的合理性",
                    "review_required": True,
                    "review_type": "health_plan",
                    "reviewer_specialty": ["营养分析", "健康计划"]
                },
                {
                    "id": "knowledge_support",
                    "agent": "laoke",
                    "action": "提供知识支持",
                    "description": "老克提供相关的健康知识和学习资源",
                    "review_required": False
                },
                {
                    "id": "response_synthesis",
                    "agent": "xiaoai",
                    "action": "综合回复",
                    "description": "小艾整合各智能体和审核的结果，给出最终回复",
                    "review_required": False
                },
                {
                    "id": "final_review",
                    "agent": "human_review",
                    "action": "最终审核",
                    "description": "对最终回复进行质量检查",
                    "review_required": True,
                    "review_type": "general_advice",
                    "condition": "高风险用户或复杂情况"
                }
            ]
        }
        
        # 2. 增强版农产品定制工作流（含人工审核）
        enhanced_product_customization_workflow = {
            "name": "增强版农产品定制工作流",
            "description": "包含安全性审核的农产品定制流程",
            "steps": [
                {
                    "id": "requirement_analysis",
                    "agent": "xiaoai",
                    "action": "需求分析",
                    "description": "分析用户的农产品定制需求",
                    "review_required": False
                },
                {
                    "id": "constitution_assessment",
                    "agent": "xiaoke",
                    "action": "体质评估",
                    "description": "评估用户体质，确定适合的食物类型",
                    "review_required": True,
                    "review_type": "medical_diagnosis",
                    "priority": "normal"
                },
                {
                    "id": "constitution_review",
                    "agent": "human_review",
                    "action": "体质评估审核",
                    "description": "中医专家审核体质评估结果",
                    "review_required": True,
                    "review_type": "medical_diagnosis",
                    "reviewer_specialty": ["中医诊断", "体质辨识"]
                },
                {
                    "id": "nutrition_analysis",
                    "agent": "soer",
                    "action": "营养分析",
                    "description": "分析营养需求，制定饮食方案",
                    "review_required": True,
                    "review_type": "nutrition_advice",
                    "priority": "normal"
                },
                {
                    "id": "nutrition_review",
                    "agent": "human_review",
                    "action": "营养方案审核",
                    "description": "营养师审核营养分析和饮食方案",
                    "review_required": True,
                    "review_type": "nutrition_advice",
                    "reviewer_specialty": ["营养分析", "饮食建议"]
                },
                {
                    "id": "product_recommendation",
                    "agent": "xiaoke",
                    "action": "产品推荐",
                    "description": "基于审核通过的营养方案推荐合适的农产品",
                    "review_required": True,
                    "review_type": "product_recommendation",
                    "priority": "normal"
                },
                {
                    "id": "product_safety_review",
                    "agent": "human_review",
                    "action": "产品安全审核",
                    "description": "专家审核产品推荐的安全性和适用性",
                    "review_required": True,
                    "review_type": "product_recommendation",
                    "reviewer_specialty": ["产品推荐", "安全性评估"]
                },
                {
                    "id": "education_content",
                    "agent": "laoke",
                    "action": "教育内容",
                    "description": "提供食疗知识和使用指导",
                    "review_required": False
                }
            ]
        }
        
        # 3. 紧急健康响应工作流（强制人工审核）
        emergency_health_response_workflow = {
            "name": "紧急健康响应工作流",
            "description": "处理紧急健康情况的特殊工作流，全程人工监督",
            "steps": [
                {
                    "id": "emergency_detection",
                    "agent": "xiaoai",
                    "action": "紧急情况检测",
                    "description": "检测用户输入中的紧急健康信号",
                    "review_required": False
                },
                {
                    "id": "immediate_review",
                    "agent": "human_review",
                    "action": "即时人工评估",
                    "description": "紧急情况专家立即评估风险等级",
                    "review_required": True,
                    "review_type": "emergency_response",
                    "priority": "urgent",
                    "mandatory": True,
                    "reviewer_specialty": ["紧急响应", "危急情况"],
                    "max_response_time": 5  # 5分钟内必须响应
                },
                {
                    "id": "emergency_routing",
                    "agent": "human_review",
                    "action": "紧急路由决策",
                    "description": "决定是否需要立即就医或可以提供远程指导",
                    "review_required": True,
                    "review_type": "emergency_response",
                    "mandatory": True
                },
                {
                    "id": "immediate_response",
                    "agent": "xiaoai",
                    "action": "即时响应",
                    "description": "基于人工审核结果提供即时响应",
                    "review_required": False,
                    "condition": "可远程处理"
                },
                {
                    "id": "emergency_referral",
                    "agent": "xiaoke",
                    "action": "紧急转诊",
                    "description": "安排紧急医疗资源和转诊",
                    "review_required": False,
                    "condition": "需要就医"
                },
                {
                    "id": "follow_up_review",
                    "agent": "human_review",
                    "action": "后续跟进审核",
                    "description": "审核处理结果并安排后续跟进",
                    "review_required": True,
                    "review_type": "emergency_response",
                    "mandatory": True
                }
            ]
        }
        
        # 注册工作流
        workflows = [
            enhanced_health_consultation_workflow,
            enhanced_product_customization_workflow,
            emergency_health_response_workflow
        ]
        
        for workflow in workflows:
            self.workflows[workflow["name"]] = workflow
            logger.info(f"已注册增强工作流: {workflow['name']}")
    
    async def execute_workflow_with_review(
        self,
        workflow_name: str,
        user_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行包含人工审核的工作流
        
        Args:
            workflow_name: 工作流名称
            user_request: 用户请求
            
        Returns:
            工作流执行结果
        """
        try:
            workflow = self.workflows.get(workflow_name)
            if not workflow:
                return {"error": f"工作流 {workflow_name} 不存在"}
            
            workflow_results = {}
            context = {"user_request": user_request}
            pending_reviews = {}  # 待审核任务
            
            for step in workflow["steps"]:
                step_id = step["id"]
                agent_id = step["agent"]
                action = step["action"]
                
                # 检查执行条件
                if "condition" in step:
                    if not self._check_condition(step["condition"], context):
                        continue
                
                # 执行步骤
                if step.get("review_required", False):
                    # 需要人工审核的步骤
                    step_result = await self._execute_step_with_review(step, context)
                    
                    # 如果是异步审核，记录待审核任务
                    if step_result.get("requires_human_review"):
                        pending_reviews[step_id] = step_result
                        # 对于非强制同步审核，可以继续执行后续步骤
                        if not step.get("mandatory", False):
                            continue
                        else:
                            # 强制审核，等待审核完成
                            review_info = step_result.get("review_info", {})
                            if "task_id" in review_info:
                                step_result = await self._wait_for_review_completion(
                                    review_info["task_id"]
                                )
                else:
                    # 普通步骤
                    step_result = await self._execute_regular_step(step, context)
                
                workflow_results[step_id] = step_result
                context[step_id] = step_result
            
            return {
                "workflow": workflow_name,
                "results": workflow_results,
                "pending_reviews": pending_reviews,
                "status": "completed" if not pending_reviews else "pending_review"
            }
            
        except Exception as e:
            logger.error(f"工作流执行失败: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def _execute_step_with_review(
        self,
        step: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行需要人工审核的步骤
        
        Args:
            step: 步骤定义
            context: 上下文
            
        Returns:
            步骤执行结果
        """
        try:
            # 首先执行智能体步骤
            if step["agent"] != "human_review":
                step_result = await self._execute_regular_step(step, context)
            else:
                step_result = {"action": step["action"], "message": "人工审核步骤"}
            
            # 提交审核
            review_result = await self.review_agent.submit_for_review(
                content=step_result,
                review_type=step.get("review_type", "general_advice"),
                user_id=context["user_request"].get("user_id", ""),
                agent_id=step["agent"],
                priority=step.get("priority", "normal")
            )
            
            # 合并结果
            step_result.update({
                "review_info": review_result,
                "requires_human_review": review_result.get("requires_human_review", False)
            })
            
            return step_result
            
        except Exception as e:
            logger.error(f"审核步骤执行失败: {e}")
            return {"error": str(e)}
    
    async def _execute_regular_step(
        self,
        step: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行普通步骤
        
        Args:
            step: 步骤定义
            context: 上下文
            
        Returns:
            步骤执行结果
        """
        # 模拟步骤执行
        return {
            "step_id": step["id"],
            "agent": step["agent"],
            "action": step["action"],
            "result": f"步骤 {step['action']} 执行完成",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _wait_for_review_completion(self, task_id: str) -> Dict[str, Any]:
        """
        等待审核完成
        
        Args:
            task_id: 审核任务ID
            
        Returns:
            审核结果
        """
        # 在实际实现中，这里会轮询审核状态
        # 这里简化为直接返回模拟结果
        await asyncio.sleep(1)  # 模拟等待
        
        return {
            "task_id": task_id,
            "review_status": "completed",
            "review_decision": "approved",
            "review_comments": "审核通过"
        }
    
    def _check_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """
        检查执行条件
        
        Args:
            condition: 条件字符串
            context: 上下文
            
        Returns:
            条件是否满足
        """
        # 简化的条件检查逻辑
        user_request = context.get("user_request", {})
        message = user_request.get("message", "")
        
        condition_mapping = {
            "需要诊断": ["诊断", "体质", "症状", "不舒服"],
            "可远程处理": ["轻微", "一般", "咨询"],
            "需要就医": ["紧急", "严重", "危险", "立即"],
            "高风险用户或复杂情况": ["复杂", "多种症状", "慢性病"]
        }
        
        keywords = condition_mapping.get(condition, [])
        return any(keyword in message for keyword in keywords)
    
    async def get_workflow_status(self, workflow_name: str) -> Dict[str, Any]:
        """
        获取工作流状态
        
        Args:
            workflow_name: 工作流名称
            
        Returns:
            工作流状态信息
        """
        workflow = self.workflows.get(workflow_name)
        if not workflow:
            return {"error": "工作流不存在"}
        
        # 统计审核步骤
        review_steps = [
            step for step in workflow["steps"]
            if step.get("review_required", False)
        ]
        
        return {
            "workflow_name": workflow_name,
            "description": workflow["description"],
            "total_steps": len(workflow["steps"]),
            "review_steps": len(review_steps),
            "mandatory_review_steps": len([
                step for step in review_steps
                if step.get("mandatory", False)
            ]),
            "review_types": list(set([
                step.get("review_type", "general_advice")
                for step in review_steps
            ])),
            "estimated_time": self._estimate_workflow_time(workflow)
        }
    
    def _estimate_workflow_time(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        估算工作流执行时间
        
        Args:
            workflow: 工作流定义
            
        Returns:
            时间估算
        """
        regular_steps = len([
            step for step in workflow["steps"]
            if not step.get("review_required", False)
        ])
        
        review_steps = len([
            step for step in workflow["steps"]
            if step.get("review_required", False)
        ])
        
        # 估算时间（分钟）
        regular_time = regular_steps * 2  # 每个普通步骤2分钟
        review_time = review_steps * 30   # 每个审核步骤30分钟
        
        return {
            "regular_steps_time": regular_time,
            "review_steps_time": review_time,
            "total_estimated_time": regular_time + review_time,
            "time_unit": "minutes"
        }


# 示例使用
async def main():
    """示例主函数"""
    # 创建工作流管理器
    workflow_manager = ReviewIntegratedWorkflows()
    
    print("🔄 索克生活人工审核集成工作流演示")
    print("=" * 60)
    
    # 获取工作流状态
    for workflow_name in workflow_manager.workflows.keys():
        status = await workflow_manager.get_workflow_status(workflow_name)
        print(f"\n📋 {workflow_name}:")
        print(f"  描述: {status['description']}")
        print(f"  总步骤: {status['total_steps']}")
        print(f"  审核步骤: {status['review_steps']}")
        print(f"  强制审核步骤: {status['mandatory_review_steps']}")
        print(f"  预估时间: {status['estimated_time']['total_estimated_time']} 分钟")
    
    # 执行示例工作流
    print("\n🚀 执行增强版健康咨询工作流:")
    user_request = {
        "user_id": "user123",
        "message": "我最近感觉很累，想了解一下我的体质，需要专业诊断",
        "type": "health_consultation"
    }
    
    result = await workflow_manager.execute_workflow_with_review(
        "增强版健康咨询工作流",
        user_request
    )
    
    print("执行结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main()) 