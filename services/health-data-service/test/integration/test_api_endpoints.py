#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API端点集成测试
"""

import unittest
import uuid
import json
import asyncio
from datetime import datetime, timedelta
from unittest import mock
from unittest.mock import MagicMock, AsyncMock, patch

import httpx
from fastapi.testclient import TestClient

from internal.delivery.rest.app import create_app
from internal.service.health_data_service import HealthDataService
from internal.model.health_data import (
    HealthData, HealthDataType, TCMConstitutionData, DeviceType, MeasurementUnit
)


class TestApiEndpoints(unittest.TestCase):
    """API端点测试类"""

    @classmethod
    def setUpClass(cls):
        """测试前设置"""
        # 测试配置
        cls.config = {
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
                'enabled': False,  # 禁用区块链
                'service_url': 'http://localhost:8080',
                'timeout': 10
            },
            'analytics': {
                'time_series': {},
                'correlation': {},
                'health_index': {}
            },
            'cors': {
                'allow_origins': ['*'],
                'allow_credentials': True,
                'allow_methods': ['*'],
                'allow_headers': ['*']
            },
            'wearable_data': {
                'supported_devices': []
            }
        }
        
        # 创建模拟服务
        with patch('sqlalchemy.ext.asyncio.create_async_engine'):
            with patch('sqlalchemy.orm.sessionmaker'):
                cls.service = HealthDataService(cls.config)
                cls.service.is_initialized = True
                
                # 创建测试客户端
                cls.app = create_app(cls.config, cls.service)
                cls.client = TestClient(cls.app)

    def setUp(self):
        """每个测试前设置"""
        self.user_id = str(uuid.uuid4())
        self.headers = {"X-User-ID": self.user_id}

    def test_health_check_endpoint(self):
        """测试健康检查端点"""
        # 模拟健康检查方法
        with patch.object(self.service, 'health_check', AsyncMock(return_value=("ok", {"ready": True}))):
            # 发送请求
            response = self.client.get("/health")
            
            # 验证响应
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "ok")
            self.assertTrue(data["details"]["ready"])

    def test_get_health_data_endpoint(self):
        """测试获取健康数据端点"""
        # 创建测试数据
        test_health_data = [
            HealthData(
                id=uuid.uuid4(),
                user_id=uuid.UUID(self.user_id),
                data_type=HealthDataType.HEART_RATE,
                timestamp=datetime.utcnow(),
                device_type=DeviceType.APPLE_HEALTH,
                device_id="test_device_id",
                value=75,
                unit=MeasurementUnit.BPM,
                source="test",
                metadata={"test_key": "test_value"}
            )
        ]
        
        # 模拟获取数据方法
        with patch.object(self.service, 'get_health_data', AsyncMock(return_value=test_health_data)):
            # 发送请求
            response = self.client.get(
                "/api/v1/health-data",
                headers=self.headers,
                params={"data_type": "heart_rate", "limit": 10, "offset": 0}
            )
            
            # 验证响应
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("results", data)
            self.assertEqual(len(data["results"]), 1)
            self.assertEqual(data["results"][0]["data_type"], "heart_rate")
            self.assertEqual(data["results"][0]["value"], 75)

    def test_create_health_data_endpoint(self):
        """测试创建健康数据端点"""
        # 测试数据
        test_data = {
            "data_type": "heart_rate",
            "timestamp": datetime.utcnow().isoformat(),
            "device_type": "apple_health",
            "device_id": "test_device_id",
            "value": 75,
            "unit": "bpm",
            "source": "test",
            "metadata": {"test_key": "test_value"}
        }
        
        # 模拟保存数据方法
        with patch.object(self.service, 'save_health_data', AsyncMock(return_value=str(uuid.uuid4()))):
            # 发送请求
            response = self.client.post(
                "/api/v1/health-data",
                headers=self.headers,
                json=test_data
            )
            
            # 验证响应
            self.assertEqual(response.status_code, 201)
            data = response.json()
            self.assertIn("id", data)
            self.assertTrue(uuid.UUID(data["id"]))

    def test_get_health_statistics_endpoint(self):
        """测试获取健康数据统计端点"""
        # 模拟统计结果
        mock_stats = {
            "average": 75.5,
            "maximum": 90.0,
            "minimum": 60.0,
            "count": 100,
            "start_time": (datetime.utcnow() - timedelta(days=30)).isoformat(),
            "end_time": datetime.utcnow().isoformat(),
            "data_type": "heart_rate"
        }
        
        # 模拟获取统计方法
        with patch.object(self.service, 'get_health_statistics', AsyncMock(return_value=mock_stats)):
            # 发送请求
            response = self.client.get(
                "/api/v1/health-data/statistics",
                headers=self.headers,
                params={"data_type": "heart_rate", "days": 30}
            )
            
            # 验证响应
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["average"], 75.5)
            self.assertEqual(data["maximum"], 90.0)
            self.assertEqual(data["data_type"], "heart_rate")

    def test_get_tcm_constitution_endpoint(self):
        """测试获取中医体质端点"""
        # 创建测试数据
        test_constitution = TCMConstitutionData(
            id=uuid.uuid4(),
            user_id=uuid.UUID(self.user_id),
            timestamp=datetime.utcnow(),
            primary_type="balanced",
            secondary_types=["qi_deficiency"],
            scores={"balanced": 80, "qi_deficiency": 60},
            analysis_basis={"source": "test"},
            recommendations={"diet": ["多吃水果"]},
            created_by="test"
        )
        
        # 模拟获取中医体质方法
        with patch.object(self.service, 'get_latest_tcm_constitution', AsyncMock(return_value=test_constitution)):
            # 发送请求
            response = self.client.get(
                "/api/v1/tcm/constitution",
                headers=self.headers
            )
            
            # 验证响应
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["primary_type"], "balanced")
            self.assertEqual(data["secondary_types"], ["qi_deficiency"])
            self.assertEqual(data["scores"]["balanced"], 80)

    def test_get_insights_endpoint(self):
        """测试获取健康洞察端点"""
        # 创建测试数据
        from internal.model.health_data import HealthInsight
        test_insights = [
            HealthInsight(
                id=uuid.uuid4(),
                user_id=uuid.UUID(self.user_id),
                timestamp=datetime.utcnow(),
                insight_type="trend",
                data_type=HealthDataType.HEART_RATE,
                time_range={"start": datetime.utcnow() - timedelta(days=7), "end": datetime.utcnow()},
                description="心率呈上升趋势",
                details={"trend_direction": "up", "change_percent": 5},
                severity="info",
                relevance_score=0.8
            )
        ]
        
        # 模拟获取洞察方法
        with patch.object(self.service, 'get_health_insights', AsyncMock(return_value=test_insights)):
            # 发送请求
            response = self.client.get(
                "/api/v1/insights",
                headers=self.headers,
                params={"insight_type": "trend", "limit": 10}
            )
            
            # 验证响应
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("results", data)
            self.assertEqual(len(data["results"]), 1)
            self.assertEqual(data["results"][0]["insight_type"], "trend")
            self.assertEqual(data["results"][0]["data_type"], "heart_rate")
            self.assertEqual(data["results"][0]["description"], "心率呈上升趋势")

    def test_process_wearable_data_endpoint(self):
        """测试处理可穿戴设备数据端点"""
        # 模拟处理结果
        mock_result = {
            "device_type": "apple_health",
            "processed_items": 10,
            "data_types": {"heart_rate": 5, "steps": 5},
            "time_range": {
                "start": (datetime.utcnow() - timedelta(days=1)).isoformat(),
                "end": datetime.utcnow().isoformat()
            }
        }
        
        # 模拟处理数据方法
        with patch.object(self.service, 'process_wearable_data', AsyncMock(return_value=mock_result)):
            # 创建测试文件数据
            files = {
                'file': ('test.xml', b'<HealthData>test</HealthData>', 'application/xml')
            }
            
            # 发送请求
            response = self.client.post(
                "/api/v1/wearables/process",
                headers=self.headers,
                files=files,
                data={"device_type": "apple_health"}
            )
            
            # 验证响应
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["device_type"], "apple_health")
            self.assertEqual(data["processed_items"], 10)
            self.assertEqual(data["data_types"]["heart_rate"], 5)


if __name__ == '__main__':
    unittest.main() 