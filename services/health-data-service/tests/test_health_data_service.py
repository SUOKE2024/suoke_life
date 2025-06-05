"""健康数据服务测试"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from health_data_service.core.exceptions import DatabaseError, NotFoundError, ValidationError
from health_data_service.models import (
    CreateHealthDataRequest,
    CreateVitalSignsRequest,
    UpdateHealthDataRequest,
    DataType,
    DataSource,
    HealthData,
    VitalSigns,
)
from health_data_service.services.health_data_service import HealthDataService, VitalSignsService, TCMDiagnosisService


class TestHealthDataService:
    """健康数据服务测试"""

    @pytest.fixture
    def health_data_service(self):
        """健康数据服务实例"""
        return HealthDataService()

    @pytest.fixture
    def sample_create_request(self):
        """示例创建请求"""
        return CreateHealthDataRequest(
            user_id=1,
            data_type=DataType.VITAL_SIGNS,
            data_source=DataSource.DEVICE,
            raw_data={"heart_rate": 72, "blood_pressure": "120/80"},
            device_id="device_001",
            tags=["test"]
        )

    @pytest.fixture
    def sample_health_data(self):
        """示例健康数据"""
        return HealthData(
            id=1,
            user_id=1,
            data_type=DataType.VITAL_SIGNS,
            data_source=DataSource.DEVICE,
            raw_data={"heart_rate": 72, "blood_pressure": "120/80"},
            device_id="device_001",
            tags=["test"],
            recorded_at=datetime.now(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    @pytest.mark.asyncio
    async def test_create_health_data_success(self, health_data_service, sample_create_request):
        """测试成功创建健康数据"""
        # Mock数据库操作
        mock_record = {
            "id": 1,
            "user_id": 1,
            "data_type": "vital_signs",
            "data_source": "device",
            "raw_data": {"heart_rate": 72, "blood_pressure": "120/80"},
            "processed_data": None,
            "device_id": "device_001",
            "location": None,
            "tags": ["test"],
            "quality_score": None,
            "confidence_score": None,
            "is_validated": False,
            "is_anomaly": False,
            "recorded_at": datetime.now(),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        with patch('health_data_service.services.health_data_service.health_data_repo') as mock_repo:
            mock_repo.create_health_data = AsyncMock(return_value=mock_record)
            
            with patch.object(health_data_service, '_get_db_manager', return_value=AsyncMock()):
                result = await health_data_service.create(sample_create_request)

                assert result.id == 1
                assert result.user_id == 1
                assert result.data_type == DataType.VITAL_SIGNS
                assert result.data_source == DataSource.DEVICE
                assert result.raw_data == {"heart_rate": 72, "blood_pressure": "120/80"}

    @pytest.mark.asyncio
    async def test_create_health_data_validation_error(self, health_data_service):
        """测试创建健康数据验证错误"""
        invalid_request = CreateHealthDataRequest(
            user_id=1,
            data_type=DataType.VITAL_SIGNS,
            data_source=DataSource.DEVICE,
            raw_data={},  # 空数据
        )

        with pytest.raises(ValidationError):
            await health_data_service.create(invalid_request)

    @pytest.mark.asyncio
    async def test_get_health_data_by_id_success(self, health_data_service):
        """测试成功根据ID获取健康数据"""
        mock_record = {
            "id": 1,
            "user_id": 1,
            "data_type": "vital_signs",
            "data_source": "device",
            "raw_data": {"heart_rate": 72},
            "processed_data": None,
            "device_id": None,
            "location": None,
            "tags": None,
            "quality_score": None,
            "confidence_score": None,
            "is_validated": False,
            "is_anomaly": False,
            "recorded_at": datetime.now(),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        with patch('health_data_service.services.health_data_service.health_data_repo') as mock_repo:
            mock_repo.get_health_data_by_id = AsyncMock(return_value=mock_record)
            
            with patch.object(health_data_service, '_get_db_manager', return_value=AsyncMock()):
                result = await health_data_service.get_by_id(1)

                assert result is not None
                assert result.id == 1
                assert result.user_id == 1

    @pytest.mark.asyncio
    async def test_get_health_data_by_id_not_found(self, health_data_service):
        """测试根据ID获取健康数据不存在"""
        with patch('health_data_service.services.health_data_service.health_data_repo') as mock_repo:
            mock_repo.get_health_data_by_id = AsyncMock(return_value=None)
            
            with patch.object(health_data_service, '_get_db_manager', return_value=AsyncMock()):
                result = await health_data_service.get_by_id(999)

                assert result is None

    @pytest.mark.asyncio
    async def test_update_health_data_success(self, health_data_service):
        """测试成功更新健康数据"""
        update_request = UpdateHealthDataRequest(
            processed_data={"normalized_heart_rate": 72},
            quality_score=0.85,
            is_validated=True
        )

        # Mock现有数据
        existing_record = {
            "id": 1,
            "user_id": 1,
            "data_type": "vital_signs",
            "data_source": "device",
            "raw_data": {"heart_rate": 72},
            "processed_data": None,
            "device_id": None,
            "location": None,
            "tags": None,
            "quality_score": None,
            "confidence_score": None,
            "is_validated": False,
            "is_anomaly": False,
            "recorded_at": datetime.now(),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        # Mock更新后数据
        updated_record = existing_record.copy()
        updated_record.update({
            "processed_data": {"normalized_heart_rate": 72},
            "quality_score": 0.85,
            "is_validated": True,
            "updated_at": datetime.now(),
        })

        with patch('health_data_service.services.health_data_service.health_data_repo') as mock_repo:
            mock_repo.get_health_data_by_id = AsyncMock(return_value=existing_record)
            mock_repo.update_health_data = AsyncMock(return_value=updated_record)
            
            with patch.object(health_data_service, '_get_db_manager', return_value=AsyncMock()):
                result = await health_data_service.update(1, update_request)

                assert result is not None
                assert result.processed_data == {"normalized_heart_rate": 72}
                assert result.quality_score == 0.85
                assert result.is_validated is True

    @pytest.mark.asyncio
    async def test_update_health_data_not_found(self, health_data_service):
        """测试更新不存在的健康数据"""
        update_request = UpdateHealthDataRequest(quality_score=0.85)

        with patch('health_data_service.services.health_data_service.health_data_repo') as mock_repo:
            mock_repo.get_health_data_by_id = AsyncMock(return_value=None)
            
            with patch.object(health_data_service, '_get_db_manager', return_value=AsyncMock()):
                with pytest.raises(NotFoundError):
                    await health_data_service.update(999, update_request)

    @pytest.mark.asyncio
    async def test_delete_health_data_success(self, health_data_service):
        """测试成功删除健康数据"""
        existing_record = {
            "id": 1,
            "user_id": 1,
            "data_type": "vital_signs",
            "data_source": "device",
            "raw_data": {"heart_rate": 72},
            "processed_data": None,
            "device_id": None,
            "location": None,
            "tags": None,
            "quality_score": None,
            "confidence_score": None,
            "is_validated": False,
            "is_anomaly": False,
            "recorded_at": datetime.now(),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        with patch('health_data_service.services.health_data_service.health_data_repo') as mock_repo:
            mock_repo.get_health_data_by_id = AsyncMock(return_value=existing_record)
            mock_repo.delete_health_data = AsyncMock(return_value=True)
            
            with patch.object(health_data_service, '_get_db_manager', return_value=AsyncMock()):
                result = await health_data_service.delete(1)

                assert result is True

    @pytest.mark.asyncio
    async def test_delete_health_data_not_found(self, health_data_service):
        """测试删除不存在的健康数据"""
        with patch('health_data_service.services.health_data_service.health_data_repo') as mock_repo:
            mock_repo.get_health_data_by_id = AsyncMock(return_value=None)
            
            with patch.object(health_data_service, '_get_db_manager', return_value=AsyncMock()):
                with pytest.raises(NotFoundError):
                    await health_data_service.delete(999)

    @pytest.mark.asyncio
    async def test_list_health_data_success(self, health_data_service):
        """测试成功获取健康数据列表"""
        mock_records = [
            {
                "id": 1,
                "user_id": 1,
                "data_type": "vital_signs",
                "data_source": "device",
                "raw_data": {"heart_rate": 72},
                "processed_data": None,
                "device_id": None,
                "location": None,
                "tags": None,
                "quality_score": None,
                "confidence_score": None,
                "is_validated": False,
                "is_anomaly": False,
                "recorded_at": datetime.now(),
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        ]

        with patch('health_data_service.services.health_data_service.health_data_repo') as mock_repo:
            mock_repo.get_health_data_by_user = AsyncMock(return_value=mock_records)
            
            with patch.object(health_data_service, '_get_db_manager', return_value=AsyncMock()):
                result, total = await health_data_service.list(user_id=1)

                assert len(result) == 1
                assert total == 1
                assert result[0].id == 1

    @pytest.mark.asyncio
    async def test_list_health_data_missing_user_id(self, health_data_service):
        """测试获取健康数据列表缺少用户ID"""
        with patch.object(health_data_service, '_get_db_manager', return_value=AsyncMock()):
            with pytest.raises(ValidationError):
                await health_data_service.list()


class TestVitalSignsService:
    """生命体征服务测试"""

    @pytest.fixture
    def vital_signs_service(self):
        """生命体征服务实例"""
        return VitalSignsService()

    @pytest.fixture
    def sample_create_request(self):
        """示例创建请求"""
        return CreateVitalSignsRequest(
            user_id=1,
            heart_rate=72,
            blood_pressure_systolic=120,
            blood_pressure_diastolic=80,
            body_temperature=36.5,
            weight=70.0,
            height=175.0
        )

    @pytest.mark.asyncio
    async def test_create_vital_signs_success(self, vital_signs_service, sample_create_request):
        """测试成功创建生命体征记录"""
        mock_record = {
            "id": 1,
            "user_id": 1,
            "systolic_bp": 120,
            "diastolic_bp": 80,
            "heart_rate": 72,
            "temperature": 36.5,
            "respiratory_rate": None,
            "oxygen_saturation": None,
            "weight": 70.0,
            "height": 175.0,
            "bmi": 22.86,
            "device_id": None,
            "location": None,
            "notes": None,
            "recorded_at": datetime.now(),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        with patch('health_data_service.services.health_data_service.vital_signs_repo') as mock_repo:
            mock_repo.create_vital_signs = AsyncMock(return_value=mock_record)
            
            with patch.object(vital_signs_service, '_get_db_manager', return_value=AsyncMock()):
                result = await vital_signs_service.create(sample_create_request)

                assert result.id == 1
                assert result.user_id == 1
                assert result.heart_rate == 72
                assert result.blood_pressure_systolic == 120
                assert result.blood_pressure_diastolic == 80
                assert result.bmi == 22.86

    @pytest.mark.asyncio
    async def test_list_vital_signs_success(self, vital_signs_service):
        """测试成功获取生命体征列表"""
        mock_records = [
            {
                "id": 1,
                "user_id": 1,
                "systolic_bp": 120,
                "diastolic_bp": 80,
                "heart_rate": 72,
                "temperature": 36.5,
                "respiratory_rate": None,
                "oxygen_saturation": None,
                "weight": 70.0,
                "height": 175.0,
                "bmi": 22.86,
                "device_id": None,
                "location": None,
                "notes": None,
                "recorded_at": datetime.now(),
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        ]

        with patch('health_data_service.services.health_data_service.vital_signs_repo') as mock_repo:
            mock_repo.get_vital_signs_by_user = AsyncMock(return_value=mock_records)
            
            with patch.object(vital_signs_service, '_get_db_manager', return_value=AsyncMock()):
                result, total = await vital_signs_service.list(user_id=1)

                assert len(result) == 1
                assert total == 1
                assert result[0].id == 1


class TestTCMDiagnosisService:
    """中医诊断服务测试"""

    @pytest.fixture
    def tcm_diagnosis_service(self):
        """中医诊断服务实例"""
        return TCMDiagnosisService()

    @pytest.mark.asyncio
    async def test_create_tcm_diagnosis_success(self, tcm_diagnosis_service):
        """测试成功创建中医诊断记录"""
        mock_record = {
            "id": 1,
            "user_id": 1,
            "diagnosis_type": "look",
            "diagnosis_data": {"face_color": "red", "tongue_color": "pink"},
            "standardized_data": None,
            "quality_score": None,
            "practitioner_id": None,
            "clinic_id": None,
            "session_id": None,
            "notes": None,
            "recorded_at": datetime.now(),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        with patch('health_data_service.services.health_data_service.tcm_diagnosis_repo') as mock_repo:
            mock_repo.create_tcm_diagnosis = AsyncMock(return_value=mock_record)
            
            with patch.object(tcm_diagnosis_service, '_get_db_manager', return_value=AsyncMock()):
                result = await tcm_diagnosis_service.create_tcm_diagnosis(
                    user_id=1,
                    diagnosis_type="look",
                    diagnosis_data={"face_color": "red", "tongue_color": "pink"}
                )

                assert result["id"] == 1
                assert result["user_id"] == 1
                assert result["diagnosis_type"] == "look"

    @pytest.mark.asyncio
    async def test_get_tcm_diagnosis_by_user_success(self, tcm_diagnosis_service):
        """测试成功获取用户中医诊断记录"""
        mock_records = [
            {
                "id": 1,
                "user_id": 1,
                "diagnosis_type": "look",
                "diagnosis_data": {"face_color": "red"},
                "standardized_data": None,
                "quality_score": None,
                "practitioner_id": None,
                "clinic_id": None,
                "session_id": None,
                "notes": None,
                "recorded_at": datetime.now(),
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        ]

        with patch('health_data_service.services.health_data_service.tcm_diagnosis_repo') as mock_repo:
            mock_repo.get_tcm_diagnosis_by_user = AsyncMock(return_value=mock_records)
            
            with patch.object(tcm_diagnosis_service, '_get_db_manager', return_value=AsyncMock()):
                result = await tcm_diagnosis_service.get_tcm_diagnosis_by_user(user_id=1)

                assert len(result) == 1
                assert result[0]["id"] == 1
                assert result[0]["diagnosis_type"] == "look"


if __name__ == "__main__":
    pytest.main([__file__]) 