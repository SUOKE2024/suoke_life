"""
API集成测试
API Integration Tests

测试所有API端点的功能和错误处理
"""

from uuid import uuid4

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

class TestReviewerAPI:
    """审核员API测试"""

    def test_create_reviewer(self, test_client):
        """测试创建审核员"""
        reviewer_data = {
            "reviewer_id": f"test_api_reviewer_{uuid4().hex[:8]}",
            "name": "API测试医生",
            "email": f"api_test_{uuid4().hex[:8]}@example.com",
            "specialties": ["中医诊断", "方剂学"],
            "experience_years": 5,
            "max_concurrent_tasks": 3,
        }

        response = test_client.post("/api/v1/reviewers/", json=reviewer_data)
        assert response.status_code == 201

        data = response.json()
        assert data["reviewer_id"] == reviewer_data["reviewer_id"]
        assert data["name"] == reviewer_data["name"]
        assert data["email"] == reviewer_data["email"]
        assert data["specialties"] == reviewer_data["specialties"]
        assert data["status"] == "active"

    def test_get_reviewer(self, test_client):
        """测试获取审核员"""
        # 先创建一个审核员
        reviewer_data = {
            "reviewer_id": f"test_get_reviewer_{uuid4().hex[:8]}",
            "name": "获取测试医生",
            "email": f"get_test_{uuid4().hex[:8]}@example.com",
            "specialties": ["中医诊断"],
            "max_concurrent_tasks": 5,
        }

        create_response = test_client.post("/api/v1/reviewers/", json=reviewer_data)
        assert create_response.status_code == 201

        # 获取审核员
        reviewer_id = reviewer_data["reviewer_id"]
        response = test_client.get(f"/api/v1/reviewers/{reviewer_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["reviewer_id"] == reviewer_id
        assert data["name"] == reviewer_data["name"]

    def test_list_reviewers(self, test_client):
        """测试列出审核员"""
        response = test_client.get("/api/v1/reviewers/")
        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert isinstance(data["items"], list)

    def test_update_reviewer(self, test_client):
        """测试更新审核员"""
        # 先创建一个审核员
        reviewer_data = {
            "reviewer_id": f"test_update_reviewer_{uuid4().hex[:8]}",
            "name": "更新测试医生",
            "email": f"update_test_{uuid4().hex[:8]}@example.com",
            "specialties": ["中医诊断"],
            "max_concurrent_tasks": 5,
        }

        create_response = test_client.post("/api/v1/reviewers/", json=reviewer_data)
        assert create_response.status_code == 201

        # 更新审核员
        reviewer_id = reviewer_data["reviewer_id"]
        update_data = {"name": "更新后的医生", "max_concurrent_tasks": 10}

        response = test_client.put(f"/api/v1/reviewers/{reviewer_id}", json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["max_concurrent_tasks"] == update_data["max_concurrent_tasks"]

    def test_reviewer_not_found(self, test_client):
        """测试审核员不存在的情况"""
        non_existent_id = f"non_existent_{uuid4().hex[:8]}"
        response = test_client.get(f"/api/v1/reviewers/{non_existent_id}")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data

    def test_create_reviewer_duplicate_id(self, test_client):
        """测试创建重复ID的审核员"""
        reviewer_data = {
            "reviewer_id": f"test_duplicate_{uuid4().hex[:8]}",
            "name": "重复测试医生",
            "email": f"duplicate_test_{uuid4().hex[:8]}@example.com",
            "specialties": ["中医诊断"],
            "max_concurrent_tasks": 5,
        }

        # 第一次创建
        response1 = test_client.post("/api/v1/reviewers/", json=reviewer_data)
        assert response1.status_code == 201

        # 第二次创建相同ID
        response2 = test_client.post("/api/v1/reviewers/", json=reviewer_data)
        assert response2.status_code == 400

        data = response2.json()
        assert "detail" in data

class TestReviewTaskAPI:
    """审核任务API测试"""

    def test_create_review_task(self, test_client):
        """测试创建审核任务"""
        task_data = {
            "review_type": "medical_diagnosis",
            "priority": "normal",
            "content": {
                "symptoms": ["头痛", "发热"],
                "diagnosis": "感冒",
                "treatment": "多休息，多喝水",
            },
            "user_id": "user_123",
            "agent_id": "xiaoai_agent",
            "estimated_duration": 1800,
        }

        response = test_client.post("/api/v1/tasks/", json=task_data)
        assert response.status_code == 201

        data = response.json()
        assert data["review_type"] == task_data["review_type"]
        assert data["priority"] == task_data["priority"]
        assert data["content"] == task_data["content"]
        assert data["user_id"] == task_data["user_id"]
        assert data["agent_id"] == task_data["agent_id"]
        assert data["status"] == "pending"

    def test_get_review_task(self, test_client):
        """测试获取审核任务"""
        # 先创建一个任务
        task_data = {
            "review_type": "medical_diagnosis",
            "priority": "normal",
            "content": {"test": "data"},
            "user_id": "user_get_123",
            "agent_id": "xiaoai_agent",
        }

        create_response = test_client.post("/api/v1/tasks/", json=task_data)
        assert create_response.status_code == 201

        task_id = create_response.json()["task_id"]

        # 获取任务
        response = test_client.get(f"/api/v1/tasks/{task_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["task_id"] == task_id
        assert data["review_type"] == task_data["review_type"]

    def test_list_review_tasks(self, test_client):
        """测试列出审核任务"""
        response = test_client.get("/api/v1/tasks/")
        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert isinstance(data["items"], list)

    def test_update_review_task(self, test_client):
        """测试更新审核任务"""
        # 先创建一个任务
        task_data = {
            "review_type": "medical_diagnosis",
            "priority": "normal",
            "content": {"test": "data"},
            "user_id": "user_update_123",
            "agent_id": "xiaoai_agent",
        }

        create_response = test_client.post("/api/v1/tasks/", json=task_data)
        assert create_response.status_code == 201

        task_id = create_response.json()["task_id"]

        # 更新任务
        update_data = {"status": "in_progress", "reviewer_notes": "开始审核"}

        response = test_client.put(f"/api/v1/tasks/{task_id}", json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == update_data["status"]
        assert data["reviewer_notes"] == update_data["reviewer_notes"]

    def test_assign_task(self, test_client):
        """测试分配任务"""
        # 先创建审核员
        reviewer_data = {
            "reviewer_id": f"test_assign_reviewer_{uuid4().hex[:8]}",
            "name": "分配测试医生",
            "email": f"assign_test_{uuid4().hex[:8]}@example.com",
            "specialties": ["中医诊断"],
            "max_concurrent_tasks": 5,
        }

        reviewer_response = test_client.post("/api/v1/reviewers/", json=reviewer_data)
        assert reviewer_response.status_code == 201

        # 创建任务
        task_data = {
            "review_type": "medical_diagnosis",
            "priority": "normal",
            "content": {"test": "data"},
            "user_id": "user_assign_123",
            "agent_id": "xiaoai_agent",
        }

        task_response = test_client.post("/api/v1/tasks/", json=task_data)
        assert task_response.status_code == 201

        task_id = task_response.json()["task_id"]
        reviewer_id = reviewer_data["reviewer_id"]

        # 分配任务
        response = test_client.post(f"/api/v1/tasks/{task_id}/assign/{reviewer_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["assigned_to"] == reviewer_id
        assert data["status"] == "assigned"

    def test_complete_task(self, test_client):
        """测试完成任务"""
        # 先创建审核员和任务，然后分配
        reviewer_data = {
            "reviewer_id": f"test_complete_reviewer_{uuid4().hex[:8]}",
            "name": "完成测试医生",
            "email": f"complete_test_{uuid4().hex[:8]}@example.com",
            "specialties": ["中医诊断"],
            "max_concurrent_tasks": 5,
        }

        reviewer_response = test_client.post("/api/v1/reviewers/", json=reviewer_data)
        assert reviewer_response.status_code == 201

        task_data = {
            "review_type": "medical_diagnosis",
            "priority": "normal",
            "content": {"test": "data"},
            "user_id": "user_complete_123",
            "agent_id": "xiaoai_agent",
        }

        task_response = test_client.post("/api/v1/tasks/", json=task_data)
        assert task_response.status_code == 201

        task_id = task_response.json()["task_id"]
        reviewer_id = reviewer_data["reviewer_id"]

        # 分配任务
        assign_response = test_client.post(
            f"/api/v1/tasks/{task_id}/assign/{reviewer_id}"
        )
        assert assign_response.status_code == 200

        # 完成任务
        decision_data = {
            "decision": "approved",
            "comments": "审核通过",
            "reviewer_notes": "内容符合要求",
        }

        response = test_client.post(
            f"/api/v1/tasks/{task_id}/complete", json=decision_data
        )
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "approved"
        assert data["review_comments"] == decision_data["comments"]

    def test_task_not_found(self, test_client):
        """测试任务不存在的情况"""
        non_existent_id = f"non_existent_{uuid4().hex[:8]}"
        response = test_client.get(f"/api/v1/tasks/{non_existent_id}")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data

class TestDashboardAPI:
    """仪表板API测试"""

    def test_get_dashboard_data(self, test_client):
        """测试获取仪表板数据"""
        response = test_client.get("/api/v1/dashboard/")
        assert response.status_code == 200

        data = response.json()
        assert "statistics" in data
        assert "pending_tasks" in data
        assert "active_reviewers" in data
        assert "recent_completions" in data

        # 检查统计数据结构
        stats = data["statistics"]
        assert "total_tasks" in stats
        assert "pending_tasks" in stats
        assert "completed_tasks" in stats
        assert "reviewer_count" in stats

    def test_get_statistics(self, test_client):
        """测试获取统计数据"""
        response = test_client.get("/api/v1/dashboard/statistics")
        assert response.status_code == 200

        data = response.json()
        assert "total_tasks" in data
        assert "pending_tasks" in data
        assert "in_progress_tasks" in data
        assert "completed_tasks" in data
        assert "reviewer_count" in data
        assert "active_reviewers" in data

    def test_get_real_time_metrics(self, test_client):
        """测试获取实时指标"""
        response = test_client.get("/api/v1/dashboard/metrics")
        assert response.status_code == 200

        data = response.json()
        assert "current_load" in data
        assert "active_tasks" in data
        assert "available_reviewers" in data
        assert "average_wait_time" in data

    def test_get_trends(self, test_client):
        """测试获取趋势数据"""
        response = test_client.get("/api/v1/dashboard/trends")
        assert response.status_code == 200

        data = response.json()
        assert "hourly_stats" in data
        assert "daily_stats" in data
        assert isinstance(data["hourly_stats"], list)
        assert isinstance(data["daily_stats"], list)

class TestErrorHandling:
    """错误处理测试"""

    def test_invalid_json(self, test_client):
        """测试无效JSON"""
        response = test_client.post(
            "/api/v1/reviewers/",
            data="invalid json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422

    def test_missing_required_fields(self, test_client):
        """测试缺少必需字段"""
        incomplete_data = {
            "name": "测试医生"
            # 缺少其他必需字段
        }

        response = test_client.post("/api/v1/reviewers/", json=incomplete_data)
        assert response.status_code == 422

        data = response.json()
        assert "detail" in data

    def test_invalid_enum_values(self, test_client):
        """测试无效枚举值"""
        task_data = {
            "review_type": "invalid_type",  # 无效的审核类型
            "priority": "normal",
            "content": {"test": "data"},
            "user_id": "user_123",
            "agent_id": "xiaoai_agent",
        }

        response = test_client.post("/api/v1/tasks/", json=task_data)
        assert response.status_code == 422

        data = response.json()
        assert "detail" in data

    def test_invalid_email_format(self, test_client):
        """测试无效邮箱格式"""
        reviewer_data = {
            "reviewer_id": f"test_invalid_email_{uuid4().hex[:8]}",
            "name": "测试医生",
            "email": "invalid-email-format",  # 无效邮箱格式
            "specialties": ["中医诊断"],
            "max_concurrent_tasks": 5,
        }

        response = test_client.post("/api/v1/reviewers/", json=reviewer_data)
        assert response.status_code == 422

        data = response.json()
        assert "detail" in data

class TestPagination:
    """分页测试"""

    def test_reviewer_pagination(self, test_client):
        """测试审核员分页"""
        # 测试默认分页
        response = test_client.get("/api/v1/reviewers/")
        assert response.status_code == 200

        data = response.json()
        assert data["page"] == 1
        assert data["size"] == 50  # 默认页面大小

        # 测试自定义分页
        response = test_client.get("/api/v1/reviewers/?page=2&size=10")
        assert response.status_code == 200

        data = response.json()
        assert data["page"] == 2
        assert data["size"] == 10

    def test_task_pagination(self, test_client):
        """测试任务分页"""
        # 测试默认分页
        response = test_client.get("/api/v1/tasks/")
        assert response.status_code == 200

        data = response.json()
        assert data["page"] == 1
        assert data["size"] == 50

        # 测试自定义分页
        response = test_client.get("/api/v1/tasks/?page=1&size=20")
        assert response.status_code == 200

        data = response.json()
        assert data["page"] == 1
        assert data["size"] == 20

class TestFiltering:
    """过滤测试"""

    def test_task_status_filter(self, test_client):
        """测试任务状态过滤"""
        response = test_client.get("/api/v1/tasks/?status=pending")
        assert response.status_code == 200

        data = response.json()
        # 验证返回的任务都是pending状态
        for task in data["items"]:
            assert task["status"] == "pending"

    def test_task_priority_filter(self, test_client):
        """测试任务优先级过滤"""
        response = test_client.get("/api/v1/tasks/?priority=high")
        assert response.status_code == 200

        data = response.json()
        # 验证返回的任务都是high优先级
        for task in data["items"]:
            assert task["priority"] == "high"

    def test_reviewer_status_filter(self, test_client):
        """测试审核员状态过滤"""
        response = test_client.get("/api/v1/reviewers/?status=active")
        assert response.status_code == 200

        data = response.json()
        # 验证返回的审核员都是active状态
        for reviewer in data["items"]:
            assert reviewer["status"] == "active"
