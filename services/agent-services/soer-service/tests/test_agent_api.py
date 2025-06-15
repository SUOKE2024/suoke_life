"""
索儿智能体API测试

测试智能体的核心功能和API端点。
"""

import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from fastapi.testclient import TestClient

from soer_service.main import app


class TestSoerAgentAPI:
    """索儿智能体API测试类"""

    @pytest.fixture
    def client(self):
        """测试客户端"""
        return TestClient(app)

    @pytest.mark.asyncio
    async def test_chat_endpoint(self, client):
        """测试聊天端点"""
        response = client.post(
            "/api/v1/agent/chat",
            json={
                "message": "你好，我想了解健康饮食建议",
                "user_id": "test-user-123",
                "session_id": "test-session-456"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "session_id" in data

    @pytest.mark.asyncio
    async def test_capabilities_endpoint(self, client):
        """测试能力查询端点"""
        response = client.get("/api/v1/agent/capabilities")
        assert response.status_code == 200
        data = response.json()
        assert "capabilities" in data
        assert isinstance(data["capabilities"], list)

    @pytest.mark.asyncio
    async def test_nutrition_analysis(self, client):
        """测试营养分析功能"""
        response = client.post(
            "/api/v1/nutrition/analyze",
            json={
                "user_id": "test-user-123",
                "food_items": [
                    {"name": "苹果", "quantity": 1, "unit": "个"},
                    {"name": "米饭", "quantity": 100, "unit": "克"}
                ]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "nutrition_analysis" in data
        assert "recommendations" in data

    @pytest.mark.asyncio
    async def test_health_data_processing(self, client):
        """测试健康数据处理"""
        response = client.post(
            "/api/v1/health/data",
            json={
                "user_id": "test-user-123",
                "data_type": "heart_rate",
                "values": [72, 75, 78, 80, 76],
                "timestamps": [
                    "2024-01-01T10:00:00Z",
                    "2024-01-01T10:01:00Z",
                    "2024-01-01T10:02:00Z",
                    "2024-01-01T10:03:00Z",
                    "2024-01-01T10:04:00Z"
                ]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"

    @pytest.mark.asyncio
    async def test_tcm_consultation(self, client):
        """测试中医咨询功能"""
        response = client.post(
            "/api/v1/tcm/consultation",
            json={
                "user_id": "test-user-123",
                "symptoms": ["头痛", "失眠", "食欲不振"],
                "constitution": "阳虚体质"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert "tcm_analysis" in data

    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """测试WebSocket连接"""
        # 这里需要实际的WebSocket测试实现
        # 暂时跳过，需要更复杂的测试设置
        pass

    @pytest.mark.asyncio
    async def test_error_handling(self, client):
        """测试错误处理"""
        # 测试无效请求
        response = client.post(
            "/api/v1/agent/chat",
            json={"invalid": "data"}
        )
        assert response.status_code == 422  # 验证错误

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy" 