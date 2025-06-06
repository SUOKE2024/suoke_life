"""
service - 索克生活项目模块
"""

from .assignment_engine import AssignmentEngine
from .config import settings
from .models import (
from .notification import NotificationService
from .risk_assessment import RiskAssessmentEngine
from datetime import datetime, timedelta, timezone
from sqlalchemy import and_, desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4
import structlog

"""
核心业务服务
Core Business Service

实现人工审核系统的主要业务逻辑
"""



    DashboardData,
    ReviewDecision,
    Reviewer,
    ReviewerCreate,
    ReviewerDB,
    ReviewerStatus,
    ReviewerUpdate,
    ReviewHistoryDB,
    ReviewPriority,
    ReviewStatistics,
    ReviewStatus,
    ReviewTask,
    ReviewTaskCreate,
    ReviewTaskDB,
    ReviewTaskUpdate,
    ReviewType,
)

logger = structlog.get_logger(__name__)

class HumanReviewService:
    """人工审核核心服务"""

    def __init__(self, session: Optional[AsyncSession] = None, redis_client=None):
        """初始化服务

        Args:
            session: 可选的数据库会话，主要用于测试
            redis_client: 可选的Redis客户端，用于通知服务
        """
        self.risk_engine = RiskAssessmentEngine()
        self.assignment_engine = AssignmentEngine()
        self._session = session
        self.notification_service = NotificationService(redis_client=redis_client)

    async def submit_review(
        self, review_data: ReviewTaskCreate, session: AsyncSession
    ) -> ReviewTask:
        """
        提交审核请求

        Args:
            review_data: 审核任务数据
            session: 数据库会话

        Returns:
            创建的审核任务
        """
        logger.info(
            "Submitting review request",
            review_type=review_data.review_type,
            user_id=review_data.user_id,
            agent_id=review_data.agent_id,
        )

        # 生成任务ID
        task_id = f"review_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}"

        # 风险评估
        risk_score = self.risk_engine.assess_risk(
            content_data=review_data.content, content_type=review_data.review_type.value
        )

        # 基于风险评分调整优先级
        assessed_priority = review_data.priority
        if risk_score >= 0.8:
            assessed_priority = ReviewPriority.CRITICAL
        elif risk_score >= 0.6:
            assessed_priority = ReviewPriority.URGENT

        # 计算过期时间
        expires_at = review_data.expires_at or (
            datetime.now(timezone.utc)
            + timedelta(seconds=settings.review.default_review_timeout)
        )

        # 创建数据库记录
        db_task = ReviewTaskDB(
            task_id=task_id,
            review_type=review_data.review_type,
            priority=assessed_priority,
            content=review_data.content,
            original_content=review_data.content.copy(),
            user_id=review_data.user_id,
            agent_id=review_data.agent_id,
            estimated_duration=review_data.estimated_duration,
            expires_at=expires_at,
            risk_score=risk_score,
        )

        session.add(db_task)
        await session.commit()
        await session.refresh(db_task)

        # 记录历史
        await self._add_history_record(
            session=session,
            task_id=db_task.id,
            action="created",
            actor_id="system",
            actor_type="system",
            details={
                "risk_score": risk_score,
                "assessed_priority": assessed_priority.value,
            },
        )

        # 检查是否需要人工审核
        if await self._needs_human_review(db_task):
            # 自动分配审核员（如果启用）
            if settings.review.auto_assign_reviews:
                await self._auto_assign_reviewer(db_task, session)
        else:
            # 自动通过
            await self._auto_approve_task(db_task, session)

        # 转换为Pydantic模型
        task = ReviewTask.model_validate(db_task)

        logger.info(
            "Review request submitted successfully",
            task_id=task_id,
            status=task.status,
            priority=task.priority,
            risk_score=risk_score,
        )

        return task

    async def create_task(
        self, session: AsyncSession, review_data: ReviewTaskCreate
    ) -> ReviewTask:
        """
        创建审核任务（别名方法，用于测试兼容性）

        Args:
            session: 数据库会话
            review_data: 审核任务数据

        Returns:
            创建的审核任务
        """
        return await self.submit_review(review_data, session)

    async def get_task(
        self, session: AsyncSession, task_id: str
    ) -> Optional[ReviewTask]:
        """
        获取审核任务（别名方法，用于测试兼容性）

        Args:
            session: 数据库会话
            task_id: 任务ID

        Returns:
            审核任务或None
        """
        return await self.get_review_task(task_id, session)

    async def get_review_task(
        self, task_id: str, session: AsyncSession
    ) -> Optional[ReviewTask]:
        """
        获取审核任务

        Args:
            task_id: 任务ID
            session: 数据库会话

        Returns:
            审核任务或None
        """
        result = await session.execute(
            select(ReviewTaskDB)
            .filter(ReviewTaskDB.task_id == task_id)
            .options(selectinload(ReviewTaskDB.reviewer))
        )
        db_task = result.scalar_one_or_none()

        if not db_task:
            return None

        return ReviewTask.model_validate(db_task)

    async def complete_review(
        self,
        task_id: str,
        reviewer_id: str,
        decision: ReviewDecision,
        session: AsyncSession,
    ) -> ReviewTask:
        """
        完成审核

        Args:
            task_id: 任务ID
            reviewer_id: 审核员ID
            decision: 审核决策
            session: 数据库会话

        Returns:
            更新后的审核任务
        """
        logger.info(
            "Completing review",
            task_id=task_id,
            reviewer_id=reviewer_id,
            decision=decision.decision,
        )

        # 获取任务
        result = await session.execute(
            select(ReviewTaskDB)
            .filter(ReviewTaskDB.task_id == task_id)
            .options(selectinload(ReviewTaskDB.reviewer))
        )
        db_task = result.scalar_one_or_none()

        if not db_task:
            raise ValueError(f"Task {task_id} not found")

        if db_task.status not in [ReviewStatus.ASSIGNED, ReviewStatus.IN_PROGRESS]:
            raise ValueError(f"Task {task_id} is not in reviewable state")

        if db_task.assigned_to != reviewer_id:
            raise ValueError(
                f"Task {task_id} is not assigned to reviewer {reviewer_id}"
            )

        # 计算实际审核时间
        actual_duration = None
        if db_task.started_at:
            actual_duration = int(
                (datetime.now(timezone.utc) - db_task.started_at).total_seconds()
            )

        # 更新任务状态
        old_status = db_task.status
        db_task.status = decision.decision
        db_task.review_comments = decision.comments
        db_task.reviewer_notes = decision.reviewer_notes
        db_task.review_result = decision.review_result
        db_task.completed_at = datetime.now(timezone.utc)
        db_task.actual_duration = actual_duration

        await session.commit()

        # 更新审核员统计
        await self._update_reviewer_stats(
            reviewer_id, decision.decision, actual_duration, session
        )

        # 记录历史
        await self._add_history_record(
            session=session,
            task_id=db_task.id,
            action="completed",
            old_status=old_status,
            new_status=decision.decision,
            actor_id=reviewer_id,
            actor_type="reviewer",
            details={"actual_duration": actual_duration, "comments": decision.comments},
            comments=decision.comments,
        )

        # 发送任务完成通知
        try:
            task_obj = ReviewTask.model_validate(db_task)
            reviewer_obj = await self.get_reviewer(reviewer_id, session)
            if reviewer_obj:
                await self.notification_service.notify_task_completed(
                    task=task_obj,
                    reviewer=reviewer_obj
                )
        except Exception as e:
            logger.warning(
                "Failed to send task completion notification",
                task_id=task_id,
                reviewer_id=reviewer_id,
                error=str(e)
            )

        task = ReviewTask.model_validate(db_task)

        logger.info(
            "Review completed successfully",
            task_id=task_id,
            decision=decision.decision,
            actual_duration=actual_duration,
        )

        return task

    async def assign_reviewer(
        self, task_id: str, reviewer_id: str, session: AsyncSession
    ) -> ReviewTask:
        """
        分配审核员

        Args:
            task_id: 任务ID
            reviewer_id: 审核员ID
            session: 数据库会话

        Returns:
            更新后的审核任务
        """
        logger.info("Assigning reviewer", task_id=task_id, reviewer_id=reviewer_id)

        # 获取任务
        result = await session.execute(
            select(ReviewTaskDB).filter(ReviewTaskDB.task_id == task_id)
        )
        db_task = result.scalar_one_or_none()

        if not db_task:
            raise ValueError(f"Task {task_id} not found")

        if db_task.status != ReviewStatus.PENDING:
            raise ValueError(f"Task {task_id} is not in pending state")

        # 检查审核员可用性
        reviewer = await self.get_reviewer(reviewer_id, session)
        if not reviewer or not reviewer.is_available:
            raise ValueError(f"Reviewer {reviewer_id} is not available")

        if reviewer.current_task_count >= reviewer.max_concurrent_tasks:
            raise ValueError(
                f"Reviewer {reviewer_id} has reached maximum concurrent tasks"
            )

        # 更新任务
        old_status = db_task.status
        db_task.status = ReviewStatus.ASSIGNED
        db_task.assigned_to = reviewer_id
        db_task.assigned_at = datetime.now(timezone.utc)

        # 更新审核员任务计数
        result = await session.execute(
            select(ReviewerDB).filter(ReviewerDB.reviewer_id == reviewer_id)
        )
        reviewer_db = result.scalar_one_or_none()
        if reviewer_db:
            reviewer_db.current_task_count += 1

        await session.commit()

        # 记录历史
        await self._add_history_record(
            session=session,
            task_id=db_task.id,
            action="assigned",
            old_status=old_status,
            new_status=ReviewStatus.ASSIGNED,
            actor_id="system",
            actor_type="system",
            details={"assigned_to": reviewer_id},
        )

        # 发送任务分配通知
        try:
            task_obj = ReviewTask.model_validate(db_task)
            reviewer_obj = Reviewer.model_validate(reviewer_db)
            await self.notification_service.notify_task_assigned(
                task=task_obj,
                reviewer=reviewer_obj
            )
        except Exception as e:
            logger.warning(
                "Failed to send task assignment notification",
                task_id=task_id,
                reviewer_id=reviewer_id,
                error=str(e)
            )

        task = ReviewTask.model_validate(db_task)

        logger.info(
            "Reviewer assigned successfully", task_id=task_id, reviewer_id=reviewer_id
        )

        return task

    async def start_review(
        self, task_id: str, reviewer_id: str, session: AsyncSession
    ) -> ReviewTask:
        """
        开始审核

        Args:
            task_id: 任务ID
            reviewer_id: 审核员ID
            session: 数据库会话

        Returns:
            更新后的审核任务
        """
        # 获取任务
        result = await session.execute(
            select(ReviewTaskDB).filter(ReviewTaskDB.task_id == task_id)
        )
        db_task = result.scalar_one_or_none()

        if not db_task:
            raise ValueError(f"Task {task_id} not found")

        if db_task.status != ReviewStatus.ASSIGNED:
            raise ValueError(f"Task {task_id} is not in assigned state")

        if db_task.assigned_to != reviewer_id:
            raise ValueError(
                f"Task {task_id} is not assigned to reviewer {reviewer_id}"
            )

        # 更新任务状态
        old_status = db_task.status
        db_task.status = ReviewStatus.IN_PROGRESS
        db_task.started_at = datetime.now(timezone.utc)

        await session.commit()

        # 记录历史
        await self._add_history_record(
            session=session,
            task_id=db_task.id,
            action="started",
            old_status=old_status,
            new_status=ReviewStatus.IN_PROGRESS,
            actor_id=reviewer_id,
            actor_type="reviewer",
        )

        return ReviewTask.model_validate(db_task)

    async def cancel_review_task(self, task_id: str, session: AsyncSession) -> bool:
        """
        取消审核任务

        Args:
            task_id: 任务ID
            session: 数据库会话

        Returns:
            是否成功取消
        """
        logger.info("Cancelling review task", task_id=task_id)

        # 获取任务
        result = await session.execute(
            select(ReviewTaskDB).filter(ReviewTaskDB.task_id == task_id)
        )
        db_task = result.scalar_one_or_none()

        if not db_task:
            return False

        # 检查任务状态是否可以取消
        if db_task.status in [
            ReviewStatus.APPROVED,
            ReviewStatus.REJECTED,
            ReviewStatus.CANCELLED,
        ]:
            raise ValueError(
                f"Task {task_id} cannot be cancelled in current state: {db_task.status}"
            )

        old_status = db_task.status
        assigned_reviewer = db_task.assigned_to

        # 更新任务状态
        db_task.status = ReviewStatus.CANCELLED
        db_task.completed_at = datetime.now(timezone.utc)

        # 如果任务已分配，需要减少审核员的任务计数
        if assigned_reviewer:
            await session.execute(
                update(ReviewerDB)
                .where(ReviewerDB.reviewer_id == assigned_reviewer)
                .values(
                    current_task_count=func.greatest(
                        0, ReviewerDB.current_task_count - 1
                    )
                )
            )

        await session.commit()

        # 记录历史
        await self._add_history_record(
            session=session,
            task_id=db_task.id,
            action="cancelled",
            old_status=old_status,
            new_status=ReviewStatus.CANCELLED,
            actor_id="system",
            actor_type="system",
            details={"reason": "manual_cancellation"},
        )

        logger.info(
            "Review task cancelled successfully",
            task_id=task_id,
            old_status=old_status,
            assigned_reviewer=assigned_reviewer,
        )

        return True

    async def get_pending_tasks(
        self, session: AsyncSession, limit: int = 50, offset: int = 0
    ) -> List[ReviewTask]:
        """
        获取待审核任务列表

        Args:
            limit: 限制数量
            offset: 偏移量
            session: 数据库会话

        Returns:
            待审核任务列表
        """
        result = await session.execute(
            select(ReviewTaskDB)
            .filter(
                ReviewTaskDB.status.in_([ReviewStatus.PENDING, ReviewStatus.ASSIGNED])
            )
            .order_by(
                desc(ReviewTaskDB.priority),
                desc(ReviewTaskDB.risk_score),
                ReviewTaskDB.created_at,
            )
            .limit(limit)
            .offset(offset)
            .options(selectinload(ReviewTaskDB.reviewer))
        )

        db_tasks = result.scalars().all()[:1000]  # 限制查询结果数量
        return [ReviewTask.model_validate(task) for task in db_tasks]

    async def get_reviewer_tasks(
        self,
        reviewer_id: str,
        session: AsyncSession,
        status: Optional[ReviewStatus] = None,
        limit: int = 50,
    ) -> List[ReviewTask]:
        """
        获取审核员的任务列表

        Args:
            reviewer_id: 审核员ID
            status: 任务状态过滤
            limit: 限制数量
            session: 数据库会话

        Returns:
            任务列表
        """
        query = select(ReviewTaskDB).filter(ReviewTaskDB.assigned_to == reviewer_id)

        if status:
            query = query.filter(ReviewTaskDB.status == status)

        result = await session.execute(
            query.order_by(desc(ReviewTaskDB.created_at))
            .limit(limit)
            .options(selectinload(ReviewTaskDB.reviewer))
        )

        db_tasks = result.scalars().all()[:1000]  # 限制查询结果数量
        return [ReviewTask.model_validate(task) for task in db_tasks]

    async def get_dashboard_data(self, session: AsyncSession) -> DashboardData:
        """
        获取仪表板数据

        Args:
            session: 数据库会话

        Returns:
            仪表板数据
        """
        # 获取统计数据
        statistics = await self._get_review_statistics(session)

        # 获取待审核任务
        pending_tasks = await self.get_pending_tasks(session=session, limit=10)

        # 获取活跃审核员
        active_reviewers = await self.get_active_reviewers(session=session)

        # 获取最近完成的任务
        recent_completions = await self._get_recent_completions(session=session)

        # 计算实时指标
        current_load = await self._calculate_current_load(session)
        estimated_wait_time = await self._estimate_wait_time(session)

        return DashboardData(
            statistics=statistics,
            pending_tasks=pending_tasks,
            active_reviewers=active_reviewers,
            recent_completions=recent_completions,
            current_load=current_load,
            estimated_wait_time=estimated_wait_time,
        )

    # 审核员管理方法

    async def create_reviewer(
        self, reviewer_data: ReviewerCreate, session: AsyncSession
    ) -> Reviewer:
        """创建审核员"""
        try:
            db_reviewer = ReviewerDB(**reviewer_data.model_dump())
            session.add(db_reviewer)
            await session.commit()
            await session.refresh(db_reviewer)

            logger.info(
                "Reviewer created",
                reviewer_id=reviewer_data.reviewer_id,
                name=reviewer_data.name,
            )

            return Reviewer.model_validate(db_reviewer)
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to create reviewer: {e}")
            raise

    async def get_reviewer(
        self, reviewer_id: str, session: AsyncSession
    ) -> Optional[Reviewer]:
        """获取审核员信息"""
        result = await session.execute(
            select(ReviewerDB).filter(ReviewerDB.reviewer_id == reviewer_id)
        )
        db_reviewer = result.scalar_one_or_none()

        if not db_reviewer:
            return None

        return Reviewer.model_validate(db_reviewer)

    async def update_reviewer(
        self, reviewer_id: str, update_data: ReviewerUpdate, session: AsyncSession
    ) -> Optional[Reviewer]:
        """更新审核员信息"""
        result = await session.execute(
            select(ReviewerDB).filter(ReviewerDB.reviewer_id == reviewer_id)
        )
        db_reviewer = result.scalar_one_or_none()

        if not db_reviewer:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(db_reviewer, field, value)

        db_reviewer.updated_at = datetime.now(timezone.utc)
        await session.commit()

        return Reviewer.model_validate(db_reviewer)

    async def get_active_reviewers(self, session: AsyncSession) -> List[Reviewer]:
        """获取活跃审核员列表"""
        result = await session.execute(
            select(ReviewerDB)
            .filter(ReviewerDB.status == ReviewerStatus.ACTIVE)
            .filter(ReviewerDB.is_available == True)
            .order_by(ReviewerDB.quality_score.desc())
        )

        db_reviewers = result.scalars().all()[:1000]  # 限制查询结果数量
        return [Reviewer.model_validate(reviewer) for reviewer in db_reviewers]

    async def list_reviewers(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 50,
        offset: int = 0,
        session: AsyncSession = None,
    ) -> List[Reviewer]:
        """获取审核员列表"""
        query = select(ReviewerDB)

        if filters:
            if "status" in filters:
                query = query.filter(ReviewerDB.status == filters["status"])
            if "specialty" in filters:
                query = query.filter(
                    ReviewerDB.specialties.contains(filters["specialty"])
                )
            if "is_available" in filters:
                query = query.filter(ReviewerDB.is_available == filters["is_available"])

        query = query.order_by(ReviewerDB.created_at.desc())
        query = query.offset(offset).limit(limit)

        result = await session.execute(query)
        db_reviewers = result.scalars().all()[:1000]  # 限制查询结果数量
        return [Reviewer.model_validate(reviewer) for reviewer in db_reviewers]

    async def list_review_tasks(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 50,
        offset: int = 0,
        session: AsyncSession = None,
    ) -> List[ReviewTask]:
        """获取审核任务列表"""
        query = select(ReviewTaskDB)

        if filters:
            if "status" in filters:
                query = query.filter(ReviewTaskDB.status == filters["status"])
            if "priority" in filters:
                query = query.filter(ReviewTaskDB.priority == filters["priority"])
            if "review_type" in filters:
                query = query.filter(ReviewTaskDB.review_type == filters["review_type"])
            if "assigned_to" in filters:
                query = query.filter(ReviewTaskDB.assigned_to == filters["assigned_to"])
            if "user_id" in filters:
                query = query.filter(ReviewTaskDB.user_id == filters["user_id"])

        query = query.order_by(ReviewTaskDB.created_at.desc())
        query = query.offset(offset).limit(limit)

        result = await session.execute(query)
        db_tasks = result.scalars().all()[:1000]  # 限制查询结果数量
        return [ReviewTask.model_validate(task) for task in db_tasks]

    async def list_tasks(
        self,
        session: AsyncSession,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ReviewTask]:
        """
        列出审核任务（别名方法，用于测试兼容性）

        Args:
            session: 数据库会话
            filters: 过滤条件
            limit: 限制数量
            offset: 偏移量

        Returns:
            审核任务列表
        """
        return await self.list_review_tasks(filters, limit, offset, session)

    async def update_task(
        self, session: AsyncSession, task_id: str, update_data: ReviewTaskUpdate
    ) -> Optional[ReviewTask]:
        """
        更新审核任务（别名方法，用于测试兼容性）

        Args:
            session: 数据库会话
            task_id: 任务ID
            update_data: 更新数据

        Returns:
            更新后的审核任务
        """
        return await self.update_review_task(task_id, update_data, session)

    async def delete_task(self, session: AsyncSession, task_id: str) -> bool:
        """
        删除审核任务

        Args:
            session: 数据库会话
            task_id: 任务ID

        Returns:
            是否删除成功
        """
        result = await session.execute(
            select(ReviewTaskDB).filter(ReviewTaskDB.task_id == task_id)
        )
        db_task = result.scalar_one_or_none()

        if not db_task:
            return False

        await session.delete(db_task)
        await session.commit()

        logger.info("Review task deleted", task_id=task_id)
        return True

    async def update_review_task(
        self, task_id: str, update_data: ReviewTaskUpdate, session: AsyncSession
    ) -> Optional[ReviewTask]:
        """更新审核任务"""
        result = await session.execute(
            select(ReviewTaskDB).filter(ReviewTaskDB.task_id == task_id)
        )
        db_task = result.scalar_one_or_none()

        if not db_task:
            return None

        # 更新字段
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(db_task, field):
                setattr(db_task, field, value)

        db_task.updated_at = datetime.now(timezone.utc)
        await session.commit()

        return ReviewTask.model_validate(db_task)

    async def get_review_statistics(self, session: AsyncSession) -> Dict[str, Any]:
        """获取审核统计数据"""
        stats = await self._get_review_statistics(session)
        return {
            "total_tasks": stats.total_tasks,
            "pending_tasks": stats.pending_tasks,
            "in_progress_tasks": stats.in_progress_tasks,
            "completed_tasks": stats.completed_tasks,
            "approved_tasks": stats.approved_tasks,
            "rejected_tasks": stats.rejected_tasks,
            "average_review_time": stats.average_review_time,
            "reviewer_count": stats.reviewer_count,
            "active_reviewers": stats.active_reviewers,
        }

    async def activate_reviewer(
        self, reviewer_id: str, session: AsyncSession
    ) -> Optional[Reviewer]:
        """激活审核员"""
        result = await session.execute(
            select(ReviewerDB).filter(ReviewerDB.reviewer_id == reviewer_id)
        )
        db_reviewer = result.scalar_one_or_none()

        if not db_reviewer:
            return None

        db_reviewer.status = ReviewerStatus.ACTIVE
        db_reviewer.is_available = True
        db_reviewer.updated_at = datetime.now(timezone.utc)

        await session.commit()
        return Reviewer.model_validate(db_reviewer)

    async def deactivate_reviewer(
        self, reviewer_id: str, session: AsyncSession
    ) -> Optional[Reviewer]:
        """停用审核员"""
        result = await session.execute(
            select(ReviewerDB).filter(ReviewerDB.reviewer_id == reviewer_id)
        )
        db_reviewer = result.scalar_one_or_none()

        if not db_reviewer:
            return None

        db_reviewer.status = ReviewerStatus.INACTIVE
        db_reviewer.is_available = False
        db_reviewer.updated_at = datetime.now(timezone.utc)

        await session.commit()
        return Reviewer.model_validate(db_reviewer)

    async def get_reviewer_workload(
        self, reviewer_id: str, session: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """获取审核员工作负载"""
        result = await session.execute(
            select(ReviewerDB).filter(ReviewerDB.reviewer_id == reviewer_id)
        )
        db_reviewer = result.scalar_one_or_none()

        if not db_reviewer:
            return None

        # 获取当前任务数
        current_tasks_result = await session.execute(
            select(func.count(ReviewTaskDB.id))
            .filter(ReviewTaskDB.assigned_to == reviewer_id)
            .filter(ReviewTaskDB.status == ReviewStatus.IN_PROGRESS)
        )
        current_tasks = current_tasks_result.scalar() or 0

        return {
            "reviewer_id": reviewer_id,
            "current_tasks": current_tasks,
            "max_concurrent_tasks": db_reviewer.max_concurrent_tasks,
            "utilization": (
                current_tasks / db_reviewer.max_concurrent_tasks
                if db_reviewer.max_concurrent_tasks > 0
                else 0
            ),
            "is_available": db_reviewer.is_available,
            "status": db_reviewer.status.value,
        }

    async def get_reviewer_performance(
        self, reviewer_id: str, days: int, session: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """获取审核员绩效统计"""
        result = await session.execute(
            select(ReviewerDB).filter(ReviewerDB.reviewer_id == reviewer_id)
        )
        db_reviewer = result.scalar_one_or_none()

        if not db_reviewer:
            return None

        # 计算时间范围
        start_date = datetime.now(timezone.utc) - timedelta(days=days)

        # 获取期间内的任务统计
        tasks_result = await session.execute(
            select(
                func.count(ReviewTaskDB.id).label("total_reviews"),
                func.count(ReviewTaskDB.id)
                .filter(ReviewTaskDB.status == ReviewStatus.APPROVED)
                .label("approved_reviews"),
                func.count(ReviewTaskDB.id)
                .filter(ReviewTaskDB.status == ReviewStatus.REJECTED)
                .label("rejected_reviews"),
                func.avg(ReviewTaskDB.actual_duration).label("avg_review_time"),
            )
            .filter(ReviewTaskDB.assigned_to == reviewer_id)
            .filter(ReviewTaskDB.completed_at >= start_date)
        )

        stats = tasks_result.first()

        return {
            "reviewer_id": reviewer_id,
            "period_days": days,
            "total_reviews": stats.total_reviews or 0,
            "approved_reviews": stats.approved_reviews or 0,
            "rejected_reviews": stats.rejected_reviews or 0,
            "approval_rate": (
                (stats.approved_reviews / stats.total_reviews * 100)
                if stats.total_reviews > 0
                else 0
            ),
            "average_review_time": float(stats.avg_review_time or 0),
            "quality_score": db_reviewer.quality_score,
        }

    async def delete_reviewer(self, reviewer_id: str, session: AsyncSession) -> bool:
        """删除审核员"""
        result = await session.execute(
            select(ReviewerDB).filter(ReviewerDB.reviewer_id == reviewer_id)
        )
        db_reviewer = result.scalar_one_or_none()

        if not db_reviewer:
            return False

        # 检查是否有进行中的任务
        active_tasks_result = await session.execute(
            select(func.count(ReviewTaskDB.id))
            .filter(ReviewTaskDB.assigned_to == reviewer_id)
            .filter(ReviewTaskDB.status == ReviewStatus.IN_PROGRESS)
        )
        active_tasks = active_tasks_result.scalar() or 0

        if active_tasks > 0:
            raise ValueError(
                f"Cannot delete reviewer {reviewer_id}: has {active_tasks} active tasks"
            )

        await session.delete(db_reviewer)
        await session.commit()
        return True

    async def get_real_time_metrics(self, session: AsyncSession) -> Dict[str, Any]:
        """获取实时指标"""
        current_load = await self._calculate_current_load(session)
        wait_time = await self._estimate_wait_time(session)

        # 获取活跃任务数
        active_tasks_result = await session.execute(
            select(func.count(ReviewTaskDB.id)).filter(
                ReviewTaskDB.status == ReviewStatus.IN_PROGRESS
            )
        )
        active_tasks = active_tasks_result.scalar() or 0

        # 获取可用审核员数
        available_reviewers_result = await session.execute(
            select(func.count(ReviewerDB.id))
            .filter(ReviewerDB.status == ReviewerStatus.ACTIVE)
            .filter(ReviewerDB.is_available == True)
        )
        available_reviewers = available_reviewers_result.scalar() or 0

        return {
            "current_load": current_load,
            "active_tasks": active_tasks,
            "available_reviewers": available_reviewers,
            "average_wait_time": wait_time,
        }

    async def get_hourly_trends(
        self, hours: int, session: AsyncSession
    ) -> List[Dict[str, Any]]:
        """获取小时趋势"""
        # 简化实现，返回模拟数据
        trends = []
        for i in range(hours):
            trends.append({"hour": i, "completed_tasks": 0, "average_duration": 0})
        return trends

    async def get_daily_trends(
        self, days: int, session: AsyncSession
    ) -> List[Dict[str, Any]]:
        """获取日趋势"""
        # 简化实现，返回模拟数据
        trends = []
        for i in range(days):
            trends.append({"day": i, "completed_tasks": 0, "average_duration": 0})
        return trends

    async def get_reviewer_performance_ranking(
        self, days: int, limit: int, session: AsyncSession
    ) -> List[Dict[str, Any]]:
        """获取审核员绩效排行"""
        # 简化实现，返回模拟数据
        ranking = []
        for i in range(min(limit, 5)):
            ranking.append(
                {
                    "reviewer_id": f"reviewer_{i}",
                    "name": f"审核员{i}",
                    "total_reviews": 0,
                    "approval_rate": 0.0,
                    "quality_score": 5.0,
                }
            )
        return ranking

    async def get_workload_distribution(self, session: AsyncSession) -> Dict[str, Any]:
        """获取工作负载分布"""
        # 简化实现，返回模拟数据
        return {
            "total_reviewers": 0,
            "active_reviewers": 0,
            "overloaded_reviewers": 0,
            "average_utilization": 0.0,
        }

    async def get_quality_metrics(
        self, days: int, session: AsyncSession
    ) -> Dict[str, Any]:
        """获取质量指标"""
        # 简化实现，返回模拟数据
        return {
            "average_quality_score": 5.0,
            "approval_rate": 0.0,
            "revision_rate": 0.0,
            "consistency_score": 5.0,
        }

    async def get_system_alerts(
        self, severity: Optional[str], limit: int, session: AsyncSession
    ) -> List[Dict[str, Any]]:
        """获取系统告警"""
        # 简化实现，返回空列表
        return []

    # 私有辅助方法

    async def _needs_human_review(self, task: ReviewTaskDB) -> bool:
        """判断是否需要人工审核"""
        # 强制人工审核的类型
        if task.review_type.value in settings.review.mandatory_review_types:
            return True

        # 可自动通过的类型
        if task.review_type.value in settings.review.auto_approve_types:
            return False

        # 基于风险评分判断
        if task.risk_score >= settings.review.risk_thresholds["high"]:
            return True

        # 高优先级需要人工审核
        if task.priority in [ReviewPriority.URGENT, ReviewPriority.CRITICAL]:
            return True

        return True  # 默认需要人工审核

    async def _auto_approve_task(
        self, task: ReviewTaskDB, session: AsyncSession
    ) -> None:
        """自动通过任务"""
        task.status = ReviewStatus.APPROVED
        task.completed_at = datetime.now(timezone.utc)
        task.review_comments = "系统自动通过"

        await session.commit()

        # 记录历史
        await self._add_history_record(
            session=session,
            task_id=task.id,
            action="auto_approved",
            old_status=ReviewStatus.PENDING,
            new_status=ReviewStatus.APPROVED,
            actor_id="system",
            actor_type="system",
            details={"reason": "auto_approve_type"},
        )

    async def _auto_assign_reviewer(
        self, task: ReviewTaskDB, session: AsyncSession
    ) -> None:
        """自动分配审核员"""
        try:
            reviewer_id = await self.assignment_engine.find_best_reviewer(
                task_type=task.review_type,
                priority=task.priority,
                complexity_score=getattr(task, "complexity_score", 0.5),
                session=session,
            )

            if reviewer_id:
                await self.assign_reviewer(task.task_id, reviewer_id, session)
        except Exception as e:
            logger.warning(
                "Failed to auto-assign reviewer", task_id=task.task_id, error=str(e)
            )

    async def _add_history_record(
        self,
        session: AsyncSession,
        task_id: Any,
        action: str,
        actor_id: str,
        actor_type: str,
        old_status: Optional[ReviewStatus] = None,
        new_status: Optional[ReviewStatus] = None,
        details: Optional[Dict[str, Any]] = None,
        comments: Optional[str] = None,
    ) -> None:
        """添加历史记录"""
        history = ReviewHistoryDB(
            task_id=task_id,
            action=action,
            old_status=old_status,
            new_status=new_status,
            actor_id=actor_id,
            actor_type=actor_type,
            details=details,
            comments=comments,
        )

        session.add(history)
        await session.commit()

    async def _update_reviewer_stats(
        self,
        reviewer_id: str,
        decision: ReviewStatus,
        duration: Optional[int],
        session: AsyncSession,
    ) -> None:
        """更新审核员统计信息"""
        result = await session.execute(
            select(ReviewerDB).filter(ReviewerDB.reviewer_id == reviewer_id)
        )
        reviewer = result.scalar_one_or_none()

        if not reviewer:
            return

        # 更新统计
        reviewer.total_reviews += 1
        reviewer.current_task_count = max(0, reviewer.current_task_count - 1)
        reviewer.last_active_at = datetime.now(timezone.utc)

        if decision == ReviewStatus.APPROVED:
            reviewer.approved_reviews += 1
        elif decision == ReviewStatus.REJECTED:
            reviewer.rejected_reviews += 1

        # 更新平均审核时间
        if duration and duration > 0:
            total_time = (
                reviewer.average_review_time * (reviewer.total_reviews - 1) + duration
            )
            reviewer.average_review_time = total_time / reviewer.total_reviews

        await session.commit()

    async def _get_review_statistics(self, session: AsyncSession) -> ReviewStatistics:
        """获取审核统计数据"""
        # 基础统计查询
        result = await session.execute(
            select(
                func.count(ReviewTaskDB.id).label("total"),
                func.count(ReviewTaskDB.id)
                .filter(ReviewTaskDB.status == ReviewStatus.PENDING)
                .label("pending"),
                func.count(ReviewTaskDB.id)
                .filter(ReviewTaskDB.status == ReviewStatus.IN_PROGRESS)
                .label("in_progress"),
                func.count(ReviewTaskDB.id)
                .filter(
                    ReviewTaskDB.status.in_(
                        [
                            ReviewStatus.APPROVED,
                            ReviewStatus.REJECTED,
                            ReviewStatus.NEEDS_REVISION,
                        ]
                    )
                )
                .label("completed"),
                func.count(ReviewTaskDB.id)
                .filter(ReviewTaskDB.status == ReviewStatus.APPROVED)
                .label("approved"),
                func.count(ReviewTaskDB.id)
                .filter(ReviewTaskDB.status == ReviewStatus.REJECTED)
                .label("rejected"),
                func.avg(ReviewTaskDB.actual_duration).label("avg_review_time"),
            )
        )

        stats = result.first()

        # 审核员统计
        reviewer_result = await session.execute(
            select(
                func.count(ReviewerDB.id).label("total_reviewers"),
                func.count(ReviewerDB.id)
                .filter(ReviewerDB.status == ReviewerStatus.ACTIVE)
                .label("active_reviewers"),
            )
        )

        reviewer_stats = reviewer_result.first()

        return ReviewStatistics(
            total_tasks=stats.total or 0,
            pending_tasks=stats.pending or 0,
            in_progress_tasks=stats.in_progress or 0,
            completed_tasks=stats.completed or 0,
            approved_tasks=stats.approved or 0,
            rejected_tasks=stats.rejected or 0,
            average_review_time=float(stats.avg_review_time or 0),
            reviewer_count=reviewer_stats.total_reviewers or 0,
            active_reviewers=reviewer_stats.active_reviewers or 0,
        )

    async def _get_recent_completions(
        self, session: AsyncSession, limit: int = 5
    ) -> List[ReviewTask]:
        """获取最近完成的任务"""
        result = await session.execute(
            select(ReviewTaskDB)
            .filter(
                ReviewTaskDB.status.in_(
                    [
                        ReviewStatus.APPROVED,
                        ReviewStatus.REJECTED,
                        ReviewStatus.NEEDS_REVISION,
                    ]
                )
            )
            .order_by(desc(ReviewTaskDB.completed_at))
            .limit(limit)
            .options(selectinload(ReviewTaskDB.reviewer))
        )

        db_tasks = result.scalars().all()[:1000]  # 限制查询结果数量
        return [ReviewTask.model_validate(task) for task in db_tasks]

    async def _calculate_current_load(self, session: AsyncSession) -> float:
        """计算当前负载百分比"""
        # 获取当前进行中的任务数
        result = await session.execute(
            select(func.count(ReviewTaskDB.id)).filter(
                ReviewTaskDB.status.in_(
                    [ReviewStatus.ASSIGNED, ReviewStatus.IN_PROGRESS]
                )
            )
        )

        current_tasks = result.scalar() or 0
        max_capacity = settings.review.max_concurrent_reviews

        return (
            min(100.0, (current_tasks / max_capacity) * 100.0)
            if max_capacity > 0
            else 0.0
        )

    async def _estimate_wait_time(self, session: AsyncSession) -> int:
        """估算等待时间（分钟）"""
        # 获取待审核任务数
        result = await session.execute(
            select(func.count(ReviewTaskDB.id)).filter(
                ReviewTaskDB.status == ReviewStatus.PENDING
            )
        )

        pending_count = result.scalar() or 0

        if pending_count == 0:
            return 0

        # 获取活跃审核员数
        reviewer_result = await session.execute(
            select(func.count(ReviewerDB.id)).filter(
                and_(
                    ReviewerDB.status == ReviewerStatus.ACTIVE,
                    ReviewerDB.is_available == True,
                )
            )
        )

        active_reviewers = reviewer_result.scalar() or 1

        # 简单估算：待审核任务数 / 活跃审核员数 * 平均审核时间
        avg_review_time_minutes = settings.review.default_review_timeout / 60
        estimated_minutes = (pending_count / active_reviewers) * avg_review_time_minutes

        return int(estimated_minutes)
