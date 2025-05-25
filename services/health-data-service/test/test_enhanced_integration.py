#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康数据服务集成测试
测试增强版健康数据服务的所有功能
"""

import asyncio
import pytest
import time
from datetime import datetime, timedelta
from typing import List
import random

from services.health_data_service.internal.service.enhanced_health_data_service import (
    EnhancedHealthDataService, HealthDataPoint, DataQuery, StreamConfig,
    DataType, AggregationType
)

@pytest.fixture
async def health_service():
    """创建健康数据服务实例"""
    service = EnhancedHealthDataService()
    # 注意：在实际测试中，需要模拟或使用测试数据库
    # await service.initialize()
    yield service
    # await service.cleanup()

class TestHealthDataService:
    """健康数据服务测试类"""
    
    @pytest.mark.asyncio
    async def test_write_single_data_point(self, health_service):
        """测试写入单个数据点"""
        data_point = HealthDataPoint(
            user_id="test_user_001",
            data_type=DataType.VITAL_SIGNS,
            timestamp=datetime.utcnow(),
            value=72.0,
            unit="bpm",
            metadata={"type": "heart_rate"},
            tags={"device": "smartwatch", "location": "home"}
        )
        
        result = await health_service.write_data([data_point])
        
        assert result['success'] == True
        assert result['written'] == 1
        assert result['failed'] == 0
        assert result['write_time'] > 0
    
    @pytest.mark.asyncio
    async def test_batch_write_data(self, health_service):
        """测试批量写入数据"""
        data_points = []
        base_time = datetime.utcnow()
        
        # 创建100个数据点
        for i in range(100):
            data_point = HealthDataPoint(
                user_id="test_user_002",
                data_type=DataType.ACTIVITY,
                timestamp=base_time - timedelta(minutes=i),
                value=random.randint(0, 10000),
                unit="steps",
                metadata={"activity_type": "walking"},
                tags={"device": "fitness_tracker"}
            )
            data_points.append(data_point)
        
        result = await health_service.write_data(data_points)
        
        assert result['success'] == True
        assert result['written'] == 100
        assert result['failed'] == 0
        print(f"批量写入100个数据点耗时: {result['write_time']:.3f}秒")
    
    @pytest.mark.asyncio
    async def test_query_raw_data(self, health_service):
        """测试查询原始数据"""
        # 先写入测试数据
        user_id = "test_user_003"
        data_points = []
        base_time = datetime.utcnow()
        
        for i in range(10):
            data_point = HealthDataPoint(
                user_id=user_id,
                data_type=DataType.SLEEP,
                timestamp=base_time - timedelta(hours=i),
                value=random.choice([1, 2, 3, 4]),  # 睡眠阶段
                unit="stage",
                metadata={"quality": random.choice(["good", "fair", "poor"])}
            )
            data_points.append(data_point)
        
        await health_service.write_data(data_points)
        
        # 查询数据
        query = DataQuery(
            user_id=user_id,
            data_types=[DataType.SLEEP],
            start_time=base_time - timedelta(days=1),
            end_time=base_time
        )
        
        result = await health_service.query_data(query)
        
        assert result['user_id'] == user_id
        assert DataType.SLEEP.value in result['data']
        sleep_data = result['data'][DataType.SLEEP.value]
        assert len(sleep_data) == 10
        assert result['query_time'] > 0
    
    @pytest.mark.asyncio
    async def test_query_aggregated_data(self, health_service):
        """测试查询聚合数据"""
        # 先写入测试数据
        user_id = "test_user_004"
        data_points = []
        base_time = datetime.utcnow()
        
        # 创建24小时的心率数据
        for hour in range(24):
            for minute in range(0, 60, 5):  # 每5分钟一个数据点
                timestamp = base_time - timedelta(hours=hour, minutes=minute)
                heart_rate = 60 + random.randint(-10, 30)  # 50-90 bpm
                
                data_point = HealthDataPoint(
                    user_id=user_id,
                    data_type=DataType.VITAL_SIGNS,
                    timestamp=timestamp,
                    value=float(heart_rate),
                    unit="bpm",
                    metadata={"type": "heart_rate"}
                )
                data_points.append(data_point)
        
        await health_service.write_data(data_points)
        
        # 查询1小时平均心率
        query = DataQuery(
            user_id=user_id,
            data_types=[DataType.VITAL_SIGNS],
            start_time=base_time - timedelta(days=1),
            end_time=base_time,
            aggregation=AggregationType.MEAN,
            interval="1h"
        )
        
        result = await health_service.query_data(query)
        
        assert result['user_id'] == user_id
        assert DataType.VITAL_SIGNS.value in result['data']
        aggregated_data = result['data'][DataType.VITAL_SIGNS.value]
        assert len(aggregated_data) > 0
        assert aggregated_data[0]['aggregation'] == 'mean'
        assert aggregated_data[0]['interval'] == '1h'
    
    @pytest.mark.asyncio
    async def test_cache_functionality(self, health_service):
        """测试缓存功能"""
        user_id = "test_user_005"
        query = DataQuery(
            user_id=user_id,
            data_types=[DataType.NUTRITION],
            start_time=datetime.utcnow() - timedelta(days=7),
            end_time=datetime.utcnow()
        )
        
        # 第一次查询（缓存未命中）
        start_time = time.time()
        result1 = await health_service.query_data(query)
        first_query_time = time.time() - start_time
        
        # 第二次查询（缓存命中）
        start_time = time.time()
        result2 = await health_service.query_data(query)
        second_query_time = time.time() - start_time
        
        # 验证缓存生效
        assert second_query_time < first_query_time * 0.5  # 缓存查询应该快很多
        assert health_service.stats['cache_hits'] > 0
        print(f"首次查询: {first_query_time:.3f}秒, 缓存查询: {second_query_time:.3f}秒")
    
    @pytest.mark.asyncio
    async def test_data_export(self, health_service):
        """测试数据导出功能"""
        user_id = "test_user_006"
        
        # 写入测试数据
        data_points = []
        base_time = datetime.utcnow()
        
        for i in range(50):
            data_point = HealthDataPoint(
                user_id=user_id,
                data_type=DataType.LAB_RESULTS,
                timestamp=base_time - timedelta(days=i),
                value=random.uniform(4.0, 6.0),
                unit="mmol/L",
                metadata={
                    "test_name": "glucose",
                    "lab_name": "Test Lab",
                    "reference_range": "3.9-6.1"
                }
            )
            data_points.append(data_point)
        
        await health_service.write_data(data_points)
        
        # 导出数据
        export_path = await health_service.export_data(
            user_id=user_id,
            data_types=[DataType.LAB_RESULTS],
            start_time=base_time - timedelta(days=60),
            end_time=base_time,
            format='csv'
        )
        
        assert export_path.endswith('.csv')
        # 实际测试中应该验证文件内容
        print(f"数据已导出到: {export_path}")
    
    @pytest.mark.asyncio
    async def test_stream_processing(self, health_service):
        """测试流处理功能"""
        config = StreamConfig(
            topic="health_data_vital_signs",
            group_id="test_consumer_group",
            batch_size=10,
            batch_timeout=1.0
        )
        
        # 创建流处理器
        stream_processor = health_service.create_stream_processor(config)
        
        # 模拟处理一些消息
        processed_count = 0
        async for message in stream_processor:
            processed_count += 1
            
            # 验证消息格式
            assert 'user_id' in message
            assert 'timestamp' in message
            assert 'value' in message
            
            # 检查是否有异常检测
            if 'alert' in message:
                print(f"检测到异常: {message['alert']}")
            
            # 处理10条消息后退出
            if processed_count >= 10:
                break
        
        assert processed_count == 10
        assert health_service.stats['active_streams'] >= 0
    
    @pytest.mark.asyncio
    async def test_data_sharding(self, health_service):
        """测试数据分片功能"""
        # 测试相同用户和数据类型总是分配到相同分片
        user_id = "test_user_007"
        data_type = DataType.VITAL_SIGNS
        
        shard_id1 = health_service._get_shard_id(user_id, data_type)
        shard_id2 = health_service._get_shard_id(user_id, data_type)
        
        assert shard_id1 == shard_id2
        assert 0 <= shard_id1 < health_service.shard_config['shard_count']
        
        # 测试不同用户分配到不同分片的分布
        shard_distribution = {}
        for i in range(1000):
            test_user = f"test_user_{i:04d}"
            shard_id = health_service._get_shard_id(test_user, data_type)
            shard_distribution[shard_id] = shard_distribution.get(shard_id, 0) + 1
        
        # 验证分片分布相对均匀
        avg_per_shard = 1000 / health_service.shard_config['shard_count']
        for shard_id, count in shard_distribution.items():
            assert abs(count - avg_per_shard) < avg_per_shard * 0.5  # 允许50%的偏差
        
        print(f"分片分布: {shard_distribution}")
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, health_service):
        """测试并发操作"""
        async def write_task(user_id: str, count: int):
            """写入任务"""
            data_points = []
            for i in range(count):
                data_point = HealthDataPoint(
                    user_id=user_id,
                    data_type=DataType.ACTIVITY,
                    timestamp=datetime.utcnow(),
                    value=float(i),
                    unit="count"
                )
                data_points.append(data_point)
            
            return await health_service.write_data(data_points)
        
        async def read_task(user_id: str):
            """读取任务"""
            query = DataQuery(
                user_id=user_id,
                data_types=[DataType.ACTIVITY],
                start_time=datetime.utcnow() - timedelta(hours=1),
                end_time=datetime.utcnow()
            )
            return await health_service.query_data(query)
        
        # 创建并发任务
        tasks = []
        
        # 10个写入任务
        for i in range(10):
            user_id = f"concurrent_user_{i:03d}"
            tasks.append(write_task(user_id, 100))
        
        # 10个读取任务
        for i in range(10):
            user_id = f"concurrent_user_{i:03d}"
            tasks.append(read_task(user_id))
        
        # 执行所有任务
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # 验证结果
        write_results = results[:10]
        read_results = results[10:]
        
        successful_writes = sum(1 for r in write_results if not isinstance(r, Exception) and r['success'])
        successful_reads = sum(1 for r in read_results if not isinstance(r, Exception))
        
        assert successful_writes >= 8  # 至少80%成功
        assert successful_reads >= 8   # 至少80%成功
        
        print(f"并发测试完成: {successful_writes}/10 写入成功, {successful_reads}/10 读取成功")
        print(f"总耗时: {total_time:.3f}秒")
    
    @pytest.mark.asyncio
    async def test_error_handling(self, health_service):
        """测试错误处理"""
        # 测试无效数据类型
        with pytest.raises(ValueError):
            invalid_point = HealthDataPoint(
                user_id="test_user",
                data_type="invalid_type",  # 这会引发错误
                timestamp=datetime.utcnow(),
                value=1.0,
                unit="unit"
            )
        
        # 测试空数据写入
        result = await health_service.write_data([])
        assert result['written'] == 0
        
        # 测试无效时间范围查询
        query = DataQuery(
            user_id="test_user",
            data_types=[DataType.VITAL_SIGNS],
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() - timedelta(days=1)  # 结束时间早于开始时间
        )
        
        result = await health_service.query_data(query)
        # 应该返回空结果而不是错误
        assert DataType.VITAL_SIGNS.value in result['data']
    
    @pytest.mark.asyncio
    async def test_health_status(self, health_service):
        """测试健康状态检查"""
        status = health_service.get_health_status()
        
        assert status['service'] == 'health-data-service'
        assert status['status'] == 'healthy'
        assert 'stats' in status
        assert 'connections' in status
        assert 'sharding' in status
        assert 'aggregation' in status
        assert status['uptime'] > 0
        
        # 验证统计信息
        stats = status['stats']
        assert 'total_writes' in stats
        assert 'total_reads' in stats
        assert 'cache_hits' in stats
        assert 'cache_misses' in stats
        
        print(f"服务状态: {status}")

# 性能测试
class TestPerformance:
    """性能测试类"""
    
    @pytest.mark.asyncio
    async def test_write_performance(self, health_service):
        """测试写入性能"""
        batch_sizes = [10, 100, 1000]
        
        for batch_size in batch_sizes:
            data_points = []
            for i in range(batch_size):
                data_point = HealthDataPoint(
                    user_id=f"perf_user_{i % 100}",
                    data_type=DataType.VITAL_SIGNS,
                    timestamp=datetime.utcnow() - timedelta(seconds=i),
                    value=random.uniform(60, 100),
                    unit="bpm",
                    metadata={"type": "heart_rate"}
                )
                data_points.append(data_point)
            
            start_time = time.time()
            result = await health_service.write_data(data_points)
            write_time = time.time() - start_time
            
            throughput = batch_size / write_time
            print(f"批量大小: {batch_size}, 耗时: {write_time:.3f}秒, 吞吐量: {throughput:.0f} 点/秒")
            
            assert result['success'] == True
            assert throughput > batch_size * 10  # 至少10倍的吞吐量
    
    @pytest.mark.asyncio
    async def test_query_performance(self, health_service):
        """测试查询性能"""
        # 准备测试数据
        user_id = "perf_query_user"
        data_points = []
        base_time = datetime.utcnow()
        
        # 创建10000个数据点
        for i in range(10000):
            timestamp = base_time - timedelta(minutes=i)
            data_point = HealthDataPoint(
                user_id=user_id,
                data_type=DataType.ACTIVITY,
                timestamp=timestamp,
                value=float(random.randint(0, 10000)),
                unit="steps"
            )
            data_points.append(data_point)
        
        # 批量写入
        await health_service.write_data(data_points)
        
        # 测试不同时间范围的查询性能
        time_ranges = [
            ("1小时", timedelta(hours=1)),
            ("1天", timedelta(days=1)),
            ("7天", timedelta(days=7))
        ]
        
        for name, time_delta in time_ranges:
            query = DataQuery(
                user_id=user_id,
                data_types=[DataType.ACTIVITY],
                start_time=base_time - time_delta,
                end_time=base_time
            )
            
            start_time = time.time()
            result = await health_service.query_data(query)
            query_time = time.time() - start_time
            
            data_count = len(result['data'].get(DataType.ACTIVITY.value, []))
            print(f"查询{name}数据: {data_count}个点, 耗时: {query_time:.3f}秒")
            
            assert query_time < 1.0  # 查询应该在1秒内完成

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"]) 