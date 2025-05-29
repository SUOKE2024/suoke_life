"""
测试配置文件 - 简化版本
提供基本的测试夹具，不依赖复杂的internal模块
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime
from uuid import uuid4

from palpation_service.config import get_settings


@pytest.fixture
def settings():
    """配置夹具"""
    return get_settings()


@pytest.fixture
def mock_session_id():
    """模拟会话ID"""
    return str(uuid4())


@pytest.fixture
def mock_user_id():
    """模拟用户ID"""
    return "test_user_123"


@pytest.fixture
def sample_sensor_data():
    """示例传感器数据"""
    return {
        "pressure": [
            {"timestamp": datetime.now().isoformat(), "value": 120.5, "unit": "mmHg"},
            {"timestamp": datetime.now().isoformat(), "value": 118.2, "unit": "mmHg"},
        ],
        "temperature": [
            {"timestamp": datetime.now().isoformat(), "value": 36.5, "unit": "celsius"},
            {"timestamp": datetime.now().isoformat(), "value": 36.7, "unit": "celsius"},
        ]
    }


@pytest.fixture
def mock_database():
    """模拟数据库连接"""
    mock_db = MagicMock()
    mock_db.execute = AsyncMock()
    mock_db.fetch = AsyncMock()
    mock_db.fetchrow = AsyncMock()
    return mock_db


@pytest.fixture
def mock_redis():
    """模拟Redis连接"""
    mock_redis = MagicMock()
    mock_redis.get = AsyncMock()
    mock_redis.set = AsyncMock()
    mock_redis.delete = AsyncMock()
    mock_redis.exists = AsyncMock()
    return mock_redis


@pytest.fixture
def event_loop():
    """事件循环夹具"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_ai_model():
    """模拟AI模型"""
    mock_model = MagicMock()
    mock_model.predict = AsyncMock(return_value={
        "confidence": 0.85,
        "results": {"health_score": 75.5},
        "recommendations": ["建议多休息", "注意饮食"]
    })
    return mock_model


@pytest.fixture
def sample_analysis_result():
    """示例分析结果"""
    return {
        "session_id": str(uuid4()),
        "analysis_type": "multimodal_fusion",
        "confidence_score": 0.85,
        "results": {
            "overall_health_score": 75.5,
            "pressure_analysis": {"systolic": 120, "diastolic": 80},
            "temperature_analysis": {"avg_temp": 36.6, "stability": "normal"}
        },
        "recommendations": [
            "血压正常，继续保持",
            "体温稳定，身体状况良好"
        ],
        "timestamp": datetime.now().isoformat()
    }


# 配置pytest-asyncio
pytest_plugins = ('pytest_asyncio',) 