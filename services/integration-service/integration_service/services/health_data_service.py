"""
健康数据服务
"""


from sqlalchemy.orm import Session

from ..models.health_data import HealthData, HealthDataType
from .base_service import BaseService


class HealthDataService(BaseService[HealthData]):
    """健康数据服务"""

    def __init__(self, db: Session):
        super().__init__(HealthData, db)

    async def get_by_user_and_type(
        self,
        user_id: str,
        data_type: HealthDataType,
        skip: int = 0,
        limit: int = 100
    ) -> list[HealthData]:
        """根据用户ID和数据类型获取健康数据"""
        return (
            self.db.query(self.model)
            .filter(
                self.model.user_id == user_id,
                self.model.data_type == data_type
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    async def get_by_user_and_platform(
        self,
        user_id: str,
        platform_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[HealthData]:
        """根据用户ID和平台ID获取健康数据"""
        return (
            self.db.query(self.model)
            .filter(
                self.model.user_id == user_id,
                self.model.platform_id == platform_id
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    async def get_latest_by_type(
        self,
        user_id: str,
        data_type: HealthDataType
    ) -> HealthData | None:
        """获取用户某类型的最新健康数据"""
        return (
            self.db.query(self.model)
            .filter(
                self.model.user_id == user_id,
                self.model.data_type == data_type
            )
            .order_by(self.model.created_at.desc())
            .first()
        )


class HealthDataIntegrationService:
    """
    只负责第三方系统对接、数据格式转换与合规校验，不实现业务决策逻辑。
    所有健康数据、诊断结果等接口均推荐采用FHIR、OpenAPI Schema等标准格式。
    """
    def __init__(self):
        pass

    def receive_external_data(self, data: dict) -> dict:
        """接收第三方系统数据，转换为FHIR标准格式"""
        # TODO: 实现数据格式转换
        fhir_data = self._convert_to_fhir(data)
        # 合规校验
        if not self._validate_fhir(fhir_data):
            raise ValueError("数据不符合FHIR标准")
        return fhir_data

    def _convert_to_fhir(self, data: dict) -> dict:
        # TODO: 实现具体转换逻辑
        return {"resourceType": "Observation", **data}

    def _validate_fhir(self, fhir_data: dict) -> bool:
        # TODO: 实现FHIR格式校验
        return "resourceType" in fhir_data
