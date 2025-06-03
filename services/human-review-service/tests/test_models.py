"""
数据模型测试
Data Models Tests

测试数据模型的各种功能
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from human_review_service.core.models import (
    ReviewerCreate,
    ReviewerDB,
    ReviewerUpdate,
    ReviewerStatus,
    ReviewTaskCreate,
    ReviewTaskDB,
    ReviewTaskUpdate,
    ReviewStatus,
    ReviewType,
    ReviewPriority,
    ReviewDecision,
    PaginatedResponse,
    ReviewerWorkload,
    DashboardStatistics,
)


class TestReviewerModels:
    """审核员模型测试"""

    def test_reviewer_create_valid(self):
        """测试创建有效的审核员"""
        reviewer_data = ReviewerCreate(
            reviewer_id="test_reviewer_001",
            name="张医生",
            email="zhang@example.com",
            specialties=["中医诊断", "方剂学"],
            max_concurrent_tasks=5,
            experience_years=10,
            certification_level="senior"
        )
        
        assert reviewer_data.reviewer_id == "test_reviewer_001"
        assert reviewer_data.name == "张医生"
        assert reviewer_data.email == "zhang@example.com"
        assert reviewer_data.specialties == ["中医诊断", "方剂学"]
        assert reviewer_data.max_concurrent_tasks == 5
        assert reviewer_data.experience_years == 10
        assert reviewer_data.certification_level == "senior"

    def test_reviewer_create_minimal(self):
        """测试创建最小必填字段的审核员"""
        reviewer_data = ReviewerCreate(
            reviewer_id="minimal_reviewer",
            name="最小医生",
            email="minimal@example.com",
            specialties=["全科"],
            max_concurrent_tasks=3
        )
        
        assert reviewer_data.reviewer_id == "minimal_reviewer"
        assert reviewer_data.name == "最小医生"
        assert reviewer_data.email == "minimal@example.com"
        assert reviewer_data.specialties == ["全科"]
        assert reviewer_data.max_concurrent_tasks == 3

    def test_reviewer_create_validation_empty_name(self):
        """测试空名称验证"""
        with pytest.raises(ValueError):
            ReviewerCreate(
                reviewer_id="test_reviewer",
                name="",  # 空名称
                email="test@example.com",
                specialties=["中医诊断"],
                max_concurrent_tasks=5
            )

    def test_reviewer_create_validation_invalid_email(self):
        """测试无效邮箱验证"""
        with pytest.raises(ValueError):
            ReviewerCreate(
                reviewer_id="test_reviewer",
                name="测试医生",
                email="invalid_email",  # 无效邮箱
                specialties=["中医诊断"],
                max_concurrent_tasks=5
            )

    def test_reviewer_create_validation_negative_tasks(self):
        """测试负数任务数验证"""
        with pytest.raises(ValueError):
            ReviewerCreate(
                reviewer_id="test_reviewer",
                name="测试医生",
                email="test@example.com",
                specialties=["中医诊断"],
                max_concurrent_tasks=-1  # 负数
            )

    def test_reviewer_db_model(self):
        """测试审核员数据库模型"""
        reviewer = ReviewerDB(
            reviewer_id="db_reviewer_001",
            name="数据库医生",
            email="db@example.com",
            specialties=["中医诊断"],
            max_concurrent_tasks=5,
            status=ReviewerStatus.ACTIVE,
            current_tasks=2,
            total_reviews=100,
            accuracy_rate=0.95,
            average_review_time=30.5,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        assert reviewer.reviewer_id == "db_reviewer_001"
        assert reviewer.status == ReviewerStatus.ACTIVE
        assert reviewer.current_tasks == 2
        assert reviewer.total_reviews == 100
        assert reviewer.accuracy_rate == 0.95
        assert reviewer.average_review_time == 30.5
        assert isinstance(reviewer.created_at, datetime)
        assert isinstance(reviewer.updated_at, datetime)

    def test_reviewer_update_model(self):
        """测试审核员更新模型"""
        update_data = ReviewerUpdate(
            name="更新后的医生",
            email="updated@example.com",
            specialties=["中医诊断", "西医诊断"],
            max_concurrent_tasks=8,
            experience_years=15
        )
        
        assert update_data.name == "更新后的医生"
        assert update_data.email == "updated@example.com"
        assert update_data.specialties == ["中医诊断", "西医诊断"]
        assert update_data.max_concurrent_tasks == 8
        assert update_data.experience_years == 15

    def test_reviewer_status_enum(self):
        """测试审核员状态枚举"""
        assert ReviewerStatus.ACTIVE == "active"
        assert ReviewerStatus.INACTIVE == "inactive"
        assert ReviewerStatus.SUSPENDED == "suspended"
        assert ReviewerStatus.PENDING == "pending"

    def test_reviewer_workload_model(self):
        """测试审核员工作负载模型"""
        workload = ReviewerWorkload(
            reviewer_id="workload_reviewer",
            current_tasks=3,
            max_concurrent_tasks=5,
            utilization_rate=0.6,
            pending_tasks=2,
            completed_today=5,
            average_completion_time=25.0
        )
        
        assert workload.reviewer_id == "workload_reviewer"
        assert workload.current_tasks == 3
        assert workload.max_concurrent_tasks == 5
        assert workload.utilization_rate == 0.6
        assert workload.pending_tasks == 2
        assert workload.completed_today == 5
        assert workload.average_completion_time == 25.0


class TestReviewTaskModels:
    """审核任务模型测试"""

    def test_review_task_create_valid(self):
        """测试创建有效的审核任务"""
        task_data = ReviewTaskCreate(
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.HIGH,
            content={
                "symptoms": ["头痛", "发热"],
                "diagnosis": "感冒",
                "treatment": "休息，多喝水"
            },
            user_id="user_123",
            agent_id="xiaoai_agent",
            estimated_duration=1800,
            metadata={"source": "mobile_app"}
        )
        
        assert task_data.review_type == ReviewType.MEDICAL_DIAGNOSIS
        assert task_data.priority == ReviewPriority.HIGH
        assert task_data.content["symptoms"] == ["头痛", "发热"]
        assert task_data.user_id == "user_123"
        assert task_data.agent_id == "xiaoai_agent"
        assert task_data.estimated_duration == 1800
        assert task_data.metadata["source"] == "mobile_app"

    def test_review_task_create_minimal(self):
        """测试创建最小必填字段的审核任务"""
        task_data = ReviewTaskCreate(
            review_type=ReviewType.GENERAL_CONSULTATION,
            priority=ReviewPriority.NORMAL,
            content={"question": "健康咨询"},
            user_id="user_456",
            agent_id="xiaoke_agent"
        )
        
        assert task_data.review_type == ReviewType.GENERAL_CONSULTATION
        assert task_data.priority == ReviewPriority.NORMAL
        assert task_data.content["question"] == "健康咨询"
        assert task_data.user_id == "user_456"
        assert task_data.agent_id == "xiaoke_agent"

    def test_review_task_create_validation_empty_content(self):
        """测试空内容验证"""
        with pytest.raises(ValueError):
            ReviewTaskCreate(
                review_type=ReviewType.MEDICAL_DIAGNOSIS,
                priority=ReviewPriority.NORMAL,
                content={},  # 空内容
                user_id="user_123",
                agent_id="xiaoai_agent"
            )

    def test_review_task_create_validation_empty_user_id(self):
        """测试空用户ID验证"""
        with pytest.raises(ValueError):
            ReviewTaskCreate(
                review_type=ReviewType.MEDICAL_DIAGNOSIS,
                priority=ReviewPriority.NORMAL,
                content={"test": "data"},
                user_id="",  # 空用户ID
                agent_id="xiaoai_agent"
            )

    def test_review_task_db_model(self):
        """测试审核任务数据库模型"""
        task = ReviewTaskDB(
            task_id=str(uuid4()),
            review_type=ReviewType.MEDICAL_DIAGNOSIS,
            priority=ReviewPriority.HIGH,
            content={"symptoms": ["头痛"]},
            user_id="user_123",
            agent_id="xiaoai_agent",
            status=ReviewStatus.PENDING,
            risk_score=0.7,
            assigned_to="reviewer_001",
            estimated_duration=1800,
            actual_duration=1500,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            assigned_at=datetime.now(timezone.utc),
            completed_at=None
        )
        
        assert task.review_type == ReviewType.MEDICAL_DIAGNOSIS
        assert task.priority == ReviewPriority.HIGH
        assert task.status == ReviewStatus.PENDING
        assert task.risk_score == 0.7
        assert task.assigned_to == "reviewer_001"
        assert task.estimated_duration == 1800
        assert task.actual_duration == 1500
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)
        assert isinstance(task.assigned_at, datetime)
        assert task.completed_at is None

    def test_review_task_update_model(self):
        """测试审核任务更新模型"""
        update_data = ReviewTaskUpdate(
            priority=ReviewPriority.URGENT,
            assigned_to="new_reviewer_002",
            status=ReviewStatus.IN_PROGRESS,
            review_comments="正在审核中",
            estimated_duration=2400
        )
        
        assert update_data.priority == ReviewPriority.URGENT
        assert update_data.assigned_to == "new_reviewer_002"
        assert update_data.status == ReviewStatus.IN_PROGRESS
        assert update_data.review_comments == "正在审核中"
        assert update_data.estimated_duration == 2400

    def test_review_type_enum(self):
        """测试审核类型枚举"""
        assert ReviewType.MEDICAL_DIAGNOSIS == "medical_diagnosis"
        assert ReviewType.TREATMENT_PLAN == "treatment_plan"
        assert ReviewType.MEDICATION_REVIEW == "medication_review"
        assert ReviewType.HEALTH_ADVICE == "health_advice"
        assert ReviewType.NUTRITION_ADVICE == "nutrition_advice"
        assert ReviewType.LIFESTYLE_RECOMMENDATION == "lifestyle_recommendation"
        assert ReviewType.EMERGENCY_ASSESSMENT == "emergency_assessment"
        assert ReviewType.GENERAL_CONSULTATION == "general_consultation"

    def test_review_priority_enum(self):
        """测试审核优先级枚举"""
        assert ReviewPriority.LOW == "low"
        assert ReviewPriority.NORMAL == "normal"
        assert ReviewPriority.HIGH == "high"
        assert ReviewPriority.URGENT == "urgent"
        assert ReviewPriority.CRITICAL == "critical"

    def test_review_status_enum(self):
        """测试审核状态枚举"""
        assert ReviewStatus.PENDING == "pending"
        assert ReviewStatus.ASSIGNED == "assigned"
        assert ReviewStatus.IN_PROGRESS == "in_progress"
        assert ReviewStatus.COMPLETED == "completed"
        assert ReviewStatus.APPROVED == "approved"
        assert ReviewStatus.REJECTED == "rejected"
        assert ReviewStatus.REQUIRES_REVISION == "requires_revision"
        assert ReviewStatus.CANCELLED == "cancelled"

    def test_review_decision_model(self):
        """测试审核决策模型"""
        decision = ReviewDecision(
            task_id="task_123",
            reviewer_id="reviewer_001",
            decision="approved",
            confidence_score=0.95,
            review_comments="审核通过，建议合理",
            reviewer_notes="患者症状描述清晰，诊断准确",
            suggested_improvements=["可以增加更多检查项目"],
            decision_timestamp=datetime.now(timezone.utc)
        )
        
        assert decision.task_id == "task_123"
        assert decision.reviewer_id == "reviewer_001"
        assert decision.decision == "approved"
        assert decision.confidence_score == 0.95
        assert decision.review_comments == "审核通过，建议合理"
        assert decision.reviewer_notes == "患者症状描述清晰，诊断准确"
        assert decision.suggested_improvements == ["可以增加更多检查项目"]
        assert isinstance(decision.decision_timestamp, datetime)


class TestUtilityModels:
    """工具模型测试"""

    def test_paginated_response_model(self):
        """测试分页响应模型"""
        items = [
            {"id": 1, "name": "item1"},
            {"id": 2, "name": "item2"},
            {"id": 3, "name": "item3"}
        ]
        
        response = PaginatedResponse(
            items=items,
            total=100,
            page=2,
            size=10,
            pages=10
        )
        
        assert response.items == items
        assert response.total == 100
        assert response.page == 2
        assert response.size == 10
        assert response.pages == 10
        assert len(response.items) == 3

    def test_paginated_response_empty(self):
        """测试空分页响应"""
        response = PaginatedResponse(
            items=[],
            total=0,
            page=1,
            size=10,
            pages=0
        )
        
        assert response.items == []
        assert response.total == 0
        assert response.page == 1
        assert response.size == 10
        assert response.pages == 0

    def test_dashboard_statistics_model(self):
        """测试仪表板统计模型"""
        stats = DashboardStatistics(
            total_tasks=1000,
            pending_tasks=50,
            in_progress_tasks=30,
            completed_tasks=900,
            approved_tasks=850,
            rejected_tasks=50,
            total_reviewers=25,
            active_reviewers=20,
            average_review_time=35.5,
            average_accuracy_rate=0.92,
            tasks_completed_today=45,
            high_priority_pending=5,
            system_load=0.75
        )
        
        assert stats.total_tasks == 1000
        assert stats.pending_tasks == 50
        assert stats.in_progress_tasks == 30
        assert stats.completed_tasks == 900
        assert stats.approved_tasks == 850
        assert stats.rejected_tasks == 50
        assert stats.total_reviewers == 25
        assert stats.active_reviewers == 20
        assert stats.average_review_time == 35.5
        assert stats.average_accuracy_rate == 0.92
        assert stats.tasks_completed_today == 45
        assert stats.high_priority_pending == 5
        assert stats.system_load == 0.75


class TestModelValidation:
    """模型验证测试"""

    def test_email_validation(self):
        """测试邮箱验证"""
        # 有效邮箱
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "123@test.com"
        ]
        
        for email in valid_emails:
            reviewer = ReviewerCreate(
                reviewer_id="test",
                name="测试",
                email=email,
                specialties=["测试"],
                max_concurrent_tasks=5
            )
            assert reviewer.email == email

        # 无效邮箱
        invalid_emails = [
            "invalid_email",
            "@example.com",
            "test@",
            "test..test@example.com",
            ""
        ]
        
        for email in invalid_emails:
            with pytest.raises(ValueError):
                ReviewerCreate(
                    reviewer_id="test",
                    name="测试",
                    email=email,
                    specialties=["测试"],
                    max_concurrent_tasks=5
                )

    def test_specialties_validation(self):
        """测试专业领域验证"""
        # 有效专业
        valid_specialties = [
            ["中医诊断"],
            ["中医诊断", "方剂学"],
            ["西医诊断", "内科", "外科"],
            ["全科医学"]
        ]
        
        for specialties in valid_specialties:
            reviewer = ReviewerCreate(
                reviewer_id="test",
                name="测试",
                email="test@example.com",
                specialties=specialties,
                max_concurrent_tasks=5
            )
            assert reviewer.specialties == specialties

        # 无效专业
        invalid_specialties = [
            [],  # 空列表
            [""],  # 空字符串
            [" "],  # 空白字符串
        ]
        
        for specialties in invalid_specialties:
            with pytest.raises(ValueError):
                ReviewerCreate(
                    reviewer_id="test",
                    name="测试",
                    email="test@example.com",
                    specialties=specialties,
                    max_concurrent_tasks=5
                )

    def test_task_content_validation(self):
        """测试任务内容验证"""
        # 有效内容
        valid_contents = [
            {"symptoms": ["头痛"]},
            {"diagnosis": "感冒", "treatment": "休息"},
            {"question": "健康咨询", "details": "详细描述"},
            {"complex": {"nested": {"data": "value"}}}
        ]
        
        for content in valid_contents:
            task = ReviewTaskCreate(
                review_type=ReviewType.MEDICAL_DIAGNOSIS,
                priority=ReviewPriority.NORMAL,
                content=content,
                user_id="user_123",
                agent_id="agent_123"
            )
            assert task.content == content

        # 无效内容
        invalid_contents = [
            {},  # 空字典
            None,  # None值
        ]
        
        for content in invalid_contents:
            with pytest.raises(ValueError):
                ReviewTaskCreate(
                    review_type=ReviewType.MEDICAL_DIAGNOSIS,
                    priority=ReviewPriority.NORMAL,
                    content=content,
                    user_id="user_123",
                    agent_id="agent_123"
                )

    def test_numeric_validation(self):
        """测试数值验证"""
        # 有效数值
        valid_values = [1, 5, 10, 100]
        
        for value in valid_values:
            reviewer = ReviewerCreate(
                reviewer_id="test",
                name="测试",
                email="test@example.com",
                specialties=["测试"],
                max_concurrent_tasks=value
            )
            assert reviewer.max_concurrent_tasks == value

        # 无效数值
        invalid_values = [0, -1, -10]
        
        for value in invalid_values:
            with pytest.raises(ValueError):
                ReviewerCreate(
                    reviewer_id="test",
                    name="测试",
                    email="test@example.com",
                    specialties=["测试"],
                    max_concurrent_tasks=value
                )

    def test_string_length_validation(self):
        """测试字符串长度验证"""
        # 测试名称长度
        long_name = "x" * 256  # 超长名称
        
        with pytest.raises(ValueError):
            ReviewerCreate(
                reviewer_id="test",
                name=long_name,
                email="test@example.com",
                specialties=["测试"],
                max_concurrent_tasks=5
            )

        # 测试ID长度
        long_id = "x" * 256  # 超长ID
        
        with pytest.raises(ValueError):
            ReviewerCreate(
                reviewer_id=long_id,
                name="测试",
                email="test@example.com",
                specialties=["测试"],
                max_concurrent_tasks=5
            ) 