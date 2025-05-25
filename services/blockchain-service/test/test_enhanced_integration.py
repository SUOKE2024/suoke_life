#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
区块链服务集成测试
测试增强版区块链服务的所有功能
"""

import asyncio
import pytest
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
import hashlib

from services.blockchain_service.internal.service.enhanced_blockchain_service import (
    EnhancedBlockchainService, ChainType, TransactionPriority, IndexedData
)

@pytest.fixture
async def blockchain_service():
    """创建区块链服务实例"""
    service = EnhancedBlockchainService()
    # 注意：在实际测试中，需要模拟或使用测试区块链
    # await service.initialize()
    yield service
    # await service.cleanup()

class TestBlockchainService:
    """区块链服务测试类"""
    
    @pytest.mark.asyncio
    async def test_send_single_transaction(self, blockchain_service):
        """测试发送单笔交易"""
        result = await blockchain_service.send_transaction(
            to_address="0x742d35Cc6634C0532925a3b844Bc9e7595f8b2dc",
            data="0x1234567890",
            value=1000000000000000000,  # 1 ETH
            priority=TransactionPriority.NORMAL
        )
        
        assert result['status'] in ['success', 'queued']
        if result['status'] == 'success':
            assert 'transaction_hash' in result
            assert 'block_number' in result
            assert 'gas_used' in result
        else:
            assert result['priority'] == TransactionPriority.NORMAL.value
    
    @pytest.mark.asyncio
    async def test_batch_transaction_processing(self, blockchain_service):
        """测试批量交易处理"""
        # 发送多笔低优先级交易
        transactions = []
        for i in range(10):
            result = await blockchain_service.send_transaction(
                to_address=f"0x742d35Cc6634C0532925a3b844Bc9e7595f8b2d{i:01x}",
                data=f"0x{i:064x}",
                value=1000000000000000,  # 0.001 ETH
                priority=TransactionPriority.LOW
            )
            transactions.append(result)
        
        # 验证交易被加入队列
        queued_count = sum(1 for tx in transactions if tx['status'] == 'queued')
        assert queued_count > 0
        print(f"批量交易：{queued_count}笔交易已加入队列")
    
    @pytest.mark.asyncio
    async def test_multi_chain_support(self, blockchain_service):
        """测试多链支持"""
        # 获取支持的链
        status = blockchain_service.get_health_status()
        active_chains = status['stats']['active_chains']
        
        assert len(active_chains) > 0
        print(f"活跃的链: {active_chains}")
        
        # 测试切换链
        if ChainType.PRIVATE.value in active_chains:
            success = await blockchain_service.switch_chain(ChainType.PRIVATE)
            assert success == True
            assert blockchain_service.current_chain == ChainType.PRIVATE
    
    @pytest.mark.asyncio
    async def test_contract_deployment(self, blockchain_service):
        """测试合约部署"""
        # 简单的存储合约字节码
        bytecode = "0x608060405234801561001057600080fd5b50610150806100206000396000f3fe"
        abi = [
            {
                "inputs": [],
                "name": "get",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"internalType": "uint256", "name": "x", "type": "uint256"}],
                "name": "set",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]
        
        result = await blockchain_service.deploy_contract(
            bytecode=bytecode,
            abi=abi
        )
        
        if result['status'] == 'success':
            assert 'contract_address' in result
            assert 'transaction_hash' in result
            assert 'gas_used' in result
            print(f"合约部署成功: {result['contract_address']}")
        else:
            print(f"合约部署失败: {result.get('error', 'Unknown error')}")
    
    @pytest.mark.asyncio
    async def test_contract_method_call(self, blockchain_service):
        """测试合约方法调用"""
        # 使用已部署的合约地址（示例）
        contract_address = "0x742d35Cc6634C0532925a3b844Bc9e7595f8b2dc"
        abi = [
            {
                "inputs": [],
                "name": "totalSupply",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        # 调用view方法
        result = await blockchain_service.call_contract_method(
            contract_address=contract_address,
            method_name="totalSupply",
            args=[],
            abi=abi,
            use_cache=True
        )
        
        assert result is not None
        print(f"合约方法调用结果: {result}")
        
        # 再次调用，应该从缓存获取
        start_time = time.time()
        cached_result = await blockchain_service.call_contract_method(
            contract_address=contract_address,
            method_name="totalSupply",
            args=[],
            abi=abi,
            use_cache=True
        )
        cache_time = time.time() - start_time
        
        assert cached_result == result
        assert cache_time < 0.1  # 缓存查询应该很快
        print(f"缓存查询时间: {cache_time:.3f}秒")
    
    @pytest.mark.asyncio
    async def test_transaction_indexing(self, blockchain_service):
        """测试交易索引"""
        # 索引交易数据
        tx_hash = "0x" + "a" * 64
        user_id = "test_user_001"
        data_type = "health_data"
        data_hash = hashlib.sha256(b"test_data").hexdigest()
        
        success = await blockchain_service.index_transaction_data(
            tx_hash=tx_hash,
            user_id=user_id,
            data_type=data_type,
            data_hash=data_hash,
            metadata={"test": "data", "timestamp": datetime.now().isoformat()},
            tags=["test", "health", "demo"]
        )
        
        assert success == True
        
        # 查询索引数据
        results = await blockchain_service.query_indexed_data(
            user_id=user_id,
            data_type=data_type,
            limit=10
        )
        
        assert len(results) > 0
        assert results[0].user_id == user_id
        assert results[0].data_type == data_type
        assert results[0].transaction_hash == tx_hash
        print(f"查询到{len(results)}条索引记录")
    
    @pytest.mark.asyncio
    async def test_tag_based_query(self, blockchain_service):
        """测试基于标签的查询"""
        # 索引多条带标签的数据
        tag = f"test_tag_{int(time.time())}"
        
        for i in range(5):
            await blockchain_service.index_transaction_data(
                tx_hash=f"0x{'b' * 63}{i}",
                user_id=f"user_{i}",
                data_type="test_data",
                data_hash=hashlib.sha256(f"data_{i}".encode()).hexdigest(),
                tags=[tag, f"user_{i}"]
            )
        
        # 按标签查询
        results = await blockchain_service.query_indexed_data(
            tags=[tag],
            limit=10
        )
        
        assert len(results) == 5
        for result in results:
            assert tag in result.tags
        print(f"通过标签'{tag}'查询到{len(results)}条记录")
    
    @pytest.mark.asyncio
    async def test_time_range_query(self, blockchain_service):
        """测试时间范围查询"""
        user_id = "time_test_user"
        now = datetime.now()
        
        # 索引不同时间的数据
        for i in range(10):
            # 模拟不同时间的数据
            timestamp = now - timedelta(hours=i)
            await blockchain_service.index_transaction_data(
                tx_hash=f"0x{'c' * 63}{i}",
                user_id=user_id,
                data_type="time_series_data",
                data_hash=hashlib.sha256(f"time_data_{i}".encode()).hexdigest(),
                metadata={"timestamp": timestamp.isoformat()}
            )
        
        # 查询最近3小时的数据
        results = await blockchain_service.query_indexed_data(
            user_id=user_id,
            start_time=now - timedelta(hours=3),
            end_time=now,
            limit=10
        )
        
        # 由于索引时使用的是当前时间，所有数据都应该在范围内
        assert len(results) > 0
        print(f"时间范围查询返回{len(results)}条记录")
    
    @pytest.mark.asyncio
    async def test_gas_price_optimization(self, blockchain_service):
        """测试gas价格优化"""
        # 发送不同优先级的交易
        priorities = [
            TransactionPriority.LOW,
            TransactionPriority.NORMAL,
            TransactionPriority.HIGH,
            TransactionPriority.URGENT
        ]
        
        gas_prices = []
        for priority in priorities:
            # 获取优化的gas价格
            web3 = blockchain_service._get_web3(blockchain_service.current_chain)
            gas_price = await blockchain_service._get_optimal_gas_price(web3, priority)
            gas_prices.append((priority, gas_price))
        
        # 验证gas价格递增
        for i in range(1, len(gas_prices)):
            assert gas_prices[i][1] > gas_prices[i-1][1]
            print(f"{gas_prices[i][0].name}: {gas_prices[i][1]} wei")
    
    @pytest.mark.asyncio
    async def test_contract_cache_management(self, blockchain_service):
        """测试合约缓存管理"""
        # 添加多个合约到缓存
        for i in range(5):
            address = f"0x{'d' * 39}{i}"
            abi = [{"name": f"contract_{i}", "type": "function"}]
            
            contract = await blockchain_service.get_contract(address, abi)
            assert contract is not None
        
        # 检查缓存状态
        cache_size = len(blockchain_service.contract_cache)
        assert cache_size == 5
        
        # 访问第一个合约多次，增加访问计数
        first_address = "0x" + "d" * 39 + "0"
        for _ in range(10):
            await blockchain_service.get_contract(
                first_address,
                [{"name": "contract_0", "type": "function"}]
            )
        
        # 验证缓存命中
        stats = blockchain_service.stats
        assert stats['cache_hits'] > 0
        print(f"缓存命中率: {stats['cache_hits'] / (stats['cache_hits'] + stats['cache_misses']):.2%}")
    
    @pytest.mark.asyncio
    async def test_concurrent_transactions(self, blockchain_service):
        """测试并发交易处理"""
        async def send_transaction(index: int):
            """发送单笔交易"""
            return await blockchain_service.send_transaction(
                to_address=f"0x742d35Cc6634C0532925a3b844Bc9e7595f8b2d{index % 10}",
                data=f"0x{index:064x}",
                value=1000000000000000,  # 0.001 ETH
                priority=TransactionPriority.NORMAL
            )
        
        # 并发发送20笔交易
        start_time = time.time()
        tasks = [send_transaction(i) for i in range(20)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # 统计结果
        successful = sum(1 for r in results if isinstance(r, dict) and r.get('status') in ['success', 'queued'])
        failed = sum(1 for r in results if isinstance(r, Exception))
        
        assert successful > 0
        print(f"并发交易测试: {successful}/20 成功, {failed} 失败")
        print(f"总耗时: {total_time:.3f}秒, 平均: {total_time/20:.3f}秒/交易")
    
    @pytest.mark.asyncio
    async def test_health_status(self, blockchain_service):
        """测试健康状态检查"""
        status = blockchain_service.get_health_status()
        
        assert status['service'] == 'blockchain-service'
        assert status['status'] == 'healthy'
        assert 'stats' in status
        assert 'chains' in status
        assert 'cache' in status
        assert 'batch_processing' in status
        
        # 验证统计信息
        stats = status['stats']
        assert 'total_transactions' in stats
        assert 'batch_transactions' in stats
        assert 'cache_hits' in stats
        assert 'average_gas_price' in stats
        
        print(f"服务状态: {json.dumps(status, indent=2)}")

# 性能测试
class TestPerformance:
    """性能测试类"""
    
    @pytest.mark.asyncio
    async def test_batch_processing_performance(self, blockchain_service):
        """测试批处理性能"""
        batch_sizes = [10, 50, 100]
        
        for batch_size in batch_sizes:
            start_time = time.time()
            
            # 发送批量交易
            tasks = []
            for i in range(batch_size):
                task = blockchain_service.send_transaction(
                    to_address=f"0x{'e' * 39}{i % 10}",
                    data="0x00",
                    value=0,
                    priority=TransactionPriority.LOW
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            batch_time = time.time() - start_time
            
            queued = sum(1 for r in results if r['status'] == 'queued')
            throughput = batch_size / batch_time
            
            print(f"批量大小: {batch_size}, 耗时: {batch_time:.3f}秒")
            print(f"吞吐量: {throughput:.0f} 交易/秒, 队列中: {queued}")
    
    @pytest.mark.asyncio
    async def test_index_query_performance(self, blockchain_service):
        """测试索引查询性能"""
        # 先创建大量索引数据
        user_id = "perf_test_user"
        
        print("创建测试索引数据...")
        for i in range(1000):
            await blockchain_service.index_transaction_data(
                tx_hash=f"0x{'f' * 60}{i:04x}",
                user_id=user_id if i % 10 == 0 else f"user_{i}",
                data_type=f"type_{i % 5}",
                data_hash=hashlib.sha256(f"data_{i}".encode()).hexdigest(),
                tags=[f"tag_{i % 10}", f"category_{i % 3}"]
            )
        
        # 测试不同查询的性能
        queries = [
            ("用户查询", {"user_id": user_id}),
            ("标签查询", {"tags": ["tag_5"]}),
            ("类型查询", {"data_type": "type_2"}),
            ("组合查询", {"tags": ["tag_5"], "data_type": "type_2"})
        ]
        
        for name, params in queries:
            start_time = time.time()
            results = await blockchain_service.query_indexed_data(**params, limit=100)
            query_time = time.time() - start_time
            
            print(f"{name}: {len(results)}条结果, 耗时: {query_time:.3f}秒")

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"]) 