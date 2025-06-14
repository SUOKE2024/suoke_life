from typing import Dict, List, Any, Optional, Union

"""
test_gRPC_service - 索克生活项目模块
"""

from api.grpc import inquiry_service_pb2 as pb2
from api.grpc import inquiry_service_pb2_grpc as pb2_grpc
from concurrent import futures
from internal.delivery.inquiry_service_impl import InquiryServiceServicer
from internal.dialogue.dialogue_manager import DialogueManager
from internal.knowledge.tcm_knowledge_base import TCMKnowledgeBase
from internal.llm.health_risk_assessor import HealthRiskAssessor
from internal.llm.llm_client import LLMClient
from internal.llm.symptom_extractor import SymptomExtractor
from internal.llm.tcm_pattern_mapper import TCMPatternMapper
from internal.repository.session_repository import SessionRepository
from internal.repository.user_repository import UserRepository
import asyncio
import grpc
import os
import pytest
import pytest_asyncio
import sys
import time

from internal.common.exceptions import ServiceTimeoutError

"""
问诊服务gRPC接口集成测试
"""


# 导入生成的gRPC代码


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".. / ..")))


class TestGRPCService:
    """gRPC服务集成测试类"""

    @pytest.fixture
    def config(self)-> None:
        """测试配置"""
        return {
            "llm": {
                "use_mock_mode": True,
                "model_type": "test",
                "temperature": 0.7,
                "timeout_seconds": 10,
            },
            "dialogue": {
                "session_timeout_seconds": 1800,
                "default_language": "zh - CN",
                "max_history_messages": 20,
            },
            "symptom_extraction": {"confidence_threshold": 0.6, "max_symptoms": 10},
            "tcm_pattern_mapping": {"confidence_threshold": 0.6, "max_patterns": 5},
            "database": {
                "type": "memory",  # 使用内存数据库进行测试
            },
            "server": {
                "port": 50099,  # 测试专用端口
                "max_workers": 2,
            },
        }

    @pytest_asyncio.fixture
    async def service_components(self, config):
        """创建服务组件"""
        # 初始化存储库
        session_repository = SessionRepository(config)
        user_repository = UserRepository(config)

        # 初始化LLM客户端
        llm_client = LLMClient(config)

        # 初始化症状提取器
        symptom_extractor = SymptomExtractor(config)

        # 初始化TCM证型映射器
        tcm_pattern_mapper = TCMPatternMapper(config)

        # 初始化健康风险评估器
        health_risk_assessor = HealthRiskAssessor(config)

        # 初始化TCM知识库
        tcm_knowledge_base = TCMKnowledgeBase(config)

        # 初始化对话管理器
        dialogue_manager = DialogueManager(
            llm_client = llm_client,
            session_repository = session_repository,
            user_repository = user_repository,
            config = config,
        )

        return dialogue_manager, symptom_extractor, tcm_pattern_mapper, health_risk_assessor, tcm_knowledge_base, llm_client

    @pytest_asyncio.fixture
    async def grpc_service(self, config, service_components):
        """创建gRPC服务"""
        dialogue_manager, symptom_extractor, tcm_pattern_mapper, health_risk_assessor, tcm_knowledge_base, llm_client = (
            service_components
        )

        # 初始化服务实现
        servicer = InquiryServiceServicer(
            dialogue_manager = dialogue_manager,
            symptom_extractor = symptom_extractor,
            tcm_pattern_mapper = tcm_pattern_mapper,
            health_risk_assessor = health_risk_assessor,
            tcm_knowledge_base = tcm_knowledge_base,
            config = config,
        )

        # 创建服务器
        server = grpc.aio.server(
            futures.ThreadPoolExecutor(max_workers = config["server"]["max_workers"])
        )

        # 注册服务
        pb2_grpc.add_InquiryServiceServicer_to_server(servicer, server)

        # 添加服务器端口
        server_address = f"localhost:{config['server']['port']}"
        server.add_insecure_port(server_address)

        # 启动服务器
        await server.start()

        # 返回服务器和地址
        yield server, server_address

        # 关闭服务器
        await server.stop(0)

    @pytest_asyncio.fixture
    async def grpc_channel(self, grpc_service):
        """创建gRPC通道"""
        server, server_address = grpc_service

        # 创建通道
        channel = grpc.aio.insecure_channel(server_address)

        # 等待通道就绪
        try:
            await asyncio.wait_for(channel.channel_ready(), timeout = 5)
        except (asyncio.TimeoutError, ServiceTimeoutError):
            pytest.fail("gRPC通道连接超时")

        # 返回通道
        yield channel

        # 关闭通道
        await channel.close()

    @pytest_asyncio.fixture
    async def grpc_stub(self, grpc_channel):
        """创建gRPC存根"""
        return pb2_grpc.InquiryServiceStub(grpc_channel)

    @pytest.mark.asyncio
    async def test_start_inquiry_session(self, grpc_stub):
        """测试开始问诊会话"""
        # 创建请求
        request = pb2.StartSessionRequest(
            user_id = "test_user_12345",
            session_type = "general",
            language_preference = "zh - CN",
            context_data = {"test_key": "test_value"},
        )

        # 发送请求
        response = await grpc_stub.StartInquirySession(request)

        # 验证响应
        assert response.session_id ! = ""
        assert response.welcome_message ! = ""
        assert len(response.welcome_message) > 10
        assert response.timestamp > 0

        # 保存会话ID用于后续测试
        session_id = response.session_id
        return session_id

    @pytest.mark.asyncio
    async def test_interaction_flow(self, grpc_stub):
        """测试完整交互流程"""
        # 1. 开始会话
        start_request = pb2.StartSessionRequest(
            user_id = "test_user_flow",
            session_type = "general",
            language_preference = "zh - CN",
        )

        start_response = await grpc_stub.StartInquirySession(start_request)
        session_id = start_response.session_id
        assert session_id ! = ""

        # 2. 发送用户问题
        interact_request = pb2.InteractionRequest(
            session_id = session_id,
            user_message = "我最近头痛很严重，特别是在右侧太阳穴，压力很大时会更明显",
            timestamp = int(time.time()),
        )

        # 收集流式响应
        responses = []
        async for response in grpc_stub.InteractWithUser(interact_request):
            responses.append(response)

        assert len(responses) > 0
        assert responses[0].response_text ! = ""
        assert len(responses[0].detected_symptoms) > = 0

        # 3. 结束会话
        end_request = pb2.EndSessionRequest(session_id = session_id, feedback = "测试完成")

        end_response = await grpc_stub.EndInquirySession(end_request)

        assert end_response.session_id == session_id
        assert end_response.session_duration > 0

    @pytest.mark.asyncio
    async def test_extract_symptoms(self, grpc_stub):
        """测试症状提取API"""
        request = pb2.SymptomsExtractionRequest(
            text_content = """
            最近两周我一直感到头晕目眩，有时站起来时会感到天旋地转，需要扶着东西才能站稳。
            昨天开始出现了轻微的恶心感，食欲也比平时差。我有点担心是不是贫血或者低血压，
            因为我之前有过类似的情况。现在这种情况影响到了我的日常工作和生活。
            """,
            user_id = "test_user",
            language = "zh - CN",
        )

        response = await grpc_stub.ExtractSymptoms(request)

        assert response.confidence_score > 0
        assert len(response.symptoms) > 0

        # 验证至少包含头晕的症状
        has_dizziness = False
        for symptom in response.symptoms:
            if "头晕" in symptom.symptom_name:
                has_dizziness = True
                break

        assert has_dizziness, "未检测到头晕症状"

    @pytest.mark.asyncio
    async def test_tcm_pattern_mapping(self, grpc_stub):
        """测试中医证型映射API"""
        # 创建症状信息
        symptoms = [
            pb2.SymptomInfo(
                symptom_name = "头晕目眩",
                severity = pb2.SymptomInfo.MODERATE,
                onset_time = int(time.time()) - 1209600,  # 两周前
                duration = 1209600,  # 持续两周
                description = "站起来时会感到天旋地转",
                confidence = 0.9,
            ),
            pb2.SymptomInfo(
                symptom_name = "恶心",
                severity = pb2.SymptomInfo.MILD,
                onset_time = int(time.time()) - 86400,  # 一天前
                duration = 86400,  # 持续一天
                description = "轻微恶心感",
                confidence = 0.85,
            ),
            pb2.SymptomInfo(
                symptom_name = "食欲不振",
                severity = pb2.SymptomInfo.MILD,
                onset_time = int(time.time()) - 86400,  # 一天前
                duration = 86400,  # 持续一天
                description = "食欲比平时差",
                confidence = 0.8,
            ),
        ]

        # 创建请求
        request = pb2.TCMPatternMappingRequest(
            symptoms = symptoms,
            user_constitution = "BALANCED",
            body_locations = [
                pb2.BodyLocation(
                    location_name = "头部",
                    associated_symptoms = ["头晕目眩"],
                    side = "central",
                )
            ],
            temporal_factors = [
                pb2.TemporalFactor(
                    factor_type = "posture",
                    description = "站立时加重",
                    symptoms_affected = ["头晕目眩"],
                )
            ],
        )

        response = await grpc_stub.MapToTCMPatterns(request)

        assert response.confidence_score > 0
        assert len(response.primary_patterns) > 0
        assert response.interpretation ! = ""

    @pytest.mark.asyncio
    async def test_analyze_medical_history(self, grpc_stub):
        """测试病史分析API"""
        request = pb2.MedicalHistoryRequest(
            user_id = "test_user",
            medical_records = [
                pb2.MedicalRecord(
                    condition = "高血压",
                    diagnosis_time = int(time.time()) - 31536000,  # 一年前
                    treatment = "降压药物治疗",
                    outcome = "血压控制在正常范围",
                    symptoms = ["头痛", "头晕", "耳鸣"],
                ),
                pb2.MedicalRecord(
                    condition = "感冒",
                    diagnosis_time = int(time.time()) - 2592000,  # 一个月前
                    treatment = "感冒药、休息",
                    outcome = "痊愈",
                    symptoms = ["发热", "咳嗽", "流涕", "喉咙痛"],
                ),
            ],
            family_history = ["父亲高血压", "母亲糖尿病"],
            additional_info = {"过敏史": "青霉素过敏"},
        )

        response = await grpc_stub.AnalyzeMedicalHistory(request)

        assert len(response.chronic_conditions) > 0
        assert len(response.risk_factors) > 0
        assert response.lifestyle_impact.overall_impact_score > 0

    @pytest.mark.asyncio
    async def test_health_risk_assessment(self, grpc_stub):
        """测试健康风险评估API"""
        # 创建当前症状
        current_symptoms = [
            pb2.SymptomInfo(
                symptom_name = "头晕目眩",
                severity = pb2.SymptomInfo.MODERATE,
                onset_time = int(time.time()) - 1209600,  # 两周前
                duration = 1209600,  # 持续两周
                description = "站起来时会感到天旋地转",
                confidence = 0.9,
            ),
            pb2.SymptomInfo(
                symptom_name = "血压升高",
                severity = pb2.SymptomInfo.MODERATE,
                onset_time = int(time.time()) - 604800,  # 一周前
                duration = 604800,  # 持续一周
                description = "血压测量值为150 / 95",
                confidence = 0.95,
            ),
        ]

        # 创建请求
        request = pb2.HealthRiskRequest(
            user_id = "test_user",
            current_symptoms = current_symptoms,
            medical_history = pb2.MedicalHistoryRequest(
                user_id = "test_user",
                medical_records = [
                    pb2.MedicalRecord(
                        condition = "高血压",
                        diagnosis_time = int(time.time()) - 31536000,  # 一年前
                        treatment = "降压药物治疗",
                        outcome = "血压控制在正常范围",
                        symptoms = ["头痛", "头晕", "耳鸣"],
                    )
                ],
                family_history = ["父亲高血压", "母亲糖尿病"],
            ),
            health_profile = pb2.HealthProfile(
                user_id = "test_user",
                constitution_type = pb2.HealthProfile.BALANCED,
                health_goals = ["控制血压", "减轻体重"],
            ),
        )

        response = await grpc_stub.AssessHealthRisks(request)

        assert len(response.immediate_risks) > 0
        assert len(response.long_term_risks) > 0
        assert len(response.prevention_strategies) > 0
        assert response.overall_risk_score > 0

if __name__ == "__main__":
    pytest.main([" - xvs", __file__])
