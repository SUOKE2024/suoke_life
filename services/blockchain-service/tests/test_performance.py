"""
test_performance - 索克生活项目模块
"""

            import random
        import os
        import psutil
from concurrent.futures import ThreadPoolExecutor
from suoke_blockchain_service.service import BlockchainService
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
import pytest
import time
import uuid

"""
性能测试和基准测试

测试区块链服务的性能指标和基准。
"""




@pytest.fixture
def blockchain_service():
    """创建区块链服务实例"""
    service = BlockchainService()
    service.encryption_service = AsyncMock()
    service.zk_proof_generator = AsyncMock()
    service.zk_proof_verifier = AsyncMock()
    service.ipfs_client = AsyncMock()
    return service


class TestPerformanceBenchmarks:
    """性能基准测试"""

    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_store_health_data_performance(self, blockchain_service, benchmark):
        """测试存储健康数据的性能"""
        # Mock外部依赖
        blockchain_service.encryption_service.encrypt_data.return_value = (b"encrypted", "key")
        blockchain_service.ipfs_client.upload_data.return_value = "QmHash"
        blockchain_service.zk_proof_generator.generate_proof.return_value = {"proof": "test"}
        
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db, \
             patch('suoke_blockchain_service.service.get_blockchain_client') as mock_blockchain:
            
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_client = AsyncMock()
            mock_client.store_health_data.return_value = "0x123456789"
            mock_blockchain.return_value = mock_client
            
            async def store_operation():
                return await blockchain_service.store_health_data(
                    user_id=str(uuid.uuid4()),
                    data={"heart_rate": 72, "timestamp": "2024-01-01T10:00:00Z"},
                    data_type="heart_rate"
                )
            
            # 基准测试
            result = await benchmark(store_operation)
            assert result["status"] == "pending"

    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_verify_health_data_performance(self, blockchain_service, benchmark):
        """测试验证健康数据的性能"""
        record_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db, \
             patch('suoke_blockchain_service.service.get_blockchain_client') as mock_blockchain:
            
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_health_record = MagicMock()
            mock_health_record.id = record_id
            mock_health_record.user_id = user_id
            mock_health_record.data_hash = "test_hash"
            mock_health_record.zkp_proof = {"proof": "test"}
            mock_health_record.public_inputs = [1, 2, 3]
            mock_health_record.verification_key = {"key": "test"}
            mock_health_record.ipfs_hash = "QmTestHash"
            mock_health_record.encrypted_data = b"encrypted_data"
            mock_health_record.record_metadata = {"zkp_circuit": "test_circuit"}
            mock_health_record.transaction = MagicMock()
            mock_health_record.transaction.transaction_hash = "0x123456789"
            
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_health_record
            mock_session.execute.return_value = mock_result

            mock_client = AsyncMock()
            mock_client.verify_health_data.return_value = True
            mock_blockchain.return_value = mock_client

            blockchain_service.zk_proof_verifier.verify_proof.return_value = True
            blockchain_service.ipfs_client.get_data.return_value = b"encrypted_data"
            
            async def verify_operation():
                return await blockchain_service.verify_health_data(
                    record_id=record_id,
                    user_id=user_id
                )
            
            result = await benchmark(verify_operation)
            assert result["overall_valid"] is True

    @pytest.mark.asyncio
    async def test_concurrent_operations_performance(self, blockchain_service):
        """测试并发操作性能"""
        blockchain_service.encryption_service.encrypt_data.return_value = (b"encrypted", "key")
        blockchain_service.ipfs_client.upload_data.return_value = "QmHash"
        blockchain_service.zk_proof_generator.generate_proof.return_value = {"proof": "test"}
        
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db, \
             patch('suoke_blockchain_service.service.get_blockchain_client') as mock_blockchain:
            
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_client = AsyncMock()
            mock_client.store_health_data.return_value = "0x123456789"
            mock_blockchain.return_value = mock_client
            
            concurrency_levels = [1, 5, 10, 20]
            
            for concurrency in concurrency_levels:
                start_time = time.time()
                
                tasks = []
                for i in range(concurrency):
                    task = blockchain_service.store_health_data(
                        user_id=f"user{i}",
                        data={"heart_rate": 70 + i},
                        data_type="heart_rate"
                    )
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                end_time = time.time()
                duration = end_time - start_time
                
                success_count = sum(1 for r in results if not isinstance(r, Exception))
                assert success_count == concurrency
                
                throughput = concurrency / duration
                print(f"并发级别 {concurrency}: {throughput:.2f} ops/sec")

    @pytest.mark.asyncio
    async def test_large_data_performance(self, blockchain_service):
        """测试大数据处理性能"""
        data_sizes = [
            {"size": "small", "records": 10},
            {"size": "medium", "records": 100},
            {"size": "large", "records": 500},
        ]
        
        blockchain_service.encryption_service.encrypt_data.return_value = (b"encrypted", "key")
        blockchain_service.ipfs_client.upload_data.return_value = "QmHash"
        blockchain_service.zk_proof_generator.generate_proof.return_value = {"proof": "test"}
        
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db, \
             patch('suoke_blockchain_service.service.get_blockchain_client') as mock_blockchain:
            
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_client = AsyncMock()
            mock_client.store_health_data.return_value = "0x123456789"
            mock_blockchain.return_value = mock_client
            
            for data_config in data_sizes:
                large_data = {
                    "measurements": [
                        {"value": i, "timestamp": f"2024-01-01T{i:02d}:00:00Z"} 
                        for i in range(data_config["records"])
                    ],
                    "metadata": {"description": f"测试数据集 - {data_config['size']}"}
                }
                
                start_time = time.time()
                
                result = await blockchain_service.store_health_data(
                    user_id="user123",
                    data=large_data,
                    data_type="comprehensive"
                )
                
                end_time = time.time()
                duration = end_time - start_time
                
                assert result["status"] == "pending"
                print(f"数据大小 {data_config['size']}: {duration:.3f}s")

    @pytest.mark.asyncio
    async def test_memory_usage_performance(self, blockchain_service):
        """测试内存使用性能"""
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Mock外部依赖
        blockchain_service.encryption_service.encrypt_data.return_value = (b"encrypted", "key")
        blockchain_service.ipfs_client.upload_data.return_value = "QmHash"
        blockchain_service.zk_proof_generator.generate_proof.return_value = {"proof": "test"}
        
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db, \
             patch('suoke_blockchain_service.service.get_blockchain_client') as mock_blockchain:
            
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_client = AsyncMock()
            mock_client.store_health_data.return_value = "0x123456789"
            mock_blockchain.return_value = mock_client
            
            # 执行大量操作
            for i in range(100):
                await blockchain_service.store_health_data(
                    user_id=f"user{i}",
                    data={"heart_rate": 70 + i, "data": "x" * 1000},  # 1KB数据
                    data_type="heart_rate"
                )
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            print(f"初始内存: {initial_memory:.2f} MB")
            print(f"最终内存: {final_memory:.2f} MB")
            print(f"内存增长: {memory_increase:.2f} MB")
            
            # 内存增长应该在合理范围内（小于100MB）
            assert memory_increase < 100

    @pytest.mark.asyncio
    async def test_database_query_performance(self, blockchain_service):
        """测试数据库查询性能"""
        user_id = str(uuid.uuid4())
        
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db:
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            # Mock大量记录
            mock_records = []
            for i in range(1000):
                mock_record = MagicMock()
                mock_record.id = str(uuid.uuid4())
                mock_record.data_type = "heart_rate"
                mock_record.data_hash = f"hash{i}"
                mock_record.ipfs_hash = f"QmHash{i}"
                mock_record.created_at = time.time()
                mock_record.zkp_proof = {"proof": f"test{i}"}
                mock_record.record_metadata = {}
                mock_record.transaction = MagicMock()
                mock_record.transaction.transaction_hash = f"0x{i}"
                mock_record.transaction.status = "confirmed"
                mock_records.append(mock_record)
            
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = mock_records
            mock_session.execute.return_value = mock_result
            
            # 测试不同分页大小的性能
            page_sizes = [10, 50, 100, 500]
            
            for page_size in page_sizes:
                start_time = time.time()
                
                result = await blockchain_service.get_health_records(
                    user_id=user_id,
                    limit=page_size,
                    offset=0
                )
                
                end_time = time.time()
                duration = end_time - start_time
                
                assert len(result["records"]) == 1000  # Mock返回所有记录
                print(f"分页大小 {page_size}: {duration:.3f}s")


class TestStressTests:
    """压力测试"""

    @pytest.mark.asyncio
    @pytest.mark.stress
    async def test_high_concurrency_stress(self, blockchain_service):
        """高并发压力测试"""
        blockchain_service.encryption_service.encrypt_data.return_value = (b"encrypted", "key")
        blockchain_service.ipfs_client.upload_data.return_value = "QmHash"
        blockchain_service.zk_proof_generator.generate_proof.return_value = {"proof": "test"}
        
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db, \
             patch('suoke_blockchain_service.service.get_blockchain_client') as mock_blockchain:
            
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_client = AsyncMock()
            mock_client.store_health_data.return_value = "0x123456789"
            mock_blockchain.return_value = mock_client
            
            concurrency = 50
            start_time = time.time()
            
            tasks = []
            for i in range(concurrency):
                task = blockchain_service.store_health_data(
                    user_id=f"stress_user{i}",
                    data={"heart_rate": 60 + (i % 40)},
                    data_type="heart_rate"
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            duration = end_time - start_time
            
            success_count = sum(1 for r in results if not isinstance(r, Exception))
            success_rate = success_count / concurrency
            throughput = success_count / duration
            
            print(f"压力测试结果:")
            print(f"  成功率: {success_rate:.2%}")
            print(f"  吞吐量: {throughput:.2f} ops/sec")
            
            assert success_rate > 0.90, f"成功率过低: {success_rate:.2%}"

    @pytest.mark.asyncio
    @pytest.mark.stress
    async def test_sustained_load_stress(self, blockchain_service):
        """持续负载压力测试"""
        # Mock外部依赖
        blockchain_service.encryption_service.encrypt_data.return_value = (b"encrypted", "key")
        blockchain_service.ipfs_client.upload_data.return_value = "QmHash"
        blockchain_service.zk_proof_generator.generate_proof.return_value = {"proof": "test"}
        
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db, \
             patch('suoke_blockchain_service.service.get_blockchain_client') as mock_blockchain:
            
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_client = AsyncMock()
            mock_client.store_health_data.return_value = "0x123456789"
            mock_blockchain.return_value = mock_client
            
            # 持续负载测试（30秒，每秒10个请求）
            duration_seconds = 10  # 减少测试时间
            requests_per_second = 10
            total_requests = 0
            successful_requests = 0
            
            start_time = time.time()
            end_time = start_time + duration_seconds
            
            while time.time() < end_time:
                batch_start = time.time()
                
                # 创建一批请求
                tasks = []
                for i in range(requests_per_second):
                    task = blockchain_service.store_health_data(
                        user_id=f"sustained_user{total_requests + i}",
                        data={"heart_rate": 70, "batch": int(time.time())},
                        data_type="heart_rate"
                    )
                    tasks.append(task)
                
                # 执行批次
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 统计结果
                total_requests += len(tasks)
                successful_requests += sum(1 for r in results if not isinstance(r, Exception))
                
                # 控制请求频率
                batch_duration = time.time() - batch_start
                if batch_duration < 1.0:
                    await asyncio.sleep(1.0 - batch_duration)
            
            actual_duration = time.time() - start_time
            success_rate = successful_requests / total_requests if total_requests > 0 else 0
            actual_throughput = successful_requests / actual_duration
            
            print(f"持续负载测试结果:")
            print(f"  测试时长: {actual_duration:.1f}s")
            print(f"  总请求数: {total_requests}")
            print(f"  成功请求数: {successful_requests}")
            print(f"  成功率: {success_rate:.2%}")
            print(f"  实际吞吐量: {actual_throughput:.2f} ops/sec")
            
            # 成功率应该大于90%
            assert success_rate > 0.90, f"持续负载成功率过低: {success_rate:.2%}"

    @pytest.mark.asyncio
    @pytest.mark.stress
    async def test_resource_exhaustion_stress(self, blockchain_service):
        """资源耗尽压力测试"""
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Mock外部依赖
        blockchain_service.encryption_service.encrypt_data.return_value = (b"encrypted", "key")
        blockchain_service.ipfs_client.upload_data.return_value = "QmHash"
        blockchain_service.zk_proof_generator.generate_proof.return_value = {"proof": "test"}
        
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db, \
             patch('suoke_blockchain_service.service.get_blockchain_client') as mock_blockchain:
            
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_client = AsyncMock()
            mock_client.store_health_data.return_value = "0x123456789"
            mock_blockchain.return_value = mock_client
            
            # 创建大量数据以测试内存限制
            large_data = {
                "measurements": [{"value": i} for i in range(10000)],  # 10K记录
                "metadata": {"description": "资源耗尽测试" * 1000}  # 大量文本
            }
            
            successful_operations = 0
            max_operations = 50  # 限制操作数量以避免测试超时
            
            try:
                for i in range(max_operations):
                    await blockchain_service.store_health_data(
                        user_id=f"resource_user{i}",
                        data=large_data,
                        data_type="comprehensive"
                    )
                    successful_operations += 1
                    
                    # 检查内存使用
                    current_memory = process.memory_info().rss / 1024 / 1024  # MB
                    memory_increase = current_memory - initial_memory
                    
                    # 如果内存增长过多，停止测试
                    if memory_increase > 500:  # 500MB限制
                        print(f"内存使用过多，停止测试: {memory_increase:.2f} MB")
                        break
                        
            except Exception as e:
                print(f"资源耗尽测试在第 {successful_operations} 次操作时失败: {e}")
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            print(f"资源耗尽测试结果:")
            print(f"  成功操作数: {successful_operations}")
            print(f"  初始内存: {initial_memory:.2f} MB")
            print(f"  最终内存: {final_memory:.2f} MB")
            print(f"  内存增长: {memory_increase:.2f} MB")
            
            # 应该能够处理至少10个大数据操作
            assert successful_operations >= 10, f"资源耗尽测试失败，只完成了 {successful_operations} 次操作"


class TestLoadTests:
    """负载测试"""

    @pytest.mark.asyncio
    @pytest.mark.load
    async def test_mixed_workload(self, blockchain_service):
        """混合工作负载测试"""
        # Mock外部依赖
        blockchain_service.encryption_service.encrypt_data.return_value = (b"encrypted", "key")
        blockchain_service.ipfs_client.upload_data.return_value = "QmHash"
        blockchain_service.zk_proof_generator.generate_proof.return_value = {"proof": "test"}
        blockchain_service.zk_proof_verifier.verify_proof.return_value = True
        blockchain_service.ipfs_client.get_data.return_value = b"encrypted_data"
        
        with patch('suoke_blockchain_service.service.get_db_session') as mock_db, \
             patch('suoke_blockchain_service.service.get_blockchain_client') as mock_blockchain:
            
            mock_session = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_session
            
            mock_client = AsyncMock()
            mock_client.store_health_data.return_value = "0x123456789"
            mock_client.verify_health_data.return_value = True
            mock_client.grant_access.return_value = "0x987654321"
            mock_blockchain.return_value = mock_client
            
            # 混合工作负载：存储、验证、授权操作
            operations = []
            
            # 50% 存储操作
            for i in range(25):
                op = ("store", {
                    "user_id": f"user{i}",
                    "data": {"heart_rate": 70 + i % 30},
                    "data_type": "heart_rate"
                })
                operations.append(op)
            
            # 30% 验证操作
            for i in range(15):
                # Mock健康记录
                mock_health_record = MagicMock()
                mock_health_record.id = f"record{i}"
                mock_health_record.user_id = f"user{i}"
                mock_health_record.data_hash = f"hash{i}"
                mock_health_record.zkp_proof = {"proof": "test"}
                mock_health_record.public_inputs = [1, 2, 3]
                mock_health_record.verification_key = {"key": "test"}
                mock_health_record.ipfs_hash = "QmTestHash"
                mock_health_record.encrypted_data = b"encrypted_data"
                mock_health_record.record_metadata = {"zkp_circuit": "test_circuit"}
                mock_health_record.transaction = MagicMock()
                mock_health_record.transaction.transaction_hash = "0x123456789"
                
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = mock_health_record
                mock_session.execute.return_value = mock_result
                
                op = ("verify", {
                    "record_id": f"record{i}",
                    "user_id": f"user{i}"
                })
                operations.append(op)
            
            # 20% 授权操作
            for i in range(10):
                # Mock健康记录和授权
                mock_health_record = MagicMock()
                mock_health_record.id = f"record{i}"
                mock_health_record.user_id = f"user{i}"
                mock_health_record.data_hash = f"hash{i}"
                
                mock_session.execute.side_effect = [
                    MagicMock(scalar_one_or_none=MagicMock(return_value=mock_health_record)),
                    MagicMock(scalar_one_or_none=MagicMock(return_value=None))
                ]
                
                op = ("grant", {
                    "owner_id": f"user{i}",
                    "grantee_id": f"grantee{i}",
                    "record_id": f"record{i}",
                    "access_level": "read"
                })
                operations.append(op)
            
            # 随机打乱操作顺序
            random.shuffle(operations)
            
            # 执行混合工作负载
            start_time = time.time()
            results = []
            
            for op_type, params in operations:
                try:
                    if op_type == "store":
                        result = await blockchain_service.store_health_data(**params)
                    elif op_type == "verify":
                        result = await blockchain_service.verify_health_data(**params)
                    elif op_type == "grant":
                        result = await blockchain_service.grant_access(**params)
                    
                    results.append(("success", op_type, result))
                except Exception as e:
                    results.append(("error", op_type, str(e)))
            
            end_time = time.time()
            duration = end_time - start_time
            
            # 统计结果
            success_count = sum(1 for r in results if r[0] == "success")
            error_count = len(results) - success_count
            throughput = len(operations) / duration
            
            # 按操作类型统计
            store_ops = sum(1 for r in results if r[1] == "store")
            verify_ops = sum(1 for r in results if r[1] == "verify")
            grant_ops = sum(1 for r in results if r[1] == "grant")
            
            print(f"混合工作负载测试结果:")
            print(f"  总操作数: {len(operations)}")
            print(f"  成功数: {success_count}")
            print(f"  失败数: {error_count}")
            print(f"  总耗时: {duration:.3f}s")
            print(f"  吞吐量: {throughput:.2f} ops/sec")
            print(f"  操作分布: 存储({store_ops}), 验证({verify_ops}), 授权({grant_ops})")
            
            # 成功率应该大于90%
            success_rate = success_count / len(operations)
            assert success_rate > 0.90, f"混合工作负载成功率过低: {success_rate:.2%}" 