"""
security_manager - 索克生活项目模块
"""

    from cryptography.fernet import Fernet
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    import jwt
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable
import asyncio
import base64
import logging
import threading
import time
import uuid

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
消息安全管理器
支持端到端加密、访问控制、审计日志和身份验证
"""


try:
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    logger.warning("Cryptography library not available, encryption features will be disabled")

try:
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    logger.warning("PyJWT not available, JWT authentication will be disabled")

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """安全级别"""
    NONE = "none"
    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    CRITICAL = "critical"

class EncryptionType(Enum):
    """加密类型"""
    NONE = "none"
    SYMMETRIC = "symmetric"
    ASYMMETRIC = "asymmetric"
    HYBRID = "hybrid"

class AuthMethod(Enum):
    """认证方法"""
    NONE = "none"
    API_KEY = "api_key"
    JWT = "jwt"
    OAUTH2 = "oauth2"
    MUTUAL_TLS = "mutual_tls"

class AuditEventType(Enum):
    """审计事件类型"""
    MESSAGE_PUBLISH = "message_publish"
    MESSAGE_CONSUME = "message_consume"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    ENCRYPTION = "encryption"
    DECRYPTION = "decryption"
    ACCESS_DENIED = "access_denied"
    SECURITY_VIOLATION = "security_violation"

@dataclass
class SecurityConfig:
    """安全配置"""
    # 基础安全配置
    security_level: SecurityLevel = SecurityLevel.STANDARD
    encryption_enabled: bool = True
    authentication_enabled: bool = True
    authorization_enabled: bool = True
    audit_enabled: bool = True
    
    # 加密配置
    encryption_type: EncryptionType = EncryptionType.HYBRID
    encryption_key_size: int = 2048
    symmetric_algorithm: str = "AES-256-GCM"
    key_rotation_interval: int = 86400  # 24小时
    
    # 认证配置
    auth_method: AuthMethod = AuthMethod.JWT
    jwt_secret: Optional[str] = None
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600  # 1小时
    api_key_length: int = 32
    
    # 访问控制配置
    default_permissions: Set[str] = field(default_factory=lambda: {"read", "write"})
    role_based_access: bool = True
    topic_level_permissions: bool = True
    
    # 审计配置
    audit_log_retention: int = 2592000  # 30天
    audit_log_max_size: int = 100 * 1024 * 1024  # 100MB
    sensitive_data_masking: bool = True
    
    # 安全策略
    max_message_size: int = 10 * 1024 * 1024  # 10MB
    rate_limiting_enabled: bool = True
    max_requests_per_minute: int = 1000
    ip_whitelist: Set[str] = field(default_factory=set)
    ip_blacklist: Set[str] = field(default_factory=set)

@dataclass
class User:
    """用户信息"""
    id: str
    username: str
    email: Optional[str] = None
    roles: Set[str] = field(default_factory=set)
    permissions: Set[str] = field(default_factory=set)
    api_keys: Set[str] = field(default_factory=set)
    created_at: float = field(default_factory=time.time)
    last_login: Optional[float] = None
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def has_permission(self, permission: str) -> bool:
        """检查用户是否有指定权限"""
        return permission in self.permissions
    
    def has_role(self, role: str) -> bool:
        """检查用户是否有指定角色"""
        return role in self.roles
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'roles': list(self.roles),
            'permissions': list(self.permissions),
            'created_at': self.created_at,
            'last_login': self.last_login,
            'is_active': self.is_active,
            'metadata': self.metadata
        }

@dataclass
class AuditEvent:
    """审计事件"""
    id: str
    event_type: AuditEventType
    user_id: Optional[str]
    resource: str
    action: str
    result: str  # success, failure, denied
    timestamp: float
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    sensitive_data_masked: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'event_type': self.event_type.value,
            'user_id': self.user_id,
            'resource': self.resource,
            'action': self.action,
            'result': self.result,
            'timestamp': self.timestamp,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'details': self.details,
            'sensitive_data_masked': self.sensitive_data_masked
        }

class EncryptionManager:
    """加密管理器"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.symmetric_keys: Dict[str, bytes] = {}
        self.asymmetric_keys: Dict[str, Tuple[bytes, bytes]] = {}  # (private_key, public_key)
        self.key_rotation_times: Dict[str, float] = {}
        self._lock = threading.Lock()
        
        if CRYPTOGRAPHY_AVAILABLE:
            self._init_encryption_keys()
    
    def _init_encryption_keys(self):
        """初始化加密密钥"""
        # 生成主密钥
        self._generate_symmetric_key("master")
        
        # 生成非对称密钥对
        if self.config.encryption_type in [EncryptionType.ASYMMETRIC, EncryptionType.HYBRID]:
            self._generate_asymmetric_key_pair("master")
    
    def _generate_symmetric_key(self, key_id: str) -> bytes:
        """生成对称密钥"""
        if not CRYPTOGRAPHY_AVAILABLE:
            raise RuntimeError("Cryptography library not available")
        
        key = Fernet.generate_key()
        
        with self._lock:
            self.symmetric_keys[key_id] = key
            self.key_rotation_times[key_id] = time.time()
        
        return key
    
    def _generate_asymmetric_key_pair(self, key_id: str) -> Tuple[bytes, bytes]:
        """生成非对称密钥对"""
        if not CRYPTOGRAPHY_AVAILABLE:
            raise RuntimeError("Cryptography library not available")
        
        # 生成RSA密钥对
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.config.encryption_key_size,
            backend=default_backend()
        )
        
        public_key = private_key.public_key()
        
        # 序列化密钥
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        with self._lock:
            self.asymmetric_keys[key_id] = (private_pem, public_pem)
            self.key_rotation_times[key_id] = time.time()
        
        return private_pem, public_pem
    
    def encrypt_message(self, message: bytes, key_id: str = "master") -> Dict[str, Any]:
        """加密消息"""
        if not CRYPTOGRAPHY_AVAILABLE or not self.config.encryption_enabled:
            return {
                'encrypted': False,
                'data': base64.b64encode(message).decode(),
                'algorithm': 'none'
            }
        
        try:
            if self.config.encryption_type == EncryptionType.SYMMETRIC:
                return self._encrypt_symmetric(message, key_id)
            elif self.config.encryption_type == EncryptionType.ASYMMETRIC:
                return self._encrypt_asymmetric(message, key_id)
            elif self.config.encryption_type == EncryptionType.HYBRID:
                return self._encrypt_hybrid(message, key_id)
            else:
                return {
                    'encrypted': False,
                    'data': base64.b64encode(message).decode(),
                    'algorithm': 'none'
                }
        
        except Exception as e:
            logger.error(f"消息加密失败: {e}")
            raise
    
    def decrypt_message(self, encrypted_data: Dict[str, Any]) -> bytes:
        """解密消息"""
        if not encrypted_data.get('encrypted', False):
            return base64.b64decode(encrypted_data['data'])
        
        if not CRYPTOGRAPHY_AVAILABLE:
            raise RuntimeError("Cryptography library not available for decryption")
        
        try:
            algorithm = encrypted_data.get('algorithm', 'none')
            
            if algorithm == 'symmetric':
                return self._decrypt_symmetric(encrypted_data)
            elif algorithm == 'asymmetric':
                return self._decrypt_asymmetric(encrypted_data)
            elif algorithm == 'hybrid':
                return self._decrypt_hybrid(encrypted_data)
            else:
                return base64.b64decode(encrypted_data['data'])
        
        except Exception as e:
            logger.error(f"消息解密失败: {e}")
            raise
    
    def _encrypt_symmetric(self, message: bytes, key_id: str) -> Dict[str, Any]:
        """对称加密"""
        key = self.symmetric_keys.get(key_id)
        if not key:
            key = self._generate_symmetric_key(key_id)
        
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(message)
        
        return {
            'encrypted': True,
            'algorithm': 'symmetric',
            'key_id': key_id,
            'data': base64.b64encode(encrypted_data).decode()
        }
    
    def _decrypt_symmetric(self, encrypted_data: Dict[str, Any]) -> bytes:
        """对称解密"""
        key_id = encrypted_data['key_id']
        key = self.symmetric_keys.get(key_id)
        
        if not key:
            raise ValueError(f"Symmetric key not found: {key_id}")
        
        fernet = Fernet(key)
        encrypted_bytes = base64.b64decode(encrypted_data['data'])
        
        return fernet.decrypt(encrypted_bytes)
    
    def _encrypt_asymmetric(self, message: bytes, key_id: str) -> Dict[str, Any]:
        """非对称加密"""
        key_pair = self.asymmetric_keys.get(key_id)
        if not key_pair:
            key_pair = self._generate_asymmetric_key_pair(key_id)
        
        public_key = serialization.load_pem_public_key(
            key_pair[1], backend=default_backend()
        )
        
        encrypted_data = public_key.encrypt(
            message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return {
            'encrypted': True,
            'algorithm': 'asymmetric',
            'key_id': key_id,
            'data': base64.b64encode(encrypted_data).decode()
        }
    
    def _decrypt_asymmetric(self, encrypted_data: Dict[str, Any]) -> bytes:
        """非对称解密"""
        key_id = encrypted_data['key_id']
        key_pair = self.asymmetric_keys.get(key_id)
        
        if not key_pair:
            raise ValueError(f"Asymmetric key pair not found: {key_id}")
        
        private_key = serialization.load_pem_private_key(
            key_pair[0], password=None, backend=default_backend()
        )
        
        encrypted_bytes = base64.b64decode(encrypted_data['data'])
        
        return private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    
    def _encrypt_hybrid(self, message: bytes, key_id: str) -> Dict[str, Any]:
        """混合加密（对称+非对称）"""
        # 生成临时对称密钥
        temp_key = Fernet.generate_key()
        fernet = Fernet(temp_key)
        
        # 用对称密钥加密消息
        encrypted_message = fernet.encrypt(message)
        
        # 用非对称密钥加密对称密钥
        key_pair = self.asymmetric_keys.get(key_id)
        if not key_pair:
            key_pair = self._generate_asymmetric_key_pair(key_id)
        
        public_key = serialization.load_pem_public_key(
            key_pair[1], backend=default_backend()
        )
        
        encrypted_key = public_key.encrypt(
            temp_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return {
            'encrypted': True,
            'algorithm': 'hybrid',
            'key_id': key_id,
            'data': base64.b64encode(encrypted_message).decode(),
            'encrypted_key': base64.b64encode(encrypted_key).decode()
        }
    
    def _decrypt_hybrid(self, encrypted_data: Dict[str, Any]) -> bytes:
        """混合解密"""
        key_id = encrypted_data['key_id']
        key_pair = self.asymmetric_keys.get(key_id)
        
        if not key_pair:
            raise ValueError(f"Asymmetric key pair not found: {key_id}")
        
        # 解密对称密钥
        private_key = serialization.load_pem_private_key(
            key_pair[0], password=None, backend=default_backend()
        )
        
        encrypted_key_bytes = base64.b64decode(encrypted_data['encrypted_key'])
        symmetric_key = private_key.decrypt(
            encrypted_key_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # 解密消息
        fernet = Fernet(symmetric_key)
        encrypted_message_bytes = base64.b64decode(encrypted_data['data'])
        
        return fernet.decrypt(encrypted_message_bytes)
    
    def rotate_keys(self):
        """轮换密钥"""
        current_time = time.time()
        
        with self._lock:
            for key_id, rotation_time in list(self.key_rotation_times.items()):
                if current_time - rotation_time > self.config.key_rotation_interval:
                    logger.info(f"轮换密钥: {key_id}")
                    
                    if key_id in self.symmetric_keys:
                        self._generate_symmetric_key(key_id)
                    
                    if key_id in self.asymmetric_keys:
                        self._generate_asymmetric_key_pair(key_id)

class AuthenticationManager:
    """认证管理器"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.users: Dict[str, User] = {}
        self.api_keys: Dict[str, str] = {}  # api_key -> user_id
        self.jwt_secret = config.jwt_secret or self._generate_jwt_secret()
        self._lock = threading.Lock()
    
    def _generate_jwt_secret(self) -> str:
        """生成JWT密钥"""
        return base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes).decode()
    
    def create_user(self, username: str, email: Optional[str] = None, 
                   roles: Set[str] = None, permissions: Set[str] = None) -> User:
        """创建用户"""
        user_id = str(uuid.uuid4())
        roles = roles or set()
        permissions = permissions or self.config.default_permissions.copy()
        
        user = User(
            id=user_id,
            username=username,
            email=email,
            roles=roles,
            permissions=permissions
        )
        
        with self._lock:
            self.users[user_id] = user
        
        logger.info(f"创建用户: {username} ({user_id})")
        return user
    
    def generate_api_key(self, user_id: str) -> str:
        """生成API密钥"""
        if user_id not in self.users:
            raise ValueError(f"User not found: {user_id}")
        
        api_key = base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes).decode()[:self.config.api_key_length]
        
        with self._lock:
            self.api_keys[api_key] = user_id
            self.users[user_id].api_keys.add(api_key)
        
        logger.info(f"为用户 {user_id} 生成API密钥")
        return api_key
    
    def generate_jwt_token(self, user_id: str) -> str:
        """生成JWT令牌"""
        if not JWT_AVAILABLE:
            raise RuntimeError("PyJWT library not available")
        
        user = self.users.get(user_id)
        if not user:
            raise ValueError(f"User not found: {user_id}")
        
        payload = {
            'user_id': user_id,
            'username': user.username,
            'roles': list(user.roles),
            'permissions': list(user.permissions),
            'iat': time.time(),
            'exp': time.time() + self.config.jwt_expiration
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.config.jwt_algorithm)
        
        # 更新最后登录时间
        with self._lock:
            user.last_login = time.time()
        
        logger.info(f"为用户 {user_id} 生成JWT令牌")
        return token
    
    def authenticate_api_key(self, api_key: str) -> Optional[User]:
        """API密钥认证"""
        user_id = self.api_keys.get(api_key)
        if not user_id:
            return None
        
        user = self.users.get(user_id)
        if not user or not user.is_active:
            return None
        
        # 更新最后登录时间
        with self._lock:
            user.last_login = time.time()
        
        return user
    
    def authenticate_jwt(self, token: str) -> Optional[User]:
        """JWT令牌认证"""
        if not JWT_AVAILABLE:
            return None
        
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.config.jwt_algorithm])
            user_id = payload.get('user_id')
            
            if not user_id:
                return None
            
            user = self.users.get(user_id)
            if not user or not user.is_active:
                return None
            
            # 更新最后登录时间
            with self._lock:
                user.last_login = time.time()
            
            return user
        
        except jwt.ExpiredSignatureError:
            logger.warning("JWT令牌已过期")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"无效的JWT令牌: {e}")
            return None
    
    def revoke_api_key(self, api_key: str) -> bool:
        """撤销API密钥"""
        user_id = self.api_keys.get(api_key)
        if not user_id:
            return False
        
        with self._lock:
            self.api_keys.pop(api_key, None)
            user = self.users.get(user_id)
            if user:
                user.api_keys.discard(api_key)
        
        logger.info(f"撤销API密钥: {api_key}")
        return True
    
    def deactivate_user(self, user_id: str) -> bool:
        """停用用户"""
        user = self.users.get(user_id)
        if not user:
            return False
        
        with self._lock:
            user.is_active = False
            # 撤销所有API密钥
            for api_key in list(user.api_keys):
                self.api_keys.pop(api_key, None)
            user.api_keys.clear()
        
        logger.info(f"停用用户: {user_id}")
        return True

class AuthorizationManager:
    """授权管理器"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.role_permissions: Dict[str, Set[str]] = {}
        self.topic_permissions: Dict[str, Dict[str, Set[str]]] = {}  # topic -> {user_id: permissions}
        self._lock = threading.Lock()
        
        # 初始化默认角色
        self._init_default_roles()
    
    def _init_default_roles(self):
        """初始化默认角色"""
        default_roles = {
            'admin': {'read', 'write', 'delete', 'manage'},
            'producer': {'write'},
            'consumer': {'read'},
            'user': {'read', 'write'}
        }
        
        with self._lock:
            self.role_permissions.update(default_roles)
    
    def create_role(self, role_name: str, permissions: Set[str]):
        """创建角色"""
        with self._lock:
            self.role_permissions[role_name] = permissions.copy()
        
        logger.info(f"创建角色: {role_name} with permissions: {permissions}")
    
    def assign_role_to_user(self, user: User, role_name: str):
        """为用户分配角色"""
        if role_name not in self.role_permissions:
            raise ValueError(f"Role not found: {role_name}")
        
        user.roles.add(role_name)
        user.permissions.update(self.role_permissions[role_name])
        
        logger.info(f"为用户 {user.id} 分配角色: {role_name}")
    
    def grant_topic_permission(self, topic: str, user_id: str, permissions: Set[str]):
        """授予主题权限"""
        with self._lock:
            if topic not in self.topic_permissions:
                self.topic_permissions[topic] = {}
            
            if user_id not in self.topic_permissions[topic]:
                self.topic_permissions[topic][user_id] = set()
            
            self.topic_permissions[topic][user_id].update(permissions)
        
        logger.info(f"为用户 {user_id} 授予主题 {topic} 权限: {permissions}")
    
    def check_permission(self, user: User, resource: str, action: str) -> bool:
        """检查权限"""
        if not self.config.authorization_enabled:
            return True
        
        # 检查全局权限
        if user.has_permission(action):
            return True
        
        # 检查主题级权限
        if self.config.topic_level_permissions and resource.startswith('topic:'):
            topic = resource[6:]  # 移除 'topic:' 前缀
            topic_perms = self.topic_permissions.get(topic, {})
            user_perms = topic_perms.get(user.id, set())
            
            if action in user_perms:
                return True
        
        return False
    
    def get_user_permissions(self, user: User, topic: Optional[str] = None) -> Set[str]:
        """获取用户权限"""
        permissions = user.permissions.copy()
        
        # 添加主题级权限
        if topic and self.config.topic_level_permissions:
            topic_perms = self.topic_permissions.get(topic, {})
            user_perms = topic_perms.get(user.id, set())
            permissions.update(user_perms)
        
        return permissions

class AuditLogger:
    """审计日志记录器"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.audit_events: deque = deque(maxlen=10000)
        self._lock = threading.Lock()
        self.sensitive_fields = {'password', 'token', 'key', 'secret', 'credential'}
    
    def log_event(self, event_type: AuditEventType, user_id: Optional[str], 
                  resource: str, action: str, result: str,
                  ip_address: Optional[str] = None, user_agent: Optional[str] = None,
                  details: Dict[str, Any] = None):
        """记录审计事件"""
        if not self.config.audit_enabled:
            return
        
        details = details or {}
        
        # 敏感数据脱敏
        if self.config.sensitive_data_masking:
            details = self._mask_sensitive_data(details)
        
        event = AuditEvent(
            id=str(uuid.uuid4()),
            event_type=event_type,
            user_id=user_id,
            resource=resource,
            action=action,
            result=result,
            timestamp=time.time(),
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            sensitive_data_masked=self.config.sensitive_data_masking
        )
        
        with self._lock:
            self.audit_events.append(event)
        
        logger.info(f"审计事件: {event_type.value} - {resource} - {action} - {result}")
    
    def _mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """脱敏敏感数据"""
        masked_data = {}
        
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in self.sensitive_fields):
                if isinstance(value, str) and len(value) > 4:
                    masked_data[key] = value[:2] + '*' * (len(value) - 4) + value[-2:]
                else:
                    masked_data[key] = '***'
            elif isinstance(value, dict):
                masked_data[key] = self._mask_sensitive_data(value)
            else:
                masked_data[key] = value
        
        return masked_data
    
    def get_audit_events(self, limit: int = 100, 
                        event_type: Optional[AuditEventType] = None,
                        user_id: Optional[str] = None,
                        start_time: Optional[float] = None,
                        end_time: Optional[float] = None) -> List[AuditEvent]:
        """获取审计事件"""
        with self._lock:
            events = list(self.audit_events)
        
        # 过滤条件
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if user_id:
            events = [e for e in events if e.user_id == user_id]
        
        if start_time:
            events = [e for e in events if e.timestamp >= start_time]
        
        if end_time:
            events = [e for e in events if e.timestamp <= end_time]
        
        # 按时间倒序排列
        events.sort(key=lambda x: x.timestamp, reverse=True)
        
        return events[:limit]
    
    def get_security_violations(self, limit: int = 50) -> List[AuditEvent]:
        """获取安全违规事件"""
        violation_types = {
            AuditEventType.ACCESS_DENIED,
            AuditEventType.SECURITY_VIOLATION
        }
        
        with self._lock:
            violations = [
                e for e in self.audit_events 
                if e.event_type in violation_types or e.result == 'denied'
            ]
        
        violations.sort(key=lambda x: x.timestamp, reverse=True)
        return violations[:limit]

class SecurityManager:
    """
    消息安全管理器
    支持端到端加密、访问控制、审计日志和身份验证
    """
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.encryption_manager = EncryptionManager(config)
        self.auth_manager = AuthenticationManager(config)
        self.authz_manager = AuthorizationManager(config)
        self.audit_logger = AuditLogger(config)
        
        # 速率限制
        self.rate_limits: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._rate_limit_lock = threading.Lock()
        
        # 运行状态
        self._running = False
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """启动安全管理器"""
        if self._running:
            return
        
        self._running = True
        
        # 启动清理任务
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("安全管理器已启动")
    
    async def stop(self):
        """停止安全管理器"""
        if not self._running:
            return
        
        self._running = False
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        logger.info("安全管理器已停止")
    
    async def _cleanup_loop(self):
        """清理循环"""
        while self._running:
            try:
                await asyncio.sleep(3600)  # 每小时清理一次
                
                # 清理过期的速率限制记录
                self._cleanup_rate_limits()
                
                # 轮换加密密钥
                self.encryption_manager.rotate_keys()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"清理任务出错: {e}")
    
    def _cleanup_rate_limits(self):
        """清理速率限制记录"""
        current_time = time.time()
        cutoff_time = current_time - 60  # 保留最近1分钟的记录
        
        with self._rate_limit_lock:
            for client_id, timestamps in self.rate_limits.items():
                # 移除过期的时间戳
                while timestamps and timestamps[0] < cutoff_time:
                    timestamps.popleft()
    
    def authenticate(self, auth_type: str, credentials: Dict[str, str], 
                    ip_address: Optional[str] = None) -> Optional[User]:
        """认证用户"""
        user = None
        
        try:
            if auth_type == 'api_key':
                api_key = credentials.get('api_key')
                if api_key:
                    user = self.auth_manager.authenticate_api_key(api_key)
            
            elif auth_type == 'jwt':
                token = credentials.get('token')
                if token:
                    user = self.auth_manager.authenticate_jwt(token)
            
            # 记录认证事件
            result = 'success' if user else 'failure'
            self.audit_logger.log_event(
                AuditEventType.AUTHENTICATION,
                user.id if user else None,
                f"auth:{auth_type}",
                "authenticate",
                result,
                ip_address=ip_address,
                details={'auth_type': auth_type}
            )
            
            return user
        
        except Exception as e:
            logger.error(f"认证失败: {e}")
            self.audit_logger.log_event(
                AuditEventType.AUTHENTICATION,
                None,
                f"auth:{auth_type}",
                "authenticate",
                "error",
                ip_address=ip_address,
                details={'error': str(e)}
            )
            return None
    
    def authorize(self, user: User, resource: str, action: str,
                 ip_address: Optional[str] = None) -> bool:
        """授权检查"""
        try:
            # IP白名单/黑名单检查
            if ip_address:
                if self.config.ip_blacklist and ip_address in self.config.ip_blacklist:
                    self.audit_logger.log_event(
                        AuditEventType.ACCESS_DENIED,
                        user.id,
                        resource,
                        action,
                        "denied",
                        ip_address=ip_address,
                        details={'reason': 'ip_blacklisted'}
                    )
                    return False
                
                if self.config.ip_whitelist and ip_address not in self.config.ip_whitelist:
                    self.audit_logger.log_event(
                        AuditEventType.ACCESS_DENIED,
                        user.id,
                        resource,
                        action,
                        "denied",
                        ip_address=ip_address,
                        details={'reason': 'ip_not_whitelisted'}
                    )
                    return False
            
            # 速率限制检查
            if not self._check_rate_limit(user.id, ip_address):
                self.audit_logger.log_event(
                    AuditEventType.ACCESS_DENIED,
                    user.id,
                    resource,
                    action,
                    "denied",
                    ip_address=ip_address,
                    details={'reason': 'rate_limit_exceeded'}
                )
                return False
            
            # 权限检查
            authorized = self.authz_manager.check_permission(user, resource, action)
            
            result = 'success' if authorized else 'denied'
            self.audit_logger.log_event(
                AuditEventType.AUTHORIZATION,
                user.id,
                resource,
                action,
                result,
                ip_address=ip_address
            )
            
            return authorized
        
        except Exception as e:
            logger.error(f"授权检查失败: {e}")
            self.audit_logger.log_event(
                AuditEventType.AUTHORIZATION,
                user.id,
                resource,
                action,
                "error",
                ip_address=ip_address,
                details={'error': str(e)}
            )
            return False
    
    def _check_rate_limit(self, user_id: str, ip_address: Optional[str] = None) -> bool:
        """检查速率限制"""
        if not self.config.rate_limiting_enabled:
            return True
        
        current_time = time.time()
        cutoff_time = current_time - 60  # 1分钟窗口
        
        # 检查用户级别的速率限制
        client_id = f"user:{user_id}"
        
        with self._rate_limit_lock:
            timestamps = self.rate_limits[client_id]
            
            # 移除过期的时间戳
            while timestamps and timestamps[0] < cutoff_time:
                timestamps.popleft()
            
            # 检查是否超过限制
            if len(timestamps) >= self.config.max_requests_per_minute:
                return False
            
            # 记录当前请求
            timestamps.append(current_time)
        
        return True
    
    def encrypt_message(self, message: bytes, user: User) -> Dict[str, Any]:
        """加密消息"""
        try:
            encrypted_data = self.encryption_manager.encrypt_message(message)
            
            self.audit_logger.log_event(
                AuditEventType.ENCRYPTION,
                user.id,
                "message",
                "encrypt",
                "success",
                details={'algorithm': encrypted_data.get('algorithm', 'none')}
            )
            
            return encrypted_data
        
        except Exception as e:
            logger.error(f"消息加密失败: {e}")
            self.audit_logger.log_event(
                AuditEventType.ENCRYPTION,
                user.id,
                "message",
                "encrypt",
                "error",
                details={'error': str(e)}
            )
            raise
    
    def decrypt_message(self, encrypted_data: Dict[str, Any], user: User) -> bytes:
        """解密消息"""
        try:
            message = self.encryption_manager.decrypt_message(encrypted_data)
            
            self.audit_logger.log_event(
                AuditEventType.DECRYPTION,
                user.id,
                "message",
                "decrypt",
                "success",
                details={'algorithm': encrypted_data.get('algorithm', 'none')}
            )
            
            return message
        
        except Exception as e:
            logger.error(f"消息解密失败: {e}")
            self.audit_logger.log_event(
                AuditEventType.DECRYPTION,
                user.id,
                "message",
                "decrypt",
                "error",
                details={'error': str(e)}
            )
            raise
    
    def validate_message_size(self, message: bytes) -> bool:
        """验证消息大小"""
        return len(message) <= self.config.max_message_size
    
    def get_security_stats(self) -> Dict[str, Any]:
        """获取安全统计信息"""
        return {
            'users': {
                'total': len(self.auth_manager.users),
                'active': sum(1 for u in self.auth_manager.users.values() if u.is_active)
            },
            'api_keys': {
                'total': len(self.auth_manager.api_keys)
            },
            'audit_events': {
                'total': len(self.audit_logger.audit_events),
                'violations': len(self.audit_logger.get_security_violations())
            },
            'encryption': {
                'enabled': self.config.encryption_enabled,
                'type': self.config.encryption_type.value,
                'keys_count': len(self.encryption_manager.symmetric_keys) + len(self.encryption_manager.asymmetric_keys)
            }
        }
    
    def create_user(self, username: str, email: Optional[str] = None,
                   roles: Set[str] = None) -> User:
        """创建用户"""
        return self.auth_manager.create_user(username, email, roles)
    
    def generate_api_key(self, user_id: str) -> str:
        """生成API密钥"""
        return self.auth_manager.generate_api_key(user_id)
    
    def generate_jwt_token(self, user_id: str) -> str:
        """生成JWT令牌"""
        return self.auth_manager.generate_jwt_token(user_id)
    
    def get_audit_events(self, **kwargs) -> List[Dict[str, Any]]:
        """获取审计事件"""
        events = self.audit_logger.get_audit_events(**kwargs)
        return [event.to_dict() for event in events]
    
    def get_security_violations(self) -> List[Dict[str, Any]]:
        """获取安全违规事件"""
        violations = self.audit_logger.get_security_violations()
        return [violation.to_dict() for violation in violations]

# 安全管理器工厂
class SecurityManagerFactory:
    """安全管理器工厂"""
    
    @staticmethod
    def create_security_manager(
        config: Optional[SecurityConfig] = None
    ) -> SecurityManager:
        """创建安全管理器"""
        if config is None:
            config = SecurityConfig()
        
        return SecurityManager(config) 