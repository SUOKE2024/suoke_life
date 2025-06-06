"""
test_zk_integration - 索克生活项目模块
"""

from suoke_blockchain_service.exceptions import ZKProofError
from suoke_blockchain_service.zk_integration import ZKProofGenerator, ZKProofVerifier
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

"""
零知识证明集成测试模块

测试零知识证明生成和验证功能。
"""




class TestZKProofGenerator:
    """零知识证明生成器测试类"""

    @pytest.fixture
    def zk_generator(self):
        """创建ZK证明生成器实例"""
        return ZKProofGenerator()

    @pytest.mark.asyncio
    async def test_generate_proof_success(self, zk_generator):
        """测试成功生成证明"""
        test_data = {"user_id": "test123", "heart_rate": 72}
        circuit_name = "health_data_heart_rate"
        
        with patch('suoke_blockchain_service.zk_integration.subprocess.run') as mock_run:
            # Mock成功的证明生成
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = '{"proof": {"a": [1, 2]}, "public_inputs": [1, 2, 3]}'
            
            result = await zk_generator.generate_proof(test_data, circuit_name)
            
            assert "proof" in result
            assert "public_inputs" in result
            assert result["proof"]["a"] == [1, 2]

    @pytest.mark.asyncio
    async def test_generate_proof_failure(self, zk_generator):
        """测试证明生成失败"""
        test_data = {"user_id": "test123", "heart_rate": 72}
        circuit_name = "invalid_circuit"
        
        with patch('suoke_blockchain_service.zk_integration.subprocess.run') as mock_run:
            # Mock失败的证明生成
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = "Circuit not found"
            
            with pytest.raises(ZKProofError, match="零知识证明生成失败"):
                await zk_generator.generate_proof(test_data, circuit_name)

    @pytest.mark.asyncio
    async def test_prepare_witness_data(self, zk_generator):
        """测试准备见证数据"""
        test_data = {
            "user_id": "test123",
            "heart_rate": 72,
            "timestamp": 1234567890
        }
        
        result = zk_generator._prepare_witness_data(test_data)
        
        assert isinstance(result, dict)
        assert "user_id_hash" in result
        assert "heart_rate" in result
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_validate_circuit_name(self, zk_generator):
        """测试电路名称验证"""
        # 有效的电路名称
        valid_circuits = [
            "health_data_heart_rate",
            "health_data_blood_pressure",
            "health_data_temperature"
        ]
        
        for circuit in valid_circuits:
            assert zk_generator._validate_circuit_name(circuit) is True
        
        # 无效的电路名称
        invalid_circuits = [
            "",
            "invalid_circuit",
            "health_data_unknown",
            None
        ]
        
        for circuit in invalid_circuits:
            assert zk_generator._validate_circuit_name(circuit) is False

    @pytest.mark.asyncio
    async def test_generate_proof_with_large_data(self, zk_generator):
        """测试大数据证明生成"""
        large_data = {
            "user_id": "test123",
            "measurements": ["x"] * 1000,  # 大量测量数据
            "metadata": {"device": "test", "version": "1.0"}
        }
        circuit_name = "health_data_heart_rate"
        
        with patch('suoke_blockchain_service.zk_integration.subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = '{"proof": {"a": [1, 2]}, "public_inputs": [1, 2, 3]}'
            
            result = await zk_generator.generate_proof(large_data, circuit_name)
            
            assert "proof" in result
            assert "public_inputs" in result


class TestZKProofVerifier:
    """零知识证明验证器测试类"""

    @pytest.fixture
    def zk_verifier(self):
        """创建ZK证明验证器实例"""
        return ZKProofVerifier()

    @pytest.mark.asyncio
    async def test_verify_proof_success(self, zk_verifier):
        """测试成功验证证明"""
        proof = {"a": [1, 2], "b": [3, 4], "c": [5, 6]}
        public_inputs = [1, 2, 3]
        verification_key = {"alpha": [1, 2], "beta": [3, 4]}
        circuit_name = "health_data_heart_rate"
        
        with patch('suoke_blockchain_service.zk_integration.subprocess.run') as mock_run:
            # Mock成功的证明验证
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "true"
            
            result = await zk_verifier.verify_proof(
                proof, public_inputs, verification_key, circuit_name
            )
            
            assert result is True

    @pytest.mark.asyncio
    async def test_verify_proof_failure(self, zk_verifier):
        """测试证明验证失败"""
        proof = {"a": [1, 2], "b": [3, 4], "c": [5, 6]}
        public_inputs = [1, 2, 3]
        verification_key = {"alpha": [1, 2], "beta": [3, 4]}
        circuit_name = "health_data_heart_rate"
        
        with patch('suoke_blockchain_service.zk_integration.subprocess.run') as mock_run:
            # Mock失败的证明验证
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "false"
            
            result = await zk_verifier.verify_proof(
                proof, public_inputs, verification_key, circuit_name
            )
            
            assert result is False

    @pytest.mark.asyncio
    async def test_verify_proof_error(self, zk_verifier):
        """测试证明验证错误"""
        proof = {"a": [1, 2]}
        public_inputs = [1, 2, 3]
        verification_key = {"alpha": [1, 2]}
        circuit_name = "invalid_circuit"
        
        with patch('suoke_blockchain_service.zk_integration.subprocess.run') as mock_run:
            # Mock验证过程错误
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = "Verification failed"
            
            with pytest.raises(ZKProofError, match="零知识证明验证失败"):
                await zk_verifier.verify_proof(
                    proof, public_inputs, verification_key, circuit_name
                )

    @pytest.mark.asyncio
    async def test_validate_proof_format(self, zk_verifier):
        """测试证明格式验证"""
        # 有效的证明格式
        valid_proof = {"a": [1, 2], "b": [3, 4], "c": [5, 6]}
        assert zk_verifier._validate_proof_format(valid_proof) is True
        
        # 无效的证明格式
        invalid_proofs = [
            {},
            {"a": [1, 2]},  # 缺少字段
            {"a": [1, 2], "b": [3, 4], "c": "invalid"},  # 错误类型
            None
        ]
        
        for invalid_proof in invalid_proofs:
            assert zk_verifier._validate_proof_format(invalid_proof) is False

    @pytest.mark.asyncio
    async def test_validate_public_inputs(self, zk_verifier):
        """测试公共输入验证"""
        # 有效的公共输入
        valid_inputs = [1, 2, 3, 4, 5]
        assert zk_verifier._validate_public_inputs(valid_inputs) is True
        
        # 无效的公共输入
        invalid_inputs = [
            [],
            None,
            [1, 2, "invalid"],  # 包含非数字
            ["a", "b", "c"]  # 全部非数字
        ]
        
        for invalid_input in invalid_inputs:
            assert zk_verifier._validate_public_inputs(invalid_input) is False

    @pytest.mark.asyncio
    async def test_batch_verify_proofs(self, zk_verifier):
        """测试批量验证证明"""
        proofs = [
            {
                "proof": {"a": [1, 2], "b": [3, 4], "c": [5, 6]},
                "public_inputs": [1, 2, 3],
                "verification_key": {"alpha": [1, 2]},
                "circuit_name": "health_data_heart_rate"
            },
            {
                "proof": {"a": [7, 8], "b": [9, 10], "c": [11, 12]},
                "public_inputs": [4, 5, 6],
                "verification_key": {"alpha": [3, 4]},
                "circuit_name": "health_data_blood_pressure"
            }
        ]
        
        with patch('suoke_blockchain_service.zk_integration.subprocess.run') as mock_run:
            # Mock所有验证都成功
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "true"
            
            results = await zk_verifier.batch_verify_proofs(proofs)
            
            assert len(results) == 2
            assert all(result is True for result in results)

    @pytest.mark.asyncio
    async def test_get_circuit_info(self, zk_verifier):
        """测试获取电路信息"""
        circuit_name = "health_data_heart_rate"
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = '''
            {
                "name": "health_data_heart_rate",
                "description": "Heart rate data verification circuit",
                "inputs": ["user_id_hash", "heart_rate", "timestamp"],
                "constraints": 1000
            }
            '''
            
            result = await zk_verifier.get_circuit_info(circuit_name)
            
            assert result["name"] == circuit_name
            assert "inputs" in result
            assert "constraints" in result

    @pytest.mark.asyncio
    async def test_performance_metrics(self, zk_verifier):
        """测试性能指标收集"""
        proof = {"a": [1, 2], "b": [3, 4], "c": [5, 6]}
        public_inputs = [1, 2, 3]
        verification_key = {"alpha": [1, 2]}
        circuit_name = "health_data_heart_rate"
        
        with patch('suoke_blockchain_service.zk_integration.subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "true"
            
            # 启用性能监控
            result = await zk_verifier.verify_proof(
                proof, public_inputs, verification_key, circuit_name,
                collect_metrics=True
            )
            
            assert result is True
            # 验证性能指标被收集（这里可以检查日志或指标存储） 