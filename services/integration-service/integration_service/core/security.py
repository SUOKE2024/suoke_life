"""
security - 索克生活项目模块
"""

from ..config import settings
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Any, Dict, Optional, Union
import jwt
import logging

"""
安全认证模块
"""




logger = logging.getLogger(__name__)

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer 认证
security = HTTPBearer()


class TokenData(BaseModel):
    """Token 数据模型"""
    user_id: Optional[str] = None
    username: Optional[str] = None
    scopes: list[str] = []


class Token(BaseModel):
    """Token 响应模型"""
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"密码验证失败: {e}")
        return False


def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"密码哈希失败: {e}")
        raise


def create_access_token(
    data: Dict[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.secret_key, 
            algorithm=settings.algorithm
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"创建访问令牌失败: {e}")
        raise


def create_refresh_token(
    data: Dict[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """创建刷新令牌"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)  # 默认7天
    
    to_encode.update({"exp": expire, "type": "refresh"})
    
    try:
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.secret_key, 
            algorithm=settings.algorithm
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"创建刷新令牌失败: {e}")
        raise


def verify_token(token: str) -> TokenData:
    """验证令牌"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            settings.secret_key, 
            algorithms=[settings.algorithm]
        )
        
        user_id: str = payload.get("sub")
        username: str = payload.get("username")
        scopes: list = payload.get("scopes", [])
        
        if user_id is None:
            raise credentials_exception
            
        token_data = TokenData(
            user_id=user_id,
            username=username,
            scopes=scopes
        )
        return token_data
        
    except jwt.PyJWTError as e:
        logger.error(f"JWT验证失败: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"令牌验证失败: {e}")
        raise credentials_exception


def verify_refresh_token(token: str) -> TokenData:
    """验证刷新令牌"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的刷新令牌",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            settings.secret_key, 
            algorithms=[settings.algorithm]
        )
        
        token_type: str = payload.get("type")
        if token_type != "refresh":
            raise credentials_exception
            
        user_id: str = payload.get("sub")
        username: str = payload.get("username")
        
        if user_id is None:
            raise credentials_exception
            
        token_data = TokenData(
            user_id=user_id,
            username=username
        )
        return token_data
        
    except jwt.PyJWTError as e:
        logger.error(f"刷新令牌验证失败: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"刷新令牌验证失败: {e}")
        raise credentials_exception


def create_token_pair(user_id: str, username: str, scopes: list[str] = None) -> Token:
    """创建令牌对（访问令牌和刷新令牌）"""
    if scopes is None:
        scopes = []
        
    token_data = {
        "sub": user_id,
        "username": username,
        "scopes": scopes
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"sub": user_id, "username": username})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        refresh_token=refresh_token
    )


class OAuth2PasswordBearerWithCookie:
    """支持Cookie的OAuth2密码Bearer认证"""
    
    def __init__(self, tokenUrl: str, scheme_name: str = None, auto_error: bool = True):
        self.tokenUrl = tokenUrl
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error
    
    async def __call__(self, request) -> Optional[str]:
        """从请求中提取令牌"""
        authorization: str = request.headers.get("Authorization")
        scheme, param = None, None
        
        if authorization:
            scheme, param = authorization.split(" ", 1) if " " in authorization else (authorization, "")
        
        if scheme and scheme.lower() == "bearer":
            return param
        
        # 尝试从Cookie中获取令牌
        token = request.cookies.get("access_token")
        if token:
            return token
        
        if self.auto_error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="未提供有效的认证凭据",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return None


# OAuth2 认证实例
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/auth/token")


def generate_api_key(user_id: str, platform_id: str) -> str:
    """生成API密钥"""
    data = {
        "user_id": user_id,
        "platform_id": platform_id,
        "type": "api_key",
        "iat": datetime.utcnow().timestamp()
    }
    
    try:
        api_key = jwt.encode(
            data,
            settings.secret_key,
            algorithm=settings.algorithm
        )
        return api_key
    except Exception as e:
        logger.error(f"生成API密钥失败: {e}")
        raise


def verify_api_key(api_key: str) -> Dict[str, Any]:
    """验证API密钥"""
    try:
        payload = jwt.decode(
            api_key,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        
        if payload.get("type") != "api_key":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的API密钥类型"
            )
        
        return payload
        
    except jwt.PyJWTError as e:
        logger.error(f"API密钥验证失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的API密钥"
        )


def encrypt_sensitive_data(data: str) -> str:
    """加密敏感数据"""
    # 这里可以使用更强的加密算法，如AES
    # 为了简化，这里使用JWT
    try:
        encrypted = jwt.encode(
            {"data": data},
            settings.secret_key,
            algorithm=settings.algorithm
        )
        return encrypted
    except Exception as e:
        logger.error(f"数据加密失败: {e}")
        raise


def decrypt_sensitive_data(encrypted_data: str) -> str:
    """解密敏感数据"""
    try:
        payload = jwt.decode(
            encrypted_data,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload.get("data")
    except Exception as e:
        logger.error(f"数据解密失败: {e}")
        raise 