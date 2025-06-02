#!/usr/bin/env python3
"""
区块链消息总线深度集成
实现端到端加密、数字签名、区块链存储和IPFS分布式存储
"""

import asyncio
import hashlib
import hmac
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union
from uuid import uuid4
import base64
import os

import aioredis
import aiohttp
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """消息类型"""
    HEALTH_DATA = "health_data"
    DIAGNOSIS_RESULT = "diagnosis_result"
    TREATMENT_PLAN = "treatment_plan"
    AGENT_DECISION = "agent_decision"
    USER_CONSENT = "user_consent"
    DATA_ACCESS_LOG = "data_access_log"
    SYSTEM_EVENT = "system_event"
    AUDIT_TRAIL = "audit_trail"


class DataSensitivity(Enum):
    """数据敏感度级别"""
    PUBLIC = "public"           # 公开
    INTERNAL = "internal"       # 内部
    CONFIDENTIAL = "confidential"  # 机密
    RESTRICTED = "restricted"   # 限制级


class BlockchainNetwork(Enum):
    """区块链网络类型"""
    ETHEREUM = "ethereum"
    HYPERLEDGER = "hyperledger"
    POLYGON = "polygon"
    BSC = "bsc"
    PRIVATE = "private"


class MessageStatus(Enum):
    """消息状态"""
    PENDING = "pending"
    ENCRYPTED = "encrypted"
    SIGNED = "signed"
    BLOCKCHAIN_PENDING = "blockchain_pending"
    BLOCKCHAIN_CONFIRMED = "blockchain_confirmed"
    IPFS_STORED = "ipfs_stored"
    DELIVERED = "delivered"
    FAILED = "failed"


@dataclass
class EncryptionConfig:
    """加密配置"""
    algorithm: str = "AES-256-GCM"
    key_derivation: str = "PBKDF2"
    iterations: int = 100000
    salt_length: int = 32
    iv_length: int = 16


@dataclass
class BlockchainConfig:
    """区块链配置"""
    network: BlockchainNetwork
    node_url: str
    contract_address: Optional[str] = None
    private_key: Optional[str] = None
    gas_limit: int = 100000
    gas_price: int = 20000000000  # 20 Gwei
    confirmation_blocks: int = 3


@dataclass
class IPFSConfig:
    """IPFS配置"""
    gateway_url: str = "http://localhost:8080"
    api_url: str = "http://localhost:5001"
    pin_content: bool = True
    timeout: int = 30


@dataclass
class SecureMessage:
    """安全消息"""
    message_id: str
    message_type: MessageType
    sender_id: str
    recipient_id: str
    data_sensitivity: DataSensitivity
    payload: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    # 加密相关
    encrypted_payload: Optional[bytes] = None
    encryption_key_hash: Optional[str] = None
    
    # 签名相关
    signature: Optional[str] = None
    signature_algorithm: str = "HMAC-SHA256"
    
    # 区块链相关
    blockchain_tx_hash: Optional[str] = None
    blockchain_block_number: Optional[int] = None
    blockchain_confirmation_count: int = 0
    
    # IPFS相关
    ipfs_hash: Optional[str] = None
    ipfs_gateway_url: Optional[str] = None
    
    # 状态跟踪
    status: MessageStatus = MessageStatus.PENDING
    status_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_status(self, status: MessageStatus, details: Optional[Dict[str, Any]] = None):
        """添加状态记录"""
        self.status = status
        status_record = {
            "status": status.value,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.status_history.append(status_record)


@dataclass
class MessageDeliveryReceipt:
    """消息投递回执"""
    message_id: str
    recipient_id: str
    delivered_at: datetime
    blockchain_verified: bool
    ipfs_accessible: bool
    signature_valid: bool
    decryption_successful: bool


class BlockchainMessageBus:
    """区块链消息总线"""
    
    def __init__(
        self,
        encryption_config: EncryptionConfig,
        blockchain_config: BlockchainConfig,
        ipfs_config: IPFSConfig,
        redis_url: str = "redis://localhost:6379"
    ):
        self.encryption_config = encryption_config
        self.blockchain_config = blockchain_config
        self.ipfs_config = ipfs_config
        self.redis_url = redis_url
        
        self.redis: Optional[aioredis.Redis] = None
        
        # 消息存储
        self.pending_messages: Dict[str, SecureMessage] = {}
        self.delivered_messages: Dict[str, SecureMessage] = {}
        
        # 加密密钥管理
        self.user_keys: Dict[str, bytes] = {}
        self.master_key: Optional[bytes] = None
        
        # 区块链客户端
        self.blockchain_client: Optional[Any] = None
        
        self._running = False
    
    async def initialize(self):
        """初始化区块链消息总线"""
        try:
            self.redis = aioredis.from_url(self.redis_url)
            await self.redis.ping()
            
            # 初始化主密钥
            await self._initialize_master_key()
            
            # 初始化区块链客户端
            await self._initialize_blockchain_client()
            
            logger.info("区块链消息总线初始化成功")
            
            # 启动后台任务
            self._running = True
            asyncio.create_task(self._message_processor())
            asyncio.create_task(self._blockchain_monitor())
            asyncio.create_task(self._ipfs_monitor())
            
        except Exception as e:
            logger.error(f"区块链消息总线初始化失败: {e}")
            raise
    
    async def send_secure_message(
        self,
        message_type: MessageType,
        sender_id: str,
        recipient_id: str,
        payload: Dict[str, Any],
        data_sensitivity: DataSensitivity = DataSensitivity.INTERNAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """发送安全消息"""
        try:
            # 创建消息
            message = SecureMessage(
                message_id=str(uuid4()),
                message_type=message_type,
                sender_id=sender_id,
                recipient_id=recipient_id,
                data_sensitivity=data_sensitivity,
                payload=payload,
                metadata=metadata or {}
            )
            
            # 加密消息
            await self._encrypt_message(message)
            
            # 签名消息
            await self._sign_message(message)
            
            # 存储到待处理队列
            self.pending_messages[message.message_id] = message
            
            # 发布消息事件
            await self._publish_message_event("message_created", message)
            
            logger.info(f"安全消息已创建: {message.message_id}")
            return message.message_id
            
        except Exception as e:
            logger.error(f"发送安全消息失败: {e}")
            raise
    
    async def receive_secure_message(
        self,
        message_id: str,
        recipient_id: str
    ) -> Optional[Dict[str, Any]]:
        """接收安全消息"""
        try:
            # 获取消息
            message = await self._get_message(message_id)
            if not message:
                return None
            
            # 验证接收者
            if message.recipient_id != recipient_id:
                logger.warning(f"消息接收者不匹配: {message_id}")
                return None
            
            # 验证签名
            if not await self._verify_message_signature(message):
                logger.error(f"消息签名验证失败: {message_id}")
                return None
            
            # 解密消息
            decrypted_payload = await self._decrypt_message(message)
            if not decrypted_payload:
                logger.error(f"消息解密失败: {message_id}")
                return None
            
            # 创建投递回执
            receipt = MessageDeliveryReceipt(
                message_id=message_id,
                recipient_id=recipient_id,
                delivered_at=datetime.now(),
                blockchain_verified=bool(message.blockchain_tx_hash),
                ipfs_accessible=bool(message.ipfs_hash),
                signature_valid=True,
                decryption_successful=True
            )
            
            # 记录投递
            await self._record_message_delivery(receipt)
            
            return {
                "message_id": message.message_id,
                "message_type": message.message_type.value,
                "sender_id": message.sender_id,
                "payload": decrypted_payload,
                "metadata": message.metadata,
                "created_at": message.created_at.isoformat(),
                "delivery_receipt": receipt
            }
            
        except Exception as e:
            logger.error(f"接收安全消息失败: {e}")
            return None
    
    async def get_message_status(self, message_id: str) -> Optional[Dict[str, Any]]:
        """获取消息状态"""
        try:
            message = await self._get_message(message_id)
            if not message:
                return None
            
            return {
                "message_id": message.message_id,
                "status": message.status.value,
                "blockchain_tx_hash": message.blockchain_tx_hash,
                "blockchain_confirmations": message.blockchain_confirmation_count,
                "ipfs_hash": message.ipfs_hash,
                "status_history": message.status_history
            }
            
        except Exception as e:
            logger.error(f"获取消息状态失败: {e}")
            return None
    
    async def _initialize_master_key(self):
        """初始化主密钥"""
        try:
            # 尝试从环境变量或配置文件加载
            master_key_b64 = os.getenv("SUOKE_MASTER_KEY")
            if master_key_b64:
                self.master_key = base64.b64decode(master_key_b64)
            else:
                # 生成新的主密钥
                self.master_key = Fernet.generate_key()
                logger.warning("生成了新的主密钥，请妥善保存")
            
        except Exception as e:
            logger.error(f"初始化主密钥失败: {e}")
            raise
    
    async def _initialize_blockchain_client(self):
        """初始化区块链客户端"""
        try:
            if self.blockchain_config.network == BlockchainNetwork.ETHEREUM:
                # 初始化以太坊客户端
                # 这里使用web3.py或类似库
                pass
            elif self.blockchain_config.network == BlockchainNetwork.HYPERLEDGER:
                # 初始化Hyperledger Fabric客户端
                pass
            # 其他网络类型...
            
            logger.info(f"区块链客户端初始化成功: {self.blockchain_config.network.value}")
            
        except Exception as e:
            logger.error(f"初始化区块链客户端失败: {e}")
            raise
    
    async def _encrypt_message(self, message: SecureMessage):
        """加密消息"""
        try:
            # 获取或生成用户密钥
            user_key = await self._get_or_create_user_key(message.recipient_id)
            
            # 创建Fernet实例
            fernet = Fernet(user_key)
            
            # 序列化载荷
            payload_json = json.dumps(message.payload, ensure_ascii=False)
            payload_bytes = payload_json.encode('utf-8')
            
            # 加密
            encrypted_payload = fernet.encrypt(payload_bytes)
            message.encrypted_payload = encrypted_payload
            
            # 生成密钥哈希（用于验证）
            message.encryption_key_hash = hashlib.sha256(user_key).hexdigest()
            
            message.add_status(MessageStatus.ENCRYPTED)
            
        except Exception as e:
            logger.error(f"消息加密失败: {e}")
            raise
    
    async def _decrypt_message(self, message: SecureMessage) -> Optional[Dict[str, Any]]:
        """解密消息"""
        try:
            if not message.encrypted_payload:
                return message.payload
            
            # 获取用户密钥
            user_key = await self._get_or_create_user_key(message.recipient_id)
            
            # 验证密钥哈希
            key_hash = hashlib.sha256(user_key).hexdigest()
            if key_hash != message.encryption_key_hash:
                logger.error("密钥哈希不匹配")
                return None
            
            # 创建Fernet实例
            fernet = Fernet(user_key)
            
            # 解密
            decrypted_bytes = fernet.decrypt(message.encrypted_payload)
            decrypted_json = decrypted_bytes.decode('utf-8')
            
            return json.loads(decrypted_json)
            
        except Exception as e:
            logger.error(f"消息解密失败: {e}")
            return None
    
    async def _sign_message(self, message: SecureMessage):
        """签名消息"""
        try:
            # 创建签名数据
            sign_data = {
                "message_id": message.message_id,
                "sender_id": message.sender_id,
                "recipient_id": message.recipient_id,
                "message_type": message.message_type.value,
                "created_at": message.created_at.isoformat(),
                "payload_hash": hashlib.sha256(
                    message.encrypted_payload or json.dumps(message.payload).encode()
                ).hexdigest()
            }
            
            # 序列化签名数据
            sign_data_json = json.dumps(sign_data, sort_keys=True)
            sign_data_bytes = sign_data_json.encode('utf-8')
            
            # 使用HMAC-SHA256签名
            signature = hmac.new(
                self.master_key,
                sign_data_bytes,
                hashlib.sha256
            ).hexdigest()
            
            message.signature = signature
            message.add_status(MessageStatus.SIGNED)
            
        except Exception as e:
            logger.error(f"消息签名失败: {e}")
            raise
    
    async def _verify_message_signature(self, message: SecureMessage) -> bool:
        """验证消息签名"""
        try:
            if not message.signature:
                return False
            
            # 重新创建签名数据
            sign_data = {
                "message_id": message.message_id,
                "sender_id": message.sender_id,
                "recipient_id": message.recipient_id,
                "message_type": message.message_type.value,
                "created_at": message.created_at.isoformat(),
                "payload_hash": hashlib.sha256(
                    message.encrypted_payload or json.dumps(message.payload).encode()
                ).hexdigest()
            }
            
            # 序列化签名数据
            sign_data_json = json.dumps(sign_data, sort_keys=True)
            sign_data_bytes = sign_data_json.encode('utf-8')
            
            # 计算期望的签名
            expected_signature = hmac.new(
                self.master_key,
                sign_data_bytes,
                hashlib.sha256
            ).hexdigest()
            
            # 比较签名
            return hmac.compare_digest(message.signature, expected_signature)
            
        except Exception as e:
            logger.error(f"验证消息签名失败: {e}")
            return False
    
    async def _get_or_create_user_key(self, user_id: str) -> bytes:
        """获取或创建用户密钥"""
        try:
            if user_id in self.user_keys:
                return self.user_keys[user_id]
            
            # 尝试从Redis加载
            key_data = await self.redis.get(f"user_key:{user_id}")
            if key_data:
                user_key = base64.b64decode(key_data)
                self.user_keys[user_id] = user_key
                return user_key
            
            # 生成新的用户密钥
            password = f"suoke_user_{user_id}".encode('utf-8')
            salt = os.urandom(self.encryption_config.salt_length)
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=self.encryption_config.iterations,
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(password))
            
            # 存储密钥
            self.user_keys[user_id] = key
            await self.redis.setex(
                f"user_key:{user_id}",
                30 * 24 * 3600,  # 30天TTL
                base64.b64encode(key)
            )
            
            return key
            
        except Exception as e:
            logger.error(f"获取用户密钥失败: {e}")
            raise
    
    async def _store_to_blockchain(self, message: SecureMessage):
        """存储到区块链"""
        try:
            # 创建区块链交易数据
            tx_data = {
                "message_id": message.message_id,
                "sender_id": message.sender_id,
                "recipient_id": message.recipient_id,
                "message_type": message.message_type.value,
                "data_hash": hashlib.sha256(
                    message.encrypted_payload or json.dumps(message.payload).encode()
                ).hexdigest(),
                "timestamp": int(message.created_at.timestamp()),
                "ipfs_hash": message.ipfs_hash
            }
            
            # 发送交易到区块链
            tx_hash = await self._send_blockchain_transaction(tx_data)
            
            if tx_hash:
                message.blockchain_tx_hash = tx_hash
                message.add_status(MessageStatus.BLOCKCHAIN_PENDING)
                logger.info(f"消息已提交到区块链: {message.message_id} -> {tx_hash}")
            
        except Exception as e:
            logger.error(f"存储到区块链失败: {e}")
    
    async def _store_to_ipfs(self, message: SecureMessage):
        """存储到IPFS"""
        try:
            # 准备IPFS数据
            ipfs_data = {
                "message_id": message.message_id,
                "encrypted_payload": base64.b64encode(message.encrypted_payload).decode() if message.encrypted_payload else None,
                "signature": message.signature,
                "metadata": message.metadata,
                "created_at": message.created_at.isoformat()
            }
            
            # 上传到IPFS
            ipfs_hash = await self._upload_to_ipfs(ipfs_data)
            
            if ipfs_hash:
                message.ipfs_hash = ipfs_hash
                message.ipfs_gateway_url = f"{self.ipfs_config.gateway_url}/ipfs/{ipfs_hash}"
                message.add_status(MessageStatus.IPFS_STORED)
                logger.info(f"消息已存储到IPFS: {message.message_id} -> {ipfs_hash}")
            
        except Exception as e:
            logger.error(f"存储到IPFS失败: {e}")
    
    async def _send_blockchain_transaction(self, tx_data: Dict[str, Any]) -> Optional[str]:
        """发送区块链交易"""
        try:
            # 这里需要根据具体的区块链网络实现
            # 示例：以太坊交易
            if self.blockchain_config.network == BlockchainNetwork.ETHEREUM:
                # 使用web3.py发送交易
                # tx_hash = await self._send_ethereum_transaction(tx_data)
                # return tx_hash
                pass
            
            # 模拟交易哈希
            return hashlib.sha256(json.dumps(tx_data).encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"发送区块链交易失败: {e}")
            return None
    
    async def _upload_to_ipfs(self, data: Dict[str, Any]) -> Optional[str]:
        """上传到IPFS"""
        try:
            async with aiohttp.ClientSession() as session:
                # 准备文件数据
                json_data = json.dumps(data, ensure_ascii=False)
                
                # 上传到IPFS
                form_data = aiohttp.FormData()
                form_data.add_field('file', json_data, content_type='application/json')
                
                async with session.post(
                    f"{self.ipfs_config.api_url}/api/v0/add",
                    data=form_data,
                    timeout=aiohttp.ClientTimeout(total=self.ipfs_config.timeout)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        ipfs_hash = result.get('Hash')
                        
                        # 如果启用了固定，则固定内容
                        if self.ipfs_config.pin_content and ipfs_hash:
                            await self._pin_ipfs_content(ipfs_hash)
                        
                        return ipfs_hash
            
            return None
            
        except Exception as e:
            logger.error(f"上传到IPFS失败: {e}")
            return None
    
    async def _pin_ipfs_content(self, ipfs_hash: str):
        """固定IPFS内容"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ipfs_config.api_url}/api/v0/pin/add",
                    params={"arg": ipfs_hash}
                ) as response:
                    if response.status == 200:
                        logger.debug(f"IPFS内容已固定: {ipfs_hash}")
                    
        except Exception as e:
            logger.error(f"固定IPFS内容失败: {e}")
    
    async def _get_message(self, message_id: str) -> Optional[SecureMessage]:
        """获取消息"""
        # 先从内存查找
        if message_id in self.pending_messages:
            return self.pending_messages[message_id]
        
        if message_id in self.delivered_messages:
            return self.delivered_messages[message_id]
        
        # 从Redis查找
        try:
            message_data = await self.redis.get(f"secure_message:{message_id}")
            if message_data:
                data = json.loads(message_data)
                return self._deserialize_message(data)
        except Exception as e:
            logger.error(f"从Redis获取消息失败: {e}")
        
        return None
    
    async def _store_message(self, message: SecureMessage):
        """存储消息"""
        try:
            message_data = self._serialize_message(message)
            await self.redis.setex(
                f"secure_message:{message.message_id}",
                7 * 24 * 3600,  # 7天TTL
                json.dumps(message_data)
            )
        except Exception as e:
            logger.error(f"存储消息失败: {e}")
    
    def _serialize_message(self, message: SecureMessage) -> Dict[str, Any]:
        """序列化消息"""
        return {
            "message_id": message.message_id,
            "message_type": message.message_type.value,
            "sender_id": message.sender_id,
            "recipient_id": message.recipient_id,
            "data_sensitivity": message.data_sensitivity.value,
            "payload": message.payload,
            "metadata": message.metadata,
            "created_at": message.created_at.isoformat(),
            "encrypted_payload": base64.b64encode(message.encrypted_payload).decode() if message.encrypted_payload else None,
            "encryption_key_hash": message.encryption_key_hash,
            "signature": message.signature,
            "signature_algorithm": message.signature_algorithm,
            "blockchain_tx_hash": message.blockchain_tx_hash,
            "blockchain_block_number": message.blockchain_block_number,
            "blockchain_confirmation_count": message.blockchain_confirmation_count,
            "ipfs_hash": message.ipfs_hash,
            "ipfs_gateway_url": message.ipfs_gateway_url,
            "status": message.status.value,
            "status_history": message.status_history
        }
    
    def _deserialize_message(self, data: Dict[str, Any]) -> SecureMessage:
        """反序列化消息"""
        message = SecureMessage(
            message_id=data["message_id"],
            message_type=MessageType(data["message_type"]),
            sender_id=data["sender_id"],
            recipient_id=data["recipient_id"],
            data_sensitivity=DataSensitivity(data["data_sensitivity"]),
            payload=data["payload"],
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"])
        )
        
        if data.get("encrypted_payload"):
            message.encrypted_payload = base64.b64decode(data["encrypted_payload"])
        
        message.encryption_key_hash = data.get("encryption_key_hash")
        message.signature = data.get("signature")
        message.signature_algorithm = data.get("signature_algorithm", "HMAC-SHA256")
        message.blockchain_tx_hash = data.get("blockchain_tx_hash")
        message.blockchain_block_number = data.get("blockchain_block_number")
        message.blockchain_confirmation_count = data.get("blockchain_confirmation_count", 0)
        message.ipfs_hash = data.get("ipfs_hash")
        message.ipfs_gateway_url = data.get("ipfs_gateway_url")
        message.status = MessageStatus(data.get("status", "pending"))
        message.status_history = data.get("status_history", [])
        
        return message
    
    async def _record_message_delivery(self, receipt: MessageDeliveryReceipt):
        """记录消息投递"""
        try:
            receipt_data = {
                "message_id": receipt.message_id,
                "recipient_id": receipt.recipient_id,
                "delivered_at": receipt.delivered_at.isoformat(),
                "blockchain_verified": receipt.blockchain_verified,
                "ipfs_accessible": receipt.ipfs_accessible,
                "signature_valid": receipt.signature_valid,
                "decryption_successful": receipt.decryption_successful
            }
            
            await self.redis.setex(
                f"delivery_receipt:{receipt.message_id}",
                30 * 24 * 3600,  # 30天TTL
                json.dumps(receipt_data)
            )
            
        except Exception as e:
            logger.error(f"记录消息投递失败: {e}")
    
    async def _publish_message_event(self, event_type: str, message: SecureMessage):
        """发布消息事件"""
        try:
            event_data = {
                "event_type": event_type,
                "message_id": message.message_id,
                "message_type": message.message_type.value,
                "sender_id": message.sender_id,
                "recipient_id": message.recipient_id,
                "status": message.status.value,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.redis.publish("blockchain_message_events", json.dumps(event_data))
            
        except Exception as e:
            logger.error(f"发布消息事件失败: {e}")
    
    async def _message_processor(self):
        """消息处理器后台任务"""
        while self._running:
            try:
                # 处理待处理的消息
                for message_id, message in list(self.pending_messages.items()):
                    if message.status == MessageStatus.SIGNED:
                        # 存储到IPFS
                        await self._store_to_ipfs(message)
                        
                        # 存储到区块链
                        await self._store_to_blockchain(message)
                        
                        # 移动到已投递队列
                        self.delivered_messages[message_id] = message
                        del self.pending_messages[message_id]
                        
                        # 存储到Redis
                        await self._store_message(message)
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"消息处理器异常: {e}")
                await asyncio.sleep(5)
    
    async def _blockchain_monitor(self):
        """区块链监控后台任务"""
        while self._running:
            try:
                # 监控区块链交易确认
                for message in self.delivered_messages.values():
                    if (message.blockchain_tx_hash and 
                        message.blockchain_confirmation_count < self.blockchain_config.confirmation_blocks):
                        
                        # 检查交易确认数
                        confirmations = await self._get_transaction_confirmations(
                            message.blockchain_tx_hash
                        )
                        
                        if confirmations >= 0:
                            message.blockchain_confirmation_count = confirmations
                            
                            if confirmations >= self.blockchain_config.confirmation_blocks:
                                message.add_status(MessageStatus.BLOCKCHAIN_CONFIRMED)
                                await self._store_message(message)
                
                await asyncio.sleep(30)  # 每30秒检查一次
                
            except Exception as e:
                logger.error(f"区块链监控异常: {e}")
                await asyncio.sleep(10)
    
    async def _ipfs_monitor(self):
        """IPFS监控后台任务"""
        while self._running:
            try:
                # 监控IPFS内容可访问性
                for message in self.delivered_messages.values():
                    if message.ipfs_hash and message.status != MessageStatus.DELIVERED:
                        accessible = await self._check_ipfs_accessibility(message.ipfs_hash)
                        if accessible:
                            message.add_status(MessageStatus.DELIVERED)
                            await self._store_message(message)
                
                await asyncio.sleep(60)  # 每分钟检查一次
                
            except Exception as e:
                logger.error(f"IPFS监控异常: {e}")
                await asyncio.sleep(10)
    
    async def _get_transaction_confirmations(self, tx_hash: str) -> int:
        """获取交易确认数"""
        try:
            # 这里需要根据具体的区块链网络实现
            # 示例：返回模拟的确认数
            return 3
            
        except Exception as e:
            logger.error(f"获取交易确认数失败: {e}")
            return -1
    
    async def _check_ipfs_accessibility(self, ipfs_hash: str) -> bool:
        """检查IPFS内容可访问性"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(
                    f"{self.ipfs_config.gateway_url}/ipfs/{ipfs_hash}",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.debug(f"IPFS内容不可访问: {ipfs_hash}")
            return False
    
    async def close(self):
        """关闭区块链消息总线"""
        self._running = False
        if self.redis:
            await self.redis.close()


# 全局区块链消息总线实例
_blockchain_message_bus: Optional[BlockchainMessageBus] = None


async def get_blockchain_message_bus() -> BlockchainMessageBus:
    """获取全局区块链消息总线"""
    global _blockchain_message_bus
    if _blockchain_message_bus is None:
        encryption_config = EncryptionConfig()
        blockchain_config = BlockchainConfig(
            network=BlockchainNetwork.ETHEREUM,
            node_url="http://localhost:8545"
        )
        ipfs_config = IPFSConfig()
        
        _blockchain_message_bus = BlockchainMessageBus(
            encryption_config=encryption_config,
            blockchain_config=blockchain_config,
            ipfs_config=ipfs_config
        )
        await _blockchain_message_bus.initialize()
    
    return _blockchain_message_bus


async def send_health_data_message(
    sender_id: str,
    recipient_id: str,
    health_data: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """发送健康数据消息的便捷函数"""
    bus = await get_blockchain_message_bus()
    
    return await bus.send_secure_message(
        message_type=MessageType.HEALTH_DATA,
        sender_id=sender_id,
        recipient_id=recipient_id,
        payload=health_data,
        data_sensitivity=DataSensitivity.CONFIDENTIAL,
        metadata=metadata
    )


async def send_agent_decision_message(
    agent_id: str,
    user_id: str,
    decision_data: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """发送智能体决策消息的便捷函数"""
    bus = await get_blockchain_message_bus()
    
    return await bus.send_secure_message(
        message_type=MessageType.AGENT_DECISION,
        sender_id=agent_id,
        recipient_id=user_id,
        payload=decision_data,
        data_sensitivity=DataSensitivity.INTERNAL,
        metadata=metadata
    )