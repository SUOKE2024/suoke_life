"""
gRPC服务测试
"""

import asyncio
import os

# 导入生成的protobuf类
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'proto'))

from proto import inquiry_service_pb2

from internal.grpc_service.inquiry_service_impl import InquiryServiceServicer


@pytest.fixture
def mock_config():
    """模拟配置"""
    return {
        "grpc": {
            "port": 50051,
            "max_workers": 10
        },
        "dialogue": {
            "max_session_duration_minutes": 30,
            "welcome_message": "欢迎使用问诊服务"
        },
        "symptom_extraction": {
            "confidence_threshold": 0.7
        },
        "tcm_mapping": {
            "confidence_threshold": 0.6
        }
    }


@pytest.fixture
async def mock_dialogue_manager():
    """模拟对话管理器"""
    manager = AsyncMock()

    # 模拟开始会话
    manager.start_session.return_value = {
        "success": True,
        "session_id": "test-session-123",
        "welcome_message": "欢迎使用问诊服务！",
        "suggested_questions": [
            "请描述您的症状",
            "您感觉哪里不舒服？"
        ]
    }

    # 模拟用户交互
    manager.interact_with_user.return_value = {
        "success": True,
        "response": "我了解您的症状，请详细描述。",
        "detected_symptoms": ["头痛"],
        "follow_up_questions": ["疼痛持续多长时间了？"],
        "confidence": 0.85
    }

    # 模拟结束会话
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
async def grpc_servicer(mock_config, mock_dialogue_manager, mock_symptom_extractor, mock_tcm_mapper):
    """创建gRPC服务实例"""
    servicer = InquiryServiceServicer(mock_config)
    servicer.dialogue_manager = mock_dialogue_manager
    servicer.symptom_extractor = mock_symptom_extractor
    servicer.tcm_mapper = mock_tcm_mapper
    return servicer


class TestInquiryServiceServicer:
    """gRPC服务测试类"""

    @pytest.mark.asyncio
    async def test_start_inquiry_session_success(self, grpc_servicer):
        """测试成功开始问诊会话"""
        request = inquiry_service_pb2.StartInquirySessionRequest(
            user_id="test-user-123",
            agent_id="xiaoai",
            user_profile=inquiry_service_pb2.UserProfile(
                age=30,
                gender="female",
                constitution_type="平和质"
            )
        )

        context = MagicMock()

        response = await grpc_servicer.StartInquirySession(request, context)

        assert response.success is True
        assert response.session_id == "test-session-123"
        assert response.welcome_message == "欢迎使用问诊服务！"
        assert len(response.suggested_questions) > 0

    @pytest.mark.asyncio
    async def test_start_inquiry_session_missing_user_id(self, grpc_servicer):
        """测试缺少用户ID的情况"""
        request = inquiry_service_pb2.StartInquirySessionRequest(
            agent_id="xiaoai"
        )

        context = MagicMock()

        response = await grpc_servicer.StartInquirySession(request, context)

        assert response.success is False
        assert "用户ID不能为空" in response.error_message

    @pytest.mark.asyncio
    async def test_interact_with_user_success(self, grpc_servicer):
        """测试成功的用户交互"""
        request = inquiry_service_pb2.InteractWithUserRequest(
            session_id="test-session-123",
            user_message="我最近头痛",
            message_type="text"
        )

        context = MagicMock()

        # 测试流式响应
        response_stream = grpc_servicer.InteractWithUser(request, context)
        responses = []

        async for response in response_stream:
            responses.append(response)

        assert len(responses) > 0

        # 检查最后一个响应
        final_response = responses[-1]
        assert final_response.success is True
        assert len(final_response.response_text) > 0

    @pytest.mark.asyncio
    async def test_interact_with_user_invalid_session(self, grpc_servicer):
        """测试无效会话ID"""
        # 模拟无效会话
        grpc_servicer.dialogue_manager.interact_with_user.return_value = {
            "success": False,
            "error": "会话不存在或已过期"
        }

        request = inquiry_service_pb2.InteractWithUserRequest(
            session_id="invalid-session",
            user_message="测试消息"
        )

        context = MagicMock()

        response_stream = grpc_servicer.InteractWithUser(request, context)
        responses = []

        async for response in response_stream:
            responses.append(response)

        assert len(responses) > 0
        final_response = responses[-1]
        assert final_response.success is False
        assert "会话不存在" in final_response.error_message

    @pytest.mark.asyncio
    async def test_end_inquiry_session_success(self, grpc_servicer):
        """测试成功结束问诊会话"""
        request = inquiry_service_pb2.EndInquirySessionRequest(
            session_id="test-session-123"
        )

        context = MagicMock()

        response = await grpc_servicer.EndInquirySession(request, context)

        assert response.success is True
        assert len(response.session_summary) > 0
        assert len(response.extracted_symptoms) > 0
        assert len(response.recommendations) > 0

    @pytest.mark.asyncio
    async def test_extract_symptoms_success(self, grpc_servicer):
        """测试成功提取症状"""
        request = inquiry_service_pb2.ExtractSymptomsRequest(
            text="我最近头痛，还有点发烧",
            session_id="test-session-123"
        )

        context = MagicMock()

        response = await grpc_servicer.ExtractSymptoms(request, context)

        assert response.success is True
        assert len(response.symptoms) > 0

        # 检查症状结构
        symptom = response.symptoms[0]
        assert len(symptom.name) > 0
        assert symptom.confidence > 0
        assert len(symptom.severity) > 0

    @pytest.mark.asyncio
    async def test_extract_symptoms_empty_text(self, grpc_servicer):
        """测试空文本的症状提取"""
        # 模拟空文本错误
        grpc_servicer.symptom_extractor.extract_symptoms.return_value = {
            "success": False,
            "error": "输入文本不能为空"
        }

        request = inquiry_service_pb2.ExtractSymptomsRequest(
            text="",
            session_id="test-session-123"
        )

        context = MagicMock()

        response = await grpc_servicer.ExtractSymptoms(request, context)

        assert response.success is False
        assert "输入文本不能为空" in response.error_message

    @pytest.mark.asyncio
    async def test_map_to_tcm_patterns_success(self, grpc_servicer):
        """测试成功的中医证型映射"""
        request = inquiry_service_pb2.MapToTCMPatternsRequest(
            symptoms=["头痛", "疲劳", "失眠"],
            user_profile=inquiry_service_pb2.UserProfile(
                age=30,
                gender="female",
                constitution_type="气虚质"
            ),
            session_id="test-session-123"
        )

        context = MagicMock()

        response = await grpc_servicer.MapToTCMPatterns(request, context)

        assert response.success is True
        assert len(response.matched_patterns) > 0
        assert len(response.primary_pattern) > 0
        assert len(response.constitution_type) > 0

    @pytest.mark.asyncio
    async def test_map_to_tcm_patterns_no_symptoms(self, grpc_servicer):
        """测试无症状的中医证型映射"""
        request = inquiry_service_pb2.MapToTCMPatternsRequest(
            symptoms=[],
            user_profile=inquiry_service_pb2.UserProfile(
                age=30,
                gender="female"
            ),
            session_id="test-session-123"
        )

        context = MagicMock()

        response = await grpc_servicer.MapToTCMPatterns(request, context)

        assert response.success is False
        assert "症状列表不能为空" in response.error_message

    @pytest.mark.asyncio
    async def test_assess_health_risks_success(self, grpc_servicer):
        """测试健康风险评估"""
        request = inquiry_service_pb2.AssessHealthRisksRequest(
            symptoms=["头痛", "高血压"],
            medical_history=inquiry_service_pb2.MedicalHistory(
                chronic_diseases=["高血压"],
                family_history=["心脏病"],
                medications=["降压药"]
            ),
            session_id="test-session-123"
        )

        context = MagicMock()

        # 模拟健康风险评估结果
        mock_result = {
            "success": True,
            "risk_level": "medium",
            "risk_factors": ["高血压", "家族史"],
            "recommendations": ["定期监测血压", "健康饮食"],
            "follow_up_actions": ["一个月后复查"]
        }

        with patch.object(grpc_servicer, '_assess_health_risks', return_value=mock_result):
            response = await grpc_servicer.AssessHealthRisks(request, context)

        assert response.success is True
        assert response.risk_level == "medium"
        assert len(response.risk_factors) > 0
        assert len(response.recommendations) > 0

    @pytest.mark.asyncio
    async def test_analyze_medical_history_success(self, grpc_servicer):
        """测试病史分析"""
        request = inquiry_service_pb2.AnalyzeMedicalHistoryRequest(
            medical_history=inquiry_service_pb2.MedicalHistory(
                chronic_diseases=["糖尿病", "高血压"],
                family_history=["心脏病"],
                medications=["二甲双胍", "降压药"],
                allergies=["青霉素"]
            ),
            current_symptoms=["头痛", "疲劳"],
            session_id="test-session-123"
        )

        context = MagicMock()

        # 模拟病史分析结果
        mock_result = {
            "success": True,
            "analysis_summary": "患者有糖尿病和高血压病史",
            "risk_factors": ["糖尿病", "高血压", "家族心脏病史"],
            "drug_interactions": [],
            "recommendations": ["控制血糖", "监测血压"]
        }

        with patch.object(grpc_servicer, '_analyze_medical_history', return_value=mock_result):
            response = await grpc_servicer.AnalyzeMedicalHistory(request, context)

        assert response.success is True
        assert len(response.analysis_summary) > 0
        assert len(response.risk_factors) > 0

    @pytest.mark.asyncio
    async def test_batch_analyze_inquiry_data_success(self, grpc_servicer):
        """测试批量分析问诊数据"""
        request = inquiry_service_pb2.BatchAnalyzeInquiryDataRequest(
            session_ids=["session-1", "session-2", "session-3"],
            analysis_types=["symptom_extraction", "tcm_mapping"]
        )

        context = MagicMock()

        # 模拟批量分析结果
        mock_result = {
            "success": True,
            "results": [
                {
                    "session_id": "session-1",
                    "analysis": {"symptoms": ["头痛"], "patterns": ["气虚证"]}
                },
                {
                    "session_id": "session-2",
                    "analysis": {"symptoms": ["发烧"], "patterns": ["热证"]}
                }
            ]
        }

        with patch.object(grpc_servicer, '_batch_analyze_inquiry_data', return_value=mock_result):
            response = await grpc_servicer.BatchAnalyzeInquiryData(request, context)

        assert response.success is True
        assert len(response.results) > 0

    @pytest.mark.asyncio
    async def test_error_handling(self, grpc_servicer):
        """测试错误处理"""
        # 模拟对话管理器异常
        grpc_servicer.dialogue_manager.start_session.side_effect = Exception("服务不可用")

        request = inquiry_service_pb2.StartInquirySessionRequest(
            user_id="test-user",
            agent_id="xiaoai"
        )

        context = MagicMock()

        response = await grpc_servicer.StartInquirySession(request, context)

        assert response.success is False
        assert "服务不可用" in response.error_message

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, grpc_servicer):
        """测试并发请求处理"""
        # 创建多个并发请求
        requests = []
        for i in range(5):
            request = inquiry_service_pb2.StartInquirySessionRequest(
                user_id=f"user-{i}",
                agent_id="xiaoai"
            )
            requests.append(request)

        context = MagicMock()

        # 并发执行
        tasks = [
            grpc_servicer.StartInquirySession(req, context)
            for req in requests
        ]

        responses = await asyncio.gather(*tasks)

        # 所有请求都应该成功
        for response in responses:
            assert response.success is True
            assert len(response.session_id) > 0

    @pytest.mark.asyncio
    async def test_request_validation(self, grpc_servicer):
        """测试请求验证"""
        # 测试各种无效请求

        # 1. 空用户ID
        request1 = inquiry_service_pb2.StartInquirySessionRequest(
            user_id="",
            agent_id="xiaoai"
        )

        context = MagicMock()
        response1 = await grpc_servicer.StartInquirySession(request1, context)
        assert response1.success is False

        # 2. 空会话ID
        request2 = inquiry_service_pb2.InteractWithUserRequest(
            session_id="",
            user_message="测试"
        )

        response_stream = grpc_servicer.InteractWithUser(request2, context)
        responses = []
        async for response in response_stream:
            responses.append(response)

        assert len(responses) > 0
        assert responses[-1].success is False

    @pytest.mark.asyncio
    async def test_streaming_response(self, grpc_servicer):
        """测试流式响应"""
        request = inquiry_service_pb2.InteractWithUserRequest(
            session_id="test-session-123",
            user_message="我头痛得很厉害，请帮我分析一下"
        )

        context = MagicMock()

        response_stream = grpc_servicer.InteractWithUser(request, context)
        responses = []

        async for response in response_stream:
            responses.append(response)

            # 检查响应结构
            assert hasattr(response, 'success')
            assert hasattr(response, 'response_text')
            assert hasattr(response, 'response_type')

        # 应该有多个流式响应
        assert len(responses) >= 1

        # 最后一个响应应该是完整的
        final_response = responses[-1]
        assert final_response.success is True
        assert len(final_response.response_text) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
