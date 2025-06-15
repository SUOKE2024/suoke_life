#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
社交登录认证服务

支持多种社交平台的OAuth2.0登录集成，包括Google、GitHub、微信等。
"""
import asyncio
import json
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode, parse_qs

import httpx
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from internal.config.settings import get_settings
from internal.model.user import User, UserStatusEnum
from internal.model.oauth import OAuthConnection, OAuthProvider
from internal.repository.user_repository import UserRepository
from internal.repository.oauth_repository import OAuthRepository
from internal.security.jwt_manager import JWTManager
from internal.cache.redis_cache import get_redis_cache
from internal.exceptions import (
    AuthenticationError,
    ValidationError,
    ExternalServiceError
)


class SocialAuthService:
    """社交登录认证服务"""
    
    def __init__(self, dependencies=None):
        if dependencies:
            self.settings = dependencies.settings
            self.jwt_manager = dependencies.jwt_manager
            self.cache = dependencies.cache
            self.db_manager = dependencies.db_manager
        else:
            # 向后兼容的构造函数
            self.settings = get_settings()
            from internal.security.jwt_manager import JWTManager
            self.jwt_manager = JWTManager()
            self.cache = get_redis_cache()
            from internal.database.connection_manager import get_connection_manager
            self.db_manager = get_connection_manager()
        
        # OAuth配置
        self.oauth_configs = {
            'google': {
                'client_id': getattr(self.settings, 'GOOGLE_CLIENT_ID', ''),
                'client_secret': getattr(self.settings, 'GOOGLE_CLIENT_SECRET', ''),
                'auth_url': 'https://accounts.google.com/o/oauth2/v2/auth',
                'token_url': 'https://oauth2.googleapis.com/token',
                'user_info_url': 'https://www.googleapis.com/oauth2/v2/userinfo',
                'scope': 'openid email profile'
            },
            'github': {
                'client_id': getattr(self.settings, 'GITHUB_CLIENT_ID', ''),
                'client_secret': getattr(self.settings, 'GITHUB_CLIENT_SECRET', ''),
                'auth_url': 'https://github.com/login/oauth/authorize',
                'token_url': 'https://github.com/login/oauth/access_token',
                'user_info_url': 'https://api.github.com/user',
                'scope': 'user:email'
            },
            'wechat': {
                'client_id': getattr(self.settings, 'WECHAT_APP_ID', ''),
                'client_secret': getattr(self.settings, 'WECHAT_APP_SECRET', ''),
                'auth_url': 'https://open.weixin.qq.com/connect/qrconnect',
                'token_url': 'https://api.weixin.qq.com/sns/oauth2/access_token',
                'user_info_url': 'https://api.weixin.qq.com/sns/userinfo',
                'scope': 'snsapi_login'
            }
        }
    
    async def get_authorization_url(
        self, 
        provider: str, 
        redirect_uri: str,
        state: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取OAuth授权URL"""
        if provider not in self.oauth_configs:
            raise ValidationError(f"不支持的OAuth提供商: {provider}")
        
        config = self.oauth_configs[provider]
        
        # 生成state参数防止CSRF攻击
        if not state:
            state = secrets.token_urlsafe(32)
        
        # 缓存state用于验证
        await self.cache.set(
            f"oauth_state:{state}",
            json.dumps({
                'provider': provider,
                'redirect_uri': redirect_uri,
                'created_at': datetime.utcnow().isoformat()
            }),
            expire=600  # 10分钟过期
        )
        
        # 构建授权URL参数
        params = {
            'client_id': config['client_id'],
            'redirect_uri': redirect_uri,
            'scope': config['scope'],
            'response_type': 'code',
            'state': state
        }
        
        # 微信特殊参数
        if provider == 'wechat':
            params['appid'] = config['client_id']
            del params['client_id']
        
        auth_url = f"{config['auth_url']}?{urlencode(params)}"
        
        return {
            'authorization_url': auth_url,
            'state': state,
            'provider': provider
        }
    
    async def handle_oauth_callback(
        self,
        provider: str,
        code: str,
        state: str,
        redirect_uri: str
    ) -> Dict[str, Any]:
        """处理OAuth回调"""
        # 验证state参数
        cached_state = await self.cache.get(f"oauth_state:{state}")
        if not cached_state:
            raise AuthenticationError("无效的state参数或已过期")
        
        state_data = json.loads(cached_state)
        if state_data['provider'] != provider:
            raise AuthenticationError("Provider不匹配")
        
        # 删除已使用的state
        await self.cache.delete(f"oauth_state:{state}")
        
        # 获取访问令牌
        access_token = await self._exchange_code_for_token(
            provider, code, redirect_uri
        )
        
        # 获取用户信息
        user_info = await self._get_user_info(provider, access_token)
        
        # 查找或创建用户
        user = await self._find_or_create_user(provider, user_info)
        
        # 更新或创建OAuth连接
        await self._update_oauth_connection(
            user.id, provider, user_info, access_token
        )
        
        # 生成JWT令牌
        tokens = await self.jwt_manager.create_tokens(user)
        
        return {
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'avatar_url': user.avatar_url
            },
            'tokens': tokens,
            'provider': provider
        }
    
    async def _exchange_code_for_token(
        self, 
        provider: str, 
        code: str, 
        redirect_uri: str
    ) -> str:
        """交换授权码获取访问令牌"""
        config = self.oauth_configs[provider]
        
        data = {
            'client_id': config['client_id'],
            'client_secret': config['client_secret'],
            'code': code,
            'redirect_uri': redirect_uri
        }
        
        if provider == 'github':
            data['grant_type'] = 'authorization_code'
            headers = {'Accept': 'application/json'}
        elif provider == 'wechat':
            data['appid'] = config['client_id']
            data['secret'] = config['client_secret']
            del data['client_id']
            del data['client_secret']
            headers = {}
        else:  # google
            data['grant_type'] = 'authorization_code'
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    config['token_url'],
                    data=data,
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                
                if provider == 'github':
                    token_data = response.json()
                else:
                    token_data = response.json()
                
                access_token = token_data.get('access_token')
                if not access_token:
                    raise ExternalServiceError(f"无法获取{provider}访问令牌")
                
                return access_token
                
        except httpx.HTTPError as e:
            raise ExternalServiceError(f"获取{provider}令牌失败: {str(e)}")
    
    async def _get_user_info(self, provider: str, access_token: str) -> Dict[str, Any]:
        """获取用户信息"""
        config = self.oauth_configs[provider]
        
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # 微信需要特殊处理
        if provider == 'wechat':
            url = f"{config['user_info_url']}?access_token={access_token}&lang=zh_CN"
            headers = {}
        else:
            url = config['user_info_url']
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=30.0)
                response.raise_for_status()
                
                user_info = response.json()
                
                # 标准化用户信息
                return self._normalize_user_info(provider, user_info)
                
        except httpx.HTTPError as e:
            raise ExternalServiceError(f"获取{provider}用户信息失败: {str(e)}")
    
    def _normalize_user_info(self, provider: str, raw_info: Dict[str, Any]) -> Dict[str, Any]:
        """标准化不同平台的用户信息"""
        if provider == 'google':
            return {
                'provider_id': raw_info.get('id'),
                'email': raw_info.get('email'),
                'name': raw_info.get('name'),
                'avatar_url': raw_info.get('picture'),
                'verified_email': raw_info.get('verified_email', False)
            }
        elif provider == 'github':
            return {
                'provider_id': str(raw_info.get('id')),
                'email': raw_info.get('email'),
                'name': raw_info.get('name') or raw_info.get('login'),
                'avatar_url': raw_info.get('avatar_url'),
                'verified_email': True  # GitHub邮箱默认验证
            }
        elif provider == 'wechat':
            return {
                'provider_id': raw_info.get('openid'),
                'email': None,  # 微信不提供邮箱
                'name': raw_info.get('nickname'),
                'avatar_url': raw_info.get('headimgurl'),
                'verified_email': False
            }
        else:
            return raw_info
    
    async def _find_or_create_user(
        self, 
        provider: str, 
        user_info: Dict[str, Any]
    ) -> User:
        """查找或创建用户"""
        provider_id = user_info['provider_id']
        
        # 首先通过OAuth连接查找用户
        oauth_connection = await self.oauth_repo.get_by_provider_and_id(
            provider, provider_id
        )
        
        if oauth_connection:
            return await self.user_repo.get_by_id(oauth_connection.user_id)
        
        # 如果有邮箱，尝试通过邮箱查找现有用户
        email = user_info.get('email')
        if email:
            existing_user = await self.user_repo.get_by_email(email)
            if existing_user:
                return existing_user
        
        # 创建新用户
        username = await self._generate_unique_username(
            user_info.get('name', f"{provider}_user")
        )
        
        user_data = {
            'username': username,
            'email': email,
            'avatar_url': user_info.get('avatar_url'),
            'status': UserStatusEnum.ACTIVE,
            'email_verified': user_info.get('verified_email', False),
            'created_via': f'oauth_{provider}'
        }
        
        return await self.user_repo.create(user_data)
    
    async def _generate_unique_username(self, base_name: str) -> str:
        """生成唯一用户名"""
        # 清理用户名
        username = ''.join(c for c in base_name if c.isalnum() or c in '_-')
        username = username[:20]  # 限制长度
        
        if not username:
            username = 'user'
        
        # 检查唯一性
        original_username = username
        counter = 1
        
        while await self.user_repo.get_by_username(username):
            username = f"{original_username}_{counter}"
            counter += 1
            if counter > 1000:  # 防止无限循环
                username = f"{original_username}_{secrets.token_hex(4)}"
                break
        
        return username
    
    async def _update_oauth_connection(
        self,
        user_id: int,
        provider: str,
        user_info: Dict[str, Any],
        access_token: str
    ):
        """更新或创建OAuth连接"""
        provider_id = user_info['provider_id']
        
        connection_data = {
            'user_id': user_id,
            'provider': provider,
            'provider_user_id': provider_id,
            'access_token': access_token,
            'user_info': user_info,
            'last_login_at': datetime.utcnow()
        }
        
        existing_connection = await self.oauth_repo.get_by_provider_and_id(
            provider, provider_id
        )
        
        if existing_connection:
            await self.oauth_repo.update(
                existing_connection.id, connection_data
            )
        else:
            await self.oauth_repo.create(connection_data)
    
    async def unlink_social_account(
        self, 
        user_id: int, 
        provider: str
    ) -> bool:
        """解除社交账号绑定"""
        connection = await self.oauth_repo.get_by_user_and_provider(
            user_id, provider
        )
        
        if not connection:
            raise ValidationError(f"未找到{provider}账号绑定")
        
        # 检查用户是否有其他登录方式
        user = await self.user_repo.get_by_id(user_id)
        if not user.password_hash:
            # 检查是否有其他OAuth连接
            other_connections = await self.oauth_repo.get_by_user_id(user_id)
            if len(other_connections) <= 1:
                raise ValidationError(
                    "无法解除绑定，请先设置密码或绑定其他社交账号"
                )
        
        await self.oauth_repo.delete(connection.id)
        return True
    
    async def get_linked_accounts(self, user_id: int) -> List[Dict[str, Any]]:
        """获取用户已绑定的社交账号"""
        connections = await self.oauth_repo.get_by_user_id(user_id)
        
        return [
            {
                'provider': conn.provider,
                'provider_user_id': conn.provider_user_id,
                'linked_at': conn.created_at,
                'last_login_at': conn.last_login_at,
                'user_info': {
                    'name': conn.user_info.get('name'),
                    'avatar_url': conn.user_info.get('avatar_url')
                }
            }
            for conn in connections
        ]


# 依赖注入函数
async def get_social_auth_service(
    user_repo: UserRepository = None,
    oauth_repo: OAuthRepository = None,
    jwt_manager: JWTManager = None
) -> SocialAuthService:
    """获取社交认证服务实例"""
    if not user_repo:
        from internal.repository.user_repository import get_user_repository
        user_repo = await get_user_repository()
    
    if not oauth_repo:
        from internal.repository.oauth_repository import get_oauth_repository
        oauth_repo = await get_oauth_repository()
    
    if not jwt_manager:
        from internal.security.jwt_manager import get_jwt_manager
        jwt_manager = get_jwt_manager()
    
    return SocialAuthService(user_repo, oauth_repo, jwt_manager)