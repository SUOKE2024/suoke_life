"""认证相关API端点"""

from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.core.auth import AuthService
from auth_service.core.database import get_db
from auth_service.models.auth import LoginResult
from auth_service.repositories.user_repository import UserRepository
from auth_service.repositories.session_repository import SessionRepository
from auth_service.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    LogoutRequest,
    MFASetupResponse,
    MFAVerifyRequest,
    SessionListResponse,
    SessionInfo,
)

router = APIRouter()
security = HTTPBearer()


def get_auth_service() -> AuthService:
    """获取认证服务实例"""
    return AuthService()


def get_client_ip(request: Request) -> str:
    """获取客户端IP地址"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host


def get_user_agent(request: Request) -> str:
    """获取用户代理"""
    return request.headers.get("User-Agent", "")


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """用户登录"""
    # 获取客户端信息
    ip_address = get_client_ip(http_request)
    user_agent = get_user_agent(http_request)
    
    # 用户认证
    user, result = await auth_service.authenticate_user(
        db, request.username, request.password
    )
    
    if result == LoginResult.FAILED_INVALID_CREDENTIALS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    elif result == LoginResult.FAILED_ACCOUNT_LOCKED:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="账户已被锁定，请稍后再试"
        )
    elif result == LoginResult.FAILED_ACCOUNT_DISABLED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用"
        )
    elif result == LoginResult.FAILED_MFA_REQUIRED:
        return LoginResponse(
            access_token="",
            refresh_token="",
            token_type="bearer",
            expires_in=0,
            user_id=str(user.id),
            username=user.username,
            mfa_required=True
        )
    
    # 创建会话
    session = await auth_service.create_user_session(
        db=db,
        user=user,
        device_id=request.device_id,
        device_name=request.device_name,
        user_agent=user_agent,
        ip_address=ip_address
    )
    
    # 更新最后登录信息
    user_repo = UserRepository(db)
    await user_repo.update_last_login(user.id, ip_address)
    
    return LoginResponse(
        access_token=session.session_token,
        refresh_token=session.refresh_token,
        token_type="bearer",
        expires_in=auth_service.settings.jwt.access_token_expire_minutes * 60,
        user_id=str(user.id),
        username=user.username,
        mfa_required=False
    )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """刷新访问令牌"""
    session_repo = SessionRepository(db)
    session = await session_repo.get_by_refresh_token(request.refresh_token)
    
    if not session or not session.is_valid():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌"
        )
    
    # 创建新的令牌
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(session.user_id)
    
    if not user or not user.is_active_user():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户账户无效"
        )
    
    # 生成新令牌
    new_access_token = auth_service.create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )
    new_refresh_token = auth_service.create_refresh_token()
    new_expires_at = session.expires_at + timedelta(
        minutes=auth_service.settings.jwt.access_token_expire_minutes
    )
    
    # 更新会话
    await session_repo.refresh_session(
        session.id,
        new_access_token,
        new_refresh_token,
        new_expires_at
    )
    
    return RefreshTokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=auth_service.settings.jwt.access_token_expire_minutes * 60
    )


@router.post("/logout")
async def logout(
    request: LogoutRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """用户登出"""
    # 验证令牌
    payload = auth_service.verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌"
        )
    
    user_id = payload.get("sub")
    session_repo = SessionRepository(db)
    
    if request.all_devices:
        # 登出所有设备
        await session_repo.deactivate_user_sessions(user_id)
    else:
        # 只登出当前设备
        session = await session_repo.get_by_session_token(credentials.credentials)
        if session:
            await session_repo.deactivate_session(session.id)
    
    return {"message": "登出成功"}


@router.post("/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """设置MFA"""
    # 验证令牌
    payload = auth_service.verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌"
        )
    
    user_id = payload.get("sub")
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 生成MFA密钥
    secret = auth_service.generate_mfa_secret()
    qr_code_url = auth_service.get_mfa_qr_code_url(user.email, secret)
    
    # 生成备用代码
    backup_codes = [auth_service.create_refresh_token()[:8] for _ in range(10)]
    
    return MFASetupResponse(
        secret=secret,
        qr_code_url=qr_code_url,
        backup_codes=backup_codes
    )


@router.post("/mfa/verify")
async def verify_mfa(
    request: MFAVerifyRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """验证MFA"""
    # 验证令牌
    payload = auth_service.verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌"
        )
    
    user_id = payload.get("sub")
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    
    if not user or not user.mfa_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA未设置"
        )
    
    # 验证MFA令牌
    if not auth_service.verify_mfa_token(user.mfa_secret, request.token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA令牌无效"
        )
    
    # 启用MFA
    await user_repo.enable_mfa(user.id, user.mfa_secret)
    
    return {"message": "MFA验证成功"}


@router.get("/sessions", response_model=SessionListResponse)
async def get_user_sessions(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """获取用户会话列表"""
    # 验证令牌
    payload = auth_service.verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌"
        )
    
    user_id = payload.get("sub")
    session_repo = SessionRepository(db)
    sessions = await session_repo.get_user_sessions(user_id)
    
    # 获取当前会话
    current_session = await session_repo.get_by_session_token(credentials.credentials)
    current_session_id = current_session.id if current_session else None
    
    session_infos = [
        SessionInfo(
            session_id=str(session.id),
            device_name=session.device_name,
            ip_address=session.ip_address,
            location=session.location,
            created_at=session.created_at,
            last_activity_at=session.last_activity_at,
            is_current=session.id == current_session_id
        )
        for session in sessions
    ]
    
    return SessionListResponse(
        sessions=session_infos,
        total=len(session_infos)
    ) 