#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
区块链服务客户端，用于集成健康数据存证和零知识证明功能
"""

import json
import uuid
import hashlib
import base64
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
import asyncio
import aiohttp
from loguru import logger


class BlockchainClient:
    """区块链服务客户端"""
    
    def __init__(self, service_url: str, timeout: int = 30):
        """
        初始化区块链服务客户端
        
        Args:
            service_url: 区块链服务URL
            timeout: 超时时间（秒）
        """
        self.service_url = service_url
        self.timeout = timeout
        self.session = None
        self.is_initialized = False
        self.zkp_enabled = False
        self.health_record_contract_address = None
        self.account_address = None
        
        logger.info(f"区块链客户端初始化，服务地址: {service_url}")
    
    async def initialize(self) -> None:
        """初始化客户端"""
        if self.is_initialized:
            return
            
        logger.info("正在初始化区块链客户端...")
        
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        
        # 检查区块链服务是否可用
        try:
            health_check = await self.health_check()
            if health_check['status'] == 'ok':
                self.is_initialized = True
                self.zkp_enabled = health_check.get('features', {}).get('zkp_enabled', False)
                self.health_record_contract_address = health_check.get('contracts', {}).get('health_record')
                self.account_address = health_check.get('account')
                
                logger.info(f"区块链客户端初始化成功")
                logger.info(f"零知识证明功能: {'已启用' if self.zkp_enabled else '未启用'}")
                logger.info(f"健康记录合约地址: {self.health_record_contract_address}")
            else:
                logger.warning(f"区块链服务健康检查失败: {health_check}")
        except Exception as e:
            logger.error(f"区块链客户端初始化失败: {e}")
            self.is_initialized = False
    
    async def health_check(self) -> Dict[str, Any]:
        """
        检查区块链服务健康状态
        
        Returns:
            健康状态信息
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                )
                
            async with self.session.get(
                f"{self.service_url}/health",
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"区块链服务健康检查失败，状态码: {response.status}, 错误: {error_text}")
                    return {"status": "error", "message": error_text}
        except Exception as e:
            logger.error(f"区块链服务健康检查出错: {e}")
            return {"status": "error", "message": str(e)}
    
    async def store_health_data_hash(
        self,
        user_id: Union[uuid.UUID, str],
        data: Dict[str, Any]
    ) -> Optional[str]:
        """
        将健康数据哈希存储到区块链
        
        Args:
            user_id: 用户ID
            data: 健康数据
            
        Returns:
            交易哈希，如果失败则返回None
        """
        if not self.is_initialized:
            await self.initialize()
            
        if not self.is_initialized or not self.health_record_contract_address:
            logger.error("区块链客户端未正确初始化")
            return None
        
        try:
            # 计算数据哈希
            data_hash = self._compute_hash(data)
            
            # 构建存证请求
            request_data = {
                "user_id": str(user_id),
                "data_hash": data_hash,
                "contract_address": self.health_record_contract_address,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {
                    "source": "health_data_service",
                    "type": "health_data"
                }
            }
            
            # 发送请求到区块链服务
            async with self.session.post(
                f"{self.service_url}/v1/records",
                json=request_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200 or response.status == 201:
                    result = await response.json()
                    transaction_hash = result.get('transaction_hash')
                    logger.info(f"健康数据哈希已存储到区块链, 交易哈希: {transaction_hash}")
                    return transaction_hash
                else:
                    error_text = await response.text()
                    logger.error(f"存储健康数据哈希失败，状态码: {response.status}, 错误: {error_text}")
                    return None
        except Exception as e:
            logger.error(f"存储健康数据哈希出错: {e}")
            return None
    
    async def verify_health_data(
        self,
        user_id: Union[uuid.UUID, str],
        data: Dict[str, Any],
        transaction_hash: str
    ) -> bool:
        """
        验证健康数据是否与区块链上的哈希匹配
        
        Args:
            user_id: 用户ID
            data: 健康数据
            transaction_hash: 交易哈希
            
        Returns:
            验证结果，True表示验证通过
        """
        if not self.is_initialized:
            await self.initialize()
            
        if not self.is_initialized:
            logger.error("区块链客户端未初始化")
            return False
        
        try:
            # 计算数据哈希
            data_hash = self._compute_hash(data)
            
            # 构建验证请求
            request_data = {
                "user_id": str(user_id),
                "data_hash": data_hash,
                "transaction_hash": transaction_hash
            }
            
            # 发送请求到区块链服务
            async with self.session.post(
                f"{self.service_url}/v1/records/verify",
                json=request_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    is_valid = result.get('is_valid', False)
                    logger.info(f"健康数据验证结果: {is_valid}")
                    return is_valid
                else:
                    error_text = await response.text()
                    logger.error(f"验证健康数据失败，状态码: {response.status}, 错误: {error_text}")
                    return False
        except Exception as e:
            logger.error(f"验证健康数据出错: {e}")
            return False
    
    async def generate_zkp(
        self,
        user_id: Union[uuid.UUID, str],
        data: Dict[str, Any],
        proof_claims: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        生成健康数据的零知识证明
        
        Args:
            user_id: 用户ID
            data: 健康数据
            proof_claims: 证明声明列表，例如["age > 18", "bmi < 25"]
            
        Returns:
            零知识证明数据，如果失败则返回None
        """
        if not self.is_initialized:
            await self.initialize()
            
        if not self.is_initialized or not self.zkp_enabled:
            logger.error("区块链客户端未初始化或零知识证明功能未启用")
            return None
        
        try:
            # 构建零知识证明请求
            request_data = {
                "user_id": str(user_id),
                "data": data,
                "claims": proof_claims
            }
            
            # 发送请求到区块链服务
            async with self.session.post(
                f"{self.service_url}/v1/zkp/generate",
                json=request_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"零知识证明已生成")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"生成零知识证明失败，状态码: {response.status}, 错误: {error_text}")
                    return None
        except Exception as e:
            logger.error(f"生成零知识证明出错: {e}")
            return None
    
    async def verify_zkp(
        self,
        proof_data: Dict[str, Any]
    ) -> bool:
        """
        验证零知识证明
        
        Args:
            proof_data: 零知识证明数据
            
        Returns:
            验证结果，True表示验证通过
        """
        if not self.is_initialized:
            await self.initialize()
            
        if not self.is_initialized or not self.zkp_enabled:
            logger.error("区块链客户端未初始化或零知识证明功能未启用")
            return False
        
        try:
            # 发送请求到区块链服务
            async with self.session.post(
                f"{self.service_url}/v1/zkp/verify",
                json=proof_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    is_valid = result.get('is_valid', False)
                    logger.info(f"零知识证明验证结果: {is_valid}")
                    return is_valid
                else:
                    error_text = await response.text()
                    logger.error(f"验证零知识证明失败，状态码: {response.status}, 错误: {error_text}")
                    return False
        except Exception as e:
            logger.error(f"验证零知识证明出错: {e}")
            return False
    
    async def get_health_data_records(
        self,
        user_id: Union[uuid.UUID, str],
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        获取用户的健康数据记录
        
        Args:
            user_id: 用户ID
            limit: 结果限制
            offset: 结果偏移
            
        Returns:
            健康数据记录列表
        """
        if not self.is_initialized:
            await self.initialize()
            
        if not self.is_initialized:
            logger.error("区块链客户端未初始化")
            return []
        
        try:
            # 发送请求到区块链服务
            async with self.session.get(
                f"{self.service_url}/v1/records",
                params={"user_id": str(user_id), "limit": limit, "offset": offset},
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    records = result.get('records', [])
                    logger.info(f"获取到{len(records)}条健康数据记录")
                    return records
                else:
                    error_text = await response.text()
                    logger.error(f"获取健康数据记录失败，状态码: {response.status}, 错误: {error_text}")
                    return []
        except Exception as e:
            logger.error(f"获取健康数据记录出错: {e}")
            return []
    
    def _compute_hash(self, data: Dict[str, Any]) -> str:
        """
        计算数据哈希
        
        Args:
            data: 数据
            
        Returns:
            数据哈希
        """
        # 将数据转换为字符串并按照键排序
        sorted_data = json.dumps(data, sort_keys=True)
        
        # 计算SHA-256哈希
        hash_object = hashlib.sha256(sorted_data.encode())
        hash_hex = hash_object.hexdigest()
        
        return hash_hex
    
    async def close(self) -> None:
        """关闭客户端"""
        if self.session:
            await self.session.close()
            self.session = None
        
        self.is_initialized = False
        logger.info("区块链客户端已关闭") 