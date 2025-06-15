#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
区块链身份验证服务

支持Web3钱包登录，包括MetaMask、WalletConnect等。
"""
import asyncio
import hashlib
import json
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

import httpx
from eth_account import Account
from eth_account.messages import encode_defunct
from fastapi import HTTPException, status
from web3 import Web3

from internal.config.settings import get_settings
from internal.model.user import User, UserStatusEnum
from internal.repository.user_repository import UserRepository
from internal.security.jwt_manager import JWTManager
from internal.cache.redis_cache import get_redis_cache
from internal.exceptions import (
    AuthenticationError,
    ValidationError,
    BlockchainError
)


class BlockchainAuthService:
    """区块链身份验证服务"""
    
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
        
        # Web3配置
        self.w3 = Web3()
        
        # 支持的区块链网络
        self.supported_networks = {
            'ethereum': {
                'name': 'Ethereum Mainnet',
                'chain_id': 1,
                'rpc_url': getattr(self.settings, 'ETHEREUM_RPC_URL', 'https://mainnet.infura.io/v3/'),
                'explorer': 'https://etherscan.io'
            },
            'polygon': {
                'name': 'Polygon',
                'chain_id': 137,
                'rpc_url': getattr(self.settings, 'POLYGON_RPC_URL', 'https://polygon-rpc.com/'),
                'explorer': 'https://polygonscan.com'
            },
            'bsc': {
                'name': 'Binance Smart Chain',
                'chain_id': 56,
                'rpc_url': getattr(self.settings, 'BSC_RPC_URL', 'https://bsc-dataseed.binance.org/'),
                'explorer': 'https://bscscan.com'
            }
        }
    
    def generate_nonce(self, wallet_address: str = None) -> str:
        """生成钱包登录随机数"""
        # 简化版本，只生成随机数
        return secrets.token_hex(16)
    
    async def generate_nonce_full(self, wallet_address: str) -> Dict[str, Any]:
        """生成钱包登录随机数（完整版本）"""
        # 验证钱包地址格式
        if not self.w3.is_address(wallet_address):
            raise ValidationError("无效的钱包地址格式")
        
        # 标准化地址格式
        wallet_address = self.w3.to_checksum_address(wallet_address)
        
        # 生成随机数和消息
        nonce = secrets.token_hex(16)
        timestamp = int(time.time())
        
        # 构建签名消息
        message = self._build_sign_message(wallet_address, nonce, timestamp)
        
        # 如果有缓存，则缓存nonce用于验证
        if hasattr(self, 'cache') and self.cache:
            try:
                cache_key = f"wallet_nonce:{wallet_address}"
                await self.cache.set(
                    cache_key,
                    json.dumps({
                        'nonce': nonce,
                        'timestamp': timestamp,
                        'message': message,
                        'created_at': datetime.utcnow().isoformat()
                    }),
                    expire=300  # 5分钟过期
                )
            except Exception:
                # 缓存失败不影响功能
                pass
        
        return {
            'wallet_address': wallet_address,
            'nonce': nonce,
            'message': message,
            'timestamp': timestamp,
            'expires_at': (datetime.utcnow() + timedelta(minutes=5)).isoformat()
        }
    
    def _build_sign_message(self, wallet_address: str, nonce: str, timestamp: int) -> str:
        """构建签名消息"""
        return f"""欢迎登录索克生活 (Suoke Life)!

请签名此消息以验证您的钱包所有权。

钱包地址: {wallet_address}
随机数: {nonce}
时间戳: {timestamp}
域名: suokelife.com

此请求不会触发区块链交易或产生任何费用。"""
    
    async def verify_wallet_signature(
        self,
        wallet_address: str,
        signature: str,
        network: str = 'ethereum'
    ) -> Dict[str, Any]:
        """验证钱包签名并登录"""
        # 验证网络支持
        if network not in self.supported_networks:
            raise ValidationError(f"不支持的区块链网络: {network}")
        
        # 标准化地址格式
        wallet_address = self.w3.to_checksum_address(wallet_address)
        
        # 获取缓存的nonce
        cache_key = f"wallet_nonce:{wallet_address}"
        cached_data = await self.cache.get(cache_key)
        
        if not cached_data:
            raise AuthenticationError("Nonce已过期或不存在，请重新获取")
        
        nonce_data = json.loads(cached_data)
        
        # 验证签名
        message = nonce_data['message']
        is_valid = self._verify_signature(wallet_address, message, signature)
        
        if not is_valid:
            raise AuthenticationError("钱包签名验证失败")
        
        # 删除已使用的nonce
        await self.cache.delete(cache_key)
        
        # 获取钱包相关信息
        wallet_info = await self._get_wallet_info(wallet_address, network)
        
        # 查找或创建用户
        user = await self._find_or_create_wallet_user(
            wallet_address, network, wallet_info
        )
        
        # 记录登录信息
        await self._record_wallet_login(user.id, wallet_address, network)
        
        # 生成JWT令牌
        tokens = await self.jwt_manager.create_tokens(user)
        
        return {
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'wallet_address': wallet_address,
                'avatar_url': user.avatar_url
            },
            'tokens': tokens,
            'wallet_info': wallet_info,
            'network': network
        }
    
    def _verify_signature(self, wallet_address: str, message: str, signature: str) -> bool:
        """验证以太坊签名"""
        try:
            # 编码消息
            encoded_message = encode_defunct(text=message)
            
            # 恢复签名者地址
            recovered_address = Account.recover_message(
                encoded_message, 
                signature=signature
            )
            
            # 比较地址
            return recovered_address.lower() == wallet_address.lower()
            
        except Exception as e:
            print(f"签名验证错误: {e}")
            return False
    
    async def _get_wallet_info(
        self, 
        wallet_address: str, 
        network: str
    ) -> Dict[str, Any]:
        """获取钱包信息"""
        network_config = self.supported_networks[network]
        
        try:
            # 连接到区块链网络
            if network_config.get('rpc_url'):
                w3 = Web3(Web3.HTTPProvider(network_config['rpc_url']))
            else:
                w3 = self.w3
            
            # 获取余额
            balance_wei = w3.eth.get_balance(wallet_address)
            balance_eth = w3.from_wei(balance_wei, 'ether')
            
            # 获取交易数量
            transaction_count = w3.eth.get_transaction_count(wallet_address)
            
            return {
                'balance': float(balance_eth),
                'transaction_count': transaction_count,
                'network': network_config['name'],
                'chain_id': network_config['chain_id'],
                'explorer_url': f"{network_config['explorer']}/address/{wallet_address}"
            }
            
        except Exception as e:
            # 如果无法获取链上信息，返回基本信息
            return {
                'balance': 0.0,
                'transaction_count': 0,
                'network': network_config['name'],
                'chain_id': network_config['chain_id'],
                'explorer_url': f"{network_config['explorer']}/address/{wallet_address}",
                'error': f"无法获取链上信息: {str(e)}"
            }
    
    async def _find_or_create_wallet_user(
        self,
        wallet_address: str,
        network: str,
        wallet_info: Dict[str, Any]
    ) -> User:
        """查找或创建钱包用户"""
        # 首先通过钱包地址查找用户
        existing_user = await self.user_repo.get_by_wallet_address(wallet_address)
        
        if existing_user:
            return existing_user
        
        # 创建新用户
        username = await self._generate_wallet_username(wallet_address)
        
        user_data = {
            'username': username,
            'wallet_address': wallet_address,
            'status': UserStatusEnum.ACTIVE,
            'created_via': f'wallet_{network}',
            'metadata': {
                'wallet_info': wallet_info,
                'primary_network': network
            }
        }
        
        return await self.user_repo.create(user_data)
    
    async def _generate_wallet_username(self, wallet_address: str) -> str:
        """生成钱包用户名"""
        # 使用钱包地址的前6位和后4位
        short_address = f"{wallet_address[:6]}...{wallet_address[-4:]}"
        base_username = f"wallet_{short_address}"
        
        # 检查唯一性
        username = base_username
        counter = 1
        
        while await self.user_repo.get_by_username(username):
            username = f"{base_username}_{counter}"
            counter += 1
            if counter > 1000:
                username = f"{base_username}_{secrets.token_hex(4)}"
                break
        
        return username
    
    async def _record_wallet_login(
        self,
        user_id: int,
        wallet_address: str,
        network: str
    ):
        """记录钱包登录信息"""
        login_data = {
            'user_id': user_id,
            'wallet_address': wallet_address,
            'network': network,
            'login_at': datetime.utcnow(),
            'ip_address': None,  # 可以从请求中获取
            'user_agent': None   # 可以从请求中获取
        }
        
        # 缓存最近的登录记录
        cache_key = f"wallet_login:{user_id}"
        await self.cache.set(
            cache_key,
            json.dumps(login_data, default=str),
            expire=86400  # 24小时
        )
    
    async def link_wallet_to_user(
        self,
        user_id: int,
        wallet_address: str,
        signature: str,
        network: str = 'ethereum'
    ) -> bool:
        """将钱包绑定到现有用户账号"""
        # 验证签名
        cache_key = f"wallet_nonce:{wallet_address}"
        cached_data = await self.cache.get(cache_key)
        
        if not cached_data:
            raise AuthenticationError("Nonce已过期，请重新获取")
        
        nonce_data = json.loads(cached_data)
        message = nonce_data['message']
        
        if not self._verify_signature(wallet_address, message, signature):
            raise AuthenticationError("钱包签名验证失败")
        
        # 检查钱包是否已被其他用户绑定
        existing_user = await self.user_repo.get_by_wallet_address(wallet_address)
        if existing_user and existing_user.id != user_id:
            raise ValidationError("该钱包已被其他用户绑定")
        
        # 更新用户钱包地址
        await self.user_repo.update(user_id, {
            'wallet_address': wallet_address,
            'metadata': {
                'wallet_network': network,
                'wallet_linked_at': datetime.utcnow().isoformat()
            }
        })
        
        # 删除已使用的nonce
        await self.cache.delete(cache_key)
        
        return True
    
    async def unlink_wallet_from_user(self, user_id: int) -> bool:
        """解除用户的钱包绑定"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValidationError("用户不存在")
        
        if not user.wallet_address:
            raise ValidationError("用户未绑定钱包")
        
        # 检查用户是否有其他登录方式
        if not user.password_hash and not user.email:
            raise ValidationError("无法解除钱包绑定，请先设置密码或绑定邮箱")
        
        # 清除钱包地址
        await self.user_repo.update(user_id, {
            'wallet_address': None,
            'metadata': {
                'wallet_unlinked_at': datetime.utcnow().isoformat()
            }
        })
        
        return True
    
    async def get_supported_networks(self) -> List[Dict[str, Any]]:
        """获取支持的区块链网络"""
        return [
            {
                'id': network_id,
                'name': config['name'],
                'chain_id': config['chain_id'],
                'explorer': config['explorer']
            }
            for network_id, config in self.supported_networks.items()
        ]


# 依赖注入函数
async def get_blockchain_auth_service(
    user_repo: UserRepository = None,
    jwt_manager: JWTManager = None
) -> BlockchainAuthService:
    """获取区块链认证服务实例"""
    if not user_repo:
        from internal.repository.user_repository import get_user_repository
        user_repo = await get_user_repository()
    
    if not jwt_manager:
        from internal.security.jwt_manager import get_jwt_manager
        jwt_manager = get_jwt_manager()
    
    return BlockchainAuthService(user_repo, jwt_manager) 