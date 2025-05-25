# 微服务安全性增强方案

## 概述

索克生活平台的安全性是保护用户健康数据和隐私的关键。本文档提供全面的安全加固方案。

## 核心安全措施

### 1. JWT 密钥管理

```python
# jwt_key_manager.py
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
import base64

class JWTKeyManager:
    def __init__(self, key_vault_url: str = None):
        self.key_vault_url = key_vault_url
        self._private_key = None
        self._public_key = None
    
    def generate_rsa_keypair(self):
        """生成 RSA 密钥对用于 JWT 签名"""
        self._private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self._public_key = self._private_key.public_key()
    
    def save_keys_to_vault(self):
        """将密钥保存到密钥管理服务"""
        private_pem = self._private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(
                os.environ.get('KEY_ENCRYPTION_PASSWORD', '').encode()
            )
        )
        
        public_pem = self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # 保存到密钥管理服务（如 HashiCorp Vault）
        # vault_client.save_secret('jwt-private-key', private_pem)
        # vault_client.save_secret('jwt-public-key', public_pem)
    
    @classmethod
    def from_environment(cls):
        """从环境变量加载密钥"""
        instance = cls()
        instance._load_from_env()
        return instance
```

### 2. API 请求签名验证

```python
# api_signature.py
import hmac
import hashlib
import time
from typing import Dict, Optional

class APISignatureValidator:
    def __init__(self, secret_key: str, max_timestamp_diff: int = 300):
        self.secret_key = secret_key.encode()
        self.max_timestamp_diff = max_timestamp_diff
    
    def generate_signature(
        self, 
        method: str, 
        path: str, 
        params: Dict[str, str], 
        timestamp: str
    ) -> str:
        """生成请求签名"""
        # 构建待签名字符串
        sorted_params = '&'.join(f"{k}={v}" for k, v in sorted(params.items()))
        message = f"{method.upper()}\n{path}\n{sorted_params}\n{timestamp}"
        
        # 计算 HMAC-SHA256
        signature = hmac.new(
            self.secret_key,
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def validate_signature(
        self,
        method: str,
        path: str,
        params: Dict[str, str],
        timestamp: str,
        signature: str
    ) -> bool:
        """验证请求签名"""
        # 检查时间戳
        current_time = int(time.time())
        request_time = int(timestamp)
        
        if abs(current_time - request_time) > self.max_timestamp_diff:
            return False
        
        # 验证签名
        expected_signature = self.generate_signature(method, path, params, timestamp)
        return hmac.compare_digest(signature, expected_signature)

# FastAPI 中间件实现
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class SignatureMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, validator: APISignatureValidator):
        super().__init__(app)
        self.validator = validator
    
    async def dispatch(self, request: Request, call_next):
        # 跳过不需要签名的路径
        if request.url.path in ['/health', '/docs', '/openapi.json']:
            return await call_next(request)
        
        # 获取签名相关头部
        signature = request.headers.get('X-Signature')
        timestamp = request.headers.get('X-Timestamp')
        
        if not signature or not timestamp:
            raise HTTPException(status_code=401, detail="Missing signature")
        
        # 构建参数字典
        params = dict(request.query_params)
        
        # 验证签名
        if not self.validator.validate_signature(
            request.method,
            request.url.path,
            params,
            timestamp,
            signature
        ):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        return await call_next(request)
```

### 3. 敏感数据加密

```python
# data_encryption.py
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import json
from typing import Any, Dict

class DataEncryption:
    def __init__(self, master_key: str):
        # 从主密钥派生加密密钥
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'stable_salt',  # 生产环境应使用随机盐
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        self.cipher = Fernet(key)
    
    def encrypt_field(self, data: Any) -> str:
        """加密单个字段"""
        json_data = json.dumps(data)
        encrypted = self.cipher.encrypt(json_data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_field(self, encrypted_data: str) -> Any:
        """解密单个字段"""
        decoded = base64.urlsafe_b64decode(encrypted_data)
        decrypted = self.cipher.decrypt(decoded)
        return json.loads(decrypted.decode())
    
    def encrypt_pii_fields(self, data: Dict[str, Any], pii_fields: list) -> Dict[str, Any]:
        """加密 PII（个人身份信息）字段"""
        encrypted_data = data.copy()
        
        for field in pii_fields:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt_field(encrypted_data[field])
        
        return encrypted_data
```

### 4. 零信任网络架构

```python
# zero_trust_auth.py
from typing import List, Dict, Optional
import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

class ZeroTrustAuthenticator:
    def __init__(self, public_key: str):
        self.public_key = public_key
        self.security = HTTPBearer()
    
    async def verify_service_identity(
        self, 
        credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())
    ) -> Dict[str, Any]:
        """验证服务身份"""
        token = credentials.credentials
        
        try:
            # 验证服务令牌
            payload = jwt.decode(
                token,
                self.public_key,
                algorithms=["RS256"],
                options={"verify_exp": True}
            )
            
            # 验证服务权限
            if not self._verify_service_permissions(payload):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    def _verify_service_permissions(self, payload: Dict[str, Any]) -> bool:
        """验证服务权限"""
        service_name = payload.get("service_name")
        requested_resources = payload.get("resources", [])
        
        # 实现基于策略的访问控制
        allowed_resources = self._get_allowed_resources(service_name)
        
        return all(res in allowed_resources for res in requested_resources)
```

### 5. 安全配置管理

```yaml
# security-config.yaml
security:
  # JWT 配置
  jwt:
    algorithm: RS256
    public_key_path: /secrets/jwt-public.pem
    private_key_path: /secrets/jwt-private.pem
    expire_minutes: 60
    refresh_expire_minutes: 1440
  
  # API 签名配置  
  api_signature:
    enabled: true
    algorithm: HMAC-SHA256
    max_timestamp_diff: 300
  
  # 加密配置
  encryption:
    algorithm: AES-256-GCM
    key_derivation: PBKDF2
    iterations: 100000
    pii_fields:
      - phone
      - email
      - id_card
      - medical_record
  
  # TLS 配置
  tls:
    enabled: true
    cert_path: /certs/server.crt
    key_path: /certs/server.key
    ca_path: /certs/ca.crt
    verify_client: true
  
  # 速率限制
  rate_limiting:
    enabled: true
    default_limit: 100
    window_seconds: 60
    by_ip: true
    by_user: true
    
  # 安全头部
  security_headers:
    X-Content-Type-Options: nosniff
    X-Frame-Options: DENY
    X-XSS-Protection: 1; mode=block
    Strict-Transport-Security: max-age=31536000; includeSubDomains
```

## 部署安全清单

1. **密钥管理**
   - [ ] 使用密钥管理服务（如 HashiCorp Vault）
   - [ ] 定期轮换密钥
   - [ ] 密钥加密存储

2. **网络安全**
   - [ ] 启用 mTLS 进行服务间通信
   - [ ] 实施网络隔离
   - [ ] 配置防火墙规则

3. **身份认证**
   - [ ] 实施多因素认证
   - [ ] 使用短期令牌
   - [ ] 实施会话管理

4. **审计日志**
   - [ ] 记录所有安全事件
   - [ ] 实施日志完整性保护
   - [ ] 定期审计日志分析

5. **漏洞管理**
   - [ ] 定期安全扫描
   - [ ] 及时更新依赖
   - [ ] 安全代码审查 