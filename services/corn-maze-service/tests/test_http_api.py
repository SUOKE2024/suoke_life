"""
HTTP API 测试模块

测试 FastAPI HTTP 接口
"""

from fastapi.testclient import TestClient

from corn_maze_service.constants import (
    DEFAULT_PAGE,
    DEFAULT_PAGE_SIZE,
    HTTP_CREATED,
    HTTP_METHOD_NOT_ALLOWED,
    HTTP_NOT_FOUND,
    HTTP_OK,
    HTTP_UNPROCESSABLE_ENTITY,
    TEST_PAGE_NUMBER,
    TEST_PAGE_SIZE,
)


class TestHealthAPI:
    """健康检查 API 测试"""

    def test_health_check(self, client: TestClient):
        """测试健康检查端点"""
        response = client.get("/health")

        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data


class TestRootAPI:
    """根 API 测试"""

    def test_root_endpoint(self, client: TestClient):
        """测试根端点"""
        response = client.get("/")

        assert response.status_code == HTTP_OK
        data = response.json()
        assert data["service"] == "Corn Maze Service"
        assert "version" in data
        assert "status" in data


class TestMazeAPI:
    """迷宫 API 测试"""

    def test_create_maze(self, client: TestClient):
        """测试创建迷宫"""
        maze_data = {
            "name": "测试迷宫",
            "description": "这是一个测试迷宫",
            "theme": "health",
            "difficulty": "easy",
            "size_x": 5,
            "size_y": 5
        }

        response = client.post("/api/v1/mazes", json=maze_data)

        assert response.status_code == HTTP_CREATED
        data = response.json()
        assert data["name"] == maze_data["name"]
        assert data["theme"] == maze_data["theme"]
        assert data["difficulty"] == maze_data["difficulty"]
        assert "id" in data
        assert "created_at" in data

    def test_create_maze_validation_error(self, client: TestClient):
        """测试创建迷宫验证错误"""
        invalid_data = {
            "name": "",  # 空名称应该失败
            "theme": "invalid_theme",
            "difficulty": "invalid_difficulty"
        }

        response = client.post("/api/v1/mazes", json=invalid_data)
        assert response.status_code == HTTP_UNPROCESSABLE_ENTITY

    def test_list_mazes(self, client: TestClient):
        """测试列出迷宫"""
        response = client.get("/api/v1/mazes")

        assert response.status_code == HTTP_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert data["page"] == DEFAULT_PAGE
        assert data["size"] == DEFAULT_PAGE_SIZE

    def test_list_mazes_with_filters(self, client: TestClient):
        """测试带过滤器的迷宫列表"""
        response = client.get(f"/api/v1/mazes?page={TEST_PAGE_NUMBER}&size={TEST_PAGE_SIZE}&theme=health&difficulty=easy")

        assert response.status_code == HTTP_OK
        data = response.json()

        assert data["page"] == TEST_PAGE_NUMBER
        assert data["size"] == TEST_PAGE_SIZE

    def test_get_maze_not_found(self, client: TestClient):
        """测试获取不存在的迷宫"""
        response = client.get("/api/v1/mazes/nonexistent-id")

        assert response.status_code == HTTP_NOT_FOUND
        data = response.json()
        assert "detail" in data

    def test_delete_maze_not_found(self, client: TestClient):
        """测试删除不存在的迷宫"""
        response = client.delete("/api/v1/mazes/nonexistent-id")

        assert response.status_code == HTTP_NOT_FOUND
        data = response.json()
        assert "detail" in data


class TestErrorHandling:
    """错误处理测试"""

    def test_404_not_found(self, client: TestClient):
        """测试 404 错误"""
        response = client.get("/nonexistent-endpoint")

        assert response.status_code == HTTP_NOT_FOUND

    def test_method_not_allowed(self, client: TestClient):
        """测试方法不允许错误"""
        response = client.patch("/health")

        assert response.status_code == HTTP_METHOD_NOT_ALLOWED
