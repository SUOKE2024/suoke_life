"""
现代化测试配置

为 listen-service 提供全面的测试配置，支持异步测试、音频测试、
集成测试和性能测试。基于 Python 3.13.3 和 pytest 最佳实践。
"""

import asyncio
import os
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Generator, Dict, Any
import uuid

import numpy as np
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
import librosa

# 测试配置
pytest_plugins = ["pytest_asyncio"]


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings():
    """测试配置"""
    from listen_service.config.settings import Settings, Environment
    
    return Settings(
        environment=Environment.TESTING,
        debug=True,
        cache={"enabled": False},  # 测试时禁用缓存
        database={"mongodb_url": "mongodb://localhost:27017/test_listen_service"},
        server={"port": 50053},  # 使用不同端口避免冲突
        logging={"level": "DEBUG", "console_enabled": True, "file_enabled": False},
    )


@pytest.fixture
def mock_audio_analyzer():
    """模拟音频分析器"""
    from listen_service.core.audio_analyzer import AudioAnalyzer
    from listen_service.models.audio_models import VoiceFeatures, AudioAnalysisResponse
    from listen_service.models.tcm_models import TCMDiagnosis
    
    analyzer = AsyncMock(spec=AudioAnalyzer)
    
    # 模拟分析结果
    mock_features = VoiceFeatures(
        mfcc=np.random.rand(13, 100),
        spectral_features={
            "spectral_centroids": np.random.rand(100),
            "spectral_bandwidth": np.random.rand(100),
        },
        prosodic_features={
            "f0_mean": 150.0,
            "f0_std": 20.0,
            "speech_rate": 2.5,
        },
        voice_quality={
            "harmonic_noise_ratio": 0.8,
            "spectral_flatness": 0.3,
        },
    )
    
    mock_tcm = TCMDiagnosis(
        constitution_type="平和质",
        emotion_state="平静",
        organ_analysis={},
        confidence_score=0.85,
    )
    
    mock_response = AudioAnalysisResponse(
        request_id=str(uuid.uuid4()),
        voice_features=mock_features,
        tcm_diagnosis=mock_tcm,
        processing_time=1.5,
    )
    
    analyzer.analyze_audio.return_value = mock_response
    analyzer.get_performance_stats.return_value = {
        "total_processed": 10,
        "average_processing_time": 1.2,
        "cache_hits": 5,
        "cache_misses": 5,
    }
    
    return analyzer


@pytest.fixture
def sample_audio_data():
    """生成示例音频数据"""
    # 生成 1 秒的正弦波音频（440Hz，A4音符）
    sample_rate = 16000
    duration = 1.0
    frequency = 440.0
    
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio_data = 0.5 * np.sin(2 * np.pi * frequency * t)
    
    return {
        "audio_array": audio_data.astype(np.float32),
        "sample_rate": sample_rate,
        "duration": duration,
        "frequency": frequency,
    }


@pytest.fixture
def audio_analysis_request():
    """音频分析请求示例"""
    from listen_service.models.audio_models import AudioAnalysisRequest, AnalysisType
    
    return AudioAnalysisRequest(
        analysis_types=[
            AnalysisType.VOICE_FEATURES,
            AnalysisType.TCM_DIAGNOSIS,
            AnalysisType.EMOTION_ANALYSIS,
        ],
        sample_rate=16000,
        enable_enhancement=True,
        enable_vad=True,
        tcm_analysis_enabled=True,
        use_cache=False,  # 测试时禁用缓存
    )


# 测试标记
def pytest_configure(config):
    """配置 pytest 标记"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "audio: marks tests that require audio processing"
    )
    config.addinivalue_line(
        "markers", "gpu: marks tests that require GPU"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    ) 