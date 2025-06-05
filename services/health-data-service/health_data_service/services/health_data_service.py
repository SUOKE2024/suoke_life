"""健康数据服务"""

import contextlib
import time
from datetime import datetime
from typing import Any, Optional, List, Tuple

from loguru import logger

from health_data_service.core.exceptions import DatabaseError
from health_data_service.core.exceptions import NotFoundError
from health_data_service.core.exceptions import ValidationError
from health_data_service.core.database import (
    get_database, 
    health_data_repo, 
    vital_signs_repo,
    tcm_diagnosis_repo,
    processing_records_repo
)
from health_data_service.models import CreateHealthDataRequest
from health_data_service.models import CreateVitalSignsRequest
from health_data_service.models import DataSource
from health_data_service.models import DataType
from health_data_service.models import HealthData
from health_data_service.models import UpdateHealthDataRequest
from health_data_service.models import VitalSigns

from .base import BaseService

class HealthDataService(BaseService[HealthData, CreateHealthDataRequest, UpdateHealthDataRequest]):
    """健康数据服务"""

    def __init__(self) -> None:
        super().__init__()
        self.db_manager = None

    async def _get_db_manager(self):
        """获取数据库管理器"""
        if not self.db_manager:
            self.db_manager = await get_database()
            if not self.db_manager._async_engine:
                await self.db_manager.initialize()
        return self.db_manager

    async def create(self, data: CreateHealthDataRequest) -> HealthData:
        """创建健康数据"""
        start_time = time.time()

        try:
            # 验证数据
            if not data.raw_data:
                raise ValidationError("原始数据不能为空")

            # 设置默认记录时间
            recorded_at = data.recorded_at or datetime.now()

            # 准备数据库数据
            db_data = {
                "user_id": data.user_id,
                "data_type": data.data_type.value,
                "data_source": data.data_source.value,
                "raw_data": data.raw_data,
                "device_id": data.device_id,
                "location": data.location,
                "tags": data.tags,
                "recorded_at": recorded_at,
            }

            # 创建数据库记录
            await self._get_db_manager()
            record = await health_data_repo.create_health_data(db_data)
            
            if not record:
                raise DatabaseError("创建健康数据失败")

            # 转换为模型
            health_data = HealthData(
                id=record["id"],
                user_id=record["user_id"],
                data_type=DataType(record["data_type"]),
                data_source=DataSource(record["data_source"]),
                raw_data=record["raw_data"],
                processed_data=record.get("processed_data"),
                device_id=record.get("device_id"),
                location=record.get("location"),
                tags=record.get("tags") or [],
                quality_score=record.get("quality_score"),
                confidence_score=record.get("confidence_score"),
                is_validated=record.get("is_validated", False),
                is_anomaly=record.get("is_anomaly", False),
                recorded_at=record["recorded_at"],
                created_at=record["created_at"],
                updated_at=record["updated_at"],
            )

            duration = time.time() - start_time
            self._log_operation("CREATE", "health_data", duration, affected_rows=1)

            logger.info(f"创建健康数据成功: user_id={data.user_id}, type={data.data_type}")
            return health_data

        except Exception as e:
            duration = time.time() - start_time
            self._log_operation("CREATE", "health_data", duration, error=str(e))

            if isinstance(e, (ValidationError, DatabaseError)):
                raise
            raise DatabaseError(f"创建健康数据失败: {str(e)}") from e

    async def get_by_id(self, id: int) -> Optional[HealthData]:
        """根据ID获取健康数据"""
        start_time = time.time()

        try:
            await self._get_db_manager()
            record = await health_data_repo.get_health_data_by_id(id)
            
            if not record:
                duration = time.time() - start_time
                self._log_operation("SELECT", "health_data", duration)
                return None

            # 转换为模型
            health_data = HealthData(
                id=record["id"],
                user_id=record["user_id"],
                data_type=DataType(record["data_type"]),
                data_source=DataSource(record["data_source"]),
                raw_data=record["raw_data"],
                processed_data=record.get("processed_data"),
                device_id=record.get("device_id"),
                location=record.get("location"),
                tags=record.get("tags") or [],
                quality_score=record.get("quality_score"),
                confidence_score=record.get("confidence_score"),
                is_validated=record.get("is_validated", False),
                is_anomaly=record.get("is_anomaly", False),
                recorded_at=record["recorded_at"],
                created_at=record["created_at"],
                updated_at=record["updated_at"],
            )

            duration = time.time() - start_time
            self._log_operation("SELECT", "health_data", duration)
            return health_data

        except Exception as e:
            duration = time.time() - start_time
            self._log_operation("SELECT", "health_data", duration, error=str(e))
            raise DatabaseError(f"查询健康数据失败: {str(e)}") from e

    async def update(self, id: int, data: UpdateHealthDataRequest) -> Optional[HealthData]:
        """更新健康数据"""
        start_time = time.time()

        try:
            # 检查数据是否存在
            existing_data = await self.get_by_id(id)
            if not existing_data:
                raise NotFoundError(f"健康数据不存在: id={id}")

            # 准备更新数据
            update_data = {}
            if data.processed_data is not None:
                update_data["processed_data"] = data.processed_data
            if data.quality_score is not None:
                update_data["quality_score"] = data.quality_score
            if data.confidence_score is not None:
                update_data["confidence_score"] = data.confidence_score
            if data.is_validated is not None:
                update_data["is_validated"] = data.is_validated
            if data.is_anomaly is not None:
                update_data["is_anomaly"] = data.is_anomaly
            if data.tags is not None:
                update_data["tags"] = data.tags

            # 更新数据库记录
            await self._get_db_manager()
            record = await health_data_repo.update_health_data(id, update_data)
            
            if not record:
                raise DatabaseError("更新健康数据失败")

            # 转换为模型
            health_data = HealthData(
                id=record["id"],
                user_id=record["user_id"],
                data_type=DataType(record["data_type"]),
                data_source=DataSource(record["data_source"]),
                raw_data=record["raw_data"],
                processed_data=record.get("processed_data"),
                device_id=record.get("device_id"),
                location=record.get("location"),
                tags=record.get("tags") or [],
                quality_score=record.get("quality_score"),
                confidence_score=record.get("confidence_score"),
                is_validated=record.get("is_validated", False),
                is_anomaly=record.get("is_anomaly", False),
                recorded_at=record["recorded_at"],
                created_at=record["created_at"],
                updated_at=record["updated_at"],
            )

            duration = time.time() - start_time
            self._log_operation("UPDATE", "health_data", duration, affected_rows=1)

            logger.info(f"更新健康数据成功: id={id}")
            return health_data

        except Exception as e:
            duration = time.time() - start_time
            self._log_operation("UPDATE", "health_data", duration, error=str(e))

            if isinstance(e, (NotFoundError, ValidationError, DatabaseError)):
                raise
            raise DatabaseError(f"更新健康数据失败: {str(e)}") from e

    async def delete(self, id: int) -> bool:
        """删除健康数据"""
        start_time = time.time()

        try:
            # 检查数据是否存在
            existing_data = await self.get_by_id(id)
            if not existing_data:
                raise NotFoundError(f"健康数据不存在: id={id}")

            # 删除数据库记录
            await self._get_db_manager()
            success = await health_data_repo.delete_health_data(id)
            
            if not success:
                raise DatabaseError("删除健康数据失败")

            duration = time.time() - start_time
            self._log_operation("DELETE", "health_data", duration, affected_rows=1)

            logger.info(f"删除健康数据成功: id={id}")
            return True

        except Exception as e:
            duration = time.time() - start_time
            self._log_operation("DELETE", "health_data", duration, error=str(e))

            if isinstance(e, (NotFoundError, DatabaseError)):
                raise
            raise DatabaseError(f"删除健康数据失败: {str(e)}") from e

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters: Any,
    ) -> Tuple[List[HealthData], int]:
        """获取健康数据列表"""
        start_time = time.time()

        try:
            await self._get_db_manager()
            
            # 获取用户数据
            user_id = filters.get("user_id")
            data_type = filters.get("data_type")
            
            if not user_id:
                raise ValidationError("必须提供用户ID")

            records = await health_data_repo.get_health_data_by_user(
                user_id=user_id,
                data_type=data_type,
                limit=limit,
                offset=skip
            )

            # 转换为模型列表
            health_data_list = []
            for record in records:
                health_data = HealthData(
                    id=record["id"],
                    user_id=record["user_id"],
                    data_type=DataType(record["data_type"]),
                    data_source=DataSource(record["data_source"]),
                    raw_data=record["raw_data"],
                    processed_data=record.get("processed_data"),
                    device_id=record.get("device_id"),
                    location=record.get("location"),
                    tags=record.get("tags") or [],
                    quality_score=record.get("quality_score"),
                    confidence_score=record.get("confidence_score"),
                    is_validated=record.get("is_validated", False),
                    is_anomaly=record.get("is_anomaly", False),
                    recorded_at=record["recorded_at"],
                    created_at=record["created_at"],
                    updated_at=record["updated_at"],
                )
                health_data_list.append(health_data)

            duration = time.time() - start_time
            self._log_operation("SELECT", "health_data", duration, affected_rows=len(health_data_list))

            return health_data_list, len(health_data_list)

        except Exception as e:
            duration = time.time() - start_time
            self._log_operation("SELECT", "health_data", duration, error=str(e))

            if isinstance(e, (ValidationError, DatabaseError)):
                raise
            raise DatabaseError(f"查询健康数据列表失败: {str(e)}") from e

    async def get_by_user_id(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        data_type: Optional[str] = None,
    ) -> Tuple[List[HealthData], int]:
        """根据用户ID获取健康数据"""
        filters = {"user_id": user_id}
        if data_type:
            filters["data_type"] = data_type
        
        return await self.list(skip=skip, limit=limit, **filters)


class VitalSignsService(BaseService[VitalSigns, CreateVitalSignsRequest, dict]):
    """生命体征服务"""

    def __init__(self) -> None:
        super().__init__()
        self.db_manager = None

    async def _get_db_manager(self):
        """获取数据库管理器"""
        if not self.db_manager:
            self.db_manager = await get_database()
            if not self.db_manager._async_engine:
                await self.db_manager.initialize()
        return self.db_manager

    async def create(self, data: CreateVitalSignsRequest) -> VitalSigns:
        """创建生命体征记录"""
        start_time = time.time()

        try:
            # 设置默认记录时间
            recorded_at = data.recorded_at or datetime.now()

            # 计算BMI
            bmi = None
            if data.weight and data.height:
                height_m = data.height / 100  # 转换为米
                bmi = data.weight / (height_m * height_m)

            # 准备数据库数据
            db_data = {
                "user_id": data.user_id,
                "systolic_bp": data.blood_pressure_systolic,
                "diastolic_bp": data.blood_pressure_diastolic,
                "heart_rate": data.heart_rate,
                "temperature": data.body_temperature,
                "respiratory_rate": data.respiratory_rate,
                "oxygen_saturation": data.oxygen_saturation,
                "weight": data.weight,
                "height": data.height,
                "bmi": bmi,
                "device_id": data.device_id,
                "location": None,  # CreateVitalSignsRequest没有location字段
                "notes": data.notes,
                "recorded_at": recorded_at,
            }

            # 创建数据库记录
            await self._get_db_manager()
            record = await vital_signs_repo.create_vital_signs(db_data)
            
            if not record:
                raise DatabaseError("创建生命体征记录失败")

            # 转换为模型
            vital_signs = VitalSigns(
                id=record["id"],
                user_id=record["user_id"],
                blood_pressure_systolic=record.get("systolic_bp"),
                blood_pressure_diastolic=record.get("diastolic_bp"),
                heart_rate=record.get("heart_rate"),
                body_temperature=record.get("temperature"),
                respiratory_rate=record.get("respiratory_rate"),
                oxygen_saturation=record.get("oxygen_saturation"),
                weight=record.get("weight"),
                height=record.get("height"),
                bmi=record.get("bmi"),
                device_id=record.get("device_id"),
                notes=record.get("notes"),
                recorded_at=record["recorded_at"],
                created_at=record["created_at"],
                updated_at=record["updated_at"],
            )

            duration = time.time() - start_time
            self._log_operation("CREATE", "vital_signs", duration, affected_rows=1)

            logger.info(f"创建生命体征记录成功: user_id={data.user_id}")
            return vital_signs

        except Exception as e:
            duration = time.time() - start_time
            self._log_operation("CREATE", "vital_signs", duration, error=str(e))

            if isinstance(e, (ValidationError, DatabaseError)):
                raise
            raise DatabaseError(f"创建生命体征记录失败: {str(e)}") from e

    async def get_by_id(self, id: int) -> Optional[VitalSigns]:
        """根据ID获取生命体征记录"""
        # TODO: 实现根据ID查询
        return None

    async def update(self, id: int, data: dict) -> Optional[VitalSigns]:
        """更新生命体征记录"""
        # TODO: 实现更新逻辑
        return None

    async def delete(self, id: int) -> bool:
        """删除生命体征记录"""
        # TODO: 实现删除逻辑
        return False

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters: Any,
    ) -> Tuple[List[VitalSigns], int]:
        """获取生命体征列表"""
        start_time = time.time()

        try:
            await self._get_db_manager()
            
            user_id = filters.get("user_id")
            if not user_id:
                raise ValidationError("必须提供用户ID")

            records = await vital_signs_repo.get_vital_signs_by_user(
                user_id=user_id,
                limit=limit,
                offset=skip
            )

            # 转换为模型列表
            vital_signs_list = []
            for record in records:
                vital_signs = VitalSigns(
                    id=record["id"],
                    user_id=record["user_id"],
                    blood_pressure_systolic=record.get("systolic_bp"),
                    blood_pressure_diastolic=record.get("diastolic_bp"),
                    heart_rate=record.get("heart_rate"),
                    body_temperature=record.get("temperature"),
                    respiratory_rate=record.get("respiratory_rate"),
                    oxygen_saturation=record.get("oxygen_saturation"),
                    weight=record.get("weight"),
                    height=record.get("height"),
                    bmi=record.get("bmi"),
                    device_id=record.get("device_id"),
                    notes=record.get("notes"),
                    recorded_at=record["recorded_at"],
                    created_at=record["created_at"],
                    updated_at=record["updated_at"],
                )
                vital_signs_list.append(vital_signs)

            duration = time.time() - start_time
            self._log_operation("SELECT", "vital_signs", duration, affected_rows=len(vital_signs_list))

            return vital_signs_list, len(vital_signs_list)

        except Exception as e:
            duration = time.time() - start_time
            self._log_operation("SELECT", "vital_signs", duration, error=str(e))

            if isinstance(e, (ValidationError, DatabaseError)):
                raise
            raise DatabaseError(f"查询生命体征列表失败: {str(e)}") from e


class TCMDiagnosisService:
    """中医诊断服务"""

    def __init__(self):
        self.db_manager = None

    async def _get_db_manager(self):
        """获取数据库管理器"""
        if not self.db_manager:
            self.db_manager = await get_database()
            if not self.db_manager._async_engine:
                await self.db_manager.initialize()
        return self.db_manager

    async def create_tcm_diagnosis(
        self,
        user_id: int,
        diagnosis_type: str,
        diagnosis_data: dict,
        standardized_data: Optional[dict] = None,
        quality_score: Optional[float] = None,
        practitioner_id: Optional[int] = None,
        clinic_id: Optional[int] = None,
        session_id: Optional[str] = None,
        notes: Optional[str] = None,
        recorded_at: Optional[datetime] = None
    ) -> dict:
        """创建中医诊断记录"""
        try:
            db_data = {
                "user_id": user_id,
                "diagnosis_type": diagnosis_type,
                "diagnosis_data": diagnosis_data,
                "standardized_data": standardized_data,
                "quality_score": quality_score,
                "practitioner_id": practitioner_id,
                "clinic_id": clinic_id,
                "session_id": session_id,
                "notes": notes,
                "recorded_at": recorded_at or datetime.now(),
            }

            await self._get_db_manager()
            record = await tcm_diagnosis_repo.create_tcm_diagnosis(db_data)
            
            if not record:
                raise DatabaseError("创建中医诊断记录失败")

            logger.info(f"创建中医诊断记录成功: user_id={user_id}, type={diagnosis_type}")
            return record

        except Exception as e:
            logger.error(f"创建中医诊断记录失败: {e}")
            raise DatabaseError(f"创建中医诊断记录失败: {str(e)}") from e

    async def get_tcm_diagnosis_by_user(
        self,
        user_id: int,
        diagnosis_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[dict]:
        """根据用户ID获取中医诊断记录"""
        try:
            await self._get_db_manager()
            records = await tcm_diagnosis_repo.get_tcm_diagnosis_by_user(
                user_id=user_id,
                diagnosis_type=diagnosis_type,
                limit=limit,
                offset=offset
            )
            return records

        except Exception as e:
            logger.error(f"查询中医诊断记录失败: {e}")
            raise DatabaseError(f"查询中医诊断记录失败: {str(e)}") from e
