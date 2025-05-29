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
