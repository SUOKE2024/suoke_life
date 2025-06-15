"""
测试配置文件

提供测试所需的fixtures和配置
"""

import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from unittest.mock import AsyncMock, MagicMock

from soer_service.main import app
from soer_service.config.settings import get_settings
from soer_service.core.database import get_mongodb, get_redis
from soer_service.clients.auth_client import AuthClient
from soer_service.services.agent_service import AgentService
from soer_service.services.health_service import HealthService
from soer_service.services.nutrition_service import NutritionService
from soer_service.services.lifestyle_service import LifestyleService


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def settings():
    """测试设置"""
    return get_settings()


@pytest_asyncio.fixture
async def mock_mongodb():
    """模拟MongoDB连接"""
    mock_client = AsyncMock(spec=AsyncIOMotorClient)
    mock_db = AsyncMock()
    mock_collection = AsyncMock()
    
    # 设置模拟行为
    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection
    mock_db.command = AsyncMock(return_value={"ok": 1})
    
    # 模拟集合操作
    mock_collection.insert_one = AsyncMock(return_value=MagicMock(inserted_id="test_id"))
    mock_collection.find_one = AsyncMock(return_value=None)
    mock_collection.find = AsyncMock()
    mock_collection.update_one = AsyncMock()
    mock_collection.delete_one = AsyncMock()
    
    return mock_db


@pytest_asyncio.fixture
async def mock_redis():
    """模拟Redis连接"""
    mock_redis = AsyncMock()
    mock_redis.ping = AsyncMock(return_value=True)
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.set = AsyncMock(return_value=True)
    mock_redis.delete = AsyncMock(return_value=1)
    mock_redis.exists = AsyncMock(return_value=0)
    return mock_redis


@pytest_asyncio.fixture
async def client(mock_mongodb, mock_redis):
    """测试客户端"""
    # 覆盖依赖
    app.dependency_overrides[get_mongodb] = lambda: mock_mongodb
    app.dependency_overrides[get_redis] = lambda: mock_redis
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # 清理依赖覆盖
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_client():
    """认证客户端实例"""
    return AuthClient()


@pytest_asyncio.fixture
async def agent_service(mock_mongodb, mock_redis):
    """智能体服务实例"""
    service = AgentService()
    service.mongodb = mock_mongodb
    service.redis = mock_redis
    return service


@pytest_asyncio.fixture
async def health_service(mock_mongodb, mock_redis):
    """健康服务实例"""
    service = HealthService()
    service.mongodb = mock_mongodb
    service.redis = mock_redis
    return service


@pytest_asyncio.fixture
async def nutrition_service(mock_mongodb, mock_redis):
    """营养服务实例"""
    service = NutritionService()
    service.mongodb = mock_mongodb
    service.redis = mock_redis
    return service


@pytest_asyncio.fixture
async def lifestyle_service(mock_mongodb, mock_redis):
    """生活方式服务实例"""
    service = LifestyleService()
    service.mongodb = mock_mongodb
    service.redis = mock_redis
    return service


@pytest.fixture
def sample_user_data():
    """示例用户数据"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }


@pytest.fixture
def sample_health_data():
    """示例健康数据"""
    return {
        "heart_rate": 72,
        "blood_pressure_systolic": 120,
        "blood_pressure_diastolic": 80,
        "weight": 70.5,
        "height": 175,
        "sleep_duration": 8.0,
        "steps": 10000
    }


@pytest.fixture
def sample_nutrition_data():
    """示例营养数据"""
    return {
        "foods": [
            {
                "name": "苹果",
                "quantity": 150,
                "unit": "g"
            },
            {
                "name": "鸡胸肉",
                "quantity": 100,
                "unit": "g"
            }
        ]
    }


@pytest.fixture
def sample_exercise_goals():
    """示例运动目标"""
    return {
        "primary_goal": "weight_loss",
        "duration_weeks": 12,
        "weekly_frequency": 4,
        "preferred_activities": ["running", "strength_training"]
    }


@pytest.fixture
def sample_stress_assessment():
    """示例压力评估数据"""
    return {
        "stress_indicators": {
            "sleep_quality": 3,
            "energy_level": 2,
            "mood": 3,
            "concentration": 2,
            "physical_symptoms": 4
        },
        "stress_sources": ["work", "relationships"],
        "physical_symptoms": ["headache", "muscle_tension"],
        "emotional_symptoms": ["anxiety", "irritability"],
        "behavioral_symptoms": ["overeating", "social_withdrawal"]
    }


@pytest.fixture
def mock_ai_response():
    """模拟AI响应"""
    return {
        "response": "这是一个测试响应",
        "confidence": 0.95,
        "intent": "health_inquiry",
        "sentiment": "neutral",
        "suggestions": ["建议1", "建议2"]
    }


@pytest.fixture
def jwt_token():
    """生成测试JWT令牌"""
    return "test_jwt_token_for_testing"


# 测试数据库清理
@pytest_asyncio.fixture(autouse=True)
async def cleanup_database(mock_mongodb):
    """自动清理测试数据库"""
    yield
    # 测试后清理（在模拟环境中不需要实际清理）
    pass


# 异步测试标记
pytest_plugins = ('pytest_asyncio',)