"""
医疗资源服务测试配置
"""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock
import uuid
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from internal.infrastructure.models import Base
from internal.enhanced_medical_resource_service import EnhancedMedicalResourceService
from internal.domain.models import (
    ResourceType, SpecialtyType, ResourceStatus, Priority,
    Location, TimeSlot, Doctor, Hospital, Equipment, Medicine
)

# 测试数据库配置
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def async_engine():
    """创建异步数据库引擎"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest_asyncio.fixture
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """创建异步数据库会话"""
    async_session_maker = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        yield session

@pytest.fixture
def mock_config():
    """模拟配置"""
    return {
        "database": {
            "url": TEST_DATABASE_URL,
            "pool_size": 5,
            "max_overflow": 10
        },
        "cache": {
            "enabled": True,
            "ttl_seconds": 300
        },
        "matching": {
            "max_distance_km": 50,
            "max_results": 10
        }
    }

@pytest_asyncio.fixture
async def medical_service(mock_config):
    """创建医疗资源服务实例"""
    service = EnhancedMedicalResourceService(mock_config)
    await service.initialize()
    yield service
    await service.close()

@pytest.fixture
def sample_location():
    """示例位置"""
    return Location(
        latitude=39.9042,
        longitude=116.4074,
        address="北京市朝阳区",
        city="北京",
        district="朝阳区"
    )

@pytest.fixture
def sample_doctor(sample_location):
    """示例医生"""
    return Doctor(
        doctor_id=str(uuid.uuid4()),
        name="张三",
        specialty=SpecialtyType.TCM,
        hospital_id=str(uuid.uuid4()),
        location=sample_location,
        rating=4.5,
        experience_years=15,
        consultation_fee=200.0,
        available_slots=[
            TimeSlot(
                start_time=datetime.now() + timedelta(hours=1),
                end_time=datetime.now() + timedelta(hours=2),
                available=True
            )
        ],
        status=ResourceStatus.AVAILABLE,
        skills=["中医诊断", "针灸", "中药调理"],
        languages=["中文", "英文"]
    )

@pytest.fixture
def sample_hospital(sample_location):
    """示例医院"""
    return Hospital(
        hospital_id=str(uuid.uuid4()),
        name="北京中医医院",
        location=sample_location,
        level="三甲",
        departments=["中医科", "针灸科", "推拿科"],
        bed_count=500,
        available_beds=50,
        rating=4.8,
        contact_info={"phone": "010-12345678", "email": "info@hospital.com"}
    )

@pytest.fixture
def sample_equipment(sample_location):
    """示例设备"""
    return Equipment(
        equipment_id=str(uuid.uuid4()),
        name="核磁共振设备",
        type="MRI",
        hospital_id=str(uuid.uuid4()),
        location=sample_location,
        status=ResourceStatus.AVAILABLE,
        maintenance_schedule=[],
        booking_slots=[
            TimeSlot(
                start_time=datetime.now() + timedelta(hours=2),
                end_time=datetime.now() + timedelta(hours=3),
                available=True
            )
        ]
    )

@pytest.fixture
def sample_medicine():
    """示例药品"""
    return Medicine(
        medicine_id=str(uuid.uuid4()),
        name="人参",
        type="中药材",
        manufacturer="同仁堂",
        stock_quantity=100,
        unit_price=50.0,
        expiry_date=datetime.now() + timedelta(days=365),
        pharmacy_locations=["北京", "上海", "广州"]
    )

@pytest.fixture
def mock_xiaoke_agent():
    """模拟小克智能体"""
    agent = AsyncMock()
    agent.recommend_resources.return_value = []
    agent.optimize_schedule.return_value = MagicMock(
        success=True,
        message="优化成功",
        suggestions=[],
        expected_improvement=0.1
    )
    return agent

@pytest.fixture
def mock_database_manager():
    """模拟数据库管理器"""
    manager = AsyncMock()
    manager.health_check.return_value = {"status": "healthy"}
    manager.get_session.return_value = AsyncMock()
    return manager

@pytest.fixture
def mock_scheduler_service():
    """模拟调度服务"""
    scheduler = AsyncMock()
    scheduler.schedule_resource.return_value = {
        "success": True,
        "resource_id": str(uuid.uuid4()),
        "scheduled_time": datetime.now().isoformat()
    }
    return scheduler

# 测试数据工厂
class TestDataFactory:
    """测试数据工厂"""
    
    @staticmethod
    def create_resource_request(
        patient_id: str = None,
        resource_type: ResourceType = ResourceType.DOCTOR,
        specialty: SpecialtyType = SpecialtyType.TCM,
        location: Location = None,
        symptoms: list = None
    ):
        """创建资源请求"""
        from internal.enhanced_medical_resource_service import ResourceRequest
        
        return ResourceRequest(
            request_id=str(uuid.uuid4()),
            patient_id=patient_id or str(uuid.uuid4()),
            resource_type=resource_type,
            specialty=specialty,
            location=location or Location(39.9042, 116.4074, "北京市"),
            preferred_time=datetime.now() + timedelta(hours=1),
            symptoms=symptoms or ["头痛", "失眠"],
            budget_range=(100.0, 500.0),
            priority=Priority.NORMAL,
            requirements={}
        )
    
    @staticmethod
    def create_appointment_data(
        user_id: str = None,
        doctor_id: str = None,
        appointment_time: datetime = None
    ):
        """创建预约数据"""
        return {
            "user_id": user_id or str(uuid.uuid4()),
            "doctor_id": doctor_id or str(uuid.uuid4()),
            "appointment_date": (appointment_time or datetime.now()).date().isoformat(),
            "appointment_time": (appointment_time or datetime.now()).time().strftime("%H:%M"),
            "symptoms": ["头痛", "失眠"],
            "constitution_type": "气虚质",
            "special_requirements": "需要中医调理"
        }

@pytest.fixture
def test_data_factory():
    """测试数据工厂实例"""
    return TestDataFactory()

# 性能测试装饰器
def performance_test(max_time_ms: int = 1000):
    """性能测试装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            import time
            start_time = time.time()
            result = await func(*args, **kwargs)
            end_time = time.time()
            
            execution_time_ms = (end_time - start_time) * 1000
            assert execution_time_ms < max_time_ms, f"执行时间 {execution_time_ms:.2f}ms 超过限制 {max_time_ms}ms"
            
            return result
        return wrapper
    return decorator

# 并发测试工具
async def run_concurrent_tasks(tasks: list, max_concurrent: int = 10):
    """运行并发任务"""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def limited_task(task):
        async with semaphore:
            return await task
    
    return await asyncio.gather(*[limited_task(task) for task in tasks])
