#!/usr/bin/env python

"""
pytest配置文件
提供测试夹具和全局配置
"""

import asyncio
import os

# 添加项目根目录到Python路径
import sys
import tempfile
from pathlib import Path
from typing import Any, AsyncGenerator, Dict
from unittest.mock import AsyncMock, Mock

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.unified_config import UnifiedConfigManager


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_config_file():
    """创建临时配置文件"""
    config_data = {
        "service": {
            "name": "test-accessibility-service",
            "version": "2.0.0-test",
            "host": "127.0.0.1",
            "port": 50051,
            "data_root": "/tmp/test-accessibility-service",
            "debug": True,
        },
        "models": {
            "scene_model": "test/scene-model",
            "sign_language_model": "test/sign-model",
            "speech_model": {
                "asr": "test/asr-model",
                "tts": "test/tts-model",
            },
            "conversion_model": "test/conversion-model",
        },
        "logging": {
            "level": "DEBUG",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": None,  # 测试时不写文件
            "max_size_mb": 10,
            "backup_count": 2,
        },
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "test_accessibility_db",
            "user": "test_user",
            "password": "test_password",
            "pool_size": 2,
            "max_overflow": 5,
        },
        "features": {
            "blind_assistance": {
                "enabled": True,
                "max_image_size": 512,
                "confidence_threshold": 0.5,
            },
            "sign_language": {
                "enabled": True,
                "supported_languages": ["zh-CN"],
            },
            "screen_reading": {
                "enabled": True,
                "confidence_threshold": 0.5,
            },
            "voice_assistance": {
                "enabled": True,
                "supported_dialects": ["mandarin"],
            },
            "content_conversion": {
                "enabled": True,
                "supported_formats": ["audio"],
            },
        },
        "cache": {
            "memory_max_size_mb": 64,
            "memory_max_items": 1000,
            "redis_enabled": False,
            "disk_enabled": False,
            "disk_cache_dir": "/tmp/test_cache",
            "cleanup_interval_seconds": 60,
        },
        "security": {
            "encryption_enabled": False,  # 测试时关闭加密
            "jwt_secret": "test-secret-key",
            "jwt_expiry_hours": 1,
            "rate_limit_per_minute": 1000,
        },
        "performance": {
            "max_memory_mb": 1024,
            "cleanup_interval_seconds": 60,
            "model_ttl_seconds": 300,
            "worker_threads": 2,
        },
        "integration": {
            "xiaoai_service": {
                "host": "localhost",
                "port": 50052,
                "timeout_ms": 1000,
                "retry": 1,
            },
            "xiaoke_service": {
                "host": "localhost",
                "port": 50053,
                "timeout_ms": 1000,
                "retry": 1,
            },
            "laoke_service": {
                "host": "localhost",
                "port": 50054,
                "timeout_ms": 1000,
                "retry": 1,
            },
            "soer_service": {
                "host": "localhost",
                "port": 50055,
                "timeout_ms": 1000,
                "retry": 1,
            },
        },
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
        temp_path = f.name

    yield temp_path

    # 清理
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def test_config(temp_config_file):
    """测试配置管理器"""
    config_manager = UnifiedConfigManager(
        config_path=temp_config_file,
        watch_changes=False,  # 测试时不监控文件变更
        validate_config=True,
    )
    yield config_manager
    config_manager.cleanup()


@pytest.fixture
def mock_model():
    """模拟模型"""
    model = Mock()
    model.predict = AsyncMock(return_value={"result": "test"})
    model.load = AsyncMock()
    model.unload = AsyncMock()
    return model


@pytest.fixture
def mock_database():
    """模拟数据库连接"""
    db = Mock()
    db.connect = AsyncMock()
    db.disconnect = AsyncMock()
    db.execute = AsyncMock()
    db.fetch = AsyncMock(return_value=[])
    db.fetchone = AsyncMock(return_value=None)
    return db


@pytest.fixture
def mock_cache():
    """模拟缓存"""
    cache = Mock()
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock()
    cache.delete = AsyncMock()
    cache.clear = AsyncMock()
    return cache


@pytest.fixture
def sample_image_data():
    """示例图像数据"""
    # 创建一个简单的测试图像数据
    return b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"


@pytest.fixture
def sample_audio_data():
    """示例音频数据"""
    # 创建一个简单的测试音频数据
    return b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"


@pytest.fixture
def sample_text_data():
    """示例文本数据"""
    return {
        "chinese": "这是一个测试文本",
        "english": "This is a test text",
        "long_text": "这是一个很长的测试文本，用于测试文本处理功能。" * 10,
    }


@pytest.fixture
async def async_test_client():
    """异步测试客户端"""
    # 这里可以创建实际的测试客户端
    # 目前返回一个模拟客户端
    client = Mock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.put = AsyncMock()
    client.delete = AsyncMock()
    yield client


@pytest.fixture
def test_data_dir():
    """测试数据目录"""
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    yield data_dir


@pytest.fixture
def cleanup_test_files():
    """清理测试文件"""
    test_files = []

    def add_file(file_path):
        test_files.append(file_path)

    yield add_file

    # 清理所有测试文件
    for file_path in test_files:
        if os.path.exists(file_path):
            if os.path.isdir(file_path):
                import shutil

                shutil.rmtree(file_path)
            else:
                os.unlink(file_path)


# 测试标记
pytest_plugins = []


# 自定义标记
def pytest_configure(config):
    """配置pytest"""
    config.addinivalue_line("markers", "unit: 单元测试")
    config.addinivalue_line("markers", "integration: 集成测试")
    config.addinivalue_line("markers", "slow: 慢速测试")
    config.addinivalue_line("markers", "gpu: 需要GPU的测试")
    config.addinivalue_line("markers", "network: 需要网络的测试")


# 测试收集钩子
def pytest_collection_modifyitems(config, items):
    """修改测试项"""
    # 为没有标记的测试添加unit标记
    for item in items:
        if not any(item.iter_markers()):
            item.add_marker(pytest.mark.unit)


# 测试报告钩子
def pytest_html_report_title(report):
    """自定义HTML报告标题"""
    report.title = "索克生活无障碍服务测试报告"


# 环境变量设置
@pytest.fixture(autouse=True)
def setup_test_env():
    """设置测试环境变量"""
    # 设置测试环境变量
    os.environ["TESTING"] = "true"
    os.environ["LOG_LEVEL"] = "DEBUG"

    yield

    # 清理环境变量
    os.environ.pop("TESTING", None)
    os.environ.pop("LOG_LEVEL", None)


# 异步测试支持
@pytest.fixture
def anyio_backend():
    """anyio后端"""
    return "asyncio"


# 性能测试夹具
@pytest.fixture
def performance_monitor():
    """性能监控器"""
    import time

    import psutil

    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.start_memory = None

        def start(self):
            self.start_time = time.time()
            self.start_memory = psutil.Process().memory_info().rss

        def stop(self):
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss

            return {
                "duration": end_time - self.start_time,
                "memory_delta": end_memory - self.start_memory,
                "peak_memory": end_memory,
            }

    return PerformanceMonitor()


# 日志捕获
@pytest.fixture
def log_capture():
    """日志捕获器"""
    import logging
    from io import StringIO

    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.DEBUG)

    # 添加到根日志记录器
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG)

    yield log_stream

    # 清理
    root_logger.removeHandler(handler)


# 数据库测试夹具
@pytest.fixture
async def test_database():
    """测试数据库"""
    # 这里可以设置测试数据库
    # 目前返回模拟数据库
    db = {
        "users": [],
        "sessions": [],
        "logs": [],
    }

    yield db

    # 清理数据库
    db.clear()


# 网络模拟
@pytest.fixture
def mock_network():
    """模拟网络请求"""
    import responses

    with responses.RequestsMock() as rsps:
        # 添加默认响应
        rsps.add(
            responses.GET,
            "http://test-api.example.com/health",
            json={"status": "ok"},
            status=200,
        )

        yield rsps
