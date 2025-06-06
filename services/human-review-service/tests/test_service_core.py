"""
test_service_core - 索克生活项目模块
"""

        import time
from datetime import datetime, timezone, timedelta
from human_review_service.core.models import (
from human_review_service.core.service import HumanReviewService
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from uuid import uuid4
import asyncio
import pytest

"""
服务层核心功能测试
Service Core Tests

专注于测试实际存在的HumanReviewService功能
"""


    ReviewerCreate,
    ReviewerUpdate,
    ReviewerDB,
    ReviewTaskCreate,
    ReviewTaskUpdate,
    ReviewTaskDB,
    ReviewStatus,
    ReviewType,
    ReviewPriority,
    ReviewerStatus
)


class TestHumanReviewServiceCore:
    """人工审核服务核心功能测试"""

    @pytest.fixture
    def mock_session(self):
        """模拟数据库会话"""
        session = AsyncMock()
        session.add = Mock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        session.execute = AsyncMock()
        session.scalar = AsyncMock()
        return session

    @pytest.fixture
    def review_service(self):
        """创建审核服务实例"""
        return HumanReviewService()

    @pytest.fixture
    def sample_reviewer_create(self):
        """示例创建审核员数据"""
        return ReviewerCreate(
            reviewer_id="test_reviewer_001",
            name="张医生",
            email="zhang@example.com",
            specialties=["中医诊断", "方剂学"],
            max_concurrent_tasks=5,
            experience_years=10
        )

    @pytest.fixture
    def sample_task_create(self):
        """示例创建任务数据"""
        return ReviewTaskCreate(
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            content={"complaint": "患者主诉：头痛、发热"},
            priority=ReviewPriority.HIGH,
            user_id="user_123",
            agent_id="agent_123"
        )

    @pytest.mark.asyncio
    async def test_service_initialization(self, review_service):
        """测试服务初始化"""
        assert review_service is not None
        assert hasattr(review_service, 'create_reviewer')
        assert hasattr(review_service, 'get_reviewer')
        assert hasattr(review_service, 'create_task')
        assert hasattr(review_service, 'get_task')

    @pytest.mark.asyncio
    async def test_create_reviewer_basic(self, review_service, mock_session, sample_reviewer_create):
        """测试基本创建审核员功能"""
        # Mock数据库操作
        mock_reviewer_db = Mock()
        mock_reviewer_db.reviewer_id = sample_reviewer_create.reviewer_id
        mock_reviewer_db.name = sample_reviewer_create.name
        mock_reviewer_db.email = sample_reviewer_create.email
        mock_reviewer_db.specialties = sample_reviewer_create.specialties
        mock_reviewer_db.certifications = sample_reviewer_create.certifications or []
        mock_reviewer_db.experience_years = sample_reviewer_create.experience_years
        mock_reviewer_db.max_concurrent_tasks = sample_reviewer_create.max_concurrent_tasks
        mock_reviewer_db.working_hours = sample_reviewer_create.working_hours or {}
        mock_reviewer_db.timezone = sample_reviewer_create.timezone
        mock_reviewer_db.status = ReviewerStatus.ACTIVE
        mock_reviewer_db.current_task_count = 0
        mock_reviewer_db.is_available = True
        mock_reviewer_db.total_reviews = 0
        mock_reviewer_db.approved_reviews = 0
        mock_reviewer_db.rejected_reviews = 0
        mock_reviewer_db.average_review_time = 0.0
        mock_reviewer_db.quality_score = 0.0
        mock_reviewer_db.id = uuid4()
        mock_reviewer_db.created_at = datetime.now(timezone.utc)
        mock_reviewer_db.updated_at = datetime.now(timezone.utc)
        mock_reviewer_db.last_active_at = datetime.now(timezone.utc)
        
        # Mock session操作
        mock_session.refresh.return_value = None
        
        with patch('human_review_service.core.service.ReviewerDB') as mock_reviewer_class:
            mock_reviewer_class.return_value = mock_reviewer_db
            
            result = await review_service.create_reviewer(sample_reviewer_create, mock_session)
            
            # 验证结果
            assert result is not None
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_reviewer_by_id(self, review_service, mock_session):
        """测试通过ID获取审核员"""
        reviewer_id = "test_reviewer_001"
        
        # Mock数据库查询结果
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
        
        # Mock execute result
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_reviewer
        mock_session.execute.return_value = mock_result
        
        result = await review_service.get_reviewer(reviewer_id, mock_session)
        
        assert result is not None
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_reviewer_not_found(self, review_service, mock_session):
        """测试获取不存在的审核员"""
        reviewer_id = "nonexistent_reviewer"
        
        # Mock execute result
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        result = await review_service.get_reviewer(reviewer_id, mock_session)
        
        assert result is None
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_task_basic(self, review_service, mock_session, sample_task_create):
        """测试基本创建任务功能"""
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
        mock_task_db.expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        mock_task_db.assigned_to = None
        mock_task_db.reviewer_notes = None
        mock_task_db.review_comments = None
        mock_task_db.complexity_score = 0.5
        mock_task_db.risk_score = 0.3
        mock_task_db.metadata = {}
        mock_task_db.id = uuid4()
        mock_task_db.created_at = datetime.now(timezone.utc)
        mock_task_db.updated_at = datetime.now(timezone.utc)
        
        # Mock session操作
        mock_session.refresh.return_value = None
        
        with patch('human_review_service.core.service.ReviewTaskDB') as mock_task_class:
            mock_task_class.return_value = mock_task_db
            
            result = await review_service.create_task(mock_session, sample_task_create)
            
            # 验证结果
            assert result is not None
            # session.add会被调用两次：一次添加任务，一次添加历史记录
            assert mock_session.add.call_count == 2
            mock_session.commit.assert_called()
            mock_session.refresh.assert_called()

    @pytest.mark.asyncio
    async def test_get_task_by_id(self, review_service, mock_session):
        """测试通过ID获取任务"""
        task_id = "test_task_001"
        
        # Mock数据库查询结果
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
        mock_task.expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        mock_task.assigned_to = None
        mock_task.reviewer_notes = None
        mock_task.review_comments = None
        mock_task.complexity_score = 0.5
        mock_task.risk_score = 0.3
        mock_task.metadata = {}
        mock_task.id = uuid4()
        mock_task.created_at = datetime.now(timezone.utc)
        mock_task.updated_at = datetime.now(timezone.utc)
        
        # Mock execute result
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_task
        mock_session.execute.return_value = mock_result
        
        result = await review_service.get_task(mock_session, task_id)
        
        assert result is not None
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_task_not_found(self, review_service, mock_session):
        """测试获取不存在的任务"""
        task_id = "nonexistent_task"
        
        # Mock execute result
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        result = await review_service.get_task(mock_session, task_id)
        
        assert result is None
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_reviewers_basic(self, review_service, mock_session):
        """测试列出审核员基本功能"""
        # Mock数据库查询结果
        def create_mock_reviewer(reviewer_id, name):
            mock_reviewer = Mock()
            mock_reviewer.reviewer_id = reviewer_id
            mock_reviewer.name = name
            mock_reviewer.email = f"{name}@example.com"
            mock_reviewer.specialties = ["中医诊断"]
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
            return mock_reviewer
        
        mock_reviewers = [
            create_mock_reviewer("reviewer_001", "张医生"),
            create_mock_reviewer("reviewer_002", "李医生")
        ]
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_reviewers
        mock_session.execute.return_value = mock_result
        
        result = await review_service.list_reviewers(session=mock_session)
        
        assert result is not None
        assert len(result) == 2
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_tasks_basic(self, review_service, mock_session):
        """测试列出任务基本功能"""
        # Mock数据库查询结果
        def create_mock_task(task_id, content):
            mock_task = Mock()
            mock_task.task_id = task_id
            mock_task.content = {"complaint": content}
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
            mock_task.expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
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
        
        mock_tasks = [
            create_mock_task("task_001", "任务1"),
            create_mock_task("task_002", "任务2")
        ]
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_tasks
        mock_session.execute.return_value = mock_result
        
        result = await review_service.list_tasks(session=mock_session)
        
        assert result is not None
        assert len(result) == 2
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_reviewer_basic(self, review_service, mock_session):
        """测试更新审核员基本功能"""
        reviewer_id = "test_reviewer_001"
        
        # Mock现有审核员
        mock_reviewer = Mock()
        mock_reviewer.reviewer_id = reviewer_id
        mock_reviewer.name = "张医生"
        mock_reviewer.email = "zhang@example.com"
        mock_reviewer.specialties = ["中医诊断"]
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
        
        # Mock execute result
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_reviewer
        mock_session.execute.return_value = mock_result
        
        # 更新数据
        update_data = ReviewerUpdate(name="张主任医师")
        
        result = await review_service.update_reviewer(reviewer_id, update_data, mock_session)
        
        assert result is not None
        assert mock_reviewer.name == "张主任医师"
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_task_basic(self, review_service, mock_session):
        """测试更新任务基本功能"""
        task_id = "test_task_001"
        
        # Mock现有任务
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
        mock_task.expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        mock_task.assigned_to = None
        mock_task.reviewer_notes = None
        mock_task.review_comments = None
        mock_task.complexity_score = 0.5
        mock_task.risk_score = 0.3
        mock_task.metadata = {}
        mock_task.id = uuid4()
        mock_task.created_at = datetime.now(timezone.utc)
        mock_task.updated_at = datetime.now(timezone.utc)
        
        # Mock execute result
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_task
        mock_session.execute.return_value = mock_result
        
        # 更新数据
        update_data = ReviewTaskUpdate(status=ReviewStatus.IN_PROGRESS)
        
        result = await review_service.update_task(mock_session, task_id, update_data)
        
        assert result is not None
        assert mock_task.status == ReviewStatus.IN_PROGRESS
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_reviewer_basic(self, review_service, mock_session):
        """测试删除审核员基本功能"""
        reviewer_id = "test_reviewer_001"
        
        # Mock现有审核员
        mock_reviewer = Mock()
        mock_reviewer.reviewer_id = reviewer_id
        
        # Mock execute result for getting reviewer
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_reviewer
        
        # Mock execute result for counting active tasks
        mock_count_result = Mock()
        mock_count_result.scalar.return_value = 0  # 没有活跃任务
        
        # 设置execute的返回值序列
        mock_session.execute.side_effect = [mock_result, mock_count_result]
        
        result = await review_service.delete_reviewer(reviewer_id, mock_session)
        
        assert result is True
        mock_session.delete.assert_called_once_with(mock_reviewer)
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_task_basic(self, review_service, mock_session):
        """测试删除任务基本功能"""
        task_id = "test_task_001"
        
        # Mock现有任务
        mock_task = Mock()
        mock_task.task_id = task_id
        
        # Mock execute result
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_task
        mock_session.execute.return_value = mock_result
        
        result = await review_service.delete_task(mock_session, task_id)
        
        assert result is True
        mock_session.delete.assert_called_once_with(mock_task)
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_service_error_handling(self, review_service, mock_session):
        """测试服务错误处理"""
        reviewer_id = "test_reviewer_001"
        
        # Mock数据库异常
        mock_session.execute.side_effect = Exception("Database error")
        
        with pytest.raises(Exception):
            await review_service.get_reviewer(mock_session, reviewer_id)

    @pytest.mark.asyncio
    async def test_service_transaction_rollback(self, review_service, mock_session, sample_reviewer_create):
        """测试服务事务回滚"""
        # Mock数据库操作失败
        mock_session.commit.side_effect = Exception("Commit failed")
        
        with patch('human_review_service.core.service.ReviewerDB') as mock_reviewer_class:
            mock_reviewer_class.return_value = Mock()
            
            with pytest.raises(Exception):
                await review_service.create_reviewer(sample_reviewer_create, mock_session)
            
            # 验证回滚被调用
            mock_session.rollback.assert_called_once()


class TestServiceValidation:
    """服务验证测试"""

    @pytest.fixture
    def review_service(self):
        """创建审核服务实例"""
        return HumanReviewService()

    @pytest.fixture
    def mock_session(self):
        """模拟数据库会话"""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_validate_reviewer_data(self, review_service, mock_session):
        """测试审核员数据验证"""
        # 测试有效数据
        valid_data = ReviewerCreate(
            reviewer_id="valid_reviewer",
            name="有效医生",
            email="valid@example.com",
            specialties=["中医"],
            max_concurrent_tasks=3,
            experience_years=5
        )
        
        with patch('human_review_service.core.service.ReviewerDB') as mock_reviewer_class:
            # 创建完整的Mock对象
            mock_reviewer = Mock()
            mock_reviewer.reviewer_id = valid_data.reviewer_id
            mock_reviewer.name = valid_data.name
            mock_reviewer.email = valid_data.email
            mock_reviewer.specialties = valid_data.specialties
            mock_reviewer.certifications = valid_data.certifications or []
            mock_reviewer.experience_years = valid_data.experience_years
            mock_reviewer.max_concurrent_tasks = valid_data.max_concurrent_tasks
            mock_reviewer.working_hours = valid_data.working_hours or {}
            mock_reviewer.timezone = valid_data.timezone
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
            
            mock_reviewer_class.return_value = mock_reviewer
            mock_session.refresh.return_value = None
            
            result = await review_service.create_reviewer(valid_data, mock_session)
            assert result is not None

    @pytest.mark.asyncio
    async def test_validate_task_data(self, review_service, mock_session):
        """测试任务数据验证"""
        # 测试有效数据
        valid_data = ReviewTaskCreate(
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            content={"complaint": "有效的任务内容"},
            priority=ReviewPriority.NORMAL,
            user_id="user_123",
            agent_id="agent_123"
        )
        
        with patch('human_review_service.core.service.ReviewTaskDB') as mock_task_class:
            # 创建完整的Mock对象
            mock_task = Mock()
            mock_task.task_id = "test_task_001"
            mock_task.content = valid_data.content
            mock_task.review_type = valid_data.review_type
            mock_task.priority = valid_data.priority
            mock_task.user_id = valid_data.user_id
            mock_task.agent_id = valid_data.agent_id
            mock_task.status = ReviewStatus.PENDING
            mock_task.reviewer_id = None
            mock_task.assigned_at = None
            mock_task.started_at = None
            mock_task.completed_at = None
            mock_task.review_result = None
            mock_task.feedback = None
            mock_task.quality_score = None
            mock_task.estimated_duration = valid_data.estimated_duration
            mock_task.actual_duration = None
            mock_task.expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
            mock_task.assigned_to = None
            mock_task.reviewer_notes = None
            mock_task.review_comments = None
            mock_task.complexity_score = 0.5
            mock_task.risk_score = 0.3
            mock_task.metadata = {}
            mock_task.id = uuid4()
            mock_task.created_at = datetime.now(timezone.utc)
            mock_task.updated_at = datetime.now(timezone.utc)
            
            mock_task_class.return_value = mock_task
            mock_session.refresh.return_value = None
            
            result = await review_service.create_task(mock_session, valid_data)
            assert result is not None

    @pytest.mark.asyncio
    async def test_service_pagination(self, review_service, mock_session):
        """测试服务分页功能"""
        # Mock分页查询结果
        def create_mock_reviewer(i):
            mock_reviewer = Mock()
            mock_reviewer.reviewer_id = f"reviewer_{i}"
            mock_reviewer.name = f"医生{i}"
            mock_reviewer.email = f"doctor{i}@example.com"
            mock_reviewer.specialties = ["中医诊断"]
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
            return mock_reviewer
        
        mock_reviewers = [create_mock_reviewer(i) for i in range(5)]
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_reviewers
        mock_session.execute.return_value = mock_result
        
        result = await review_service.list_reviewers(session=mock_session, limit=5, offset=0)
        
        assert result is not None
        assert len(result) == 5

    @pytest.mark.asyncio
    async def test_service_filtering(self, review_service, mock_session):
        """测试服务过滤功能"""
        # Mock过滤查询结果
        def create_active_reviewer(reviewer_id):
            mock_reviewer = Mock()
            mock_reviewer.reviewer_id = reviewer_id
            mock_reviewer.name = f"医生{reviewer_id}"
            mock_reviewer.email = f"{reviewer_id}@example.com"
            mock_reviewer.specialties = ["中医诊断"]
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
            return mock_reviewer
        
        mock_active_reviewers = [
            create_active_reviewer("active_1"),
            create_active_reviewer("active_2")
        ]
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_active_reviewers
        mock_session.execute.return_value = mock_result
        
        result = await review_service.list_reviewers(
            session=mock_session, 
            filters={"status": ReviewerStatus.ACTIVE}
        )
        
        assert result is not None
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_service_sorting(self, review_service, mock_session):
        """测试服务排序功能"""
        # Mock排序查询结果
        def create_task_with_priority(task_id, priority):
            mock_task = Mock()
            mock_task.task_id = task_id
            mock_task.content = {"complaint": f"任务{task_id}"}
            mock_task.review_type = ReviewType.MEDICAL_DIAGNOSIS
            mock_task.priority = priority
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
            mock_task.expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
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
        
        mock_sorted_tasks = [
            create_task_with_priority("high_priority", ReviewPriority.HIGH),
            create_task_with_priority("normal_priority", ReviewPriority.NORMAL),
            create_task_with_priority("low_priority", ReviewPriority.LOW)
        ]
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_sorted_tasks
        mock_session.execute.return_value = mock_result
        
        result = await review_service.list_tasks(
            session=mock_session,
            filters={"order_by": "priority"}
        )
        
        assert result is not None
        assert len(result) == 3


class TestServiceIntegration:
    """服务集成测试"""

    @pytest.fixture
    def review_service(self):
        """创建审核服务实例"""
        return HumanReviewService()

    @pytest.fixture
    def mock_session(self):
        """模拟数据库会话"""
        session = AsyncMock()
        session.add = Mock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        session.execute = AsyncMock()
        session.scalar = AsyncMock()
        session.delete = Mock()
        session.rollback = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_complete_workflow(self, review_service, mock_session):
        """测试完整的工作流程"""
        # 1. 创建审核员
        reviewer_data = ReviewerCreate(
            reviewer_id="workflow_reviewer",
            name="工作流医生",
            email="workflow@example.com",
            specialties=["内科"],
            max_concurrent_tasks=5,
            experience_years=8
        )
        
        # 创建完整的Mock审核员对象
        mock_reviewer = Mock()
        mock_reviewer.reviewer_id = reviewer_data.reviewer_id
        mock_reviewer.name = reviewer_data.name
        mock_reviewer.email = reviewer_data.email
        mock_reviewer.specialties = reviewer_data.specialties
        mock_reviewer.certifications = reviewer_data.certifications or []
        mock_reviewer.experience_years = reviewer_data.experience_years
        mock_reviewer.max_concurrent_tasks = reviewer_data.max_concurrent_tasks
        mock_reviewer.working_hours = reviewer_data.working_hours or {}
        mock_reviewer.timezone = reviewer_data.timezone
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
        
        with patch('human_review_service.core.service.ReviewerDB', return_value=mock_reviewer):
            created_reviewer = await review_service.create_reviewer(reviewer_data, mock_session)
            assert created_reviewer is not None
        
        # 2. 创建任务
        task_data = ReviewTaskCreate(
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            content={"complaint": "工作流任务内容"},
            priority=ReviewPriority.HIGH,
            user_id="user_123",
            agent_id="agent_123"
        )
        
        # 创建完整的Mock任务对象
        mock_task = Mock()
        mock_task.task_id = "workflow_task"
        mock_task.content = task_data.content
        mock_task.review_type = task_data.review_type
        mock_task.priority = task_data.priority
        mock_task.user_id = task_data.user_id
        mock_task.agent_id = task_data.agent_id
        mock_task.status = ReviewStatus.PENDING
        mock_task.reviewer_id = None
        mock_task.assigned_at = None
        mock_task.started_at = None
        mock_task.completed_at = None
        mock_task.review_result = None
        mock_task.feedback = None
        mock_task.quality_score = None
        mock_task.estimated_duration = task_data.estimated_duration
        mock_task.actual_duration = None
        mock_task.expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        mock_task.assigned_to = None
        mock_task.reviewer_notes = None
        mock_task.review_comments = None
        mock_task.complexity_score = 0.5
        mock_task.risk_score = 0.3
        mock_task.metadata = {}
        mock_task.id = uuid4()
        mock_task.created_at = datetime.now(timezone.utc)
        mock_task.updated_at = datetime.now(timezone.utc)
        
        with patch('human_review_service.core.service.ReviewTaskDB', return_value=mock_task):
            created_task = await review_service.create_task(mock_session, task_data)
            assert created_task is not None
        
        # 3. 分配任务（模拟）
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_task
        mock_session.execute.return_value = mock_result
        
        updated_task = await review_service.update_task(
            mock_session, 
            "workflow_task", 
            ReviewTaskUpdate(status=ReviewStatus.IN_PROGRESS, assigned_to=reviewer_data.reviewer_id)
        )
        assert updated_task is not None
        
        # 4. 完成任务（模拟）
        completed_task = await review_service.update_task(
            mock_session,
            "workflow_task",
            ReviewTaskUpdate(status=ReviewStatus.APPROVED)
        )
        assert completed_task is not None

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, review_service, mock_session):
        """测试并发操作"""
        # 模拟并发创建多个审核员
        reviewer_data_list = [
            ReviewerCreate(
                reviewer_id=f"concurrent_reviewer_{i}",
                name=f"并发医生{i}",
                email=f"concurrent{i}@example.com",
                specialties=["内科"],
                max_concurrent_tasks=3,
                experience_years=5
            )
            for i in range(3)
        ]
        
        # Mock数据库操作
        def create_complete_mock_reviewer(data):
            mock_reviewer = Mock()
            mock_reviewer.reviewer_id = data.reviewer_id
            mock_reviewer.name = data.name
            mock_reviewer.email = data.email
            mock_reviewer.specialties = data.specialties
            mock_reviewer.certifications = data.certifications or []
            mock_reviewer.experience_years = data.experience_years
            mock_reviewer.max_concurrent_tasks = data.max_concurrent_tasks
            mock_reviewer.working_hours = data.working_hours or {}
            mock_reviewer.timezone = data.timezone
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
            return mock_reviewer
        
        mock_reviewers = [create_complete_mock_reviewer(data) for data in reviewer_data_list]
        
        with patch('human_review_service.core.service.ReviewerDB', side_effect=mock_reviewers):
            tasks = [
                review_service.create_reviewer(data, mock_session)
                for data in reviewer_data_list
            ]
            
            results = await asyncio.gather(*tasks)
            
            assert len(results) == 3
            assert all(result is not None for result in results)

    @pytest.mark.asyncio
    async def test_service_performance(self, review_service, mock_session):
        """测试服务性能"""
        
        # 模拟大量数据查询
        def create_perf_reviewer(i):
            mock_reviewer = Mock()
            mock_reviewer.reviewer_id = f"perf_reviewer_{i}"
            mock_reviewer.name = f"性能测试医生{i}"
            mock_reviewer.email = f"perf{i}@example.com"
            mock_reviewer.specialties = ["中医诊断"]
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
            return mock_reviewer
        
        # 减少数量以避免测试过慢
        mock_reviewers = [create_perf_reviewer(i) for i in range(100)]
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_reviewers
        mock_session.execute.return_value = mock_result
        
        start_time = time.time()
        result = await review_service.list_reviewers(session=mock_session)
        end_time = time.time()
        
        # 验证查询时间合理（应该很快，因为是mock）
        assert (end_time - start_time) < 1.0
        assert result is not None
        assert len(result) == 100 