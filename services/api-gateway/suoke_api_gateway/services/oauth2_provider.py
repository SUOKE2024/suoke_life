"""
oauth2_provider - 索克生活项目模块
"""

from ..core.config import get_settings
from ..core.logging import get_logger
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, Any, Optional, List, Set
from urllib.parse import urlencode, parse_qs, urlparse
import base64
import hashlib
import jwt
import secrets
import time

#! / usr / bin / env python
# - * - coding: utf - 8 - * -

"""
OAuth2 / OIDC 认证提供者

实现标准的 OAuth2 授权码流程和 OIDC 协议。
"""




logger = get_logger(__name__)
settings = get_settings()

class GrantType(Enum):
    """授权类型"""
    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    REFRESH_TOKEN = "refresh_token"
    IMPLICIT = "implicit"
    PASSWORD = "password"

class ResponseType(Enum):
    """响应类型"""
    CODE = "code"
    TOKEN = "token"
    ID_TOKEN = "id_token"

class TokenType(Enum):
    """令牌类型"""
    ACCESS_TOKEN = "access_token"
    REFRESH_TOKEN = "refresh_token"
    ID_TOKEN = "id_token"

@dataclass
class OAuthClient:
    """OAuth 客户端"""
    client_id: str
    client_secret: str
    client_name: str
    redirect_uris: List[str]
    grant_types: List[str]
    response_types: List[str]
    scope: str
    is_active: bool = True
    created_at: float = None

    def __post_init__(self)-> None:
        """TODO: 添加文档字符串"""
        if self.created_at is None:
            self.created_at = time.time()

    def validate_redirect_uri(self, redirect_uri: str)-> bool:
        """验证重定向URI"""
        return redirect_uri in self.redirect_uris

    def validate_grant_type(self, grant_type: str)-> bool:
        """验证授权类型"""
        return grant_type in self.grant_types

    def validate_response_type(self, response_type: str)-> bool:
        """验证响应类型"""
        return response_type in self.response_types

@dataclass
class AuthorizationCode:
    """授权码"""
    code: str
    client_id: str
    user_id: str
    redirect_uri: str
    scope: str
    code_challenge: Optional[str] = None
    code_challenge_method: Optional[str] = None
    expires_at: float = None
    is_used: bool = False

    def __post_init__(self)-> None:
        """TODO: 添加文档字符串"""
        if self.expires_at is None:
            self.expires_at = time.time() + 600  # 10分钟过期

    def is_expired(self)-> bool:
        """检查是否过期"""
        return time.time() > self.expires_at

    def validate_pkce(self, code_verifier: str)-> bool:
        """验证 PKCE"""
        if not self.code_challenge:
            return True  # 没有 PKCE 挑战

        if self.code_challenge_method == "S256":
            # SHA256 哈希
            digest = hashlib.sha256(code_verifier.encode()).digest()
            challenge = base64.urlsafe_b64encode(digest).decode().rstrip(" = ")
            return challenge == self.code_challenge
        elif self.code_challenge_method == "plain":
            # 明文
            return code_verifier == self.code_challenge

        return False

@dataclass
class AccessToken:
    """访问令牌"""
    token: str
    client_id: str
    user_id: Optional[str]
    scope: str
    token_type: str = "Bearer"
    expires_at: float = None

    def __post_init__(self)-> None:
        """TODO: 添加文档字符串"""
        if self.expires_at is None:
            self.expires_at = time.time() + 3600  # 1小时过期

    def is_expired(self)-> bool:
        """检查是否过期"""
        return time.time() > self.expires_at

    def to_dict(self)-> Dict[str, Any]:
        """转换为字典"""
        return {
            "access_token": self.token,
            "token_type": self.token_type,
            "expires_in": max(0, int(self.expires_at - time.time())),
            "scope": self.scope,
        }

@dataclass
class RefreshToken:
    """刷新令牌"""
    token: str
    client_id: str
    user_id: Optional[str]
    scope: str
    expires_at: float = None

    def __post_init__(self)-> None:
        """TODO: 添加文档字符串"""
        if self.expires_at is None:
            self.expires_at = time.time() + 86400 * 30  # 30天过期

    def is_expired(self)-> bool:
        """检查是否过期"""
        return time.time() > self.expires_at

@dataclass
class IDToken:
    """ID 令牌"""
    token: str
    client_id: str
    user_id: str
    expires_at: float = None

    def __post_init__(self)-> None:
        """TODO: 添加文档字符串"""
        if self.expires_at is None:
            self.expires_at = time.time() + 3600  # 1小时过期

    def is_expired(self)-> bool:
        """检查是否过期"""
        return time.time() > self.expires_at

class OAuth2Provider:
    """OAuth2 / OIDC 提供者"""

    def __init__(self)-> None:
        """TODO: 添加文档字符串"""
        # 存储
        self.clients: Dict[str, OAuthClient] = {}
        self.authorization_codes: Dict[str, AuthorizationCode] = {}
        self.access_tokens: Dict[str, AccessToken] = {}
        self.refresh_tokens: Dict[str, RefreshToken] = {}
        self.id_tokens: Dict[str, IDToken] = {}

        # JWT 密钥
        self._private_key = None
        self._public_key = None
        self._generate_keys()

        # 配置
        self.issuer = settings.oauth2_issuer or "https: / /api.suoke.life"
        self.authorization_endpoint = f"{self.issuer} / oauth2 / authorize"
        self.token_endpoint = f"{self.issuer} / oauth2 / token"
        self.userinfo_endpoint = f"{self.issuer} / oauth2 / userinfo"
        self.jwks_endpoint = f"{self.issuer} / oauth2 / jwks"

        # 注册默认客户端
        self._register_default_clients()

    def _generate_keys(self)-> None:
        """生成 JWT 密钥对"""
        self._private_key = rsa.generate_private_key(
            public_exponent = 65537,
            key_size = 2048,
        )
        self._public_key = self._private_key.public_key()

        logger.info("Generated OAuth2 JWT key pair")

    def _register_default_clients(self)-> None:
        """注册默认客户端"""
        # 索克生活移动应用
        self.register_client(
            client_id = "suoke_mobile_app",
            client_secret = secrets.token_urlsafe(32),
            client_name = "索克生活移动应用",
            redirect_uris = ["suoke: / /oauth / callback"],
            grant_types = ["authorization_code", "refresh_token"],
            response_types = ["code"],
            scope = "openid profile health_data",
        )

        # 索克生活 Web 应用
        self.register_client(
            client_id = "suoke_web_app",
            client_secret = secrets.token_urlsafe(32),
            client_name = "索克生活 Web 应用",
            redirect_uris = ["https: / /app.suoke.life / oauth / callback"],
            grant_types = ["authorization_code", "refresh_token"],
            response_types = ["code"],
            scope = "openid profile health_data",
        )

        # 第三方集成客户端
        self.register_client(
            client_id = "third_party_integration",
            client_secret = secrets.token_urlsafe(32),
            client_name = "第三方集成",
            redirect_uris = ["https: / /example.com / oauth / callback"],
            grant_types = ["client_credentials"],
            response_types = ["token"],
            scope = "api_access",
        )

    def register_client(
        self,
        client_id: str,
        client_secret: str,
        client_name: str,
        redirect_uris: List[str],
        grant_types: List[str],
        response_types: List[str],
        scope: str,
    )-> OAuthClient:
        """注册客户端"""
        client = OAuthClient(
            client_id = client_id,
            client_secret = client_secret,
            client_name = client_name,
            redirect_uris = redirect_uris,
            grant_types = grant_types,
            response_types = response_types,
            scope = scope,
        )

        self.clients[client_id] = client

        logger.info(
            "OAuth2 client registered",
            client_id = client_id,
            client_name = client_name,
        )

        return client

    def get_client(self, client_id: str)-> Optional[OAuthClient]:
        """获取客户端"""
        return self.clients.get(client_id)

    def validate_client(self, client_id: str, client_secret: str)-> bool:
        """验证客户端"""
        client = self.get_client(client_id)
        if not client or not client.is_active:
            return False

        return client.client_secret == client_secret

    def create_authorization_url(
        self,
        client_id: str,
        redirect_uri: str,
        scope: str,
        response_type: str = "code",
        state: Optional[str] = None,
        code_challenge: Optional[str] = None,
        code_challenge_method: Optional[str] = None,
    )-> str:
        """创建授权URL"""
        params = {
            "response_type": response_type,
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
        }

        if state:
            params["state"] = state

        if code_challenge:
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = code_challenge_method or "S256"

        return f"{self.authorization_endpoint}?{urlencode(params)}"

    def handle_authorization_request(
        self,
        client_id: str,
        redirect_uri: str,
        response_type: str,
        scope: str,
        user_id: str,
        state: Optional[str] = None,
        code_challenge: Optional[str] = None,
        code_challenge_method: Optional[str] = None,
    )-> Dict[str, Any]:
        """处理授权请求"""
        # 验证客户端
        client = self.get_client(client_id)
        if not client or not client.is_active:
            return {"error": "invalid_client"}

        # 验证重定向URI
        if not client.validate_redirect_uri(redirect_uri):
            return {"error": "invalid_redirect_uri"}

        # 验证响应类型
        if not client.validate_response_type(response_type):
            return {"error": "unsupported_response_type"}

        if response_type == "code":
            # 授权码流程
            code = secrets.token_urlsafe(32)
            auth_code = AuthorizationCode(
                code = code,
                client_id = client_id,
                user_id = user_id,
                redirect_uri = redirect_uri,
                scope = scope,
                code_challenge = code_challenge,
                code_challenge_method = code_challenge_method,
            )

            self.authorization_codes[code] = auth_code

            # 构建重定向URL
            params = {"code": code}
            if state:
                params["state"] = state

            redirect_url = f"{redirect_uri}?{urlencode(params)}"

            return {
                "success": True,
                "redirect_url": redirect_url,
                "code": code,
            }

        elif response_type == "token":
            # 隐式流程
            access_token = self._create_access_token(client_id, user_id, scope)

            # 构建重定向URL（使用片段）
            params = {
                "access_token": access_token.token,
                "token_type": access_token.token_type,
                "expires_in": int(access_token.expires_at - time.time()),
                "scope": scope,
            }
            if state:
                params["state"] = state

            redirect_url = f"{redirect_uri}#{urlencode(params)}"

            return {
                "success": True,
                "redirect_url": redirect_url,
                "access_token": access_token.to_dict(),
            }

        return {"error": "unsupported_response_type"}

    def exchange_code_for_tokens(
        self,
        client_id: str,
        client_secret: str,
        code: str,
        redirect_uri: str,
        code_verifier: Optional[str] = None,
    )-> Dict[str, Any]:
        """交换授权码获取令牌"""
        # 验证客户端
        if not self.validate_client(client_id, client_secret):
            return {"error": "invalid_client"}

        # 获取授权码
        auth_code = self.authorization_codes.get(code)
        if not auth_code:
            return {"error": "invalid_grant"}

        # 检查授权码是否过期或已使用
        if auth_code.is_expired() or auth_code.is_used:
            return {"error": "invalid_grant"}

        # 验证客户端ID
        if auth_code.client_id ! = client_id:
            return {"error": "invalid_grant"}

        # 验证重定向URI
        if auth_code.redirect_uri ! = redirect_uri:
            return {"error": "invalid_grant"}

        # 验证 PKCE
        if auth_code.code_challenge and not auth_code.validate_pkce(code_verifier or ""):
            return {"error": "invalid_grant"}

        # 标记授权码为已使用
        auth_code.is_used = True

        # 创建令牌
        access_token = self._create_access_token(
            client_id, auth_code.user_id, auth_code.scope
        )
        refresh_token = self._create_refresh_token(
            client_id, auth_code.user_id, auth_code.scope
        )

        result = {
            **access_token.to_dict(),
            "refresh_token": refresh_token.token,
        }

        # 如果包含 openid scope，创建 ID 令牌
        if "openid" in auth_code.scope:
            id_token = self._create_id_token(client_id, auth_code.user_id)
            result["id_token"] = id_token.token

        return result

    def refresh_access_token(
        self,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        scope: Optional[str] = None,
    )-> Dict[str, Any]:
        """刷新访问令牌"""
        # 验证客户端
        if not self.validate_client(client_id, client_secret):
            return {"error": "invalid_client"}

        # 获取刷新令牌
        refresh_token_obj = self.refresh_tokens.get(refresh_token)
        if not refresh_token_obj:
            return {"error": "invalid_grant"}

        # 检查刷新令牌是否过期
        if refresh_token_obj.is_expired():
            return {"error": "invalid_grant"}

        # 验证客户端ID
        if refresh_token_obj.client_id ! = client_id:
            return {"error": "invalid_grant"}

        # 使用原始 scope 或请求的 scope（不能超出原始范围）
        token_scope = scope or refresh_token_obj.scope
        if scope and not self._is_scope_subset(scope, refresh_token_obj.scope):
            return {"error": "invalid_scope"}

        # 创建新的访问令牌
        access_token = self._create_access_token(
            client_id, refresh_token_obj.user_id, token_scope
        )

        result = access_token.to_dict()

        # 如果包含 openid scope，创建新的 ID 令牌
        if "openid" in token_scope and refresh_token_obj.user_id:
            id_token = self._create_id_token(client_id, refresh_token_obj.user_id)
            result["id_token"] = id_token.token

        return result

    def client_credentials_grant(
        self,
        client_id: str,
        client_secret: str,
        scope: Optional[str] = None,
    )-> Dict[str, Any]:
        """客户端凭证授权"""
        # 验证客户端
        if not self.validate_client(client_id, client_secret):
            return {"error": "invalid_client"}

        client = self.get_client(client_id)
        if not client.validate_grant_type("client_credentials"):
            return {"error": "unauthorized_client"}

        # 使用客户端默认 scope 或请求的 scope
        token_scope = scope or client.scope

        # 创建访问令牌（无用户ID）
        access_token = self._create_access_token(client_id, None, token_scope)

        return access_token.to_dict()

    def validate_access_token(self, token: str)-> Optional[AccessToken]:
        """验证访问令牌"""
        access_token = self.access_tokens.get(token)
        if not access_token or access_token.is_expired():
            return None

        return access_token

    def get_userinfo(self, access_token: str)-> Dict[str, Any]:
        """获取用户信息"""
        token_obj = self.validate_access_token(access_token)
        if not token_obj or not token_obj.user_id:
            return {"error": "invalid_token"}

        # 这里应该从用户服务获取用户信息
        # 暂时返回模拟数据
        return {
            "sub": token_obj.user_id,
            "name": f"用户{token_obj.user_id}",
            "email": f"user{token_obj.user_id}@suoke.life",
            "email_verified": True,
            "picture": f"https: / /api.suoke.life / users / {token_obj.user_id} / avatar",
        }

    def get_jwks(self)-> Dict[str, Any]:
        """获取 JSON Web Key Set"""
        public_numbers = self._public_key.public_numbers()

        # 计算密钥ID
        key_id = hashlib.sha256(
            self._public_key.public_bytes(
                encoding = serialization.Encoding.DER,
                format = serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        ).hexdigest()[:16]

        return {
            "keys": [
                {
                    "kty": "RSA",
                    "use": "sig",
                    "kid": key_id,
                    "n": base64.urlsafe_b64encode(
                        public_numbers.n.to_bytes(
                            (public_numbers.n.bit_length() + 7) / / 8, "big"
                        )
                    ).decode().rstrip(" = "),
                    "e": base64.urlsafe_b64encode(
                        public_numbers.e.to_bytes(
                            (public_numbers.e.bit_length() + 7) / / 8, "big"
                        )
                    ).decode().rstrip(" = "),
                    "alg": "RS256",
                }
            ]
        }

    def get_openid_configuration(self)-> Dict[str, Any]:
        """获取 OpenID Connect 配置"""
        return {
            "issuer": self.issuer,
            "authorization_endpoint": self.authorization_endpoint,
            "token_endpoint": self.token_endpoint,
            "userinfo_endpoint": self.userinfo_endpoint,
            "jwks_uri": self.jwks_endpoint,
            "response_types_supported": ["code", "token", "id_token"],
            "grant_types_supported": [
                "authorization_code",
                "client_credentials",
                "refresh_token",
                "implicit",
            ],
            "subject_types_supported": ["public"],
            "id_token_signing_alg_values_supported": ["RS256"],
            "scopes_supported": ["openid", "profile", "email", "health_data", "api_access"],
            "token_endpoint_auth_methods_supported": ["client_secret_basic", "client_secret_post"],
            "code_challenge_methods_supported": ["S256", "plain"],
        }

    def _create_access_token(
        self, client_id: str, user_id: Optional[str], scope: str
    )-> AccessToken:
        """创建访问令牌"""
        token = secrets.token_urlsafe(32)
        access_token = AccessToken(
            token = token,
            client_id = client_id,
            user_id = user_id,
            scope = scope,
        )

        self.access_tokens[token] = access_token
        return access_token

    def _create_refresh_token(
        self, client_id: str, user_id: Optional[str], scope: str
    )-> RefreshToken:
        """创建刷新令牌"""
        token = secrets.token_urlsafe(32)
        refresh_token = RefreshToken(
            token = token,
            client_id = client_id,
            user_id = user_id,
            scope = scope,
        )

        self.refresh_tokens[token] = refresh_token
        return refresh_token

    def _create_id_token(self, client_id: str, user_id: str)-> IDToken:
        """创建 ID 令牌"""
        now = time.time()

        payload = {
            "iss": self.issuer,
            "sub": user_id,
            "aud": client_id,
            "exp": int(now + 3600),  # 1小时过期
            "iat": int(now),
            "auth_time": int(now),
            "nonce": secrets.token_urlsafe(16),
        }

        # 签名 JWT
        token = jwt.encode(
            payload,
            self._private_key,
            algorithm = "RS256",
            headers = {"typ": "JWT", "alg": "RS256"},
        )

        id_token = IDToken(
            token = token,
            client_id = client_id,
            user_id = user_id,
        )

        self.id_tokens[token] = id_token
        return id_token

    def _is_scope_subset(self, requested_scope: str, original_scope: str)-> bool:
        """检查请求的 scope 是否是原始 scope 的子集"""
        requested_scopes = set(requested_scope.split())
        original_scopes = set(original_scope.split())
        return requested_scopes.issubset(original_scopes)

    def cleanup_expired_tokens(self)-> None:
        """清理过期令牌"""
        current_time = time.time()

        # 清理过期的授权码
        expired_codes = [
            code for code, auth_code in self.authorization_codes.items()
            if auth_code.is_expired()
        ]
        for code in expired_codes:
            del self.authorization_codes[code]

        # 清理过期的访问令牌
        expired_access_tokens = [
            token for token, access_token in self.access_tokens.items()
            if access_token.is_expired()
        ]
        for token in expired_access_tokens:
            del self.access_tokens[token]

        # 清理过期的刷新令牌
        expired_refresh_tokens = [
            token for token, refresh_token in self.refresh_tokens.items()
            if refresh_token.is_expired()
        ]
        for token in expired_refresh_tokens:
            del self.refresh_tokens[token]

        # 清理过期的 ID 令牌
        expired_id_tokens = [
            token for token, id_token in self.id_tokens.items()
            if id_token.is_expired()
        ]
        for token in expired_id_tokens:
            del self.id_tokens[token]

        if expired_codes or expired_access_tokens or expired_refresh_tokens or expired_id_tokens:
            logger.info(
                "Cleaned up expired OAuth2 tokens",
                expired_codes = len(expired_codes),
                expired_access_tokens = len(expired_access_tokens),
                expired_refresh_tokens = len(expired_refresh_tokens),
                expired_id_tokens = len(expired_id_tokens),
            )

    def get_stats(self)-> Dict[str, Any]:
        """获取统计信息"""
        return {
            "clients": len(self.clients),
            "authorization_codes": len(self.authorization_codes),
            "access_tokens": len(self.access_tokens),
            "refresh_tokens": len(self.refresh_tokens),
            "id_tokens": len(self.id_tokens),
        }

# 全局 OAuth2 提供者实例
oauth2_provider = OAuth2Provider()

def get_oauth2_provider()-> OAuth2Provider:
    """获取全局 OAuth2 提供者"""
    return oauth2_provider