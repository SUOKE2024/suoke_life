 """
闻诊服务测试模块
"""
import os
import sys
import unittest
import grpc
import tempfile
from concurrent import futures
import threading
import time
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.grpc import listen_service_pb2 as pb2
from api.grpc import listen_service_pb2_grpc as pb2_grpc
from internal.delivery.listen_service_impl import ListenServiceServicer

class TestListenService(unittest.TestCase):
    """闻诊服务单元测试"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        # 创建测试音频文件
        cls.test_audio_dir = tempfile.mkdtemp()
        cls.test_wav_path = os.path.join(cls.test_audio_dir, "test.wav")
        cls._create_test_audio(cls.test_wav_path)
        
        # 使用模拟的配置和存储库
        with patch('internal.delivery.listen_service_impl.get_config') as mock_config:
            mock_config.return_value = cls._mock_config()
            with patch('internal.delivery.listen_service_impl.get_audio_repository') as mock_repo:
                mock_repo.return_value = cls._mock_repository()
                with patch('internal.delivery.listen_service_impl.get_metrics') as mock_metrics:
                    mock_metrics.return_value = cls._mock_metrics()
                    
                    # 启动测试服务器
                    cls.server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
                    cls.service = ListenServiceServicer()
                    pb2_grpc.add_ListenServiceServicer_to_server(cls.service, cls.server)
                    cls.port = 50099  # 测试端口
                    cls.server.add_insecure_port(f'[::]:{cls.port}')
                    cls.server.start()
                    
                    # 创建客户端通道
                    cls.channel = grpc.insecure_channel(f'localhost:{cls.port}')
                    cls.stub = pb2_grpc.ListenServiceStub(cls.channel)
    
    @classmethod
    def tearDownClass(cls):
        """清理测试环境"""
        cls.channel.close()
        cls.server.stop(0)
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
    
    @classmethod
    def _mock_config(cls):
        """创建模拟配置"""
        mock = MagicMock()
        mock.config = {
            "server": {
                "host": "0.0.0.0",
                "port": 50099,
                "max_workers": 1
            },
            "models": {
                "voice_model": {
                    "path": "/tmp/mock_model",
                    "preload": False
                },
                "sound_model": {
                    "path": "/tmp/mock_model",
                    "preload": False
                },
                "emotion_model": {
                    "path": "/tmp/mock_model",
                    "preload": False
                }
            },
            "audio_processing": {
                "default_sample_rate": 16000,
                "supported_formats": ["wav", "mp3", "flac"]
            }
        }
        mock.get.return_value = mock.config
        return mock
    
    @classmethod
    def _mock_repository(cls):
        """创建模拟存储库"""
        mock = MagicMock()
        mock.save_voice_analysis.return_value = "mock_id"
        mock.save_sound_analysis.return_value = "mock_id"
        mock.save_emotion_analysis.return_value = "mock_id"
        mock.save_dialect_detection.return_value = "mock_id"
        mock.save_transcription.return_value = "mock_id"
        mock.save_batch_analysis.return_value = "mock_id"
        return mock
    
    @classmethod
    def _mock_metrics(cls):
        """创建模拟指标收集器"""
        mock = MagicMock()
        return mock
    
    def test_analyze_voice(self):
        """测试语音分析功能"""
        with open(self.test_wav_path, 'rb') as f:
            audio_data = f.read()
        
        request = pb2.VoiceAnalysisRequest(
            user_id="test_user",
            session_id="test_session",
            audio_data=audio_data,
            audio_format="wav",
            sample_rate=16000,
            channels=1,
            apply_preprocessing=True
        )
        
        # 调用服务
        response = self.stub.AnalyzeVoice(request)
        
        # 验证响应
        self.assertIsNotNone(response.analysis_id)
        # 确保有时间戳
        self.assertGreater(response.timestamp, 0)
    
    def test_analyze_sound(self):
        """测试声音分析功能"""
        with open(self.test_wav_path, 'rb') as f:
            audio_data = f.read()
        
        request = pb2.SoundAnalysisRequest(
            user_id="test_user",
            session_id="test_session",
            audio_data=audio_data,
            audio_format="wav",
            sample_rate=16000,
            sound_type=pb2.SoundType.COUGH,
            apply_preprocessing=True
        )
        
        # 调用服务
        response = self.stub.AnalyzeSound(request)
        
        # 验证响应
        self.assertIsNotNone(response.analysis_id)
        # 声音类型应该是请求的类型
        self.assertEqual(response.sound_type, pb2.SoundType.COUGH)
    
    def test_analyze_emotion(self):
        """测试情绪分析功能"""
        with open(self.test_wav_path, 'rb') as f:
            audio_data = f.read()
        
        request = pb2.EmotionAnalysisRequest(
            user_id="test_user",
            session_id="test_session",
            audio_data=audio_data,
            audio_format="wav",
            sample_rate=16000,
            text_transcript="这是一个测试文本"
        )
        
        # 调用服务
        response = self.stub.AnalyzeEmotion(request)
        
        # 验证响应
        self.assertIsNotNone(response.analysis_id)
        # 应该有情绪数据
        self.assertGreater(len(response.emotions), 0)
    
    def test_batch_analyze(self):
        """测试批量分析功能"""
        with open(self.test_wav_path, 'rb') as f:
            audio_data = f.read()
        
        request = pb2.BatchAnalysisRequest(
            user_id="test_user",
            session_id="test_session",
            audio_data=audio_data,
            audio_format="wav",
            sample_rate=16000,
            analysis_types=["voice", "sound", "emotion"]
        )
        
        # 调用服务
        response = self.stub.BatchAnalyze(request)
        
        # 验证响应
        self.assertIsNotNone(response.batch_id)
        # 应该包含请求的分析结果
        self.assertIsNotNone(response.voice_analysis.analysis_id)
        self.assertIsNotNone(response.sound_analysis.analysis_id)
        self.assertIsNotNone(response.emotion.analysis_id)
    
    def test_health_check(self):
        """测试健康检查功能"""
        request = pb2.HealthCheckRequest(include_details=True)
        
        # 调用服务
        response = self.stub.HealthCheck(request)
        
        # 验证响应
        self.assertEqual(response.status, pb2.HealthCheckResponse.SERVING)
        self.assertGreater(len(response.details), 0)


if __name__ == '__main__':
    unittest.main()