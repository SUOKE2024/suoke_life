#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完整的认证服务实现

提供用户认证、令牌管理、多因子认证、密码重置等完整功能。
"""
import logging
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

import jwt
import pyotp
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from internal.config.settings import get_settings
from internal.db import get_db_session, get_redis_client
from internal.model.user import User, UserStatusEnum, MFATypeEnum
from internal.repository.user_repository_new import UserRepository
from internal.repository.token_repository import TokenRepository
from internal.repository.audit_repository import AuditRepository
from internal.security.password import PasswordManager
from .email_service import EmailService
from .sms_service import SMSService

logger = logging.getLogger(__name__)
settings = get_settings()

# OAuth2配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")


class AuthService:
    """完整的认证服务类"""
    
    def __init__(
        self,
        user_repo: UserRepository,
        token_repo: TokenRepository,
        audit_repo: AuditRepository,
        email_service: EmailService,
        sms_service: SMSService,
        password_manager: PasswordManager,
        redis_client=None
    ):
        self.user_repo = user_repo
        self.token_repo = token_repo
        self.audit_repo = audit_repo
        self.email_service = email_service
        self.sms_service = sms_service
        self.password_manager = password_manager
        self.redis_client = redis_client
        
    async def authenticate_user(self, username: str, password: str, ip_address: str = None) -> Optional[User]:
        """
        验证用户凭据
        
        Args:
            username: 用户名或邮箱
            password: 密码
            ip_address: 客户端IP地址
        
        Returns:
            Optional[User]: 验证成功返回用户对象，否则返回None
        """
        logger.info(f"尝试验证用户: {username}")
        
        try:
            # 查找用户
            user = await self.user_repo.get_by_username_or_email(username)
            if not user:
                await self._log_failed_login(username, ip_address, "用户不存在")
                return None
            
            # 检查用户状态
            if user.status != UserStatusEnum.ACTIVE:
                await self._log_failed_login(username, ip_address, f"用户状态: {user.status}")
                return None
            
            # 验证密码
            if not self.password_manager.verify_password(password, user.password_hash):
                await self._log_failed_login(username, ip_address, "密码错误")
                return None
            
            # 记录成功登录
            await self.audit_repo.log_action(
                user_id=user.id,
                action="LOGIN_SUCCESS",
                resource="auth",
                ip_address=ip_address,
                details={"username": username}
            )
            
            # 更新最后登录时间
            await self.user_repo.update_last_login(user.id)
            
            return user
            
        except Exception as e:
            logger.error(f"用户认证失败: {str(e)}")
            await self._log_failed_login(username, ip_address, f"系统错误: {str(e)}")
            return None
    
    async def create_tokens(self, user: User, device_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        为用户创建访问令牌和刷新令牌
        
        Args:
            user: 用户对象
            device_info: 设备信息
        
        Returns:
            Dict[str, Any]: 包含令牌的字典
        """
        logger.info(f"为用户创建令牌: {user.id}")
        
        try:
            # 创建访问令牌
            access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
            access_token = self._create_jwt_token(
                data={
                    "sub": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "type": "access",
                    "permissions": await self._get_user_permissions(user)
                },
                expires_delta=access_token_expires
            )
            
            # 创建刷新令牌
            refresh_token_expires = timedelta(days=settings.jwt_refresh_token_expire_days)
            refresh_token = self._create_jwt_token(
                data={
                    "sub": str(user.id),
                    "type": "refresh",
                    "jti": str(uuid.uuid4())  # JWT ID for token revocation
                },
                expires_delta=refresh_token_expires
            )
            
            # 保存刷新令牌到数据库
            await self.token_repo.create_refresh_token(
                user_id=user.id,
                token=refresh_token,
                expires_at=datetime.utcnow() + refresh_token_expires,
                device_info=device_info or {}
            )
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": settings.jwt_access_token_expire_minutes * 60,
                "refresh_expires_in": settings.jwt_refresh_token_expire_days * 24 * 60 * 60,
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "status": user.status,
                    "permissions": await self._get_user_permissions(user)
                }
            }
            
        except Exception as e:
            logger.error(f"创建令牌失败: {str(e)}")
            raise ValueError(f"创建令牌失败: {str(e)}")
    
    def _create_jwt_token(self, data: Dict[str, Any], expires_delta: timedelta) -> str:
        """
        创建JWT令牌
        
        Args:
            data: 令牌数据
            expires_delta: 有效期
        
        Returns:
            str: JWT令牌
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": settings.jwt_issuer
        })
        
        encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        return encoded_jwt
    
    async def refresh_tokens(self, refresh_token: str, device_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        使用刷新令牌获取新的访问令牌
        
        Args:
            refresh_token: 刷新令牌
            device_info: 设备信息
        
        Returns:
            Dict[str, Any]: 包含新令牌的字典
        
        Raises:
            ValueError: 刷新令牌无效
        """
        logger.info("使用刷新令牌获取新的访问令牌")
        
        try:
            # 验证刷新令牌
            payload = jwt.decode(
                refresh_token, 
                settings.jwt_secret_key, 
                algorithms=[settings.jwt_algorithm]
            )
            
            user_id = payload.get("sub")
            token_type = payload.get("type")
            jti = payload.get("jti")
            
            if not user_id or token_type != "refresh" or not jti:
                raise ValueError("无效的刷新令牌格式")
            
            # 检查令牌是否在数据库中存在且有效
            stored_token = await self.token_repo.get_refresh_token(refresh_token)
            if not stored_token or stored_token.is_revoked:
                raise ValueError("刷新令牌已失效")
            
            # 获取用户
            user = await self.user_repo.get_by_id(uuid.UUID(user_id))
            if not user or user.status != UserStatusEnum.ACTIVE:
                raise ValueError("用户不存在或已禁用")
            
            # 撤销旧的刷新令牌
            await self.token_repo.revoke_refresh_token(refresh_token)
            
            # 创建新令牌
            return await self.create_tokens(user, device_info)
            
        except jwt.ExpiredSignatureError:
            logger.warning("刷新令牌已过期")
            raise ValueError("刷新令牌已过期")
        except jwt.PyJWTError as e:
            logger.error(f"刷新令牌验证失败: {str(e)}")
            raise ValueError("无效的刷新令牌")
        except Exception as e:
            logger.error(f"刷新令牌处理失败: {str(e)}")
            raise ValueError(f"刷新令牌处理失败: {str(e)}")
    
    async def logout(self, user: User, refresh_token: str = None) -> None:
        """
        用户登出，撤销令牌
        
        Args:
            user: 用户对象
            refresh_token: 刷新令牌（可选）
        """
        logger.info(f"用户登出: {user.id}")
        
        try:
            # 撤销指定的刷新令牌
            if refresh_token:
                await self.token_repo.revoke_refresh_token(refresh_token)
            else:
                # 撤销用户的所有刷新令牌
                await self.token_repo.revoke_user_tokens(user.id)
            
            # 记录登出事件
            await self.audit_repo.log_action(
                user_id=user.id,
                action="LOGOUT",
                resource="auth",
                details={"logout_type": "manual"}
            )
            
        except Exception as e:
            logger.error(f"用户登出失败: {str(e)}")
            raise ValueError(f"登出失败: {str(e)}")
    
    async def verify_token(self, token: str) -> User:
        """
        验证访问令牌有效性
        
        Args:
            token: 访问令牌
        
        Returns:
            User: 用户对象
        
        Raises:
            ValueError: 令牌无效
        """
        try:
            # 验证令牌
            payload = jwt.decode(
                token, 
                settings.jwt_secret_key, 
                algorithms=[settings.jwt_algorithm]
            )
            
            user_id = payload.get("sub")
            token_type = payload.get("type")
            
            if not user_id or token_type != "access":
                raise ValueError("无效的访问令牌格式")
            
            # 获取用户
            user = await self.user_repo.get_by_id(uuid.UUID(user_id))
            if not user or user.status != UserStatusEnum.ACTIVE:
                raise ValueError("用户不存在或已禁用")
            
            return user
            
        except jwt.ExpiredSignatureError:
            raise ValueError("访问令牌已过期")
        except jwt.PyJWTError as e:
            logger.error(f"访问令牌验证失败: {str(e)}")
            raise ValueError("无效的访问令牌")
        except Exception as e:
            logger.error(f"令牌验证失败: {str(e)}")
            raise ValueError(f"令牌验证失败: {str(e)}")
    
    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> User:
        """
        获取当前用户（FastAPI依赖）
        
        Args:
            token: 访问令牌
        
        Returns:
            User: 当前用户对象
        
        Raises:
            HTTPException: 认证失败
        """
        try:
            return await self.verify_token(token)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def send_password_reset(self, email: str, ip_address: str = None) -> None:
        """
        发送密码重置邮件
        
        Args:
            email: 用户邮箱
            ip_address: 客户端IP地址
        """
        logger.info(f"发送密码重置邮件: {email}")
        
        try:
            # 查找用户
            user = await self.user_repo.get_by_email(email)
            if not user:
                # 为了安全，即使用户不存在也不报错
                logger.warning(f"尝试重置不存在用户的密码: {email}")
                return
            
            # 生成重置令牌
            reset_token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(hours=1)  # 1小时有效期
            
            # 保存重置令牌（使用Redis）
            if self.redis_client:
                await self.redis_client.setex(
                    f"password_reset:{reset_token}",
                    3600,  # 1小时
                    str(user.id)
                )
            
            # 发送重置邮件
            await self.email_service.send_password_reset_email(
                email=user.email,
                username=user.username,
                reset_token=reset_token
            )
            
            # 记录重置请求
            await self.audit_repo.log_action(
                user_id=user.id,
                action="PASSWORD_RESET_REQUEST",
                resource="auth",
                ip_address=ip_address,
                details={"email": email}
            )
            
        except Exception as e:
            logger.error(f"发送密码重置邮件失败: {str(e)}")
            raise ValueError(f"发送重置邮件失败: {str(e)}")
    
    async def reset_password(self, token: str, new_password: str, ip_address: str = None) -> None:
        """
        重置密码
        
        Args:
            token: 重置令牌
            new_password: 新密码
            ip_address: 客户端IP地址
        """
        logger.info("重置用户密码")
        
        try:
            # 验证重置令牌
            if not self.redis_client:
                raise ValueError("密码重置功能不可用")
            
            user_id_str = await self.redis_client.get(f"password_reset:{token}")
            if not user_id_str:
                raise ValueError("重置令牌无效或已过期")
            
            user_id = uuid.UUID(user_id_str.decode())
            
            # 获取用户
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                raise ValueError("用户不存在")
            
            # 验证新密码强度
            if not self.password_manager.validate_password_strength(new_password):
                raise ValueError("密码强度不足")
            
            # 更新密码
            password_hash = self.password_manager.hash_password(new_password)
            await self.user_repo.update_password(user.id, password_hash)
            
            # 删除重置令牌
            await self.redis_client.delete(f"password_reset:{token}")
            
            # 撤销所有刷新令牌（强制重新登录）
            await self.token_repo.revoke_user_tokens(user.id)
            
            # 发送密码重置成功通知
            await self.email_service.send_password_changed_notification(
                email=user.email,
                username=user.username
            )
            
            # 记录密码重置
            await self.audit_repo.log_action(
                user_id=user.id,
                action="PASSWORD_RESET_SUCCESS",
                resource="auth",
                ip_address=ip_address,
                details={"method": "email_token"}
            )
            
        except Exception as e:
            logger.error(f"密码重置失败: {str(e)}")
            raise ValueError(f"密码重置失败: {str(e)}")
    
    async def setup_mfa(self, user: User, mfa_type: str) -> Dict[str, Any]:
        """
        设置多因子认证
        
        Args:
            user: 用户对象
            mfa_type: MFA类型 (totp, sms, email)
        
        Returns:
            Dict[str, Any]: MFA设置信息
        """
        logger.info(f"为用户设置MFA: {user.id}, 类型: {mfa_type}")
        
        try:
            if mfa_type.upper() not in [e.value for e in MFATypeEnum]:
                raise ValueError(f"不支持的MFA类型: {mfa_type}")
            
            mfa_enum = MFATypeEnum(mfa_type.upper())
            
            if mfa_enum == MFATypeEnum.TOTP:
                # 生成TOTP密钥
                secret = pyotp.random_base32()
                
                # 生成QR码URL
                totp = pyotp.TOTP(secret)
                qr_url = totp.provisioning_uri(
                    name=user.email,
                    issuer_name="索克生活"
                )
                
                # 生成备用验证码
                backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
                
                # 保存MFA设置（临时，需要用户验证后才正式启用）
                await self.user_repo.save_mfa_setup(
                    user_id=user.id,
                    mfa_type=mfa_enum,
                    secret=secret,
                    backup_codes=backup_codes,
                    is_verified=False
                )
                
                return {
                    "type": mfa_type,
                    "secret": secret,
                    "qr_code": qr_url,
                    "backup_codes": backup_codes,
                    "success": True
                }
            
            elif mfa_enum == MFATypeEnum.SMS:
                if not user.phone_number:
                    raise ValueError("用户未设置手机号码")
                
                # 生成验证码
                verification_code = secrets.randbelow(900000) + 100000  # 6位数字
                
                # 保存验证码（5分钟有效）
                if self.redis_client:
                    await self.redis_client.setex(
                        f"mfa_setup:{user.id}:sms",
                        300,  # 5分钟
                        str(verification_code)
                    )
                
                # 发送短信
                await self.sms_service.send_mfa_setup_code(
                    phone_number=user.phone_number,
                    code=str(verification_code)
                )
                
                return {
                    "type": mfa_type,
                    "message": "验证码已发送到您的手机",
                    "success": True
                }
            
            elif mfa_enum == MFATypeEnum.EMAIL:
                # 生成验证码
                verification_code = secrets.randbelow(900000) + 100000  # 6位数字
                
                # 保存验证码（5分钟有效）
                if self.redis_client:
                    await self.redis_client.setex(
                        f"mfa_setup:{user.id}:email",
                        300,  # 5分钟
                        str(verification_code)
                    )
                
                # 发送邮件
                await self.email_service.send_mfa_setup_email(
                    email=user.email,
                    username=user.username,
                    code=str(verification_code)
                )
                
                return {
                    "type": mfa_type,
                    "message": "验证码已发送到您的邮箱",
                    "success": True
                }
            
        except Exception as e:
            logger.error(f"MFA设置失败: {str(e)}")
            raise ValueError(f"MFA设置失败: {str(e)}")
    
    async def verify_mfa(self, user: User, code: str, mfa_type: str = None) -> bool:
        """
        验证多因子认证代码
        
        Args:
            user: 用户对象
            code: 验证码
            mfa_type: MFA类型（可选，用于设置阶段）
        
        Returns:
            bool: 验证是否成功
        """
        logger.info(f"验证用户MFA: {user.id}")
        
        try:
            # 如果是设置阶段的验证
            if mfa_type:
                return await self._verify_mfa_setup(user, code, mfa_type)
            
            # 正常的MFA验证
            mfa_secret = await self.user_repo.get_user_mfa_secret(user.id)
            if not mfa_secret:
                raise ValueError("用户未启用MFA")
            
            if mfa_secret.mfa_type == MFATypeEnum.TOTP:
                # 验证TOTP代码
                totp = pyotp.TOTP(mfa_secret.secret)
                if totp.verify(code, valid_window=1):  # 允许前后30秒的时间窗口
                    return True
                
                # 检查是否是备用验证码
                if code.upper() in mfa_secret.backup_codes:
                    # 使用后移除备用验证码
                    await self.user_repo.use_backup_code(user.id, code.upper())
                    return True
                
                return False
            
            elif mfa_secret.mfa_type == MFATypeEnum.SMS:
                # 验证短信验证码
                if self.redis_client:
                    stored_code = await self.redis_client.get(f"mfa_verify:{user.id}:sms")
                    if stored_code and stored_code.decode() == code:
                        await self.redis_client.delete(f"mfa_verify:{user.id}:sms")
                        return True
                return False
            
            elif mfa_secret.mfa_type == MFATypeEnum.EMAIL:
                # 验证邮件验证码
                if self.redis_client:
                    stored_code = await self.redis_client.get(f"mfa_verify:{user.id}:email")
                    if stored_code and stored_code.decode() == code:
                        await self.redis_client.delete(f"mfa_verify:{user.id}:email")
                        return True
                return False
            
            return False
            
        except Exception as e:
            logger.error(f"MFA验证失败: {str(e)}")
            return False
    
    async def _verify_mfa_setup(self, user: User, code: str, mfa_type: str) -> bool:
        """验证MFA设置阶段的代码"""
        mfa_enum = MFATypeEnum(mfa_type.upper())
        
        if mfa_enum == MFATypeEnum.TOTP:
            # 获取临时保存的密钥
            mfa_setup = await self.user_repo.get_mfa_setup(user.id)
            if not mfa_setup:
                return False
            
            # 验证TOTP代码
            totp = pyotp.TOTP(mfa_setup.secret)
            if totp.verify(code, valid_window=1):
                # 正式启用MFA
                await self.user_repo.enable_mfa(user.id, mfa_setup)
                return True
            return False
        
        elif mfa_enum in [MFATypeEnum.SMS, MFATypeEnum.EMAIL]:
            # 验证验证码
            if self.redis_client:
                cache_key = f"mfa_setup:{user.id}:{mfa_type.lower()}"
                stored_code = await self.redis_client.get(cache_key)
                if stored_code and stored_code.decode() == code:
                    # 启用MFA
                    await self.user_repo.enable_simple_mfa(user.id, mfa_enum)
                    await self.redis_client.delete(cache_key)
                    return True
            return False
        
        return False
    
    async def disable_mfa(self, user: User) -> None:
        """
        禁用多因子认证
        
        Args:
            user: 用户对象
        """
        logger.info(f"禁用用户MFA: {user.id}")
        
        try:
            await self.user_repo.disable_mfa(user.id)
            
            # 记录MFA禁用事件
            await self.audit_repo.log_action(
                user_id=user.id,
                action="MFA_DISABLED",
                resource="auth",
                details={"method": "user_request"}
            )
            
        except Exception as e:
            logger.error(f"禁用MFA失败: {str(e)}")
            raise ValueError(f"禁用MFA失败: {str(e)}")
    
    async def _get_user_permissions(self, user: User) -> List[str]:
        """获取用户权限列表"""
        try:
            return await self.user_repo.get_user_permissions(user.id)
        except Exception as e:
            logger.error(f"获取用户权限失败: {str(e)}")
            return []
    
    async def _log_failed_login(self, username: str, ip_address: str, reason: str) -> None:
        """记录登录失败事件"""
        try:
            await self.audit_repo.log_action(
                user_id=None,
                action="LOGIN_FAILED",
                resource="auth",
                ip_address=ip_address,
                details={
                    "username": username,
                    "reason": reason
                }
            )
        except Exception as e:
            logger.error(f"记录登录失败事件失败: {str(e)}")


# 依赖注入函数
async def get_auth_service(
    db: AsyncSession = Depends(get_db_session),
    redis_client = Depends(get_redis_client)
) -> AuthService:
    """获取认证服务实例"""
    user_repo = UserRepository(db, redis_client)
    token_repo = TokenRepository(db, redis_client)
    audit_repo = AuditRepository(db)
    email_service = EmailService()
    sms_service = SMSService()
    password_manager = PasswordManager()
    
    return AuthService(
        user_repo=user_repo,
        token_repo=token_repo,
        audit_repo=audit_repo,
        email_service=email_service,
        sms_service=sms_service,
        password_manager=password_manager,
        redis_client=redis_client
    )


# 全局认证服务实例（用于向后兼容）
_auth_service_instance = None

async def get_auth_service_instance() -> AuthService:
    """获取全局认证服务实例"""
    global _auth_service_instance
    if _auth_service_instance is None:
        _auth_service_instance = await get_auth_service()
    return _auth_service_instance


# 向后兼容的函数
async def authenticate_user(username: str, password: str, ip_address: str = None) -> Optional[User]:
    """向后兼容的用户认证函数"""
    auth_service = await get_auth_service_instance()
    return await auth_service.authenticate_user(username, password, ip_address)


async def create_tokens(user: User, device_info: Dict[str, Any] = None) -> Dict[str, Any]:
    """向后兼容的令牌创建函数"""
    auth_service = await get_auth_service_instance()
    return await auth_service.create_tokens(user, device_info)


async def refresh_tokens(refresh_token: str, device_info: Dict[str, Any] = None) -> Dict[str, Any]:
    """向后兼容的令牌刷新函数"""
    auth_service = await get_auth_service_instance()
    return await auth_service.refresh_tokens(refresh_token, device_info)


async def logout(user: User, refresh_token: str = None) -> None:
    """向后兼容的登出函数"""
    auth_service = await get_auth_service_instance()
    return await auth_service.logout(user, refresh_token)


async def verify_token(token: str) -> User:
    """向后兼容的令牌验证函数"""
    auth_service = await get_auth_service_instance()
    return await auth_service.verify_token(token)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """向后兼容的当前用户获取函数"""
    auth_service = await get_auth_service_instance()
    return await auth_service.get_current_user(token)


async def send_password_reset(email: str, ip_address: str = None) -> None:
    """向后兼容的密码重置函数"""
    auth_service = await get_auth_service_instance()
    return await auth_service.send_password_reset(email, ip_address)


async def reset_password(token: str, new_password: str, ip_address: str = None) -> None:
    """向后兼容的密码重置函数"""
    auth_service = await get_auth_service_instance()
    return await auth_service.reset_password(token, new_password, ip_address)


async def setup_mfa(user: User, mfa_type: str) -> Dict[str, Any]:
    """向后兼容的MFA设置函数"""
    auth_service = await get_auth_service_instance()
    return await auth_service.setup_mfa(user, mfa_type)


async def verify_mfa(user: User, code: str, mfa_type: str = None) -> bool:
    """向后兼容的MFA验证函数"""
    auth_service = await get_auth_service_instance()
    return await auth_service.verify_mfa(user, code, mfa_type)


async def disable_mfa(user: User) -> None:
    """向后兼容的MFA禁用函数"""
    auth_service = await get_auth_service_instance()
    return await auth_service.disable_mfa(user)