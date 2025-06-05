"""
HTTP API 测试模块

测试 FastAPI HTTP 接口
"""

from uuid import uuid4

from fastapi.testclient import TestClient

from corn_maze_service.internal.model.maze import MazeDifficulty, MazeTheme


class TestHealthAPI:
    """健康检查API测试"""

    def test_health_check(self, client: TestClient):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data

    def test_readiness_check(self, client: TestClient):
        """测试就绪检查端点"""
        response = client.get("/ready")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ready"
        assert "checks" in data


class TestMazeAPI:
    """迷宫API测试"""

    def test_create_maze(self, client: TestClient):
        """测试创建迷宫"""
        maze_data = {
            "name": "测试迷宫",
            "description": "用于测试的迷宫",
            "theme": MazeTheme.HEALTH.value,
            "difficulty": MazeDifficulty.EASY.value,
            "size": 5
        }

        response = client.post("/api/v1/mazes", json=maze_data)
        assert response.status_code == 201

        data = response.json()
        assert data["name"] == maze_data["name"]
        assert data["theme"] == maze_data["theme"]
        assert data["difficulty"] == maze_data["difficulty"]
        assert data["size"] == maze_data["size"]
        assert "id" in data
        assert "created_at" in data

    def test_create_maze_validation(self, client: TestClient):
        """测试创建迷宫的验证"""
        # 测试缺少必需字段
        response = client.post("/api/v1/mazes", json={})
        assert response.status_code == 422

        # 测试无效的主题
        invalid_data = {
            "name": "测试迷宫",
            "theme": "invalid_theme",
            "difficulty": MazeDifficulty.EASY.value,
            "size": 5
        }
        response = client.post("/api/v1/mazes", json=invalid_data)
        assert response.status_code == 400  # 我们的自定义验证返回400

        # 测试无效的大小
        invalid_size_data = {
            "name": "测试迷宫",
            "theme": MazeTheme.HEALTH.value,
            "difficulty": MazeDifficulty.EASY.value,
            "size": 1  # 太小
        }
        response = client.post("/api/v1/mazes", json=invalid_size_data)
        assert response.status_code == 422

    def test_get_maze(self, client: TestClient):
        """测试获取迷宫"""
        # 首先创建一个迷宫
        maze_data = {
            "name": "测试迷宫",
            "description": "用于测试的迷宫",
            "theme": MazeTheme.HEALTH.value,
            "difficulty": MazeDifficulty.EASY.value,
            "size": 5
        }

        create_response = client.post("/api/v1/mazes", json=maze_data)
        assert create_response.status_code == 201

        maze_id = create_response.json()["id"]

        # 获取迷宫
        response = client.get(f"/api/v1/mazes/{maze_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == maze_id
        assert data["name"] == maze_data["name"]

    def test_get_maze_not_found(self, client: TestClient):
        """测试获取不存在的迷宫"""
        fake_id = str(uuid4())
        response = client.get(f"/api/v1/mazes/{fake_id}")
        assert response.status_code == 404

    def test_list_mazes(self, client: TestClient):
        """测试列出迷宫"""
        response = client.get("/api/v1/mazes")
        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert isinstance(data["items"], list)

    def test_list_mazes_with_filters(self, client: TestClient):
        """测试带过滤器的迷宫列表"""
        # 测试主题过滤
        response = client.get(f"/api/v1/mazes?theme={MazeTheme.HEALTH.value}")
        assert response.status_code == 200

        # 测试难度过滤
        response = client.get(f"/api/v1/mazes?difficulty={MazeDifficulty.EASY.value}")
        assert response.status_code == 200

        # 测试分页
        response = client.get("/api/v1/mazes?page=1&size=10")
        assert response.status_code == 200

        data = response.json()
        assert data["page"] == 1
        assert data["size"] == 10

    def test_update_maze(self, client: TestClient):
        """测试更新迷宫"""
        # 首先创建一个迷宫
        maze_data = {
            "name": "测试迷宫",
            "description": "用于测试的迷宫",
            "theme": MazeTheme.HEALTH.value,
            "difficulty": MazeDifficulty.EASY.value,
            "size": 5
        }

        create_response = client.post("/api/v1/mazes", json=maze_data)
        maze_id = create_response.json()["id"]

        # 更新迷宫
        update_data = {
            "name": "更新后的迷宫",
            "description": "更新后的描述",
            "difficulty": MazeDifficulty.NORMAL.value
        }

        response = client.put(f"/api/v1/mazes/{maze_id}", json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert data["difficulty"] == update_data["difficulty"]

    def test_delete_maze(self, client: TestClient):
        """测试删除迷宫"""
        # 首先创建一个迷宫
        maze_data = {
            "name": "测试迷宫",
            "description": "用于测试的迷宫",
            "theme": MazeTheme.HEALTH.value,
            "difficulty": MazeDifficulty.EASY.value,
            "size": 5
        }

        create_response = client.post("/api/v1/mazes", json=maze_data)
        maze_id = create_response.json()["id"]

        # 删除迷宫
        response = client.delete(f"/api/v1/mazes/{maze_id}")
        assert response.status_code == 204

        # 验证迷宫已被删除
        get_response = client.get(f"/api/v1/mazes/{maze_id}")
        assert get_response.status_code == 404


class TestProgressAPI:
    """进度API测试"""

    def test_start_maze(self, client: TestClient):
        """测试开始迷宫"""
        # 首先创建一个迷宫
        maze_data = {
            "name": "测试迷宫",
            "description": "用于测试的迷宫",
            "theme": MazeTheme.HEALTH.value,
            "difficulty": MazeDifficulty.EASY.value,
            "size": 5
        }

        create_response = client.post("/api/v1/mazes", json=maze_data)
        maze_id = create_response.json()["id"]

        # 开始迷宫
        user_id = str(uuid4())
        response = client.post(f"/api/v1/mazes/{maze_id}/start", json={"user_id": user_id})
        assert response.status_code == 201

        data = response.json()
        assert data["user_id"] == user_id
        assert data["maze_id"] == maze_id
        assert data["status"] == "in_progress"
        assert "current_position" in data

    def test_move_in_maze(self, client: TestClient):
        """测试在迷宫中移动"""
        # 创建迷宫并开始
        maze_data = {
            "name": "测试迷宫",
            "description": "用于测试的迷宫",
            "theme": MazeTheme.HEALTH.value,
            "difficulty": MazeDifficulty.EASY.value,
            "size": 5
        }

        create_response = client.post("/api/v1/mazes", json=maze_data)
        maze_id = create_response.json()["id"]

        user_id = str(uuid4())
        start_response = client.post(f"/api/v1/mazes/{maze_id}/start", json={"user_id": user_id})
        assert start_response.status_code == 201

        # 移动
        move_data = {
            "user_id": user_id,
            "direction": "right"
        }

        response = client.post(f"/api/v1/mazes/{maze_id}/move", json=move_data)
        assert response.status_code == 200

        data = response.json()
        assert "current_position" in data
        assert "valid_move" in data

    def test_get_progress(self, client: TestClient):
        """测试获取进度"""
        # 创建迷宫并开始
        maze_data = {
            "name": "测试迷宫",
            "description": "用于测试的迷宫",
            "theme": MazeTheme.HEALTH.value,
            "difficulty": MazeDifficulty.EASY.value,
            "size": 5
        }

        create_response = client.post("/api/v1/mazes", json=maze_data)
        maze_id = create_response.json()["id"]

        user_id = str(uuid4())
        start_response = client.post(f"/api/v1/mazes/{maze_id}/start", json={"user_id": user_id})
        assert start_response.status_code == 201

        # 获取进度
        response = client.get(f"/api/v1/mazes/{maze_id}/progress/{user_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["user_id"] == user_id
        assert data["maze_id"] == maze_id
        assert "current_position" in data
        assert "visited_nodes" in data
        assert "score" in data


class TestErrorHandling:
    """错误处理测试"""

    def test_404_error(self, client: TestClient):
        """测试404错误"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404

    def test_method_not_allowed(self, client: TestClient):
        """测试方法不允许错误"""
        response = client.patch("/api/v1/mazes")
        assert response.status_code == 405

    def test_validation_error(self, client: TestClient):
        """测试验证错误"""
        response = client.post("/api/v1/mazes", json={"invalid": "data"})
        assert response.status_code == 422

        data = response.json()
        assert "detail" in data
