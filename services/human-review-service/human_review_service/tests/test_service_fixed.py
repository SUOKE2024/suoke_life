"""
修复后的服务测试
Fixed Service Tests

修复数据模型验证错误，提高测试覆盖率
"""

import pytest
from uuid import uuid4
from datetime import datetime, timezone

from human_review_service.core.service import HumanReviewService
from human_review_service.core.models import (
    ReviewerCreate,
    ReviewerDB,
    ReviewerStatus,
    ReviewPriority,
    ReviewStatus,
    ReviewTaskCreate,
    ReviewTaskDB,
    ReviewType,
)


class TestHumanReviewServiceFixed:
    """修复后的人工审核服务测试"""

    @pytest.mark.asyncio
    async def test_create_reviewer(self, db_session):
        """测试创建审核员"""
        service = HumanReviewService(db_session)

        reviewer_data = ReviewerCreate(
            reviewer_id=f"test_reviewer_{uuid4().hex[:8]}",
            name="测试医生",
            email="test@example.com",
            specialties=["中医诊断", "方剂学"],
            max_concurrent_tasks=5,
        )

        reviewer = await service.create_reviewer(reviewer_data)

        assert reviewer.reviewer_id == reviewer_data.reviewer_id
        assert reviewer.name == reviewer_data.name
        assert reviewer.email == reviewer_data.email
        assert reviewer.specialties == reviewer_data.specialties
        assert reviewer.max_concurrent_tasks == reviewer_data.max_concurrent_tasks
        assert reviewer.status == ReviewerStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_get_reviewer(self, db_session):
        """测试获取审核员"""
        service = HumanReviewService(db_session)

        # 创建审核员
        reviewer_data = ReviewerCreate(
            reviewer_id=f"test_reviewer_get_{uuid4().hex[:8]}",
            name="测试医生2",
            email="test2@example.com",
            specialties=["西医诊断"],
            max_concurrent_tasks=3,
        )

        created_reviewer = await service.create_reviewer(reviewer_data)

        # 获取审核员
        retrieved_reviewer = await service.get_reviewer(created_reviewer.reviewer_id)

        assert retrieved_reviewer is not None
        assert retrieved_reviewer.reviewer_id == created_reviewer.reviewer_id
        assert retrieved_reviewer.name == created_reviewer.name
        assert retrieved_reviewer.email == created_reviewer.email

    @pytest.mark.asyncio
    async def test_update_reviewer(self, db_session):
        """测试更新审核员"""
        service = HumanReviewService(db_session)

        # 创建审核员
        reviewer_data = ReviewerCreate(
            reviewer_id=f"test_reviewer_update_{uuid4().hex[:8]}",
            name="测试医生3",
            email="test3@example.com",
            specialties=["营养学"],
            max_concurrent_tasks=2,
        )

        created_reviewer = await service.create_reviewer(reviewer_data)

        # 更新审核员
        update_data = {
            "name": "更新后的医生",
            "max_concurrent_tasks": 8,
            "specialties": ["营养学", "健康管理"]
        }

        updated_reviewer = await service.update_reviewer(
            created_reviewer.reviewer_id, update_data
        )

        assert updated_reviewer.name == update_data["name"]
        assert updated_reviewer.max_concurrent_tasks == update_data["max_concurrent_tasks"]
        assert updated_reviewer.specialties == update_data["specialties"]

    @pytest.mark.asyncio
    async def test_activate_deactivate_reviewer(self, db_session):
        """测试激活和停用审核员"""
        service = HumanReviewService(db_session)

        # 创建审核员
        reviewer_data = ReviewerCreate(
            reviewer_id=f"test_reviewer_status_{uuid4().hex[:8]}",
            name="测试医生4",
            email="test4@example.com",
            specialties=["健康管理"],
            max_concurrent_tasks=4,
        )

        created_reviewer = await service.create_reviewer(reviewer_data)
        assert created_reviewer.status == ReviewerStatus.ACTIVE

        # 停用审核员
        deactivated_reviewer = await service.deactivate_reviewer(created_reviewer.reviewer_id)
        assert deactivated_reviewer.status == ReviewerStatus.INACTIVE

        # 激活审核员
        activated_reviewer = await service.activate_reviewer(created_reviewer.reviewer_id)
        assert activated_reviewer.status == ReviewerStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_create_review_task(self, db_session):
        """测试创建审核任务"""
        service = HumanReviewService(db_session)

        task_data = ReviewTaskCreate(
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.NORMAL,
            content={
                "symptoms": ["头痛", "发热"],
                "diagnosis": "感冒",
                "treatment": "多休息，多喝水",
            },
            user_id="user_123",
            agent_id="xiaoai_agent",
            estimated_duration=1800,
        )

        task = await service.submit_review(task_data)

        assert task.review_type == task_data.review_type
        assert task.priority == task_data.priority
        assert task.content == task_data.content
        assert task.user_id == task_data.user_id
        assert task.agent_id == task_data.agent_id
        assert task.status == ReviewStatus.PENDING

    @pytest.mark.asyncio
    async def test_assign_review_task(self, db_session):
        """测试分配审核任务"""
        service = HumanReviewService(db_session)

        # 创建审核员
        reviewer_data = ReviewerCreate(
            reviewer_id=f"test_reviewer_assign_{uuid4().hex[:8]}",
            name="分配测试医生",
            email="assign@example.com",
            specialties=["中医诊断"],
            max_concurrent_tasks=5,
        )

        reviewer = await service.create_reviewer(reviewer_data)

        # 创建审核任务
        task_data = ReviewTaskCreate(
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.NORMAL,
            content={"test": "data"},
            user_id="user_assign_123",
            agent_id="xiaoai_agent",
        )

        task = await service.submit_review(task_data)

        # 分配任务
        assigned_task = await service.assign_task(task.task_id, reviewer.reviewer_id)

        assert assigned_task.assigned_to == reviewer.reviewer_id
        assert assigned_task.status == ReviewStatus.ASSIGNED

    @pytest.mark.asyncio
    async def test_complete_review_task(self, db_session):
        """测试完成审核任务"""
        service = HumanReviewService(db_session)

        # 创建审核员
        reviewer_data = ReviewerCreate(
            reviewer_id=f"test_reviewer_complete_{uuid4().hex[:8]}",
            name="完成测试医生",
            email="complete@example.com",
            specialties=["中医诊断"],
            max_concurrent_tasks=5,
        )

        reviewer = await service.create_reviewer(reviewer_data)

        # 创建并分配任务
        task_data = ReviewTaskCreate(
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.NORMAL,
            content={"test": "data"},
            user_id="user_complete_123",
            agent_id="xiaoai_agent",
        )

        task = await service.submit_review(task_data)
        assigned_task = await service.assign_task(task.task_id, reviewer.reviewer_id)

        # 完成任务
        decision_data = {
            "decision": "approved",
            "comments": "审核通过",
            "reviewer_notes": "内容符合要求",
        }

        completed_task = await service.complete_review(
            assigned_task.task_id, 
            decision_data["decision"],
            decision_data["comments"],
            decision_data["reviewer_notes"]
        )

        assert completed_task.status == ReviewStatus.APPROVED
        assert completed_task.review_comments == decision_data["comments"]

    @pytest.mark.asyncio
    async def test_list_reviewers(self, db_session):
        """测试列出审核员"""
        service = HumanReviewService(db_session)

        # 创建多个审核员
        reviewers_data = [
            ReviewerCreate(
                reviewer_id=f"test_reviewer_list_{i}_{uuid4().hex[:8]}",
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

        # 列出审核员
        reviewers_list = await service.list_reviewers(page=1, size=10)

        assert len(reviewers_list.items) >= 5
        assert reviewers_list.total >= 5
        assert reviewers_list.page == 1
        assert reviewers_list.size == 10

    @pytest.mark.asyncio
    async def test_list_review_tasks(self, db_session):
        """测试列出审核任务"""
        service = HumanReviewService(db_session)

        # 创建多个审核任务
        tasks_data = [
            ReviewTaskCreate(
                review_type=ReviewType.MEDICAL_DIAGNOSIS,
                priority=ReviewPriority.NORMAL if i % 2 == 0 else ReviewPriority.HIGH,
                content={"test": f"data_{i}"},
                user_id=f"user_list_{i}",
                agent_id="xiaoai_agent",
            )
            for i in range(5)
        ]

        created_tasks = []
        for task_data in tasks_data:
            task = await service.submit_review(task_data)
            created_tasks.append(task)

        # 列出审核任务
        tasks_list = await service.list_review_tasks(page=1, size=10)

        assert len(tasks_list.items) >= 5
        assert tasks_list.total >= 5
        assert tasks_list.page == 1
        assert tasks_list.size == 10

    @pytest.mark.asyncio
    async def test_get_reviewer_workload(self, db_session):
        """测试获取审核员工作负载"""
        service = HumanReviewService(db_session)

        # 创建审核员
        reviewer_data = ReviewerCreate(
            reviewer_id=f"test_reviewer_workload_{uuid4().hex[:8]}",
            name="工作负载测试医生",
            email="workload@example.com",
            specialties=["中医诊断"],
            max_concurrent_tasks=5,
        )

        reviewer = await service.create_reviewer(reviewer_data)

        # 创建并分配任务
        task_data = ReviewTaskCreate(
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.NORMAL,
            content={"test": "workload"},
            user_id="user_workload_123",
            agent_id="xiaoai_agent",
        )

        task = await service.submit_review(task_data)
        await service.assign_task(task.task_id, reviewer.reviewer_id)

        # 获取工作负载
        workload = await service.get_reviewer_workload(reviewer.reviewer_id)

        assert workload["reviewer_id"] == reviewer.reviewer_id
        assert workload["current_tasks"] >= 1
        assert workload["max_concurrent_tasks"] == 5
        assert workload["utilization_rate"] > 0

    @pytest.mark.asyncio
    async def test_get_dashboard_statistics(self, db_session):
        """测试获取仪表板统计数据"""
        service = HumanReviewService(db_session)

        # 创建一些测试数据
        reviewer_data = ReviewerCreate(
            reviewer_id=f"test_reviewer_stats_{uuid4().hex[:8]}",
            name="统计测试医生",
            email="stats@example.com",
            specialties=["中医诊断"],
            max_concurrent_tasks=5,
        )

        reviewer = await service.create_reviewer(reviewer_data)

        task_data = ReviewTaskCreate(
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.NORMAL,
            content={"test": "stats"},
            user_id="user_stats_123",
            agent_id="xiaoai_agent",
        )

        task = await service.submit_review(task_data)

        # 获取统计数据
        stats = await service.get_dashboard_statistics()

        assert "total_tasks" in stats
        assert "pending_tasks" in stats
        assert "completed_tasks" in stats
        assert "reviewer_count" in stats
        assert stats["total_tasks"] >= 1
        assert stats["reviewer_count"] >= 1

    @pytest.mark.asyncio
    async def test_get_reviewer_not_found(self, db_session):
        """测试获取不存在的审核员"""
        service = HumanReviewService(db_session)

        non_existent_id = f"non_existent_{uuid4().hex[:8]}"
        reviewer = await service.get_reviewer(non_existent_id)

        assert reviewer is None

    @pytest.mark.asyncio
    async def test_get_review_task_not_found(self, db_session):
        """测试获取不存在的审核任务"""
        service = HumanReviewService(db_session)

        non_existent_id = f"non_existent_{uuid4().hex[:8]}"
        task = await service.get_review_task(non_existent_id)

        assert task is None

    @pytest.mark.asyncio
    async def test_assign_task_to_inactive_reviewer(self, db_session):
        """测试分配任务给非活跃审核员"""
        service = HumanReviewService(db_session)

        # 创建审核员并停用
        reviewer_data = ReviewerCreate(
            reviewer_id=f"test_reviewer_inactive_{uuid4().hex[:8]}",
            name="非活跃测试医生",
            email="inactive@example.com",
            specialties=["中医诊断"],
            max_concurrent_tasks=5,
        )

        reviewer = await service.create_reviewer(reviewer_data)
        await service.deactivate_reviewer(reviewer.reviewer_id)

        # 创建任务
        task_data = ReviewTaskCreate(
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.NORMAL,
            content={"test": "inactive"},
            user_id="user_inactive_123",
            agent_id="xiaoai_agent",
        )

        task = await service.submit_review(task_data)

        # 尝试分配任务给非活跃审核员
        with pytest.raises(Exception):
            await service.assign_task(task.task_id, reviewer.reviewer_id)

    @pytest.mark.asyncio
    async def test_risk_assessment(self, db_session):
        """测试风险评估"""
        service = HumanReviewService(db_session)

        # 创建高风险任务
        high_risk_task_data = ReviewTaskCreate(
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.URGENT,
            content={
                "symptoms": ["胸痛", "呼吸困难", "心悸"],
                "diagnosis": "心肌梗死",
                "treatment": "立即就医",
            },
            user_id="user_risk_123",
            agent_id="xiaoai_agent",
        )

        task = await service.submit_review(high_risk_task_data)

        # 验证风险评分
        assert task.risk_score is not None
        assert task.risk_score > 0

    @pytest.mark.asyncio
    async def test_auto_assignment(self, db_session):
        """测试自动分配"""
        service = HumanReviewService(db_session)

        # 创建多个审核员
        reviewers = []
        for i in range(3):
            reviewer_data = ReviewerCreate(
                reviewer_id=f"test_reviewer_auto_{i}_{uuid4().hex[:8]}",
                name=f"自动分配测试医生{i}",
                email=f"auto{i}@example.com",
                specialties=["中医诊断"],
                max_concurrent_tasks=5,
            )
            reviewer = await service.create_reviewer(reviewer_data)
            reviewers.append(reviewer)

        # 创建任务并自动分配
        task_data = ReviewTaskCreate(
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.NORMAL,
            content={"test": "auto_assignment"},
            user_id="user_auto_123",
            agent_id="xiaoai_agent",
        )

        task = await service.submit_review(task_data)
        assigned_task = await service.auto_assign_task(task.task_id)

        assert assigned_task.assigned_to is not None
        assert assigned_task.status == ReviewStatus.ASSIGNED 