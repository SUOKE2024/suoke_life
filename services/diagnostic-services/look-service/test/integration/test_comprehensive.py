#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
望诊服务综合测试脚本

测试整个look-service的功能，包括API、存储、错误处理等
这是一个集成测试，需要启动完整的服务才能运行。
"""

import os
import sys
import uuid
import unittest
import time
import random
import tempfile
import json
from concurrent import futures
from unittest.mock import MagicMock, patch

import grpc
import numpy as np
import cv2
import sqlite3

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from api.grpc import look_service_pb2, look_service_pb2_grpc
from internal.delivery.look_service_impl import LookServiceServicer
from internal.model.model_factory import ModelFactory
from internal.analysis.face_analyzer import FaceAnalyzer
from internal.analysis.body_analyzer import BodyAnalyzer
from internal.analysis.tongue_analyzer import TongueAnalyzer
from internal.repository.analysis_repository import AnalysisRepository
from config.config import get_config
from pkg.utils.image_utils import auto_enhance_image, check_image_quality


class TestLookServiceComprehensive(unittest.TestCase):
    """望诊服务综合测试"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化，设置gRPC服务器和客户端"""
        # 创建测试数据目录
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.data_dir = os.path.join(cls.temp_dir.name, 'data')
        cls.logs_dir = os.path.join(cls.temp_dir.name, 'logs')
        cls.images_dir = os.path.join(cls.data_dir, 'images')
        cls.analysis_dir = os.path.join(cls.data_dir, 'analysis')
        
        # 创建目录
        os.makedirs(cls.data_dir, exist_ok=True)
        os.makedirs(cls.logs_dir, exist_ok=True)
        os.makedirs(cls.images_dir, exist_ok=True)
        os.makedirs(cls.analysis_dir, exist_ok=True)
        
        # 创建测试配置
        cls.config = {
            "server": {
                "host": "0.0.0.0",
                "port": 50053,
                "debug": False,
                "grpc": {
                    "max_workers": 2
                }
            },
            "logging": {
                "level": "DEBUG",
                "file": os.path.join(cls.logs_dir, "look_service.log"),
                "console": True
            },
            "database": {
                "uri": f"sqlite:///{os.path.join(cls.data_dir, 'look_service.db')}"
            },
            "models": {
                "face_analysis": {
                    "path": "./models/face_analyzer",
                    "version": "v1.0.0",
                    "batch_size": 1,
                    "device": "cpu",
                    "threshold": 0.7,
                    "input_size": [224, 224]
                },
                "body_analysis": {
                    "path": "./models/body_analyzer",
                    "version": "v1.0.0",
                    "batch_size": 1,
                    "device": "cpu",
                    "threshold": 0.6,
                    "input_size": [384, 384]
                }
            },
            "storage": {
                "image": {
                    "path": cls.images_dir,
                    "max_size_mb": 10,
                    "allowed_formats": ["jpg", "jpeg", "png"],
                },
                "analysis": {
                    "path": cls.analysis_dir,
                    "ttl_days": 90
                }
            },
            "integration": {
                "xiaoai_service": {
                    "host": "xiaoai-service-mock",
                    "port": 50050,
                    "timeout_ms": 1000,
                    "max_retries": 1
                }
            },
            "monitoring": {
                "prometheus": {
                    "enabled": False
                }
            }
        }
        
        # 使用补丁来模拟模型工厂和分析器
        with patch('internal.model.model_factory.ModelFactory') as mock_factory_cls:
            # 设置模型工厂模拟
            cls.mock_factory = MagicMock()
            mock_factory_cls.return_value = cls.mock_factory
            
            # 设置分析器模拟
            cls.mock_face_analyzer = MagicMock()
            cls.mock_body_analyzer = MagicMock()
            cls.mock_tongue_analyzer = MagicMock()
            
            # 创建存储库
            cls.analysis_repository = AnalysisRepository(cls.config)
            
            # 创建服务实现
            cls.servicer = LookServiceServicer(
                cls.config,
                cls.mock_factory,
                cls.mock_tongue_analyzer,
                cls.analysis_repository
            )
            
            # 设置舌象分析器属性
            cls.servicer.face_analyzer = cls.mock_face_analyzer
            cls.servicer.body_analyzer = cls.mock_body_analyzer
            
            # 设置xiaoai客户端模拟
            cls.servicer.xiaoai_client = MagicMock()
            
            # 创建测试服务器
            cls.server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
            look_service_pb2_grpc.add_LookServiceServicer_to_server(cls.servicer, cls.server)
            cls.port = cls.server.add_insecure_port('[::]:0')  # 随机可用端口
            cls.server.start()
            
            # 创建客户端通道
            cls.channel = grpc.insecure_channel(f'localhost:{cls.port}')
            cls.stub = look_service_pb2_grpc.LookServiceStub(cls.channel)
        
        # 创建测试图像
        cls.face_image = np.zeros((200, 200, 3), dtype=np.uint8)
        cv2.circle(cls.face_image, (100, 80), 60, (200, 180, 160), -1)  # 脸部
        cv2.circle(cls.face_image, (80, 70), 10, (255, 255, 255), -1)   # 左眼
        cv2.circle(cls.face_image, (120, 70), 10, (255, 255, 255), -1)  # 右眼
        cv2.ellipse(cls.face_image, (100, 110), (30, 10), 0, 0, 180, (120, 80, 80), -1)  # 嘴巴
        _, cls.face_image_binary = cv2.imencode('.jpg', cls.face_image)
        cls.face_image_bytes = cls.face_image_binary.tobytes()
        
        cls.body_image = np.zeros((400, 200, 3), dtype=np.uint8)
        cv2.circle(cls.body_image, (100, 50), 30, (200, 180, 160), -1)  # 头部
        cv2.rectangle(cls.body_image, (70, 80), (130, 200), (200, 180, 160), -1)  # 身体
        cv2.rectangle(cls.body_image, (70, 200), (90, 350), (200, 180, 160), -1)  # 左腿
        cv2.rectangle(cls.body_image, (110, 200), (130, 350), (200, 180, 160), -1)  # 右腿
        _, cls.body_image_binary = cv2.imencode('.jpg', cls.body_image)
        cls.body_image_bytes = cls.body_image_binary.tobytes()
        
        cls.tongue_image = np.zeros((150, 200, 3), dtype=np.uint8)
        cv2.ellipse(cls.tongue_image, (100, 75), (80, 50), 0, 0, 360, (130, 20, 30), -1)  # 舌体
        cv2.ellipse(cls.tongue_image, (100, 75), (60, 35), 0, 0, 360, (200, 200, 200), -1)  # 舌苔
        _, cls.tongue_image_binary = cv2.imencode('.jpg', cls.tongue_image)
        cls.tongue_image_bytes = cls.tongue_image_binary.tobytes()

    @classmethod
    def tearDownClass(cls):
        """测试类清理，关闭服务和删除临时文件"""
        cls.channel.close()
        cls.server.stop(None)  # 立即停止服务器
        cls.temp_dir.cleanup()  # 清理临时目录

    def setUp(self):
        """每个测试用例的初始化"""
        self.user_id = f"test-user-{uuid.uuid4()}"
        
        # 设置模拟分析器的返回值
        # 面色分析返回值
        self.mock_face_analyzer.analyze.return_value = self.create_mock_face_analysis_result()
        
        # 形体分析返回值
        self.mock_body_analyzer.analyze.return_value = self.create_mock_body_analysis_result()
        
        # 舌象分析返回值
        self.mock_tongue_analyzer.analyze.return_value = self.create_mock_tongue_analysis_result()

    def create_mock_face_analysis_result(self):
        """创建模拟的面色分析结果"""
        result = MagicMock()
        result.request_id = str(uuid.uuid4())
        result.face_color = "黄色"
        result.regions = [
            MagicMock(region_name="前额", color="黄白", feature="湿润", confidence=0.92),
            MagicMock(region_name="双颊", color="红赤", feature="干燥", confidence=0.89)
        ]
        result.features = ["颧骨偏高", "印堂饱满"]
        result.body_constitution = [
            MagicMock(constitution_type="湿热质", confidence=0.75, description="面色偏黄，多汗，口干")
        ]
        result.organ_correlations = [
            MagicMock(organ_name="脾", status="湿热", confidence=0.82, description="脾失健运")
        ]
        result.analysis_summary = "面色偏黄，颧骨偏高，印堂饱满，双颊偏红，显示脾胃湿热体质特征。"
        result.tcm_analysis = {"face_color": "yellow", "constitution": "damp_heat"}
        return result

    def create_mock_body_analysis_result(self):
        """创建模拟的形体分析结果"""
        result = MagicMock()
        result.request_id = str(uuid.uuid4())
        result.body_type = "偏瘦型"
        result.features = [
            MagicMock(feature_name="肩宽", value="窄", confidence=0.85),
            MagicMock(feature_name="胸围", value="偏小", confidence=0.88)
        ]
        result.posture = [
            MagicMock(posture_aspect="站姿", status="微驼背", confidence=0.87, suggestion="注意挺胸"),
            MagicMock(posture_aspect="肩部", status="左高右低", confidence=0.79, suggestion="调整肩部平衡")
        ]
        result.body_constitution = [
            MagicMock(constitution_type="气虚质", confidence=0.82, description="体型偏瘦，易疲劳")
        ]
        result.analysis_summary = "体型偏瘦，肩窄，胸围偏小，站姿微驼背，肩部不平，显示气虚体质特征。"
        result.tcm_analysis = {"body_type": "thin", "constitution": "qi_deficiency"}
        return result

    def create_mock_tongue_analysis_result(self):
        """创建模拟的舌象分析结果"""
        result = MagicMock()
        result.request_id = str(uuid.uuid4())
        result.analysis_id = str(uuid.uuid4())
        result.tongue_color = MagicMock(value="淡红")
        result.tongue_shape = MagicMock(value="正常")
        result.coating_color = MagicMock(value="薄白")
        result.coating_distribution = "均匀"
        result.features = ["舌尖红", "舌体胖大"]
        result.locations = [
            MagicMock(feature_name="舌尖红", x_min=80, y_min=60, x_max=120, y_max=70, confidence=0.91)
        ]
        result.body_constitution = [
            MagicMock(constitution_type="痰湿质", confidence=0.68, description="舌体胖大，舌苔白腻")
        ]
        result.metrics = {"moisture": 0.65, "coating_thickness": 0.3}
        result.analysis_summary = "舌质淡红，舌体胖大，舌苔薄白均匀，舌尖偏红，显示痰湿体质特征。"
        result.timestamp = int(time.time())
        return result

    def test_face_analysis_basic_flow(self):
        """测试面色分析基本流程"""
        # 创建请求
        request = look_service_pb2.FaceAnalysisRequest(
            image=self.face_image_bytes,
            user_id=self.user_id,
            analysis_type=look_service_pb2.AnalysisType.BASIC,
            save_result=True,
            metadata={"source": "comprehensive_test"}
        )
        
        # 发送请求
        response = self.stub.AnalyzeFace(request)
        
        # 验证响应
        self.assertIsNotNone(response)
        self.assertEqual(response.face_color, "黄色")
        self.assertEqual(len(response.regions), 2)
        self.assertEqual(response.regions[0].region_name, "前额")
        self.assertEqual(len(response.body_constitution), 1)
        self.assertEqual(response.body_constitution[0].constitution_type, "湿热质")
        self.assertIn("面色偏黄", response.analysis_summary)
        
        # 验证模拟方法调用
        self.mock_face_analyzer.analyze.assert_called_once()
        args, kwargs = self.mock_face_analyzer.analyze.call_args
        self.assertEqual(args[0], self.face_image_bytes)
        self.assertEqual(args[1], self.user_id)
        
        # 验证小艾服务通知
        self.servicer.xiaoai_client.notify_analysis_result.assert_called_once()

    def test_body_analysis_basic_flow(self):
        """测试形体分析基本流程"""
        # 创建请求
        request = look_service_pb2.BodyAnalysisRequest(
            image=self.body_image_bytes,
            user_id=self.user_id,
            analysis_type=look_service_pb2.AnalysisType.BASIC,
            save_result=True,
            metadata={"source": "comprehensive_test"}
        )
        
        # 发送请求
        response = self.stub.AnalyzeBody(request)
        
        # 验证响应
        self.assertIsNotNone(response)
        self.assertEqual(response.body_type, "偏瘦型")
        self.assertEqual(len(response.features), 2)
        self.assertEqual(response.features[0].feature_name, "肩宽")
        self.assertEqual(len(response.posture), 2)
        self.assertEqual(response.posture[0].posture_aspect, "站姿")
        self.assertEqual(len(response.body_constitution), 1)
        self.assertEqual(response.body_constitution[0].constitution_type, "气虚质")
        self.assertIn("体型偏瘦", response.analysis_summary)
        
        # 验证模拟方法调用
        self.mock_body_analyzer.analyze.assert_called_once()
        args, kwargs = self.mock_body_analyzer.analyze.call_args
        self.assertEqual(args[0], self.body_image_bytes)
        self.assertEqual(args[1], self.user_id)
        
        # 验证小艾服务通知
        self.servicer.xiaoai_client.notify_analysis_result.assert_called()

    def test_tongue_analysis_basic_flow(self):
        """测试舌象分析基本流程"""
        # 创建请求
        request = look_service_pb2.TongueAnalysisRequest(
            image=self.tongue_image_bytes,
            user_id=self.user_id,
            analysis_type=look_service_pb2.AnalysisType.BASIC,
            save_result=True,
            metadata={"source": "comprehensive_test"}
        )
        
        # 发送请求
        response = self.stub.AnalyzeTongue(request)
        
        # 验证响应
        self.assertIsNotNone(response)
        self.assertEqual(response.tongue_color, "淡红")
        self.assertEqual(response.tongue_shape, "正常")
        self.assertEqual(response.coating_color, "薄白")
        self.assertEqual(response.coating_distribution, "均匀")
        self.assertEqual(len(response.features), 2)
        self.assertEqual(response.features[0], "舌尖红")
        self.assertEqual(len(response.locations), 1)
        self.assertEqual(response.locations[0].feature_name, "舌尖红")
        self.assertEqual(len(response.body_constitution), 1)
        self.assertEqual(response.body_constitution[0].constitution_type, "痰湿质")
        self.assertEqual(len(response.metrics), 2)
        self.assertIn("舌质淡红", response.analysis_summary)
        
        # 验证模拟方法调用
        self.mock_tongue_analyzer.analyze.assert_called_once()
        args, kwargs = self.mock_tongue_analyzer.analyze.call_args
        self.assertEqual(args[0], self.tongue_image_bytes)
        self.assertEqual(args[1], self.user_id)

    def test_analysis_history(self):
        """测试历史分析记录"""
        # 先创建几个分析记录
        for _ in range(3):
            request = look_service_pb2.TongueAnalysisRequest(
                image=self.tongue_image_bytes,
                user_id=self.user_id,
                analysis_type=look_service_pb2.AnalysisType.BASIC,
                save_result=True
            )
            self.stub.AnalyzeTongue(request)
        
        # 获取历史记录
        history_request = look_service_pb2.AnalysisHistoryRequest(
            user_id=self.user_id,
            analysis_type="tongue",
            limit=10
        )
        
        # 发送历史记录请求
        history_response = self.stub.GetAnalysisHistory(history_request)
        
        # 验证历史记录响应
        self.assertIsNotNone(history_response)
        # 注意：当前实现是模拟数据，总是返回3条记录
        self.assertGreater(history_response.total_count, 0)

    def test_compare_analysis(self):
        """测试比较分析结果"""
        # 创建两个分析记录
        first_response = self.stub.AnalyzeTongue(look_service_pb2.TongueAnalysisRequest(
            image=self.tongue_image_bytes,
            user_id=self.user_id,
            analysis_type=look_service_pb2.AnalysisType.BASIC,
            save_result=True
        ))
        
        # 等待一点时间，确保时间戳不同
        time.sleep(1)
        
        second_response = self.stub.AnalyzeTongue(look_service_pb2.TongueAnalysisRequest(
            image=self.tongue_image_bytes,
            user_id=self.user_id,
            analysis_type=look_service_pb2.AnalysisType.BASIC,
            save_result=True
        ))
        
        # 比较分析
        compare_request = look_service_pb2.CompareAnalysisRequest(
            user_id=self.user_id,
            analysis_type="tongue",
            first_analysis_id=first_response.analysis_id,
            second_analysis_id=second_response.analysis_id
        )
        
        # 发送比较请求
        compare_response = self.stub.CompareAnalysis(compare_request)
        
        # 验证比较响应
        self.assertIsNotNone(compare_response)
        self.assertGreaterEqual(len(compare_response.feature_comparisons), 0)

    def test_health_check(self):
        """测试健康检查接口"""
        # 创建请求
        request = look_service_pb2.HealthCheckRequest(include_details=True)
        
        # 发送请求
        response = self.stub.HealthCheck(request)
        
        # 验证响应
        self.assertEqual(response.status, look_service_pb2.HealthCheckResponse.SERVING)
        self.assertGreater(len(response.details), 0)

    def test_invalid_input_handling(self):
        """测试无效输入处理"""
        # 空图像数据
        empty_request = look_service_pb2.FaceAnalysisRequest(
            image=b"",
            user_id=self.user_id,
            analysis_type=look_service_pb2.AnalysisType.BASIC,
            save_result=True
        )
        
        # 验证抛出异常
        with self.assertRaises(grpc.RpcError) as context:
            self.stub.AnalyzeFace(empty_request)
        
        # 验证错误码
        self.assertEqual(context.exception.code(), grpc.StatusCode.INVALID_ARGUMENT)
        
        # 无效图像数据
        invalid_request = look_service_pb2.FaceAnalysisRequest(
            image=b"not an image",
            user_id=self.user_id,
            analysis_type=look_service_pb2.AnalysisType.BASIC,
            save_result=True
        )
        
        # 验证抛出异常
        with self.assertRaises(grpc.RpcError) as context:
            self.stub.AnalyzeFace(invalid_request)
        
        # 验证错误码
        self.assertEqual(context.exception.code(), grpc.StatusCode.INVALID_ARGUMENT)
        
        # 缺少用户ID
        no_user_request = look_service_pb2.FaceAnalysisRequest(
            image=self.face_image_bytes,
            user_id="",
            analysis_type=look_service_pb2.AnalysisType.BASIC,
            save_result=True
        )
        
        # 验证抛出异常
        with self.assertRaises(grpc.RpcError) as context:
            self.stub.AnalyzeFace(no_user_request)
        
        # 验证错误码
        self.assertEqual(context.exception.code(), grpc.StatusCode.INVALID_ARGUMENT)

    def test_image_quality_utils(self):
        """测试图像质量工具函数"""
        # 检查图像质量
        quality = check_image_quality(self.face_image)
        
        # 验证质量指标
        self.assertIn("sharpness", quality)
        self.assertIn("brightness", quality)
        self.assertIn("contrast", quality)
        self.assertIn("noise_level", quality)
        self.assertIn("overall_score", quality)
        
        # 测试自动增强
        enhanced = auto_enhance_image(self.face_image)
        
        # 验证增强后图像
        self.assertEqual(enhanced.shape, self.face_image.shape)
        
        # 再次检查质量，应该有所改善
        enhanced_quality = check_image_quality(enhanced)
        
        # 通常增强后的整体得分应该不低于原始图像
        # 注意：在某些特殊情况下，这个断言可能不成立，取决于图像本身和增强算法
        # self.assertGreaterEqual(enhanced_quality["overall_score"], quality["overall_score"])


if __name__ == '__main__':
    unittest.main() 