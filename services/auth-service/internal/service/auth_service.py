#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
认证服务核心业务逻辑模块

提供用户认证、授权、令牌管理、密码重置和多因素认证等核心功能。
"""
import os
import uuid
import jwt
import pyotp
import qrcode
import base64
from io import BytesIO
from datetime import datetime, timedelta, UTC
from typing import Dict, Optional, List, Any, Tuple

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from ..model.user import User, RefreshToken, AuditLog, MFATypeEnum, UserStatusEnum
from ..repository.user_repository import UserRepository
from ..repository.token_repository import TokenRepository
from ..repository.audit_repository import AuditRepository
from ..db.session import get_session
from ..schemas.auth import TokenResponse, MFASetupResponse

# 配置
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "suoke_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))
MFA_ISSUER = "索克生活APP"

# 工具初始化
pwd_context = CryptContext(
    schemes=["bcrypt", "sha256_crypt"],
    default="bcrypt",
    bcrypt__rounds=12,  # 工作因子，增加安全性
    sha256_crypt__rounds=100000,  # 足够强度的备用哈希
    deprecated=["auto"]  # 自动弃用不安全的哈希
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    """获取当前用户（从JWT令牌）"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="凭证无效",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 解码JWT令牌
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # 获取用户
        user_repo = UserRepository(session)
        user = await user_repo.get_user_by_id(user_id)
        
        # 检查用户状态
        if user is None or user.status != UserStatusEnum.ACTIVE:
            raise credentials_exception
            
        return user
    except jwt.PyJWTError:
        raise credentials_exception


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


async def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)


async def authenticate_user(
    username: str,
    password: str,
    session: AsyncSession = Depends(get_session),
) -> Optional[User]:
    """认证用户（用户名+密码）"""
    user_repo = UserRepository(session)
    audit_repo = AuditRepository(session)
    
    # 查找用户
    user = await user_repo.get_user_by_username(username)
    if not user:
        # 记录登录失败日志
        ip_address = "0.0.0.0"  # 实际应用中应获取真实IP
        await audit_repo.add_login_attempt(None, ip_address, False)
        return None
    
    # 验证密码
    if not await verify_password(password, user.password_hash):
        # 记录登录失败日志
        ip_address = "0.0.0.0"  # 实际应用中应获取真实IP
        await audit_repo.add_login_attempt(user.id, ip_address, False)
        
        # 检查失败次数并锁定账户
        failed_attempts = await audit_repo.get_recent_failed_attempts(user.id, minutes=30)
        if len(failed_attempts) >= 5:  # 30分钟内5次失败尝试则锁定账户
            user.status = UserStatusEnum.LOCKED
            await session.commit()
            
        return None
    
    # 检查用户状态
    if user.status != UserStatusEnum.ACTIVE:
        return None
    
    # 记录登录成功
    ip_address = "0.0.0.0"  # 实际应用中应获取真实IP
    await audit_repo.add_login_attempt(user.id, ip_address, True)
    
    # 更新最后登录时间
    user.last_login = datetime.now(UTC)
    await session.commit()
    
    return user


async def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    
    # 设置过期时间
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # 创建JWT令牌
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def create_refresh_token(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> Tuple[str, datetime]:
    """创建刷新令牌"""
    # 调用仓储创建刷新令牌
    token_repo = TokenRepository(session)
    result = await token_repo.create_refresh_token(str(user_id), expires_days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    return result["token_value"], result["expires_at"]


async def create_tokens(
    user: User,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    """创建访问令牌和刷新令牌"""
    # 获取用户权限列表
    permissions = []
    for role in user.roles:
        for permission in role.permissions:
            permissions.append(f"{permission.resource}:{permission.action}")
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": str(user.id), "username": user.username, "permissions": permissions},
        expires_delta=access_token_expires,
    )
    
    # 创建刷新令牌
    refresh_token, refresh_expires = await create_refresh_token(user.id, session)
    
    # 生成响应
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_expires_in=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )


async def refresh_tokens(
    refresh_token: str,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    """刷新访问令牌"""
    token_repo = TokenRepository(session)
    user_repo = UserRepository(session)
    
    # 验证刷新令牌
    token = await token_repo.get_refresh_token(refresh_token)
    if not token or token.revoked or token.expires_at < datetime.now(UTC):
        raise ValueError("刷新令牌无效或已过期")
    
    # 获取用户
    user = await user_repo.get_user_by_id(str(token.user_id))
    if not user or user.status != UserStatusEnum.ACTIVE:
        raise ValueError("用户不存在或已被禁用")
    
    # 创建新令牌
    return await create_tokens(user, session)


async def logout(
    user: User,
    session: AsyncSession = Depends(get_session),
) -> bool:
    """用户登出，吊销所有刷新令牌"""
    token_repo = TokenRepository(session)
    return await token_repo.revoke_all_user_tokens(user.id)


async def verify_token(
    token: str,
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """验证访问令牌有效性，返回用户信息"""
    try:
        # 解码JWT令牌
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise ValueError("无效的令牌")
        
        # 检查用户是否存在
        user_repo = UserRepository(session)
        user = await user_repo.get_user_by_id(user_id)
        if user is None or user.status != UserStatusEnum.ACTIVE:
            raise ValueError("用户不存在或已被禁用")
        
        # 提取并返回用户信息
        return {
            "id": user_id,
            "username": user.username,
            "email": user.email,
            "permissions": payload.get("permissions", []),
        }
    except jwt.PyJWTError as e:
        raise ValueError(f"令牌验证失败: {str(e)}")


async def send_password_reset(
    email: str,
    session: AsyncSession = Depends(get_session),
) -> bool:
    """发送密码重置邮件"""
    user_repo = UserRepository(session)
    
    # 查找用户
    user = await user_repo.get_user_by_email(email)
    if not user:
        # 不暴露用户是否存在
        return True
    
    # 创建重置令牌
    token_data = {
        "sub": str(user.id),
        "type": "password_reset",
    }
    token = await create_access_token(token_data, timedelta(hours=1))
    
    # TODO: 实际发送邮件
    # 这里应集成邮件发送服务
    print(f"[模拟] 发送密码重置邮件到: {email}，令牌: {token}")
    
    return True


async def reset_password(
    token: str,
    new_password: str,
    session: AsyncSession = Depends(get_session),
) -> bool:
    """重置密码"""
    user_repo = UserRepository(session)
    
    try:
        # 验证令牌
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 检查令牌类型
        if payload.get("type") != "password_reset":
            raise ValueError("无效的令牌类型")
        
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("无效的令牌")
        
        # 获取用户
        user = await user_repo.get_user_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")
        
        # 更新密码
        password_hash = await get_password_hash(new_password)
        await user_repo.update_password(user_id, password_hash)
        
        # 吊销所有刷新令牌
        token_repo = TokenRepository(session)
        await token_repo.revoke_all_user_tokens(user.id)
        
        return True
    except jwt.PyJWTError:
        raise ValueError("无效或已过期的令牌")


async def setup_mfa(
    user: User,
    mfa_type: str,
    session: AsyncSession = Depends(get_session),
) -> MFASetupResponse:
    """设置多因素认证"""
    user_repo = UserRepository(session)
    
    # 验证MFA类型
    try:
        mfa_type_enum = MFATypeEnum(mfa_type)
    except ValueError:
        raise ValueError(f"不支持的多因素认证类型: {mfa_type}")
    
    # 根据类型设置MFA
    if mfa_type_enum == MFATypeEnum.TOTP:
        # 生成TOTP密钥
        secret = pyotp.random_base32()
        provisioning_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.email,
            issuer_name=MFA_ISSUER
        )
        
        # 生成QR码
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 转换QR码为base64
        buffered = BytesIO()
        img.save(buffered)
        qr_code_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # 保存MFA设置
        await user_repo.update_mfa_settings(
            user_id=str(user.id),
            mfa_enabled=True,
            mfa_type=mfa_type_enum,
            mfa_secret=secret,
        )
        
        return MFASetupResponse(
            type="totp",
            secret=secret,
            qr_code=f"data:image/png;base64,{qr_code_base64}",
            success=True,
        )
        
    elif mfa_type_enum == MFATypeEnum.SMS:
        # TODO: 实现SMS验证码多因素认证
        # 此处应集成短信服务
        raise ValueError("SMS多因素认证暂未实现")
        
    elif mfa_type_enum == MFATypeEnum.EMAIL:
        # TODO: 实现邮件验证码多因素认证
        # 此处应集成邮件服务
        raise ValueError("邮件多因素认证暂未实现")
        
    else:
        raise ValueError(f"不支持的多因素认证类型: {mfa_type}")


async def verify_mfa(
    user: User,
    code: str,
    session: AsyncSession = Depends(get_session),
) -> bool:
    """验证多因素认证代码"""
    # 检查用户是否启用MFA
    if not user.mfa_enabled or user.mfa_type == MFATypeEnum.NONE:
        raise ValueError("未启用多因素认证")
    
    # 根据MFA类型验证
    if user.mfa_type == MFATypeEnum.TOTP:
        # 验证TOTP代码
        totp = pyotp.TOTP(user.mfa_secret)
        return totp.verify(code)
        
    elif user.mfa_type == MFATypeEnum.SMS:
        # TODO: 实现SMS验证码验证
        raise ValueError("SMS多因素认证暂未实现")
        
    elif user.mfa_type == MFATypeEnum.EMAIL:
        # TODO: 实现邮件验证码验证
        raise ValueError("邮件多因素认证暂未实现")
        
    else:
        raise ValueError(f"不支持的多因素认证类型: {user.mfa_type}")


async def disable_mfa(
    user: User,
    session: AsyncSession = Depends(get_session),
) -> bool:
    """禁用多因素认证"""
    user_repo = UserRepository(session)
    
    # 检查MFA是否已启用
    if not user.mfa_enabled or user.mfa_type == MFATypeEnum.NONE:
        raise ValueError("多因素认证未启用")
    
    # 禁用MFA
    await user_repo.update_mfa_settings(
        user_id=str(user.id),
        mfa_enabled=False,
        mfa_type=MFATypeEnum.NONE,
        mfa_secret=None,
    )
    
    # 记录审计日志
    audit_repo = AuditRepository(session)
    await audit_repo.add_audit_log(
        user_id=user.id,
        action="disable_mfa",
        resource="user",
        resource_id=str(user.id),
        details="禁用多因素认证",
    )
    
    return True


async def log_audit_event(
    user_id: Optional[uuid.UUID],
    action: str,
    resource: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
) -> None:
    """记录审计日志"""
    audit_repo = AuditRepository(session)
    await audit_repo.add_audit_log(
        user_id=user_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
    ) 