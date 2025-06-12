"""
oauth - 索克生活项目模块
"""

import json
import secrets
import urllib.parse
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, Optional

import httpx
from auth_service.config import get_settings

"""OAuth认证管理器"""


class OAuthProvider(str, Enum):
    """OAuth提供商枚举"""

    GOOGLE = "google"
    GITHUB = "github"
    WECHAT = "wechat"
    QQ = "qq"
    WEIBO = "weibo"


class OAuthManager:
    """OAuth认证管理器"""

    def __init__(self) -> None:
        """TODO: 添加文档字符串"""
        self.settings = get_settings()
        self.providers_config = {
            OAuthProvider.GOOGLE: {
                "client_id": getattr(self.settings, "GOOGLE_CLIENT_ID", ""),
                "client_secret": getattr(self.settings, "GOOGLE_CLIENT_SECRET", ""),
                "auth_url": "https: //accounts.google.com / o / oauth2 / v2 / auth",
                "token_url": "https: //oauth2.googleapis.com / token",
                "user_info_url": "https: //www.googleapis.com / oauth2 / v2 / userinfo",
                "scope": "openid email profile",
            },
            OAuthProvider.GITHUB: {
                "client_id": getattr(self.settings, "GITHUB_CLIENT_ID", ""),
                "client_secret": getattr(self.settings, "GITHUB_CLIENT_SECRET", ""),
                "auth_url": "https: //github.com / login / oauth / authorize",
                "token_url": "https: //github.com / login / oauth / access_token",
                "user_info_url": "https: //api.github.com / user",
                "scope": "user:email",
            },
            OAuthProvider.WECHAT: {
                "client_id": getattr(self.settings, "WECHAT_APP_ID", ""),
                "client_secret": getattr(self.settings, "WECHAT_APP_SECRET", ""),
                "auth_url": "https: //open.weixin.qq.com / connect / qrconnect",
                "token_url": "https: //api.weixin.qq.com / sns / oauth2 / access_token",
                "user_info_url": "https: //api.weixin.qq.com / sns / userinfo",
                "scope": "snsapi_login",
            },
            OAuthProvider.QQ: {
                "client_id": getattr(self.settings, "QQ_APP_ID", ""),
                "client_secret": getattr(self.settings, "QQ_APP_KEY", ""),
                "auth_url": "https: //graph.qq.com / oauth2.0 / authorize",
                "token_url": "https: //graph.qq.com / oauth2.0 / token",
                "user_info_url": "https: //graph.qq.com / user / get_user_info",
                "scope": "get_user_info",
            },
            OAuthProvider.WEIBO: {
                "client_id": getattr(self.settings, "WEIBO_APP_KEY", ""),
                "client_secret": getattr(self.settings, "WEIBO_APP_SECRET", ""),
                "auth_url": "https: //api.weibo.com / oauth2 / authorize",
                "token_url": "https: //api.weibo.com / oauth2 / access_token",
                "user_info_url": "https: //api.weibo.com / 2 / users / show.json",
                "scope": "email",
            },
        }

    def is_provider_supported(self, provider: str) -> bool:
        """检查是否支持指定的OAuth提供商"""
        try:
            return OAuthProvider(provider) in self.providers_config
        except ValueError:
            return False

    def get_authorization_url(
        self,
        provider: str,
        redirect_uri: Optional[str] = None,
        state: Optional[str] = None,
    ) -> str:
        """生成OAuth授权URL"""
        if not self.is_provider_supported(provider):
            raise ValueError(f"不支持的OAuth提供商: {provider}")

        config = self.providers_config[OAuthProvider(provider)]

        # 生成状态参数
        if not state:
            state = secrets.token_urlsafe(32)

        # 设置默认重定向URI
        if not redirect_uri:
            base_url = getattr(self.settings, "BASE_URL", "http: //localhost:8000")
            redirect_uri = f"{base_url} / auth / oauth / callback / {provider}"

        # 构建授权参数
        params = {
            "client_id": config["client_id"],
            "redirect_uri": redirect_uri,
            "scope": config["scope"],
            "response_type": "code",
            "state": state,
        }

        # 特殊处理不同提供商的参数
        if provider == OAuthProvider.WECHAT:
            params["appid"] = config["client_id"]
            params.pop("client_id")

        # 构建完整URL
        query_string = urllib.parse.urlencode(params)
        return f"{config['auth_url']}?{query_string}"

    async def exchange_code_for_token(
        self,
        provider: str,
        code: str,
        state: Optional[str] = None,
        redirect_uri: Optional[str] = None,
    ) -> str:
        """交换授权码获取访问令牌"""
        if not self.is_provider_supported(provider):
            raise ValueError(f"不支持的OAuth提供商: {provider}")

        config = self.providers_config[OAuthProvider(provider)]

        # 设置默认重定向URI
        if not redirect_uri:
            base_url = getattr(self.settings, "BASE_URL", "http: //localhost:8000")
            redirect_uri = f"{base_url} / auth / oauth / callback / {provider}"

        # 构建令牌请求参数
        data = {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "code": code,
            "redirect_uri": redirect_uri,
        }

        # 特殊处理不同提供商的参数
        if provider in [OAuthProvider.GOOGLE, OAuthProvider.GITHUB]:
            data["grant_type"] = "authorization_code"
        elif provider == OAuthProvider.WECHAT:
            data["appid"] = config["client_id"]
            data["secret"] = config["client_secret"]
            data.pop("client_id")
            data.pop("client_secret")

        # 发送令牌请求
        async with httpx.AsyncClient() as client:
            headers = {"Accept": "application / json"}

            if provider == OAuthProvider.GITHUB:
                headers["Accept"] = "application / vnd.github.v3 + json"

            response = await client.post(
                config["token_url"], data=data, headers=headers, timeout=30.0
            )

            if response.status_code != 200:
                raise Exception(f"获取访问令牌失败: {response.text}")

            token_data = response.json()

            # 提取访问令牌
            if "access_token" in token_data:
                return token_data["access_token"]
            else:
                raise Exception(f"响应中未找到访问令牌: {token_data}")

    async def get_user_info(self, provider: str, access_token: str) -> Dict[str, Any]:
        """获取用户信息"""
        if not self.is_provider_supported(provider):
            raise ValueError(f"不支持的OAuth提供商: {provider}")

        config = self.providers_config[OAuthProvider(provider)]

        # 构建请求头
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application / json",
        }

        # 特殊处理不同提供商的认证方式
        if provider == OAuthProvider.QQ:
            # QQ需要先获取OpenID
            openid = await self._get_qq_openid(access_token)
            url = f"{config['user_info_url']}?access_token = {access_token}&oauth_consumer_key = {config['client_id']}&openid = {openid}"
            headers.pop("Authorization")
        elif provider == OAuthProvider.WECHAT:
            # 微信需要OpenID
            openid = await self._get_wechat_openid(access_token)
            url = f"{config['user_info_url']}?access_token = {access_token}&openid = {openid}"
            headers.pop("Authorization")
        else:
            url = config["user_info_url"]

        # 发送用户信息请求
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0)

            if response.status_code != 200:
                raise Exception(f"获取用户信息失败: {response.text}")

            user_data = response.json()

            # 标准化用户信息
            return self._normalize_user_info(provider, user_data)

    def _normalize_user_info(
        self, provider: str, user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """标准化不同提供商的用户信息"""
        normalized = {
            "id": None,
            "username": None,
            "email": None,
            "name": None,
            "avatar_url": None,
            "provider": provider,
            "raw_data": user_data,
        }

        if provider == OAuthProvider.GOOGLE:
            normalized.update(
                {
                    "id": user_data.get("id"),
                    "username": user_data.get("email"),
                    "email": user_data.get("email"),
                    "name": user_data.get("name"),
                    "avatar_url": user_data.get("picture"),
                }
            )
        elif provider == OAuthProvider.GITHUB:
            normalized.update(
                {
                    "id": str(user_data.get("id")),
                    "username": user_data.get("login"),
                    "email": user_data.get("email"),
                    "name": user_data.get("name"),
                    "avatar_url": user_data.get("avatar_url"),
                }
            )
        elif provider == OAuthProvider.WECHAT:
            normalized.update(
                {
                    "id": user_data.get("openid"),
                    "username": user_data.get("nickname"),
                    "name": user_data.get("nickname"),
                    "avatar_url": user_data.get("headimgurl"),
                }
            )
        elif provider == OAuthProvider.QQ:
            normalized.update(
                {
                    "id": user_data.get("openid"),
                    "username": user_data.get("nickname"),
                    "name": user_data.get("nickname"),
                    "avatar_url": user_data.get("figureurl_qq_2")
                    or user_data.get("figureurl_qq_1"),
                }
            )
        elif provider == OAuthProvider.WEIBO:
            normalized.update(
                {
                    "id": str(user_data.get("id")),
                    "username": user_data.get("screen_name"),
                    "name": user_data.get("name"),
                    "avatar_url": user_data.get("avatar_large")
                    or user_data.get("profile_image_url"),
                }
            )

        return normalized

    async def _get_qq_openid(self, access_token: str) -> str:
        """获取QQ用户的OpenID"""
        url = f"https: //graph.qq.com / oauth2.0 / me?access_token = {access_token}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30.0)

            if response.status_code != 200:
                raise Exception(f"获取QQ OpenID失败: {response.text}")

            # QQ返回的是JSONP格式，需要解析
            text = response.text
            if text.startswith("callback("):
                text = text[9:-3]  # 移除callback( 和 );

            data = json.loads(text)
            return data.get("openid")

    async def _get_wechat_openid(self, access_token: str) -> str:
        """获取微信用户的OpenID"""
        # 在实际的微信OAuth流程中，OpenID通常在获取access_token时一起返回
        # 这里是简化实现，实际应该从token响应中获取
        return "mock_wechat_openid"

    def validate_state(self, received_state: str, expected_state: str) -> bool:
        """验证OAuth状态参数"""
        return received_state == expected_state

    def generate_state(self) -> str:
        """生成OAuth状态参数"""
        return secrets.token_urlsafe(32)
