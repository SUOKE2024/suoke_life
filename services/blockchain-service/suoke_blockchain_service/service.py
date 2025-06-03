"""
区块链服务实现

实现区块链相关的业务逻辑，包括健康数据存储、验证、访问控制等功能。
"""

import uuid
import hashlib
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.orm import selectinload

from .models import (
    BlockchainTransaction, HealthDataRecord, AccessGrant, 
    ZKProofRegistry, SmartContract, AuditLog,
    TransactionStatus, DataType, AccessLevel
)
from .database import get_database_session as get_db_session
from .blockchain_client import get_blockchain_client, TransactionReceipt
from .zk_integration import ZKProofGenerator, ZKProofVerifier
from .encryption import EncryptionService
from .ipfs_client import IPFSClient
from .config import settings
from .logging import get_logger
from .monitoring import record_operation_metrics
from .exceptions import (
    BlockchainServiceError, ValidationError, 
    NotFoundError, PermissionError, IntegrationError
)

logger = get_logger(__name__)

class BlockchainService:
    """区块链服务"""

    def __init__(self):
        self.encryption_service = EncryptionService()
        self.zk_proof_generator = ZKProofGenerator()
        self.zk_proof_verifier = ZKProofVerifier()
        self.ipfs_client = IPFSClient()

    async def store_health_data(
        self,
        user_id: str,
        data: Dict[str, Any],
        data_type: str,
        permissions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """存储健康数据到区块链"""
        try:
            logger.info("开始存储健康数据", user_id=user_id, data_type=data_type)
            
            # 验证输入
            self._validate_store_request(user_id, data, data_type)
            
            # 生成数据哈希
            data_hash = self._generate_data_hash(data)
            
            # 加密数据
            encrypted_data, encryption_key = await self.encryption_service.encrypt_data(
                json.dumps(data, ensure_ascii=False)
            )
            encryption_key_hash = hashlib.sha256(encryption_key.encode()).hexdigest()
            
            # 上传到IPFS
            ipfs_hash = await self.ipfs_client.upload_data(encrypted_data)
            
            # 生成零知识证明
            zkp_proof = await self.zk_proof_generator.generate_proof(
                data, 
                circuit_id=f"health_data_{data_type}"
            )
            
            async with get_db_session() as session:
                # 创建区块链交易记录
                transaction = BlockchainTransaction(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    status=TransactionStatus.PENDING,
                    data_hash=data_hash,
                    tx_metadata={
                        "data_type": data_type,
                        "permissions": permissions or {},
                        "ipfs_hash": ipfs_hash
                    }
                )
                session.add(transaction)
                
                # 创建健康数据记录
                health_record = HealthDataRecord(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    transaction_id=transaction.id,
                    data_type=DataType(data_type),
                    data_hash=data_hash,
                    encrypted_data=encrypted_data,
                    encryption_key_hash=encryption_key_hash,
                    ipfs_hash=ipfs_hash,
                    zkp_proof=zkp_proof,
                    public_inputs=zkp_proof.get("public_inputs", []),
                    verification_key=zkp_proof.get("verification_key", {}),
                    record_metadata={
                        "original_size": len(json.dumps(data)),
                        "encryption_algorithm": "AES-256-GCM",
                        "zkp_circuit": f"health_data_{data_type}"
                    }
                )
                session.add(health_record)
                
                # 创建ZK证明注册记录
                zk_registry = ZKProofRegistry(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    data_hash=data_hash,
                    proof_type=f"health_data_{data_type}",
                    proof_data=zkp_proof,
                    public_inputs=zkp_proof.get("public_inputs", []),
                    verification_key=zkp_proof.get("verification_key", {}),
                    circuit_id=f"health_data_{data_type}",
                    is_verified=False
                )
                session.add(zk_registry)
                
                await session.commit()
                
                # 发送到区块链
                blockchain_client = await get_blockchain_client()
                tx_hash = await blockchain_client.store_health_data(
                    data_hash=data_hash,
                    data_type=data_type,
                    ipfs_hash=ipfs_hash,
                    encryption_key_hash=encryption_key_hash
                )
                
                # 更新交易哈希
                transaction.transaction_hash = tx_hash
                await session.commit()
                
                # 记录审计日志
                await self._create_audit_log(
                    session=session,
                    user_id=user_id,
                    action="store_health_data",
                    resource_type="health_data",
                    resource_id=health_record.id,
                    new_values={
                        "data_type": data_type,
                        "data_hash": data_hash,
                        "transaction_hash": tx_hash
                    }
                )
                
                await session.commit()
                
                logger.info(
                    "健康数据存储成功",
                    user_id=user_id,
                    record_id=health_record.id,
                    tx_hash=tx_hash
                )
                
                record_operation_metrics("store_health_data", "success")
                
                return {
                    "record_id": health_record.id,
                    "transaction_id": transaction.id,
                    "transaction_hash": tx_hash,
                    "data_hash": data_hash,
                    "ipfs_hash": ipfs_hash,
                    "zkp_proof": zkp_proof,
                    "status": "pending"
                }
                
        except Exception as e:
            logger.error("存储健康数据失败", user_id=user_id, error=str(e))
            record_operation_metrics("store_health_data", "failed")
            raise BlockchainServiceError(f"存储健康数据失败: {str(e)}")

    async def verify_health_data(
        self,
        record_id: str,
        user_id: str,
        data_hash: Optional[str] = None
    ) -> Dict[str, Any]:
        """验证健康数据完整性"""
        try:
            logger.info("开始验证健康数据", record_id=record_id, user_id=user_id)
            
            async with get_db_session() as session:
                # 查询健康数据记录
                stmt = select(HealthDataRecord).where(
                    and_(
                        HealthDataRecord.id == record_id,
                        HealthDataRecord.user_id == user_id
                    )
                ).options(selectinload(HealthDataRecord.transaction))
                
                result = await session.execute(stmt)
                health_record = result.scalar_one_or_none()
                
                if not health_record:
                    raise NotFoundError(f"健康数据记录不存在: {record_id}")
                
                # 使用记录中的数据哈希（如果未提供）
                verify_hash = data_hash or health_record.data_hash
                
                # 区块链验证
                blockchain_client = await get_blockchain_client()
                
                # 获取区块链记录ID（简化实现，实际需要从交易回执中获取）
                blockchain_record_id = 1  # 这里需要实际的区块链记录ID
                
                blockchain_valid = await blockchain_client.verify_health_data(
                    record_id=blockchain_record_id,
                    data_hash=verify_hash
                )
                
                # ZK证明验证
                zkp_valid = False
                if health_record.zkp_proof:
                    zkp_valid = await self.zk_proof_verifier.verify_proof(
                        proof=health_record.zkp_proof,
                        public_inputs=health_record.public_inputs,
                        verification_key=health_record.verification_key,
                        circuit_id=health_record.record_metadata.get("zkp_circuit", "")
                    )
                
                # IPFS数据完整性验证
                ipfs_valid = False
                if health_record.ipfs_hash:
                    try:
                        ipfs_data = await self.ipfs_client.get_data(health_record.ipfs_hash)
                        ipfs_valid = (ipfs_data == health_record.encrypted_data)
                    except Exception as e:
                        logger.warning("IPFS验证失败", error=str(e))
                
                # 综合验证结果
                overall_valid = blockchain_valid and zkp_valid and ipfs_valid
                
                # 记录验证结果
                verification_result = {
                    "record_id": record_id,
                    "data_hash": verify_hash,
                    "blockchain_valid": blockchain_valid,
                    "zkp_valid": zkp_valid,
                    "ipfs_valid": ipfs_valid,
                    "overall_valid": overall_valid,
                    "verified_at": datetime.utcnow().isoformat(),
                    "transaction_hash": health_record.transaction.transaction_hash if health_record.transaction else None
                }
                
                # 记录审计日志
                await self._create_audit_log(
                    session=session,
                    user_id=user_id,
                    action="verify_health_data",
                    resource_type="health_data",
                    resource_id=record_id,
                    audit_metadata=verification_result
                )
                
                await session.commit()
                
                logger.info(
                    "健康数据验证完成",
                    record_id=record_id,
                    valid=overall_valid
                )
                
                record_operation_metrics("verify_health_data", "success")
                
                return verification_result
                
        except Exception as e:
            logger.error("验证健康数据失败", record_id=record_id, error=str(e))
            record_operation_metrics("verify_health_data", "failed")
            raise BlockchainServiceError(f"验证健康数据失败: {str(e)}")

    async def grant_access(
        self,
        owner_id: str,
        grantee_id: str,
        record_id: str,
        access_level: str,
        expires_at: Optional[datetime] = None,
        permissions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """授权访问健康数据"""
        try:
            logger.info(
                "开始授权访问",
                owner_id=owner_id,
                grantee_id=grantee_id,
                record_id=record_id
            )
            
            async with get_db_session() as session:
                # 验证健康数据记录存在且属于所有者
                stmt = select(HealthDataRecord).where(
                    and_(
                        HealthDataRecord.id == record_id,
                        HealthDataRecord.user_id == owner_id
                    )
                )
                result = await session.execute(stmt)
                health_record = result.scalar_one_or_none()
                
                if not health_record:
                    raise NotFoundError(f"健康数据记录不存在或无权限: {record_id}")
                
                # 检查是否已存在有效授权
                existing_grant_stmt = select(AccessGrant).where(
                    and_(
                        AccessGrant.owner_id == owner_id,
                        AccessGrant.grantee_id == grantee_id,
                        AccessGrant.health_record_id == record_id,
                        AccessGrant.is_active == True,
                        or_(
                            AccessGrant.expires_at.is_(None),
                            AccessGrant.expires_at > datetime.utcnow()
                        )
                    )
                )
                existing_result = await session.execute(existing_grant_stmt)
                existing_grant = existing_result.scalar_one_or_none()
                
                if existing_grant:
                    # 更新现有授权
                    existing_grant.access_level = AccessLevel(access_level)
                    existing_grant.permissions = permissions or {}
                    existing_grant.expires_at = expires_at
                    existing_grant.updated_at = datetime.utcnow()
                    grant = existing_grant
                else:
                    # 创建新的授权记录
                    grant = AccessGrant(
                        id=str(uuid.uuid4()),
                        owner_id=owner_id,
                        grantee_id=grantee_id,
                        health_record_id=record_id,
                        access_level=AccessLevel(access_level),
                        permissions=permissions or {},
                        expires_at=expires_at,
                        is_active=True
                    )
                    session.add(grant)
                
                # 创建区块链交易
                transaction = BlockchainTransaction(
                    id=str(uuid.uuid4()),
                    user_id=owner_id,
                    status=TransactionStatus.PENDING,
                    function_name="grantAccess",
                    tx_metadata={
                        "grantee_id": grantee_id,
                        "record_id": record_id,
                        "access_level": access_level
                    }
                )
                session.add(transaction)
                grant.transaction_id = transaction.id
                
                await session.commit()
                
                # 发送到区块链
                blockchain_client = await get_blockchain_client()
                
                # 这里需要grantee的区块链地址，简化实现
                grantee_address = f"0x{grantee_id[:40]}"  # 简化地址生成
                blockchain_record_id = 1  # 需要实际的区块链记录ID
                
                tx_hash = await blockchain_client.grant_access(
                    record_id=blockchain_record_id,
                    grantee_address=grantee_address
                )
                
                # 更新交易哈希
                transaction.transaction_hash = tx_hash
                await session.commit()
                
                # 记录审计日志
                await self._create_audit_log(
                    session=session,
                    user_id=owner_id,
                    action="grant_access",
                    resource_type="access_grant",
                    resource_id=grant.id,
                    new_values={
                        "grantee_id": grantee_id,
                        "access_level": access_level,
                        "transaction_hash": tx_hash
                    }
                )
                
                await session.commit()
                
                logger.info(
                    "访问授权成功",
                    grant_id=grant.id,
                    tx_hash=tx_hash
                )
                
                record_operation_metrics("grant_access", "success")
                
                return {
                    "grant_id": grant.id,
                    "transaction_id": transaction.id,
                    "transaction_hash": tx_hash,
                    "access_level": access_level,
                    "expires_at": expires_at.isoformat() if expires_at else None,
                    "status": "pending"
                }
                
        except Exception as e:
            logger.error("授权访问失败", error=str(e))
            record_operation_metrics("grant_access", "failed")
            raise BlockchainServiceError(f"授权访问失败: {str(e)}")

    async def revoke_access(
        self,
        owner_id: str,
        grantee_id: str,
        record_id: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """撤销访问授权"""
        try:
            logger.info(
                "开始撤销访问",
                owner_id=owner_id,
                grantee_id=grantee_id,
                record_id=record_id
            )
            
            async with get_db_session() as session:
                # 查找有效的授权记录
                stmt = select(AccessGrant).where(
                    and_(
                        AccessGrant.owner_id == owner_id,
                        AccessGrant.grantee_id == grantee_id,
                        AccessGrant.health_record_id == record_id,
                        AccessGrant.is_active == True
                    )
                )
                result = await session.execute(stmt)
                grant = result.scalar_one_or_none()
                
                if not grant:
                    raise NotFoundError("访问授权不存在或已撤销")
                
                # 撤销授权
                grant.is_active = False
                grant.revoked_at = datetime.utcnow()
                grant.revocation_reason = reason
                grant.updated_at = datetime.utcnow()
                
                # 创建区块链交易
                transaction = BlockchainTransaction(
                    id=str(uuid.uuid4()),
                    user_id=owner_id,
                    status=TransactionStatus.PENDING,
                    function_name="revokeAccess",
                    tx_metadata={
                        "grantee_id": grantee_id,
                        "record_id": record_id,
                        "reason": reason
                    }
                )
                session.add(transaction)
                
                await session.commit()
                
                # 发送到区块链
                blockchain_client = await get_blockchain_client()
                
                grantee_address = f"0x{grantee_id[:40]}"  # 简化地址生成
                blockchain_record_id = 1  # 需要实际的区块链记录ID
                
                tx_hash = await blockchain_client.revoke_access(
                    record_id=blockchain_record_id,
                    grantee_address=grantee_address
                )
                
                # 更新交易哈希
                transaction.transaction_hash = tx_hash
                await session.commit()
                
                # 记录审计日志
                await self._create_audit_log(
                    session=session,
                    user_id=owner_id,
                    action="revoke_access",
                    resource_type="access_grant",
                    resource_id=grant.id,
                    old_values={"is_active": True},
                    new_values={
                        "is_active": False,
                        "reason": reason,
                        "transaction_hash": tx_hash
                    }
                )
                
                await session.commit()
                
                logger.info(
                    "访问撤销成功",
                    grant_id=grant.id,
                    tx_hash=tx_hash
                )
                
                record_operation_metrics("revoke_access", "success")
                
                return {
                    "grant_id": grant.id,
                    "transaction_id": transaction.id,
                    "transaction_hash": tx_hash,
                    "revoked_at": grant.revoked_at.isoformat(),
                    "reason": reason,
                    "status": "pending"
                }
                
        except Exception as e:
            logger.error("撤销访问失败", error=str(e))
            record_operation_metrics("revoke_access", "failed")
            raise BlockchainServiceError(f"撤销访问失败: {str(e)}")

    async def get_health_records(
        self,
        user_id: str,
        data_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """获取用户的健康数据记录列表"""
        try:
            async with get_db_session() as session:
                # 构建查询
                stmt = select(HealthDataRecord).where(
                    HealthDataRecord.user_id == user_id
                )
                
                if data_type:
                    stmt = stmt.where(HealthDataRecord.data_type == DataType(data_type))
                
                stmt = stmt.order_by(desc(HealthDataRecord.created_at))
                stmt = stmt.offset(offset).limit(limit)
                stmt = stmt.options(selectinload(HealthDataRecord.transaction))
                
                result = await session.execute(stmt)
                records = result.scalars().all()
                
                # 获取总数
                count_stmt = select(HealthDataRecord).where(
                    HealthDataRecord.user_id == user_id
                )
                if data_type:
                    count_stmt = count_stmt.where(HealthDataRecord.data_type == DataType(data_type))
                
                count_result = await session.execute(count_stmt)
                total_count = len(count_result.scalars().all())
                
                # 格式化返回数据
                records_data = []
                for record in records:
                    records_data.append({
                        "id": record.id,
                        "data_type": record.data_type.value,
                        "data_hash": record.data_hash,
                        "ipfs_hash": record.ipfs_hash,
                        "created_at": record.created_at.isoformat(),
                        "transaction_hash": record.transaction.transaction_hash if record.transaction else None,
                        "transaction_status": record.transaction.status.value if record.transaction else None,
                        "has_zkp": bool(record.zkp_proof),
                        "metadata": record.record_metadata
                    })
                
                return {
                    "records": records_data,
                    "total_count": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + len(records) < total_count
                }
                
        except Exception as e:
            logger.error("获取健康记录失败", user_id=user_id, error=str(e))
            raise BlockchainServiceError(f"获取健康记录失败: {str(e)}")

    async def get_access_grants(
        self,
        user_id: str,
        as_owner: bool = True,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """获取访问授权列表"""
        try:
            async with get_db_session() as session:
                # 构建查询
                if as_owner:
                    stmt = select(AccessGrant).where(AccessGrant.owner_id == user_id)
                else:
                    stmt = select(AccessGrant).where(AccessGrant.grantee_id == user_id)
                
                if active_only:
                    stmt = stmt.where(
                        and_(
                            AccessGrant.is_active == True,
                            or_(
                                AccessGrant.expires_at.is_(None),
                                AccessGrant.expires_at > datetime.utcnow()
                            )
                        )
                    )
                
                stmt = stmt.order_by(desc(AccessGrant.created_at))
                stmt = stmt.options(
                    selectinload(AccessGrant.health_record),
                    selectinload(AccessGrant.transaction)
                )
                
                result = await session.execute(stmt)
                grants = result.scalars().all()
                
                # 格式化返回数据
                grants_data = []
                for grant in grants:
                    grants_data.append({
                        "id": grant.id,
                        "owner_id": grant.owner_id,
                        "grantee_id": grant.grantee_id,
                        "health_record_id": grant.health_record_id,
                        "access_level": grant.access_level.value,
                        "permissions": grant.permissions,
                        "granted_at": grant.granted_at.isoformat(),
                        "expires_at": grant.expires_at.isoformat() if grant.expires_at else None,
                        "is_active": grant.is_active,
                        "revoked_at": grant.revoked_at.isoformat() if grant.revoked_at else None,
                        "revocation_reason": grant.revocation_reason,
                        "transaction_hash": grant.transaction.transaction_hash if grant.transaction else None,
                        "health_record": {
                            "data_type": grant.health_record.data_type.value,
                            "created_at": grant.health_record.created_at.isoformat()
                        } if grant.health_record else None
                    })
                
                return grants_data
                
        except Exception as e:
            logger.error("获取访问授权失败", user_id=user_id, error=str(e))
            raise BlockchainServiceError(f"获取访问授权失败: {str(e)}")

    def _validate_store_request(
        self, 
        user_id: str, 
        data: Dict[str, Any], 
        data_type: str
    ) -> None:
        """验证存储请求"""
        if not user_id:
            raise ValidationError("用户ID不能为空")
        
        if not data:
            raise ValidationError("数据不能为空")
        
        if not data_type:
            raise ValidationError("数据类型不能为空")
        
        try:
            DataType(data_type)
        except ValueError:
            raise ValidationError(f"无效的数据类型: {data_type}")
        
        # 验证数据大小
        data_size = len(json.dumps(data, ensure_ascii=False))
        if data_size > settings.blockchain.max_data_size:
            raise ValidationError(f"数据大小超过限制: {data_size} > {settings.blockchain.max_data_size}")

    def _generate_data_hash(self, data: Dict[str, Any]) -> str:
        """生成数据哈希"""
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()

    async def _create_audit_log(
        self,
        session: AsyncSession,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        audit_metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """创建审计日志"""
        audit_log = AuditLog(
            id=str(uuid.uuid4()),
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            success=success,
            error_message=error_message,
            audit_metadata=audit_metadata
        )
        session.add(audit_log)

# 全局服务实例
_blockchain_service: Optional[BlockchainService] = None

def get_blockchain_service() -> BlockchainService:
    """获取区块链服务实例"""
    global _blockchain_service
    
    if _blockchain_service is None:
        _blockchain_service = BlockchainService()
    
    return _blockchain_service 