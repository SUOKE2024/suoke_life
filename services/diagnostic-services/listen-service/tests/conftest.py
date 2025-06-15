"""
测试配置文件

提供测试用的fixtures和配置。
"""

import asyncio
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from listen_service.config.settings import get_settings
from listen_service.delivery.rest_api import create_app
from listen_service.utils.cache import AudioCache, MemoryCache


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """临时目录fixture"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def test_settings(temp_dir: Path):
    """测试设置"""
    from listen_service.config.settings import Settings
    
    # 创建测试配置
    test_config = {
        "environment": "test",
        "server": {
            "host": "127.0.0.1",
            "port": 8004,
            "reload": False,
            "workers": 1
        },
        "cache": {
            "backend": "memory",
            "max_size": 100,
            "default_ttl": 300
        },
        "redis": {
            "url": "redis://localhost:6379/15",
            "prefix": "test_listen_service:"
        }
    }
    
    settings = Settings(**test_config)
    return settings


@pytest.fixture
async def cache() -> AsyncGenerator[AudioCache, None]:
    """缓存fixture"""
    cache_instance = AudioCache(backend=MemoryCache(max_size=100, default_ttl=300))
    yield cache_instance
    await cache_instance.cleanup()


@pytest.fixture
def app(test_settings):
    """FastAPI应用fixture"""
    return create_app()


@pytest.fixture
def client(app) -> TestClient:
    """测试客户端fixture"""
    return TestClient(app)


@pytest.fixture
def sample_audio_file(temp_dir: Path) -> Path:
    """示例音频文件fixture"""
    import numpy as np
    import soundfile as sf
    
    # 生成1秒的正弦波音频
    sample_rate = 22050
    duration = 1.0
    frequency = 440.0  # A4音符
    
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio_data = np.sin(2 * np.pi * frequency * t)
    
    audio_file = temp_dir / "test_audio.wav"
    sf.write(str(audio_file), audio_data, sample_rate)
    
    return audio_file


@pytest.fixture
def sample_audio_files(temp_dir: Path) -> list[Path]:
    """多个示例音频文件fixture"""
    import numpy as np
    import soundfile as sf
    
    files = []
    sample_rate = 22050
    duration = 1.0
    
    for i, frequency in enumerate([440.0, 523.25, 659.25]):  # A4, C5, E5
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = np.sin(2 * np.pi * frequency * t)
        
        audio_file = temp_dir / f"test_audio_{i}.wav"
        sf.write(str(audio_file), audio_data, sample_rate)
        files.append(audio_file)
    
    return files


@pytest.fixture
def mock_user_id() -> str:
    """模拟用户ID"""
    return "test_user_123"


@pytest.fixture
def mock_session_id() -> str:
    """模拟会话ID"""
    return "test_session_456"


@pytest.fixture
def sample_request_data(sample_audio_file: Path, mock_user_id: str) -> dict:
    """示例请求数据"""
    return {
        "file_path": str(sample_audio_file),
        "analysis_type": "basic",
        "user_id": mock_user_id,
        "language": "zh-CN"
    }


@pytest.fixture
def sample_tcm_request_data(sample_audio_file: Path, mock_user_id: str) -> dict:
    """示例中医请求数据"""
    return {
        "file_path": str(sample_audio_file),
        "user_id": mock_user_id,
        "constitution_type": "平和质",
        "symptoms": ["咳嗽", "气短"],
        "context": {
            "age": 30,
            "gender": "male",
            "medical_history": []
        }
    }


# 标记配置
pytest_plugins = ["pytest_asyncio"]


def pytest_configure(config):
    """Pytest配置"""
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
        "markers", "gpu: marks tests that require GPU"
    )
    config.addinivalue_line(
        "markers", "benchmark: marks performance benchmark tests"
    )


def pytest_collection_modifyitems(config, items):
    """修改测试项目"""
    # 为没有标记的测试添加unit标记
    for item in items:
        if not any(mark.name in ["unit", "integration", "slow", "gpu", "benchmark"] 
                  for mark in item.iter_markers()):
            item.add_marker(pytest.mark.unit)


# 异步测试配置
@pytest_asyncio.fixture(scope="session")
async def async_session_setup():
    """异步会话设置"""
    # 这里可以添加全局异步设置
    yield
    # 清理代码
