"""
API层测试
API Layer Tests

测试REST API端点
"""

import pytest
from fastapi.testclient import TestClient

from ..api.main import app

class TestReviewAPI:
    """审核任务API测试"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return TestClient(app)

    @pytest.mark.asyncio
    async def test_create_review_task(self, client):
        """测试创建审核任务"""
        task_data = {
            "content_type": "diagnosis",
            "content_id": "test_diag_123",
            "content_data": {
                "symptoms": ["头痛", "发热"],
                "diagnosis": "感冒",
                "treatment": "多休息，多喝水",
            },
            "review_type": "medical_diagnosis",
            "priority": "normal",
            "requester_id": "test_user_123",
            "metadata": {"source": "test"},
        }

        response = client.post("/api/v1/reviews/", json=task_data)

        assert response.status_code == 201
        data = response.json()
        assert data["content_type"] == "diagnosis"
        assert data["content_id"] == "test_diag_123"
        assert data["review_type"] == "medical_diagnosis"
        assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_get_review_task(self, client):
        """测试获取审核任务"""
        # 先创建一个任务
        task_data = {
            "content_type": "diagnosis",
            "content_id": "test_get_diag_123",
            "content_data": {"test": "data"},
            "review_type": "medical_diagnosis",
            "priority": "normal",
            "requester_id": "test_user_get_123",
        }

        create_response = client.post("/api/v1/reviews/", json=task_data)
        assert create_response.status_code == 201
        task_id = create_response.json()["task_id"]

        # 获取任务
        get_response = client.get(f"/api/v1/reviews/{task_id}")

        assert get_response.status_code == 200
        data = get_response.json()
        assert data["task_id"] == task_id
        assert data["content_type"] == "diagnosis"

    @pytest.mark.asyncio
    async def test_list_review_tasks(self, client):
        """测试列出审核任务"""
        # 创建几个任务
        for i in range(3):
            task_data = {
                "content_type": "diagnosis",
                "content_id": f"test_list_diag_{i}",
                "content_data": {"test": f"data_{i}"},
                "review_type": "medical_diagnosis",
                "priority": "normal",
                "requester_id": f"test_user_list_{i}",
            }
            client.post("/api/v1/reviews/", json=task_data)

        # 列出任务
        response = client.get("/api/v1/reviews/")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 3

    @pytest.mark.asyncio
    async def test_update_review_task(self, client):
        """测试更新审核任务"""
        # 创建任务
        task_data = {
            "content_type": "diagnosis",
            "content_id": "test_update_diag_123",
            "content_data": {"test": "data"},
            "review_type": "medical_diagnosis",
            "priority": "normal",
            "requester_id": "test_user_update_123",
        }

        create_response = client.post("/api/v1/reviews/", json=task_data)
        task_id = create_response.json()["task_id"]

        # 更新任务
        update_data = {"priority": "high", "metadata": {"updated": True}}

        update_response = client.put(f"/api/v1/reviews/{task_id}", json=update_data)

        assert update_response.status_code == 200
        data = update_response.json()
        assert data["priority"] == "high"

class TestReviewerAPI:
    """审核员API测试"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return TestClient(app)

    @pytest.mark.asyncio
    async def test_create_reviewer(self, client):
        """测试创建审核员"""
        reviewer_data = {
            "name": "API测试医生",
            "email": "api_test@example.com",
            "specialties": ["中医诊断", "方剂学"],
            "max_concurrent_tasks": 5,
        }

        response = client.post("/api/v1/reviewers/", json=reviewer_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "API测试医生"
        assert data["email"] == "api_test@example.com"
        assert data["specialties"] == ["中医诊断", "方剂学"]
        assert data["status"] == "active"

    @pytest.mark.asyncio
    async def test_get_reviewer(self, client):
        """测试获取审核员"""
        # 创建审核员
        reviewer_data = {
            "name": "API获取测试医生",
            "email": "api_get_test@example.com",
            "specialties": ["西医诊断"],
            "max_concurrent_tasks": 3,
        }

        create_response = client.post("/api/v1/reviewers/", json=reviewer_data)
        reviewer_id = create_response.json()["reviewer_id"]

        # 获取审核员
        get_response = client.get(f"/api/v1/reviewers/{reviewer_id}")

        assert get_response.status_code == 200
        data = get_response.json()
        assert data["reviewer_id"] == reviewer_id
        assert data["name"] == "API获取测试医生"

    @pytest.mark.asyncio
    async def test_list_reviewers(self, client):
        """测试列出审核员"""
        # 创建几个审核员
        for i in range(3):
            reviewer_data = {
                "name": f"API列表测试医生{i}",
                "email": f"api_list_test{i}@example.com",
                "specialties": ["中医诊断"],
                "max_concurrent_tasks": 3 + i,
            }
            client.post("/api/v1/reviewers/", json=reviewer_data)

        # 列出审核员
        response = client.get("/api/v1/reviewers/")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 3

    @pytest.mark.asyncio
    async def test_update_reviewer(self, client):
        """测试更新审核员"""
        # 创建审核员
        reviewer_data = {
            "name": "API更新测试医生",
            "email": "api_update_test@example.com",
            "specialties": ["营养学"],
            "max_concurrent_tasks": 2,
        }

        create_response = client.post("/api/v1/reviewers/", json=reviewer_data)
        reviewer_id = create_response.json()["reviewer_id"]

        # 更新审核员
        update_data = {"name": "API更新后的医生", "max_concurrent_tasks": 8}

        update_response = client.put(
            f"/api/v1/reviewers/{reviewer_id}", json=update_data
        )

        assert update_response.status_code == 200
        data = update_response.json()
        assert data["name"] == "API更新后的医生"
        assert data["max_concurrent_tasks"] == 8

    @pytest.mark.asyncio
    async def test_activate_deactivate_reviewer(self, client):
        """测试激活和停用审核员"""
        # 创建审核员
        reviewer_data = {
            "name": "API激活测试医生",
            "email": "api_activate_test@example.com",
            "specialties": ["健康管理"],
            "max_concurrent_tasks": 4,
        }

        create_response = client.post("/api/v1/reviewers/", json=reviewer_data)
        reviewer_id = create_response.json()["reviewer_id"]

        # 停用审核员
        deactivate_response = client.post(f"/api/v1/reviewers/{reviewer_id}/deactivate")
        assert deactivate_response.status_code == 200
        data = deactivate_response.json()
        assert data["status"] == "inactive"

        # 激活审核员
        activate_response = client.post(f"/api/v1/reviewers/{reviewer_id}/activate")
        assert activate_response.status_code == 200
        data = activate_response.json()
        assert data["status"] == "active"

class TestDashboardAPI:
    """仪表板API测试"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return TestClient(app)

    @pytest.mark.asyncio
    async def test_get_dashboard(self, client):
        """测试获取仪表板数据"""
        response = client.get("/api/v1/dashboard/")

        assert response.status_code == 200
        data = response.json()
        assert "total_tasks" in data
        assert "total_reviewers" in data
        assert "pending_tasks" in data
        assert "completed_tasks" in data

    @pytest.mark.asyncio
    async def test_get_statistics(self, client):
        """测试获取统计数据"""
        response = client.get("/api/v1/dashboard/statistics")

        assert response.status_code == 200
        data = response.json()
        assert "review_stats" in data
        assert "reviewer_stats" in data

    @pytest.mark.asyncio
    async def test_get_real_time_metrics(self, client):
        """测试获取实时指标"""
        response = client.get("/api/v1/dashboard/metrics/real-time")

        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data
        assert "metrics" in data

class TestHealthCheck:
    """健康检查测试"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return TestClient(app)

    def test_health_check(self, client):
        """测试健康检查端点"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data

    def test_readiness_check(self, client):
        """测试就绪检查端点"""
        response = client.get("/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert "checks" in data
