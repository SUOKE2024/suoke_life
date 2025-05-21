#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
望诊服务API集成测试脚本

测试服务的gRPC接口功能，验证端到端服务调用的正确性。
"""

import os
import sys
import time
import unittest
import uuid
import grpc
import cv2
import numpy as np
from concurrent import futures

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from api.grpc import look_service_pb2, look_service_pb2_grpc
from internal.delivery.look_service_impl import LookServiceServicer


class TestLookServiceAPI(unittest.TestCase):
    """望诊服务API集成测试"""

    @classmethod
    def setUpClass(cls):
        """测试类设置"""
        # 启动测试服务器
        cls.server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
        cls.servicer = LookServiceServicer()
        look_service_pb2_grpc.add_LookServiceServicer_to_server(cls.servicer, cls.server)
        cls.port = 50099  # 使用不常用端口避免冲突
        cls.server.add_insecure_port(f'[::]:{cls.port}')
        cls.server.start()
        
        # 创建客户端通道
        cls.channel = grpc.insecure_channel(f'localhost:{cls.port}')
        cls.stub = look_service_pb2_grpc.LookServiceStub(cls.channel)
        
        # 创建测试用户ID
        cls.test_user_id = f"test_user_{str(uuid.uuid4())[:8]}"
        
        # 创建测试图像
        cls.face_image = cls._create_face_test_image()
        cls.body_image = cls._create_body_test_image()
    
    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        # 关闭客户端通道
        cls.channel.close()
        
        # 关闭服务器
        cls.server.stop(grace=None)
    
    @classmethod
    def _create_face_test_image(cls):
        """创建面部测试图像"""
        # 创建一个简单的彩色图像
        img = np.ones((200, 200, 3), dtype=np.uint8) * 200  # 浅灰色背景
        
        # 添加一个简单的面部图形（椭圆）
        cv2.ellipse(img, (100, 100), (60, 80), 0, 0, 360, (210, 170, 150), -1)  # 面部肤色
        
        # 添加眼睛
        cv2.circle(img, (70, 80), 10, (50, 50, 50), -1)  # 左眼
        cv2.circle(img, (130, 80), 10, (50, 50, 50), -1)  # 右眼
        
        # 添加鼻子
        cv2.ellipse(img, (100, 110), (10, 15), 0, 0, 360, (180, 140, 130), -1)
        
        # 添加嘴巴
        cv2.ellipse(img, (100, 140), (30, 10), 0, 0, 180, (150, 90, 90), 3)
        
        # 编码为JPEG
        _, buffer = cv2.imencode('.jpg', img)
        return buffer.tobytes()
    
    @classmethod
    def _create_body_test_image(cls):
        """创建身体测试图像"""
        # 创建一个简单的彩色图像
        img = np.ones((400, 200, 3), dtype=np.uint8) * 220  # 浅灰色背景
        
        # 头部
        cv2.circle(img, (100, 50), 30, (210, 170, 150), -1)
        
        # 躯干
        cv2.rectangle(img, (70, 80), (130, 220), (210, 170, 150), -1)
        
        # 手臂
        cv2.rectangle(img, (50, 90), (70, 180), (210, 170, 150), -1)  # 左臂
        cv2.rectangle(img, (130, 90), (150, 180), (210, 170, 150), -1)  # 右臂
        
        # 腿部
        cv2.rectangle(img, (80, 220), (95, 350), (210, 170, 150), -1)  # 左腿
        cv2.rectangle(img, (105, 220), (120, 350), (210, 170, 150), -1)  # 右腿
        
        # 编码为JPEG
        _, buffer = cv2.imencode('.jpg', img)
        return buffer.tobytes()
    
    def test_health_check(self):
        """测试健康检查端点"""
        # 创建健康检查请求
        request = look_service_pb2.HealthCheckRequest(include_details=True)
        
        # 调用健康检查
        response = self.stub.HealthCheck(request)
        
        # 验证响应
        self.assertEqual(response.status, look_service_pb2.HealthCheckResponse.Status.SERVING)
    
    def test_analyze_face(self):
        """测试面色分析功能"""
        # 创建面色分析请求
        request = look_service_pb2.FaceAnalysisRequest(
            user_id=self.test_user_id,
            image_data=self.face_image
        )
        
        # 调用面色分析
        response = self.stub.AnalyzeFace(request)
        
        # 验证响应
        self.assertIsNotNone(response.analysis_id)
        self.assertEqual(response.user_id, self.test_user_id)
        self.assertGreater(response.confidence, 0.0)
        self.assertIsNotNone(response.face_color)
        self.assertIsNotNone(response.skin_moisture)
        self.assertIsNotNone(response.tcm_analysis)
        
        # 保存分析ID用于后续测试
        self.face_analysis_id = response.analysis_id
    
    def test_analyze_body(self):
        """测试形体分析功能"""
        # 创建形体分析请求
        request = look_service_pb2.BodyAnalysisRequest(
            user_id=self.test_user_id,
            image_data=self.body_image
        )
        
        # 调用形体分析
        response = self.stub.AnalyzeBody(request)
        
        # 验证响应
        self.assertIsNotNone(response.analysis_id)
        self.assertEqual(response.user_id, self.test_user_id)
        self.assertGreater(response.confidence, 0.0)
        self.assertIsNotNone(response.body_shape)
        self.assertIsNotNone(response.posture)
        self.assertIsNotNone(response.tcm_analysis)
        
        # 保存分析ID用于后续测试
        self.body_analysis_id = response.analysis_id
    
    def test_get_face_analysis(self):
        """测试获取面色分析结果"""
        # 首先确保有面色分析结果
        if not hasattr(self, 'face_analysis_id'):
            self.test_analyze_face()
        
        # 创建获取面色分析请求
        request = look_service_pb2.GetFaceAnalysisRequest(
            analysis_id=self.face_analysis_id
        )
        
        # 调用获取面色分析
        response = self.stub.GetFaceAnalysis(request)
        
        # 验证响应
        self.assertEqual(response.analysis_id, self.face_analysis_id)
        self.assertEqual(response.user_id, self.test_user_id)
        self.assertIsNotNone(response.face_color)
        self.assertIsNotNone(response.skin_moisture)
        self.assertIsNotNone(response.tcm_analysis)
    
    def test_get_body_analysis(self):
        """测试获取形体分析结果"""
        # 首先确保有形体分析结果
        if not hasattr(self, 'body_analysis_id'):
            self.test_analyze_body()
        
        # 创建获取形体分析请求
        request = look_service_pb2.GetBodyAnalysisRequest(
            analysis_id=self.body_analysis_id
        )
        
        # 调用获取形体分析
        response = self.stub.GetBodyAnalysis(request)
        
        # 验证响应
        self.assertEqual(response.analysis_id, self.body_analysis_id)
        self.assertEqual(response.user_id, self.test_user_id)
        self.assertIsNotNone(response.body_shape)
        self.assertIsNotNone(response.posture)
        self.assertIsNotNone(response.tcm_analysis)
    
    def test_get_user_analysis_history(self):
        """测试获取用户分析历史"""
        # 首先确保有分析记录
        if not hasattr(self, 'face_analysis_id'):
            self.test_analyze_face()
        if not hasattr(self, 'body_analysis_id'):
            self.test_analyze_body()
        
        # 等待数据写入
        time.sleep(1)
        
        # 创建获取用户分析历史请求
        request = look_service_pb2.GetUserAnalysisHistoryRequest(
            user_id=self.test_user_id,
            limit=10,
            offset=0
        )
        
        # 调用获取用户分析历史
        response = self.stub.GetUserAnalysisHistory(request)
        
        # 验证响应
        self.assertEqual(response.user_id, self.test_user_id)
        self.assertGreaterEqual(response.total_count, 2)  # 至少有面色和形体分析记录
        self.assertGreaterEqual(len(response.history), 2)
        
        # 检查是否包含之前的分析记录
        analysis_ids = [item.analysis_id for item in response.history]
        self.assertIn(self.face_analysis_id, analysis_ids)
        self.assertIn(self.body_analysis_id, analysis_ids)
    
    def test_delete_analysis(self):
        """测试删除分析记录"""
        # 首先创建一个新的分析记录
        request = look_service_pb2.FaceAnalysisRequest(
            user_id=self.test_user_id,
            image_data=self.face_image
        )
        response = self.stub.AnalyzeFace(request)
        analysis_id = response.analysis_id
        
        # 创建删除分析请求
        delete_request = look_service_pb2.DeleteAnalysisRequest(
            analysis_id=analysis_id,
            analysis_type="face"
        )
        
        # 调用删除分析
        delete_response = self.stub.DeleteAnalysis(delete_request)
        
        # 验证响应
        self.assertTrue(delete_response.success)
        
        # 尝试获取已删除的记录，应该失败
        get_request = look_service_pb2.GetFaceAnalysisRequest(
            analysis_id=analysis_id
        )
        
        with self.assertRaises(grpc.RpcError) as context:
            self.stub.GetFaceAnalysis(get_request)
        
        # 验证错误代码是NOT_FOUND
        self.assertEqual(context.exception.code(), grpc.StatusCode.NOT_FOUND)
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试无效的用户ID
        request = look_service_pb2.FaceAnalysisRequest(
            user_id="",
            image_data=self.face_image
        )
        
        with self.assertRaises(grpc.RpcError) as context:
            self.stub.AnalyzeFace(request)
        
        # 验证错误代码是INVALID_ARGUMENT
        self.assertEqual(context.exception.code(), grpc.StatusCode.INVALID_ARGUMENT)
        
        # 测试无效的图像数据
        request = look_service_pb2.FaceAnalysisRequest(
            user_id=self.test_user_id,
            image_data=b"This is not an image"
        )
        
        with self.assertRaises(grpc.RpcError) as context:
            self.stub.AnalyzeFace(request)
        
        # 验证错误代码是INVALID_ARGUMENT
        self.assertEqual(context.exception.code(), grpc.StatusCode.INVALID_ARGUMENT)
        
        # 测试不存在的分析记录
        request = look_service_pb2.GetFaceAnalysisRequest(
            analysis_id="non_existent_id"
        )
        
        with self.assertRaises(grpc.RpcError) as context:
            self.stub.GetFaceAnalysis(request)
        
        # 验证错误代码是NOT_FOUND
        self.assertEqual(context.exception.code(), grpc.StatusCode.NOT_FOUND)


if __name__ == "__main__":
    unittest.main() 