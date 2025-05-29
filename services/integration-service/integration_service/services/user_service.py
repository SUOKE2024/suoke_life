"""
用户服务
"""


from sqlalchemy.orm import Session

from ..models.user import User, UserPlatformAuth
from .base_service import BaseService


class UserService(BaseService[User]):
    """用户服务"""

    def __init__(self, db: Session):
        super().__init__(User, db)

    async def get_by_username(self, username: str) -> User | None:
        """根据用户名获取用户"""
        return self.db.query(self.model).filter(self.model.username == username).first()

    async def get_by_email(self, email: str) -> User | None:
        """根据邮箱获取用户"""
        return self.db.query(self.model).filter(self.model.email == email).first()

    async def get_user_platform_auth(
        self,
        user_id: str,
        platform_id: str
    ) -> UserPlatformAuth | None:
        """获取用户平台授权信息"""
        return (
            self.db.query(UserPlatformAuth)
            .filter(
                UserPlatformAuth.user_id == user_id,
                UserPlatformAuth.platform_id == platform_id
            )
            .first()
        )

    async def create_or_update_platform_auth(
        self,
        user_id: str,
        platform_id: str,
        access_token: str = None,
        refresh_token: str = None,
        token_expires_at = None,
        auth_metadata: dict = None
    ) -> UserPlatformAuth:
        """创建或更新用户平台授权"""
        auth = await self.get_user_platform_auth(user_id, platform_id)

        if auth:
            if access_token:
                auth.access_token = access_token
            if refresh_token:
                auth.refresh_token = refresh_token
            if token_expires_at:
                auth.token_expires_at = token_expires_at
            if auth_metadata:
                auth.auth_metadata = auth_metadata
            auth.is_active = True
            self.db.commit()
            self.db.refresh(auth)
        else:
            auth = UserPlatformAuth(
                user_id=user_id,
                platform_id=platform_id,
                access_token=access_token,
                refresh_token=refresh_token,
                token_expires_at=token_expires_at,
                auth_metadata=auth_metadata,
                is_active=True
            )
            self.db.add(auth)
            self.db.commit()
            self.db.refresh(auth)

        return auth

    async def get_user_platforms(self, user_id: str) -> list[UserPlatformAuth]:
        """获取用户已授权的平台列表"""
        return (
            self.db.query(UserPlatformAuth)
            .filter(
                UserPlatformAuth.user_id == user_id,
                UserPlatformAuth.is_active
            )
            .all()
        )
