"""
安全加固模块
Security Enhancement Module

提供认证授权、数据加密、审计日志、安全策略等功能
"""

import hashlib
import hmac
import secrets
import time
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union

import bcrypt
import jwt
import structlog
from cryptography.fernet import Fernet
from pydantic import BaseModel, EmailStr

from .config import settings

logger = structlog.get_logger(__name__)


class UserRole(str, Enum):
    """用户角色枚举"""
    
    ADMIN = "admin"  # 管理员
    REVIEWER = "reviewer"  # 审核员
    SUPERVISOR = "supervisor"  # 主管
    AUDITOR = "auditor"  # 审计员
    READONLY = "readonly"  # 只读用户


class Permission(str, Enum):
    """权限枚举"""
    
    # 审核任务权限
    TASK_CREATE = "task:create"
    TASK_READ = "task:read"
    TASK_UPDATE = "task:update"
    TASK_DELETE = "task:delete"
    TASK_ASSIGN = "task:assign"
    TASK_REVIEW = "task:review"
    
    # 审核员权限
    REVIEWER_CREATE = "reviewer:create"
    REVIEWER_READ = "reviewer:read"
    REVIEWER_UPDATE = "reviewer:update"
    REVIEWER_DELETE = "reviewer:delete"
    REVIEWER_ACTIVATE = "reviewer:activate"
    REVIEWER_DEACTIVATE = "reviewer:deactivate"
    
    # 系统权限
    SYSTEM_CONFIG = "system:config"
    SYSTEM_MONITOR = "system:monitor"
    SYSTEM_AUDIT = "system:audit"
    SYSTEM_BACKUP = "system:backup"
    
    # 报告权限
    REPORT_VIEW = "report:view"
    REPORT_EXPORT = "report:export"
    REPORT_ADMIN = "report:admin"


class AuditAction(str, Enum):
    """审计动作枚举"""
    
    LOGIN = "login"
    LOGOUT = "logout"
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    ASSIGN = "assign"
    APPROVE = "approve"
    REJECT = "reject"
    CANCEL = "cancel"
    EXPORT = "export"
    CONFIG_CHANGE = "config_change"


class SecurityLevel(str, Enum):
    """安全级别枚举"""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class User(BaseModel):
    """用户模型"""
    
    user_id: str
    username: str
    email: EmailStr
    roles: List[UserRole]
    permissions: List[Permission]
    is_active: bool = True
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class AuditLog(BaseModel):
    """审计日志模型"""
    
    id: str
    user_id: str
    username: str
    action: AuditAction
    resource_type: str
    resource_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime
    security_level: SecurityLevel = SecurityLevel.MEDIUM


class PasswordManager:
    """密码管理器"""
    
    def __init__(self):
        """初始化密码管理器"""
        self.min_length = 8
        self.require_uppercase = True
        self.require_lowercase = True
        self.require_digits = True
        self.require_special = True
        self.special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    def hash_password(self, password: str) -> str:
        """哈希密码"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        """验证密码"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error("Password verification failed", error=str(e))
            return False

    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """验证密码强度"""
        issues = []
        score = 0
        
        # 长度检查
        if len(password) < self.min_length:
            issues.append(f"密码长度至少需要{self.min_length}位")
        else:
            score += 1
        
        # 大写字母检查
        if self.require_uppercase and not any(c.isupper() for c in password):
            issues.append("密码需要包含大写字母")
        else:
            score += 1
        
        # 小写字母检查
        if self.require_lowercase and not any(c.islower() for c in password):
            issues.append("密码需要包含小写字母")
        else:
            score += 1
        
        # 数字检查
        if self.require_digits and not any(c.isdigit() for c in password):
            issues.append("密码需要包含数字")
        else:
            score += 1
        
        # 特殊字符检查
        if self.require_special and not any(c in self.special_chars for c in password):
            issues.append("密码需要包含特殊字符")
        else:
            score += 1
        
        # 计算强度等级
        if score == 5:
            strength = "strong"
        elif score >= 3:
            strength = "medium"
        else:
            strength = "weak"
        
        return {
            "is_valid": len(issues) == 0,
            "strength": strength,
            "score": score,
            "issues": issues
        }

    def generate_secure_password(self, length: int = 12) -> str:
        """生成安全密码"""
        import string
        
        # 确保包含所有必需的字符类型
        chars = ""
        password = ""
        
        if self.require_uppercase:
            chars += string.ascii_uppercase
            password += secrets.choice(string.ascii_uppercase)
        
        if self.require_lowercase:
            chars += string.ascii_lowercase
            password += secrets.choice(string.ascii_lowercase)
        
        if self.require_digits:
            chars += string.digits
            password += secrets.choice(string.digits)
        
        if self.require_special:
            chars += self.special_chars
            password += secrets.choice(self.special_chars)
        
        # 填充剩余长度
        for _ in range(length - len(password)):
            password += secrets.choice(chars)
        
        # 打乱密码字符顺序
        password_list = list(password)
        secrets.SystemRandom().shuffle(password_list)
        
        return ''.join(password_list)


class TokenManager:
    """令牌管理器"""
    
    def __init__(self):
        """初始化令牌管理器"""
        self.secret_key = settings.security.secret_key
        self.algorithm = settings.security.algorithm
        self.access_token_expire_minutes = settings.security.access_token_expire_minutes
        self.refresh_token_expire_days = settings.security.refresh_token_expire_days

    def create_access_token(self, user_id: str, permissions: List[str]) -> str:
        """创建访问令牌"""
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            "sub": user_id,
            "permissions": permissions,
            "type": "access",
            "iat": now.timestamp(),
            "exp": expire.timestamp(),
            "jti": secrets.token_urlsafe(16)  # JWT ID
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, user_id: str) -> str:
        """创建刷新令牌"""
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            "sub": user_id,
            "type": "refresh",
            "iat": now.timestamp(),
            "exp": expire.timestamp(),
            "jti": secrets.token_urlsafe(16)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # 检查令牌是否过期
            if payload.get("exp", 0) < time.time():
                logger.warning("Token expired", user_id=payload.get("sub"))
                return None
            
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning("Invalid token", error=str(e))
            return None

    def refresh_access_token(self, refresh_token: str, permissions: List[str]) -> Optional[str]:
        """刷新访问令牌"""
        payload = self.verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        return self.create_access_token(user_id, permissions)


class PermissionManager:
    """权限管理器"""
    
    def __init__(self):
        """初始化权限管理器"""
        # 角色权限映射
        self.role_permissions = {
            UserRole.ADMIN: [
                Permission.TASK_CREATE, Permission.TASK_READ, Permission.TASK_UPDATE, 
                Permission.TASK_DELETE, Permission.TASK_ASSIGN,
                Permission.REVIEWER_CREATE, Permission.REVIEWER_READ, Permission.REVIEWER_UPDATE,
                Permission.REVIEWER_DELETE, Permission.REVIEWER_ACTIVATE, Permission.REVIEWER_DEACTIVATE,
                Permission.SYSTEM_CONFIG, Permission.SYSTEM_MONITOR, Permission.SYSTEM_AUDIT,
                Permission.SYSTEM_BACKUP, Permission.REPORT_VIEW, Permission.REPORT_EXPORT,
                Permission.REPORT_ADMIN
            ],
            UserRole.SUPERVISOR: [
                Permission.TASK_READ, Permission.TASK_UPDATE, Permission.TASK_ASSIGN,
                Permission.REVIEWER_READ, Permission.REVIEWER_UPDATE,
                Permission.SYSTEM_MONITOR, Permission.REPORT_VIEW, Permission.REPORT_EXPORT
            ],
            UserRole.REVIEWER: [
                Permission.TASK_READ, Permission.TASK_REVIEW,
                Permission.REVIEWER_READ, Permission.REPORT_VIEW
            ],
            UserRole.AUDITOR: [
                Permission.TASK_READ, Permission.REVIEWER_READ,
                Permission.SYSTEM_AUDIT, Permission.REPORT_VIEW, Permission.REPORT_EXPORT
            ],
            UserRole.READONLY: [
                Permission.TASK_READ, Permission.REVIEWER_READ, Permission.REPORT_VIEW
            ]
        }

    def get_permissions_for_roles(self, roles: List[UserRole]) -> List[Permission]:
        """获取角色对应的权限"""
        permissions = set()
        for role in roles:
            role_perms = self.role_permissions.get(role, [])
            permissions.update(role_perms)
        return list(permissions)

    def has_permission(self, user_permissions: List[Permission], required_permission: Permission) -> bool:
        """检查用户是否有指定权限"""
        return required_permission in user_permissions

    def has_any_permission(self, user_permissions: List[Permission], required_permissions: List[Permission]) -> bool:
        """检查用户是否有任一指定权限"""
        return any(perm in user_permissions for perm in required_permissions)

    def has_all_permissions(self, user_permissions: List[Permission], required_permissions: List[Permission]) -> bool:
        """检查用户是否有所有指定权限"""
        return all(perm in user_permissions for perm in required_permissions)


class DataEncryption:
    """数据加密器"""
    
    def __init__(self, key: Optional[bytes] = None):
        """初始化数据加密器
        
        Args:
            key: 加密密钥，如果为None则生成新密钥
        """
        if key is None:
            key = Fernet.generate_key()
        self.cipher = Fernet(key)
        self.key = key

    def encrypt(self, data: str) -> str:
        """加密数据"""
        try:
            encrypted_data = self.cipher.encrypt(data.encode('utf-8'))
            return encrypted_data.decode('utf-8')
        except Exception as e:
            logger.error("Data encryption failed", error=str(e))
            raise

    def decrypt(self, encrypted_data: str) -> str:
        """解密数据"""
        try:
            decrypted_data = self.cipher.decrypt(encrypted_data.encode('utf-8'))
            return decrypted_data.decode('utf-8')
        except Exception as e:
            logger.error("Data decryption failed", error=str(e))
            raise

    def encrypt_dict(self, data: Dict[str, Any]) -> str:
        """加密字典数据"""
        import json
        json_str = json.dumps(data, ensure_ascii=False)
        return self.encrypt(json_str)

    def decrypt_dict(self, encrypted_data: str) -> Dict[str, Any]:
        """解密字典数据"""
        import json
        json_str = self.decrypt(encrypted_data)
        return json.loads(json_str)


class AuditLogger:
    """审计日志记录器"""
    
    def __init__(self):
        """初始化审计日志记录器"""
        self.logs: List[AuditLog] = []

    async def log_action(
        self,
        user_id: str,
        username: str,
        action: AuditAction,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        security_level: SecurityLevel = SecurityLevel.MEDIUM
    ) -> str:
        """记录审计日志"""
        log_id = secrets.token_urlsafe(16)
        
        audit_log = AuditLog(
            id=log_id,
            user_id=user_id,
            username=username,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.now(timezone.utc),
            security_level=security_level
        )
        
        # 记录到内存（实际应用中应该持久化到数据库）
        self.logs.append(audit_log)
        
        # 记录到结构化日志
        logger.info(
            "Audit log recorded",
            log_id=log_id,
            user_id=user_id,
            username=username,
            action=action.value,
            resource_type=resource_type,
            resource_id=resource_id,
            security_level=security_level.value,
            ip_address=ip_address
        )
        
        return log_id

    async def get_logs(
        self,
        user_id: Optional[str] = None,
        action: Optional[AuditAction] = None,
        resource_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """获取审计日志"""
        filtered_logs = self.logs
        
        # 应用过滤条件
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
        
        # 按时间倒序排列并限制数量
        filtered_logs.sort(key=lambda x: x.timestamp, reverse=True)
        return filtered_logs[:limit]


class SecurityValidator:
    """安全验证器"""
    
    def __init__(self):
        """初始化安全验证器"""
        self.max_login_attempts = 5
        self.lockout_duration = timedelta(minutes=30)
        self.failed_attempts: Dict[str, List[datetime]] = {}

    def validate_ip_address(self, ip_address: str, allowed_ips: Optional[List[str]] = None) -> bool:
        """验证IP地址"""
        if not allowed_ips:
            return True
        
        # 简单的IP白名单检查
        return ip_address in allowed_ips

    def check_rate_limit(self, user_id: str, action: str, max_requests: int = 100, window_minutes: int = 60) -> bool:
        """检查速率限制"""
        # 这里应该使用Redis等外部存储来实现分布式速率限制
        # 当前只是一个简单的内存实现
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(minutes=window_minutes)
        
        key = f"{user_id}:{action}"
        if key not in self.failed_attempts:
            self.failed_attempts[key] = []
        
        # 清理过期记录
        self.failed_attempts[key] = [
            timestamp for timestamp in self.failed_attempts[key]
            if timestamp > window_start
        ]
        
        # 检查是否超过限制
        if len(self.failed_attempts[key]) >= max_requests:
            logger.warning(
                "Rate limit exceeded",
                user_id=user_id,
                action=action,
                requests=len(self.failed_attempts[key]),
                limit=max_requests
            )
            return False
        
        # 记录当前请求
        self.failed_attempts[key].append(now)
        return True

    def record_failed_login(self, username: str, ip_address: str):
        """记录登录失败"""
        key = f"login:{username}:{ip_address}"
        now = datetime.now(timezone.utc)
        
        if key not in self.failed_attempts:
            self.failed_attempts[key] = []
        
        self.failed_attempts[key].append(now)
        
        # 清理过期记录
        cutoff_time = now - self.lockout_duration
        self.failed_attempts[key] = [
            timestamp for timestamp in self.failed_attempts[key]
            if timestamp > cutoff_time
        ]

    def is_account_locked(self, username: str, ip_address: str) -> bool:
        """检查账户是否被锁定"""
        key = f"login:{username}:{ip_address}"
        
        if key not in self.failed_attempts:
            return False
        
        now = datetime.now(timezone.utc)
        cutoff_time = now - self.lockout_duration
        
        # 清理过期记录
        self.failed_attempts[key] = [
            timestamp for timestamp in self.failed_attempts[key]
            if timestamp > cutoff_time
        ]
        
        # 检查失败次数
        recent_failures = len(self.failed_attempts[key])
        if recent_failures >= self.max_login_attempts:
            logger.warning(
                "Account locked due to too many failed login attempts",
                username=username,
                ip_address=ip_address,
                failures=recent_failures
            )
            return True
        
        return False

    def clear_failed_attempts(self, username: str, ip_address: str):
        """清除失败记录"""
        key = f"login:{username}:{ip_address}"
        if key in self.failed_attempts:
            del self.failed_attempts[key]


class SecurityManager:
    """安全管理器"""
    
    def __init__(self):
        """初始化安全管理器"""
        self.password_manager = PasswordManager()
        self.token_manager = TokenManager()
        self.permission_manager = PermissionManager()
        self.audit_logger = AuditLogger()
        self.security_validator = SecurityValidator()
        self.data_encryption = DataEncryption()

    async def authenticate_user(
        self, 
        username: str, 
        password: str, 
        ip_address: str
    ) -> Optional[Dict[str, Any]]:
        """用户认证"""
        # 检查账户是否被锁定
        if self.security_validator.is_account_locked(username, ip_address):
            await self.audit_logger.log_action(
                user_id="unknown",
                username=username,
                action=AuditAction.LOGIN,
                resource_type="authentication",
                details={"result": "account_locked"},
                ip_address=ip_address,
                security_level=SecurityLevel.HIGH
            )
            return None
        
        # 这里应该从数据库获取用户信息
        # 当前只是示例实现
        user = await self._get_user_by_username(username)
        if not user:
            self.security_validator.record_failed_login(username, ip_address)
            await self.audit_logger.log_action(
                user_id="unknown",
                username=username,
                action=AuditAction.LOGIN,
                resource_type="authentication",
                details={"result": "user_not_found"},
                ip_address=ip_address,
                security_level=SecurityLevel.MEDIUM
            )
            return None
        
        # 验证密码
        if not self.password_manager.verify_password(password, user.get("password_hash", "")):
            self.security_validator.record_failed_login(username, ip_address)
            await self.audit_logger.log_action(
                user_id=user.get("user_id", "unknown"),
                username=username,
                action=AuditAction.LOGIN,
                resource_type="authentication",
                details={"result": "invalid_password"},
                ip_address=ip_address,
                security_level=SecurityLevel.MEDIUM
            )
            return None
        
        # 清除失败记录
        self.security_validator.clear_failed_attempts(username, ip_address)
        
        # 生成令牌
        permissions = self.permission_manager.get_permissions_for_roles(user.get("roles", []))
        access_token = self.token_manager.create_access_token(
            user["user_id"], 
            [perm.value for perm in permissions]
        )
        refresh_token = self.token_manager.create_refresh_token(user["user_id"])
        
        # 记录成功登录
        await self.audit_logger.log_action(
            user_id=user["user_id"],
            username=username,
            action=AuditAction.LOGIN,
            resource_type="authentication",
            details={"result": "success"},
            ip_address=ip_address,
            security_level=SecurityLevel.LOW
        )
        
        return {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "permissions": [perm.value for perm in permissions]
        }

    async def _get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """根据用户名获取用户信息（示例实现）"""
        # 这里应该从数据库查询用户信息
        # 当前只是示例数据
        return None

    def require_permission(self, required_permission: Permission):
        """权限检查装饰器"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # 这里应该从请求上下文获取用户权限
                # 当前只是示例实现
                user_permissions = kwargs.get("user_permissions", [])
                
                if not self.permission_manager.has_permission(user_permissions, required_permission):
                    logger.warning(
                        "Permission denied",
                        required_permission=required_permission.value,
                        user_permissions=user_permissions
                    )
                    raise PermissionError(f"Required permission: {required_permission.value}")
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator


# 全局安全管理器实例
security_manager = SecurityManager() 