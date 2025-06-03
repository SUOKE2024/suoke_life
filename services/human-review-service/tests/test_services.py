"""
服务层测试
Service Layer Tests

测试业务逻辑服务层的功能
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

from human_review_service.core.service import HumanReviewService
from human_review_service.core.models import (
    ReviewerCreate,
    ReviewerDB,
    ReviewerUpdate,
    ReviewTaskCreate,
    ReviewTaskDB,
    ReviewStatus,
    ReviewType,
    ReviewPriority,
    ReviewerStatus
)


class TestHumanReviewService:
    """人工审核服务测试"""

    @pytest.fixture
    def mock_session(self):
        """模拟数据库会话"""
        return AsyncMock()

    @pytest.fixture
    def review_service(self, mock_session):
        """创建审核服务实例"""
        return HumanReviewService(session=mock_session)

    @pytest.fixture
    def sample_reviewer_create(self):
        """示例创建审核员数据"""
        return ReviewerCreate(
            reviewer_id="test_reviewer_001",
            name="张医生",
            email="zhang@example.com",
            specialties=["中医诊断", "方剂学"],
            max_concurrent_tasks=5,
            experience_years=10,
            certification_level="senior"
        )

    @pytest.fixture
    def sample_task_create(self):
        """示例创建任务数据"""
        return ReviewTaskCreate(
            task_id="test_task_001",
            content="患者主诉：头痛、发热",
            content_type="diagnosis",
            priority=ReviewPriority.HIGH,
            metadata={"patient_id": "P001", "department": "内科"}
        )

    @pytest.mark.asyncio
    async def test_create_reviewer(self, review_service, mock_session, sample_reviewer_create):
        """测试创建审核员"""
        # Mock数据库操作
        mock_reviewer_db = Mock()
        mock_reviewer_db.reviewer_id = sample_reviewer_create.reviewer_id
        mock_reviewer_db.name = sample_reviewer_create.name
        mock_reviewer_db.email = sample_reviewer_create.email
        mock_reviewer_db.specialties = sample_reviewer_create.specialties
        mock_reviewer_db.max_concurrent_tasks = sample_reviewer_create.max_concurrent_tasks
        mock_reviewer_db.experience_years = sample_reviewer_create.experience_years
        mock_reviewer_db.status = ReviewerStatus.ACTIVE
        mock_reviewer_db.id = uuid4()
        mock_reviewer_db.created_at = datetime.now(timezone.utc)
        mock_reviewer_db.updated_at = datetime.now(timezone.utc)
        mock_reviewer_db.current_task_count = 0
        mock_reviewer_db.is_available = True
        mock_reviewer_db.total_reviews = 0
        mock_reviewer_db.approved_reviews = 0
        mock_reviewer_db.rejected_reviews = 0
        mock_reviewer_db.average_review_time = 1800.0
        mock_reviewer_db.quality_score = 5.0
        mock_reviewer_db.last_active_at = None
        mock_reviewer_db.certifications = []
        mock_reviewer_db.working_hours = {}
        mock_reviewer_db.timezone = "Asia/Shanghai"
        mock_reviewer_db.certification_level = "senior"

        mock_session.add = Mock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        # 模拟refresh操作，设置返回的对象
        async def mock_refresh(obj):
            for attr, value in vars(mock_reviewer_db).items():
                setattr(obj, attr, value)

        mock_session.refresh.side_effect = mock_refresh

        result = await review_service.create_reviewer(sample_reviewer_create, mock_session)

        assert result.reviewer_id == sample_reviewer_create.reviewer_id
        assert result.name == sample_reviewer_create.name
        assert result.email == sample_reviewer_create.email
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_task(self, review_service, mock_session, sample_task_create):
        """测试创建任务"""
        # Mock数据库操作
        mock_task_db = Mock()
        mock_task_db.task_id = sample_task_create.task_id
        mock_task_db.content = sample_task_create.content
        mock_task_db.content_type = sample_task_create.content_type
        mock_task_db.priority = sample_task_create.priority
        mock_task_db.metadata = sample_task_create.metadata
        mock_task_db.status = ReviewStatus.PENDING
        mock_task_db.id = uuid4()
        mock_task_db.created_at = datetime.now(timezone.utc)
        mock_task_db.updated_at = datetime.now(timezone.utc)
        mock_task_db.assigned_reviewer_id = None
        mock_task_db.assigned_at = None
        mock_task_db.completed_at = None
        mock_task_db.review_result = None
        mock_task_db.review_notes = None
        mock_task_db.confidence_score = None

        mock_session.add = Mock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        # 模拟refresh操作
        async def mock_refresh(obj):
            for attr, value in vars(mock_task_db).items():
                setattr(obj, attr, value)

        mock_session.refresh.side_effect = mock_refresh

        result = await review_service.submit_review(sample_task_create, mock_session)

        assert result.task_id == sample_task_create.task_id
        assert result.content == sample_task_create.content
        assert result.priority == sample_task_create.priority
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_reviewer_by_id(self, review_service, mock_session):
        """测试根据ID获取审核员"""
        reviewer_id = "test_reviewer_001"
        
        # Mock查询结果
        mock_result = Mock()
        mock_reviewer = Mock()
        mock_reviewer.reviewer_id = reviewer_id
        mock_reviewer.name = "张医生"
        mock_reviewer.email = "zhang@example.com"
        mock_result.scalar_one_or_none.return_value = mock_reviewer
        
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await review_service.get_reviewer(reviewer_id, mock_session)

        assert result == mock_reviewer
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_task_by_id(self, review_service, mock_session):
        """测试根据ID获取任务"""
        task_id = "test_task_001"
        
        # Mock查询结果
        mock_result = Mock()
        mock_task = Mock()
        mock_task.task_id = task_id
        mock_task.content = "患者主诉：头痛、发热"
        mock_task.status = ReviewStatus.PENDING
        mock_result.scalar_one_or_none.return_value = mock_task
        
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await review_service.get_review_task(task_id, mock_session)

        assert result == mock_task
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_assign_task(self, review_service, mock_session):
        """测试分配任务"""
        task_id = "test_task_001"
        reviewer_id = "test_reviewer_001"
        
        # Mock查询结果
        mock_result = Mock()
        mock_task = Mock()
        mock_task.task_id = task_id
        mock_task.status = ReviewStatus.PENDING
        mock_task.assigned_reviewer_id = None
        mock_result.scalar_one_or_none.return_value = mock_task
        
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        result = await review_service.assign_reviewer(task_id, reviewer_id, mock_session)

        assert result.assigned_to == reviewer_id
        assert result.status == ReviewStatus.ASSIGNED
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_complete_task(self, review_service, mock_session):
        """测试完成任务"""
        task_id = "test_task_001"
        reviewer_id = "test_reviewer_001"
        
        # 创建ReviewDecision对象
        from human_review_service.core.models import ReviewDecision
        decision = ReviewDecision(
            decision=ReviewStatus.APPROVED,
            comments="诊断合理",
            reviewer_notes="患者症状明确",
            review_result={"approved": True, "confidence": 0.95}
        )
        
        # Mock查询结果
        mock_result = Mock()
        mock_task = Mock()
        mock_task.task_id = task_id
        mock_task.status = ReviewStatus.IN_PROGRESS
        mock_task.assigned_to = reviewer_id
        mock_task.started_at = datetime.now(timezone.utc)
        mock_result.scalar_one_or_none.return_value = mock_task
        
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        result = await review_service.complete_review(task_id, reviewer_id, decision, mock_session)

        assert result.review_comments == decision.comments
        assert result.status == decision.decision
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_pending_tasks(self, review_service, mock_session):
        """测试获取待处理任务"""
        # Mock查询结果
        mock_result = Mock()
        mock_tasks = [
            Mock(task_id="task_001", status=ReviewStatus.PENDING),
            Mock(task_id="task_002", status=ReviewStatus.PENDING)
        ]
        mock_result.scalars.return_value.all.return_value = mock_tasks
        
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await review_service.get_pending_tasks(mock_session)

        assert len(result) == 2
        assert all(task.status == ReviewStatus.PENDING for task in result)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_reviewer_workload(self, review_service, mock_session):
        """测试获取审核员工作负载"""
        reviewer_id = "test_reviewer_001"
        
        # Mock查询结果
        mock_result = Mock()
        mock_result.scalar.return_value = 3  # 当前任务数
        
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await review_service.get_reviewer_workload(reviewer_id, mock_session)

        assert result["current_tasks"] == 3
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_dashboard_stats(self, review_service, mock_session):
        """测试获取仪表板统计"""
        # Mock查询结果
        mock_result = Mock()
        mock_result.scalar.return_value = 100
        
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await review_service.get_dashboard_data(mock_session)

        assert result is not None
        mock_session.execute.assert_called() 