"""
pytest配置文件 - 全局测试配置和fixtures
"""

import asyncio
from collections.abc import Generator
import os
import shutil
import sys
import tempfile
from typing import Any, Optional
from unittest.mock import AsyncMock, MagicMock

import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Generator[str]:
    """创建临时目录"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_config() -> dict[str, Any]:
    """测试配置"""
    return {
        "server": {
            "host": "localhost",
            "port": 8080,
            "debug": True
        },
        "grpc": {
            "host": "localhost",
            "port": 50051,
            "max_workers": 4,
            "max_message_length": 4 * 1024 * 1024,
            "keepalive_time_ms": 30000,
            "keepalive_timeout_ms": 5000,
            "keepalive_permit_without_calls": True,
            "max_connection_idle_ms": 300000
        },
        "dialogue": {
            "max_session_duration_minutes": 30,
            "max_messages_per_session": 100,
            "session_timeout_minutes": 5,
            "welcome_message": "您好！我是您的健康顾问，请问有什么可以帮助您的？",
            "default_suggestions": [
                "描述您的症状",
                "了解体质调理",
                "咨询健康建议",
                "预防保健知识"
            ],
            "max_response_length": 2000,
            "enable_context_memory": True,
            "context_window_size": 10
        },
        "llm": {
            "model_type": "llama3",
            "use_mock_mode": True,
            "temperature": 0.7,
            "top_p": 0.95,
            "response_max_tokens": 1024,
            "timeout_seconds": 30,
            "retry_attempts": 3,
            "retry_delay_seconds": 1,
            "remote_endpoint": "",
            "system_prompt_path": "./config/prompts/system_prompt.txt"
        },
        "symptom_extraction": {
            "confidence_threshold": 0.7,
            "max_symptoms_per_text": 20,
            "enable_negation_detection": True,
            "enable_severity_analysis": True,
            "enable_duration_extraction": True,
            "enable_body_part_mapping": True,
            "parallel_processing": True,
            "batch_size": 10,
            "timeout_seconds": 30
        },
        "tcm_mapping": {
            "confidence_threshold": 0.6,
            "max_patterns_per_analysis": 5,
            "enable_constitution_analysis": True,
            "enable_pattern_combination": True,
            "pattern_database_path": "./data/tcm_patterns.json",
            "constitution_database_path": "./data/constitutions.json"
        },
        "database": {
            "url": "sqlite+aiosqlite:///:memory:",
            "pool_size": 5,
            "max_overflow": 10,
            "pool_timeout": 30,
            "pool_recycle": 3600,
            "echo": False
        },
        "cache": {
            "enabled": False,
            "url": "redis://localhost:6379/0",
            "session_ttl_seconds": 3600,
            "max_connections": 10,
            "retry_on_timeout": True
        },
        "monitoring": {
            "enabled": True,
            "metrics_port": 9090,
            "health_check_interval": 30,
            "log_level": "INFO"
        },
        "logging": {
            "level": "DEBUG",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file_path": "./logs/test.log",
            "max_file_size": "10MB",
            "backup_count": 5
        }
    }


@pytest.fixture
def mock_user_profile() -> dict[str, Any]:
    """模拟用户档案"""
    return {
        "user_id": "test-user-123",
        "name": "张三",
        "age": 30,
        "gender": "female",
        "constitution_type": "平和质",
        "medical_history": {
            "chronic_diseases": [],
            "allergies": [],
            "medications": [],
            "family_history": []
        },
        "lifestyle": {
            "exercise_frequency": "moderate",
            "diet_type": "balanced",
            "sleep_hours": 8,
            "stress_level": "low"
        }
    }


@pytest.fixture
def sample_symptoms() -> list:
    """示例症状列表"""
    return [
        {
            "name": "头痛",
            "confidence": 0.9,
            "severity": "中等",
            "body_part": "头部",
            "duration": "2天",
            "description": "持续性钝痛"
        },
        {
            "name": "疲劳",
            "confidence": 0.8,
            "severity": "轻微",
            "body_part": "全身",
            "duration": "1周",
            "description": "容易疲倦，精神不振"
        },
        {
            "name": "失眠",
            "confidence": 0.85,
            "severity": "中等",
            "body_part": "神经系统",
            "duration": "3天",
            "description": "入睡困难，易醒"
        }
    ]


@pytest.fixture
def sample_tcm_patterns() -> list:
    """示例中医证型"""
    return [
        {
            "pattern_name": "气虚证",
            "confidence": 0.8,
            "description": "气虚体质，容易疲劳",
            "symptoms": ["疲劳", "气短", "乏力"],
            "recommendations": ["补气养血", "适当运动", "规律作息"]
        },
        {
            "pattern_name": "血虚证",
            "confidence": 0.7,
            "description": "血虚体质，面色苍白",
            "symptoms": ["头晕", "心悸", "失眠"],
            "recommendations": ["补血养阴", "营养均衡", "避免熬夜"]
        }
    ]


@pytest.fixture
def sample_session_messages() -> list:
    """示例会话消息"""
    return [
        {
            "role": "user",
            "content": "我最近头痛",
            "timestamp": "2024-01-01T10:00:00Z",
            "metadata": {}
        },
        {
            "role": "assistant",
            "content": "请详细描述一下您的头痛症状",
            "timestamp": "2024-01-01T10:00:05Z",
            "metadata": {
                "detected_symptoms": ["头痛"],
                "confidence": 0.9
            }
        },
        {
            "role": "user",
            "content": "头痛持续了两天，主要是太阳穴疼",
            "timestamp": "2024-01-01T10:01:00Z",
            "metadata": {}
        },
        {
            "role": "assistant",
            "content": "根据您的描述，可能是紧张性头痛。建议您注意休息。",
            "timestamp": "2024-01-01T10:01:10Z",
            "metadata": {
                "detected_symptoms": ["头痛"],
                "severity": "中等",
                "recommendations": ["休息", "放松"]
            }
        }
    ]


@pytest.fixture
async def mock_llm_client():
    """模拟LLM客户端"""
    client = AsyncMock()

    client.generate_response.return_value = {
        "response_text": "我理解您的症状，请详细描述一下。",
        "response_type": "TEXT",
        "detected_symptoms": ["头痛"],
        "follow_up_questions": ["疼痛持续多长时间了？", "疼痛的性质如何？"],
        "confidence": 0.85,
        "processing_time": 0.5
    }

    client.extract_symptoms.return_value = {
        "response_text": "检测到以下症状：头痛",
        "detected_symptoms": ["头痛"],
        "confidence": 0.9
    }

    client.map_tcm_patterns.return_value = {
        "response_text": "根据症状分析，可能是气虚证",
        "matched_patterns": ["气虚证"],
        "confidence": 0.8
    }

    client.assess_health_risks.return_value = {
        "response_text": "风险等级：低",
        "risk_level": "low",
        "recommendations": ["注意休息", "规律作息"]
    }

    return client


@pytest.fixture
async def mock_session_repository():
    """模拟会话存储库"""
    repo = AsyncMock()

    repo.create_session.return_value = "test-session-123"

    repo.get_session.return_value = {
        "session_id": "test-session-123",
        "user_id": "test-user",
        "agent_id": "xiaoai",
        "status": "active",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "metadata": {}
    }

    repo.update_session.return_value = True
    repo.delete_session.return_value = True
    repo.add_message.return_value = "test-message-123"
    repo.get_session_messages.return_value = []
    repo.save_session_summary.return_value = "test-summary-123"
    repo.get_session_summary.return_value = None
    repo.get_user_sessions.return_value = []
    repo.cleanup_expired_sessions.return_value = 0
    repo.get_session_statistics.return_value = {
        "total_sessions": 0,
        "active_sessions": 0,
        "completed_sessions": 0,
        "abandoned_sessions": 0,
        "completion_rate": 0
    }

    return repo


@pytest.fixture
async def mock_dialogue_manager(mock_llm_client, mock_session_repository):
    """模拟对话管理器"""
    manager = AsyncMock()

    manager.start_session.return_value = {
        "success": True,
        "session_id": "test-session-123",
        "welcome_message": "欢迎使用问诊服务！",
        "suggested_questions": [
            "请描述您的症状",
            "您感觉哪里不舒服？"
        ]
    }

    manager.interact_with_user.return_value = {
        "success": True,
        "response": "我了解您的症状，请详细描述。",
        "detected_symptoms": ["头痛"],
        "follow_up_questions": ["疼痛持续多长时间了？"],
        "confidence": 0.85
    }

    manager.end_session.return_value = {
        "success": True,
        "session_summary": "用户主要症状为头痛",
        "extracted_symptoms": ["头痛", "疲劳"],
        "recommendations": ["建议充分休息", "保持规律作息"]
    }

    return manager


@pytest.fixture
async def mock_symptom_extractor():
    """模拟症状提取器"""
    extractor = AsyncMock()

    extractor.extract_symptoms.return_value = {
        "success": True,
        "symptoms": [
            {
                "name": "头痛",
                "confidence": 0.9,
                "severity": "中等",
                "body_part": "头部",
                "duration": "2天"
            }
        ],
        "processing_time": 0.5
    }

    extractor.batch_extract_symptoms.return_value = {
        "success": True,
        "results": [
            {
                "text_index": 0,
                "symptoms": [
                    {
                        "name": "头痛",
                        "confidence": 0.9,
                        "severity": "中等",
                        "body_part": "头部"
                    }
                ]
            }
        ]
    }

    return extractor


@pytest.fixture
async def mock_tcm_mapper():
    """模拟中医证型映射器"""
    mapper = AsyncMock()

    mapper.map_patterns.return_value = {
        "success": True,
        "matched_patterns": [
            {
                "pattern_name": "气虚证",
                "confidence": 0.8,
                "description": "气虚体质，容易疲劳"
            }
        ],
        "primary_pattern": "气虚证",
        "constitution_type": "气虚质",
        "recommendations": ["补气养血", "适当运动"]
    }

    return mapper


@pytest.fixture
def grpc_context():
    """模拟gRPC上下文"""
    context = MagicMock()
    context.is_active.return_value = True
    context.time_remaining.return_value = 30.0
    context.peer.return_value = "test-client"
    return context


# 测试数据生成器
class TestDataGenerator:
    """测试数据生成器"""

    @staticmethod
    def generate_user_message(content: str, message_type: str = "text") -> dict[str, Any]:
        """生成用户消息"""
        return {
            "role": "user",
            "content": content,
            "message_type": message_type,
            "timestamp": "2024-01-01T10:00:00Z",
            "metadata": {}
        }

    @staticmethod
    def generate_assistant_message(content: str, symptoms: Optional[list] = None) -> dict[str, Any]:
        """生成助手消息"""
        return {
            "role": "assistant",
            "content": content,
            "timestamp": "2024-01-01T10:00:05Z",
            "metadata": {
                "detected_symptoms": symptoms or [],
                "confidence": 0.85
            }
        }

    @staticmethod
    def generate_session_data(user_id: str, agent_id: str = "xiaoai") -> dict[str, Any]:
        """生成会话数据"""
        return {
            "user_id": user_id,
            "agent_id": agent_id,
            "user_profile": {
                "age": 30,
                "gender": "female",
                "constitution_type": "平和质"
            },
            "session_config": {
                "language": "zh-CN",
                "mode": "standard"
            }
        }


@pytest.fixture
def test_data_generator():
    """测试数据生成器实例"""
    return TestDataGenerator()


# 测试标记
pytest_plugins = []

# 自定义标记
def pytest_configure(config):
    """配置pytest标记"""
    config.addinivalue_line(
        "markers", "unit: 单元测试"
    )
    config.addinivalue_line(
        "markers", "integration: 集成测试"
    )
    config.addinivalue_line(
        "markers", "e2e: 端到端测试"
    )
    config.addinivalue_line(
        "markers", "slow: 慢速测试"
    )
    config.addinivalue_line(
        "markers", "grpc: gRPC相关测试"
    )
    config.addinivalue_line(
        "markers", "database: 数据库相关测试"
    )


# 测试收集钩子
def pytest_collection_modifyitems(config, items):
    """修改测试项"""
    for item in items:
        # 为异步测试添加asyncio标记
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)

        # 根据文件名添加标记
        if "test_grpc" in item.nodeid:
            item.add_marker(pytest.mark.grpc)
        elif "test_database" in item.nodeid or "test_repository" in item.nodeid:
            item.add_marker(pytest.mark.database)
        elif "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        else:
            item.add_marker(pytest.mark.unit)
