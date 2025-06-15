import pytest
import asyncio
import numpy as np
from unittest.mock import Mock, patch
from listen_service.core.audio_analyzer import AudioAnalyzer
from listen_service.models.audio_models import AudioFeatures, AnalysisRequest


class TestAudioAnalyzer:
    """音频分析器测试类"""
    
    @pytest.fixture
    def audio_analyzer(self):
        """创建音频分析器实例"""
        return AudioAnalyzer()
    
    @pytest.fixture
    def sample_audio_data(self):
        """创建示例音频数据"""
        # 生成1秒的正弦波音频数据 (44100 Hz)
        duration = 1.0
        sample_rate = 44100
        frequency = 440  # A4音符
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = np.sin(2 * np.pi * frequency * t)
        return audio_data, sample_rate
    
    @pytest.mark.asyncio
    async def test_audio_analyzer_initialization(self, audio_analyzer):
        """测试音频分析器初始化"""
        await audio_analyzer.initialize()
        assert audio_analyzer is not None
    
    @pytest.mark.asyncio
    async def test_extract_features(self, audio_analyzer, sample_audio_data):
        """测试特征提取"""
        audio_data, sample_rate = sample_audio_data
        
        with patch('librosa.load') as mock_load:
            mock_load.return_value = (audio_data, sample_rate)
            
            features = await audio_analyzer.extract_features(
                audio_data, sample_rate
            )
            
            assert isinstance(features, AudioFeatures)
            assert features.sample_rate == sample_rate
            assert features.duration > 0
            assert len(features.mfcc) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_audio_file(self, audio_analyzer, tmp_path):
        """测试音频文件分析"""
        # 创建临时音频文件路径
        audio_file = tmp_path / "test_audio.wav"
        
        # 模拟音频文件分析
        with patch('librosa.load') as mock_load:
            mock_load.return_value = (np.random.random(44100), 44100)
            
            request = AnalysisRequest(
                audio_file=str(audio_file),
                analysis_type="comprehensive"
            )
            
            result = await audio_analyzer.analyze_audio(request)
            
            assert result is not None
            assert result.status == "success"
    
    def test_calculate_spectral_features(self, audio_analyzer, sample_audio_data):
        """测试频谱特征计算"""
        audio_data, sample_rate = sample_audio_data
        
        features = audio_analyzer._calculate_spectral_features(
            audio_data, sample_rate
        )
        
        assert 'spectral_centroid' in features
        assert 'spectral_bandwidth' in features
        assert 'spectral_rolloff' in features
        assert 'zero_crossing_rate' in features
    
    def test_calculate_temporal_features(self, audio_analyzer, sample_audio_data):
        """测试时域特征计算"""
        audio_data, sample_rate = sample_audio_data
        
        features = audio_analyzer._calculate_temporal_features(
            audio_data, sample_rate
        )
        
        assert 'rms_energy' in features
        assert 'tempo' in features
        assert 'beat_frames' in features
    
    def test_calculate_mfcc_features(self, audio_analyzer, sample_audio_data):
        """测试MFCC特征计算"""
        audio_data, sample_rate = sample_audio_data
        
        mfcc = audio_analyzer._calculate_mfcc_features(
            audio_data, sample_rate
        )
        
        assert isinstance(mfcc, list)
        assert len(mfcc) > 0
        assert all(isinstance(coeff, float) for coeff in mfcc)
