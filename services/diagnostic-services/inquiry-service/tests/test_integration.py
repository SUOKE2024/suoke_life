"""
集成测试 - 测试各组件之间的集成
"""

import asyncio

import pytest

from internal.dialogue.dialogue_manager import DialogueManager
from internal.grpc_service.inquiry_service_impl import InquiryServiceServicer
from internal.llm.llm_client import LLMClient
from internal.repository.session_repository import SessionRepository
from internal.symptom.optimized_symptom_extractor import OptimizedSymptomExtractor
from internal.tcm.tcm_pattern_mapper import TCMPatternMapper


@pytest.fixture
async def integration_config():
    """集成测试配置"""
    return {
        "server": {
            "host": "localhost",
            "port": 8080
        },
        "grpc": {
            "host": "localhost",
            "port": 50051,
            "max_workers": 4
        },
        "dialogue": {
            "max_session_duration_minutes": 30,
            "max_messages_per_session": 100,
            "session_timeout_minutes": 5,
            "welcome_message": "您好！我是您的健康顾问。",
            "default_suggestions": [
                "描述您的症状",
                "了解体质调理"
            ]
        },
        "llm": {
            "model_type": "llama3",
            "use_mock_mode": True,  # 使用模拟模式进行测试
            "temperature": 0.7,
            "response_max_tokens": 1024,
            "timeout_seconds": 30
        },
        "symptom_extraction": {
            "confidence_threshold": 0.7,
            "max_symptoms_per_text": 20,
            "enable_negation_detection": True,
            "enable_severity_analysis": True,
            "parallel_processing": True
        },
        "tcm_mapping": {
            "confidence_threshold": 0.6,
            "max_patterns_per_analysis": 5,
            "enable_constitution_analysis": True
        },
        "database": {
            "url": "sqlite+aiosqlite:///:memory:",
            "pool_size": 5,
            "max_overflow": 10
        },
        "cache": {
            "enabled": False  # 测试时禁用缓存
        },
        "monitoring": {
            "enabled": False  # 测试时禁用监控
        },
        "logging": {
            "level": "DEBUG"
        }
    }


@pytest.fixture
async def integrated_components(integration_config):
    """创建集成的组件"""
    # 创建各个组件
    llm_client = LLMClient(integration_config)
    await llm_client.initialize()

    session_repository = SessionRepository(integration_config)
    await session_repository.initialize()

    symptom_extractor = OptimizedSymptomExtractor(integration_config)
    await symptom_extractor.initialize()

    tcm_mapper = TCMPatternMapper(integration_config)
    await tcm_mapper.initialize()

    dialogue_manager = DialogueManager(integration_config)
    dialogue_manager.llm_client = llm_client
    dialogue_manager.session_repository = session_repository
    await dialogue_manager.initialize()

    # 创建gRPC服务
    grpc_servicer = InquiryServiceServicer(integration_config)
    grpc_servicer.dialogue_manager = dialogue_manager
    grpc_servicer.symptom_extractor = symptom_extractor
    grpc_servicer.tcm_mapper = tcm_mapper

    components = {
        "llm_client": llm_client,
        "session_repository": session_repository,
        "symptom_extractor": symptom_extractor,
        "tcm_mapper": tcm_mapper,
        "dialogue_manager": dialogue_manager,
        "grpc_servicer": grpc_servicer
    }

    yield components

    # 清理资源
    await llm_client.close()
    await session_repository.close()


@pytest.mark.integration
class TestInquiryServiceIntegration:
    """问诊服务集成测试"""

    @pytest.mark.asyncio
    async def test_complete_inquiry_flow(self, integrated_components):
        """测试完整的问诊流程"""
        dialogue_manager = integrated_components["dialogue_manager"]

        # 1. 开始会话
        start_request = {
            "user_id": "integration-test-user",
            "agent_id": "xiaoai",
            "user_profile": {
                "age": 30,
                "gender": "female",
                "constitution_type": "平和质"
            }
        }

        start_result = await dialogue_manager.start_session(start_request)
        assert start_result["success"] is True
        session_id = start_result["session_id"]
        assert len(start_result["welcome_message"]) > 0
        assert len(start_result["suggested_questions"]) > 0

        # 2. 用户交互 - 第一轮
        interact_request1 = {
            "session_id": session_id,
            "user_message": "我最近头痛得很厉害，持续了三天了",
            "message_type": "text"
        }

        interact_result1 = await dialogue_manager.interact_with_user(interact_request1)
        assert interact_result1["success"] is True
        assert len(interact_result1["response"]) > 0
        assert "detected_symptoms" in interact_result1
        assert "follow_up_questions" in interact_result1

        # 3. 用户交互 - 第二轮
        interact_request2 = {
            "session_id": session_id,
            "user_message": "主要是太阳穴疼，还有点恶心，晚上睡不好",
            "message_type": "text"
        }

        interact_result2 = await dialogue_manager.interact_with_user(interact_request2)
        assert interact_result2["success"] is True
        assert len(interact_result2["response"]) > 0

        # 4. 结束会话
        end_request = {"session_id": session_id}
        end_result = await dialogue_manager.end_session(end_request)
        assert end_result["success"] is True
        assert "session_summary" in end_result
        assert "extracted_symptoms" in end_result
        assert "recommendations" in end_result
        assert len(end_result["extracted_symptoms"]) > 0

    @pytest.mark.asyncio
    async def test_symptom_extraction_integration(self, integrated_components):
        """测试症状提取集成"""
        symptom_extractor = integrated_components["symptom_extractor"]

        # 测试单个文本提取
        text = "我头痛得很厉害，还有点发烧，胃也不舒服，感觉很疲劳"

        result = await symptom_extractor.extract_symptoms(text)

        assert result["success"] is True
        assert "symptoms" in result
        assert len(result["symptoms"]) > 0

        # 检查症状结构
        for symptom in result["symptoms"]:
            assert "name" in symptom
            assert "confidence" in symptom
            assert symptom["confidence"] >= 0.7  # 配置的阈值
            assert "severity" in symptom
            assert "body_part" in symptom

        # 测试批量提取
        texts = [
            "头痛三天了",
            "发烧38度",
            "胃疼想吐",
            "咳嗽有痰",
            "失眠多梦"
        ]

        batch_result = await symptom_extractor.batch_extract_symptoms(texts)

        assert batch_result["success"] is True
        assert "results" in batch_result
        assert len(batch_result["results"]) == len(texts)

    @pytest.mark.asyncio
    async def test_tcm_mapping_integration(self, integrated_components):
        """测试中医证型映射集成"""
        tcm_mapper = integrated_components["tcm_mapper"]

        # 测试证型映射
        symptoms = ["头痛", "疲劳", "失眠", "食欲不振"]
        user_profile = {
            "age": 30,
            "gender": "female",
            "constitution_type": "气虚质"
        }

        result = await tcm_mapper.map_patterns(symptoms, user_profile)

        assert result["success"] is True
        assert "matched_patterns" in result
        assert "primary_pattern" in result
        assert "constitution_type" in result
        assert "recommendations" in result

        # 检查匹配的证型
        if result["matched_patterns"]:
            for pattern in result["matched_patterns"]:
                assert "pattern_name" in pattern
                assert "confidence" in pattern
                assert pattern["confidence"] >= 0.6  # 配置的阈值

    @pytest.mark.asyncio
    async def test_session_persistence_integration(self, integrated_components):
        """测试会话持久化集成"""
        session_repository = integrated_components["session_repository"]
        dialogue_manager = integrated_components["dialogue_manager"]

        # 创建会话
        start_request = {
            "user_id": "persistence-test-user",
            "agent_id": "xiaoai"
        }

        start_result = await dialogue_manager.start_session(start_request)
        session_id = start_result["session_id"]

        # 验证会话已保存
        session_data = await session_repository.get_session(session_id)
        assert session_data is not None
        assert session_data["user_id"] == "persistence-test-user"
        assert session_data["status"] == "active"

        # 添加消息
        interact_request = {
            "session_id": session_id,
            "user_message": "我头痛",
            "message_type": "text"
        }

        await dialogue_manager.interact_with_user(interact_request)

        # 验证消息已保存
        messages = await session_repository.get_session_messages(session_id)
        assert len(messages) >= 2  # 用户消息 + 助手回复

        # 结束会话
        await dialogue_manager.end_session({"session_id": session_id})

        # 验证会话状态更新
        updated_session = await session_repository.get_session(session_id)
        assert updated_session["status"] == "completed"

    @pytest.mark.asyncio
    async def test_concurrent_sessions_integration(self, integrated_components):
        """测试并发会话集成"""
        dialogue_manager = integrated_components["dialogue_manager"]

        # 创建多个并发会话
        user_count = 5
        tasks = []

        for i in range(user_count):
            start_request = {
                "user_id": f"concurrent-user-{i}",
                "agent_id": "xiaoai"
            }
            tasks.append(dialogue_manager.start_session(start_request))

        # 并发执行
        results = await asyncio.gather(*tasks)

        # 验证所有会话都成功创建
        session_ids = []
        for result in results:
            assert result["success"] is True
            session_ids.append(result["session_id"])

        # 验证会话ID唯一
        assert len(set(session_ids)) == user_count

        # 并发进行交互
        interact_tasks = []
        for session_id in session_ids:
            interact_request = {
                "session_id": session_id,
                "user_message": "我头痛",
                "message_type": "text"
            }
            interact_tasks.append(dialogue_manager.interact_with_user(interact_request))

        interact_results = await asyncio.gather(*interact_tasks)

        # 验证所有交互都成功
        for result in interact_results:
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_error_handling_integration(self, integrated_components):
        """测试错误处理集成"""
        dialogue_manager = integrated_components["dialogue_manager"]

        # 测试无效会话ID
        invalid_interact_request = {
            "session_id": "invalid-session-id",
            "user_message": "测试消息"
        }

        result = await dialogue_manager.interact_with_user(invalid_interact_request)
        assert result["success"] is False
        assert "error" in result

        # 测试空用户ID
        invalid_start_request = {
            "user_id": "",
            "agent_id": "xiaoai"
        }

        result = await dialogue_manager.start_session(invalid_start_request)
        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_data_flow_integration(self, integrated_components):
        """测试数据流集成"""
        dialogue_manager = integrated_components["dialogue_manager"]
        symptom_extractor = integrated_components["symptom_extractor"]
        tcm_mapper = integrated_components["tcm_mapper"]

        # 1. 开始会话
        start_request = {
            "user_id": "dataflow-test-user",
            "agent_id": "xiaoai",
            "user_profile": {
                "age": 35,
                "gender": "male",
                "constitution_type": "阳虚质"
            }
        }

        start_result = await dialogue_manager.start_session(start_request)
        session_id = start_result["session_id"]

        # 2. 用户描述症状
        symptom_text = "我最近经常感到疲劳，手脚冰凉，腰膝酸软，夜尿频繁"

        interact_request = {
            "session_id": session_id,
            "user_message": symptom_text,
            "message_type": "text"
        }

        interact_result = await dialogue_manager.interact_with_user(interact_request)
        assert interact_result["success"] is True

        # 3. 直接测试症状提取
        extract_result = await symptom_extractor.extract_symptoms(symptom_text)
        assert extract_result["success"] is True
        extracted_symptoms = [s["name"] for s in extract_result["symptoms"]]

        # 4. 测试中医证型映射
        if extracted_symptoms:
            tcm_result = await tcm_mapper.map_patterns(
                extracted_symptoms,
                start_request["user_profile"]
            )
            assert tcm_result["success"] is True

            # 验证阳虚质相关的证型
            if tcm_result["matched_patterns"]:
                pattern_names = [p["pattern_name"] for p in tcm_result["matched_patterns"]]
                # 根据症状和体质，应该能匹配到相关证型
                assert len(pattern_names) > 0

        # 5. 结束会话并获取完整分析
        end_result = await dialogue_manager.end_session({"session_id": session_id})
        assert end_result["success"] is True
        assert len(end_result["extracted_symptoms"]) > 0
        assert len(end_result["recommendations"]) > 0

    @pytest.mark.asyncio
    async def test_configuration_integration(self, integrated_components):
        """测试配置集成"""
        dialogue_manager = integrated_components["dialogue_manager"]

        # 验证配置是否正确应用
        assert dialogue_manager.max_session_duration == 30  # 分钟
        assert dialogue_manager.max_messages_per_session == 100
        assert dialogue_manager.session_timeout == 5  # 分钟

        symptom_extractor = integrated_components["symptom_extractor"]
        assert symptom_extractor.confidence_threshold == 0.7
        assert symptom_extractor.max_symptoms_per_text == 20

        tcm_mapper = integrated_components["tcm_mapper"]
        assert tcm_mapper.confidence_threshold == 0.6
        assert tcm_mapper.max_patterns_per_analysis == 5

    @pytest.mark.asyncio
    async def test_performance_integration(self, integrated_components):
        """测试性能集成"""
        dialogue_manager = integrated_components["dialogue_manager"]

        import time

        # 测试会话创建性能
        start_time = time.time()

        start_request = {
            "user_id": "performance-test-user",
            "agent_id": "xiaoai"
        }

        start_result = await dialogue_manager.start_session(start_request)
        session_creation_time = time.time() - start_time

        assert start_result["success"] is True
        assert session_creation_time < 2.0  # 应该在2秒内完成

        # 测试交互性能
        session_id = start_result["session_id"]

        start_time = time.time()

        interact_request = {
            "session_id": session_id,
            "user_message": "我头痛、发烧、咳嗽、胃疼、失眠、疲劳",
            "message_type": "text"
        }

        interact_result = await dialogue_manager.interact_with_user(interact_request)
        interaction_time = time.time() - start_time

        assert interact_result["success"] is True
        assert interaction_time < 5.0  # 应该在5秒内完成

    @pytest.mark.asyncio
    async def test_memory_usage_integration(self, integrated_components):
        """测试内存使用集成"""
        dialogue_manager = integrated_components["dialogue_manager"]

        # 创建多个会话测试内存使用
        session_ids = []

        for i in range(10):
            start_request = {
                "user_id": f"memory-test-user-{i}",
                "agent_id": "xiaoai"
            }

            start_result = await dialogue_manager.start_session(start_request)
            assert start_result["success"] is True
            session_ids.append(start_result["session_id"])

        # 每个会话进行多次交互
        for session_id in session_ids:
            for j in range(5):
                interact_request = {
                    "session_id": session_id,
                    "user_message": f"症状描述 {j}",
                    "message_type": "text"
                }

                result = await dialogue_manager.interact_with_user(interact_request)
                assert result["success"] is True

        # 结束所有会话
        for session_id in session_ids:
            end_result = await dialogue_manager.end_session({"session_id": session_id})
            assert end_result["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
