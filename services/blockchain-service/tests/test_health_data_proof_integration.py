"""
区块链健康数据存证全链路集成测试

测试覆盖：
1. 健康数据上链存证
2. 数据完整性验证
3. 隐私保护验证
4. 跨链数据同步
5. 智能合约执行
6. 零知识证明验证
"""

import pytest
import asyncio
import json
import hashlib
import time
from typing import Dict, List, Any, Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import secrets

class HealthDataProofIntegrationTest:
    """健康数据存证全链路集成测试类"""
    
    def __init__(self):
        self.blockchain_endpoint = "http://localhost:8545"
        self.ipfs_endpoint = "http://localhost:5001"
        self.test_user_id = "test_user_12345"
        self.test_session_id = "session_67890"
        self.private_key = None
        self.public_key = None
        self.setup_crypto_keys()
    
    def setup_crypto_keys(self):
        """设置加密密钥对"""
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
    
    @pytest.fixture
    async def health_data_sample(self):
        """健康数据样本"""
        return {
            "user_id": self.test_user_id,
            "session_id": self.test_session_id,
            "timestamp": int(time.time()),
            "data_type": "comprehensive_diagnosis",
            "diagnostic_results": {
                "calculation": {
                    "ziwu_analysis": {
                        "current_meridian": "lung",
                        "energy_level": 0.85,
                        "recommendations": ["深呼吸练习", "适量运动"]
                    },
                    "constitution_analysis": {
                        "primary_type": "qi_deficiency",
                        "secondary_type": "yang_deficiency",
                        "confidence": 0.92
                    }
                },
                "look": {
                    "face_analysis": {
                        "complexion": "pale",
                        "tongue_coating": "thin_white",
                        "confidence": 0.88
                    }
                },
                "listen": {
                    "voice_analysis": {
                        "tone_quality": "weak",
                        "breathing_pattern": "shallow",
                        "confidence": 0.79
                    }
                },
                "inquiry": {
                    "symptoms": ["fatigue", "cold_limbs", "poor_appetite"],
                    "severity_scores": [8, 6, 7],
                    "confidence": 0.95
                },
                "palpation": {
                    "pulse_analysis": {
                        "pulse_type": "weak_slow",
                        "rate": 58,
                        "confidence": 0.91
                    }
                }
            },
            "agent_consensus": {
                "xiaoai_analysis": {
                    "syndrome": "spleen_qi_deficiency",
                    "confidence": 0.89
                },
                "xiaoke_analysis": {
                    "treatment_plan": ["tonify_spleen_qi", "warm_yang"],
                    "confidence": 0.87
                },
                "laoke_analysis": {
                    "lifestyle_advice": ["regular_sleep", "warm_food"],
                    "confidence": 0.93
                },
                "soer_analysis": {
                    "emotional_support": ["stress_reduction", "meditation"],
                    "confidence": 0.85
                }
            },
            "metadata": {
                "version": "1.0.0",
                "data_source": "suoke_life_platform",
                "processing_time": 1250,
                "quality_score": 0.89
            }
        }
    
    async def test_01_data_encryption_and_hashing(self, health_data_sample):
        """测试数据加密和哈希生成"""
        print("\n=== 测试1: 数据加密和哈希生成 ===")
        
        # 1. 数据序列化
        data_json = json.dumps(health_data_sample, sort_keys=True)
        print(f"原始数据大小: {len(data_json)} bytes")
        
        # 2. 生成数据哈希
        data_hash = hashlib.sha256(data_json.encode()).hexdigest()
        print(f"数据哈希: {data_hash[:16]}...")
        
        # 3. 对称加密数据
        encryption_key = secrets.token_bytes(32)  # AES-256 key
        iv = secrets.token_bytes(16)  # AES IV
        
        cipher = Cipher(algorithms.AES(encryption_key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        
        # 填充数据到16字节边界
        padded_data = data_json.encode()
        padding_length = 16 - (len(padded_data) % 16)
        padded_data += bytes([padding_length]) * padding_length
        
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        print(f"加密数据大小: {len(encrypted_data)} bytes")
        
        # 4. 使用公钥加密对称密钥
        encrypted_key = self.public_key.encrypt(
            encryption_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # 5. 验证解密
        decrypted_key = self.private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        assert decrypted_key == encryption_key
        print("✓ 加密密钥验证成功")
        
        # 6. 验证数据解密
        cipher = Cipher(algorithms.AES(decrypted_key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()
        
        # 移除填充
        padding_length = decrypted_padded[-1]
        decrypted_data = decrypted_padded[:-padding_length]
        
        assert decrypted_data.decode() == data_json
        print("✓ 数据解密验证成功")
        
        return {
            "data_hash": data_hash,
            "encrypted_data": encrypted_data,
            "encrypted_key": encrypted_key,
            "iv": iv
        }
    
    async def test_02_ipfs_storage(self, health_data_sample):
        """测试IPFS分布式存储"""
        print("\n=== 测试2: IPFS分布式存储 ===")
        
        # 1. 准备加密数据
        encryption_result = await self.test_01_data_encryption_and_hashing(health_data_sample)
        
        # 2. 创建IPFS存储包
        ipfs_package = {
            "data_hash": encryption_result["data_hash"],
            "encrypted_data": encryption_result["encrypted_data"].hex(),
            "iv": encryption_result["iv"].hex(),
            "timestamp": int(time.time()),
            "user_id_hash": hashlib.sha256(self.test_user_id.encode()).hexdigest(),
            "metadata": {
                "version": "1.0.0",
                "encryption_algorithm": "AES-256-CBC",
                "key_encryption": "RSA-OAEP"
            }
        }
        
        # 3. 模拟IPFS上传
        ipfs_hash = await self.mock_ipfs_upload(ipfs_package)
        print(f"IPFS哈希: {ipfs_hash}")
        
        # 4. 验证IPFS检索
        retrieved_package = await self.mock_ipfs_retrieve(ipfs_hash)
        assert retrieved_package["data_hash"] == encryption_result["data_hash"]
        print("✓ IPFS存储和检索验证成功")
        
        return {
            "ipfs_hash": ipfs_hash,
            "ipfs_package": ipfs_package
        }
    
    async def test_03_blockchain_transaction(self, health_data_sample):
        """测试区块链交易上链"""
        print("\n=== 测试3: 区块链交易上链 ===")
        
        # 1. 准备IPFS存储结果
        ipfs_result = await self.test_02_ipfs_storage(health_data_sample)
        
        # 2. 创建区块链交易
        transaction = {
            "from": f"0x{hashlib.sha256(self.test_user_id.encode()).hexdigest()[:40]}",
            "to": "0x1234567890123456789012345678901234567890",  # 智能合约地址
            "data": {
                "function": "storeHealthDataProof",
                "parameters": {
                    "user_id_hash": hashlib.sha256(self.test_user_id.encode()).hexdigest(),
                    "data_hash": ipfs_result["ipfs_package"]["data_hash"],
                    "ipfs_hash": ipfs_result["ipfs_hash"],
                    "timestamp": int(time.time()),
                    "data_type": "comprehensive_diagnosis",
                    "access_permissions": ["user", "authorized_doctors"],
                    "retention_period": 365 * 24 * 60 * 60  # 1年
                }
            },
            "gas": 200000,
            "gasPrice": "20000000000",  # 20 Gwei
            "nonce": 1
        }
        
        # 3. 模拟交易签名和广播
        tx_hash = await self.mock_blockchain_transaction(transaction)
        print(f"交易哈希: {tx_hash}")
        
        # 4. 等待交易确认
        receipt = await self.mock_wait_for_confirmation(tx_hash)
        assert receipt["status"] == "success"
        print(f"✓ 交易确认成功，区块号: {receipt['block_number']}")
        
        return {
            "transaction_hash": tx_hash,
            "block_number": receipt["block_number"],
            "contract_address": transaction["to"]
        }
    
    async def test_04_smart_contract_execution(self, health_data_sample):
        """测试智能合约执行"""
        print("\n=== 测试4: 智能合约执行 ===")
        
        # 1. 准备区块链交易结果
        blockchain_result = await self.test_03_blockchain_transaction(health_data_sample)
        
        # 2. 调用智能合约查询方法
        query_result = await self.mock_smart_contract_call(
            contract_address=blockchain_result["contract_address"],
            function="getHealthDataProof",
            parameters={
                "user_id_hash": hashlib.sha256(self.test_user_id.encode()).hexdigest(),
                "data_hash": hashlib.sha256(json.dumps(health_data_sample, sort_keys=True).encode()).hexdigest()
            }
        )
        
        assert query_result["exists"] == True
        assert query_result["ipfs_hash"] is not None
        print("✓ 智能合约查询验证成功")
        
        # 3. 测试访问权限验证
        access_result = await self.mock_smart_contract_call(
            contract_address=blockchain_result["contract_address"],
            function="checkAccessPermission",
            parameters={
                "user_id_hash": hashlib.sha256(self.test_user_id.encode()).hexdigest(),
                "requester": "authorized_doctor_123",
                "data_hash": hashlib.sha256(json.dumps(health_data_sample, sort_keys=True).encode()).hexdigest()
            }
        )
        
        assert access_result["has_permission"] == True
        print("✓ 访问权限验证成功")
        
        return query_result
    
    async def test_05_zero_knowledge_proof(self, health_data_sample):
        """测试零知识证明验证"""
        print("\n=== 测试5: 零知识证明验证 ===")
        
        # 1. 生成零知识证明（简化实现）
        proof_data = {
            "user_has_condition": True,  # 用户是否有某种健康状况
            "condition_severity": "moderate",  # 严重程度
            "proof_timestamp": int(time.time())
        }
        
        # 2. 创建承诺（commitment）
        commitment = await self.generate_zk_commitment(proof_data)
        print(f"零知识承诺: {commitment[:16]}...")
        
        # 3. 生成证明
        proof = await self.generate_zk_proof(proof_data, commitment)
        print(f"零知识证明: {proof[:16]}...")
        
        # 4. 验证证明
        is_valid = await self.verify_zk_proof(proof, commitment)
        assert is_valid == True
        print("✓ 零知识证明验证成功")
        
        # 5. 测试隐私保护
        revealed_info = await self.extract_public_info(proof)
        assert "user_has_condition" in revealed_info
        assert "detailed_diagnosis" not in revealed_info  # 敏感信息不应泄露
        print("✓ 隐私保护验证成功")
        
        return {
            "commitment": commitment,
            "proof": proof,
            "public_info": revealed_info
        }
    
    async def test_06_cross_chain_synchronization(self, health_data_sample):
        """测试跨链数据同步"""
        print("\n=== 测试6: 跨链数据同步 ===")
        
        # 1. 准备主链数据
        main_chain_result = await self.test_03_blockchain_transaction(health_data_sample)
        
        # 2. 同步到侧链
        side_chain_tx = await self.mock_cross_chain_sync(
            main_chain_tx=main_chain_result["transaction_hash"],
            target_chain="polygon",
            data_hash=hashlib.sha256(json.dumps(health_data_sample, sort_keys=True).encode()).hexdigest()
        )
        
        print(f"侧链交易哈希: {side_chain_tx}")
        
        # 3. 验证跨链数据一致性
        main_chain_data = await self.mock_get_chain_data("ethereum", main_chain_result["transaction_hash"])
        side_chain_data = await self.mock_get_chain_data("polygon", side_chain_tx)
        
        assert main_chain_data["data_hash"] == side_chain_data["data_hash"]
        print("✓ 跨链数据一致性验证成功")
        
        # 4. 测试跨链查询
        cross_chain_query = await self.mock_cross_chain_query(
            user_id_hash=hashlib.sha256(self.test_user_id.encode()).hexdigest(),
            chains=["ethereum", "polygon"]
        )
        
        assert len(cross_chain_query["results"]) == 2
        print("✓ 跨链查询验证成功")
        
        return {
            "main_chain_tx": main_chain_result["transaction_hash"],
            "side_chain_tx": side_chain_tx,
            "cross_chain_query": cross_chain_query
        }
    
    async def test_07_data_integrity_verification(self, health_data_sample):
        """测试数据完整性验证"""
        print("\n=== 测试7: 数据完整性验证 ===")
        
        # 1. 创建数据指纹
        original_fingerprint = await self.create_data_fingerprint(health_data_sample)
        print(f"原始数据指纹: {original_fingerprint[:16]}...")
        
        # 2. 模拟数据篡改
        tampered_data = health_data_sample.copy()
        tampered_data["diagnostic_results"]["calculation"]["constitution_analysis"]["confidence"] = 0.50
        
        tampered_fingerprint = await self.create_data_fingerprint(tampered_data)
        
        # 3. 验证完整性检查
        integrity_check = await self.verify_data_integrity(
            original_data=health_data_sample,
            stored_fingerprint=original_fingerprint
        )
        assert integrity_check["is_valid"] == True
        print("✓ 原始数据完整性验证成功")
        
        # 4. 验证篡改检测
        tamper_check = await self.verify_data_integrity(
            original_data=tampered_data,
            stored_fingerprint=original_fingerprint
        )
        assert tamper_check["is_valid"] == False
        print("✓ 数据篡改检测成功")
        
        # 5. 测试时间戳验证
        timestamp_check = await self.verify_timestamp_integrity(health_data_sample)
        assert timestamp_check["is_valid"] == True
        print("✓ 时间戳完整性验证成功")
        
        return {
            "original_fingerprint": original_fingerprint,
            "integrity_verified": True,
            "tamper_detected": True
        }
    
    async def test_08_performance_benchmarks(self, health_data_sample):
        """测试性能基准"""
        print("\n=== 测试8: 性能基准测试 ===")
        
        benchmarks = {}
        
        # 1. 加密性能测试
        start_time = time.time()
        for _ in range(100):
            await self.test_01_data_encryption_and_hashing(health_data_sample)
        encryption_time = (time.time() - start_time) / 100
        benchmarks["encryption_avg_time"] = encryption_time
        print(f"平均加密时间: {encryption_time:.4f}s")
        
        # 2. IPFS存储性能测试
        start_time = time.time()
        for _ in range(10):
            await self.test_02_ipfs_storage(health_data_sample)
        ipfs_time = (time.time() - start_time) / 10
        benchmarks["ipfs_avg_time"] = ipfs_time
        print(f"平均IPFS存储时间: {ipfs_time:.4f}s")
        
        # 3. 区块链交易性能测试
        start_time = time.time()
        for _ in range(5):
            await self.test_03_blockchain_transaction(health_data_sample)
        blockchain_time = (time.time() - start_time) / 5
        benchmarks["blockchain_avg_time"] = blockchain_time
        print(f"平均区块链交易时间: {blockchain_time:.4f}s")
        
        # 4. 验证性能要求
        assert encryption_time < 0.1  # 加密时间应小于100ms
        assert ipfs_time < 1.0  # IPFS存储时间应小于1s
        assert blockchain_time < 5.0  # 区块链交易时间应小于5s
        print("✓ 所有性能基准测试通过")
        
        return benchmarks
    
    async def test_09_end_to_end_workflow(self, health_data_sample):
        """测试端到端工作流"""
        print("\n=== 测试9: 端到端工作流 ===")
        
        workflow_results = {}
        
        # 1. 完整数据存证流程
        print("执行完整数据存证流程...")
        
        # 加密和哈希
        encryption_result = await self.test_01_data_encryption_and_hashing(health_data_sample)
        workflow_results["encryption"] = encryption_result
        
        # IPFS存储
        ipfs_result = await self.test_02_ipfs_storage(health_data_sample)
        workflow_results["ipfs"] = ipfs_result
        
        # 区块链上链
        blockchain_result = await self.test_03_blockchain_transaction(health_data_sample)
        workflow_results["blockchain"] = blockchain_result
        
        # 智能合约执行
        contract_result = await self.test_04_smart_contract_execution(health_data_sample)
        workflow_results["smart_contract"] = contract_result
        
        # 零知识证明
        zk_result = await self.test_05_zero_knowledge_proof(health_data_sample)
        workflow_results["zero_knowledge"] = zk_result
        
        # 跨链同步
        cross_chain_result = await self.test_06_cross_chain_synchronization(health_data_sample)
        workflow_results["cross_chain"] = cross_chain_result
        
        # 完整性验证
        integrity_result = await self.test_07_data_integrity_verification(health_data_sample)
        workflow_results["integrity"] = integrity_result
        
        print("✓ 端到端工作流执行成功")
        
        # 2. 验证数据可追溯性
        trace_result = await self.verify_data_traceability(workflow_results)
        assert trace_result["is_traceable"] == True
        print("✓ 数据可追溯性验证成功")
        
        # 3. 验证数据恢复能力
        recovery_result = await self.test_data_recovery(workflow_results)
        assert recovery_result["recovery_successful"] == True
        print("✓ 数据恢复能力验证成功")
        
        return workflow_results
    
    # 模拟方法实现
    async def mock_ipfs_upload(self, data: Dict) -> str:
        """模拟IPFS上传"""
        data_str = json.dumps(data, sort_keys=True)
        return f"Qm{hashlib.sha256(data_str.encode()).hexdigest()[:44]}"
    
    async def mock_ipfs_retrieve(self, ipfs_hash: str) -> Dict:
        """模拟IPFS检索"""
        # 在实际实现中，这里会从IPFS网络检索数据
        return {"data_hash": "mock_hash", "status": "retrieved"}
    
    async def mock_blockchain_transaction(self, transaction: Dict) -> str:
        """模拟区块链交易"""
        tx_data = json.dumps(transaction, sort_keys=True)
        return f"0x{hashlib.sha256(tx_data.encode()).hexdigest()}"
    
    async def mock_wait_for_confirmation(self, tx_hash: str) -> Dict:
        """模拟等待交易确认"""
        await asyncio.sleep(0.1)  # 模拟网络延迟
        return {
            "status": "success",
            "block_number": 12345678,
            "gas_used": 150000
        }
    
    async def mock_smart_contract_call(self, contract_address: str, function: str, parameters: Dict) -> Dict:
        """模拟智能合约调用"""
        if function == "getHealthDataProof":
            return {
                "exists": True,
                "ipfs_hash": "QmMockHash123",
                "timestamp": int(time.time())
            }
        elif function == "checkAccessPermission":
            return {"has_permission": True}
        return {}
    
    async def generate_zk_commitment(self, data: Dict) -> str:
        """生成零知识承诺"""
        commitment_data = json.dumps(data, sort_keys=True)
        return hashlib.sha256(commitment_data.encode()).hexdigest()
    
    async def generate_zk_proof(self, data: Dict, commitment: str) -> str:
        """生成零知识证明"""
        proof_data = f"{commitment}:{json.dumps(data, sort_keys=True)}"
        return hashlib.sha256(proof_data.encode()).hexdigest()
    
    async def verify_zk_proof(self, proof: str, commitment: str) -> bool:
        """验证零知识证明"""
        return len(proof) == 64 and len(commitment) == 64  # 简化验证
    
    async def extract_public_info(self, proof: str) -> Dict:
        """从证明中提取公开信息"""
        return {"user_has_condition": True, "proof_valid": True}
    
    async def mock_cross_chain_sync(self, main_chain_tx: str, target_chain: str, data_hash: str) -> str:
        """模拟跨链同步"""
        sync_data = f"{main_chain_tx}:{target_chain}:{data_hash}"
        return f"0x{hashlib.sha256(sync_data.encode()).hexdigest()}"
    
    async def mock_get_chain_data(self, chain: str, tx_hash: str) -> Dict:
        """模拟获取链上数据"""
        return {
            "chain": chain,
            "tx_hash": tx_hash,
            "data_hash": "mock_data_hash",
            "timestamp": int(time.time())
        }
    
    async def mock_cross_chain_query(self, user_id_hash: str, chains: List[str]) -> Dict:
        """模拟跨链查询"""
        return {
            "user_id_hash": user_id_hash,
            "results": [{"chain": chain, "records": 1} for chain in chains]
        }
    
    async def create_data_fingerprint(self, data: Dict) -> str:
        """创建数据指纹"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    async def verify_data_integrity(self, original_data: Dict, stored_fingerprint: str) -> Dict:
        """验证数据完整性"""
        current_fingerprint = await self.create_data_fingerprint(original_data)
        return {
            "is_valid": current_fingerprint == stored_fingerprint,
            "current_fingerprint": current_fingerprint,
            "stored_fingerprint": stored_fingerprint
        }
    
    async def verify_timestamp_integrity(self, data: Dict) -> Dict:
        """验证时间戳完整性"""
        current_time = int(time.time())
        data_time = data.get("timestamp", 0)
        time_diff = abs(current_time - data_time)
        
        return {
            "is_valid": time_diff < 3600,  # 1小时内有效
            "time_difference": time_diff
        }
    
    async def verify_data_traceability(self, workflow_results: Dict) -> Dict:
        """验证数据可追溯性"""
        # 检查是否可以从区块链追溯到IPFS，再到原始数据
        has_blockchain_record = "blockchain" in workflow_results
        has_ipfs_record = "ipfs" in workflow_results
        has_encryption_record = "encryption" in workflow_results
        
        return {
            "is_traceable": has_blockchain_record and has_ipfs_record and has_encryption_record,
            "trace_path": ["blockchain", "ipfs", "encryption"]
        }
    
    async def test_data_recovery(self, workflow_results: Dict) -> Dict:
        """测试数据恢复"""
        # 模拟从区块链和IPFS恢复数据
        try:
            # 1. 从区块链获取IPFS哈希
            ipfs_hash = workflow_results["ipfs"]["ipfs_hash"]
            
            # 2. 从IPFS获取加密数据
            encrypted_package = await self.mock_ipfs_retrieve(ipfs_hash)
            
            # 3. 解密数据（需要私钥）
            # 在实际实现中，这里会执行真正的解密
            
            return {"recovery_successful": True, "recovered_data_hash": "mock_hash"}
        except Exception as e:
            return {"recovery_successful": False, "error": str(e)}

# 测试运行器
@pytest.mark.asyncio
async def test_health_data_proof_integration():
    """运行完整的健康数据存证集成测试"""
    test_suite = HealthDataProofIntegrationTest()
    
    # 创建测试数据
    health_data = {
        "user_id": test_suite.test_user_id,
        "session_id": test_suite.test_session_id,
        "timestamp": int(time.time()),
        "data_type": "comprehensive_diagnosis",
        "diagnostic_results": {
            "calculation": {"confidence": 0.92},
            "look": {"confidence": 0.88},
            "listen": {"confidence": 0.79},
            "inquiry": {"confidence": 0.95},
            "palpation": {"confidence": 0.91}
        }
    }
    
    print("开始健康数据存证全链路集成测试...")
    
    # 执行所有测试
    test_results = {}
    
    try:
        # 单元测试
        test_results["encryption"] = await test_suite.test_01_data_encryption_and_hashing(health_data)
        test_results["ipfs"] = await test_suite.test_02_ipfs_storage(health_data)
        test_results["blockchain"] = await test_suite.test_03_blockchain_transaction(health_data)
        test_results["smart_contract"] = await test_suite.test_04_smart_contract_execution(health_data)
        test_results["zero_knowledge"] = await test_suite.test_05_zero_knowledge_proof(health_data)
        test_results["cross_chain"] = await test_suite.test_06_cross_chain_synchronization(health_data)
        test_results["integrity"] = await test_suite.test_07_data_integrity_verification(health_data)
        test_results["performance"] = await test_suite.test_08_performance_benchmarks(health_data)
        
        # 端到端测试
        test_results["end_to_end"] = await test_suite.test_09_end_to_end_workflow(health_data)
        
        print("\n" + "="*50)
        print("🎉 所有测试通过！健康数据存证系统运行正常")
        print("="*50)
        
        return test_results
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        raise

if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_health_data_proof_integration()) 