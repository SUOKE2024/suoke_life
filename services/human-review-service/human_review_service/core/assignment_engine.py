"""
任务分配引擎
Assignment Engine

用于智能分配审核任务给合适的审核员
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
import structlog

from .models import ReviewerDB, ReviewTaskDB, ReviewType, ReviewPriority, ReviewerStatus

logger = structlog.get_logger(__name__)


class AssignmentEngine:
    """任务分配引擎"""
    
    def __init__(self):
        """初始化分配引擎"""
        self.specialty_mapping = {
            "medical_diagnosis": ["中医诊断", "西医诊断", "内科", "全科"],
            "treatment_plan": ["中医治疗", "西医治疗", "康复医学"],
            "medication_review": ["药学", "临床药学", "中药学"],
            "nutrition_advice": ["营养学", "临床营养", "中医养生"],
            "lifestyle_recommendation": ["健康管理", "预防医学", "中医养生"],
            "emergency_assessment": ["急诊医学", "内科", "外科"]
        }
    
    async def find_best_reviewer(
        self,
        task_type: ReviewType,
        priority: ReviewPriority,
        complexity_score: float,
        session: AsyncSession,
        excluded_reviewers: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        找到最适合的审核员
        
        Args:
            task_type: 任务类型
            priority: 优先级
            complexity_score: 复杂度评分
            session: 数据库会话
            excluded_reviewers: 排除的审核员ID列表
            
        Returns:
            最适合的审核员ID，如果没有找到则返回None
        """
        try:
            # 获取候选审核员
            candidates = await self._get_candidate_reviewers(
                task_type, session, excluded_reviewers
            )
            
            if not candidates:
                logger.warning(
                    "No candidate reviewers found",
                    task_type=task_type.value,
                    excluded_count=len(excluded_reviewers) if excluded_reviewers else 0
                )
                return None
            
            # 计算每个候选人的适配分数
            scored_candidates = []
            for reviewer in candidates:
                score = await self._calculate_assignment_score(
                    reviewer, task_type, priority, complexity_score, session
                )
                scored_candidates.append((reviewer, score))
            
            # 按分数排序，选择最高分的审核员
            scored_candidates.sort(key=lambda x: x[1], reverse=True)
            best_reviewer = scored_candidates[0][0]
            
            logger.info(
                "Best reviewer found",
                reviewer_id=best_reviewer.reviewer_id,
                reviewer_name=best_reviewer.name,
                score=scored_candidates[0][1],
                task_type=task_type.value,
                priority=priority.value
            )
            
            return best_reviewer.reviewer_id
            
        except Exception as e:
            logger.error(
                "Failed to find best reviewer",
                task_type=task_type.value,
                error=str(e)
            )
            return None
    
    async def _get_candidate_reviewers(
        self,
        task_type: ReviewType,
        session: AsyncSession,
        excluded_reviewers: Optional[List[str]] = None
    ) -> List[ReviewerDB]:
        """获取候选审核员列表"""
        # 获取任务类型对应的专业领域
        required_specialties = self.specialty_mapping.get(task_type.value, [])
        
        # 构建查询条件
        conditions = [
            ReviewerDB.status == ReviewerStatus.ACTIVE,
            ReviewerDB.is_available == True,
            ReviewerDB.current_task_count < ReviewerDB.max_concurrent_tasks
        ]
        
        # 排除指定的审核员
        if excluded_reviewers:
            conditions.append(~ReviewerDB.reviewer_id.in_(excluded_reviewers))
        
        # 如果有专业要求，添加专业过滤
        if required_specialties:
            specialty_conditions = []
            for specialty in required_specialties:
                specialty_conditions.append(
                    ReviewerDB.specialties.contains([specialty])
                )
            if specialty_conditions:
                conditions.append(or_(*specialty_conditions))
        
        # 执行查询
        result = await session.execute(
            select(ReviewerDB).where(and_(*conditions))
        )
        
        return result.scalars().all()
    
    async def _calculate_assignment_score(
        self,
        reviewer: ReviewerDB,
        task_type: ReviewType,
        priority: ReviewPriority,
        complexity_score: float,
        session: AsyncSession
    ) -> float:
        """
        计算审核员的任务分配分数
        
        分数越高表示越适合分配该任务
        """
        score = 0.0
        
        # 1. 专业匹配度 (0-40分)
        specialty_score = self._calculate_specialty_score(reviewer, task_type)
        score += specialty_score
        
        # 2. 工作负载 (0-25分)
        workload_score = self._calculate_workload_score(reviewer)
        score += workload_score
        
        # 3. 历史绩效 (0-20分)
        performance_score = self._calculate_performance_score(reviewer)
        score += performance_score
        
        # 4. 优先级匹配 (0-10分)
        priority_score = self._calculate_priority_score(reviewer, priority)
        score += priority_score
        
        # 5. 复杂度匹配 (0-5分)
        complexity_score_match = self._calculate_complexity_score(reviewer, complexity_score)
        score += complexity_score_match
        
        logger.debug(
            "Assignment score calculated",
            reviewer_id=reviewer.reviewer_id,
            total_score=score,
            specialty_score=specialty_score,
            workload_score=workload_score,
            performance_score=performance_score,
            priority_score=priority_score,
            complexity_score=complexity_score_match
        )
        
        return score
    
    def _calculate_specialty_score(self, reviewer: ReviewerDB, task_type: ReviewType) -> float:
        """计算专业匹配度分数"""
        required_specialties = self.specialty_mapping.get(task_type.value, [])
        if not required_specialties:
            return 20.0  # 如果没有特定专业要求，给予中等分数
        
        reviewer_specialties = reviewer.specialties or []
        
        # 计算匹配的专业数量
        matches = 0
        for specialty in required_specialties:
            if specialty in reviewer_specialties:
                matches += 1
        
        # 计算匹配度
        if matches == 0:
            return 0.0
        
        match_ratio = matches / len(required_specialties)
        return min(40.0 * match_ratio, 40.0)
    
    def _calculate_workload_score(self, reviewer: ReviewerDB) -> float:
        """计算工作负载分数"""
        if reviewer.max_concurrent_tasks == 0:
            return 0.0
        
        # 计算当前负载率
        load_ratio = reviewer.current_task_count / reviewer.max_concurrent_tasks
        
        # 负载越低，分数越高
        return 25.0 * (1.0 - load_ratio)
    
    def _calculate_performance_score(self, reviewer: ReviewerDB) -> float:
        """计算历史绩效分数"""
        # 基于质量评分和完成率
        quality_score = getattr(reviewer, 'quality_score', 0.8) or 0.8
        completion_rate = getattr(reviewer, 'completion_rate', 0.9) or 0.9
        
        # 综合绩效分数
        performance = (quality_score * 0.7 + completion_rate * 0.3)
        return 20.0 * performance
    
    def _calculate_priority_score(self, reviewer: ReviewerDB, priority: ReviewPriority) -> float:
        """计算优先级匹配分数"""
        # 高优先级任务优先分配给经验丰富的审核员
        reviewer_experience = getattr(reviewer, 'experience_level', 'intermediate')
        
        if priority in [ReviewPriority.URGENT, ReviewPriority.CRITICAL]:
            if reviewer_experience == 'senior':
                return 10.0
            elif reviewer_experience == 'intermediate':
                return 7.0
            else:
                return 3.0
        elif priority == ReviewPriority.HIGH:
            if reviewer_experience in ['senior', 'intermediate']:
                return 8.0
            else:
                return 5.0
        else:
            # 普通优先级任务可以分配给任何级别的审核员
            return 6.0
    
    def _calculate_complexity_score(self, reviewer: ReviewerDB, complexity_score: float) -> float:
        """计算复杂度匹配分数"""
        # 根据审核员的经验水平匹配复杂度
        reviewer_experience = getattr(reviewer, 'experience_level', 'intermediate')
        
        if complexity_score >= 0.8:  # 高复杂度
            if reviewer_experience == 'senior':
                return 5.0
            elif reviewer_experience == 'intermediate':
                return 3.0
            else:
                return 1.0
        elif complexity_score >= 0.5:  # 中等复杂度
            if reviewer_experience in ['senior', 'intermediate']:
                return 4.0
            else:
                return 3.0
        else:  # 低复杂度
            return 3.0  # 任何级别都可以处理 