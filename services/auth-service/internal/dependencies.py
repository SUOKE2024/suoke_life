#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
依赖注入容器

管理服务间的依赖关系，提供统一的服务实例化接口。
"""
from typing import Optional, Dict, Any
from functools import lru_cache

from .config.settings import get_settings
from .security.jwt_manager import JWTManager, get_jwt_key_manager
from .security.password import PasswordManager
from .database.connection_manager import get_connection_manager
from .cache.redis_cache import get_redis_cache


class ServiceDependencies:
    """服务依赖容器"""
    
    def __init__(self):
        self.settings = get_settings()
        self._jwt_manager: Optional[JWTManager] = None
        self._password_manager: Optional[PasswordManager] = None
        self._db_manager = None
        self._cache = None
        
    @property
    def jwt_manager(self) -> JWTManager:
        """获取JWT管理器"""
        if self._jwt_manager is None:
            self._jwt_manager = JWTManager()
        return self._jwt_manager
    
    @property
    def password_manager(self) -> PasswordManager:
        """获取密码管理器"""
        if self._password_manager is None:
            self._password_manager = PasswordManager()
        return self._password_manager
    
    @property
    def db_manager(self):
        """获取数据库管理器"""
        if self._db_manager is None:
            self._db_manager = get_connection_manager()
        return self._db_manager
    
    @property
    def cache(self):
        """获取缓存管理器"""
        if self._cache is None:
            self._cache = get_redis_cache()
        return self._cache


# 全局依赖容器实例
_dependencies: Optional[ServiceDependencies] = None


@lru_cache()
def get_dependencies() -> ServiceDependencies:
    """获取依赖容器实例（单例模式）"""
    global _dependencies
    if _dependencies is None:
        _dependencies = ServiceDependencies()
    return _dependencies


# 服务工厂函数
def create_auth_service():
    """创建认证服务实例"""
    from .service.auth_service import AuthService
    deps = get_dependencies()
    return AuthService(deps)


def create_social_auth_service():
    """创建社交认证服务实例"""
    from .service.social_auth_service import SocialAuthService
    deps = get_dependencies()
    return SocialAuthService(deps)


def create_blockchain_auth_service():
    """创建区块链认证服务实例"""
    from .service.blockchain_auth_service import BlockchainAuthService
    deps = get_dependencies()
    return BlockchainAuthService(deps)


def create_biometric_auth_service():
    """创建生物识别认证服务实例"""
    from .service.biometric_auth_service import BiometricAuthService
    deps = get_dependencies()
    return BiometricAuthService(deps)


def create_mfa_service():
    """创建MFA服务实例"""
    from .service.mfa_service import MFAService
    deps = get_dependencies()
    return MFAService(deps)


def create_user_service():
    """创建用户服务实例"""
    from .service.user_service import UserService
    deps = get_dependencies()
    return UserService(deps)


# 便捷的获取函数
def get_auth_service():
    """获取认证服务实例"""
    return create_auth_service()


def get_social_auth_service():
    """获取社交认证服务实例"""
    return create_social_auth_service()


def get_blockchain_auth_service():
    """获取区块链认证服务实例"""
    return create_blockchain_auth_service()


def get_biometric_auth_service():
    """获取生物识别认证服务实例"""
    return create_biometric_auth_service()


def get_mfa_service():
    """获取MFA服务实例"""
    return create_mfa_service()


def get_user_service():
    """获取用户服务实例"""
    return create_user_service() 