"""
auth - 索克生活项目模块
"""

from datetime import datetime, timedelta, UTC
from internal.model.config import JwtConfig
from pydantic import BaseModel
from typing import Dict, List, Optional, Union
import jwt
import logging
import pydantic
import time
import uuid

#! / usr / bin / env python
# - * - coding: utf - 8 - * -

"""
认证工具模块，提供JWT令牌管理
"""




logger = logging.getLogger(__name__)


class TokenPayload(BaseModel):
    """令牌负载"""
    sub: str  # 用户ID
    roles: List[str] = []  # 用户角色
    type: str  # 令牌类型 (access, refresh)
    exp: float  # 过期时间戳
    iat: float  # 签发时间戳
    nbf: float  # 生效时间戳
    jti: str  # 令牌ID


class JWTManager:
    """JWT令牌管理器"""

    def __init__(self, config: JwtConfig):
        """
        初始化JWT管理器

        Args:
            config: JWT配置
        """
        self.config = config

    def create_access_token(self, user_id: str, roles: List[str] = None) - > str:
        """
        创建访问令牌

        Args:
            user_id: 用户ID
            roles: 用户角色列表

        Returns:
            访问令牌
        """
        return self._create_token(
            user_id = user_id,
            roles = roles or ["user"],
            token_type = "access",
            expires_delta = timedelta(minutes = self.config.expire_minutes)
        )

    def create_refresh_token(self, user_id: str, roles: List[str] = None) - > str:
        """
        创建刷新令牌

        Args:
            user_id: 用户ID
            roles: 用户角色列表

        Returns:
            刷新令牌
        """
        return self._create_token(
            user_id = user_id,
            roles = roles or ["user"],
            token_type = "refresh",
            expires_delta = timedelta(minutes = self.config.refresh_expire_minutes)
        )

    def _create_token(
        self,
        user_id: str,
        roles: List[str],
        token_type: str,
        expires_delta: timedelta
    ) - > str:
        """
        创建令牌

        Args:
            user_id: 用户ID
            roles: 用户角色列表
            token_type: 令牌类型
            expires_delta: 过期时间增量

        Returns:
            JWT令牌
        """
        now = datetime.now(UTC)
        expires = now + expires_delta

        # 创建令牌负载
        payload = {
            "sub": user_id,
            "roles": roles,
            "type": token_type,
            "exp": expires.timestamp(),
            "iat": now.timestamp(),
            "nbf": now.timestamp(),
            "jti": str(uuid.uuid4())
        }

        # 编码令牌
        token = jwt.encode(
            payload,
            self.config.secret_key,
            algorithm = self.config.algorithm
        )

        return token

    def decode_token(self, token: str) - > TokenPayload:
        """
        解码令牌

        Args:
            token: JWT令牌

        Returns:
            令牌负载

        Raises:
            jwt.InvalidTokenError: 无效令牌
            jwt.ExpiredSignatureError: 令牌已过期
        """
        payload = jwt.decode(
            token,
            self.config.secret_key,
            algorithms = [self.config.algorithm],
            options = {"verify_signature": True}
        )

        return TokenPayload( * *payload)

    def refresh_access_token(self, refresh_token: str) - > str:
        """
        使用刷新令牌创建新的访问令牌

        Args:
            refresh_token: 刷新令牌

        Returns:
            新的访问令牌

        Raises:
            ValueError: 无效的刷新令牌
        """
        try:
            payload = self.decode_token(refresh_token)

            # 验证令牌类型
            if payload.type ! = "refresh":
                raise ValueError("不是有效的刷新令牌")

            # 创建新的访问令牌
            return self.create_access_token(
                user_id = payload.sub,
                roles = payload.roles
            )

        except jwt.InvalidTokenError as e:
            logger.warning(f"无效的刷新令牌: {e}")
            raise ValueError("无效的刷新令牌") from e

    def validate_token(self, token: str) - > TokenPayload:
        """
        验证令牌有效性

        Args:
            token: JWT令牌

        Returns:
            令牌负载

        Raises:
            ValueError: 令牌验证失败的具体原因
        """
        try:
            payload = self.decode_token(token)

            # 验证exp字段
            if not payload.exp or payload.exp < time.time():
                raise ValueError("令牌已过期")

            # 验证nbf字段
            if not payload.nbf or payload.nbf > time.time():
                raise ValueError("令牌尚未生效")

            return payload

        except jwt.ExpiredSignatureError:
            raise ValueError("令牌已过期")
        except pydantic.ValidationError:
            # 处理验证错误，表示令牌缺少必要字段
            raise ValueError("缺少必要字段")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"无效的令牌: {str(e)}")


def extract_token_from_header(authorization: str) - > str:
    """
    从认证头中提取令牌

    Args:
        authorization: 认证头

    Returns:
        JWT令牌

    Raises:
        ValueError: 无效的认证头格式
    """
    if not authorization:
        raise ValueError("未提供认证令牌")

    parts = authorization.split()
    if len(parts) ! = 2 or parts[0].lower() ! = "bearer":
        raise ValueError("无效的认证头部格式")

    return parts[1]