"""
健康数据服务单元测试
"""

import pytest
from uuid import UUID, uuid4
from unittest.mock import AsyncMock, patch

from blockchain_service.services.health_data_service import HealthDataService
from blockchain_service.core.exceptions import ValidationError, StorageError


class TestHealthDataService:
    """健康数据服务测试"""
    
    @pytest.mark.asyncio
    async def test_store_health_data_success(self, health_data_service):
        """测试成功存储健康数据"""
        user_id = uuid4()
        data_type = "vital_signs"
        data_content = {
            "heart_rate": 72,
            "blood_pressure": "120/80",
            "temperature": 36.5
        }
        metadata = {
            "device": "smart_watch",
            "location": "home"
        }
        
        result = await health_data_service.store_health_data(
            user_id, data_type, data_content, metadata
        )
        
        assert result["success"] is True
        assert "data_id" in result
        assert "transaction_hash" in result
        assert "block_number" in result
    
    @pytest.mark.asyncio
    async def test_store_health_data_empty_content(self, health_data_service):
        """测试存储空数据内容"""
        user_id = uuid4()
        data_type = "vital_signs"
        data_content = {}
        
        with pytest.raises(StorageError, match="存储健康数据失败"):
            await health_data_service.store_health_data(
                user_id, data_type, data_content
            )
    
    @pytest.mark.asyncio
    async def test_get_health_data_success(self, health_data_service):
        """测试成功获取健康数据"""
        user_id = uuid4()
        
        result = await health_data_service.get_health_data(user_id)
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert "data_id" in result[0]
        assert "user_id" in result[0]
        assert "data_type" in result[0]
        assert "data_content" in result[0]
    
    @pytest.mark.asyncio
    async def test_get_health_data_with_data_id(self, health_data_service):
        """测试使用数据ID获取健康数据"""
        user_id = uuid4()
        data_id = "specific_data_id"
        
        result = await health_data_service.get_health_data(user_id, data_id)
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0]["data_id"] == data_id
    
    @pytest.mark.asyncio
    async def test_verify_data_integrity_success(self, health_data_service):
        """测试成功验证数据完整性"""
        data_id = "test_data_id"
        blockchain_hash = "0x1234567890abcdef"
        
        result = await health_data_service.verify_data_integrity(
            data_id, blockchain_hash
        )
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_verify_data_integrity_with_exception(self, health_data_service):
        """测试验证数据完整性时发生异常"""
        data_id = "test_data_id"
        blockchain_hash = "invalid_hash"
        
        # 模拟异常情况
        with patch.object(health_data_service.logger, 'info', side_effect=Exception("Test error")):
            result = await health_data_service.verify_data_integrity(
                data_id, blockchain_hash
            )
            
            assert result is False
    
    def test_health_data_service_initialization(self):
        """测试健康数据服务初始化"""
        service = HealthDataService()
        
        assert service.logger is not None
        assert hasattr(service, 'store_health_data')
        assert hasattr(service, 'get_health_data')
        assert hasattr(service, 'verify_data_integrity')