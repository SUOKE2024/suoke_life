"""
test_services - 索克生活项目模块
"""

        from human_review_service.core.models import ReviewTaskUpdate
from datetime import datetime, timezone
from human_review_service.core.models import (
from human_review_service.core.service import HumanReviewService
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4
import pytest

"""
服务层测试
Service Layer Tests

测试业务逻辑服务层的功能
"""


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
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            content={"complaint": "患者主诉：头痛、发热"},
            priority=ReviewPriority.HIGH,
            user_id="user_123",
            agent_id="agent_123",
            estimated_duration=1800
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
        mock_task_db.task_id = "test_task_001"
        mock_task_db.content = sample_task_create.content
        mock_task_db.review_type = sample_task_create.review_type
        mock_task_db.priority = sample_task_create.priority
        mock_task_db.user_id = sample_task_create.user_id
        mock_task_db.agent_id = sample_task_create.agent_id
        mock_task_db.status = ReviewStatus.PENDING
        mock_task_db.reviewer_id = None
        mock_task_db.assigned_at = None
        mock_task_db.started_at = None
        mock_task_db.completed_at = None
        mock_task_db.review_result = None
        mock_task_db.feedback = None
        mock_task_db.quality_score = None
        mock_task_db.estimated_duration = sample_task_create.estimated_duration
        mock_task_db.actual_duration = None
        mock_task_db.expires_at = datetime.now(timezone.utc)
        mock_task_db.assigned_to = None
        mock_task_db.reviewer_notes = None
        mock_task_db.review_comments = None
        mock_task_db.complexity_score = 0.5
        mock_task_db.risk_score = 0.3
        mock_task_db.metadata = {}
        mock_task_db.id = uuid4()
        mock_task_db.created_at = datetime.now(timezone.utc)
        mock_task_db.updated_at = datetime.now(timezone.utc)

        mock_session.add = Mock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        # Mock execute方法用于assignment engine查询
        mock_execute_result = Mock()
        mock_execute_result.scalars.return_value = []  # 返回空的审核员列表
        mock_session.execute = AsyncMock(return_value=mock_execute_result)

        # 模拟refresh操作
        async def mock_refresh(obj):
            for attr, value in vars(mock_task_db).items():
                setattr(obj, attr, value)

        mock_session.refresh.side_effect = mock_refresh

        result = await review_service.create_task(mock_session, sample_task_create)

        assert result.task_id == "test_task_001"
        assert result.content == sample_task_create.content
        assert result.priority == sample_task_create.priority
        assert mock_session.add.call_count == 2  # 添加任务和历史记录
        assert mock_session.commit.call_count == 2  # 提交任务和历史记录
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
        mock_reviewer.specialties = ["中医诊断", "方剂学"]
        mock_reviewer.certifications = []
        mock_reviewer.experience_years = 10
        mock_reviewer.max_concurrent_tasks = 5
        mock_reviewer.working_hours = {}
        mock_reviewer.timezone = "Asia/Shanghai"
        mock_reviewer.status = ReviewerStatus.ACTIVE
        mock_reviewer.current_task_count = 0
        mock_reviewer.is_available = True
        mock_reviewer.total_reviews = 0
        mock_reviewer.approved_reviews = 0
        mock_reviewer.rejected_reviews = 0
        mock_reviewer.average_review_time = 0.0
        mock_reviewer.quality_score = 0.0
        mock_reviewer.id = uuid4()
        mock_reviewer.created_at = datetime.now(timezone.utc)
        mock_reviewer.updated_at = datetime.now(timezone.utc)
        mock_reviewer.last_active_at = datetime.now(timezone.utc)
        mock_result.scalar_one_or_none.return_value = mock_reviewer
        
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await review_service.get_reviewer(reviewer_id, mock_session)

        assert result.reviewer_id == reviewer_id
        assert result.name == "张医生"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_task_by_id(self, review_service, mock_session):
        """测试根据ID获取任务"""
        task_id = "test_task_001"
        
        # Mock查询结果
        mock_result = Mock()
        mock_task = Mock()
        mock_task.task_id = task_id
        mock_task.content = {"complaint": "患者主诉：头痛、发热"}
        mock_task.review_type = ReviewType.MEDICAL_DIAGNOSIS
        mock_task.priority = ReviewPriority.HIGH
        mock_task.user_id = "user_123"
        mock_task.agent_id = "agent_123"
        mock_task.status = ReviewStatus.PENDING
        mock_task.reviewer_id = None
        mock_task.assigned_at = None
        mock_task.started_at = None
        mock_task.completed_at = None
        mock_task.review_result = None
        mock_task.feedback = None
        mock_task.quality_score = None
        mock_task.estimated_duration = 1800
        mock_task.actual_duration = None
        mock_task.expires_at = datetime.now(timezone.utc)
        mock_task.assigned_to = None
        mock_task.reviewer_notes = None
        mock_task.review_comments = None
        mock_task.complexity_score = 0.5
        mock_task.risk_score = 0.3
        mock_task.metadata = {}
        mock_task.id = uuid4()
        mock_task.created_at = datetime.now(timezone.utc)
        mock_task.updated_at = datetime.now(timezone.utc)
        mock_result.scalar_one_or_none.return_value = mock_task
        
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await review_service.get_task(mock_session, task_id)

        assert result.task_id == task_id
        assert result.status == ReviewStatus.PENDING
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_assign_task(self, review_service, mock_session):
        """测试分配任务"""
        task_id = "test_task_001"
        reviewer_id = "test_reviewer_001"
        
        # Mock任务查询结果
        mock_task_result = Mock()
        mock_task = Mock()
        mock_task.task_id = task_id
        mock_task.content = {"complaint": "患者主诉：头痛、发热"}
        mock_task.review_type = ReviewType.MEDICAL_DIAGNOSIS
        mock_task.priority = ReviewPriority.HIGH
        mock_task.user_id = "user_123"
        mock_task.agent_id = "agent_123"
        mock_task.status = ReviewStatus.PENDING
        mock_task.reviewer_id = None
        mock_task.assigned_at = None
        mock_task.started_at = None
        mock_task.completed_at = None
        mock_task.review_result = None
        mock_task.feedback = None
        mock_task.quality_score = None
        mock_task.estimated_duration = 1800
        mock_task.actual_duration = None
        mock_task.expires_at = datetime.now(timezone.utc)
        mock_task.assigned_to = None
        mock_task.reviewer_notes = None
        mock_task.review_comments = None
        mock_task.complexity_score = 0.5
        mock_task.risk_score = 0.3
        mock_task.metadata = {}
        mock_task.id = uuid4()
        mock_task.created_at = datetime.now(timezone.utc)
        mock_task.updated_at = datetime.now(timezone.utc)
        mock_task_result.scalar_one_or_none.return_value = mock_task
        
        # Mock审核员查询结果
        mock_reviewer_result = Mock()
        mock_reviewer = Mock()
        mock_reviewer.reviewer_id = reviewer_id
        mock_reviewer.name = "张医生"
        mock_reviewer.email = "zhang@example.com"
        mock_reviewer.specialties = ["中医诊断", "方剂学"]
        mock_reviewer.certifications = []
        mock_reviewer.experience_years = 10
        mock_reviewer.max_concurrent_tasks = 5
        mock_reviewer.working_hours = {}
        mock_reviewer.timezone = "Asia/Shanghai"
        mock_reviewer.status = ReviewerStatus.ACTIVE
        mock_reviewer.current_task_count = 0
        mock_reviewer.is_available = True
        mock_reviewer.total_reviews = 0
        mock_reviewer.approved_reviews = 0
        mock_reviewer.rejected_reviews = 0
        mock_reviewer.average_review_time = 0.0
        mock_reviewer.quality_score = 0.0
        mock_reviewer.id = uuid4()
        mock_reviewer.created_at = datetime.now(timezone.utc)
        mock_reviewer.updated_at = datetime.now(timezone.utc)
        mock_reviewer.last_active_at = datetime.now(timezone.utc)
        mock_reviewer_result.scalar_one_or_none.return_value = mock_reviewer
        
        # 设置execute的返回值序列 - 需要更多的mock结果用于历史记录查询
        mock_history_result = Mock()
        mock_history_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(side_effect=[mock_task_result, mock_reviewer_result, mock_history_result])
        mock_session.commit = AsyncMock()
        mock_session.add = Mock()

        result = await review_service.assign_reviewer(task_id, reviewer_id, mock_session)

        assert result.assigned_to == reviewer_id
        assert result.status == ReviewStatus.ASSIGNED
        assert mock_session.execute.call_count == 3  # 任务查询、审核员查询、历史记录查询
        assert mock_session.commit.call_count == 2  # 更新任务和添加历史记录

    @pytest.mark.asyncio
    async def test_complete_task(self, review_service, mock_session):
        """测试完成任务"""
        task_id = "test_task_001"
        reviewer_id = "test_reviewer_001"
        
        # 创建ReviewTaskUpdate对象
        update_data = ReviewTaskUpdate(
            status=ReviewStatus.APPROVED,
            review_comments="诊断合理",
            reviewer_notes="患者症状明确",
            review_result={"approved": True, "confidence": 0.95}
        )
        
        # Mock查询结果
        mock_result = Mock()
        mock_task = Mock()
        mock_task.task_id = task_id
        mock_task.content = {"complaint": "患者主诉：头痛、发热"}
        mock_task.review_type = ReviewType.MEDICAL_DIAGNOSIS
        mock_task.priority = ReviewPriority.HIGH
        mock_task.user_id = "user_123"
        mock_task.agent_id = "agent_123"
        mock_task.status = ReviewStatus.IN_PROGRESS
        mock_task.reviewer_id = reviewer_id
        mock_task.assigned_at = datetime.now(timezone.utc)
        mock_task.started_at = datetime.now(timezone.utc)
        mock_task.completed_at = None
        mock_task.review_result = None
        mock_task.feedback = None
        mock_task.quality_score = None
        mock_task.estimated_duration = 1800
        mock_task.actual_duration = 0  # 设置为整数而不是Mock
        mock_task.expires_at = datetime.now(timezone.utc)
        mock_task.assigned_to = reviewer_id
        mock_task.reviewer_notes = None
        mock_task.review_comments = None
        mock_task.complexity_score = 0.5
        mock_task.risk_score = 0.3
        mock_task.metadata = {}
        mock_task.id = uuid4()
        mock_task.created_at = datetime.now(timezone.utc)
        mock_task.updated_at = datetime.now(timezone.utc)
        mock_result.scalar_one_or_none.return_value = mock_task
        
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        result = await review_service.update_task(mock_session, task_id, update_data)

        assert result.review_comments == update_data.review_comments
        assert result.status == update_data.status
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_pending_tasks(self, review_service, mock_session):
        """测试获取待处理任务"""
        # Mock查询结果
        def create_mock_task(task_id):
            mock_task = Mock()
            mock_task.task_id = task_id
            mock_task.content = {"complaint": f"任务{task_id}"}
            mock_task.review_type = ReviewType.MEDICAL_DIAGNOSIS
            mock_task.priority = ReviewPriority.HIGH
            mock_task.user_id = "user_123"
            mock_task.agent_id = "agent_123"
            mock_task.status = ReviewStatus.PENDING
            mock_task.reviewer_id = None
            mock_task.assigned_at = None
            mock_task.started_at = None
            mock_task.completed_at = None
            mock_task.review_result = None
            mock_task.feedback = None
            mock_task.quality_score = None
            mock_task.estimated_duration = 1800
            mock_task.actual_duration = None
            mock_task.expires_at = datetime.now(timezone.utc)
            mock_task.assigned_to = None
            mock_task.reviewer_notes = None
            mock_task.review_comments = None
            mock_task.complexity_score = 0.5
            mock_task.risk_score = 0.3
            mock_task.metadata = {}
            mock_task.id = uuid4()
            mock_task.created_at = datetime.now(timezone.utc)
            mock_task.updated_at = datetime.now(timezone.utc)
            return mock_task
        
        mock_result = Mock()
        mock_tasks = [
            create_mock_task("task_001"),
            create_mock_task("task_002")
        ]
        mock_result.scalars.return_value.all.return_value = mock_tasks
        
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await review_service.list_tasks(session=mock_session, filters={"status": ReviewStatus.PENDING})

        assert len(result) == 2
        assert all(task.status == ReviewStatus.PENDING for task in result)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_reviewer_workload(self, review_service, mock_session):
        """测试获取审核员工作负载"""
        reviewer_id = "test_reviewer_001"
        
        # Mock审核员查询结果
        mock_reviewer_result = Mock()
        mock_reviewer = Mock()
        mock_reviewer.reviewer_id = reviewer_id
        mock_reviewer.name = "张医生"
        mock_reviewer.email = "zhang@example.com"
        mock_reviewer.specialties = ["中医诊断", "方剂学"]
        mock_reviewer.certifications = []
        mock_reviewer.experience_years = 10
        mock_reviewer.max_concurrent_tasks = 5
        mock_reviewer.working_hours = {}
        mock_reviewer.timezone = "Asia/Shanghai"
        mock_reviewer.status = ReviewerStatus.ACTIVE
        mock_reviewer.current_task_count = 3  # 设置为整数而不是Mock
        mock_reviewer.is_available = True
        mock_reviewer.total_reviews = 100
        mock_reviewer.approved_reviews = 80
        mock_reviewer.rejected_reviews = 20
        mock_reviewer.average_review_time = 1800.0
        mock_reviewer.quality_score = 4.5
        mock_reviewer.id = uuid4()
        mock_reviewer.created_at = datetime.now(timezone.utc)
        mock_reviewer.updated_at = datetime.now(timezone.utc)
        mock_reviewer.last_active_at = datetime.now(timezone.utc)
        mock_reviewer_result.scalar_one_or_none.return_value = mock_reviewer
        
        mock_session.execute = AsyncMock(return_value=mock_reviewer_result)

        result = await review_service.get_reviewer(reviewer_id, mock_session)

        assert result.current_task_count == 3
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_dashboard_stats(self, review_service, mock_session):
        """测试获取仪表板统计"""
        # Mock统计查询结果
        mock_stats_result = Mock()
        mock_stats_row = Mock()
        mock_stats_row.total = 100
        mock_stats_row.pending = 50
        mock_stats_row.in_progress = 30
        mock_stats_row.completed = 20
        mock_stats_row.approved = 15
        mock_stats_row.rejected = 5
        mock_stats_row.avg_review_time = 1800.0
        mock_stats_result.first.return_value = mock_stats_row
        
        # Mock审核员统计查询结果
        mock_reviewer_result = Mock()
        mock_reviewer_row = Mock()
        mock_reviewer_row.total_reviewers = 15
        mock_reviewer_row.active_reviewers = 10
        mock_reviewer_result.first.return_value = mock_reviewer_row
        
        # Mock其他查询结果（待处理任务、活跃审核员、最近完成等）
        mock_pending_result = Mock()
        mock_pending_result.scalars.return_value.all.return_value = []
        
        mock_active_reviewers_result = Mock()
        mock_active_reviewers_result.scalars.return_value.all.return_value = []
        
        mock_recent_result = Mock()
        mock_recent_result.scalars.return_value.all.return_value = []
        
        mock_load_result = Mock()
        mock_load_result.scalar.return_value = 0.5
        
        mock_wait_result = Mock()
        mock_wait_result.scalar.return_value = 300

        # 为_estimate_wait_time添加额外的mock结果
        mock_wait_reviewer_result = Mock()
        mock_wait_reviewer_result.scalar.return_value = 5  # 活跃审核员数量
        
        mock_session.execute = AsyncMock(side_effect=[
            mock_stats_result,      # _get_review_statistics第一个查询
            mock_reviewer_result,   # _get_review_statistics第二个查询
            mock_pending_result,    # get_pending_tasks
            mock_active_reviewers_result,  # get_active_reviewers
            mock_recent_result,     # _get_recent_completions
            mock_load_result,       # _calculate_current_load
            mock_wait_reviewer_result,  # _estimate_wait_time第一个查询
            mock_wait_result        # _estimate_wait_time第二个查询
        ])

        result = await review_service.get_dashboard_data(mock_session)

        assert result is not None
        assert hasattr(result, 'statistics')
        assert hasattr(result, 'pending_tasks')
        assert hasattr(result, 'active_reviewers')
        assert hasattr(result, 'recent_completions')
        assert hasattr(result, 'current_load')
        assert hasattr(result, 'estimated_wait_time')
        # 验证execute被调用了多次（用于各种统计查询）
        assert mock_session.execute.call_count >= 6 