#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
舌象分析端到端测试

测试舌象分析服务的完整流程，包括图像上传、分析和结果获取。
这是一个集成测试，需要启动完整的服务才能运行。
"""

import os
import sys
import uuid
import unittest
import time
from concurrent import futures

import grpc
import numpy as np
import cv2

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from api.grpc import look_service_pb2, look_service_pb2_grpc
from internal.delivery.look_service_impl import LookServiceServicer
from internal.model.model_factory import ModelFactory
from internal.analysis.tongue_analyzer import TongueAnalyzer
from internal.repository.analysis_repository import AnalysisRepository
from config.config import get_config


class TestTongueAnalysisE2E(unittest.TestCase):
    """舌象分析端到端测试"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化，设置grpc服务器和客户端"""
        # 获取配置
        cls.config = get_config()
        
        # 创建模型工厂
        cls.model_factory = ModelFactory(cls.config)
        
        # 创建舌象分析器
        cls.tongue_analyzer = TongueAnalyzer(cls.config, cls.model_factory)
        
        # 创建分析存储库
        cls.analysis_repository = AnalysisRepository(cls.config)
        
        # 创建服务实现
        cls.servicer = LookServiceServicer(
            cls.config,
            cls.model_factory,
            cls.tongue_analyzer,
            cls.analysis_repository
        )
        
        # 创建测试服务器
        cls.server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
        look_service_pb2_grpc.add_LookServiceServicer_to_server(cls.servicer, cls.server)
        cls.port = cls.server.add_insecure_port('[::]:0')  # 随机可用端口
        cls.server.start()
        
        # 创建客户端通道
        cls.channel = grpc.insecure_channel(f'localhost:{cls.port}')
        cls.stub = look_service_pb2_grpc.LookServiceStub(cls.channel)
        
        # 创建测试舌象图像 (100x100 像素的模拟舌头)
        cls.test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        # 添加舌头形状 (红色圆形)
        cv2.circle(cls.test_image, (50, 50), 40, (0, 0, 220), -1)
        # 添加舌苔 (浅白色覆盖)
        cv2.circle(cls.test_image, (50, 50), 30, (220, 220, 220), -1)
        # 编码为二进制
        _, cls.test_image_binary = cv2.imencode('.jpg', cls.test_image)
        cls.test_image_bytes = cls.test_image_binary.tobytes()

    @classmethod
    def tearDownClass(cls):
        """测试类清理，关闭grpc服务器和客户端"""
        cls.channel.close()
        cls.server.stop(None)  # 立即停止服务器

    def setUp(self):
        """每个测试用例的初始化"""
        self.user_id = f"test-user-{uuid.uuid4()}"

    def test_tongue_analysis_basic_flow(self):
        """测试舌象分析基本流程"""
        # 创建请求
        request = look_service_pb2.TongueAnalysisRequest(
            image=self.test_image_bytes,
            user_id=self.user_id,
            analysis_type=look_service_pb2.AnalysisType.BASIC,
            save_result=True,
            metadata={"source": "e2e_test"}
        )
        
        # 发送请求
        response = self.stub.AnalyzeTongue(request)
        
        # 验证响应
        self.assertIsNotNone(response)
        self.assertIsNotNone(response.request_id)
        self.assertTrue(len(response.tongue_color) > 0)
        self.assertTrue(len(response.tongue_shape) > 0)
        self.assertTrue(len(response.coating_color) > 0)
        self.assertTrue(len(response.analysis_summary) > 0)
        self.assertGreater(len(response.body_constitution), 0)

    def test_tongue_analysis_error_handling(self):
        """测试舌象分析错误处理"""
        # 创建错误请求 (空图像)
        request = look_service_pb2.TongueAnalysisRequest(
            image=b"",
            user_id=self.user_id,
            analysis_type=look_service_pb2.AnalysisType.BASIC,
            save_result=True
        )
        
        # 发送请求，验证异常
        with self.assertRaises(grpc.RpcError) as context:
            self.stub.AnalyzeTongue(request)
        
        # 验证错误码
        self.assertEqual(context.exception.code(), grpc.StatusCode.INVALID_ARGUMENT)

    def test_tongue_analysis_comprehensive(self):
        """测试全面舌象分析"""
        # 创建请求
        request = look_service_pb2.TongueAnalysisRequest(
            image=self.test_image_bytes,
            user_id=self.user_id,
            analysis_type=look_service_pb2.AnalysisType.COMPREHENSIVE,
            save_result=True
        )
        
        # 发送请求
        response = self.stub.AnalyzeTongue(request)
        
        # 验证响应
        self.assertIsNotNone(response)
        self.assertTrue(len(response.metrics) > 0)  # 全面分析应该包含更多量化指标
        
        # 获取分析ID用于历史记录测试
        analysis_id = response.analysis_id
        self.assertIsNotNone(analysis_id)
        
        # 等待数据存储完成
        time.sleep(1)
        
        # 测试历史记录获取
        history_request = look_service_pb2.AnalysisHistoryRequest(
            user_id=self.user_id,
            analysis_type="tongue",
            limit=10
        )
        
        # 发送历史记录请求
        history_response = self.stub.GetAnalysisHistory(history_request)
        
        # 验证历史记录响应
        self.assertIsNotNone(history_response)
        self.assertGreater(history_response.total_count, 0)

    def test_health_check(self):
        """测试健康检查接口"""
        # 创建请求
        request = look_service_pb2.HealthCheckRequest(include_details=True)
        
        # 发送请求
        response = self.stub.HealthCheck(request)
        
        # 验证响应
        self.assertEqual(response.status, look_service_pb2.HealthCheckResponse.SERVING)
        self.assertGreater(len(response.details), 0)


if __name__ == '__main__':
    unittest.main() 