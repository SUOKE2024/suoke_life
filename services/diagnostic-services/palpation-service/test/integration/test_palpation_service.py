#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
切诊服务集成测试
测试服务的完整功能流程
"""

import unittest
import sys
import os
import time
import grpc
import json
import logging
import uuid
from concurrent import futures
from pathlib import Path
from unittest.mock import MagicMock, patch
import numpy as np

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# 导入服务相关模块
from api.grpc import palpation_service_pb2 as pb2
from api.grpc import palpation_service_pb2_grpc as pb2_grpc
from internal.delivery.palpation_service_impl import PalpationServiceImpl, PalpationServiceServicer
from internal.repository.session_repository import SessionRepository
from internal.repository.user_repository import UserRepository
from internal.signal.pulse_processor import PulseProcessor
from internal.signal.abdominal_analyzer import AbdominalAnalyzer
from internal.signal.skin_analyzer import SkinAnalyzer

class TestPalpationServiceIntegration(unittest.TestCase):
    """切诊服务集成测试"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        # 加载测试配置
        cls.config = {
            'pulse_analysis': {
                'sampling_rate': 100,
                'window_size': 5,
                'feature_extraction': {
                    'time_domain': True,
                    'frequency_domain': True,
                    'wavelet_domain': True
                }
            },
            'abdominal_analysis': {
                'region_mappings': [
                    {'id': 'right_top', 'name': '右上腹', 'organs': ['liver', 'gallbladder']}
                ]
            },
            'skin_analysis': {
                'region_mappings': [
                    {'id': 'face', 'name': '面部', 'related_organs': ['lung', 'heart']}
                ]
            },
            'devices': {
                'supported_models': [
                    {
                        'model': 'TEST_MODEL',
                        'sampling_rate': 1000,
                        'sampling_duration': 30
                    }
                ]
            }
        }
        
        # 创建模拟数据库仓库
        cls.mock_session_repo = MagicMock(spec=SessionRepository)
        cls.mock_user_repo = MagicMock(spec=UserRepository)
        
        # 配置模拟仓库的行为
        cls.mock_user_repo.get_user.return_value = {'user_id': 'test_user', 'name': '测试用户'}
        cls.stored_session = None
        
        def mock_create_session(session_id, data):
            cls.stored_session = data
            return True
            
        def mock_get_session(session_id):
            if cls.stored_session and cls.stored_session.get('session_id') == session_id:
                return cls.stored_session
            return None
        
        def mock_update_session(session_id, data):
            if cls.stored_session and cls.stored_session.get('session_id') == session_id:
                cls.stored_session = data
                return True
            return False
            
        cls.mock_session_repo.create_session.side_effect = mock_create_session
        cls.mock_session_repo.get_session.side_effect = mock_get_session
        cls.mock_session_repo.update_session.side_effect = mock_update_session
        
        # 创建服务实现
        cls.service = PalpationServiceImpl(
            config=cls.config,
            session_repository=cls.mock_session_repo,
            user_repository=cls.mock_user_repo
        )
        
        # 创建gRPC服务器
        cls.server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
        pb2_grpc.add_PalpationServiceServicer_to_server(cls.service, cls.server)
        cls.port = 50099
        cls.server.add_insecure_port(f'[::]:{cls.port}')
        cls.server.start()
        
        # 创建gRPC客户端
        cls.channel = grpc.insecure_channel(f'localhost:{cls.port}')
        cls.client = pb2_grpc.PalpationServiceStub(cls.channel)
    
    @classmethod
    def tearDownClass(cls):
        """清理测试环境"""
        cls.channel.close()
        cls.server.stop(0)
    
    def setUp(self):
        """每个测试前准备"""
        self.__class__.stored_session = None
    
    def test_full_analysis_flow(self):
        """测试完整的分析流程"""
        # 步骤1: 启动脉诊会话
        session_response = self.client.StartPulseSession(pb2.StartPulseSessionRequest(
            user_id='test_user',
            device_info=pb2.DeviceInfo(
                device_id='device123',
                model='TEST_MODEL',
                firmware_version='v1.0',
                sensor_types=['pressure', 'temperature']
            ),
            calibration_data=pb2.SensorCalibrationData(
                calibration_values=[1.0, 1.1, 1.0],
                calibration_timestamp=int(time.time()),
                calibration_operator='auto'
            )
        ))
        
        # 验证会话创建成功
        self.assertTrue(session_response.success)
        self.assertNotEqual(session_response.session_id, '')
        session_id = session_response.session_id
        
        # 步骤2: 记录脉诊数据
        # 创建模拟脉搏数据
        pulse_data_packets = []
        
        for i in range(5):
            # 创建正弦波形模拟脉搏
            import math
            import numpy as np
            time_points = np.linspace(0, 2*math.pi, 100)
            pressure_data = [math.sin(t) + 1 for t in time_points]  # 范围 0-2
            velocity_data = [math.cos(t) for t in time_points]
            
            packet = pb2.PulseDataPacket(
                session_id=session_id,
                timestamp=int(time.time()) + i,
                pressure_data=pressure_data,
                velocity_data=velocity_data,
                position=i % 6 + 1,  # 轮换六个脉位
                skin_temperature=36.5,
                skin_moisture=0.7
            )
            pulse_data_packets.append(packet)
        
        # 发送数据包
        record_response = self.client.RecordPulseData(iter(pulse_data_packets))
        
        # 验证数据记录成功
        self.assertTrue(record_response.success)
        self.assertEqual(record_response.packets_received, len(pulse_data_packets))
        
        # 步骤3: 提取脉象特征
        extract_response = self.client.ExtractPulseFeatures(pb2.ExtractPulseFeaturesRequest(
            session_id=session_id,
            include_raw_data=False
        ))
        
        # 验证特征提取成功
        self.assertTrue(extract_response.success)
        self.assertTrue(len(extract_response.features) > 0)
        
        # 步骤4: 分析脉象
        analyze_response = self.client.AnalyzePulse(pb2.AnalyzePulseRequest(
            session_id=session_id,
            user_id='test_user',
            include_detailed_analysis=True,
            options=pb2.AnalysisOptions(
                use_tcm_model=True,
                use_western_model=False,
                analysis_depth='detailed'
            )
        ))
        
        # 验证脉象分析成功
        self.assertTrue(analyze_response.success)
        
        # 步骤5: 腹诊分析
        abdominal_data = [pb2.AbdominalRegionData(
            region_id='right_top',
            region_name='右上腹',
            tenderness_level=0.7,
            tension_level=0.6,
            has_mass=False,
            texture_description='稍硬',
            comments='轻度压痛'
        )]
        
        abdominal_response = self.client.AnalyzeAbdominalPalpation(pb2.AbdominalPalpationRequest(
            user_id='test_user',
            regions=abdominal_data,
            include_detailed_analysis=True
        ))
        
        # 验证腹诊分析成功
        self.assertTrue(abdominal_response.success)
        self.assertTrue(len(abdominal_response.findings) > 0)
        
        # 步骤6: 皮肤触诊分析
        skin_data = [pb2.SkinRegionData(
            region_id='face',
            region_name='面部',
            moisture_level=0.4,
            elasticity=0.6,
            texture='正常',
            temperature=36.8,
            color='正常'
        )]
        
        skin_response = self.client.AnalyzeSkinPalpation(pb2.SkinPalpationRequest(
            user_id='test_user',
            regions=skin_data
        ))
        
        # 验证皮肤触诊分析成功
        self.assertTrue(skin_response.success)
        
        # 步骤7: 获取综合分析
        comprehensive_response = self.client.GetComprehensivePalpationAnalysis(pb2.ComprehensiveAnalysisRequest(
            user_id='test_user',
            pulse_session_id=session_id,
            include_abdominal=True,
            include_skin=True
        ))
        
        # 验证综合分析成功
        self.assertTrue(comprehensive_response.success)
        self.assertNotEqual(comprehensive_response.summary, '')
        
        # 验证结果包含所有切诊方法的分析
        self.assertTrue(hasattr(comprehensive_response.overview, 'pulse'))
        self.assertTrue(hasattr(comprehensive_response.overview, 'abdominal'))
        self.assertTrue(hasattr(comprehensive_response.overview, 'skin'))

class HealthCheckTests(unittest.TestCase):
    """健康检查接口测试"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        # 加载测试配置
        test_config_path = Path(__file__).resolve().parents[1] / "data" / "test_config.json"
        if test_config_path.exists():
            with open(test_config_path, 'r', encoding='utf-8') as f:
                cls.config = json.load(f)
        else:
            # 使用默认测试配置
            cls.config = {
                "server": {"port": 50053, "max_workers": 5},
                "database": {"type": "mongodb", "connection_string": "mongodb://localhost:27017", "name": "palpation_test_db"},
                "pulse_analysis": {"model_path": "./test/data/dummy_model", "confidence_threshold": 0.6},
                "abdominal_analysis": {"model_path": "./test/data/dummy_model", "confidence_threshold": 0.6},
                "skin_analysis": {"model_path": "./test/data/dummy_model", "confidence_threshold": 0.6}
            }
        
        # 创建服务器
        cls.server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
        
        # 初始化仓库和处理器
        cls.session_repo = SessionRepository(cls.config.get('database', {}))
        cls.user_repo = UserRepository(cls.config.get('database', {}))
        cls.pulse_processor = PulseProcessor(cls.config.get('pulse_analysis', {}))
        cls.abdominal_analyzer = AbdominalAnalyzer(cls.config.get('abdominal_analysis', {}))
        cls.skin_analyzer = SkinAnalyzer(cls.config.get('skin_analysis', {}))
        
        # 创建服务实现
        cls.servicer = PalpationServiceServicer(
            session_repository=cls.session_repo,
            user_repository=cls.user_repo,
            pulse_processor=cls.pulse_processor,
            abdominal_analyzer=cls.abdominal_analyzer,
            skin_analyzer=cls.skin_analyzer,
            config=cls.config
        )
        
        # 注册服务
        pb2_grpc.add_PalpationServiceServicer_to_server(cls.servicer, cls.server)
        
        # 选择随机端口
        cls.port = 50055 + np.random.randint(100)
        cls.server.add_insecure_port(f'[::]:{cls.port}')
        cls.server.start()
        
        # 创建客户端通道
        cls.channel = grpc.insecure_channel(f'localhost:{cls.port}')
        cls.stub = pb2_grpc.PalpationServiceStub(cls.channel)
        
        logging.info(f"集成测试服务器启动，端口: {cls.port}")
    
    @classmethod
    def tearDownClass(cls):
        """清理测试环境"""
        cls.channel.close()
        cls.server.stop(grace=0)
        logging.info("集成测试服务器已关闭")
    
    def test_minimal_health_check(self):
        """测试最小级别健康检查"""
        request = pb2.HealthCheckRequest(
            level=pb2.HealthCheckRequest.HealthCheckLevel.MINIMAL
        )
        
        response = self.stub.HealthCheck(request)
        
        self.assertEqual(response.status, pb2.HealthCheckResponse.ServiceStatus.SERVING)
        self.assertTrue(len(response.components) >= 1)
        self.assertIsNotNone(response.version)
        self.assertGreater(response.timestamp, 0)
        
        # 验证组件信息
        service_component = next((c for c in response.components if c.component_name == "palpation_service"), None)
        self.assertIsNotNone(service_component)
        self.assertEqual(service_component.status, pb2.HealthCheckResponse.ServiceStatus.SERVING)
    
    def test_basic_health_check(self):
        """测试基础级别健康检查"""
        request = pb2.HealthCheckRequest(
            level=pb2.HealthCheckRequest.HealthCheckLevel.BASIC
        )
        
        response = self.stub.HealthCheck(request)
        
        self.assertEqual(response.status, pb2.HealthCheckResponse.ServiceStatus.SERVING)
        self.assertTrue(len(response.components) >= 2)
        
        # 验证数据库组件信息
        db_component = next((c for c in response.components if c.component_name == "database"), None)
        self.assertIsNotNone(db_component)
        # 注意：由于测试环境可能没有真实的数据库连接，此处的状态可能会有不同
    
    def test_full_health_check(self):
        """测试完整级别健康检查"""
        request = pb2.HealthCheckRequest(
            level=pb2.HealthCheckRequest.HealthCheckLevel.FULL
        )
        
        response = self.stub.HealthCheck(request)
        
        # 验证响应包含足够的组件信息
        self.assertTrue(len(response.components) >= 4)
        
        # 验证模型组件信息
        model_component = next((c for c in response.components if c.component_name == "ml_models"), None)
        self.assertIsNotNone(model_component)
        
        # 验证集成服务组件信息
        xiaoai_component = next((c for c in response.components if c.component_name == "xiaoai_service"), None)
        self.assertIsNotNone(xiaoai_component)
        
        rag_component = next((c for c in response.components if c.component_name == "rag_service"), None)
        self.assertIsNotNone(rag_component)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main() 