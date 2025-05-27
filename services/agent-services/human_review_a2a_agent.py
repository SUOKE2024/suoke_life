#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
索克生活人工审核智能体
Suoke Life Human Review A2A Agent

管理人工审核流程，确保医疗健康建议的安全性和准确性
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, asdict
from python_a2a import A2AServer, AgentCard

logger = logging.getLogger(__name__)


class ReviewStatus(Enum):
    """审核状态"""
    PENDING = "pending"          # 待审核
    IN_PROGRESS = "in_progress"  # 审核中
    APPROVED = "approved"        # 已通过
    REJECTED = "rejected"        # 已拒绝
    NEEDS_REVISION = "needs_revision"  # 需要修改


class ReviewPriority(Enum):
    """审核优先级"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ReviewType(Enum):
    """审核类型"""
    MEDICAL_DIAGNOSIS = "medical_diagnosis"      # 医疗诊断
    HEALTH_PLAN = "health_plan"                 # 健康计划
    NUTRITION_ADVICE = "nutrition_advice"        # 营养建议
    PRODUCT_RECOMMENDATION = "product_recommendation"  # 产品推荐
    EMERGENCY_RESPONSE = "emergency_response"    # 紧急响应
    GENERAL_ADVICE = "general_advice"           # 一般建议


@dataclass
class ReviewTask:
    """审核任务"""
    task_id: str
    review_type: ReviewType
    priority: ReviewPriority
    status: ReviewStatus
    content: Dict[str, Any]
    user_id: str
    agent_id: str
    created_at: datetime
    assigned_to: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    review_comments: str = ""
    review_result: Optional[Dict[str, Any]] = None
    estimated_time: int = 30  # 预估审核时间（分钟）


@dataclass
class Reviewer:
    """审核员"""
    reviewer_id: str
    name: str
    specialties: List[str]  # 专业领域
    max_concurrent_tasks: int = 5
    current_tasks: int = 0
    average_review_time: float = 30.0  # 平均审核时间（分钟）
    is_available: bool = True


class HumanReviewA2AAgent(A2AServer):
    """人工审核智能体"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化人工审核智能体
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        
        # 创建智能体卡片
        self.agent_card = AgentCard(
            name="人工审核智能体",
            description="负责医疗健康建议的人工审核，确保安全性和准确性",
            url="http://localhost:8080/human_review"
        )
        
        # 初始化审核系统
        self.review_queue: List[ReviewTask] = []
        self.reviewers: Dict[str, Reviewer] = {}
        self.review_history: List[ReviewTask] = []
        self.review_statistics = {
            "total_reviews": 0,
            "approved_count": 0,
            "rejected_count": 0,
            "average_review_time": 0.0,
            "pending_count": 0
        }
        
        # 初始化审核员
        self._init_reviewers()
        
        # 风险评估规则
        self.risk_rules = self._init_risk_rules()
        
        super().__init__(self.agent_card)
        logger.info("人工审核智能体初始化完成")
    
    def _init_reviewers(self):
        """初始化审核员"""
        default_reviewers = [
            {
                "reviewer_id": "dr_zhang",
                "name": "张医生",
                "specialties": ["中医诊断", "体质辨识", "医疗建议"],
                "max_concurrent_tasks": 3
            },
            {
                "reviewer_id": "nutritionist_li",
                "name": "李营养师",
                "specialties": ["营养分析", "饮食建议", "健康计划"],
                "max_concurrent_tasks": 5
            },
            {
                "reviewer_id": "pharmacist_wang",
                "name": "王药师",
                "specialties": ["药物建议", "产品推荐", "安全性评估"],
                "max_concurrent_tasks": 4
            },
            {
                "reviewer_id": "emergency_specialist",
                "name": "急诊专家",
                "specialties": ["紧急响应", "风险评估", "危急情况"],
                "max_concurrent_tasks": 2
            }
        ]
        
        for reviewer_data in default_reviewers:
            reviewer = Reviewer(**reviewer_data)
            self.reviewers[reviewer.reviewer_id] = reviewer
    
    def _init_risk_rules(self) -> Dict[str, Any]:
        """初始化风险评估规则"""
        return {
            "high_risk_keywords": [
                "紧急", "急诊", "危险", "严重", "立即就医", "心脏病", "中风", "过敏反应"
            ],
            "medical_keywords": [
                "诊断", "治疗", "药物", "手术", "病症", "疾病", "症状"
            ],
            "auto_approve_types": [
                "general_advice"  # 一般建议可以自动通过
            ],
            "mandatory_review_types": [
                "medical_diagnosis", "emergency_response"  # 必须人工审核
            ]
        }
    
    async def submit_for_review(
        self,
        content: Dict[str, Any],
        review_type: str,
        user_id: str,
        agent_id: str,
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """
        提交内容进行审核
        
        Args:
            content: 待审核内容
            review_type: 审核类型
            user_id: 用户ID
            agent_id: 智能体ID
            priority: 优先级
            
        Returns:
            审核任务信息
        """
        try:
            # 创建审核任务
            task_id = f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.review_queue)}"
            
            # 风险评估
            assessed_priority = self._assess_risk(content, priority)
            
            review_task = ReviewTask(
                task_id=task_id,
                review_type=ReviewType(review_type),
                priority=ReviewPriority(assessed_priority),
                status=ReviewStatus.PENDING,
                content=content,
                user_id=user_id,
                agent_id=agent_id,
                created_at=datetime.now()
            )
            
            # 检查是否需要人工审核
            if self._needs_human_review(review_task):
                # 分配审核员
                assigned_reviewer = self._assign_reviewer(review_task)
                if assigned_reviewer:
                    review_task.assigned_to = assigned_reviewer
                    review_task.status = ReviewStatus.IN_PROGRESS
                    self.reviewers[assigned_reviewer].current_tasks += 1
                
                # 添加到队列
                self.review_queue.append(review_task)
                self.review_statistics["pending_count"] += 1
                
                logger.info(f"审核任务已创建: {task_id}, 分配给: {assigned_reviewer}")
                
                return {
                    "task_id": task_id,
                    "status": "submitted",
                    "assigned_to": assigned_reviewer,
                    "estimated_completion": self._estimate_completion_time(review_task).isoformat(),
                    "requires_human_review": True
                }
            else:
                # 自动通过
                review_task.status = ReviewStatus.APPROVED
                review_task.reviewed_at = datetime.now()
                review_task.review_result = content
                
                self.review_history.append(review_task)
                self._update_statistics(review_task)
                
                return {
                    "task_id": task_id,
                    "status": "auto_approved",
                    "result": content,
                    "requires_human_review": False
                }
                
        except Exception as e:
            logger.error(f"提交审核失败: {e}")
            return {"error": str(e)}
    
    def _assess_risk(self, content: Dict[str, Any], base_priority: str) -> str:
        """
        评估内容风险等级
        
        Args:
            content: 内容
            base_priority: 基础优先级
            
        Returns:
            评估后的优先级
        """
        content_text = json.dumps(content, ensure_ascii=False).lower()
        
        # 检查高风险关键词
        for keyword in self.risk_rules["high_risk_keywords"]:
            if keyword in content_text:
                return "urgent"
        
        # 检查医疗关键词
        for keyword in self.risk_rules["medical_keywords"]:
            if keyword in content_text:
                if base_priority == "normal":
                    return "high"
        
        return base_priority
    
    def _needs_human_review(self, task: ReviewTask) -> bool:
        """
        判断是否需要人工审核
        
        Args:
            task: 审核任务
            
        Returns:
            是否需要人工审核
        """
        # 强制审核类型
        if task.review_type.value in self.risk_rules["mandatory_review_types"]:
            return True
        
        # 自动通过类型
        if task.review_type.value in self.risk_rules["auto_approve_types"]:
            return False
        
        # 高优先级需要审核
        if task.priority in [ReviewPriority.HIGH, ReviewPriority.URGENT]:
            return True
        
        return True  # 默认需要审核
    
    def _assign_reviewer(self, task: ReviewTask) -> Optional[str]:
        """
        分配审核员
        
        Args:
            task: 审核任务
            
        Returns:
            分配的审核员ID
        """
        # 根据任务类型和审核员专业匹配
        suitable_reviewers = []
        
        for reviewer_id, reviewer in self.reviewers.items():
            if not reviewer.is_available:
                continue
            
            if reviewer.current_tasks >= reviewer.max_concurrent_tasks:
                continue
            
            # 检查专业匹配
            task_type_mapping = {
                ReviewType.MEDICAL_DIAGNOSIS: ["中医诊断", "医疗建议"],
                ReviewType.HEALTH_PLAN: ["营养分析", "健康计划"],
                ReviewType.NUTRITION_ADVICE: ["营养分析", "饮食建议"],
                ReviewType.PRODUCT_RECOMMENDATION: ["产品推荐", "安全性评估"],
                ReviewType.EMERGENCY_RESPONSE: ["紧急响应", "危急情况"]
            }
            
            required_specialties = task_type_mapping.get(task.review_type, [])
            if any(specialty in reviewer.specialties for specialty in required_specialties):
                suitable_reviewers.append((reviewer_id, reviewer))
        
        if not suitable_reviewers:
            # 如果没有专业匹配的，选择工作量最少的
            available_reviewers = [
                (rid, r) for rid, r in self.reviewers.items()
                if r.is_available and r.current_tasks < r.max_concurrent_tasks
            ]
            if available_reviewers:
                suitable_reviewers = available_reviewers
        
        if suitable_reviewers:
            # 选择当前任务最少的审核员
            selected = min(suitable_reviewers, key=lambda x: x[1].current_tasks)
            return selected[0]
        
        return None
    
    def _estimate_completion_time(self, task: ReviewTask) -> datetime:
        """
        估算完成时间
        
        Args:
            task: 审核任务
            
        Returns:
            预估完成时间
        """
        if task.assigned_to:
            reviewer = self.reviewers[task.assigned_to]
            estimated_minutes = reviewer.average_review_time
        else:
            estimated_minutes = task.estimated_time
        
        # 根据优先级调整
        priority_multiplier = {
            ReviewPriority.URGENT: 0.5,
            ReviewPriority.HIGH: 0.7,
            ReviewPriority.NORMAL: 1.0,
            ReviewPriority.LOW: 1.5
        }
        
        estimated_minutes *= priority_multiplier.get(task.priority, 1.0)
        
        return datetime.now() + timedelta(minutes=estimated_minutes)
    
    async def get_review_status(self, task_id: str) -> Dict[str, Any]:
        """
        获取审核状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            审核状态信息
        """
        try:
            # 在队列中查找
            for task in self.review_queue:
                if task.task_id == task_id:
                    return {
                        "task_id": task_id,
                        "status": task.status.value,
                        "assigned_to": task.assigned_to,
                        "created_at": task.created_at.isoformat(),
                        "estimated_completion": self._estimate_completion_time(task).isoformat()
                    }
            
            # 在历史中查找
            for task in self.review_history:
                if task.task_id == task_id:
                    return {
                        "task_id": task_id,
                        "status": task.status.value,
                        "reviewed_at": task.reviewed_at.isoformat() if task.reviewed_at else None,
                        "review_comments": task.review_comments,
                        "result": task.review_result
                    }
            
            return {"error": "任务不存在"}
            
        except Exception as e:
            logger.error(f"获取审核状态失败: {e}")
            return {"error": str(e)}
    
    async def complete_review(
        self,
        task_id: str,
        reviewer_id: str,
        decision: str,
        comments: str = "",
        revised_content: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        完成审核
        
        Args:
            task_id: 任务ID
            reviewer_id: 审核员ID
            decision: 审核决定 (approved/rejected/needs_revision)
            comments: 审核意见
            revised_content: 修改后的内容
            
        Returns:
            审核结果
        """
        try:
            # 查找任务
            task = None
            for i, t in enumerate(self.review_queue):
                if t.task_id == task_id and t.assigned_to == reviewer_id:
                    task = self.review_queue.pop(i)
                    break
            
            if not task:
                return {"error": "任务不存在或无权限"}
            
            # 更新任务状态
            task.status = ReviewStatus(decision)
            task.reviewed_at = datetime.now()
            task.review_comments = comments
            
            if decision == "approved":
                task.review_result = revised_content or task.content
            elif decision == "needs_revision":
                task.review_result = revised_content
            else:  # rejected
                task.review_result = None
            
            # 更新审核员状态
            if reviewer_id in self.reviewers:
                self.reviewers[reviewer_id].current_tasks -= 1
            
            # 添加到历史
            self.review_history.append(task)
            
            # 更新统计
            self._update_statistics(task)
            
            logger.info(f"审核完成: {task_id}, 决定: {decision}")
            
            return {
                "task_id": task_id,
                "status": "completed",
                "decision": decision,
                "result": task.review_result
            }
            
        except Exception as e:
            logger.error(f"完成审核失败: {e}")
            return {"error": str(e)}
    
    def _update_statistics(self, task: ReviewTask):
        """更新统计信息"""
        self.review_statistics["total_reviews"] += 1
        
        if task.status == ReviewStatus.APPROVED:
            self.review_statistics["approved_count"] += 1
        elif task.status == ReviewStatus.REJECTED:
            self.review_statistics["rejected_count"] += 1
        
        if task.reviewed_at and task.created_at:
            review_time = (task.reviewed_at - task.created_at).total_seconds() / 60
            total_time = self.review_statistics["average_review_time"] * (self.review_statistics["total_reviews"] - 1)
            self.review_statistics["average_review_time"] = (total_time + review_time) / self.review_statistics["total_reviews"]
        
        self.review_statistics["pending_count"] = len([t for t in self.review_queue if t.status == ReviewStatus.PENDING])
    
    async def get_review_dashboard(self) -> Dict[str, Any]:
        """
        获取审核仪表板数据
        
        Returns:
            仪表板数据
        """
        try:
            # 队列统计
            queue_stats = {
                "total_pending": len([t for t in self.review_queue if t.status == ReviewStatus.PENDING]),
                "total_in_progress": len([t for t in self.review_queue if t.status == ReviewStatus.IN_PROGRESS]),
                "urgent_tasks": len([t for t in self.review_queue if t.priority == ReviewPriority.URGENT]),
                "high_priority_tasks": len([t for t in self.review_queue if t.priority == ReviewPriority.HIGH])
            }
            
            # 审核员状态
            reviewer_stats = {}
            for reviewer_id, reviewer in self.reviewers.items():
                reviewer_stats[reviewer_id] = {
                    "name": reviewer.name,
                    "current_tasks": reviewer.current_tasks,
                    "max_tasks": reviewer.max_concurrent_tasks,
                    "is_available": reviewer.is_available,
                    "utilization": reviewer.current_tasks / reviewer.max_concurrent_tasks
                }
            
            return {
                "queue_statistics": queue_stats,
                "reviewer_statistics": reviewer_stats,
                "overall_statistics": self.review_statistics,
                "recent_tasks": [
                    {
                        "task_id": task.task_id,
                        "type": task.review_type.value,
                        "priority": task.priority.value,
                        "status": task.status.value,
                        "created_at": task.created_at.isoformat()
                    }
                    for task in self.review_queue[-10:]  # 最近10个任务
                ]
            }
            
        except Exception as e:
            logger.error(f"获取仪表板数据失败: {e}")
            return {"error": str(e)}
    
    async def handle_task(self, task) -> Any:
        """
        处理A2A任务
        
        Args:
            task: A2A任务对象
            
        Returns:
            处理结果
        """
        try:
            message_content = task.message.get("content", {})
            text = message_content.get("text", "")
            
            # 解析任务类型
            if "提交审核" in text:
                # 提取审核参数
                result = await self.submit_for_review(
                    content={"text": text},
                    review_type="general_advice",
                    user_id=task.user_id,
                    agent_id="human_review"
                )
            elif "审核状态" in text:
                # 获取审核状态
                result = await self.get_review_dashboard()
            else:
                result = {"message": "人工审核智能体已就绪，可以处理审核任务"}
            
            # 创建响应
            task.artifacts = [{
                "type": "text",
                "parts": [{
                    "text": json.dumps(result, ensure_ascii=False, indent=2)
                }]
            }]
            
            return task
            
        except Exception as e:
            logger.error(f"处理任务失败: {e}")
            task.artifacts = [{
                "type": "text", 
                "parts": [{
                    "text": f"处理失败: {str(e)}"
                }]
            }]
            return task


def create_human_review_a2a_agent(config: Dict[str, Any] = None) -> HumanReviewA2AAgent:
    """
    创建人工审核智能体实例
    
    Args:
        config: 配置参数
        
    Returns:
        人工审核智能体实例
    """
    return HumanReviewA2AAgent(config)


# 示例使用
async def main():
    """示例主函数"""
    # 创建审核智能体
    review_agent = create_human_review_a2a_agent()
    
    print("🔍 人工审核智能体演示")
    print("=" * 50)
    
    # 提交审核任务
    review_result = await review_agent.submit_for_review(
        content={
            "diagnosis": "根据症状分析，可能是阳虚体质",
            "recommendations": ["多吃温热食物", "适当运动", "保持充足睡眠"]
        },
        review_type="medical_diagnosis",
        user_id="user123",
        agent_id="xiaoke",
        priority="high"
    )
    
    print("审核提交结果:")
    print(json.dumps(review_result, ensure_ascii=False, indent=2))
    
    # 获取仪表板数据
    dashboard = await review_agent.get_review_dashboard()
    print("\n审核仪表板:")
    print(json.dumps(dashboard, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main()) 