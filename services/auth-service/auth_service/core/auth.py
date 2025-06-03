"""认证核心服务"""

import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

import pyotp
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.config.settings import get_settings
from auth_service.models.auth import LoginResult, MFADevice
from auth_service.models.user import User, UserSession


class AuthService:
    """认证服务核心类"""
    
    def __init__(self):
        self.settings = get_settings()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """生成密码哈希"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: Dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.settings.jwt.access_token_expire_minutes
            )
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": self.settings.jwt.issuer,
            "aud": self.settings.jwt.audience
        })
        
        return jwt.encode(
            to_encode, 
            self.settings.jwt.secret_key, 
            algorithm=self.settings.jwt.algorithm
        )
    
    def create_refresh_token(self) -> str:
        """创建刷新令牌"""
        return secrets.token_urlsafe(32)
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """验证令牌"""
        try:
            payload = jwt.decode(
                token,
                self.settings.jwt.secret_key,
                algorithms=[self.settings.jwt.algorithm],
                audience=self.settings.jwt.audience,
                issuer=self.settings.jwt.issuer
            )
            return payload
        except JWTError:
            return None
    
    async def authenticate_user(
        self, 
        db: AsyncSession, 
        username: str, 
        password: str
    ) -> Tuple[Optional[User], LoginResult]:
        """用户认证"""
        from auth_service.repositories.user_repository import UserRepository
        
        user_repo = UserRepository(db)
        user = await user_repo.get_by_username_or_email(username)
        
        if not user:
            return None, LoginResult.FAILED_INVALID_CREDENTIALS
        
        if not user.is_active_user():
            if user.is_locked():
                return None, LoginResult.FAILED_ACCOUNT_LOCKED
            else:
                return None, LoginResult.FAILED_ACCOUNT_DISABLED
        
        if not self.verify_password(password, user.password_hash):
            # 增加失败尝试次数
            await user_repo.increment_failed_attempts(user.id)
            return None, LoginResult.FAILED_INVALID_CREDENTIALS
        
        # 检查是否需要MFA
        if user.mfa_enabled:
            return user, LoginResult.FAILED_MFA_REQUIRED
        
        # 重置失败尝试次数
        await user_repo.reset_failed_attempts(user.id)
        
        return user, LoginResult.SUCCESS
    
    def generate_mfa_secret(self) -> str:
        """生成MFA密钥"""
        return pyotp.random_base32()
    
    def get_mfa_qr_code_url(self, user_email: str, secret: str) -> str:
        """获取MFA二维码URL"""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=user_email,
            issuer_name=self.settings.security.mfa_issuer_name
        )
    
    def verify_mfa_token(self, secret: str, token: str) -> bool:
        """验证MFA令牌"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
    
    async def create_user_session(
        self,
        db: AsyncSession,
        user: User,
        device_id: Optional[str] = None,
        device_name: Optional[str] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> UserSession:
        """创建用户会话"""
        from auth_service.repositories.session_repository import SessionRepository
        
        # 创建令牌
        access_token = self.create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )
        refresh_token = self.create_refresh_token()
        
        # 创建会话
        session_repo = SessionRepository(db)
        session = await session_repo.create_session(
            user_id=user.id,
            session_token=access_token,
            refresh_token=refresh_token,
            device_id=device_id,
            device_name=device_name,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=datetime.utcnow() + timedelta(
                minutes=self.settings.jwt.access_token_expire_minutes
            )
        )
        
        return session
    
    def validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """验证密码强度"""
        security = self.settings.security
        
        if len(password) < security.password_min_length:
            return False, f"密码长度至少需要{security.password_min_length}位"
        
        if security.password_require_uppercase and not any(c.isupper() for c in password):
            return False, "密码必须包含大写字母"
        
        if security.password_require_lowercase and not any(c.islower() for c in password):
            return False, "密码必须包含小写字母"
        
        if security.password_require_numbers and not any(c.isdigit() for c in password):
            return False, "密码必须包含数字"
        
        if security.password_require_symbols and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False, "密码必须包含特殊字符"
        
        return True, "密码强度符合要求" 