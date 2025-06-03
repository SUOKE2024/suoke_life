"""
服务层测试
Service Layer Tests

测试核心业务逻辑
"""

import pytest

from ..core.models import (
    ReviewerCreate,
    ReviewerStatus,
    ReviewerUpdate,
    ReviewPriority,
    ReviewStatus,
    ReviewTaskCreate,
    ReviewTaskUpdate,
    ReviewType,
)
from ..core.service import HumanReviewService

class TestHumanReviewService:
    """人工审核服务测试"""

    @pytest.mark.asyncio
    async def test_create_reviewer(self, db_session):
        """测试创建审核员"""
        service = HumanReviewService(db_session)

        reviewer_data = ReviewerCreate(
            name="测试医生",
            email="test@example.com",
            specialties=["中医诊断", "方剂学"],
            max_concurrent_tasks=5,
        )

        reviewer = await service.create_reviewer(reviewer_data)

        assert reviewer.name == "测试医生"
        assert reviewer.email == "test@example.com"
        assert reviewer.specialties == ["中医诊断", "方剂学"]
        assert reviewer.max_concurrent_tasks == 5
        assert reviewer.status == ReviewerStatus.ACTIVE
        assert reviewer.current_task_count == 0
        assert reviewer.is_available is True

    @pytest.mark.asyncio
    async def test_get_reviewer(self, db_session):
        """测试获取审核员"""
        service = HumanReviewService(db_session)

        # 创建审核员
        reviewer_data = ReviewerCreate(
            name="测试医生2",
            email="test2@example.com",
            specialties=["西医诊断"],
            max_concurrent_tasks=3,
        )
        created_reviewer = await service.create_reviewer(reviewer_data)

        # 获取审核员
        reviewer = await service.get_reviewer(created_reviewer.reviewer_id)

        assert reviewer is not None
        assert reviewer.reviewer_id == created_reviewer.reviewer_id
        assert reviewer.name == "测试医生2"

    @pytest.mark.asyncio
    async def test_update_reviewer(self, db_session):
        """测试更新审核员"""
        service = HumanReviewService(db_session)

        # 创建审核员
        reviewer_data = ReviewerCreate(
            name="测试医生3",
            email="test3@example.com",
            specialties=["营养学"],
            max_concurrent_tasks=2,
        )
        created_reviewer = await service.create_reviewer(reviewer_data)

        # 更新审核员
        update_data = ReviewerUpdate(name="更新后的医生", max_concurrent_tasks=8)
        updated_reviewer = await service.update_reviewer(
            created_reviewer.reviewer_id, update_data
        )

        assert updated_reviewer.name == "更新后的医生"
        assert updated_reviewer.max_concurrent_tasks == 8
        assert updated_reviewer.email == "test3@example.com"  # 未更新的字段保持不变

    @pytest.mark.asyncio
    async def test_activate_deactivate_reviewer(self, db_session):
        """测试激活和停用审核员"""
        service = HumanReviewService(db_session)

        # 创建审核员
        reviewer_data = ReviewerCreate(
            name="测试医生4",
            email="test4@example.com",
            specialties=["健康管理"],
            max_concurrent_tasks=4,
        )
        created_reviewer = await service.create_reviewer(reviewer_data)

        # 停用审核员
        deactivated_reviewer = await service.deactivate_reviewer(
            created_reviewer.reviewer_id
        )
        assert deactivated_reviewer.status == ReviewerStatus.INACTIVE
        assert deactivated_reviewer.is_available is False

        # 激活审核员
        activated_reviewer = await service.activate_reviewer(
            created_reviewer.reviewer_id
        )
        assert activated_reviewer.status == ReviewerStatus.ACTIVE
        assert activated_reviewer.is_available is True

    @pytest.mark.asyncio
    async def test_create_review_task(self, db_session):
        """测试创建审核任务"""
        service = HumanReviewService(db_session)

        task_data = ReviewTaskCreate(
            content_type="diagnosis",
            content_id="diag_123",
            content_data={
                "symptoms": ["头痛", "发热"],
                "diagnosis": "感冒",
                "treatment": "多休息，多喝水",
            },
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.NORMAL,
            requester_id="user_123",
            metadata={"source": "xiaoai_agent"},
        )

        task = await service.create_review_task(task_data)

        assert task.content_type == "diagnosis"
        assert task.content_id == "diag_123"
        assert task.review_type == ReviewType.MEDICAL_DIAGNOSIS
        assert task.priority == ReviewPriority.NORMAL
        assert task.status == ReviewStatus.PENDING
        assert task.requester_id == "user_123"
        assert task.reviewer_id is None  # 未分配

    @pytest.mark.asyncio
    async def test_assign_review_task(self, db_session):
        """测试分配审核任务"""
        service = HumanReviewService(db_session)

        # 创建审核员
        reviewer_data = ReviewerCreate(
            name="分配测试医生",
            email="assign@example.com",
            specialties=["中医诊断"],
            max_concurrent_tasks=5,
        )
        reviewer = await service.create_reviewer(reviewer_data)

        # 创建审核任务
        task_data = ReviewTaskCreate(
            content_type="diagnosis",
            content_id="diag_assign_123",
            content_data={"test": "data"},
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.NORMAL,
            requester_id="user_assign_123",
        )
        task = await service.create_review_task(task_data)

        # 分配任务
        assigned_task = await service.assign_review_task(
            task.task_id, reviewer.reviewer_id
        )

        assert assigned_task.reviewer_id == reviewer.reviewer_id
        assert assigned_task.status == ReviewStatus.IN_PROGRESS
        assert assigned_task.assigned_at is not None

    @pytest.mark.asyncio
    async def test_complete_review_task(self, db_session):
        """测试完成审核任务"""
        service = HumanReviewService(db_session)

        # 创建审核员
        reviewer_data = ReviewerCreate(
            name="完成测试医生",
            email="complete@example.com",
            specialties=["中医诊断"],
            max_concurrent_tasks=5,
        )
        reviewer = await service.create_reviewer(reviewer_data)

        # 创建并分配审核任务
        task_data = ReviewTaskCreate(
            content_type="diagnosis",
            content_id="diag_complete_123",
            content_data={"test": "data"},
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.NORMAL,
            requester_id="user_complete_123",
        )
        task = await service.create_review_task(task_data)
        assigned_task = await service.assign_review_task(
            task.task_id, reviewer.reviewer_id
        )

        # 完成任务
        completion_data = {
            "approved": True,
            "feedback": "诊断准确，建议合理",
            "suggestions": ["可以增加一些预防措施"],
            "quality_score": 0.95,
        }

        completed_task = await service.complete_review_task(
            assigned_task.task_id, completion_data
        )

        assert completed_task.status == ReviewStatus.COMPLETED
        assert completed_task.completed_at is not None
        assert completed_task.result["approved"] is True
        assert completed_task.result["feedback"] == "诊断准确，建议合理"
        assert completed_task.quality_score == 0.95

    @pytest.mark.asyncio
    async def test_list_reviewers(self, db_session):
        """测试列出审核员"""
        service = HumanReviewService(db_session)

        # 创建多个审核员
        reviewers_data = [
            ReviewerCreate(
                name=f"列表测试医生{i}",
                email=f"list{i}@example.com",
                specialties=["中医诊断"] if i % 2 == 0 else ["西医诊断"],
                max_concurrent_tasks=3 + i,
            )
            for i in range(5)
        ]

        created_reviewers = []
        for reviewer_data in reviewers_data:
            reviewer = await service.create_reviewer(reviewer_data)
            created_reviewers.append(reviewer)

        # 测试无过滤条件
        all_reviewers = await service.list_reviewers()
        assert len(all_reviewers) >= 5

        # 测试按专业领域过滤
        tcm_reviewers = await service.list_reviewers(filters={"specialty": "中医诊断"})
        assert len(tcm_reviewers) >= 3  # 至少有3个中医诊断的审核员

        # 测试按状态过滤
        active_reviewers = await service.list_reviewers(
            filters={"status": ReviewerStatus.ACTIVE}
        )
        assert len(active_reviewers) >= 5

    @pytest.mark.asyncio
    async def test_list_review_tasks(self, db_session):
        """测试列出审核任务"""
        service = HumanReviewService(db_session)

        # 创建多个审核任务
        tasks_data = [
            ReviewTaskCreate(
                content_type="diagnosis",
                content_id=f"diag_list_{i}",
                content_data={"test": f"data_{i}"},
                review_type=ReviewType.MEDICAL_DIAGNOSIS,
                priority=ReviewPriority.NORMAL if i % 2 == 0 else ReviewPriority.HIGH,
                requester_id=f"user_list_{i}",
            )
            for i in range(5)
        ]

        created_tasks = []
        for task_data in tasks_data:
            task = await service.create_review_task(task_data)
            created_tasks.append(task)

        # 测试无过滤条件
        all_tasks = await service.list_review_tasks()
        assert len(all_tasks) >= 5

        # 测试按状态过滤
        pending_tasks = await service.list_review_tasks(
            filters={"status": ReviewStatus.PENDING}
        )
        assert len(pending_tasks) >= 5

        # 测试按优先级过滤
        high_priority_tasks = await service.list_review_tasks(
            filters={"priority": ReviewPriority.HIGH}
        )
        assert len(high_priority_tasks) >= 2

    @pytest.mark.asyncio
    async def test_get_reviewer_workload(self, db_session):
        """测试获取审核员工作负载"""
        service = HumanReviewService(db_session)

        # 创建审核员
        reviewer_data = ReviewerCreate(
            name="工作负载测试医生",
            email="workload@example.com",
            specialties=["中医诊断"],
            max_concurrent_tasks=5,
        )
        reviewer = await service.create_reviewer(reviewer_data)

        # 创建并分配任务
        task_data = ReviewTaskCreate(
            content_type="diagnosis",
            content_id="diag_workload_123",
            content_data={"test": "data"},
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.NORMAL,
            requester_id="user_workload_123",
        )
        task = await service.create_review_task(task_data)
        await service.assign_review_task(task.task_id, reviewer.reviewer_id)

        # 获取工作负载
        workload = await service.get_reviewer_workload(reviewer.reviewer_id)

        assert workload is not None
        assert workload["in_progress_tasks"] >= 1
        assert workload["total_tasks"] >= 1
