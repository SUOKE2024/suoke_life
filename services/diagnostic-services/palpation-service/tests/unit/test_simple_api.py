"""
简化版API测试
测试基本的API端点功能
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from palpation_service.simple_main import create_app
from palpation_service.models import SessionType, SensorType, AnalysisType


@pytest.fixture
def client():
    """测试客户端"""
    app = create_app()
    return TestClient(app)


class TestHealthEndpoints:
    """健康检查端点测试"""
    
    def test_health_check(self, client):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "服务运行正常"
        assert "data" in data
        assert data["data"]["service"] == "palpation-service"
        assert data["data"]["status"] == "healthy"
    
    def test_metrics_endpoint(self, client):
        """测试指标端点"""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]


class TestSessionManagement:
    """会话管理测试"""
    
    def test_create_session(self, client):
        """测试创建会话"""
        session_data = {
            "user_id": "test_user_123",
            "session_type": SessionType.STANDARD,
            "metadata": {"test": True}
        }
        
        response = client.post("/palpation/sessions", json=session_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["user_id"] == "test_user_123"
        assert data["session_type"] == SessionType.STANDARD
        assert data["status"] == "active"
        assert "id" in data
        
        return data["id"]  # 返回会话ID供其他测试使用
    
    def test_get_session(self, client):
        """测试获取会话"""
        # 先创建一个会话
        session_id = self.test_create_session(client)
        
        # 获取会话信息
        response = client.get(f"/palpation/sessions/{session_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == session_id
        assert data["user_id"] == "test_user_123"
    
    def test_get_nonexistent_session(self, client):
        """测试获取不存在的会话"""
        response = client.get("/palpation/sessions/nonexistent-id")
        assert response.status_code == 404
        assert "会话不存在" in response.json()["detail"]


class TestSensorData:
    """传感器数据测试"""
    
    def test_upload_sensor_data(self, client):
        """测试上传传感器数据"""
        # 先创建一个会话
        session_data = {
            "user_id": "test_user_456",
            "session_type": SessionType.STANDARD
        }
        session_response = client.post("/palpation/sessions", json=session_data)
        session_id = session_response.json()["id"]
        
        # 上传传感器数据
        sensor_data = {
            "sensor_type": SensorType.PRESSURE,
            "data_points": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "value": 120.5,
                    "unit": "mmHg",
                    "metadata": {}
                },
                {
                    "timestamp": datetime.now().isoformat(),
                    "value": 118.2,
                    "unit": "mmHg",
                    "metadata": {}
                }
            ],
            "quality_indicators": {"snr": 0.95}
        }
        
        response = client.post(f"/palpation/sessions/{session_id}/data", json=sensor_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "数据上传成功"
        assert data["data"]["session_id"] == session_id
        assert data["data"]["sensor_type"] == SensorType.PRESSURE
        assert data["data"]["data_points_count"] == 2
    
    def test_upload_data_to_nonexistent_session(self, client):
        """测试向不存在的会话上传数据"""
        sensor_data = {
            "sensor_type": SensorType.TEMPERATURE,
            "data_points": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "value": 36.5,
                    "unit": "celsius",
                    "metadata": {}
                }
            ]
        }
        
        response = client.post("/palpation/sessions/nonexistent-id/data", json=sensor_data)
        assert response.status_code == 404


class TestAnalysis:
    """分析功能测试"""
    
    def test_analyze_session(self, client):
        """测试会话分析"""
        # 创建会话并上传数据
        session_data = {
            "user_id": "test_user_789",
            "session_type": SessionType.DETAILED
        }
        session_response = client.post("/palpation/sessions", json=session_data)
        session_id = session_response.json()["id"]
        
        # 上传一些传感器数据
        sensor_data = {
            "sensor_type": SensorType.PRESSURE,
            "data_points": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "value": 125.0,
                    "unit": "mmHg",
                    "metadata": {}
                }
            ]
        }
        client.post(f"/palpation/sessions/{session_id}/data", json=sensor_data)
        
        # 请求分析
        analysis_request = {
            "session_id": session_id,
            "analysis_types": [AnalysisType.PRESSURE_ANALYSIS, AnalysisType.HEALTH_ASSESSMENT],
            "parameters": {}
        }
        
        response = client.post(f"/palpation/sessions/{session_id}/analyze", json=analysis_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "分析完成"
        assert "data" in data
        
        analysis_result = data["data"]
        assert analysis_result["session_id"] == session_id
        assert "overall_health_score" in analysis_result["results"]
        assert "recommendations" in analysis_result
        assert len(analysis_result["recommendations"]) > 0


class TestConfiguration:
    """配置端点测试"""
    
    def test_get_config(self, client):
        """测试获取配置"""
        response = client.get("/config")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "配置信息"
        assert "service" in data["data"]
        assert "fusion" in data["data"]
        
        service_config = data["data"]["service"]
        assert service_config["name"] == "palpation-service"
        assert service_config["version"] == "1.0.0"
    
    def test_get_stats(self, client):
        """测试获取统计信息"""
        response = client.get("/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "统计信息"
        assert "total_sessions" in data["data"]
        assert "active_sessions" in data["data"]
        assert "total_sensor_data" in data["data"]


class TestIntegration:
    """集成测试"""
    
    def test_complete_workflow(self, client):
        """测试完整的工作流程"""
        # 1. 创建会话
        session_data = {
            "user_id": "integration_test_user",
            "session_type": SessionType.STANDARD,
            "metadata": {"test_type": "integration"}
        }
        session_response = client.post("/palpation/sessions", json=session_data)
        assert session_response.status_code == 200
        session_id = session_response.json()["id"]
        
        # 2. 上传多种类型的传感器数据
        sensor_types = [SensorType.PRESSURE, SensorType.TEMPERATURE, SensorType.TEXTURE]
        
        for sensor_type in sensor_types:
            sensor_data = {
                "sensor_type": sensor_type,
                "data_points": [
                    {
                        "timestamp": datetime.now().isoformat(),
                        "value": 100.0 + hash(sensor_type) % 50,
                        "unit": "unit",
                        "metadata": {"sensor": sensor_type}
                    }
                ],
                "quality_indicators": {"snr": 0.9}
            }
            
            response = client.post(f"/palpation/sessions/{session_id}/data", json=sensor_data)
            assert response.status_code == 200
        
        # 3. 执行分析
        analysis_request = {
            "session_id": session_id,
            "analysis_types": [AnalysisType.MULTIMODAL_FUSION],
            "parameters": {"include_recommendations": True}
        }
        
        analysis_response = client.post(f"/palpation/sessions/{session_id}/analyze", json=analysis_request)
        assert analysis_response.status_code == 200
        
        # 4. 验证分析结果
        analysis_data = analysis_response.json()["data"]
        assert analysis_data["session_id"] == session_id
        assert "overall_health_score" in analysis_data["results"]
        assert len(analysis_data["recommendations"]) > 0
        
        # 5. 检查统计信息
        stats_response = client.get("/stats")
        stats_data = stats_response.json()["data"]
        assert stats_data["total_sessions"] >= 1
        assert stats_data["total_sensor_data"] >= 3 