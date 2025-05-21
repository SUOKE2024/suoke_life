"""
闻诊服务集成测试模块
测试闻诊服务与其他服务的集成功能
"""
import os
import sys
import unittest
import grpc
import json
import tempfile
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from api.grpc import listen_service_pb2 as pb2
from api.grpc import listen_service_pb2_grpc as pb2_grpc
from internal.integration.four_diagnosis_coordinator import FourDiagnosisCoordinator

class TestListenServiceIntegration(unittest.TestCase):
    """闻诊服务集成测试"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        # 创建测试音频文件
        cls.test_audio_dir = tempfile.mkdtemp()
        cls.test_wav_path = os.path.join(cls.test_audio_dir, "test.wav")
        cls._create_test_audio(cls.test_wav_path)
        
        # 创建测试配置
        cls.test_config = {
            "integration": {
                "xiaoai_service": {
                    "host": "localhost",
                    "port": 50060,
                    "timeout": 5
                },
                "inquiry_service": {
                    "host": "localhost",
                    "port": 50053,
                    "timeout": 5
                },
                "look_service": {
                    "host": "localhost",
                    "port": 50051,
                    "timeout": 5
                },
                "palpation_service": {
                    "host": "localhost",
                    "port": 50054,
                    "timeout": 5
                }
            }
        }
    
    @classmethod
    def tearDownClass(cls):
        """清理测试环境"""
        # 删除测试文件
        os.remove(cls.test_wav_path)
        os.rmdir(cls.test_audio_dir)
    
    @classmethod
    def _create_test_audio(cls, file_path):
        """创建测试用音频文件"""
        try:
            import numpy as np
            import soundfile as sf
            
            # 创建一个简单的正弦波音频
            sample_rate = 16000
            duration = 1.0  # 秒
            t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
            audio = 0.5 * np.sin(2 * np.pi * 440 * t)  # 440 Hz 正弦波
            
            # 保存为 WAV 文件
            sf.write(file_path, audio, sample_rate)
        except ImportError:
            # 如果没有安装 soundfile，创建一个空文件
            with open(file_path, 'wb') as f:
                f.write(b'\x00' * 1000)
    
    def test_four_diagnosis_integration(self):
        """测试四诊集成功能"""
        # 模拟配置加载
        with patch('internal.integration.four_diagnosis_coordinator.get_config') as mock_config:
            mock_config.return_value.get.return_value = self.test_config
            
            # 模拟其他服务客户端
            with patch('internal.integration.four_diagnosis_coordinator.grpc.insecure_channel') as mock_channel:
                # 模拟grpc客户端存根
                mock_inquiry_stub = MagicMock()
                mock_look_stub = MagicMock()
                mock_palpation_stub = MagicMock()
                mock_xiaoai_stub = MagicMock()
                
                # 设置模拟响应
                mock_inquiry_response = MagicMock()
                mock_inquiry_response.diagnosis_id = "inq123"
                mock_inquiry_response.tcm_patterns = {"湿热": 0.8, "气虚": 0.5}
                mock_inquiry_stub.GetInquiryDiagnosis.return_value = mock_inquiry_response
                
                mock_look_response = MagicMock()
                mock_look_response.diagnosis_id = "look123"
                mock_look_response.tcm_patterns = {"阳虚": 0.7, "血瘀": 0.6}
                mock_look_stub.GetLookDiagnosis.return_value = mock_look_response
                
                mock_palpation_response = MagicMock()
                mock_palpation_response.diagnosis_id = "palp123"
                mock_palpation_response.tcm_patterns = {"痰湿": 0.9, "肝郁": 0.4}
                mock_palpation_stub.GetPalpationDiagnosis.return_value = mock_palpation_response
                
                # 设置通道创建返回的不同客户端
                def side_effect(address):
                    mock_channel_obj = MagicMock()
                    if "inquiry_service" in str(address):
                        # 创建一个Mock对象，使其能够正确地返回inquiry_stub
                        mock_channel_obj._channel = MagicMock()
                        return mock_channel_obj
                    elif "look_service" in str(address):
                        # 类似地，返回不同的mock对象
                        mock_channel_obj._channel = MagicMock()
                        return mock_channel_obj
                    elif "palpation_service" in str(address):
                        mock_channel_obj._channel = MagicMock()
                        return mock_channel_obj
                    elif "xiaoai_service" in str(address):
                        mock_channel_obj._channel = MagicMock()
                        return mock_channel_obj
                    return mock_channel_obj
                
                mock_channel.side_effect = side_effect
                
                # 模拟gRPC存根创建
                with patch('internal.integration.four_diagnosis_coordinator.inquiry_pb2_grpc.InquiryServiceStub') as mock_inquiry_service:
                    with patch('internal.integration.four_diagnosis_coordinator.look_pb2_grpc.LookServiceStub') as mock_look_service:
                        with patch('internal.integration.four_diagnosis_coordinator.palpation_pb2_grpc.PalpationServiceStub') as mock_palpation_service:
                            with patch('internal.integration.four_diagnosis_coordinator.xiaoai_pb2_grpc.XiaoaiServiceStub') as mock_xiaoai_service:
                                mock_inquiry_service.return_value = mock_inquiry_stub
                                mock_look_service.return_value = mock_look_stub
                                mock_palpation_service.return_value = mock_palpation_stub
                                mock_xiaoai_service.return_value = mock_xiaoai_stub
                                
                                # 创建协调器
                                coordinator = FourDiagnosisCoordinator()
                                
                                # 创建闻诊结果
                                listen_result = pb2.ListenDiagnosisResult(
                                    diagnosis_id="listen123",
                                    tcm_patterns={"气虚": 0.7, "湿热": 0.6},
                                    constitution_relevance={"气虚质": 0.8, "湿热质": 0.7},
                                    analysis_summary="语音分析显示气虚特征明显，兼有湿热",
                                    confidence=0.85
                                )
                                
                                # 调用四诊合参
                                result = coordinator.integrate_with_other_diagnostics(
                                    user_id="test123",
                                    session_id="session456",
                                    listen_diagnosis=listen_result
                                )
                                
                                # 验证结果
                                self.assertIsNotNone(result)
                                self.assertIsInstance(result, dict)
                                self.assertIn("integrated_diagnosis", result)
                                self.assertIn("combined_patterns", result)
                                
                                # 验证是否调用了其他服务的方法
                                mock_inquiry_stub.GetInquiryDiagnosis.assert_called_once()
                                mock_look_stub.GetLookDiagnosis.assert_called_once()
                                mock_palpation_stub.GetPalpationDiagnosis.assert_called_once()

    def test_error_handling_missing_service(self):
        """测试当某个服务不可用时的错误处理"""
        # 模拟配置加载
        with patch('internal.integration.four_diagnosis_coordinator.get_config') as mock_config:
            mock_config.return_value.get.return_value = self.test_config
            
            # 模拟grpc连接错误
            with patch('internal.integration.four_diagnosis_coordinator.grpc.insecure_channel') as mock_channel:
                # 设置某个服务连接抛出异常
                def side_effect(address):
                    if "inquiry_service" in str(address):
                        raise grpc.RpcError("模拟服务不可用")
                    mock_channel_obj = MagicMock()
                    mock_channel_obj._channel = MagicMock()
                    return mock_channel_obj
                
                mock_channel.side_effect = side_effect
                
                # 模拟gRPC存根创建
                with patch('internal.integration.four_diagnosis_coordinator.inquiry_pb2_grpc.InquiryServiceStub') as mock_inquiry_service:
                    with patch('internal.integration.four_diagnosis_coordinator.look_pb2_grpc.LookServiceStub') as mock_look_service:
                        with patch('internal.integration.four_diagnosis_coordinator.palpation_pb2_grpc.PalpationServiceStub') as mock_palpation_service:
                            with patch('internal.integration.four_diagnosis_coordinator.xiaoai_pb2_grpc.XiaoaiServiceStub') as mock_xiaoai_service:
                                # 创建mock stubs
                                mock_look_stub = MagicMock()
                                mock_palpation_stub = MagicMock()
                                mock_xiaoai_stub = MagicMock()
                                
                                # 设置模拟响应
                                mock_look_response = MagicMock()
                                mock_look_response.diagnosis_id = "look123"
                                mock_look_response.tcm_patterns = {"阳虚": 0.7, "血瘀": 0.6}
                                mock_look_stub.GetLookDiagnosis.return_value = mock_look_response
                                
                                mock_palpation_response = MagicMock()
                                mock_palpation_response.diagnosis_id = "palp123"
                                mock_palpation_response.tcm_patterns = {"痰湿": 0.9, "肝郁": 0.4}
                                mock_palpation_stub.GetPalpationDiagnosis.return_value = mock_palpation_response
                                
                                # 设置返回值
                                mock_look_service.return_value = mock_look_stub
                                mock_palpation_service.return_value = mock_palpation_stub
                                mock_xiaoai_service.return_value = mock_xiaoai_stub
                                
                                # 创建协调器
                                coordinator = FourDiagnosisCoordinator()
                                
                                # 创建闻诊结果
                                listen_result = pb2.ListenDiagnosisResult(
                                    diagnosis_id="listen123",
                                    tcm_patterns={"气虚": 0.7, "湿热": 0.6},
                                    constitution_relevance={"气虚质": 0.8, "湿热质": 0.7},
                                    analysis_summary="语音分析显示气虚特征明显，兼有湿热",
                                    confidence=0.85
                                )
                                
                                # 调用四诊合参 - 应该能处理问诊服务不可用的情况
                                result = coordinator.integrate_with_other_diagnostics(
                                    user_id="test123",
                                    session_id="session456",
                                    listen_diagnosis=listen_result
                                )
                                
                                # 验证结果 - 应该仍然返回结果，但只包含可用的服务数据
                                self.assertIsNotNone(result)
                                self.assertIsInstance(result, dict)
                                self.assertIn("integrated_diagnosis", result)
                                self.assertIn("combined_patterns", result)
                                self.assertIn("available_services", result)
                                # 问诊服务应该标记为不可用
                                self.assertNotIn("inquiry", result["available_services"])


if __name__ == '__main__':
    unittest.main() 