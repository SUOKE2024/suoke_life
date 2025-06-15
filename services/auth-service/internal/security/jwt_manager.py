"""
JWT密钥管理器

支持RS256算法的JWT令牌管理，包括密钥生成、加载和验证。
"""
import logging
from pathlib import Path
from typing import Optional, Union
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

from internal.config.settings import get_settings

logger = logging.getLogger(__name__)


class JWTKeyManager:
    """JWT密钥管理器"""
    
    def __init__(self):
        self.settings = get_settings()
        self._private_key: Optional[rsa.RSAPrivateKey] = None
        self._public_key: Optional[rsa.RSAPublicKey] = None
        self._private_key_pem: Optional[bytes] = None
        self._public_key_pem: Optional[bytes] = None
        
        # 初始化密钥
        self._load_keys()
    
    def _load_keys(self):
        """加载RSA密钥对"""
        try:
            # 优先从文件路径加载
            if self.settings.jwt_private_key_path and self.settings.jwt_public_key_path:
                self._load_keys_from_files()
            # 其次从配置内容加载
            elif self.settings.jwt_private_key and self.settings.jwt_public_key:
                self._load_keys_from_config()
            # 最后生成新密钥对
            else:
                logger.warning("未找到RSA密钥配置，将生成新的密钥对")
                self._generate_key_pair()
                
        except Exception as e:
            logger.error(f"加载RSA密钥失败: {e}")
            # 回退到生成新密钥对
            self._generate_key_pair()
    
    def _load_keys_from_files(self):
        """从文件加载密钥"""
        try:
            # 加载私钥
            private_key_path = Path(self.settings.jwt_private_key_path)
            if private_key_path.exists():
                with open(private_key_path, 'rb') as f:
                    self._private_key_pem = f.read()
                    self._private_key = serialization.load_pem_private_key(
                        self._private_key_pem,
                        password=None,
                        backend=default_backend()
                    )
            
            # 加载公钥
            public_key_path = Path(self.settings.jwt_public_key_path)
            if public_key_path.exists():
                with open(public_key_path, 'rb') as f:
                    self._public_key_pem = f.read()
                    self._public_key = serialization.load_pem_public_key(
                        self._public_key_pem,
                        backend=default_backend()
                    )
            
            logger.info("从文件成功加载RSA密钥对")
            
        except Exception as e:
            logger.error(f"从文件加载密钥失败: {e}")
            raise
    
    def _load_keys_from_config(self):
        """从配置加载密钥"""
        try:
            # 加载私钥
            if self.settings.jwt_private_key:
                self._private_key_pem = self.settings.jwt_private_key.encode()
                self._private_key = serialization.load_pem_private_key(
                    self._private_key_pem,
                    password=None,
                    backend=default_backend()
                )
            
            # 加载公钥
            if self.settings.jwt_public_key:
                self._public_key_pem = self.settings.jwt_public_key.encode()
                self._public_key = serialization.load_pem_public_key(
                    self._public_key_pem,
                    backend=default_backend()
                )
            
            logger.info("从配置成功加载RSA密钥对")
            
        except Exception as e:
            logger.error(f"从配置加载密钥失败: {e}")
            raise
    
    def _generate_key_pair(self):
        """生成新的RSA密钥对"""
        try:
            # 生成私钥
            self._private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            
            # 获取公钥
            self._public_key = self._private_key.public_key()
            
            # 序列化密钥
            self._private_key_pem = self._private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            self._public_key_pem = self._public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            logger.warning("生成了新的RSA密钥对，建议保存到配置文件中")
            logger.info("RSA密钥对已生成，请通过安全方式获取密钥内容")
            # 注意：出于安全考虑，不在日志中输出私钥内容
            
        except Exception as e:
            logger.error(f"生成RSA密钥对失败: {e}")
            raise
    
    def get_private_key(self) -> Union[rsa.RSAPrivateKey, bytes, str]:
        """获取私钥"""
        if self.settings.jwt_algorithm == "RS256":
            return self._private_key
        else:
            # 对于HS256等对称算法，返回密钥字符串
            return self.settings.jwt_secret_key
    
    def get_public_key(self) -> Union[rsa.RSAPublicKey, bytes, str]:
        """获取公钥"""
        if self.settings.jwt_algorithm == "RS256":
            return self._public_key
        else:
            # 对于HS256等对称算法，返回密钥字符串
            return self.settings.jwt_secret_key
    
    def get_private_key_pem(self) -> Optional[str]:
        """获取PEM格式的私钥"""
        if self._private_key_pem:
            return self._private_key_pem.decode()
        return None
    
    def get_public_key_pem(self) -> Optional[str]:
        """获取PEM格式的公钥"""
        if self._public_key_pem:
            return self._public_key_pem.decode()
        return None
    
    def save_keys_to_files(self, private_key_path: str, public_key_path: str):
        """保存密钥到文件"""
        try:
            # 保存私钥
            with open(private_key_path, 'wb') as f:
                f.write(self._private_key_pem)
            
            # 保存公钥
            with open(public_key_path, 'wb') as f:
                f.write(self._public_key_pem)
            
            logger.info(f"密钥已保存到文件: {private_key_path}, {public_key_path}")
            
        except Exception as e:
            logger.error(f"保存密钥到文件失败: {e}")
            raise


# 全局密钥管理器实例
import threading
_key_manager: Optional[JWTKeyManager] = None
_lock = threading.Lock()


def get_jwt_key_manager() -> JWTKeyManager:
    """获取JWT密钥管理器实例（线程安全的单例模式）"""
    global _key_manager
    if _key_manager is None:
        with _lock:
            # 双重检查锁定模式
            if _key_manager is None:
                _key_manager = JWTKeyManager()
    return _key_manager


def reload_jwt_keys():
    """重新加载JWT密钥（线程安全）"""
    global _key_manager
    with _lock:
        _key_manager = JWTKeyManager()
    return _key_manager 


class JWTManager:
    """JWT管理器类 - 兼容性包装器"""
    
    def __init__(self):
        self.key_manager = get_jwt_key_manager()
    
    def create_tokens(self, user_data: dict) -> dict:
        """创建访问令牌和刷新令牌"""
        from datetime import datetime, timedelta
        import jwt
        import secrets
        from internal.config.settings import get_settings
        
        settings = get_settings()
        
        # 创建访问令牌
        access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
        access_payload = {
            **user_data,
            "type": "access",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + access_token_expires,
            "iss": "suoke-auth-service"
        }
        
        access_token = jwt.encode(
            access_payload,
            self.key_manager.get_private_key(),
            algorithm=settings.jwt_algorithm
        )
        
        # 创建刷新令牌
        refresh_token_expires = timedelta(days=settings.jwt_refresh_token_expire_days)
        refresh_payload = {
            "sub": user_data.get("sub"),
            "type": "refresh",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + refresh_token_expires,
            "iss": "suoke-auth-service",
            "jti": secrets.token_urlsafe(32)
        }
        
        refresh_token = jwt.encode(
            refresh_payload,
            self.key_manager.get_private_key(),
            algorithm=settings.jwt_algorithm
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.jwt_access_token_expire_minutes * 60
        }
    
    def verify_token(self, token: str) -> dict:
        """验证JWT令牌"""
        import jwt
        from internal.config.settings import get_settings
        
        settings = get_settings()
        
        try:
            payload = jwt.decode(
                token,
                self.key_manager.get_public_key(),
                algorithms=[settings.jwt_algorithm],
                issuer="suoke-auth-service"
            )
            return payload
        except jwt.ExpiredSignatureError:
            from internal.exceptions import TokenExpiredError
            raise TokenExpiredError("令牌已过期")
        except jwt.InvalidTokenError:
            from internal.exceptions import TokenInvalidError
            raise TokenInvalidError("无效的令牌")


# 兼容性别名
JWTKeyManager = JWTKeyManager
