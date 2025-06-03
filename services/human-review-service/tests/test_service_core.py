"""
服务层核心功能测试
Service Core Tests

专注于测试实际存在的HumanReviewService功能
"""

import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from uuid import uuid4

from human_review_service.core.service import HumanReviewService
from human_review_service.core.models import (
    ReviewerCreate,
    ReviewerDB,
    ReviewTaskCreate,
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
            task_id="test_task_001",
            content="患者主诉：头痛、发热",
            content_type="diagnosis",
            priority=ReviewPriority.HIGH
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
        mock_reviewer_db.id = uuid4()
        mock_reviewer_db.created_at = datetime.now(timezone.utc)
        
        # Mock session操作
        mock_session.refresh.return_value = None
        
        with patch('human_review_service.core.service.ReviewerDB') as mock_reviewer_class:
            mock_reviewer_class.return_value = mock_reviewer_db
            
            result = await review_service.create_reviewer(mock_session, sample_reviewer_create)
            
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
        mock_reviewer.status = ReviewerStatus.ACTIVE
        
        mock_session.scalar.return_value = mock_reviewer
        
        result = await review_service.get_reviewer(mock_session, reviewer_id)
        
        assert result is not None
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_reviewer_not_found(self, review_service, mock_session):
        """测试获取不存在的审核员"""
        reviewer_id = "nonexistent_reviewer"
        
        mock_session.scalar.return_value = None
        
        result = await review_service.get_reviewer(mock_session, reviewer_id)
        
        assert result is None
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_task_basic(self, review_service, mock_session, sample_task_create):
        """测试基本创建任务功能"""
        # Mock数据库操作
        mock_task_db = Mock()
        mock_task_db.task_id = sample_task_create.task_id
        mock_task_db.content = sample_task_create.content
        mock_task_db.content_type = sample_task_create.content_type
        mock_task_db.priority = sample_task_create.priority
        mock_task_db.id = uuid4()
        mock_task_db.created_at = datetime.now(timezone.utc)
        
        # Mock session操作
        mock_session.refresh.return_value = None
        
        with patch('human_review_service.core.service.ReviewTaskDB') as mock_task_class:
            mock_task_class.return_value = mock_task_db
            
            result = await review_service.create_task(mock_session, sample_task_create)
            
            # 验证结果
            assert result is not None
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_task_by_id(self, review_service, mock_session):
        """测试通过ID获取任务"""
        task_id = "test_task_001"
        
        # Mock数据库查询结果
        mock_task = Mock()
        mock_task.task_id = task_id
        mock_task.content = "患者主诉：头痛、发热"
        mock_task.status = ReviewStatus.PENDING
        
        mock_session.scalar.return_value = mock_task
        
        result = await review_service.get_task(mock_session, task_id)
        
        assert result is not None
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_task_not_found(self, review_service, mock_session):
        """测试获取不存在的任务"""
        task_id = "nonexistent_task"
        
        mock_session.scalar.return_value = None
        
        result = await review_service.get_task(mock_session, task_id)
        
        assert result is None
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_reviewers_basic(self, review_service, mock_session):
        """测试列出审核员基本功能"""
        # Mock数据库查询结果
        mock_reviewers = [
            Mock(reviewer_id="reviewer_001", name="张医生"),
            Mock(reviewer_id="reviewer_002", name="李医生")
        ]
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_reviewers
        mock_session.execute.return_value = mock_result
        
        result = await review_service.list_reviewers(mock_session)
        
        assert result is not None
        assert len(result) == 2
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_tasks_basic(self, review_service, mock_session):
        """测试列出任务基本功能"""
        # Mock数据库查询结果
        mock_tasks = [
            Mock(task_id="task_001", content="任务1"),
            Mock(task_id="task_002", content="任务2")
        ]
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_tasks
        mock_session.execute.return_value = mock_result
        
        result = await review_service.list_tasks(mock_session)
        
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
        
        mock_session.scalar.return_value = mock_reviewer
        
        # 更新数据
        update_data = {"name": "张主任医师"}
        
        result = await review_service.update_reviewer(mock_session, reviewer_id, update_data)
        
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
        mock_task.status = ReviewStatus.PENDING
        
        mock_session.scalar.return_value = mock_task
        
        # 更新数据
        update_data = {"status": ReviewStatus.IN_PROGRESS}
        
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
        
        mock_session.scalar.return_value = mock_reviewer
        
        result = await review_service.delete_reviewer(mock_session, reviewer_id)
        
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
        
        mock_session.scalar.return_value = mock_task
        
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
                await review_service.create_reviewer(mock_session, sample_reviewer_create)
            
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
            mock_reviewer_class.return_value = Mock()
            mock_session.refresh.return_value = None
            
            result = await review_service.create_reviewer(mock_session, valid_data)
            assert result is not None

    @pytest.mark.asyncio
    async def test_validate_task_data(self, review_service, mock_session):
        """测试任务数据验证"""
        # 测试有效数据
        valid_data = ReviewTaskCreate(
            task_id="valid_task",
            content="有效的任务内容",
            content_type="diagnosis",
            priority=ReviewPriority.MEDIUM
        )
        
        with patch('human_review_service.core.service.ReviewTaskDB') as mock_task_class:
            mock_task_class.return_value = Mock()
            mock_session.refresh.return_value = None
            
            result = await review_service.create_task(mock_session, valid_data)
            assert result is not None

    @pytest.mark.asyncio
    async def test_service_pagination(self, review_service, mock_session):
        """测试服务分页功能"""
        # Mock分页查询结果
        mock_reviewers = [Mock(reviewer_id=f"reviewer_{i}") for i in range(10)]
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_reviewers[:5]  # 模拟分页
        mock_session.execute.return_value = mock_result
        
        result = await review_service.list_reviewers(mock_session, skip=0, limit=5)
        
        assert result is not None
        assert len(result) == 5

    @pytest.mark.asyncio
    async def test_service_filtering(self, review_service, mock_session):
        """测试服务过滤功能"""
        # Mock过滤查询结果
        mock_active_reviewers = [
            Mock(reviewer_id="active_1", status=ReviewerStatus.ACTIVE),
            Mock(reviewer_id="active_2", status=ReviewerStatus.ACTIVE)
        ]
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_active_reviewers
        mock_session.execute.return_value = mock_result
        
        result = await review_service.list_reviewers(
            mock_session, 
            status=ReviewerStatus.ACTIVE
        )
        
        assert result is not None
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_service_sorting(self, review_service, mock_session):
        """测试服务排序功能"""
        # Mock排序查询结果
        mock_sorted_tasks = [
            Mock(task_id="high_priority", priority=ReviewPriority.HIGH),
            Mock(task_id="medium_priority", priority=ReviewPriority.MEDIUM),
            Mock(task_id="low_priority", priority=ReviewPriority.LOW)
        ]
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_sorted_tasks
        mock_session.execute.return_value = mock_result
        
        result = await review_service.list_tasks(
            mock_session,
            order_by="priority"
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
        
        mock_reviewer = Mock()
        mock_reviewer.reviewer_id = reviewer_data.reviewer_id
        
        with patch('human_review_service.core.service.ReviewerDB', return_value=mock_reviewer):
            created_reviewer = await review_service.create_reviewer(mock_session, reviewer_data)
            assert created_reviewer is not None
        
        # 2. 创建任务
        task_data = ReviewTaskCreate(
            task_id="workflow_task",
            content="工作流任务内容",
            content_type="diagnosis",
            priority=ReviewPriority.HIGH
        )
        
        mock_task = Mock()
        mock_task.task_id = task_data.task_id
        
        with patch('human_review_service.core.service.ReviewTaskDB', return_value=mock_task):
            created_task = await review_service.create_task(mock_session, task_data)
            assert created_task is not None
        
        # 3. 分配任务（模拟）
        mock_session.scalar.return_value = mock_task
        updated_task = await review_service.update_task(
            mock_session, 
            task_data.task_id, 
            {"status": ReviewStatus.IN_PROGRESS, "reviewer_id": reviewer_data.reviewer_id}
        )
        assert updated_task is not None
        
        # 4. 完成任务（模拟）
        completed_task = await review_service.update_task(
            mock_session,
            task_data.task_id,
            {"status": ReviewStatus.APPROVED}
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
        mock_reviewers = [Mock(reviewer_id=data.reviewer_id) for data in reviewer_data_list]
        
        with patch('human_review_service.core.service.ReviewerDB', side_effect=mock_reviewers):
            tasks = [
                review_service.create_reviewer(mock_session, data)
                for data in reviewer_data_list
            ]
            
            results = await asyncio.gather(*tasks)
            
            assert len(results) == 3
            assert all(result is not None for result in results)

    @pytest.mark.asyncio
    async def test_service_performance(self, review_service, mock_session):
        """测试服务性能"""
        import time
        
        # 模拟大量数据查询
        mock_reviewers = [Mock(reviewer_id=f"perf_reviewer_{i}") for i in range(1000)]
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_reviewers
        mock_session.execute.return_value = mock_result
        
        start_time = time.time()
        result = await review_service.list_reviewers(mock_session)
        end_time = time.time()
        
        # 验证查询时间合理（应该很快，因为是mock）
        assert (end_time - start_time) < 1.0
        assert result is not None
        assert len(result) == 1000 