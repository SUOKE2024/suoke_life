"""
健康数据工作流端到端测试

测试从数据收集到区块链存储的完整流程
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import json

from blockchain_service.services.blockchain_client import BlockchainClient
from blockchain_service.services.smart_contract_manager import SmartContractManager
from blockchain_service.services.transaction_manager import TransactionManager
from blockchain_service.services.ipfs_client import IPFSClient
from blockchain_service.services.zkp_service import ZKPService
from blockchain_service.services.encryption_service import EncryptionService
from blockchain_service.models.health_data import HealthData, DataType
from blockchain_service.models.blockchain_models import BlockchainTransaction, TransactionStatus


class TestHealthDataWorkflow:
    """健康数据工作流端到端测试"""
    
    @pytest.mark.asyncio
    async def test_complete_health_data_storage_workflow(self):
        """测试完整的健康数据存储工作流"""
        
        # 模拟所有外部依赖
        with patch('web3.Web3') as mock_web3, \
             patch('ipfshttpclient.connect') as mock_ipfs:
            
            # 设置区块链模拟
            mock_web3_instance = mock_web3.return_value
            mock_web3_instance.is_connected.return_value = True
            mock_web3_instance.eth.chain_id = 1
            mock_web3_instance.eth.get_balance.return_value = 1000000000000000000
            mock_web3_instance.eth.send_raw_transaction.return_value = b'0x' + b'1' * 32
            mock_web3_instance.eth.wait_for_transaction_receipt.return_value = {
                'status': 1,
                'transactionHash': '0x' + '1' * 64,
                'blockNumber': 12345
            }
            
            # 设置IPFS模拟
            mock_ipfs_client = AsyncMock()
            mock_ipfs_client.add.return_value = {'Hash': 'QmHealthData123'}
            mock_ipfs_client.cat.return_value = b'encrypted_health_data'
            mock_ipfs.return_value = mock_ipfs_client
            
            # 设置智能合约模拟
            mock_contract = MagicMock()
            mock_function = MagicMock()
            mock_function.build_transaction.return_value = {
                'to': '0x' + '1' * 40,
                'data': '0x' + '1' * 64,
                'gas': 100000,
                'gasPrice': 20000000000
            }
            mock_contract.functions.storeHealthData.return_value = mock_function
            mock_web3_instance.eth.contract.return_value = mock_contract
            
            # 初始化所有服务
            blockchain_client = BlockchainClient("http://localhost:8545")
            await blockchain_client.initialize()
            
            ipfs_client = IPFSClient("http://localhost:5001")
            await ipfs_client.initialize()
            
            contract_manager = SmartContractManager(mock_web3_instance)
            transaction_manager = TransactionManager(mock_web3_instance)
            zkp_service = ZKPService()
            encryption_service = EncryptionService()
            
            # 步骤1: 创建健康数据
            health_data = {
                'user_id': 'user123',
                'data_type': 'vital_signs',
                'data': {
                    'heart_rate': 72,
                    'blood_pressure': '120/80',
                    'temperature': 36.5,
                    'timestamp': datetime.now().isoformat()
                },
                'metadata': {
                    'device_id': 'device123',
                    'location': 'home'
                }
            }
            
            # 步骤2: 加密健康数据
            encrypted_data = await encryption_service.encrypt(json.dumps(health_data))
            assert encrypted_data is not None
            
            # 步骤3: 生成零知识证明
            zkp_proof = await zkp_service.generate_proof(
                json.dumps(health_data), 
                "user_secret_key"
            )
            assert zkp_proof is not None
            
            # 步骤4: 存储到IPFS
            ipfs_hash = await ipfs_client.store_data(encrypted_data.encode())
            assert ipfs_hash == 'QmHealthData123'
            
            # 步骤5: 部署智能合约（如果需要）
            contract_address = await contract_manager.deploy_contract(
                "HealthDataContract",
                [],  # ABI
                "0x608060405234801561001057600080fd5b50"  # bytecode
            )
            assert contract_address is not None
            
            # 步骤6: 调用智能合约存储数据
            tx_hash = await contract_manager.send_contract_transaction(
                "HealthDataContract",
                "storeHealthData",
                [health_data['user_id'], ipfs_hash, zkp_proof]
            )
            assert tx_hash is not None
            
            # 步骤7: 等待交易确认
            receipt = await transaction_manager.wait_for_confirmation(tx_hash)
            assert receipt['status'] == 1
            
            # 步骤8: 验证数据完整性
            # 从IPFS检索数据
            retrieved_data = await ipfs_client.retrieve_data(ipfs_hash)
            assert retrieved_data is not None
            
            # 解密数据
            decrypted_data = await encryption_service.decrypt(retrieved_data.decode())
            assert json.loads(decrypted_data) == health_data
            
            # 验证零知识证明
            is_valid = await zkp_service.verify_proof(zkp_proof, json.dumps(health_data))
            assert is_valid
            
            print("✅ 健康数据存储工作流测试通过")
            print(f"   - 数据已加密并存储到IPFS: {ipfs_hash}")
            print(f"   - 交易已确认: {tx_hash}")
            print(f"   - 零知识证明验证通过")
    
    @pytest.mark.asyncio
    async def test_health_data_retrieval_workflow(self):
        """测试健康数据检索工作流"""
        
        with patch('web3.Web3') as mock_web3, \
             patch('ipfshttpclient.connect') as mock_ipfs:
            
            # 设置模拟
            mock_web3_instance = mock_web3.return_value
            mock_web3_instance.is_connected.return_value = True
            mock_web3_instance.eth.chain_id = 1
            
            # 模拟智能合约查询
            mock_contract = MagicMock()
            mock_function = MagicMock()
            mock_function.call.return_value = ['QmHealthData123', 'zkp_proof_data']
            mock_contract.functions.getHealthData.return_value = mock_function
            mock_web3_instance.eth.contract.return_value = mock_contract
            
            # 模拟IPFS检索
            mock_ipfs_client = AsyncMock()
            test_data = json.dumps({
                'user_id': 'user123',
                'data_type': 'vital_signs',
                'data': {'heart_rate': 72}
            })
            encrypted_test_data = "encrypted_" + test_data
            mock_ipfs_client.cat.return_value = encrypted_test_data.encode()
            mock_ipfs.return_value = mock_ipfs_client
            
            # 初始化服务
            blockchain_client = BlockchainClient("http://localhost:8545")
            await blockchain_client.initialize()
            
            ipfs_client = IPFSClient("http://localhost:5001")
            await ipfs_client.initialize()
            
            contract_manager = SmartContractManager(mock_web3_instance)
            encryption_service = EncryptionService()
            zkp_service = ZKPService()
            
            # 步骤1: 从智能合约查询数据位置
            contract_manager.contracts["HealthDataContract"] = mock_contract
            result = await contract_manager.call_contract_function(
                "HealthDataContract",
                "getHealthData",
                ["user123"]
            )
            ipfs_hash, zkp_proof = result
            assert ipfs_hash == 'QmHealthData123'
            
            # 步骤2: 从IPFS检索加密数据
            encrypted_data = await ipfs_client.retrieve_data(ipfs_hash)
            assert encrypted_data is not None
            
            # 步骤3: 解密数据
            decrypted_data = await encryption_service.decrypt(encrypted_data.decode())
            health_data = json.loads(decrypted_data)
            assert health_data['user_id'] == 'user123'
            
            # 步骤4: 验证零知识证明
            is_valid = await zkp_service.verify_proof(zkp_proof, json.dumps(health_data))
            assert is_valid
            
            print("✅ 健康数据检索工作流测试通过")
            print(f"   - 成功从IPFS检索数据: {ipfs_hash}")
            print(f"   - 数据解密成功")
            print(f"   - 零知识证明验证通过")
    
    @pytest.mark.asyncio
    async def test_multi_user_data_sharing_workflow(self):
        """测试多用户数据共享工作流"""
        
        with patch('web3.Web3') as mock_web3, \
             patch('ipfshttpclient.connect') as mock_ipfs:
            
            # 设置模拟
            mock_web3_instance = mock_web3.return_value
            mock_web3_instance.is_connected.return_value = True
            mock_web3_instance.eth.chain_id = 1
            mock_web3_instance.eth.send_raw_transaction.return_value = b'0x' + b'1' * 32
            mock_web3_instance.eth.wait_for_transaction_receipt.return_value = {
                'status': 1,
                'transactionHash': '0x' + '1' * 64
            }
            
            mock_ipfs_client = AsyncMock()
            mock_ipfs_client.add.return_value = {'Hash': 'QmSharedData123'}
            mock_ipfs.return_value = mock_ipfs_client
            
            # 模拟智能合约
            mock_contract = MagicMock()
            mock_function = MagicMock()
            mock_function.build_transaction.return_value = {
                'to': '0x' + '1' * 40,
                'data': '0x' + '1' * 64,
                'gas': 100000,
                'gasPrice': 20000000000
            }
            mock_contract.functions.shareData.return_value = mock_function
            mock_web3_instance.eth.contract.return_value = mock_contract
            
            # 初始化服务
            blockchain_client = BlockchainClient("http://localhost:8545")
            await blockchain_client.initialize()
            
            ipfs_client = IPFSClient("http://localhost:5001")
            await ipfs_client.initialize()
            
            contract_manager = SmartContractManager(mock_web3_instance)
            transaction_manager = TransactionManager(mock_web3_instance)
            encryption_service = EncryptionService()
            zkp_service = ZKPService()
            
            # 模拟多个用户的健康数据
            users_data = [
                {
                    'user_id': f'user{i}',
                    'data': {
                        'heart_rate': 70 + i,
                        'steps': 8000 + i * 100,
                        'timestamp': datetime.now().isoformat()
                    }
                }
                for i in range(3)
            ]
            
            # 步骤1: 为每个用户加密和存储数据
            shared_data_hashes = []
            for user_data in users_data:
                # 加密数据
                encrypted_data = await encryption_service.encrypt(json.dumps(user_data))
                
                # 存储到IPFS
                ipfs_hash = await ipfs_client.store_data(encrypted_data.encode())
                shared_data_hashes.append(ipfs_hash)
                
                # 生成零知识证明
                zkp_proof = await zkp_service.generate_proof(
                    json.dumps(user_data), 
                    f"secret_key_{user_data['user_id']}"
                )
                
                # 记录到区块链
                contract_manager.contracts["HealthDataContract"] = mock_contract
                tx_hash = await contract_manager.send_contract_transaction(
                    "HealthDataContract",
                    "shareData",
                    [user_data['user_id'], ipfs_hash, zkp_proof]
                )
                
                # 等待确认
                receipt = await transaction_manager.wait_for_confirmation(tx_hash)
                assert receipt['status'] == 1
            
            # 步骤2: 验证所有数据都已正确存储
            assert len(shared_data_hashes) == 3
            for i, ipfs_hash in enumerate(shared_data_hashes):
                # 检索数据
                retrieved_data = await ipfs_client.retrieve_data(ipfs_hash)
                decrypted_data = await encryption_service.decrypt(retrieved_data.decode())
                user_data = json.loads(decrypted_data)
                
                # 验证数据正确性
                assert user_data['user_id'] == f'user{i}'
                assert user_data['data']['heart_rate'] == 70 + i
            
            print("✅ 多用户数据共享工作流测试通过")
            print(f"   - 成功处理 {len(users_data)} 个用户的数据")
            print(f"   - 所有数据已加密存储到IPFS")
            print(f"   - 所有交易已确认")
    
    @pytest.mark.asyncio
    async def test_error_handling_workflow(self):
        """测试错误处理工作流"""
        
        with patch('web3.Web3') as mock_web3, \
             patch('ipfshttpclient.connect') as mock_ipfs:
            
            # 设置失败的模拟
            mock_web3_instance = mock_web3.return_value
            mock_web3_instance.is_connected.return_value = False  # 连接失败
            
            mock_ipfs_client = AsyncMock()
            mock_ipfs_client.add.side_effect = Exception("IPFS connection failed")
            mock_ipfs.return_value = mock_ipfs_client
            
            # 测试区块链连接失败
            blockchain_client = BlockchainClient("http://localhost:8545")
            with pytest.raises(Exception):
                await blockchain_client.initialize()
            
            # 测试IPFS连接失败
            ipfs_client = IPFSClient("http://localhost:5001")
            await ipfs_client.initialize()  # 初始化成功
            
            with pytest.raises(Exception):
                await ipfs_client.store_data(b"test data")
            
            print("✅ 错误处理工作流测试通过")
            print("   - 正确处理区块链连接失败")
            print("   - 正确处理IPFS存储失败")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])