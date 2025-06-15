"""
小克智能体API测试

测试小克智能体的核心功能和API端点。
"""

import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from fastapi.testclient import TestClient

# 导入通用测试基类
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent / "tests"))
from common.test_base import AgentTestCase


class TestXiaokeAgentAPI(AgentTestCase):
    """小克智能体API测试类"""

    def get_app(self):
        """获取FastAPI应用实例"""
        # 这里需要导入实际的app实例
        # from xiaoke_service.main import app
        # return app
        # 暂时返回None，实际实现时需要导入真实的app
        return None

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """测试健康检查端点"""
        if client is None:
            pytest.skip("App not available for testing")
        
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_chat_endpoint(self, client):
        """测试聊天端点"""
        if client is None:
            pytest.skip("App not available for testing")
            
        response = client.post(
            "/api/v1/agent/chat",
            json={
                "message": "你好，我想了解健康管理建议",
                "user_id": "test-user-123",
                "session_id": "test-session-456"
            }
        )
        assert response.status_code == 200
        await self.assert_chat_response(response)

    @pytest.mark.asyncio
    async def test_capabilities_endpoint(self, client):
        """测试能力查询端点"""
        if client is None:
            pytest.skip("App not available for testing")
            
        response = client.get("/api/v1/agent/capabilities")
        assert response.status_code == 200
        data = response.json()
        assert "capabilities" in data
        assert isinstance(data["capabilities"], list)

    @pytest.mark.asyncio
    async def test_health_analysis(self, client):
        """测试健康分析功能"""
        if client is None:
            pytest.skip("App not available for testing")
            
        response = client.post(
            "/api/v1/health/analyze",
            json={
                "user_id": "test-user-123",
                "health_data": {
                    "symptoms": ["头痛", "失眠"],
                    "vital_signs": {
                        "heart_rate": 75,
                        "blood_pressure": "120/80",
                        "temperature": 36.5
                    }
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "analysis" in data
        assert "recommendations" in data

    @pytest.mark.asyncio
    async def test_knowledge_query(self, client):
        """测试知识查询功能"""
        if client is None:
            pytest.skip("App not available for testing")
            
        response = client.post(
            "/api/v1/knowledge/query",
            json={
                "query": "什么是阳虚体质？",
                "category": "tcm_constitution"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data

    @pytest.mark.asyncio
    async def test_error_handling(self, client):
        """测试错误处理"""
        if client is None:
            pytest.skip("App not available for testing")
            
        # 测试无效请求
        response = client.post(
            "/api/v1/agent/chat",
            json={"invalid": "data"}
        )
        assert response.status_code == 422  # 验证错误

    @pytest.mark.asyncio
    async def test_authentication_required(self, client):
        """测试需要认证的端点"""
        if client is None:
            pytest.skip("App not available for testing")
            
        # 测试没有认证token的请求
        response = client.post(
            "/api/v1/agent/private-chat",
            json={
                "message": "私密健康咨询",
                "user_id": "test-user-123"
            }
        )
        # 应该返回401未认证错误
        assert response.status_code in [401, 403]


class TestXiaokeAgentService:
    """小克智能体服务层测试"""

    @pytest.fixture
    def mock_knowledge_base(self):
        """模拟知识库"""
        kb = AsyncMock()
        kb.search.return_value = [
            {"content": "阳虚体质的特征...", "score": 0.9},
            {"content": "阳虚体质的调理方法...", "score": 0.8}
        ]
        return kb

    @pytest.fixture
    def mock_health_analyzer(self):
        """模拟健康分析器"""
        analyzer = AsyncMock()
        analyzer.analyze.return_value = {
            "constitution": "阳虚体质",
            "health_score": 75,
            "risk_factors": ["睡眠不足", "运动不足"],
            "recommendations": ["早睡早起", "适量运动"]
        }
        return analyzer

    @pytest.mark.asyncio
    async def test_health_analysis_service(self, mock_health_analyzer):
        """测试健康分析服务"""
        # 这里应该测试实际的服务类
        # 暂时跳过，等待实际服务实现
        pass

    @pytest.mark.asyncio
    async def test_knowledge_retrieval_service(self, mock_knowledge_base):
        """测试知识检索服务"""
        # 这里应该测试实际的知识检索服务
        # 暂时跳过，等待实际服务实现
        pass


class TestXiaokeAgentIntegration:
    """小克智能体集成测试"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_full_consultation_flow(self):
        """测试完整的咨询流程"""
        # 这里应该测试从用户输入到最终响应的完整流程
        # 包括：输入处理 -> 知识检索 -> AI推理 -> 响应生成
        pass

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_multi_agent_collaboration(self):
        """测试多智能体协作"""
        # 测试小克与其他智能体（索儿、老克、小艾）的协作
        pass 