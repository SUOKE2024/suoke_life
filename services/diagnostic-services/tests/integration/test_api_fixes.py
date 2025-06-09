"""
API集成测试修复
"""

import pytest
import httpx
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

class TestAPIIntegration:
    """API集成测试修复"""
    
    def setup_method(self):
        """测试设置"""
        self.client = TestClient(app)
        self.base_url = "http://testserver"
    
    @pytest.mark.asyncio
    async def test_api_health_endpoint(self):
        """测试API健康检查端点"""
        response = self.client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_api_diagnosis_endpoint(self):
        """测试诊断API端点"""
        test_data = {
            "symptoms": ["头痛", "发热"],
            "patient_info": {
                "age": 30,
                "gender": "male"
            }
        }
        
        response = self.client.post("/api/v1/diagnosis", json=test_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "diagnosis" in result
        assert "confidence" in result
        assert result["confidence"] > 0.5
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self):
        """测试API错误处理"""
        # 测试无效数据
        invalid_data = {"invalid": "data"}
        response = self.client.post("/api/v1/diagnosis", json=invalid_data)
        assert response.status_code == 422
        
        # 测试空数据
        response = self.client.post("/api/v1/diagnosis", json={})
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_api_performance(self):
        """测试API性能"""
        import time
        
        test_data = {
            "symptoms": ["咳嗽", "胸闷"],
            "patient_info": {"age": 25, "gender": "female"}
        }
        
        start_time = time.time()
        response = self.client.post("/api/v1/diagnosis", json=test_data)
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 2.0  # 响应时间小于2秒
