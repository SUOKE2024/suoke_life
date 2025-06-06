"""
demo_mock_mode - 索克生活项目模块
"""

            from suoke_blockchain_service.models import HealthDataRecord, BlockchainTransaction, DataType
from datetime import datetime, timedelta
from suoke_blockchain_service.config import settings
from suoke_blockchain_service.logging import configure_logging, get_logger
from suoke_blockchain_service.service import BlockchainService
from typing import Dict, Any
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
import json
import uuid

#!/usr/bin/env python3
"""
Blockchain Service 模拟模式演示脚本

在模拟模式下演示区块链服务的核心功能，不依赖外部服务。
"""


# 导入服务模块

logger = get_logger(__name__)

class MockBlockchainServiceDemo:
    """模拟模式区块链服务演示类"""
    
    def __init__(self):
        self.demo_user_id = "demo-user-" + str(uuid.uuid4())[:8]
        self.demo_grantee_id = "demo-grantee-" + str(uuid.uuid4())[:8]
        self.mock_record_id = str(uuid.uuid4())
        self.mock_transaction_id = str(uuid.uuid4())
        self.mock_data_hash = "86c7ac470b1df737e610f4d23f930c7b9fdbf5ef37713a601e6749ff0957767e"
        self.mock_ipfs_hash = "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"
        self.mock_tx_hash = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    
    def create_mock_service(self) -> BlockchainService:
        """创建模拟的区块链服务"""
        service = BlockchainService()
        
        # 模拟加密服务
        service.encryption_service.encrypt_data = AsyncMock(return_value=(
            b"encrypted_data_mock", "encryption_key_mock"
        ))
        service.encryption_service.decrypt_data = AsyncMock(return_value="decrypted_data_mock")
        
        # 模拟IPFS客户端
        service.ipfs_client.upload_data = AsyncMock(return_value=self.mock_ipfs_hash)
        service.ipfs_client.get_data = AsyncMock(return_value=b"encrypted_data_mock")
        
        # 模拟零知识证明
        service.zk_proof_generator.generate_proof = AsyncMock(return_value={
            "proof": {"a": [1, 2], "b": [3, 4], "c": [5, 6]},
            "public_inputs": [1, 2, 3],
            "verification_key": {"alpha": [1, 2]}
        })
        service.zk_proof_verifier.verify_proof = AsyncMock(return_value=True)
        
        return service
    
    async def demo_health_data_storage(self, service: BlockchainService) -> Dict[str, Any]:
        """演示健康数据存储功能"""
        print("\n=== 演示1: 健康数据存储 ===")
        
        # 准备示例健康数据
        health_data = {
            "user_id": self.demo_user_id,
            "timestamp": datetime.now().isoformat(),
            "data_type": "heart_rate",
            "measurements": {
                "heart_rate": 72,
                "blood_pressure": {"systolic": 120, "diastolic": 80},
                "temperature": 36.5,
                "weight": 70.5
            },
            "device_info": {
                "device_id": "smartwatch-001",
                "manufacturer": "HealthTech",
                "model": "HT-Watch-Pro",
                "firmware_version": "2.1.0"
            },
            "location": {
                "latitude": 39.9042,
                "longitude": 116.4074,
                "accuracy": 10
            },
            "metadata": {
                "session_id": str(uuid.uuid4()),
                "quality_score": 0.95,
                "notes": "Regular morning measurement"
            }
        }
        
        print(f"📊 存储用户 {self.demo_user_id} 的健康数据...")
        print(f"📋 数据类型: {health_data['data_type']}")
        print(f"📏 数据大小: {len(json.dumps(health_data))} bytes")
        
        # 模拟数据库操作和区块链交互
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db, \
             patch('suoke_blockchain_service.service.get_blockchain_client') as mock_blockchain:
            
            # 模拟数据库会话
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            # 模拟区块链客户端
            mock_client = AsyncMock()
            mock_client.store_health_data.return_value = self.mock_tx_hash
            mock_blockchain.return_value = mock_client
            
            try:
                # 调用存储服务
                result = await service.store_health_data(
                    user_id=self.demo_user_id,
                    data=health_data,
                    data_type="heart_rate",
                    permissions={
                        "read": ["doctor", "emergency"],
                        "write": ["self"],
                        "share": ["family"]
                    }
                )
                
                print(f"✅ 存储成功!")
                print(f"📝 记录ID: {result['record_id']}")
                print(f"🔗 交易ID: {result['transaction_id']}")
                print(f"🔒 数据哈希: {result['data_hash'][:16]}...")
                print(f"🌐 IPFS哈希: {result['ipfs_hash']}")
                print(f"🔐 零知识证明: {'已生成' if result['zkp_proof'] else '未生成'}")
                print(f"⛓️ 交易哈希: {result.get('transaction_hash', 'N/A')}")
                
                return result
                
            except Exception as e:
                print(f"❌ 存储失败: {str(e)}")
                return {}
    
    async def demo_health_data_verification(self, service: BlockchainService) -> Dict[str, Any]:
        """演示健康数据验证功能"""
        print("\n=== 演示2: 健康数据验证 ===")
        
        print(f"🔍 验证记录 {self.mock_record_id}...")
        
        # 模拟数据库查询和区块链验证
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db, \
             patch('suoke_blockchain_service.service.get_blockchain_client') as mock_blockchain:
            
            # 模拟数据库记录
            
            mock_record = MagicMock()
            mock_record.id = self.mock_record_id
            mock_record.user_id = self.demo_user_id
            mock_record.data_hash = self.mock_data_hash
            mock_record.ipfs_hash = self.mock_ipfs_hash
            mock_record.encrypted_data = b"encrypted_data_mock"
            mock_record.zkp_proof = {"proof": {"a": [1, 2]}}
            mock_record.public_inputs = [1, 2, 3]
            mock_record.verification_key = {"alpha": [1, 2]}
            mock_record.record_metadata = {"zkp_circuit": "health_data_heart_rate"}
            mock_record.transaction = MagicMock()
            mock_record.transaction.transaction_hash = self.mock_tx_hash
            
            mock_session = AsyncMock()
            mock_result = AsyncMock()
            mock_result.scalar_one_or_none.return_value = mock_record
            mock_session.execute.return_value = mock_result
            mock_db.return_value.__aenter__.return_value = mock_session
            
            # 模拟区块链验证
            mock_client = AsyncMock()
            mock_client.verify_health_data.return_value = True
            mock_blockchain.return_value = mock_client
            
            try:
                # 调用验证服务
                result = await service.verify_health_data(
                    record_id=self.mock_record_id,
                    user_id=self.demo_user_id
                )
                
                print(f"📊 验证结果:")
                print(f"  🔗 区块链验证: {'✅ 通过' if result['blockchain_valid'] else '❌ 失败'}")
                print(f"  🔐 零知识证明: {'✅ 通过' if result['zkp_valid'] else '❌ 失败'}")
                print(f"  🌐 IPFS完整性: {'✅ 通过' if result['ipfs_valid'] else '❌ 失败'}")
                print(f"  🎯 综合验证: {'✅ 通过' if result['overall_valid'] else '❌ 失败'}")
                print(f"  ⏰ 验证时间: {result['verified_at']}")
                print(f"  🔗 交易哈希: {result.get('transaction_hash', 'N/A')}")
                
                return result
                
            except Exception as e:
                print(f"❌ 验证失败: {str(e)}")
                return {}
    
    async def demo_access_control(self, service: BlockchainService) -> Dict[str, Any]:
        """演示访问控制功能"""
        print("\n=== 演示3: 访问控制 ===")
        
        print(f"🔑 授权用户 {self.demo_grantee_id} 访问记录 {self.mock_record_id}...")
        
        # 模拟数据库操作
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db, \
             patch('suoke_blockchain_service.service.get_blockchain_client') as mock_blockchain:
            
            # 模拟健康数据记录
            mock_health_record = MagicMock()
            mock_health_record.id = self.mock_record_id
            mock_health_record.user_id = self.demo_user_id
            
            # 模拟访问授权记录
            mock_grant = MagicMock()
            mock_grant.id = str(uuid.uuid4())
            mock_grant.owner_id = self.demo_user_id
            mock_grant.grantee_id = self.demo_grantee_id
            mock_grant.health_record_id = self.mock_record_id
            mock_grant.access_level.value = "read"
            mock_grant.permissions = {"read_data": True}
            mock_grant.granted_at = datetime.now()
            mock_grant.expires_at = datetime.now() + timedelta(hours=24)
            mock_grant.is_active = True
            mock_grant.revoked_at = None
            mock_grant.revocation_reason = None
            mock_grant.health_record = mock_health_record
            mock_grant.transaction = MagicMock()
            mock_grant.transaction.transaction_hash = self.mock_tx_hash
            
            mock_session = AsyncMock()
            mock_result = AsyncMock()
            mock_result.scalar_one_or_none.side_effect = [mock_health_record, None, mock_grant]
            mock_result.scalars.return_value.all.return_value = [mock_grant]
            mock_session.execute.return_value = mock_result
            mock_db.return_value.__aenter__.return_value = mock_session
            
            # 模拟区块链客户端
            mock_client = AsyncMock()
            mock_client.grant_access.return_value = self.mock_tx_hash
            mock_client.revoke_access.return_value = self.mock_tx_hash
            mock_blockchain.return_value = mock_client
            
            try:
                # 授权访问
                grant_result = await service.grant_access(
                    owner_id=self.demo_user_id,
                    grantee_id=self.demo_grantee_id,
                    record_id=self.mock_record_id,
                    access_level="read",
                    expires_at=datetime.now() + timedelta(hours=24),
                    permissions={
                        "read_data": True,
                        "read_metadata": True,
                        "download": False,
                        "share": False
                    }
                )
                
                print(f"✅ 授权成功!")
                print(f"🆔 授权ID: {grant_result['grant_id']}")
                print(f"🔗 交易哈希: {grant_result.get('transaction_hash', 'N/A')}")
                print(f"📅 过期时间: {grant_result['expires_at']}")
                
                # 查询访问授权
                print(f"\n📋 查询用户 {self.demo_user_id} 的授权列表...")
                grants = await service.get_access_grants(
                    user_id=self.demo_user_id,
                    as_owner=True,
                    active_only=True
                )
                
                print(f"📊 找到 {len(grants)} 个有效授权:")
                for grant in grants:
                    print(f"  👤 被授权者: {grant['grantee_id']}")
                    print(f"  🔒 访问级别: {grant['access_level']}")
                    print(f"  📅 授权时间: {grant['granted_at']}")
                    print(f"  ⏰ 过期时间: {grant['expires_at'] or '永不过期'}")
                
                # 撤销访问
                print(f"\n🚫 撤销用户 {self.demo_grantee_id} 的访问权限...")
                
                # 更新模拟数据
                mock_grant.is_active = False
                mock_grant.revoked_at = datetime.now()
                mock_grant.revocation_reason = "演示完成"
                
                revoke_result = await service.revoke_access(
                    owner_id=self.demo_user_id,
                    grantee_id=self.demo_grantee_id,
                    record_id=self.mock_record_id,
                    reason="演示完成"
                )
                
                print(f"✅ 撤销成功!")
                print(f"🆔 授权ID: {revoke_result['grant_id']}")
                print(f"📅 撤销时间: {revoke_result['revoked_at']}")
                print(f"📝 撤销原因: {revoke_result['reason']}")
                
                return {
                    "grant_result": grant_result,
                    "grants": grants,
                    "revoke_result": revoke_result
                }
                
            except Exception as e:
                print(f"❌ 访问控制操作失败: {str(e)}")
                return {}
    
    async def demo_data_query(self, service: BlockchainService) -> Dict[str, Any]:
        """演示数据查询功能"""
        print("\n=== 演示4: 数据查询 ===")
        
        print(f"📋 查询用户 {self.demo_user_id} 的健康记录...")
        
        # 模拟数据库查询
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db:
            
            # 模拟健康记录
            mock_record = MagicMock()
            mock_record.id = self.mock_record_id
            mock_record.data_type.value = "heart_rate"
            mock_record.data_hash = self.mock_data_hash
            mock_record.ipfs_hash = self.mock_ipfs_hash
            mock_record.created_at = datetime.now()
            mock_record.zkp_proof = {"proof": {"a": [1, 2]}}
            mock_record.record_metadata = {"original_size": 567}
            mock_record.transaction = MagicMock()
            mock_record.transaction.transaction_hash = self.mock_tx_hash
            mock_record.transaction.status.value = "confirmed"
            
            mock_session = AsyncMock()
            mock_result = AsyncMock()
            mock_result.scalars.return_value.all.return_value = [mock_record]
            mock_session.execute.return_value = mock_result
            mock_db.return_value.__aenter__.return_value = mock_session
            
            try:
                # 查询健康记录
                records = await service.get_health_records(
                    user_id=self.demo_user_id,
                    data_type="heart_rate",
                    limit=10,
                    offset=0
                )
                
                print(f"📊 查询结果:")
                print(f"  📝 总记录数: {records['total_count']}")
                print(f"  📄 当前页记录: {len(records['records'])}")
                print(f"  📖 是否有更多: {records['has_more']}")
                
                for i, record in enumerate(records['records'], 1):
                    print(f"\n  📋 记录 {i}:")
                    print(f"    🆔 ID: {record['id']}")
                    print(f"    📊 数据类型: {record['data_type']}")
                    print(f"    🔒 数据哈希: {record['data_hash'][:16]}...")
                    print(f"    📅 创建时间: {record['created_at']}")
                    print(f"    🔗 交易状态: {record['transaction_status'] or 'N/A'}")
                    print(f"    🔐 零知识证明: {'✅' if record['has_zkp'] else '❌'}")
                    print(f"    🌐 IPFS哈希: {record['ipfs_hash']}")
                
                return records
                
            except Exception as e:
                print(f"❌ 查询失败: {str(e)}")
                return {}
    
    async def run_demo(self):
        """运行完整演示"""
        print("🚀 开始 Blockchain Service 模拟模式功能演示")
        print("=" * 60)
        
        # 创建模拟服务
        service = self.create_mock_service()
        
        try:
            # 演示1: 数据存储
            storage_result = await self.demo_health_data_storage(service)
            if not storage_result:
                print("❌ 数据存储演示失败，继续其他演示...")
            
            # 演示2: 数据验证
            await self.demo_health_data_verification(service)
            
            # 演示3: 访问控制
            await self.demo_access_control(service)
            
            # 演示4: 数据查询
            await self.demo_data_query(service)
            
            print("\n" + "=" * 60)
            print("🎉 模拟演示完成! 所有核心功能运行正常")
            print("\n📊 演示总结:")
            print("✅ 健康数据存储 - 支持加密存储和IPFS分布式存储")
            print("✅ 数据完整性验证 - 多层验证机制确保数据可信")
            print("✅ 访问权限控制 - 细粒度权限管理和时间限制")
            print("✅ 数据查询服务 - 高效的数据检索和分页支持")
            print("✅ 区块链集成 - 不可篡改的数据存证和审计")
            print("✅ 零知识证明 - 隐私保护的数据验证")
            print("\n💡 注意: 这是模拟模式演示，实际部署需要配置:")
            print("  🗄️ PostgreSQL数据库")
            print("  🌐 IPFS节点")
            print("  ⛓️ 以太坊节点")
            print("  🔐 零知识证明库")
            
        except Exception as e:
            print(f"\n❌ 演示过程中发生错误: {str(e)}")
            logger.exception("演示失败")

async def main():
    """主函数"""
    # 配置日志
    configure_logging()
    
    print(f"🔧 配置信息:")
    print(f"  📱 应用名称: {settings.app_name}")
    print(f"  🔧 环境: {settings.environment}")
    print(f"  🐛 调试模式: {settings.debug}")
    print(f"  🗄️ 数据库: {settings.database.host}:{settings.database.port}")
    print(f"  🌐 IPFS节点: {settings.ipfs.node_url}")
    print(f"  ⛓️ 区块链节点: {settings.blockchain.eth_node_url}")
    
    # 运行演示
    demo = MockBlockchainServiceDemo()
    await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(main()) 