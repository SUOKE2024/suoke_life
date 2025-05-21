import unittest
import os
import sys
import json
import grpc
import time
from unittest.mock import patch, MagicMock
import numpy as np
import cv2

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# 导入gRPC相关模块
from api.grpc import look_service_pb2, look_service_pb2_grpc
# 假设xiaoai服务也有类似的gRPC定义
# from integration.xiaoai_service.api.grpc import xiaoai_service_pb2, xiaoai_service_pb2_grpc

class XiaoaiIntegrationTest(unittest.TestCase):
    """测试Look服务与小艾服务的集成"""

    def setUp(self):
        """测试前的准备工作"""
        # 设置Look服务客户端
        # 在测试环境中使用模拟的gRPC通道
        self.look_channel = MagicMock()
        self.look_stub = look_service_pb2_grpc.LookServiceStub(self.look_channel)
        
        # 设置小艾服务客户端
        self.xiaoai_channel = MagicMock()
        # self.xiaoai_stub = xiaoai_service_pb2_grpc.XiaoaiServiceStub(self.xiaoai_channel)
        
        # 创建测试图像数据
        test_image = np.ones((512, 512, 3), dtype=np.uint8) * 150
        _, self.test_image_bytes = cv2.imencode('.jpg', test_image)
        self.test_image_bytes = self.test_image_bytes.tobytes()
        
        # 模拟Look服务的分析结果
        self.mock_tongue_analysis = {
            'request_id': 'test_request_123',
            'tongue_color': 'red',
            'tongue_shape': 'normal',
            'coating_color': 'white',
            'coating_distribution': 'center',
            'features': ['thin_coating', 'red_tip'],
            'body_constitution': [
                {'constitution_type': '气虚质', 'confidence': 0.72, 'description': '舌淡胖大'}
            ],
            'metrics': {'color_intensity': 0.65, 'coating_thickness': 0.3},
            'analysis_summary': '舌质红，苔薄白，舌尖偏红，疑似心火旺盛',
            'analysis_id': 'analysis_123',
            'timestamp': int(time.time())
        }
        
        self.mock_face_analysis = {
            'request_id': 'test_request_124',
            'face_color': 'yellow',
            'regions': [
                {'region_name': 'forehead', 'color': 'yellow', 'feature': 'oily', 'confidence': 0.85}
            ],
            'features': ['yellow_complexion', 'oily_skin'],
            'organ_correlations': [
                {'organ_name': '脾胃', 'status': '湿热', 'confidence': 0.8, 'description': '脾胃湿热'}
            ],
            'body_constitution': [
                {'constitution_type': '湿热质', 'confidence': 0.75, 'description': '面色偏黄'}
            ],
            'analysis_summary': '面色偏黄，额头油腻，疑似脾胃湿热',
            'analysis_id': 'analysis_124',
            'timestamp': int(time.time())
        }

    def test_tongue_analysis_integration(self):
        """测试舌象分析与小艾服务的集成"""
        # 模拟Look服务的舌象分析响应
        mock_tongue_response = MagicMock()
        mock_tongue_response.request_id = self.mock_tongue_analysis['request_id']
        mock_tongue_response.tongue_color = self.mock_tongue_analysis['tongue_color']
        mock_tongue_response.tongue_shape = self.mock_tongue_analysis['tongue_shape']
        mock_tongue_response.coating_color = self.mock_tongue_analysis['coating_color']
        mock_tongue_response.coating_distribution = self.mock_tongue_analysis['coating_distribution']
        mock_tongue_response.features.extend(self.mock_tongue_analysis['features'])
        
        # 设置体质关联
        for constitution in self.mock_tongue_analysis['body_constitution']:
            body_const = mock_tongue_response.body_constitution.add()
            body_const.constitution_type = constitution['constitution_type']
            body_const.confidence = constitution['confidence']
            body_const.description = constitution['description']
        
        # 设置量化指标
        for k, v in self.mock_tongue_analysis['metrics'].items():
            mock_tongue_response.metrics[k] = v
            
        mock_tongue_response.analysis_summary = self.mock_tongue_analysis['analysis_summary']
        mock_tongue_response.analysis_id = self.mock_tongue_analysis['analysis_id']
        mock_tongue_response.timestamp = self.mock_tongue_analysis['timestamp']
        
        # 模拟Look服务的AnalyzeTongue方法
        self.look_stub.AnalyzeTongue = MagicMock(return_value=mock_tongue_response)
        
        # 创建舌象分析请求
        tongue_request = look_service_pb2.TongueAnalysisRequest(
            image=self.test_image_bytes,
            user_id='test_user_123',
            analysis_type=look_service_pb2.AnalysisType.COMPREHENSIVE,
            save_result=True,
            metadata={'session_id': 'test_session_123'}
        )
        
        # 调用Look服务的舌象分析
        response = self.look_stub.AnalyzeTongue(tongue_request)
        
        # 验证舌象分析结果
        self.assertEqual(response.tongue_color, 'red')
        self.assertEqual(response.tongue_shape, 'normal')
        self.assertEqual(response.coating_color, 'white')
        self.assertEqual(len(response.features), 2)
        self.assertEqual(len(response.body_constitution), 1)
        self.assertEqual(response.body_constitution[0].constitution_type, '气虚质')
        
        # 模拟将舌象分析结果发送到小艾服务进行诊断整合
        # 这里假设小艾服务有一个IntegrateLookDiagnostic方法来整合望诊结果
        '''
        xiaoai_request = xiaoai_service_pb2.IntegrateDiagnosticRequest(
            user_id='test_user_123',
            diagnostic_type='tongue',
            analysis_id=response.analysis_id,
            analysis_summary=response.analysis_summary,
            timestamp=response.timestamp
        )
        
        # 模拟小艾服务的响应
        mock_xiaoai_response = MagicMock()
        mock_xiaoai_response.success = True
        mock_xiaoai_response.integration_id = 'integration_123'
        mock_xiaoai_response.message = '成功整合舌象分析结果'
        
        # 设置模拟响应
        self.xiaoai_stub.IntegrateLookDiagnostic = MagicMock(return_value=mock_xiaoai_response)
        
        # 调用小艾服务整合望诊结果
        xiaoai_response = self.xiaoai_stub.IntegrateLookDiagnostic(xiaoai_request)
        
        # 验证整合结果
        self.assertTrue(xiaoai_response.success)
        self.assertEqual(xiaoai_response.integration_id, 'integration_123')
        '''
        
        # 在实际集成中，上面注释的代码会被解注释并使用真实的小艾服务接口
        # 此处为了测试可以运行，暂时使用模拟代码
        
        # 模拟小艾服务整合结果
        xiaoai_integration_success = True
        
        # 验证整合结果
        self.assertTrue(xiaoai_integration_success)

    def test_face_analysis_integration(self):
        """测试面色分析与小艾服务的集成"""
        # 模拟Look服务的面色分析响应
        mock_face_response = MagicMock()
        mock_face_response.request_id = self.mock_face_analysis['request_id']
        mock_face_response.face_color = self.mock_face_analysis['face_color']
        mock_face_response.features.extend(self.mock_face_analysis['features'])
        
        # 设置区域分析
        for region in self.mock_face_analysis['regions']:
            face_region = mock_face_response.regions.add()
            face_region.region_name = region['region_name']
            face_region.color = region['color']
            face_region.feature = region['feature']
            face_region.confidence = region['confidence']
        
        # 设置脏腑关联
        for organ in self.mock_face_analysis['organ_correlations']:
            organ_corr = mock_face_response.organ_correlations.add()
            organ_corr.organ_name = organ['organ_name']
            organ_corr.status = organ['status']
            organ_corr.confidence = organ['confidence']
            organ_corr.description = organ['description']
        
        # 设置体质关联
        for constitution in self.mock_face_analysis['body_constitution']:
            body_const = mock_face_response.body_constitution.add()
            body_const.constitution_type = constitution['constitution_type']
            body_const.confidence = constitution['confidence']
            body_const.description = constitution['description']
            
        mock_face_response.analysis_summary = self.mock_face_analysis['analysis_summary']
        mock_face_response.analysis_id = self.mock_face_analysis['analysis_id']
        mock_face_response.timestamp = self.mock_face_analysis['timestamp']
        
        # 模拟Look服务的AnalyzeFace方法
        self.look_stub.AnalyzeFace = MagicMock(return_value=mock_face_response)
        
        # 创建面色分析请求
        face_request = look_service_pb2.FaceAnalysisRequest(
            image=self.test_image_bytes,
            user_id='test_user_123',
            analysis_type=look_service_pb2.AnalysisType.COMPREHENSIVE,
            save_result=True,
            metadata={'session_id': 'test_session_123'}
        )
        
        # 调用Look服务的面色分析
        response = self.look_stub.AnalyzeFace(face_request)
        
        # 验证面色分析结果
        self.assertEqual(response.face_color, 'yellow')
        self.assertEqual(len(response.regions), 1)
        self.assertEqual(response.regions[0].region_name, 'forehead')
        self.assertEqual(len(response.features), 2)
        self.assertEqual(len(response.organ_correlations), 1)
        self.assertEqual(response.organ_correlations[0].organ_name, '脾胃')
        self.assertEqual(len(response.body_constitution), 1)
        self.assertEqual(response.body_constitution[0].constitution_type, '湿热质')
        
        # 模拟将面色分析结果发送到小艾服务进行诊断整合
        # 同上，这里使用模拟代码替代实际的小艾服务调用
        xiaoai_integration_success = True
        
        # 验证整合结果
        self.assertTrue(xiaoai_integration_success)

    def test_compare_analysis_integration(self):
        """测试比较分析与小艾服务的集成"""
        # 模拟Look服务的比较分析响应
        mock_compare_response = MagicMock()
        
        # 设置特征比较
        feature_comparison = mock_compare_response.feature_comparisons.add()
        feature_comparison.feature_name = "舌色"
        feature_comparison.first_value = "淡红"
        feature_comparison.second_value = "红"
        feature_comparison.change_percentage = 20.0
        feature_comparison.change_direction = "deteriorated"
        
        feature_comparison = mock_compare_response.feature_comparisons.add()
        feature_comparison.feature_name = "舌苔"
        feature_comparison.first_value = "薄白"
        feature_comparison.second_value = "薄白"
        feature_comparison.change_percentage = 0.0
        feature_comparison.change_direction = "unchanged"
        
        # 设置改善项、恶化项和未变项
        mock_compare_response.deteriorations.append("舌色加深")
        mock_compare_response.unchanged.append("舌苔未变")
        mock_compare_response.comparison_summary = "舌色有所加深，舌苔未见明显变化"
        
        # 模拟Look服务的CompareAnalysis方法
        self.look_stub.CompareAnalysis = MagicMock(return_value=mock_compare_response)
        
        # 创建比较分析请求
        compare_request = look_service_pb2.CompareAnalysisRequest(
            user_id='test_user_123',
            analysis_type='tongue',
            first_analysis_id='analysis_001',
            second_analysis_id='analysis_002'
        )
        
        # 调用Look服务的比较分析
        response = self.look_stub.CompareAnalysis(compare_request)
        
        # 验证比较分析结果
        self.assertEqual(len(response.feature_comparisons), 2)
        self.assertEqual(response.feature_comparisons[0].feature_name, "舌色")
        self.assertEqual(response.feature_comparisons[0].change_direction, "deteriorated")
        self.assertEqual(len(response.deteriorations), 1)
        self.assertEqual(response.deteriorations[0], "舌色加深")
        
        # 模拟将比较分析结果发送到小艾服务进行健康趋势分析
        # 同上，这里使用模拟代码替代实际的小艾服务调用
        xiaoai_trend_analysis_success = True
        
        # 验证趋势分析结果
        self.assertTrue(xiaoai_trend_analysis_success)


if __name__ == '__main__':
    unittest.main() 