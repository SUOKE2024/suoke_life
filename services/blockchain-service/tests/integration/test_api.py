"""
API集成测试
"""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from blockchain_service.api.main import create_app


@pytest.fixture
def test_client():
    """测试客户端"""
    app = create_app()
    return TestClient(app)


class TestHealthEndpoints:
    """健康检查端点测试"""
    
    def test_health_check(self, test_client):
        """测试基础健康检查"""
        response = test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
    
    def test_readiness_check(self, test_client):
        """测试就绪状态检查"""
        response = test_client.get("/health/ready")
        
        # 检查响应状态码（可能是200或503）
        assert response.status_code in [200, 503]
        data = response.json()
        
        # 如果是503错误，响应在detail字段中
        if response.status_code == 503:
            assert "detail" in data
            detail = data["detail"]
            assert "status" in detail
            assert "components" in detail
        else:
            # 如果是200，直接检查字段
            assert "status" in data
            assert "components" in data
    
    def test_liveness_check(self, test_client):
        """测试存活状态检查"""
        response = test_client.get("/health/live")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"


class TestBlockchainEndpoints:
    """区块链端点测试"""
    
    def test_store_health_data_success(self, test_client):
        """测试成功存储健康数据"""
        health_data = {
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "data_type": "vital_signs",
            "data_content": {
                "heart_rate": 72,
                "blood_pressure": "120/80",
                "temperature": 36.5
            },
            "metadata": {
                "device": "smart_watch",
                "location": "home"
            }
        }
        
        with patch('blockchain_service.api.blockchain.get_blockchain_client') as mock_client:
            mock_client.return_value = AsyncMock()
            
            response = test_client.post("/api/v1/blockchain/store-health-data", json=health_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "transaction_hash" in data
            assert "block_number" in data
    
    def test_store_health_data_validation_error(self, test_client):
        """测试存储无效健康数据"""
        invalid_data = {"invalid": "data"}
        
        response = test_client.post("/api/v1/blockchain/store-health-data", json=invalid_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_get_transaction_status_success(self, test_client):
        """测试成功获取交易状态"""
        tx_hash = "0x1234567890abcdef"
        
        with patch('blockchain_service.api.blockchain.get_blockchain_client') as mock_client:
            mock_client.return_value = AsyncMock()
            
            response = test_client.get(f"/api/v1/blockchain/transaction/{tx_hash}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["transaction_hash"] == tx_hash
            assert "status" in data
    
    def test_get_contracts_info_success(self, test_client):
        """测试成功获取合约信息"""
        with patch('blockchain_service.api.blockchain.get_blockchain_client') as mock_client:
            mock_blockchain_client = AsyncMock()
            mock_blockchain_client.contracts = {
                "health_storage": AsyncMock(
                    name="HealthDataStorage",
                    address="0x1234567890abcdef",
                    abi=[{"name": "storeData", "type": "function"}]
                )
            }
            mock_client.return_value = mock_blockchain_client
            
            response = test_client.get("/api/v1/blockchain/contracts")
            
            assert response.status_code == 200
            data = response.json()
            assert "contracts" in data
            assert isinstance(data["contracts"], list)


class TestRootEndpoint:
    """根端点测试"""
    
    def test_root_endpoint(self, test_client):
        """测试根端点"""
        response = test_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"


class TestErrorHandling:
    """错误处理测试"""
    
    def test_404_error(self, test_client):
        """测试404错误"""
        response = test_client.get("/nonexistent")
        
        assert response.status_code == 404
    
    def test_method_not_allowed(self, test_client):
        """测试方法不允许错误"""
        response = test_client.post("/health")
        
        assert response.status_code == 405
    
    def test_blockchain_service_unavailable(self, test_client):
        """测试区块链服务不可用"""
        health_data = {
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "data_type": "vital_signs",
            "data_content": {"heart_rate": 72}
        }
        
        with patch('blockchain_service.api.blockchain.get_blockchain_client') as mock_client:
            mock_client.side_effect = Exception("Service unavailable")
            
            response = test_client.post("/api/v1/blockchain/store-health-data", json=health_data)
            
            assert response.status_code == 503