#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
健康数据服务优化功能集成测试
验证所有优化功能的正确性和性能
"""

import asyncio
import pytest
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from ...internal.model.database import Base, HealthDataRecord
from ...internal.model.health_data import HealthData, HealthDataType, DeviceType, MeasurementUnit
from ...internal.service.health_data_service_optimized import HealthDataServiceOptimized
from ...internal.service.quality.data_quality_assessor import DataQualityAssessor
from ...internal.service.analytics.health_index_calculator import HealthIndexCalculator
from ...internal.service.tcm.constitution_analyzer import TCMConstitutionAnalyzer
from ...internal.repository.health_data_repository_optimized import HealthDataRepositoryOptimized
from ...internal.delivery.health_data_handler_optimized import HealthDataHandlerOptimized
from ...pkg.utils.cache_service import CacheService
from ...pkg.utils.error_handler import ErrorHandler
from ...pkg.utils.performance_monitor import PerformanceMonitor


class TestOptimizedHealthDataService:
    """优化版健康数据服务集成测试"""
    
    @pytest.fixture
    async def setup_test_environment(self):
        """设置测试环境"""
        # 创建内存SQLite数据库
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            echo=False
        )
        
        # 创建表
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # 创建会话工厂
        async_session_factory = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # 配置
        config = {
            'database': {
                'url': "sqlite+aiosqlite:///:memory:",
                'pool_size': 5,
                'max_overflow': 10
            },
            'cache': {
                'type': 'memory',
                'max_size': 1000,
                'ttl': 300
            },
            'performance': {
                'batch_size': 100,
                'max_concurrent_requests': 50
            },
            'quality': {
                'min_quality_score': 0.7,
                'validation_rules': {}
            }
        }
        
        # 创建服务组件
        cache_service = CacheService(config['cache'])
        await cache_service.initialize()
        
        error_handler = ErrorHandler(config)
        performance_monitor = PerformanceMonitor(config)
        await performance_monitor.initialize()
        
        repository = HealthDataRepositoryOptimized(async_session_factory, cache_service)
        
        quality_assessor = DataQualityAssessor(config['quality'])
        await quality_assessor.initialize()
        
        health_index_calculator = HealthIndexCalculator(config)
        await health_index_calculator.initialize()
        
        constitution_analyzer = TCMConstitutionAnalyzer(config)
        await constitution_analyzer.initialize()
        
        service = HealthDataServiceOptimized(
            repository=repository,
            cache_service=cache_service,
            quality_assessor=quality_assessor,
            health_index_calculator=health_index_calculator,
            constitution_analyzer=constitution_analyzer,
            performance_monitor=performance_monitor,
            config=config
        )
        await service.initialize()
        
        api_handler = HealthDataHandlerOptimized(service, cache_service)
        
        yield {
            'engine': engine,
            'service': service,
            'repository': repository,
            'cache_service': cache_service,
            'quality_assessor': quality_assessor,
            'health_index_calculator': health_index_calculator,
            'constitution_analyzer': constitution_analyzer,
            'performance_monitor': performance_monitor,
            'api_handler': api_handler,
            'config': config
        }
        
        # 清理
        await cache_service.cleanup()
        await performance_monitor.cleanup()
        await engine.dispose()
    
    @pytest.mark.asyncio
    async def test_basic_health_data_operations(self, setup_test_environment):
        """测试基本健康数据操作"""
        env = await setup_test_environment
        service = env['service']
        
        # 创建测试用户
        user_id = str(uuid.uuid4())
        
        # 创建健康数据
        health_data = HealthData(
            user_id=user_id,
            data_type=HealthDataType.HEART_RATE,
            value=75.0,
            unit=MeasurementUnit.BPM,
            device_type=DeviceType.SMARTWATCH,
            device_id="test_device_001",
            source="test",
            timestamp=datetime.utcnow(),
            metadata={"test": True}
        )
        
        # 保存数据
        record_id = await service.save_health_data(health_data)
        assert record_id is not None
        
        # 获取数据
        retrieved_record = await service.get_health_data_by_id(record_id)
        assert retrieved_record is not None
        assert retrieved_record.user_id == user_id
        assert retrieved_record.data_type == HealthDataType.HEART_RATE.value
        assert retrieved_record.value == 75.0
        
        # 更新数据
        updates = {"value": 80.0, "metadata": {"test": True, "updated": True}}
        success = await service.update_health_data(record_id, updates)
        assert success
        
        # 验证更新
        updated_record = await service.get_health_data_by_id(record_id)
        assert updated_record.value == 80.0
        assert updated_record.metadata["updated"] is True
        
        # 删除数据
        success = await service.delete_health_data(record_id)
        assert success
        
        # 验证删除
        deleted_record = await service.get_health_data_by_id(record_id)
        assert deleted_record is None
    
    @pytest.mark.asyncio
    async def test_batch_operations(self, setup_test_environment):
        """测试批量操作"""
        env = await setup_test_environment
        service = env['service']
        
        user_id = str(uuid.uuid4())
        
        # 创建批量健康数据
        health_data_list = []
        for i in range(50):
            health_data = HealthData(
                user_id=user_id,
                data_type=HealthDataType.HEART_RATE,
                value=70.0 + i,
                unit=MeasurementUnit.BPM,
                device_type=DeviceType.SMARTWATCH,
                device_id=f"test_device_{i:03d}",
                source="batch_test",
                timestamp=datetime.utcnow() - timedelta(minutes=i),
                metadata={"batch_index": i}
            )
            health_data_list.append(health_data)
        
        # 批量保存
        start_time = time.time()
        record_ids = await service.save_health_data_batch(health_data_list)
        batch_save_time = time.time() - start_time
        
        assert len(record_ids) == 50
        assert batch_save_time < 5.0  # 批量保存应该在5秒内完成
        
        # 获取用户数据
        records = await service.get_health_data(
            user_id=user_id,
            data_type=HealthDataType.HEART_RATE.value,
            limit=100
        )
        
        assert len(records) == 50
        
        # 验证数据顺序（应该按时间戳降序）
        for i in range(1, len(records)):
            assert records[i-1].timestamp >= records[i].timestamp
    
    @pytest.mark.asyncio
    async def test_data_quality_assessment(self, setup_test_environment):
        """测试数据质量评估"""
        env = await setup_test_environment
        service = env['service']
        quality_assessor = env['quality_assessor']
        
        user_id = str(uuid.uuid4())
        
        # 创建不同质量的健康数据
        test_data = [
            # 高质量数据
            HealthData(
                user_id=user_id,
                data_type=HealthDataType.HEART_RATE,
                value=75.0,
                unit=MeasurementUnit.BPM,
                device_type=DeviceType.SMARTWATCH,
                device_id="high_quality_device",
                source="medical_grade",
                timestamp=datetime.utcnow(),
                metadata={"calibrated": True, "accuracy": 0.95}
            ),
            # 中等质量数据
            HealthData(
                user_id=user_id,
                data_type=HealthDataType.HEART_RATE,
                value=72.0,
                unit=MeasurementUnit.BPM,
                device_type=DeviceType.SMARTPHONE,
                device_id="medium_quality_device",
                source="consumer_app",
                timestamp=datetime.utcnow(),
                metadata={"accuracy": 0.8}
            ),
            # 低质量数据
            HealthData(
                user_id=user_id,
                data_type=HealthDataType.HEART_RATE,
                value=200.0,  # 异常值
                unit=MeasurementUnit.BPM,
                device_type=DeviceType.MANUAL,
                device_id="manual_entry",
                source="user_input",
                timestamp=datetime.utcnow() - timedelta(days=1),  # 过时数据
                metadata={}
            )
        ]
        
        # 保存数据并评估质量
        for health_data in test_data:
            record_id = await service.save_health_data(health_data)
            record = await service.get_health_data_by_id(record_id)
            
            # 验证质量评分已计算
            assert record.quality_score is not None
            assert 0.0 <= record.quality_score <= 1.0
        
        # 获取数据质量指标
        quality_metrics = await service.get_data_quality_metrics(user_id=user_id)
        
        assert quality_metrics['total_count'] == 3
        assert quality_metrics['average_quality_score'] > 0.0
        assert quality_metrics['validation_rate'] >= 0.0
    
    @pytest.mark.asyncio
    async def test_health_index_calculation(self, setup_test_environment):
        """测试健康指数计算"""
        env = await setup_test_environment
        service = env['service']
        
        user_id = str(uuid.uuid4())
        
        # 创建完整的健康数据集
        health_data_list = [
            # 心率数据
            HealthData(
                user_id=user_id,
                data_type=HealthDataType.HEART_RATE,
                value=72.0,
                unit=MeasurementUnit.BPM,
                timestamp=datetime.utcnow() - timedelta(hours=i)
            ) for i in range(24)
        ] + [
            # 步数数据
            HealthData(
                user_id=user_id,
                data_type=HealthDataType.STEPS,
                value=8000 + i * 100,
                unit=MeasurementUnit.COUNT,
                timestamp=datetime.utcnow() - timedelta(hours=i)
            ) for i in range(24)
        ] + [
            # 睡眠数据
            HealthData(
                user_id=user_id,
                data_type=HealthDataType.SLEEP,
                value={"duration": 7.5, "quality": 85},
                timestamp=datetime.utcnow() - timedelta(days=i)
            ) for i in range(7)
        ] + [
            # 血压数据
            HealthData(
                user_id=user_id,
                data_type=HealthDataType.BLOOD_PRESSURE,
                value={"systolic": 120, "diastolic": 80},
                unit=MeasurementUnit.MMHG,
                timestamp=datetime.utcnow() - timedelta(days=i)
            ) for i in range(7)
        ]
        
        # 批量保存数据
        await service.save_health_data_batch(health_data_list)
        
        # 计算健康指数
        health_metrics = await service.calculate_health_index(user_id=user_id, days=7)
        
        assert health_metrics is not None
        assert 0.0 <= health_metrics.overall_score <= 100.0
        assert health_metrics.grade in ["优秀", "良好", "一般", "较差", "差"]
        assert len(health_metrics.recommendations) > 0
        
        # 验证各项指标
        assert 0.0 <= health_metrics.heart_rate_score <= 100.0
        assert 0.0 <= health_metrics.steps_score <= 100.0
        assert 0.0 <= health_metrics.sleep_score <= 100.0
        assert 0.0 <= health_metrics.blood_pressure_score <= 100.0
    
    @pytest.mark.asyncio
    async def test_tcm_constitution_analysis(self, setup_test_environment):
        """测试中医体质分析"""
        env = await setup_test_environment
        service = env['service']
        constitution_analyzer = env['constitution_analyzer']
        
        user_id = str(uuid.uuid4())
        
        # 创建符合特定体质特征的健康数据
        # 模拟气虚质特征：心率偏慢、血压偏低、活动量少
        health_data_list = [
            # 心率偏慢
            HealthData(
                user_id=user_id,
                data_type=HealthDataType.HEART_RATE,
                value=60.0,  # 偏慢
                unit=MeasurementUnit.BPM,
                timestamp=datetime.utcnow() - timedelta(hours=i)
            ) for i in range(24)
        ] + [
            # 血压偏低
            HealthData(
                user_id=user_id,
                data_type=HealthDataType.BLOOD_PRESSURE,
                value={"systolic": 100, "diastolic": 65},  # 偏低
                unit=MeasurementUnit.MMHG,
                timestamp=datetime.utcnow() - timedelta(days=i)
            ) for i in range(7)
        ] + [
            # 活动量少
            HealthData(
                user_id=user_id,
                data_type=HealthDataType.STEPS,
                value=5000,  # 偏少
                unit=MeasurementUnit.COUNT,
                timestamp=datetime.utcnow() - timedelta(days=i)
            ) for i in range(7)
        ] + [
            # 睡眠时间长但质量不高
            HealthData(
                user_id=user_id,
                data_type=HealthDataType.SLEEP,
                value={"duration": 9.0, "quality": 60},
                timestamp=datetime.utcnow() - timedelta(days=i)
            ) for i in range(7)
        ]
        
        # 批量保存数据
        await service.save_health_data_batch(health_data_list)
        
        # 获取健康数据进行体质分析
        records = await service.get_health_data(user_id=user_id, limit=1000)
        health_data_objects = []
        
        for record in records:
            health_data = HealthData(
                user_id=record.user_id,
                data_type=HealthDataType(record.data_type),
                value=record.value,
                unit=MeasurementUnit(record.unit) if record.unit else None,
                device_type=DeviceType(record.device_type) if record.device_type else None,
                device_id=record.device_id,
                source=record.source,
                timestamp=record.timestamp,
                metadata=record.metadata or {}
            )
            health_data_objects.append(health_data)
        
        # 进行体质分析
        constitution_analysis = await constitution_analyzer.analyze_constitution(
            user_id=user_id,
            health_data_list=health_data_objects,
            days=30
        )
        
        assert constitution_analysis is not None
        assert constitution_analysis.primary_constitution is not None
        assert constitution_analysis.primary_constitution.score > 0.0
        assert constitution_analysis.primary_constitution.constitution_type in [
            "平和质", "气虚质", "阳虚质", "阴虚质", "痰湿质", 
            "湿热质", "血瘀质", "气郁质", "特禀质"
        ]
        assert len(constitution_analysis.primary_constitution.recommendations) > 0
        assert 0.0 <= constitution_analysis.reliability <= 1.0
    
    @pytest.mark.asyncio
    async def test_caching_performance(self, setup_test_environment):
        """测试缓存性能"""
        env = await setup_test_environment
        service = env['service']
        cache_service = env['cache_service']
        
        user_id = str(uuid.uuid4())
        
        # 创建测试数据
        health_data = HealthData(
            user_id=user_id,
            data_type=HealthDataType.HEART_RATE,
            value=75.0,
            unit=MeasurementUnit.BPM,
            timestamp=datetime.utcnow()
        )
        
        record_id = await service.save_health_data(health_data)
        
        # 第一次查询（应该从数据库获取）
        start_time = time.time()
        record1 = await service.get_health_data_by_id(record_id)
        first_query_time = time.time() - start_time
        
        # 第二次查询（应该从缓存获取）
        start_time = time.time()
        record2 = await service.get_health_data_by_id(record_id)
        second_query_time = time.time() - start_time
        
        # 验证缓存效果
        assert record1.id == record2.id
        assert second_query_time < first_query_time  # 缓存查询应该更快
        
        # 验证缓存统计
        cache_stats = cache_service.get_stats()
        assert cache_stats['hits'] > 0
    
    @pytest.mark.asyncio
    async def test_error_handling(self, setup_test_environment):
        """测试错误处理"""
        env = await setup_test_environment
        service = env['service']
        
        # 测试无效的记录ID
        invalid_id = uuid.uuid4()
        record = await service.get_health_data_by_id(invalid_id)
        assert record is None
        
        # 测试更新不存在的记录
        success = await service.update_health_data(invalid_id, {"value": 100.0})
        assert not success
        
        # 测试删除不存在的记录
        success = await service.delete_health_data(invalid_id)
        assert not success
        
        # 测试无效的用户ID查询
        records = await service.get_health_data(user_id="invalid_user_id")
        assert len(records) == 0
    
    @pytest.mark.asyncio
    async def test_performance_monitoring(self, setup_test_environment):
        """测试性能监控"""
        env = await setup_test_environment
        performance_monitor = env['performance_monitor']
        
        # 启动监控
        performance_monitor.start_monitoring()
        
        # 模拟API请求
        performance_monitor.record_api_request(
            endpoint="/health-data",
            method="POST",
            response_time=0.1,
            is_error=False
        )
        
        performance_monitor.record_api_request(
            endpoint="/health-data",
            method="GET",
            response_time=0.05,
            is_error=False
        )
        
        # 模拟数据库查询
        performance_monitor.record_database_query(0.02, is_slow=False, is_error=False)
        performance_monitor.record_database_query(1.5, is_slow=True, is_error=False)
        
        # 模拟缓存操作
        performance_monitor.record_cache_operation("get", hit=True)
        performance_monitor.record_cache_operation("get", hit=False)
        performance_monitor.record_cache_operation("set")
        
        # 获取指标摘要
        api_summary = performance_monitor.get_api_metrics_summary()
        db_summary = performance_monitor.get_database_metrics_summary()
        cache_summary = performance_monitor.get_cache_metrics_summary()
        
        # 验证API指标
        assert len(api_summary) > 0
        for endpoint_metrics in api_summary.values():
            assert endpoint_metrics['request_count'] > 0
            assert endpoint_metrics['avg_response_time'] > 0
        
        # 验证数据库指标
        assert db_summary['query_count'] == 2
        assert db_summary['slow_query_count'] == 1
        assert db_summary['avg_query_time'] > 0
        
        # 验证缓存指标
        assert cache_summary['hit_count'] == 1
        assert cache_summary['miss_count'] == 1
        assert cache_summary['set_count'] == 1
        assert cache_summary['hit_rate'] == 50.0
        
        # 获取健康状态
        health_status = performance_monitor.get_health_status()
        assert health_status['status'] in ['healthy', 'warning', 'critical', 'unknown']
        
        # 停止监控
        performance_monitor.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, setup_test_environment):
        """测试并发操作"""
        env = await setup_test_environment
        service = env['service']
        
        user_id = str(uuid.uuid4())
        
        async def create_health_data(index: int):
            """创建健康数据的协程"""
            health_data = HealthData(
                user_id=user_id,
                data_type=HealthDataType.HEART_RATE,
                value=70.0 + index,
                unit=MeasurementUnit.BPM,
                device_id=f"device_{index}",
                timestamp=datetime.utcnow(),
                metadata={"index": index}
            )
            return await service.save_health_data(health_data)
        
        # 并发创建100个健康数据记录
        start_time = time.time()
        tasks = [create_health_data(i) for i in range(100)]
        record_ids = await asyncio.gather(*tasks)
        concurrent_time = time.time() - start_time
        
        # 验证所有记录都创建成功
        assert len(record_ids) == 100
        assert all(record_id is not None for record_id in record_ids)
        assert concurrent_time < 10.0  # 并发操作应该在10秒内完成
        
        # 验证数据完整性
        records = await service.get_health_data(user_id=user_id, limit=200)
        assert len(records) == 100
        
        # 验证数据唯一性
        record_ids_set = set(str(record.id) for record in records)
        assert len(record_ids_set) == 100
    
    @pytest.mark.asyncio
    async def test_data_statistics(self, setup_test_environment):
        """测试数据统计功能"""
        env = await setup_test_environment
        service = env['service']
        
        user_id = str(uuid.uuid4())
        
        # 创建一周的心率数据
        heart_rate_values = [70, 72, 68, 75, 73, 71, 69]
        health_data_list = []
        
        for i, value in enumerate(heart_rate_values):
            health_data = HealthData(
                user_id=user_id,
                data_type=HealthDataType.HEART_RATE,
                value=float(value),
                unit=MeasurementUnit.BPM,
                timestamp=datetime.utcnow() - timedelta(days=i)
            )
            health_data_list.append(health_data)
        
        await service.save_health_data_batch(health_data_list)
        
        # 获取统计信息
        stats = await service.get_health_data_statistics(
            user_id=user_id,
            data_type=HealthDataType.HEART_RATE.value,
            start_time=datetime.utcnow() - timedelta(days=7),
            end_time=datetime.utcnow()
        )
        
        assert stats is not None
        assert stats['count'] == 7
        assert stats['average'] == sum(heart_rate_values) / len(heart_rate_values)
        assert stats['min'] == min(heart_rate_values)
        assert stats['max'] == max(heart_rate_values)
        assert 'std_dev' in stats
        
        # 获取用户数据摘要
        summary = await service.get_user_data_summary(user_id=user_id, days=7)
        
        assert summary is not None
        assert 'total_records' in summary
        assert 'data_types' in summary
        assert 'date_range' in summary
        assert summary['total_records'] == 7


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--asyncio-mode=auto"]) 