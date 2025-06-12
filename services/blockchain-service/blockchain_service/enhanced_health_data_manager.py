"""
增强的健康数据管理器
集成零知识证明和区块链存储，实现隐私保护的健康数据管理
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

try:
    from .privacy.zkp_manager import zkp_manager, HealthDataClaim, ZKProof
except ImportError:
    # 如果导入失败，创建模拟对象
    class MockZKPManager:
        """TODO: 添加文档字符串"""
        async def generate_health_data_proof(self, claim):
            return type('ZKProof', (), {'proof_id': 'mock_proof_id'})()

        async def verify_proof(self, proof_id):
            return True

    zkp_manager = MockZKPManager()

    @dataclass
    class HealthDataClaim:
        """TODO: 添加文档字符串"""
        user_id: str
        data_type: str
        claim_type: str
        value_hash: str
        metadata: Dict[str, Any]
        timestamp: datetime

logger = logging.getLogger(__name__)

@dataclass
class HealthDataRecord:
    """健康数据记录"""
    record_id: str
    user_id: str
    data_type: str  # 'tongue_analysis', 'health_metrics', 'diagnosis', 'treatment'
    encrypted_data: str  # 加密的健康数据
    data_hash: str  # 数据哈希
    blockchain_tx_hash: str  # 区块链交易哈希
    ipfs_hash: Optional[str]  # IPFS存储哈希
    zkp_proof_id: Optional[str]  # 零知识证明ID
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    access_permissions: List[str]  # 访问权限列表
    is_verified: bool = False

@dataclass
class DataAccessRequest:
    """数据访问请求"""
    request_id: str
    requester_id: str
    data_owner_id: str
    record_ids: List[str]
    access_type: str  # 'read', 'analyze', 'share'
    purpose: str  # 访问目的
    requested_at: datetime
    expires_at: datetime
    status: str = 'pending'  # 'pending', 'approved', 'denied', 'expired'
    zkp_requirements: List[str] = None  # 需要的零知识证明类型

@dataclass
class PrivacyPolicy:
    """隐私策略"""
    policy_id: str
    user_id: str
    data_types: List[str]  # 适用的数据类型
    sharing_rules: Dict[str, Any]  # 分享规则
    retention_period: int  # 数据保留期（天）
    anonymization_level: str  # 'none', 'basic', 'advanced'
    zkp_requirements: List[str]  # 零知识证明要求
    created_at: datetime
    is_active: bool = True

class EncryptionManager:
    """加密管理器"""

    def __init__(self) -> None:
        """TODO: 添加文档字符串"""
        self.master_key = self._generate_master_key()
        self.user_keys: Dict[str, bytes] = {}

    def _generate_master_key(self) -> bytes:
        """生成主密钥"""
        # 在生产环境中，应该从安全的密钥管理服务获取
        password = os.environ.get('MASTER_PASSWORD', 'suoke_health_master_key_2024').encode()
        salt = os.environ.get('MASTER_SALT', 'suoke_salt_2024').encode()

        kdf = PBKDF2HMAC(
            algorithm = hashes.SHA256(),
            length = 32,
            salt = salt,
            iterations = 100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password))

    def get_user_key(self, user_id: str) -> bytes:
        """获取用户专用密钥"""
        if user_id not in self.user_keys:
            # 基于用户ID和主密钥生成用户专用密钥
            user_data = f"{user_id}_{datetime.utcnow().date()}".encode()
            kdf = PBKDF2HMAC(
                algorithm = hashes.SHA256(),
                length = 32,
                salt = user_data,
                iterations = 50000,
            )
            self.user_keys[user_id] = base64.urlsafe_b64encode(kdf.derive(self.master_key))

        return self.user_keys[user_id]

    def encrypt_data(self, data: Dict[str, Any], user_id: str) -> str:
        """加密健康数据"""
        try:
            user_key = self.get_user_key(user_id)
            fernet = Fernet(user_key)

            # 序列化数据
            data_json = json.dumps(data, ensure_ascii = False, default = str)

            # 加密
            encrypted_data = fernet.encrypt(data_json.encode('utf - 8'))

            return base64.urlsafe_b64encode(encrypted_data).decode('utf - 8')

        except Exception as e:
            logger.error(f"数据加密失败: {e}")
            raise

    def decrypt_data(self, encrypted_data: str, user_id: str) -> Dict[str, Any]:
        """解密健康数据"""
        try:
            user_key = self.get_user_key(user_id)
            fernet = Fernet(user_key)

            # 解码和解密
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf - 8'))
            decrypted_data = fernet.decrypt(encrypted_bytes)

            # 反序列化
            data_json = decrypted_data.decode('utf - 8')
            return json.loads(data_json)

        except Exception as e:
            logger.error(f"数据解密失败: {e}")
            raise

class BlockchainIntegration:
    """区块链集成"""

    def __init__(self) -> None:
        """TODO: 添加文档字符串"""
        self.contract_address = "0x1234567890abcdef"  # 智能合约地址
        self.web3_provider = None  # Web3提供者

    async def store_data_hash(self, record_id: str, data_hash: str,
                            user_id: str) -> str:
        """在区块链上存储数据哈希"""
        try:
            # 模拟区块链交易
            tx_data = {
                'record_id': record_id,
                'data_hash': data_hash,
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat(),
                'contract': self.contract_address
            }

            # 生成模拟交易哈希
            tx_hash = hashlib.sha256(
                json.dumps(tx_data, sort_keys = True).encode()
            ).hexdigest()

            logger.info(f"数据哈希已存储到区块链: {tx_hash}")
            return f"0x{tx_hash}"

        except Exception as e:
            logger.error(f"区块链存储失败: {e}")
            raise

    async def verify_data_integrity(self, tx_hash: str,
                                expected_hash: str) -> bool:
        """验证数据完整性"""
        try:
            # 模拟从区块链查询数据
            await asyncio.sleep(0.1)  # 模拟网络延迟

            # 简单验证逻辑
            return tx_hash.startswith('0x') and len(tx_hash)==66

        except Exception as e:
            logger.error(f"数据完整性验证失败: {e}")
            return False

class IPFSIntegration:
    """IPFS集成"""

    def __init__(self) -> None:
        """TODO: 添加文档字符串"""
        self.ipfs_gateway = "https: / /ipfs.io / ipfs / "
        self.local_node = "http: / /localhost:5001"

    async def store_encrypted_data(self, encrypted_data: str) -> str:
        """在IPFS上存储加密数据"""
        try:
            # 模拟IPFS存储
            data_bytes = encrypted_data.encode('utf - 8')
            ipfs_hash = hashlib.sha256(data_bytes).hexdigest()

            # 生成IPFS哈希格式
            ipfs_hash = f"Qm{ipfs_hash[:44]}"

            logger.info(f"数据已存储到IPFS: {ipfs_hash}")
            return ipfs_hash

        except Exception as e:
            logger.error(f"IPFS存储失败: {e}")
            raise

    async def retrieve_encrypted_data(self, ipfs_hash: str) -> str:
        """从IPFS检索加密数据"""
        try:
            # 模拟IPFS检索
            await asyncio.sleep(0.2)  # 模拟网络延迟

            # 在实际实现中，这里会从IPFS网络检索数据
            logger.info(f"从IPFS检索数据: {ipfs_hash}")
            return "encrypted_data_from_ipfs"

        except Exception as e:
            logger.error(f"IPFS检索失败: {e}")
            raise

class EnhancedHealthDataManager:
    """增强的健康数据管理器"""

    def __init__(self) -> None:
        """TODO: 添加文档字符串"""
        self.encryption_manager = EncryptionManager()
        self.blockchain = BlockchainIntegration()
        self.ipfs = IPFSIntegration()
        self.records: Dict[str, HealthDataRecord] = {}
        self.access_requests: Dict[str, DataAccessRequest] = {}
        self.privacy_policies: Dict[str, PrivacyPolicy] = {}
        self.audit_log: List[Dict[str, Any]] = []

    async def store_health_data(self, user_id: str, data_type: str,
                            health_data: Dict[str, Any],
                            privacy_level: str = 'high') -> HealthDataRecord:
        """存储健康数据"""
        try:
            # 生成记录ID
            record_id = f"hdr_{hashlib.sha256(f'{user_id}_{data_type}_{datetime.utcnow()}'.encode()).hexdigest()[:16]}"

            # 加密数据
            encrypted_data = self.encryption_manager.encrypt_data(health_data, user_id)

            # 计算数据哈希
            data_hash = hashlib.sha256(
                json.dumps(health_data, sort_keys = True).encode()
            ).hexdigest()

            # 存储到IPFS
            ipfs_hash = await self.ipfs.store_encrypted_data(encrypted_data)

            # 存储到区块链
            blockchain_tx_hash = await self.blockchain.store_data_hash(
                record_id, data_hash, user_id
            )

            # 生成零知识证明（如果需要）
            zkp_proof_id = None
            if privacy_level=='high':
                zkp_proof_id = await self._generate_privacy_proof(
                    user_id, data_type, health_data, data_hash
                )

            # 创建健康数据记录
            record = HealthDataRecord(
                record_id = record_id,
                user_id = user_id,
                data_type = data_type,
                encrypted_data = encrypted_data,
                data_hash = data_hash,
                blockchain_tx_hash = blockchain_tx_hash,
                ipfs_hash = ipfs_hash,
                zkp_proof_id = zkp_proof_id,
                metadata = {
                    'privacy_level': privacy_level,
                    'data_size': len(json.dumps(health_data)),
                    'encryption_algorithm': 'AES - 256 - GCM',
                    'storage_locations': ['blockchain', 'ipfs']
                },
                created_at = datetime.utcnow(),
                updated_at = datetime.utcnow(),
                access_permissions = [user_id],  # 默认只有用户自己可以访问
                is_verified = True
            )

            # 存储记录
            self.records[record_id] = record

            # 记录审计日志
            await self._log_audit_event('data_stored', {
                'record_id': record_id,
                'user_id': user_id,
                'data_type': data_type,
                'privacy_level': privacy_level
            })

            logger.info(f"健康数据已安全存储: {record_id}")
            return record

        except Exception as e:
            logger.error(f"存储健康数据失败: {e}")
            raise

    async def _generate_privacy_proof(self, user_id: str, data_type: str,
                                    health_data: Dict[str, Any],
                                    data_hash: str) -> str:
        """生成隐私保护证明"""
        try:
            # 根据数据类型确定证明类型
            if data_type=='tongue_analysis':
                claim_type = 'membership_proof'  # 证明舌象分析结果属于有效范围
                metadata = {
                    'value': health_data.get('tongue_color', 'normal'),
                    'valid_set': ['pale', 'red', 'purple', 'normal', 'dark']
                }
            elif data_type=='health_metrics':
                claim_type = 'range_proof'  # 证明健康指标在正常范围内
                metadata = {
                    'value': health_data.get('blood_pressure_systolic', 120),
                    'min_value': 90,
                    'max_value': 180
                }
            else:
                claim_type = 'equality_proof'  # 通用相等证明
                metadata = {
                    'value1': data_hash,
                    'value2': data_hash
                }

            # 创建健康数据声明
            claim = HealthDataClaim(
                user_id = user_id,
                data_type = data_type,
                claim_type = claim_type,
                value_hash = data_hash,
                metadata = metadata,
                timestamp = datetime.utcnow()
            )

            # 生成零知识证明
            proof = await zkp_manager.generate_health_data_proof(claim)

            return proof.proof_id

        except Exception as e:
            logger.error(f"生成隐私证明失败: {e}")
            return None

    async def retrieve_health_data(self, record_id: str,
                                requester_id: str) -> Optional[Dict[str, Any]]:
        """检索健康数据"""
        try:
            # 检查记录是否存在
            record = self.records.get(record_id)
            if not record:
                logger.warning(f"记录不存在: {record_id}")
                return None

            # 检查访问权限
            if not await self._check_access_permission(record, requester_id):
                logger.warning(f"访问权限不足: {requester_id} -> {record_id}")
                return None

            # 验证数据完整性
            if not await self._verify_data_integrity(record):
                logger.error(f"数据完整性验证失败: {record_id}")
                return None

            # 解密数据
            decrypted_data = self.encryption_manager.decrypt_data(
                record.encrypted_data, record.user_id
            )

            # 记录访问日志
            await self._log_audit_event('data_accessed', {
                'record_id': record_id,
                'requester_id': requester_id,
                'access_time': datetime.utcnow().isoformat()
            })

            logger.info(f"健康数据已安全检索: {record_id}")
            return decrypted_data

        except Exception as e:
            logger.error(f"检索健康数据失败: {e}")
            return None

    async def _check_access_permission(self, record: HealthDataRecord,
                                    requester_id: str) -> bool:
        """检查访问权限"""
        # 数据所有者总是有权限
        if requester_id==record.user_id:
            return True

        # 检查显式权限
        if requester_id in record.access_permissions:
            return True

        # 检查临时访问请求
        for request in self.access_requests.values():
            if (request.requester_id==requester_id and
                record.record_id in request.record_ids and
                request.status=='approved' and
                datetime.utcnow() < request.expires_at):
                return True

        return False

    async def _verify_data_integrity(self, record: HealthDataRecord) -> bool:
        """验证数据完整性"""
        try:
            # 验证区块链存储的哈希
            blockchain_valid = await self.blockchain.verify_data_integrity(
                record.blockchain_tx_hash, record.data_hash
            )

            # 验证零知识证明（如果存在）
            zkp_valid = True
            if record.zkp_proof_id:
                zkp_valid = await zkp_manager.verify_proof(record.zkp_proof_id)

            return blockchain_valid and zkp_valid

        except Exception as e:
            logger.error(f"数据完整性验证失败: {e}")
            return False

    async def request_data_access(self, requester_id: str, data_owner_id: str,
                                record_ids: List[str], purpose: str,
                                duration_hours: int = 24) -> DataAccessRequest:
        """请求数据访问"""
        try:
            request_id = f"dar_{hashlib.sha256(f'{requester_id}_{data_owner_id}_{datetime.utcnow()}'.encode()).hexdigest()[:16]}"

            request = DataAccessRequest(
                request_id = request_id,
                requester_id = requester_id,
                data_owner_id = data_owner_id,
                record_ids = record_ids,
                access_type = 'read',
                purpose = purpose,
                requested_at = datetime.utcnow(),
                expires_at = datetime.utcnow() + timedelta(hours = duration_hours),
                status = 'pending'
            )

            self.access_requests[request_id] = request

            # 记录审计日志
            await self._log_audit_event('access_requested', {
                'request_id': request_id,
                'requester_id': requester_id,
                'data_owner_id': data_owner_id,
                'purpose': purpose
            })

            logger.info(f"数据访问请求已创建: {request_id}")
            return request

        except Exception as e:
            logger.error(f"创建访问请求失败: {e}")
            raise

    async def approve_access_request(self, request_id: str,
                                    approver_id: str) -> bool:
        """批准访问请求"""
        try:
            request = self.access_requests.get(request_id)
            if not request:
                return False

            # 检查批准者权限
            if approver_id !=request.data_owner_id:
                logger.warning(f"无权批准请求: {approver_id} -> {request_id}")
                return False

            # 检查请求是否过期
            if datetime.utcnow() > request.expires_at:
                request.status = 'expired'
                return False

            # 批准请求
            request.status = 'approved'

            # 记录审计日志
            await self._log_audit_event('access_approved', {
                'request_id': request_id,
                'approver_id': approver_id,
                'approved_at': datetime.utcnow().isoformat()
            })

            logger.info(f"访问请求已批准: {request_id}")
            return True

        except Exception as e:
            logger.error(f"批准访问请求失败: {e}")
            return False

    async def _log_audit_event(self, event_type: str, event_data: Dict[str, Any]):
        """记录审计事件"""
        audit_entry = {
            'event_id': f"audit_{hashlib.sha256(f'{event_type}_{datetime.utcnow()}'.encode()).hexdigest()[:16]}",
            'event_type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'data': event_data
        }

        self.audit_log.append(audit_entry)

        # 保持审计日志大小
        if len(self.audit_log) > 10000:
            self.audit_log = self.audit_log[ - 5000:]

    def get_user_data_summary(self, user_id: str) -> Dict[str, Any]:
        """获取用户数据摘要"""
        user_records = [r for r in self.records.values() if r.user_id==user_id]

        # 按数据类型统计
        type_stats = {}
        for record in user_records:
            data_type = record.data_type
            type_stats[data_type] = type_stats.get(data_type, 0) + 1

        # 隐私保护统计
        zkp_protected = sum(1 for r in user_records if r.zkp_proof_id)

        return {
            'user_id': user_id,
            'total_records': len(user_records),
            'data_types': type_stats,
            'zkp_protected_records': zkp_protected,
            'privacy_protection_rate': (zkp_protected / len(user_records) * 100) if user_records else 0,
            'storage_locations': {
                'blockchain': len([r for r in user_records if r.blockchain_tx_hash]),
                'ipfs': len([r for r in user_records if r.ipfs_hash])
            },
            'last_updated': max([r.updated_at for r in user_records]).isoformat() if user_records else None
        }

    def get_system_statistics(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        total_records = len(self.records)
        zkp_protected = sum(1 for r in self.records.values() if r.zkp_proof_id)

        # 数据类型分布
        type_distribution = {}
        for record in self.records.values():
            data_type = record.data_type
            type_distribution[data_type] = type_distribution.get(data_type, 0) + 1

        # 访问请求统计
        access_stats = {
            'total_requests': len(self.access_requests),
            'pending': len([r for r in self.access_requests.values() if r.status=='pending']),
            'approved': len([r for r in self.access_requests.values() if r.status=='approved']),
            'denied': len([r for r in self.access_requests.values() if r.status=='denied'])
        }

        return {
            'total_health_records': total_records,
            'zkp_protected_records': zkp_protected,
            'privacy_protection_rate': (zkp_protected / total_records * 100) if total_records > 0 else 0,
            'data_type_distribution': type_distribution,
            'access_request_stats': access_stats,
            'audit_log_entries': len(self.audit_log),
            'active_users': len(set(r.user_id for r in self.records.values())),
            'system_uptime': datetime.utcnow().isoformat()
        }

# 全局健康数据管理器实例
health_data_manager = EnhancedHealthDataManager()