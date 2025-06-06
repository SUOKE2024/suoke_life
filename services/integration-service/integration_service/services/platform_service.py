"""
platform_service - 索克生活项目模块
"""

from ..models.platform import Platform, PlatformConfig
from .base_service import BaseService
from sqlalchemy.orm import Session

"""
平台服务
"""





class PlatformService(BaseService[Platform]):
    """平台服务"""

    def __init__(self, db: Session):
        super().__init__(Platform, db)

    async def get_by_name(self, name: str) -> Platform | None:
        """根据名称获取平台"""
        return self.db.query(self.model).filter(self.model.name == name).first()

    async def get_enabled_platforms(self) -> list[Platform]:
        """获取启用的平台列表"""
        return self.db.query(self.model).filter(self.model.is_enabled).prefetch_related().all()[:1000]  # 限制查询结果数量

    async def get_platform_config(self, platform_id: str, config_key: str) -> PlatformConfig | None:
        """获取平台配置"""
        return (
            self.db.query(PlatformConfig)
            .filter(
                PlatformConfig.platform_id == platform_id,
                PlatformConfig.config_key == config_key
            )
            .first()
        )

    async def set_platform_config(
        self,
        platform_id: str,
        config_key: str,
        config_value: str,
        is_encrypted: bool = False,
        description: str = None
    ) -> PlatformConfig:
        """设置平台配置"""
        config = await self.get_platform_config(platform_id, config_key)

        if config:
            config.config_value = config_value
            config.is_encrypted = is_encrypted
            if description:
                config.description = description
            self.db.commit()
            self.db.refresh(config)
        else:
            config = PlatformConfig(
                platform_id=platform_id,
                config_key=config_key,
                config_value=config_value,
                is_encrypted=is_encrypted,
                description=description
            )
            self.db.add(config)
            self.db.commit()
            self.db.refresh(config)

        return config
