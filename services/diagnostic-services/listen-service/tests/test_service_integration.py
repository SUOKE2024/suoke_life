"""
闻诊服务集成测试

整合了原有的服务级别测试，使用现代化的 pytest 框架。
"""

import pytest
import grpc
import tempfile
import os
import numpy as np
import soundfile as sf

from listen_service.delivery.grpc_server import ListenServiceGRPCServer
from listen_service.core.audio_analyzer import AudioAnalyzer
from listen_service.core.tcm_analyzer import TCMFeatureExtractor
from listen_service.utils.cache import AudioCache, MemoryCache

class TestListenServiceIntegration:
    """闻诊服务集成测试"""
    
    @pytest.fixture(scope="class")
    def test_audio_file(self):
        """创建测试音频文件"""
        temp_dir = tempfile.mkdtemp()
        test_wav_path = os.path.join(temp_dir, "test.wav")
        
        # 创建一个简单的正弦波音频
        sample_rate = 16000
        duration = 1.0  # 秒
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)  # 440 Hz 正弦波
        
        # 保存为 WAV 文件
        sf.write(test_wav_path, audio, sample_rate)
        
        yield test_wav_path
        
        # 清理
        os.remove(test_wav_path)
        os.rmdir(temp_dir)
    
    @pytest.fixture(scope="function")
    async def grpc_server(self):
        """启动测试 gRPC 服务器"""
        # 创建组件
        cache = AudioCache(MemoryCache())
        audio_analyzer = AudioAnalyzer(cache_enabled=True)
        tcm_analyzer = TCMFeatureExtractor()
        
        # 创建服务器
        server = ListenServiceGRPCServer(
            audio_analyzer=audio_analyzer,
            tcm_analyzer=tcm_analyzer,
            cache=cache,
        )
        
        # 启动服务器
        port = 50099  # 测试端口
        await server.start_server(host="localhost", port=port)
        
        yield server, port
        
        # 停止服务器
        await server.stop_server()
    
    @pytest.fixture
    def grpc_client(self, grpc_server):
        """创建 gRPC 客户端"""
        server, port = grpc_server
        
        # 创建客户端通道
        channel = grpc.insecure_channel(f'localhost:{port}')
        
        # 这里需要根据实际的 protobuf 定义创建 stub
        # stub = pb2_grpc.ListenServiceStub(channel)
        
        yield channel  # 暂时返回 channel，实际使用时需要返回 stub
        
        # 关闭通道
        channel.close()
    
    @pytest.mark.asyncio
    async def test_voice_analysis_integration(self, test_audio_file, grpc_client):
        """测试语音分析集成功能"""
        # 读取测试音频
        with open(test_audio_file, 'rb') as f:
            audio_data = f.read()
        
        # 这里需要根据实际的 protobuf 定义创建请求
        # request = pb2.VoiceAnalysisRequest(
        #     user_id="test_user",
        #     session_id="test_session",
        #     audio_data=audio_data,
        #     audio_format="wav",
        #     sample_rate=16000,
        #     channels=1,
        #     apply_preprocessing=True
        # )
        
        # 调用服务
        # response = grpc_client.AnalyzeVoice(request)
        
        # 验证响应
        # assert response.analysis_id is not None
        # assert response.timestamp > 0
        
        # 暂时跳过实际的 gRPC 调用，因为需要完整的 protobuf 定义
        pytest.skip("需要完整的 protobuf 定义才能执行")
    
    @pytest.mark.asyncio
    async def test_sound_analysis_integration(self, test_audio_file, grpc_client):
        """测试声音分析集成功能"""
        # 读取测试音频
        with open(test_audio_file, 'rb') as f:
            audio_data = f.read()
        
        # 暂时跳过，原因同上
        pytest.skip("需要完整的 protobuf 定义才能执行")
    
    @pytest.mark.asyncio
    async def test_emotion_analysis_integration(self, test_audio_file, grpc_client):
        """测试情绪分析集成功能"""
        # 读取测试音频
        with open(test_audio_file, 'rb') as f:
            audio_data = f.read()
        
        # 暂时跳过，原因同上
        pytest.skip("需要完整的 protobuf 定义才能执行")
    
    @pytest.mark.asyncio
    async def test_batch_analysis_integration(self, test_audio_file, grpc_client):
        """测试批量分析集成功能"""
        # 暂时跳过，原因同上
        pytest.skip("需要完整的 protobuf 定义才能执行")
    
    @pytest.mark.asyncio
    async def test_health_check_integration(self, grpc_client):
        """测试健康检查集成功能"""
        # 暂时跳过，原因同上
        pytest.skip("需要完整的 protobuf 定义才能执行")

@pytest.mark.performance
class TestListenServicePerformance:
    """闻诊服务性能测试"""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests_performance(self):
        """测试并发请求性能"""
        # 这里可以添加性能测试逻辑
        pytest.skip("性能测试需要完整的服务实现")
    
    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self):
        """测试负载下的内存使用"""
        # 这里可以添加内存使用测试逻辑
        pytest.skip("内存测试需要完整的服务实现") 