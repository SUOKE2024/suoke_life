"""
test_api_endpoints - 索克生活项目模块
"""

    from human_review_service.core.database import get_session_dependency
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from httpx import AsyncClient
from human_review_service.api.main import create_app
from human_review_service.core.models import (
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from uuid import uuid4
import asyncio
import pytest

"""
API端点测试
API Endpoints Tests

测试所有API端点的功能和错误处理
"""



    ReviewerCreate,
    ReviewerDB,
    ReviewTaskCreate,
    ReviewTaskDB,
    ReviewStatus,
    ReviewType,
    ReviewPriority,
    ReviewerStatus
)


@pytest.fixture
def mock_session():
    """模拟数据库会话"""
    session = AsyncMock()
    session.add = Mock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def app():
    """创建测试应用"""
    return create_app(skip_lifespan=True)


@pytest.fixture
def client(app, mock_session):
    """创建测试客户端"""
    
    # Mock数据库依赖
    async def mock_get_session():
        yield mock_session
    
    app.dependency_overrides[get_session_dependency] = mock_get_session
    
    return TestClient(app)


@pytest.fixture
async def async_client(app):
    """创建异步测试客户端"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


class TestReviewerEndpoints:
    """审核员端点测试"""

    def test_create_reviewer_success(self, client, mock_session):
        """测试成功创建审核员"""
        reviewer_data = {
            "reviewer_id": "test_reviewer_001",
            "name": "张医生",
            "email": "zhang@example.com",
            "specialties": ["中医诊断", "方剂学"],
            "max_concurrent_tasks": 5,
            "experience_years": 10
        }

        # Mock服务方法
        with patch('human_review_service.core.service.HumanReviewService.create_reviewer') as mock_create:
            mock_reviewer = Mock()
            mock_reviewer.reviewer_id = reviewer_data["reviewer_id"]
            mock_reviewer.name = reviewer_data["name"]
            mock_reviewer.email = reviewer_data["email"]
            mock_reviewer.specialties = reviewer_data["specialties"]
            mock_reviewer.max_concurrent_tasks = reviewer_data["max_concurrent_tasks"]
            mock_reviewer.experience_years = reviewer_data["experience_years"]
            mock_reviewer.status = ReviewerStatus.ACTIVE
            mock_reviewer.id = uuid4()
            mock_reviewer.created_at = datetime.now(timezone.utc)
            mock_reviewer.updated_at = datetime.now(timezone.utc)
            mock_reviewer.current_task_count = 0
            mock_reviewer.is_available = True
            mock_reviewer.total_reviews = 0
            mock_reviewer.approved_reviews = 0
            mock_reviewer.rejected_reviews = 0
            mock_reviewer.average_review_time = 1800.0
            mock_reviewer.quality_score = 5.0
            mock_reviewer.last_active_at = None
            mock_reviewer.certifications = []
            mock_reviewer.working_hours = {}
            mock_reviewer.timezone = "Asia/Shanghai"
            mock_reviewer.certification_level = "senior"

            mock_create.return_value = mock_reviewer

            response = client.post("/api/v1/reviewers/", json=reviewer_data)

        assert response.status_code == 201
        data = response.json()
        assert data["reviewer_id"] == reviewer_data["reviewer_id"]
        assert data["name"] == reviewer_data["name"]
        assert data["email"] == reviewer_data["email"]
        assert data["specialties"] == reviewer_data["specialties"]

    def test_create_reviewer_validation_error(self, client):
        """测试创建审核员验证错误"""
        invalid_data = {
            "name": "张医生",
            # 缺少必填字段
        }

        response = client.post("/api/v1/reviewers/", json=invalid_data)
        assert response.status_code == 422

    def test_get_reviewer_success(self, client, mock_session):
        """测试成功获取审核员"""
        reviewer_id = "test_reviewer_001"
        
        with patch('human_review_service.core.service.HumanReviewService.get_reviewer') as mock_get:
            mock_reviewer = Mock()
            mock_reviewer.reviewer_id = reviewer_id
            mock_reviewer.name = "张医生"
            mock_reviewer.email = "zhang@example.com"
            mock_reviewer.specialties = ["中医诊断"]
            mock_reviewer.max_concurrent_tasks = 5
            mock_reviewer.status = ReviewerStatus.ACTIVE
            mock_reviewer.id = uuid4()
            mock_reviewer.created_at = datetime.now(timezone.utc)
            mock_reviewer.updated_at = datetime.now(timezone.utc)
            mock_reviewer.current_task_count = 0
            mock_reviewer.is_available = True
            mock_reviewer.total_reviews = 0
            mock_reviewer.approved_reviews = 0
            mock_reviewer.rejected_reviews = 0
            mock_reviewer.average_review_time = 1800.0
            mock_reviewer.quality_score = 5.0
            mock_reviewer.last_active_at = None
            mock_reviewer.experience_years = 10
            mock_reviewer.certifications = None
            mock_reviewer.working_hours = None
            mock_reviewer.timezone = "Asia/Shanghai"
            
            mock_get.return_value = mock_reviewer

            response = client.get(f"/api/v1/reviewers/{reviewer_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["reviewer_id"] == reviewer_id

    def test_get_reviewer_not_found(self, client, mock_session):
        """测试获取不存在的审核员"""
        reviewer_id = "nonexistent"
        
        with patch('human_review_service.core.service.HumanReviewService.get_reviewer') as mock_get:
            mock_get.return_value = None

            response = client.get(f"/api/v1/reviewers/{reviewer_id}")

        assert response.status_code == 404

    def test_list_reviewers_success(self, client, mock_session):
        """测试成功获取审核员列表"""
        with patch('human_review_service.core.service.HumanReviewService.list_reviewers') as mock_list:
            mock_reviewer = Mock()
            mock_reviewer.reviewer_id = "reviewer_001"
            mock_reviewer.name = "张医生"
            mock_reviewer.email = "zhang@example.com"
            mock_reviewer.specialties = ["中医诊断"]
            mock_reviewer.max_concurrent_tasks = 5
            mock_reviewer.status = ReviewerStatus.ACTIVE
            mock_reviewer.id = uuid4()
            mock_reviewer.created_at = datetime.now(timezone.utc)
            mock_reviewer.updated_at = datetime.now(timezone.utc)
            mock_reviewer.current_task_count = 0
            mock_reviewer.is_available = True
            mock_reviewer.total_reviews = 0
            mock_reviewer.approved_reviews = 0
            mock_reviewer.rejected_reviews = 0
            mock_reviewer.average_review_time = 1800.0
            mock_reviewer.quality_score = 5.0
            mock_reviewer.last_active_at = None
            mock_reviewer.experience_years = 10
            mock_reviewer.certifications = None
            mock_reviewer.working_hours = None
            mock_reviewer.timezone = "Asia/Shanghai"
            
            mock_list.return_value = [mock_reviewer]

            response = client.get("/api/v1/reviewers/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["reviewer_id"] == "reviewer_001"

    def test_update_reviewer_success(self, client, mock_session):
        """测试成功更新审核员"""
        reviewer_id = "test_reviewer_001"
        update_data = {
            "name": "张医生（更新）",
            "max_concurrent_tasks": 8
        }

        with patch('human_review_service.core.service.HumanReviewService.update_reviewer') as mock_update:
            mock_reviewer = Mock()
            mock_reviewer.reviewer_id = reviewer_id
            mock_reviewer.name = update_data["name"]
            mock_reviewer.email = "zhang@example.com"
            mock_reviewer.specialties = ["中医诊断"]
            mock_reviewer.max_concurrent_tasks = update_data["max_concurrent_tasks"]
            mock_reviewer.status = ReviewerStatus.ACTIVE
            mock_reviewer.id = uuid4()
            mock_reviewer.created_at = datetime.now(timezone.utc)
            mock_reviewer.updated_at = datetime.now(timezone.utc)
            mock_reviewer.current_task_count = 0
            mock_reviewer.is_available = True
            mock_reviewer.total_reviews = 0
            mock_reviewer.approved_reviews = 0
            mock_reviewer.rejected_reviews = 0
            mock_reviewer.average_review_time = 1800.0
            mock_reviewer.quality_score = 5.0
            mock_reviewer.last_active_at = None
            mock_reviewer.experience_years = 10
            mock_reviewer.certifications = None
            mock_reviewer.working_hours = None
            mock_reviewer.timezone = "Asia/Shanghai"
            
            mock_update.return_value = mock_reviewer

            response = client.put(f"/api/v1/reviewers/{reviewer_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]

    def test_delete_reviewer_success(self, client, mock_session):
        """测试成功删除审核员"""
        reviewer_id = "test_reviewer_001"

        with patch('human_review_service.core.service.HumanReviewService.delete_reviewer') as mock_delete:
            mock_delete.return_value = True

            response = client.delete(f"/api/v1/reviewers/{reviewer_id}")

        assert response.status_code == 204

    def test_get_reviewer_workload(self, client, mock_session):
        """测试获取审核员工作负载"""
        reviewer_id = "test_reviewer_001"

        with patch('human_review_service.core.service.HumanReviewService.get_reviewer_workload') as mock_workload:
            mock_workload.return_value = {
                "reviewer_id": reviewer_id,
                "current_tasks": 3,
                "max_concurrent_tasks": 5,
                "utilization_rate": 0.6
            }

            response = client.get(f"/api/v1/reviewers/{reviewer_id}/workload")

        assert response.status_code == 200
        data = response.json()
        assert data["reviewer_id"] == reviewer_id
        assert data["current_tasks"] == 3


class TestReviewTaskEndpoints:
    """审核任务端点测试"""

    def test_create_task_success(self, client, mock_session):
        """测试成功创建任务"""
        task_data = {
            "review_type": "medical_diagnosis",
            "priority": "high",
            "content": {
                "symptoms": ["头痛", "发热"],
                "diagnosis": "感冒"
            },
            "user_id": "user_123",
            "agent_id": "xiaoai_agent"
        }

        with patch('human_review_service.core.service.HumanReviewService.submit_review') as mock_submit:
            mock_task = Mock()
            mock_task.id = uuid4()
            mock_task.task_id = "task_001"
            mock_task.review_type = ReviewType.MEDICAL_DIAGNOSIS
            mock_task.priority = ReviewPriority.HIGH
            mock_task.content = task_data["content"]
            mock_task.user_id = task_data["user_id"]
            mock_task.agent_id = task_data["agent_id"]
            mock_task.status = ReviewStatus.PENDING
            mock_task.created_at = datetime.now(timezone.utc)
            mock_task.updated_at = datetime.now(timezone.utc)
            mock_task.assigned_to = None
            mock_task.reviewer_notes = None
            mock_task.review_comments = None
            mock_task.review_result = None
            mock_task.assigned_at = None
            mock_task.started_at = None
            mock_task.completed_at = None
            mock_task.expires_at = None
            mock_task.estimated_duration = 1800
            mock_task.actual_duration = None
            mock_task.complexity_score = 1.0
            mock_task.risk_score = 0.0
            
            mock_submit.return_value = mock_task

            response = client.post("/api/v1/tasks/", json=task_data)

        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == task_data["user_id"]

    def test_get_task_success(self, client, mock_session):
        """测试成功获取任务"""
        task_id = "task_001"

        with patch('human_review_service.core.service.HumanReviewService.get_review_task') as mock_get:
            mock_task = Mock()
            mock_task.id = uuid4()
            mock_task.task_id = task_id
            mock_task.review_type = ReviewType.MEDICAL_DIAGNOSIS
            mock_task.priority = ReviewPriority.HIGH
            mock_task.content = {"test": "data"}
            mock_task.user_id = "user_123"
            mock_task.agent_id = "agent_123"
            mock_task.status = ReviewStatus.PENDING
            mock_task.created_at = datetime.now(timezone.utc)
            mock_task.updated_at = datetime.now(timezone.utc)
            mock_task.assigned_to = None
            mock_task.reviewer_notes = None
            mock_task.review_comments = None
            mock_task.review_result = None
            mock_task.assigned_at = None
            mock_task.started_at = None
            mock_task.completed_at = None
            mock_task.expires_at = None
            mock_task.estimated_duration = 1800
            mock_task.actual_duration = None
            mock_task.complexity_score = 1.0
            mock_task.risk_score = 0.0
            
            mock_get.return_value = mock_task

            response = client.get(f"/api/v1/tasks/{task_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == task_id


class TestHealthEndpoints:
    """健康检查端点测试"""

    def test_health_check(self, client):
        """测试健康检查"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data

    def test_readiness_check(self, client):
        """测试就绪检查"""
        response = client.get("/ready")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "checks" in data


class TestErrorHandling:
    """错误处理测试"""

    def test_method_not_allowed(self, client):
        """测试方法不允许错误"""
        response = client.patch("/api/v1/reviewers/")
        assert response.status_code == 405

    def test_invalid_json(self, client):
        """测试无效JSON错误"""
        response = client.post(
            "/api/v1/reviewers/",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422


class TestAuthentication:
    """认证测试"""

    def test_unauthorized_access(self, client):
        """测试未授权访问"""
        # 这里假设某些端点需要认证
        # 在实际实现中，应该根据具体的认证机制来测试
        pass 