#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
高级安全机制 - 认证、授权、加密和审计功能
"""

import asyncio
import time
import uuid
import hashlib
import hmac
import secrets
import json
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from loguru import logger

from ..observability.metrics import MetricsCollector


class AuthMethod(str, Enum):
    """认证方法"""
    JWT = "jwt"                 # JWT令牌
    API_KEY = "api_key"         # API密钥
    OAUTH2 = "oauth2"           # OAuth2
    BASIC = "basic"             # 基础认证
    CERTIFICATE = "certificate" # 证书认证


class Permission(str, Enum):
    """权限类型"""
    READ = "read"               # 读取
    WRITE = "write"             # 写入
    DELETE = "delete"           # 删除
    ADMIN = "admin"             # 管理
    EXECUTE = "execute"         # 执行


class ResourceType(str, Enum):
    """资源类型"""
    DOCUMENT = "document"       # 文档
    KNOWLEDGE_GRAPH = "knowledge_graph"  # 知识图谱
    TCM_DATA = "tcm_data"       # 中医数据
    USER_DATA = "user_data"     # 用户数据
    SYSTEM = "system"           # 系统
    API = "api"                 # API


class AuditAction(str, Enum):
    """审计动作"""
    LOGIN = "login"             # 登录
    LOGOUT = "logout"           # 登出
    ACCESS = "access"           # 访问
    CREATE = "create"           # 创建
    UPDATE = "update"           # 更新
    DELETE = "delete"           # 删除
    QUERY = "query"             # 查询
    EXPORT = "export"           # 导出


@dataclass
class User:
    """用户"""
    id: str
    username: str
    email: str
    roles: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    is_active: bool = True
    created_at: float = field(default_factory=time.time)
    last_login: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "roles": self.roles,
            "permissions": self.permissions,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "last_login": self.last_login,
            "metadata": self.metadata
        }


@dataclass
class Role:
    """角色"""
    id: str
    name: str
    description: str
    permissions: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "permissions": self.permissions,
            "created_at": self.created_at
        }


@dataclass
class AccessToken:
    """访问令牌"""
    token: str
    user_id: str
    expires_at: float
    scopes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        return time.time() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "token": self.token,
            "user_id": self.user_id,
            "expires_at": self.expires_at,
            "scopes": self.scopes,
            "metadata": self.metadata
        }


@dataclass
class AuditLog:
    """审计日志"""
    id: str
    user_id: str
    action: AuditAction
    resource_type: ResourceType
    resource_id: str
    timestamp: float = field(default_factory=time.time)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action.value,
            "resource_type": self.resource_type.value,
            "resource_id": self.resource_id,
            "timestamp": self.timestamp,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "details": self.details,
            "success": self.success
        }


class PasswordHasher:
    """密码哈希器"""
    
    def __init__(self, algorithm: str = "pbkdf2_sha256", iterations: int = 100000):
        self.algorithm = algorithm
        self.iterations = iterations
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> str:
        """哈希密码"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        if self.algorithm == "pbkdf2_sha256":
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt.encode(),
                iterations=self.iterations,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            return f"{self.algorithm}${self.iterations}${salt}${key.decode()}"
        
        else:
            raise ValueError(f"不支持的哈希算法: {self.algorithm}")
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """验证密码"""
        try:
            parts = hashed.split('$')
            if len(parts) != 4:
                return False
            
            algorithm, iterations, salt, key = parts
            
            if algorithm != self.algorithm:
                return False
            
            # 重新计算哈希
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt.encode(),
                iterations=int(iterations),
            )
            expected_key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            
            return hmac.compare_digest(key.encode(), expected_key)
            
        except Exception as e:
            logger.error(f"密码验证失败: {e}")
            return False


class JWTManager:
    """JWT管理器"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256", expiry_hours: int = 24):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expiry_hours = expiry_hours
    
    def create_token(self, user: User, scopes: Optional[List[str]] = None) -> AccessToken:
        """创建JWT令牌"""
        now = time.time()
        expires_at = now + (self.expiry_hours * 3600)
        
        payload = {
            "user_id": user.id,
            "username": user.username,
            "roles": user.roles,
            "permissions": user.permissions,
            "scopes": scopes or [],
            "iat": now,
            "exp": expires_at,
            "jti": str(uuid.uuid4())
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        return AccessToken(
            token=token,
            user_id=user.id,
            expires_at=expires_at,
            scopes=scopes or [],
            metadata={"algorithm": self.algorithm}
        )
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证JWT令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # 检查过期时间
            if time.time() > payload.get("exp", 0):
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT令牌已过期")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"无效的JWT令牌: {e}")
            return None
    
    def refresh_token(self, token: str) -> Optional[AccessToken]:
        """刷新JWT令牌"""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        # 创建新令牌
        user = User(
            id=payload["user_id"],
            username=payload["username"],
            email="",  # 从payload中获取或从数据库查询
            roles=payload.get("roles", []),
            permissions=payload.get("permissions", [])
        )
        
        return self.create_token(user, payload.get("scopes", []))


class EncryptionManager:
    """加密管理器"""
    
    def __init__(self, master_key: Optional[str] = None):
        if master_key:
            self.master_key = master_key.encode()
        else:
            self.master_key = Fernet.generate_key()
        
        self.fernet = Fernet(self.master_key)
        
        # 生成RSA密钥对
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        self.public_key = self.private_key.public_key()
    
    def encrypt_symmetric(self, data: str) -> str:
        """对称加密"""
        encrypted = self.fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_symmetric(self, encrypted_data: str) -> str:
        """对称解密"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"对称解密失败: {e}")
            raise
    
    def encrypt_asymmetric(self, data: str, public_key: Optional[Any] = None) -> str:
        """非对称加密"""
        key = public_key or self.public_key
        
        encrypted = key.encrypt(
            data.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_asymmetric(self, encrypted_data: str) -> str:
        """非对称解密"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            
            decrypted = self.private_key.decrypt(
                encrypted_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return decrypted.decode()
        except Exception as e:
            logger.error(f"非对称解密失败: {e}")
            raise
    
    def get_public_key_pem(self) -> str:
        """获取公钥PEM格式"""
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode()
    
    def hash_data(self, data: str, algorithm: str = "sha256") -> str:
        """哈希数据"""
        if algorithm == "sha256":
            return hashlib.sha256(data.encode()).hexdigest()
        elif algorithm == "sha512":
            return hashlib.sha512(data.encode()).hexdigest()
        elif algorithm == "md5":
            return hashlib.md5(data.encode()).hexdigest()
        else:
            raise ValueError(f"不支持的哈希算法: {algorithm}")


class PermissionManager:
    """权限管理器"""
    
    def __init__(self):
        self.roles: Dict[str, Role] = {}
        self.permissions: Dict[str, List[str]] = {}  # resource_type -> permissions
        
        # 初始化默认权限
        self._initialize_default_permissions()
    
    def _initialize_default_permissions(self):
        """初始化默认权限"""
        # 创建默认角色
        admin_role = Role(
            id="admin",
            name="管理员",
            description="系统管理员，拥有所有权限",
            permissions=["*"]  # 通配符表示所有权限
        )
        
        user_role = Role(
            id="user",
            name="普通用户",
            description="普通用户，拥有基本权限",
            permissions=[
                "document:read",
                "tcm_data:read",
                "api:query"
            ]
        )
        
        tcm_expert_role = Role(
            id="tcm_expert",
            name="中医专家",
            description="中医专家，拥有中医数据的读写权限",
            permissions=[
                "document:read",
                "document:write",
                "tcm_data:read",
                "tcm_data:write",
                "knowledge_graph:read",
                "api:query",
                "api:execute"
            ]
        )
        
        self.roles.update({
            "admin": admin_role,
            "user": user_role,
            "tcm_expert": tcm_expert_role
        })
    
    def create_role(self, role: Role) -> bool:
        """创建角色"""
        if role.id in self.roles:
            logger.warning(f"角色已存在: {role.id}")
            return False
        
        self.roles[role.id] = role
        logger.info(f"角色已创建: {role.name} ({role.id})")
        return True
    
    def get_role(self, role_id: str) -> Optional[Role]:
        """获取角色"""
        return self.roles.get(role_id)
    
    def check_permission(
        self,
        user: User,
        resource_type: ResourceType,
        permission: Permission,
        resource_id: Optional[str] = None
    ) -> bool:
        """检查权限"""
        # 检查用户直接权限
        required_permission = f"{resource_type.value}:{permission.value}"
        
        if required_permission in user.permissions or "*" in user.permissions:
            return True
        
        # 检查角色权限
        for role_id in user.roles:
            role = self.roles.get(role_id)
            if role:
                if required_permission in role.permissions or "*" in role.permissions:
                    return True
        
        # 检查资源特定权限
        if resource_id:
            resource_permission = f"{resource_type.value}:{resource_id}:{permission.value}"
            if resource_permission in user.permissions:
                return True
        
        return False
    
    def get_user_permissions(self, user: User) -> List[str]:
        """获取用户所有权限"""
        permissions = set(user.permissions)
        
        # 添加角色权限
        for role_id in user.roles:
            role = self.roles.get(role_id)
            if role:
                permissions.update(role.permissions)
        
        return list(permissions)


class AuditLogger:
    """审计日志记录器"""
    
    def __init__(self, storage_backend: str = "memory"):
        self.storage_backend = storage_backend
        self.logs: List[AuditLog] = []  # 内存存储
    
    async def log_action(
        self,
        user_id: str,
        action: AuditAction,
        resource_type: ResourceType,
        resource_id: str,
        success: bool = True,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """记录审计日志"""
        log_id = str(uuid.uuid4())
        
        audit_log = AuditLog(
            id=log_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {}
        )
        
        # 存储日志
        await self._store_log(audit_log)
        
        logger.info(f"审计日志已记录: {action.value} on {resource_type.value}:{resource_id} by {user_id}")
        
        return log_id
    
    async def _store_log(self, audit_log: AuditLog):
        """存储审计日志"""
        if self.storage_backend == "memory":
            self.logs.append(audit_log)
        elif self.storage_backend == "file":
            # 写入文件
            log_data = audit_log.to_dict()
            # 这里应该写入到文件或数据库
            pass
        elif self.storage_backend == "database":
            # 写入数据库
            pass
    
    async def get_logs(
        self,
        user_id: Optional[str] = None,
        action: Optional[AuditAction] = None,
        resource_type: Optional[ResourceType] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """获取审计日志"""
        filtered_logs = self.logs
        
        if user_id:
            filtered_logs = [log for log in filtered_logs if log.user_id == user_id]
        
        if action:
            filtered_logs = [log for log in filtered_logs if log.action == action]
        
        if resource_type:
            filtered_logs = [log for log in filtered_logs if log.resource_type == resource_type]
        
        if start_time:
            filtered_logs = [log for log in filtered_logs if log.timestamp >= start_time]
        
        if end_time:
            filtered_logs = [log for log in filtered_logs if log.timestamp <= end_time]
        
        # 按时间倒序排列
        filtered_logs.sort(key=lambda x: x.timestamp, reverse=True)
        
        return filtered_logs[:limit]


class SecurityManager:
    """安全管理器"""
    
    def __init__(
        self,
        secret_key: str,
        metrics_collector: Optional[MetricsCollector] = None
    ):
        self.secret_key = secret_key
        self.metrics_collector = metrics_collector
        
        # 初始化组件
        self.password_hasher = PasswordHasher()
        self.jwt_manager = JWTManager(secret_key)
        self.encryption_manager = EncryptionManager()
        self.permission_manager = PermissionManager()
        self.audit_logger = AuditLogger()
        
        # 用户存储（实际应该使用数据库）
        self.users: Dict[str, User] = {}
        self.tokens: Dict[str, AccessToken] = {}
        
        # 安全配置
        self.max_login_attempts = 5
        self.lockout_duration = 300  # 5分钟
        self.failed_attempts: Dict[str, List[float]] = {}
    
    async def register_user(
        self,
        username: str,
        email: str,
        password: str,
        roles: Optional[List[str]] = None
    ) -> str:
        """注册用户"""
        # 检查用户是否已存在
        for user in self.users.values():
            if user.username == username or user.email == email:
                raise ValueError("用户名或邮箱已存在")
        
        user_id = str(uuid.uuid4())
        
        # 哈希密码
        password_hash = self.password_hasher.hash_password(password)
        
        user = User(
            id=user_id,
            username=username,
            email=email,
            roles=roles or ["user"],
            metadata={"password_hash": password_hash}
        )
        
        self.users[user_id] = user
        
        # 记录审计日志
        await self.audit_logger.log_action(
            user_id=user_id,
            action=AuditAction.CREATE,
            resource_type=ResourceType.USER_DATA,
            resource_id=user_id,
            details={"username": username, "email": email}
        )
        
        logger.info(f"用户已注册: {username} ({user_id})")
        
        return user_id
    
    async def authenticate_user(
        self,
        username: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Optional[AccessToken]:
        """用户认证"""
        # 检查登录尝试次数
        if self._is_account_locked(username):
            logger.warning(f"账户被锁定: {username}")
            return None
        
        # 查找用户
        user = None
        for u in self.users.values():
            if u.username == username:
                user = u
                break
        
        if not user or not user.is_active:
            self._record_failed_attempt(username)
            await self.audit_logger.log_action(
                user_id=user.id if user else "unknown",
                action=AuditAction.LOGIN,
                resource_type=ResourceType.SYSTEM,
                resource_id="login",
                success=False,
                ip_address=ip_address,
                user_agent=user_agent,
                details={"reason": "user_not_found"}
            )
            return None
        
        # 验证密码
        password_hash = user.metadata.get("password_hash", "")
        if not self.password_hasher.verify_password(password, password_hash):
            self._record_failed_attempt(username)
            await self.audit_logger.log_action(
                user_id=user.id,
                action=AuditAction.LOGIN,
                resource_type=ResourceType.SYSTEM,
                resource_id="login",
                success=False,
                ip_address=ip_address,
                user_agent=user_agent,
                details={"reason": "invalid_password"}
            )
            return None
        
        # 清除失败尝试记录
        if username in self.failed_attempts:
            del self.failed_attempts[username]
        
        # 更新最后登录时间
        user.last_login = time.time()
        
        # 创建访问令牌
        token = self.jwt_manager.create_token(user)
        self.tokens[token.token] = token
        
        # 记录成功登录
        await self.audit_logger.log_action(
            user_id=user.id,
            action=AuditAction.LOGIN,
            resource_type=ResourceType.SYSTEM,
            resource_id="login",
            success=True,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # 记录指标
        if self.metrics_collector:
            await self.metrics_collector.increment_counter(
                "security_logins",
                {"status": "success", "user": username}
            )
        
        logger.info(f"用户登录成功: {username}")
        
        return token
    
    async def verify_token(self, token: str) -> Optional[User]:
        """验证访问令牌"""
        # 检查令牌缓存
        cached_token = self.tokens.get(token)
        if cached_token and cached_token.is_expired():
            del self.tokens[token]
            cached_token = None
        
        if not cached_token:
            # 验证JWT令牌
            payload = self.jwt_manager.verify_token(token)
            if not payload:
                return None
            
            user_id = payload.get("user_id")
            user = self.users.get(user_id)
            
            if not user or not user.is_active:
                return None
            
            return user
        
        # 从缓存获取用户
        user = self.users.get(cached_token.user_id)
        return user if user and user.is_active else None
    
    async def check_permission(
        self,
        user: User,
        resource_type: ResourceType,
        permission: Permission,
        resource_id: Optional[str] = None
    ) -> bool:
        """检查用户权限"""
        has_permission = self.permission_manager.check_permission(
            user, resource_type, permission, resource_id
        )
        
        # 记录访问日志
        await self.audit_logger.log_action(
            user_id=user.id,
            action=AuditAction.ACCESS,
            resource_type=resource_type,
            resource_id=resource_id or "unknown",
            success=has_permission,
            details={
                "permission": permission.value,
                "granted": has_permission
            }
        )
        
        return has_permission
    
    async def logout_user(self, token: str) -> bool:
        """用户登出"""
        cached_token = self.tokens.get(token)
        if cached_token:
            user = self.users.get(cached_token.user_id)
            
            # 移除令牌
            del self.tokens[token]
            
            # 记录登出日志
            if user:
                await self.audit_logger.log_action(
                    user_id=user.id,
                    action=AuditAction.LOGOUT,
                    resource_type=ResourceType.SYSTEM,
                    resource_id="logout",
                    success=True
                )
                
                logger.info(f"用户登出: {user.username}")
            
            return True
        
        return False
    
    def _is_account_locked(self, username: str) -> bool:
        """检查账户是否被锁定"""
        if username not in self.failed_attempts:
            return False
        
        attempts = self.failed_attempts[username]
        current_time = time.time()
        
        # 清理过期的尝试记录
        attempts = [t for t in attempts if current_time - t < self.lockout_duration]
        self.failed_attempts[username] = attempts
        
        return len(attempts) >= self.max_login_attempts
    
    def _record_failed_attempt(self, username: str):
        """记录失败尝试"""
        if username not in self.failed_attempts:
            self.failed_attempts[username] = []
        
        self.failed_attempts[username].append(time.time())
    
    async def encrypt_sensitive_data(self, data: str, use_asymmetric: bool = False) -> str:
        """加密敏感数据"""
        if use_asymmetric:
            return self.encryption_manager.encrypt_asymmetric(data)
        else:
            return self.encryption_manager.encrypt_symmetric(data)
    
    async def decrypt_sensitive_data(self, encrypted_data: str, use_asymmetric: bool = False) -> str:
        """解密敏感数据"""
        if use_asymmetric:
            return self.encryption_manager.decrypt_asymmetric(encrypted_data)
        else:
            return self.encryption_manager.decrypt_symmetric(encrypted_data)
    
    async def get_security_statistics(self) -> Dict[str, Any]:
        """获取安全统计"""
        total_users = len(self.users)
        active_tokens = len(self.tokens)
        locked_accounts = len([u for u in self.failed_attempts.keys() if self._is_account_locked(u)])
        
        # 获取最近的审计日志
        recent_logs = await self.audit_logger.get_logs(limit=100)
        
        # 统计登录成功/失败
        login_success = len([log for log in recent_logs if log.action == AuditAction.LOGIN and log.success])
        login_failed = len([log for log in recent_logs if log.action == AuditAction.LOGIN and not log.success])
        
        return {
            "total_users": total_users,
            "active_tokens": active_tokens,
            "locked_accounts": locked_accounts,
            "recent_login_success": login_success,
            "recent_login_failed": login_failed,
            "total_audit_logs": len(self.audit_logger.logs)
        }


# 全局安全管理器实例
_security_manager: Optional[SecurityManager] = None


def initialize_security_manager(
    secret_key: str,
    metrics_collector: Optional[MetricsCollector] = None
) -> SecurityManager:
    """初始化安全管理器"""
    global _security_manager
    _security_manager = SecurityManager(secret_key, metrics_collector)
    return _security_manager


def get_security_manager() -> Optional[SecurityManager]:
    """获取安全管理器实例"""
    return _security_manager


# 安全装饰器
def require_auth(func: Callable):
    """需要认证的装饰器"""
    async def wrapper(*args, **kwargs):
        # 从kwargs中提取token
        token = kwargs.get("token") or kwargs.get("authorization")
        
        if not token or not _security_manager:
            raise PermissionError("需要认证")
        
        user = await _security_manager.verify_token(token)
        if not user:
            raise PermissionError("无效的认证令牌")
        
        # 将用户信息注入到kwargs中
        kwargs["current_user"] = user
        
        return await func(*args, **kwargs)
    
    return wrapper


def require_permission(resource_type: ResourceType, permission: Permission):
    """需要特定权限的装饰器"""
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            
            if not current_user or not _security_manager:
                raise PermissionError("需要认证")
            
            resource_id = kwargs.get("resource_id")
            
            has_permission = await _security_manager.check_permission(
                current_user, resource_type, permission, resource_id
            )
            
            if not has_permission:
                raise PermissionError(f"缺少权限: {resource_type.value}:{permission.value}")
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def audit_action(action: AuditAction, resource_type: ResourceType):
    """审计动作装饰器"""
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            resource_id = kwargs.get("resource_id", "unknown")
            
            if current_user and _security_manager:
                try:
                    result = await func(*args, **kwargs)
                    
                    # 记录成功的审计日志
                    await _security_manager.audit_logger.log_action(
                        user_id=current_user.id,
                        action=action,
                        resource_type=resource_type,
                        resource_id=str(resource_id),
                        success=True
                    )
                    
                    return result
                    
                except Exception as e:
                    # 记录失败的审计日志
                    await _security_manager.audit_logger.log_action(
                        user_id=current_user.id,
                        action=action,
                        resource_type=resource_type,
                        resource_id=str(resource_id),
                        success=False,
                        details={"error": str(e)}
                    )
                    raise
            else:
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator 