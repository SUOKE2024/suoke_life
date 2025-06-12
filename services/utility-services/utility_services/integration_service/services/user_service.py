"""
user_service - 索克生活项目模块
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..core.security import get_password_hash, verify_password
from ..models.user import User, UserPlatformAuth
from .base_service import BaseService

"""
用户服务模块
"""


logger = logging.getLogger(__name__)


class UserService(BaseService[User]):
    """用户服务类"""

    def __init__(self, db: Session):
        """TODO: 添加文档字符串"""
        super().__init__(User, db)

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """根据用户ID获取用户"""
        try:
            return self.db.query(User).filter(User.id == user_id).first()
        except Exception as e:
            logger.error(f"获取用户失败: {e}")
            return None

    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        try:
            return self.db.query(User).filter(User.username == username).first()
        except Exception as e:
            logger.error(f"根据用户名获取用户失败: {e}")
            return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        try:
            return self.db.query(User).filter(User.email == email).first()
        except Exception as e:
            logger.error(f"根据邮箱获取用户失败: {e}")
            return None

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """验证用户凭据"""
        try:
            # 尝试用户名登录
            user = self.get_user_by_username(username)

            # 如果用户名不存在，尝试邮箱登录
            if not user:
                user = self.get_user_by_email(username)

            if not user:
                return None

            # 验证密码（这里假设用户模型有password字段）
            # 实际实现中需要根据具体的用户模型调整
            if hasattr(user, "password_hash") and verify_password(
                password, user.password_hash
            ):
                return user

            return None

        except Exception as e:
            logger.error(f"用户认证失败: {e}")
            return None

    def create_user(
        self,
        username: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        password: Optional[str] = None,
        profile: Optional[Dict[str, Any]] = None,
    ) -> Optional[User]:
        """创建新用户"""
        try:
            # 检查用户名是否已存在
            if self.get_user_by_username(username):
                logger.warning(f"用户名 {username} 已存在")
                return None

            # 检查邮箱是否已存在
            if email and self.get_user_by_email(email):
                logger.warning(f"邮箱 {email} 已存在")
                return None

            # 创建用户对象
            user_data = {
                "username": username,
                "email": email,
                "phone": phone,
                "is_active": True,
                "profile": profile or {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }

            # 如果提供了密码，进行哈希处理
            if password:
                user_data["password_hash"] = get_password_hash(password)

            user = User(**user_data)

            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

            logger.info(f"用户 {username} 创建成功")
            return user

        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"创建用户失败，数据完整性错误: {e}")
            return None
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建用户失败: {e}")
            return None

    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[User]:
        """更新用户信息"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return None

            # 更新字段
            for field, value in update_data.items():
                if hasattr(user, field):
                    setattr(user, field, value)

            # 更新时间戳
            user.updated_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(user)

            logger.info(f"用户 {user_id} 信息更新成功")
            return user

        except Exception as e:
            self.db.rollback()
            logger.error(f"更新用户信息失败: {e}")
            return None

    def update_user_password(self, user_id: str, new_password: str) -> bool:
        """更新用户密码"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False

            # 哈希新密码
            password_hash = get_password_hash(new_password)

            # 更新密码
            if hasattr(user, "password_hash"):
                user.password_hash = password_hash
                user.updated_at = datetime.utcnow()

                self.db.commit()

                logger.info(f"用户 {user_id} 密码更新成功")
                return True

            return False

        except Exception as e:
            self.db.rollback()
            logger.error(f"更新用户密码失败: {e}")
            return False

    def deactivate_user(self, user_id: str) -> bool:
        """停用用户"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False

            user.is_active = False
            user.updated_at = datetime.utcnow()

            self.db.commit()

            logger.info(f"用户 {user_id} 已停用")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"停用用户失败: {e}")
            return False

    def activate_user(self, user_id: str) -> bool:
        """激活用户"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False

            user.is_active = True
            user.updated_at = datetime.utcnow()

            self.db.commit()

            logger.info(f"用户 {user_id} 已激活")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"激活用户失败: {e}")
            return False

    def delete_user(self, user_id: str) -> bool:
        """删除用户"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False

            self.db.delete(user)
            self.db.commit()

            logger.info(f"用户 {user_id} 已删除")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"删除用户失败: {e}")
            return False

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户档案"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return None

            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "is_active": user.is_active,
                "profile": user.profile,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat(),
            }

        except Exception as e:
            logger.error(f"获取用户档案失败: {e}")
            return None

    def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """更新用户档案"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False

            # 合并档案数据
            current_profile = user.profile or {}
            current_profile.update(profile_data)

            user.profile = current_profile
            user.updated_at = datetime.utcnow()

            self.db.commit()

            logger.info(f"用户 {user_id} 档案更新成功")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"更新用户档案失败: {e}")
            return False

    async def get_user_platform_auth(
        self, user_id: str, platform_id: str
    ) -> UserPlatformAuth | None:
        """获取用户平台授权信息"""
        return (
            self.db.query(UserPlatformAuth)
            .filter(
                UserPlatformAuth.user_id == user_id,
                UserPlatformAuth.platform_id == platform_id,
            )
            .first()
        )

    async def create_or_update_platform_auth(
        self,
        user_id: str,
        platform_id: str,
        access_token: str = None,
        refresh_token: str = None,
        token_expires_at=None,
        auth_metadata: dict = None,
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
                is_active=True,
            )
            self.db.add(auth)
            self.db.commit()
            self.db.refresh(auth)

        return auth

    async def get_user_platforms(self, user_id: str) -> list[UserPlatformAuth]:
        """获取用户已授权的平台列表"""
        return (
            self.db.query(UserPlatformAuth)
            .filter(UserPlatformAuth.user_id == user_id, UserPlatformAuth.is_active)
            .all()[:1000]  # 限制查询结果数量
        )
