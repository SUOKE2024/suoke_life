"""
HTTP API 测试
"""

from fastapi.testclient import TestClient


class TestHealthAPI:
    """健康检查 API 测试"""

    def test_health_check(self, client: TestClient):
        """测试健康检查端点"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data

    def test_root_endpoint(self, client: TestClient):
        """测试根端点"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert data["message"] == "Corn Maze Service API"


class TestMazeAPI:
    """迷宫 API 测试"""

    def test_create_maze(self, client: TestClient):
        """测试创建迷宫"""
        maze_data = {
            "name": "Test Maze",
            "description": "A test maze",
            "size": 10,
            "theme": "health",
            "difficulty": "normal",
            "is_public": False
        }

        response = client.post("/api/v1/mazes", json=maze_data)

        assert response.status_code == 201
        data = response.json()

        assert data["name"] == maze_data["name"]
        assert data["description"] == maze_data["description"]
        assert data["size"] == maze_data["size"]
        assert data["theme"] == maze_data["theme"]
        assert data["difficulty"] == maze_data["difficulty"]
        assert data["is_public"] == maze_data["is_public"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_maze_validation(self, client: TestClient):
        """测试创建迷宫验证"""
        # 测试无效数据
        invalid_data = {
            "name": "",  # 空名称
            "size": 200,  # 超出最大大小
        }

        response = client.post("/api/v1/mazes", json=invalid_data)
        assert response.status_code == 422

    def test_list_mazes(self, client: TestClient):
        """测试获取迷宫列表"""
        response = client.get("/api/v1/mazes")

        assert response.status_code == 200
        data = response.json()

        assert "mazes" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert data["page"] == 1
        assert data["size"] == 10

    def test_list_mazes_with_filters(self, client: TestClient):
        """测试带过滤器的迷宫列表"""
        response = client.get("/api/v1/mazes?page=2&size=5&theme=health&difficulty=easy")

        assert response.status_code == 200
        data = response.json()

        assert data["page"] == 2
        assert data["size"] == 5

    def test_get_maze_not_found(self, client: TestClient):
        """测试获取不存在的迷宫"""
        response = client.get("/api/v1/mazes/nonexistent-id")

        assert response.status_code == 404
        data = response.json()

        assert data["error"] == "HTTP_ERROR"
        assert "not found" in data["message"]

    def test_delete_maze_not_found(self, client: TestClient):
        """测试删除不存在的迷宫"""
        response = client.delete("/api/v1/mazes/nonexistent-id")

        assert response.status_code == 404
        data = response.json()

        assert data["error"] == "HTTP_ERROR"
        assert "not found" in data["message"]


class TestErrorHandling:
    """错误处理测试"""

    def test_404_error(self, client: TestClient):
        """测试 404 错误"""
        response = client.get("/nonexistent-endpoint")

        assert response.status_code == 404

    def test_method_not_allowed(self, client: TestClient):
        """测试方法不允许错误"""
        response = client.patch("/health")

        assert response.status_code == 405
