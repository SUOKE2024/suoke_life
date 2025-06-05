"""
简化的服务测试
Simple Service Tests

专注于测试基本功能，避免复杂的Mock验证
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timezone
from uuid import uuid4

from human_review_service.core.service import HumanReviewService
from human_review_service.core.models import (
    ReviewerCreate, ReviewTaskCreate, ReviewType, ReviewPriority
)


class TestServiceBasic:
    """基本服务功能测试"""

    @pytest.fixture
    def review_service(self):
        """创建审核服务实例"""
        return HumanReviewService()

    def test_service_initialization(self, review_service):
        """测试服务初始化"""
        assert review_service is not None
        assert hasattr(review_service, 'create_reviewer')
        assert hasattr(review_service, 'get_reviewer')
        assert hasattr(review_service, 'create_task')
        assert hasattr(review_service, 'get_task')
        assert hasattr(review_service, 'list_reviewers')
        assert hasattr(review_service, 'list_tasks')
        assert hasattr(review_service, 'update_reviewer')
        assert hasattr(review_service, 'update_task')
        assert hasattr(review_service, 'delete_reviewer')
        assert hasattr(review_service, 'delete_task')

    def test_reviewer_create_model(self):
        """测试审核员创建模型"""
        reviewer_data = ReviewerCreate(
            reviewer_id="test_reviewer",
            name="测试医生",
            email="test@example.com",
            specialties=["内科"],
            max_concurrent_tasks=5,
            experience_years=10
        )
        
        assert reviewer_data.reviewer_id == "test_reviewer"
        assert reviewer_data.name == "测试医生"
        assert reviewer_data.email == "test@example.com"
        assert reviewer_data.specialties == ["内科"]
        assert reviewer_data.max_concurrent_tasks == 5
        assert reviewer_data.experience_years == 10

    def test_task_create_model(self):
        """测试任务创建模型"""
        task_data = ReviewTaskCreate(
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            content={"complaint": "头痛"},
            priority=ReviewPriority.HIGH,
            user_id="user_123",
            agent_id="agent_123"
        )
        
        assert task_data.review_type == ReviewType.MEDICAL_DIAGNOSIS
        assert task_data.content == {"complaint": "头痛"}
        assert task_data.priority == ReviewPriority.HIGH
        assert task_data.user_id == "user_123"
        assert task_data.agent_id == "agent_123"

    @pytest.mark.asyncio
    async def test_service_methods_exist(self, review_service):
        """测试服务方法存在性"""
        # 检查所有必要的方法都存在
        methods = [
            'create_reviewer', 'get_reviewer', 'update_reviewer', 'delete_reviewer',
            'list_reviewers', 'create_task', 'get_task', 'update_task', 
            'delete_task', 'list_tasks', 'submit_review', 'complete_review'
        ]
        
        for method in methods:
            assert hasattr(review_service, method), f"Method {method} not found"
            assert callable(getattr(review_service, method)), f"Method {method} is not callable" 