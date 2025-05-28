"""
音频分析器单元测试

测试音频特征提取和分析功能。
"""

import pytest
import numpy as np
from unittest.mock import Mock, AsyncMock, patch
import asyncio

from listen_service.core.audio_analyzer import AudioAnalyzer, AudioProcessor
from listen_service.models.audio_models import (
    AudioMetadata, AudioFormat, AnalysisRequest, VoiceFeatures
)


class TestAudioProcessor:
    """音频处理器测试"""
    
    def test_init(self):
        """测试初始化"""
        processor = AudioProcessor()
        assert processor.sample_rate == 16000
        assert processor.frame_length == 2048
        assert processor.hop_length == 512
    
    def test_preprocess_audio(self):
        """测试音频预处理"""
        processor = AudioProcessor()
        
        # 创建测试音频数据
        audio_data = np.random.randn(16000).astype(np.float32)  # 1秒音频
        
        processed = processor.preprocess_audio(audio_data)
        
        assert isinstance(processed, np.ndarray)
        assert processed.dtype == np.float32
        assert len(processed) > 0
    
    def test_extract_mfcc_features(self):
        """测试MFCC特征提取"""
        processor = AudioProcessor()
        
        # 创建测试音频数据
        audio_data = np.random.randn(16000).astype(np.float32)
        
        mfcc_features = processor.extract_mfcc_features(audio_data)
        
        assert isinstance(mfcc_features, np.ndarray)
        assert mfcc_features.shape[0] == 13  # 13个MFCC系数
        assert mfcc_features.shape[1] > 0    # 时间帧数
    
    def test_extract_spectral_features(self):
        """测试频谱特征提取"""
        processor = AudioProcessor()
        
        # 创建测试音频数据
        audio_data = np.random.randn(16000).astype(np.float32)
        
        features = processor.extract_spectral_features(audio_data)
        
        assert isinstance(features, dict)
        assert "spectral_centroid" in features
        assert "spectral_bandwidth" in features
        assert "spectral_rolloff" in features
        assert "zero_crossing_rate" in features
        
        # 检查特征值的合理性
        for key, value in features.items():
            assert isinstance(value, (int, float, np.number))
            assert not np.isnan(value)
    
    def test_extract_prosodic_features(self):
        """测试韵律特征提取"""
        processor = AudioProcessor()
        
        # 创建测试音频数据
        audio_data = np.random.randn(16000).astype(np.float32)
        
        features = processor.extract_prosodic_features(audio_data)
        
        assert isinstance(features, dict)
        assert "fundamental_frequency" in features
        assert "pitch_variance" in features
        assert "energy" in features
        assert "rhythm_features" in features
        
        # 检查特征值的合理性
        for key, value in features.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    assert isinstance(sub_value, (int, float, np.number))
            else:
                assert isinstance(value, (int, float, np.number))


class TestAudioAnalyzer:
    """音频分析器测试"""
    
    @pytest.fixture
    def analyzer(self):
        """创建音频分析器实例"""
        return AudioAnalyzer()
    
    @pytest.fixture
    def sample_audio_request(self):
        """创建示例音频分析请求"""
        # 创建1秒的测试音频数据
        audio_data = (np.random.randn(16000) * 32767).astype(np.int16).tobytes()
        
        metadata = AudioMetadata(
            sample_rate=16000,
            channels=1,
            duration=1.0,
            format=AudioFormat.WAV,
            file_size=len(audio_data),
        )
        
        return AnalysisRequest(
            request_id="test-request-001",
            audio_data=audio_data,
            metadata=metadata,
            analysis_type="default",
        )
    
    @pytest.mark.asyncio
    async def test_analyze_audio_success(self, analyzer, sample_audio_request):
        """测试音频分析成功场景"""
        result = await analyzer.analyze_audio(sample_audio_request)
        
        assert result.success is True
        assert result.request_id == sample_audio_request.request_id
        assert result.voice_features is not None
        assert result.processing_time > 0
        assert result.error_message is None
        
        # 检查语音特征
        features = result.voice_features
        assert isinstance(features.mfcc_features, list)
        assert len(features.mfcc_features) > 0
        assert isinstance(features.spectral_features, dict)
        assert isinstance(features.prosodic_features, dict)
    
    @pytest.mark.asyncio
    async def test_analyze_audio_invalid_data(self, analyzer):
        """测试无效音频数据"""
        metadata = AudioMetadata(
            sample_rate=16000,
            channels=1,
            duration=0.0,
            format=AudioFormat.WAV,
            file_size=0,
        )
        
        request = AnalysisRequest(
            request_id="test-invalid",
            audio_data=b"",  # 空音频数据
            metadata=metadata,
            analysis_type="default",
        )
        
        result = await analyzer.analyze_audio(request)
        
        assert result.success is False
        assert result.error_message is not None
        assert "音频数据为空" in result.error_message
    
    @pytest.mark.asyncio
    async def test_analyze_audio_with_caching(self, analyzer, sample_audio_request):
        """测试带缓存的音频分析"""
        # 启用缓存
        sample_audio_request.enable_caching = True
        
        # 第一次分析
        result1 = await analyzer.analyze_audio(sample_audio_request)
        assert result1.success is True
        
        # 第二次分析（应该从缓存获取）
        result2 = await analyzer.analyze_audio(sample_audio_request)
        assert result2.success is True
        
        # 结果应该相同
        assert result1.voice_features.mfcc_features == result2.voice_features.mfcc_features
    
    @pytest.mark.asyncio
    async def test_get_analysis_stats(self, analyzer, sample_audio_request):
        """测试获取分析统计"""
        # 执行一些分析
        await analyzer.analyze_audio(sample_audio_request)
        
        stats = await analyzer.get_analysis_stats()
        
        assert isinstance(stats, dict)
        assert "total_analyses" in stats
        assert "successful_analyses" in stats
        assert "failed_analyses" in stats
        assert "average_processing_time" in stats
        assert stats["total_analyses"] >= 1
    
    @pytest.mark.asyncio
    async def test_concurrent_analysis(self, analyzer):
        """测试并发分析"""
        # 创建多个分析请求
        requests = []
        for i in range(5):
            audio_data = (np.random.randn(8000) * 32767).astype(np.int16).tobytes()
            metadata = AudioMetadata(
                sample_rate=16000,
                channels=1,
                duration=0.5,
                format=AudioFormat.WAV,
                file_size=len(audio_data),
            )
            
            request = AnalysisRequest(
                request_id=f"concurrent-test-{i}",
                audio_data=audio_data,
                metadata=metadata,
                analysis_type="default",
            )
            requests.append(request)
        
        # 并发执行分析
        tasks = [analyzer.analyze_audio(req) for req in requests]
        results = await asyncio.gather(*tasks)
        
        # 检查所有结果
        assert len(results) == 5
        for result in results:
            assert result.success is True
            assert result.voice_features is not None
    
    def test_convert_audio_bytes_to_numpy(self, analyzer):
        """测试音频字节转换为numpy数组"""
        # 创建测试音频数据
        audio_data = (np.random.randn(1000) * 32767).astype(np.int16).tobytes()
        
        numpy_array = analyzer._convert_audio_bytes_to_numpy(audio_data, channels=1)
        
        assert isinstance(numpy_array, np.ndarray)
        assert numpy_array.dtype == np.float32
        assert len(numpy_array) == 1000
        assert numpy_array.min() >= -1.0
        assert numpy_array.max() <= 1.0
    
    def test_validate_audio_data(self, analyzer):
        """测试音频数据验证"""
        # 有效数据
        valid_data = (np.random.randn(1000) * 32767).astype(np.int16).tobytes()
        assert analyzer._validate_audio_data(valid_data, min_duration=0.01) is True
        
        # 无效数据（空）
        assert analyzer._validate_audio_data(b"", min_duration=0.01) is False
        
        # 无效数据（太短）
        short_data = (np.random.randn(10) * 32767).astype(np.int16).tobytes()
        assert analyzer._validate_audio_data(short_data, min_duration=1.0) is False


@pytest.mark.integration
class TestAudioAnalyzerIntegration:
    """音频分析器集成测试"""
    
    @pytest.mark.asyncio
    async def test_real_audio_analysis_pipeline(self):
        """测试真实音频分析流水线"""
        analyzer = AudioAnalyzer()
        
        # 创建更真实的音频数据（正弦波）
        duration = 2.0  # 2秒
        sample_rate = 16000
        frequency = 440  # A4音符
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_signal = np.sin(2 * np.pi * frequency * t)
        audio_data = (audio_signal * 32767).astype(np.int16).tobytes()
        
        metadata = AudioMetadata(
            sample_rate=sample_rate,
            channels=1,
            duration=duration,
            format=AudioFormat.WAV,
            file_size=len(audio_data),
        )
        
        request = AnalysisRequest(
            request_id="integration-test",
            audio_data=audio_data,
            metadata=metadata,
            analysis_type="detailed",
        )
        
        result = await analyzer.analyze_audio(request)
        
        assert result.success is True
        assert result.voice_features is not None
        
        # 检查特征的合理性
        features = result.voice_features
        
        # MFCC特征应该存在
        assert len(features.mfcc_features) > 0
        
        # 频谱特征应该合理
        assert features.spectral_features["spectral_centroid"] > 0
        assert features.spectral_features["spectral_bandwidth"] > 0
        
        # 韵律特征应该合理
        assert features.prosodic_features["energy"] > 0
        
        # 基频应该接近440Hz（允许一定误差）
        f0 = features.prosodic_features["fundamental_frequency"]
        assert 400 <= f0 <= 480  # 允许±40Hz误差
    
    @pytest.mark.asyncio
    async def test_performance_under_load(self):
        """测试负载下的性能"""
        analyzer = AudioAnalyzer()
        
        # 创建多个不同长度的音频请求
        requests = []
        for i in range(10):
            duration = 0.5 + i * 0.1  # 0.5到1.4秒
            sample_rate = 16000
            
            audio_signal = np.random.randn(int(sample_rate * duration))
            audio_data = (audio_signal * 32767).astype(np.int16).tobytes()
            
            metadata = AudioMetadata(
                sample_rate=sample_rate,
                channels=1,
                duration=duration,
                format=AudioFormat.WAV,
                file_size=len(audio_data),
            )
            
            request = AnalysisRequest(
                request_id=f"load-test-{i}",
                audio_data=audio_data,
                metadata=metadata,
                analysis_type="default",
            )
            requests.append(request)
        
        # 测量处理时间
        import time
        start_time = time.time()
        
        tasks = [analyzer.analyze_audio(req) for req in requests]
        results = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        
        # 检查结果
        assert len(results) == 10
        successful_results = [r for r in results if r.success]
        assert len(successful_results) >= 8  # 至少80%成功率
        
        # 性能检查
        avg_time_per_request = total_time / len(requests)
        assert avg_time_per_request < 2.0  # 平均每个请求不超过2秒
        
        print(f"处理{len(requests)}个请求总时间: {total_time:.2f}秒")
        print(f"平均每个请求时间: {avg_time_per_request:.2f}秒") 