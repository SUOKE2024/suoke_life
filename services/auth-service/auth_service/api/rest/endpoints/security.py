"""安全相关API端点"""

import uuid
import secrets
from typing import Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.core.auth import AuthService
from auth_service.core.database import get_db
from auth_service.core.email import EmailService
from auth_service.core.redis import get_redis
from auth_service.config.settings import get_settings
from auth_service.repositories.user_repository import UserRepository
from auth_service.repositories.session_repository import SessionRepository
from auth_service.schemas.auth import (
    PasswordResetRequest,
    PasswordResetConfirmRequest,
    EmailVerificationRequest,
    EmailVerificationConfirmRequest,
)

router = APIRouter()
security = HTTPBearer()
auth_service = AuthService()
settings = get_settings()
email_service = EmailService(settings.email)


@router.post("/password-reset")
async def request_password_reset(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
):
    """请求密码重置"""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(request.email)
    
    if not user:
        # 为了安全，即使用户不存在也返回成功
        return {"message": "如果邮箱存在，重置链接已发送"}
    
    try:
        # 生成重置令牌
        reset_token = secrets.token_urlsafe(32)
        
        # 存储令牌到Redis，24小时过期
        reset_key = f"password_reset:{reset_token}"
        await redis.setex(
            reset_key,
            timedelta(hours=24),
            str(user.id)
        )
        
        # 发送密码重置邮件
        await email_service.send_password_reset_email(
            to_email=user.email,
            username=user.username,
            reset_token=reset_token
        )
        
        return {"message": "如果邮箱存在，重置链接已发送"}
        
    except Exception as e:
        # 记录错误但不暴露给用户
        import structlog
        logger = structlog.get_logger()
        logger.error("Failed to send password reset email", error=str(e), email=request.email)
        return {"message": "如果邮箱存在，重置链接已发送"}


@router.post("/password-reset/confirm")
async def confirm_password_reset(
    request: PasswordResetConfirmRequest,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
):
    """确认密码重置"""
    try:
        # 验证重置令牌
        reset_key = f"password_reset:{request.token}"
        user_id_str = await redis.get(reset_key)
        
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="重置令牌无效或已过期"
            )
        
        # 验证新密码强度
        is_valid, message = auth_service.validate_password_strength(request.new_password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        # 获取用户
        user_repo = UserRepository(db)
        user_id = uuid.UUID(user_id_str.decode())
        user = await user_repo.get_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户不存在"
            )
        
        # 更新密码
        new_password_hash = auth_service.get_password_hash(request.new_password)
        await user_repo.update_password(user.id, new_password_hash)
        
        # 删除重置令牌
        await redis.delete(reset_key)
        
        # 清除所有用户会话（强制重新登录）
        session_repo = SessionRepository(db)
        await session_repo.deactivate_user_sessions(user.id)
        
        return {"message": "密码重置成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        import structlog
        logger = structlog.get_logger()
        logger.error("Failed to reset password", error=str(e), token=request.token)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="密码重置失败"
        )


@router.post("/email-verification")
async def request_email_verification(
    request: EmailVerificationRequest,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
):
    """请求邮箱验证"""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(request.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已验证"
        )
    
    try:
        # 生成验证令牌
        verification_token = secrets.token_urlsafe(32)
        
        # 存储令牌到Redis，24小时过期
        verification_key = f"email_verification:{verification_token}"
        await redis.setex(
            verification_key,
            timedelta(hours=24),
            str(user.id)
        )
        
        # 发送邮箱验证邮件
        await email_service.send_verification_email(
            to_email=user.email,
            username=user.username,
            verification_token=verification_token
        )
        
        return {"message": "验证邮件已发送"}
        
    except Exception as e:
        # 记录错误但不暴露给用户
        import structlog
        logger = structlog.get_logger()
        logger.error("Failed to send verification email", error=str(e), email=request.email)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="发送验证邮件失败"
        )


@router.post("/email-verification/confirm")
async def confirm_email_verification(
    request: EmailVerificationConfirmRequest,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
):
    """确认邮箱验证"""
    try:
        # 验证令牌
        verification_key = f"email_verification:{request.token}"
        user_id_str = await redis.get(verification_key)
        
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="验证令牌无效或已过期"
            )
        
        # 获取用户
        user_repo = UserRepository(db)
        user_id = uuid.UUID(user_id_str.decode())
        user = await user_repo.get_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户不存在"
            )
        
        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已验证"
            )
        
        # 更新用户验证状态
        await user_repo.verify_email(user.id)
        
        # 删除验证令牌
        await redis.delete(verification_key)
        
        # 发送欢迎邮件
        try:
            await email_service.send_welcome_email(
                to_email=user.email,
                username=user.username
            )
        except Exception as e:
            # 欢迎邮件发送失败不影响验证流程
            import structlog
            logger = structlog.get_logger()
            logger.warning("Failed to send welcome email", error=str(e), user_id=str(user.id))
        
        return {"message": "邮箱验证成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        import structlog
        logger = structlog.get_logger()
        logger.error("Failed to verify email", error=str(e), token=request.token)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="邮箱验证失败"
        )


@router.post("/sessions/cleanup")
async def cleanup_expired_sessions(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """清理过期会话（管理员功能）"""
    # 验证令牌
    payload = auth_service.verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌"
        )
    
    user_id = payload.get("sub")
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(uuid.UUID(user_id))
    
    if not user or not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    session_repo = SessionRepository(db)
    cleaned_count = await session_repo.cleanup_expired_sessions()
    
    return {"message": f"已清理 {cleaned_count} 个过期会话"}


@router.delete("/sessions/{session_id}")
async def terminate_session(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """终止指定会话"""
    # 验证令牌
    payload = auth_service.verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌"
        )
    
    user_id = payload.get("sub")
    session_repo = SessionRepository(db)
    
    # 检查会话是否属于当前用户
    sessions = await session_repo.get_user_sessions(uuid.UUID(user_id))
    target_session = None
    
    for session in sessions:
        if str(session.id) == session_id:
            target_session = session
            break
    
    if not target_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在或无权限"
        )
    
    # 终止会话
    await session_repo.deactivate_session(target_session.id)
    
    return {"message": "会话已终止"}


@router.get("/audit/login-attempts")
async def get_login_attempts(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
    limit: int = 50
):
    """获取登录尝试记录（管理员功能）"""
    # 验证令牌
    payload = auth_service.verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌"
        )
    
    user_id = payload.get("sub")
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(uuid.UUID(user_id))
    
    if not user or not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # TODO: 实现获取登录尝试记录的逻辑
    # 这需要在登录时记录尝试信息
    
    return {"message": "功能开发中"}


@router.post("/lockout/unlock/{user_id}")
async def unlock_user_account(
    user_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """解锁用户账户（管理员功能）"""
    # 验证令牌
    payload = auth_service.verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌"
        )
    
    current_user_id = payload.get("sub")
    user_repo = UserRepository(db)
    current_user = await user_repo.get_by_id(uuid.UUID(current_user_id))
    
    if not current_user or not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 解锁用户
    await user_repo.reset_failed_attempts(uuid.UUID(user_id))
    
    return {"message": "用户账户已解锁"}


@router.get("/security-settings")
async def get_security_settings(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """获取安全设置"""
    # 验证令牌
    payload = auth_service.verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌"
        )
    
    user_id = payload.get("sub")
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(uuid.UUID(user_id))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return {
        "mfa_enabled": user.mfa_enabled,
        "password_changed_at": user.password_changed_at,
        "failed_login_attempts": user.failed_login_attempts,
        "locked_until": user.locked_until,
        "last_login_at": user.last_login_at,
        "last_login_ip": user.last_login_ip
    } 