#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
健康数据服务单元测试
"""

import unittest
import uuid
import asyncio
from datetime import datetime, timedelta
from unittest import mock
from unittest.mock import MagicMock, AsyncMock, patch

from internal.service.health_data_service import HealthDataService
from internal.model.health_data import (
    HealthData, HealthDataType, TCMConstitutionData, DeviceType, MeasurementUnit
)


class TestHealthDataService(unittest.TestCase):
    """健康数据服务测试类"""

    def setUp(self):
        """测试前设置"""
        self.config = {
            'database': {
                'dialect': 'postgresql',
                'driver': 'asyncpg',
                'host': 'localhost',
                'port': 5432,
                'username': 'test',
                'password': 'test',
                'database': 'test_health_data',
                'pool_size': 5,
                'max_overflow': 10
            },
            'blockchain': {
                'enabled': True,
                'service_url': 'http://localhost:8080',
                'timeout': 10
            },
            'analytics': {
                'time_series': {},
                'correlation': {},
                'health_index': {}
            },
            'wearable_data': {
                'supported_devices': [
                    {
                        'name': 'apple_health',
                        'parser': 'apple_health_xml_parser'
                    },
                    {
                        'name': 'fitbit',
                        'parser': 'fitbit_json_parser'
                    }
                ]
            }
        }
        
        # 使用异步循环运行测试
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        # 模拟数据库会话工厂
        self.mock_session_factory = MagicMock()
        self.mock_session = AsyncMock()
        self.mock_session_factory.return_value.__aenter__.return_value = self.mock_session
        
        # 创建测试服务
        with patch('sqlalchemy.ext.asyncio.create_async_engine'):
            with patch('sqlalchemy.orm.sessionmaker', return_value=self.mock_session_factory):
                self.service = HealthDataService(self.config)
                # 手动设置会话工厂，避免真实数据库连接
                self.service.session_factory = self.mock_session_factory
                self.service.is_initialized = True

    def tearDown(self):
        """测试后清理"""
        self.loop.close()

    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.service.config, self.config)
        self.assertTrue(self.service.is_initialized)

    def test_create_health_data(self):
        """测试创建健康数据"""
        # 创建健康数据对象
        user_id = uuid.uuid4()
        health_data = HealthData(
            user_id=user_id,
            data_type=HealthDataType.HEART_RATE,
            timestamp=datetime.utcnow(),
            device_type=DeviceType.APPLE_HEALTH,
            device_id="test_device_id",
            value=75,
            unit=MeasurementUnit.BPM,
            source="test",
            metadata={"test_key": "test_value"}
        )
        
        # 模拟数据库操作
        mock_record = MagicMock()
        mock_record.id = uuid.uuid4()
        self.mock_session.commit = AsyncMock()
        
        # 模拟 HealthDataRepository.save_health_data 方法
        with patch('internal.repository.health_data_repository.HealthDataRepository.save_health_data', 
                  AsyncMock(return_value=mock_record)):
            # 模拟区块链客户端
            with patch.object(self.service, 'blockchain_client', AsyncMock()) as mock_blockchain:
                mock_blockchain._save_to_blockchain = AsyncMock(return_value="test_transaction_hash")
                
                # 执行测试
                result = self.loop.run_until_complete(self.service.save_health_data(health_data))
                
                # 验证结果
                self.assertEqual(result, str(mock_record.id))

    def test_get_health_data(self):
        """测试获取健康数据"""
        # 创建测试数据
        user_id = uuid.uuid4()
        
        # 模拟 HealthDataRepository.get_health_data 方法返回的数据
        mock_records = [
            MagicMock(
                id=uuid.uuid4(),
                user_id=user_id,
                data_type=HealthDataType.HEART_RATE.value,
                timestamp=datetime.utcnow(),
                device_type=DeviceType.APPLE_HEALTH.value,
                device_id="test_device_id",
                value={"value": 75},
                unit=MeasurementUnit.BPM.value,
                source="test",
                metadata={"test_key": "test_value"}
            )
        ]
        
        # 模拟数据库操作
        with patch('internal.repository.health_data_repository.HealthDataRepository.get_health_data', 
                  AsyncMock(return_value=mock_records)):
            # 执行测试
            result = self.loop.run_until_complete(
                self.service.get_health_data(
                    user_id=user_id,
                    data_type=HealthDataType.HEART_RATE,
                    start_time=datetime.utcnow() - timedelta(days=7),
                    end_time=datetime.utcnow(),
                    limit=10,
                    offset=0
                )
            )
            
            # 验证结果
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].data_type, HealthDataType.HEART_RATE)
            self.assertEqual(result[0].user_id, user_id)

    def test_get_health_statistics(self):
        """测试获取健康数据统计"""
        # 创建测试数据
        user_id = uuid.uuid4()
        
        # 模拟统计结果
        mock_stats = {
            "average": 75.5,
            "maximum": 90.0,
            "minimum": 60.0,
            "count": 100,
            "start_time": datetime.utcnow() - timedelta(days=30),
            "end_time": datetime.utcnow(),
            "data_type": HealthDataType.HEART_RATE.value
        }
        
        # 模拟数据库操作
        with patch('internal.repository.health_data_repository.HealthDataRepository.get_health_data_statistics', 
                  AsyncMock(return_value=mock_stats)):
            # 执行测试
            result = self.loop.run_until_complete(
                self.service.get_health_statistics(
                    user_id=user_id,
                    data_type=HealthDataType.HEART_RATE,
                    days=30
                )
            )
            
            # 验证结果
            self.assertEqual(result["average"], 75.5)
            self.assertEqual(result["maximum"], 90.0)
            self.assertEqual(result["data_type"], HealthDataType.HEART_RATE.value)

    def test_get_latest_tcm_constitution(self):
        """测试获取最新中医体质"""
        # 创建测试数据
        user_id = uuid.uuid4()
        
        # 模拟 TCMConstitution 记录
        from internal.model.database import TCMConstitution
        mock_constitution = MagicMock(spec=TCMConstitution)
        mock_constitution.id = uuid.uuid4()
        mock_constitution.user_id = user_id
        mock_constitution.timestamp = datetime.utcnow()
        mock_constitution.primary_type = "balanced"
        mock_constitution.secondary_types = ["qi_deficiency"]
        mock_constitution.scores = {"balanced": 80, "qi_deficiency": 60}
        mock_constitution.analysis_basis = {"source": "test"}
        mock_constitution.recommendations = {"diet": ["多吃水果"]}
        mock_constitution.created_by = "test"
        mock_constitution.created_at = datetime.utcnow()
        mock_constitution.updated_at = datetime.utcnow()
        
        # 模拟数据库操作
        with patch('internal.repository.health_data_repository.HealthDataRepository.get_latest_tcm_constitution', 
                  AsyncMock(return_value=mock_constitution)):
            # 执行测试
            result = self.loop.run_until_complete(
                self.service.get_latest_tcm_constitution(user_id)
            )
            
            # 验证结果
            self.assertIsNotNone(result)
            self.assertEqual(result.user_id, user_id)
            self.assertEqual(result.primary_type.value, "balanced")

    def test_process_wearable_data(self):
        """测试处理可穿戴设备数据"""
        # 创建测试数据
        user_id = uuid.uuid4()
        device_type = DeviceType.APPLE_HEALTH
        test_data = "<HealthData>test</HealthData>"
        
        # 模拟解析器
        mock_parser = AsyncMock()
        mock_parser.parse = AsyncMock(return_value=[
            {
                "data_type": HealthDataType.HEART_RATE,
                "timestamp": datetime.utcnow(),
                "value": 75,
                "unit": MeasurementUnit.BPM,
                "device_id": "test_device_id",
                "metadata": {}
            }
        ])
        
        # 模拟批量保存方法
        with patch.object(self.service, 'save_health_data_batch', AsyncMock(return_value=["test_id"])):
            # 模拟解析器注册
            self.service.wearable_parsers = {
                "apple_health_xml_parser": mock_parser
            }
            
            # 执行测试
            result = self.loop.run_until_complete(
                self.service.process_wearable_data(
                    user_id=user_id,
                    device_type=device_type,
                    data=test_data,
                    source="test"
                )
            )
            
            # 验证结果
            self.assertEqual(result["device_type"], device_type.value)
            self.assertEqual(result["processed_items"], 1)
            self.assertEqual(list(result["data_types"].keys())[0], HealthDataType.HEART_RATE.value)

    def test_health_check(self):
        """测试健康检查"""
        # 执行测试
        result = self.loop.run_until_complete(self.service.health_check())
        
        # 验证结果
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "SERVING")
        self.assertIsInstance(result[1], dict)


if __name__ == '__main__':
    unittest.main() 