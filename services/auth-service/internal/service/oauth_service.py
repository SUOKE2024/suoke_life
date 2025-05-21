#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OAuth服务模块

提供社交媒体平台OAuth2.0登录支持，包括微信、QQ、微博、GitHub等。
"""
import json
import uuid
import logging
import secrets
from typing import Dict, Any, Optional, List, Tuple
from urllib.parse import urlencode
from datetime import datetime, timedelta

import httpx
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from internal.model.user import User, UserStatusEnum
from internal.model.errors import AuthServiceError, UserNotFoundError, ValidationError
from internal.repository.user_repository import UserRepository
from internal.repository.token_repository import TokenRepository
from internal.service.auth_service import create_tokens, get_password_hash
from internal.db.session import get_session

logger = logging.getLogger(__name__)


class OAuthProvider:
    """OAuth提供商基类"""
    
    def __init__(
        self, 
        client_id: str, 
        client_secret: str, 
        redirect_uri: str, 
        scopes: List[str] = None
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scopes = scopes or []
        
    def get_authorize_url(self) -> str:
        """获取授权URL"""
        raise NotImplementedError()
    
    async def exchange_code(self, code: str) -> Dict[str, Any]:
        """使用授权码交换令牌"""
        raise NotImplementedError()
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """获取用户信息"""
        raise NotImplementedError()
    
    async def normalize_user_info(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """标准化用户信息"""
        raise NotImplementedError()


class WechatOAuthProvider(OAuthProvider):
    """微信OAuth提供商"""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        scopes: List[str] = None
    ):
        scopes = scopes or ["snsapi_userinfo"]
        super().__init__(client_id, client_secret, redirect_uri, scopes)
        self.authorize_url = "https://open.weixin.qq.com/connect/qrconnect"
        self.token_url = "https://api.weixin.qq.com/sns/oauth2/access_token"
        self.userinfo_url = "https://api.weixin.qq.com/sns/userinfo"
    
    def get_authorize_url(self) -> str:
        """获取授权URL"""
        params = {
            "appid": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "state": secrets.token_urlsafe(16)
        }
        return f"{self.authorize_url}?{urlencode(params)}#wechat_redirect"
    
    async def exchange_code(self, code: str) -> Dict[str, Any]:
        """使用授权码交换令牌"""
        params = {
            "appid": self.client_id,
            "secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.token_url, params=params)
            
            if response.status_code != 200:
                logger.error(f"微信OAuth令牌交换失败: {response.text}")
                raise AuthServiceError(
                    "OAuth认证失败", 
                    details={"provider": "wechat", "status": response.status_code}
                )
            
            data = response.json()
            if "errcode" in data and data["errcode"] != 0:
                logger.error(f"微信OAuth令牌交换错误: {data}")
                raise AuthServiceError(
                    f"微信认证错误: {data.get('errmsg', '未知错误')}", 
                    details={"provider": "wechat", "errcode": data["errcode"]}
                )
                
            return data
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """获取用户信息"""
        # 微信API需要同时提供访问令牌和openid
        if not isinstance(access_token, dict) or "openid" not in access_token:
            # 我们预期收到的是一个包含access_token和openid的字典
            if isinstance(access_token, str):
                # 尝试解析为字典
                try:
                    token_data = json.loads(access_token)
                    if not isinstance(token_data, dict) or "openid" not in token_data:
                        raise ValueError("无效的令牌格式")
                    access_token = token_data
                except (json.JSONDecodeError, ValueError):
                    raise AuthServiceError("无效的微信令牌格式")
            else:
                raise AuthServiceError("无效的微信令牌格式")
        
        # 从令牌数据中提取需要的字段
        token = access_token["access_token"]
        openid = access_token["openid"]
        
        params = {
            "access_token": token,
            "openid": openid,
            "lang": "zh_CN"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.userinfo_url, params=params)
            
            if response.status_code != 200:
                logger.error(f"微信用户信息获取失败: {response.text}")
                raise AuthServiceError(
                    "获取用户信息失败", 
                    details={"provider": "wechat", "status": response.status_code}
                )
            
            data = response.json()
            if "errcode" in data and data["errcode"] != 0:
                logger.error(f"微信用户信息获取错误: {data}")
                raise AuthServiceError(
                    f"微信用户信息错误: {data.get('errmsg', '未知错误')}", 
                    details={"provider": "wechat", "errcode": data["errcode"]}
                )
                
            return data
    
    async def normalize_user_info(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """标准化用户信息"""
        return {
            "provider": "wechat",
            "provider_user_id": user_info["openid"],
            "unionid": user_info.get("unionid"),  # 微信特有字段
            "username": f"wx_{user_info['openid'][:8]}",
            "display_name": user_info.get("nickname", "微信用户"),
            "avatar": user_info.get("headimgurl"),
            "email": None,  # 微信不提供邮箱
            "profile_data": {
                "nickname": user_info.get("nickname"),
                "gender": user_info.get("sex"),
                "province": user_info.get("province"),
                "city": user_info.get("city"),
                "country": user_info.get("country"),
                "privilege": user_info.get("privilege"),
            }
        }


class GithubOAuthProvider(OAuthProvider):
    """GitHub OAuth提供商"""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        scopes: List[str] = None
    ):
        scopes = scopes or ["read:user", "user:email"]
        super().__init__(client_id, client_secret, redirect_uri, scopes)
        self.authorize_url = "https://github.com/login/oauth/authorize"
        self.token_url = "https://github.com/login/oauth/access_token"
        self.userinfo_url = "https://api.github.com/user"
        self.user_emails_url = "https://api.github.com/user/emails"
    
    def get_authorize_url(self) -> str:
        """获取授权URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.scopes),
            "state": secrets.token_urlsafe(16)
        }
        return f"{self.authorize_url}?{urlencode(params)}"
    
    async def exchange_code(self, code: str) -> Dict[str, Any]:
        """使用授权码交换令牌"""
        headers = {
            "Accept": "application/json"
        }
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, json=data, headers=headers)
            
            if response.status_code != 200:
                logger.error(f"GitHub OAuth令牌交换失败: {response.text}")
                raise AuthServiceError(
                    "OAuth认证失败", 
                    details={"provider": "github", "status": response.status_code}
                )
            
            try:
                data = response.json()
            except Exception as e:
                logger.error(f"GitHub OAuth响应解析错误: {e}")
                raise AuthServiceError(
                    "OAuth响应解析失败", 
                    details={"provider": "github", "error": str(e)}
                )
            
            if "error" in data:
                logger.error(f"GitHub OAuth令牌交换错误: {data}")
                raise AuthServiceError(
                    f"GitHub认证错误: {data.get('error_description', '未知错误')}", 
                    details={"provider": "github", "error": data["error"]}
                )
                
            return data
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """获取用户信息"""
        # GitHub API需要Authorization: Bearer header
        if isinstance(access_token, dict) and "access_token" in access_token:
            access_token = access_token["access_token"]
            
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        async with httpx.AsyncClient() as client:
            # 获取用户基本信息
            response = await client.get(self.userinfo_url, headers=headers)
            
            if response.status_code != 200:
                logger.error(f"GitHub用户信息获取失败: {response.text}")
                raise AuthServiceError(
                    "获取用户信息失败", 
                    details={"provider": "github", "status": response.status_code}
                )
            
            user_data = response.json()
            
            # 获取用户邮箱 (可能需要额外权限)
            email_response = await client.get(self.user_emails_url, headers=headers)
            email = None
            
            if email_response.status_code == 200:
                emails = email_response.json()
                # 查找主要的且已验证的邮箱
                primary_emails = [e for e in emails if e.get("primary") and e.get("verified")]
                if primary_emails:
                    email = primary_emails[0]["email"]
                else:
                    # 找任何已验证的邮箱
                    verified_emails = [e for e in emails if e.get("verified")]
                    if verified_emails:
                        email = verified_emails[0]["email"]
            
            # 合并用户数据和邮箱信息
            user_data["email"] = email or user_data.get("email")
            
            return user_data
    
    async def normalize_user_info(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """标准化用户信息"""
        # 从登录名生成一个唯一的用户名
        github_login = user_info.get("login", "")
        username = f"github_{github_login}" if github_login else f"github_{uuid.uuid4().hex[:8]}"
        
        return {
            "provider": "github",
            "provider_user_id": str(user_info["id"]),
            "username": username,
            "display_name": user_info.get("name") or github_login or "GitHub用户",
            "email": user_info.get("email"),
            "avatar": user_info.get("avatar_url"),
            "profile_data": {
                "github_username": github_login,
                "bio": user_info.get("bio"),
                "location": user_info.get("location"),
                "company": user_info.get("company"),
                "blog": user_info.get("blog"),
                "twitter_username": user_info.get("twitter_username"),
                "public_repos": user_info.get("public_repos"),
                "followers": user_info.get("followers"),
                "following": user_info.get("following"),
            }
        }


class QQOAuthProvider(OAuthProvider):
    """QQ OAuth提供商"""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        scopes: List[str] = None
    ):
        scopes = scopes or ["get_user_info"]
        super().__init__(client_id, client_secret, redirect_uri, scopes)
        self.authorize_url = "https://graph.qq.com/oauth2.0/authorize"
        self.token_url = "https://graph.qq.com/oauth2.0/token"
        self.openid_url = "https://graph.qq.com/oauth2.0/me"
        self.userinfo_url = "https://graph.qq.com/user/get_user_info"
    
    def get_authorize_url(self) -> str:
        """获取授权URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "state": secrets.token_urlsafe(16)
        }
        return f"{self.authorize_url}?{urlencode(params)}"
    
    async def exchange_code(self, code: str) -> Dict[str, Any]:
        """使用授权码交换令牌"""
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
            "fmt": "json"  # 请求JSON格式响应
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.token_url, params=params)
            
            if response.status_code != 200:
                logger.error(f"QQ OAuth令牌交换失败: {response.text}")
                raise AuthServiceError(
                    "OAuth认证失败", 
                    details={"provider": "qq", "status": response.status_code}
                )
            
            try:
                data = response.json()
                if "error" in data:
                    logger.error(f"QQ OAuth令牌交换错误: {data}")
                    raise AuthServiceError(
                        f"QQ认证错误: {data.get('error_description', '未知错误')}", 
                        details={"provider": "qq", "error": data["error"]}
                    )
            except:
                # QQ返回的可能是URL编码的字符串，需要手动解析
                text = response.text
                result = {}
                for item in text.split("&"):
                    if "=" in item:
                        key, value = item.split("=", 1)
                        result[key] = value
                
                if "access_token" not in result:
                    logger.error(f"QQ OAuth令牌交换错误: {text}")
                    raise AuthServiceError(
                        "无法获取QQ令牌", 
                        details={"provider": "qq", "response": text}
                    )
                    
                data = result
            
            # 获取OpenID
            openid_params = {
                "access_token": data["access_token"],
                "fmt": "json"
            }
            
            openid_response = await client.get(self.openid_url, params=openid_params)
            
            if openid_response.status_code != 200:
                logger.error(f"QQ OpenID获取失败: {openid_response.text}")
                raise AuthServiceError(
                    "获取OpenID失败", 
                    details={"provider": "qq", "status": openid_response.status_code}
                )
            
            try:
                openid_data = openid_response.json()
                if "error" in openid_data:
                    logger.error(f"QQ OpenID获取错误: {openid_data}")
                    raise AuthServiceError(
                        f"QQ OpenID错误: {openid_data.get('error_description', '未知错误')}", 
                        details={"provider": "qq", "error": openid_data["error"]}
                    )
                
                # 合并令牌和OpenID信息
                data["openid"] = openid_data["openid"]
                if "unionid" in openid_data:
                    data["unionid"] = openid_data["unionid"]
                    
            except Exception as e:
                logger.error(f"QQ OpenID解析错误: {e}, 响应: {openid_response.text}")
                raise AuthServiceError(
                    "OpenID解析失败", 
                    details={"provider": "qq", "error": str(e)}
                )
                
            return data
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """获取用户信息"""
        # QQ API需要同时提供访问令牌、appid和openid
        if isinstance(access_token, dict):
            token = access_token["access_token"]
            openid = access_token["openid"]
        else:
            raise AuthServiceError("无效的QQ令牌格式，需要包含access_token和openid")
        
        params = {
            "access_token": token,
            "oauth_consumer_key": self.client_id,  # 即appid
            "openid": openid
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.userinfo_url, params=params)
            
            if response.status_code != 200:
                logger.error(f"QQ用户信息获取失败: {response.text}")
                raise AuthServiceError(
                    "获取用户信息失败", 
                    details={"provider": "qq", "status": response.status_code}
                )
            
            data = response.json()
            if data.get("ret") != 0:
                logger.error(f"QQ用户信息获取错误: {data}")
                raise AuthServiceError(
                    f"QQ用户信息错误: {data.get('msg', '未知错误')}", 
                    details={"provider": "qq", "error": data.get("ret")}
                )
            
            # 将openid添加到用户信息中，因为它在normalize步骤中需要使用
            data["openid"] = openid
            if "unionid" in access_token:
                data["unionid"] = access_token["unionid"]
                
            return data
    
    async def normalize_user_info(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """标准化用户信息"""
        openid = user_info["openid"]
        
        return {
            "provider": "qq",
            "provider_user_id": openid,
            "unionid": user_info.get("unionid"),  # QQ特有字段
            "username": f"qq_{openid[:8]}",
            "display_name": user_info.get("nickname", "QQ用户"),
            "avatar": user_info.get("figureurl_qq_2") or user_info.get("figureurl_qq_1"),
            "email": None,  # QQ不提供邮箱
            "profile_data": {
                "nickname": user_info.get("nickname"),
                "gender": user_info.get("gender"),
                "province": user_info.get("province"),
                "city": user_info.get("city"),
                "year": user_info.get("year"),
                "constellation": user_info.get("constellation"),
                "figureurl": user_info.get("figureurl"),
                "figureurl_1": user_info.get("figureurl_1"),
                "figureurl_2": user_info.get("figureurl_2"),
                "figureurl_qq_1": user_info.get("figureurl_qq_1"),
                "figureurl_qq_2": user_info.get("figureurl_qq_2"),
                "vip": user_info.get("vip"),
                "level": user_info.get("level"),
                "yellow_vip_level": user_info.get("yellow_vip_level"),
            }
        }


class OAuthService:
    """OAuth服务"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化OAuth服务
        
        Args:
            config: OAuth配置，包含各平台的client_id和client_secret等
        """
        self.providers = {}
        
        # 加载各平台配置
        # 微信
        if "wechat" in config:
            wechat_config = config["wechat"]
            self.providers["wechat"] = WechatOAuthProvider(
                client_id=wechat_config["client_id"],
                client_secret=wechat_config["client_secret"],
                redirect_uri=wechat_config["redirect_uri"],
                scopes=wechat_config.get("scopes")
            )
        
        # GitHub
        if "github" in config:
            github_config = config["github"]
            self.providers["github"] = GithubOAuthProvider(
                client_id=github_config["client_id"],
                client_secret=github_config["client_secret"],
                redirect_uri=github_config["redirect_uri"],
                scopes=github_config.get("scopes")
            )
        
        # QQ
        if "qq" in config:
            qq_config = config["qq"]
            self.providers["qq"] = QQOAuthProvider(
                client_id=qq_config["client_id"],
                client_secret=qq_config["client_secret"],
                redirect_uri=qq_config["redirect_uri"],
                scopes=qq_config.get("scopes")
            )
        
        # 其他平台可以按需添加
    
    def get_provider(self, provider_name: str) -> OAuthProvider:
        """
        获取OAuth提供商
        
        Args:
            provider_name: 提供商名称，如'wechat', 'github'等
            
        Returns:
            OAuthProvider: OAuth提供商实例
            
        Raises:
            ValidationError: 提供商不支持
        """
        if provider_name not in self.providers:
            raise ValidationError(f"不支持的OAuth提供商: {provider_name}")
        
        return self.providers[provider_name]
    
    def get_authorize_url(self, provider_name: str) -> str:
        """
        获取授权URL
        
        Args:
            provider_name: 提供商名称
            
        Returns:
            str: 授权URL
        """
        provider = self.get_provider(provider_name)
        return provider.get_authorize_url()
    
    async def handle_callback(
        self, 
        provider_name: str, 
        code: str, 
        session: AsyncSession
    ) -> Tuple[User, Dict[str, Any]]:
        """
        处理OAuth回调，登录或注册用户
        
        Args:
            provider_name: 提供商名称
            code: 授权码
            session: 数据库会话
            
        Returns:
            Tuple[User, Dict[str, Any]]: 用户对象和令牌信息
        """
        provider = self.get_provider(provider_name)
        
        # 1. 使用授权码交换令牌
        token_data = await provider.exchange_code(code)
        
        # 2. 使用令牌获取用户信息
        user_info = await provider.get_user_info(token_data)
        
        # 3. 标准化用户信息
        normalized_info = await provider.normalize_user_info(user_info)
        
        # 4. 查找或创建用户
        user_repo = UserRepository(session)
        
        # 尝试通过OAuth标识查找用户
        provider_id = normalized_info["provider_user_id"]
        user = await user_repo.get_user_by_oauth_id(provider_name, provider_id)
        
        if not user:
            # 尝试通过邮箱查找用户 (如果提供了邮箱)
            email = normalized_info.get("email")
            if email:
                user = await user_repo.get_user_by_email(email)
            
            if not user:
                # 创建新用户
                # 生成随机密码
                random_password = secrets.token_urlsafe(16)
                password_hash = await get_password_hash(random_password)
                
                # 准备用户数据
                username = normalized_info["username"]
                display_name = normalized_info["display_name"]
                avatar = normalized_info.get("avatar")
                
                # 确保用户名唯一
                username_exists = await user_repo.get_user_by_username(username)
                if username_exists:
                    # 添加随机后缀
                    username = f"{username}_{uuid.uuid4().hex[:6]}"
                
                # 提取额外资料
                profile_data = normalized_info.get("profile_data", {})
                profile_data["oauth_provider"] = provider_name
                profile_data["display_name"] = display_name
                if avatar:
                    profile_data["avatar"] = avatar
                
                # 创建用户
                user_id = await user_repo.create_user(
                    username=username,
                    email=email,
                    password_hash=password_hash,
                    profile_data=profile_data,
                    status=UserStatusEnum.ACTIVE
                )
                
                # 关联OAuth账号
                await user_repo.link_oauth_account(
                    user_id=user_id,
                    provider=provider_name,
                    provider_user_id=provider_id,
                    provider_data=user_info
                )
                
                # 获取新创建的用户
                user = await user_repo.get_user_by_id(user_id)
            else:
                # 用户已存在但未关联此OAuth账号，进行关联
                await user_repo.link_oauth_account(
                    user_id=user.id,
                    provider=provider_name,
                    provider_user_id=provider_id,
                    provider_data=user_info
                )
        
        # 5. 生成会话令牌
        tokens = await create_tokens(user, session)
        
        # 6. 记录登录信息
        user.last_login = datetime.utcnow()
        await session.commit()
        
        return user, tokens
    
    async def unlink_oauth(
        self, 
        user_id: str, 
        provider_name: str,
        session: AsyncSession
    ) -> bool:
        """
        解除OAuth关联
        
        Args:
            user_id: 用户ID
            provider_name: 提供商名称
            session: 数据库会话
            
        Returns:
            bool: 操作是否成功
        """
        user_repo = UserRepository(session)
        
        # 检查用户是否存在
        user = await user_repo.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        
        # 检查是否有密码 - 如果没有设置密码且这是唯一的登录方式，则不允许解除关联
        if not user.password_hash:
            # 检查关联的OAuth账号数量
            oauth_accounts = await user_repo.get_user_oauth_accounts(user_id)
            if len(oauth_accounts) <= 1:
                raise ValidationError("无法解除唯一的登录方式，请先设置密码")
        
        # 解除关联
        return await user_repo.unlink_oauth_account(user_id, provider_name) 