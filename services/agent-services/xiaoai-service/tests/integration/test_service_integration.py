"""
服务集成测试
"""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import grpc
import pytest

from xiaoai.core.five_diagnosis_coordinator import FiveDiagnosisCoordinator
from xiaoai.models.diagnosis import DiagnosisData, DiagnosisRequest
from xiaoai.services.service_clients import (
    DiagnosisServiceClient,
    InquiryServiceClient,
    ListenServiceClient,
    LookServiceClient,
    PalpationServiceClient,
)


class TestServiceIntegration:
    """服务集成测试类"""

    @pytest.fixture
    async def coordinator(self):
        """创建五诊协调器实例"""
        coordinator = FiveDiagnosisCoordinator()
        await coordinator.initialize()
        yield coordinator
        await coordinator.cleanup()

    @pytest.fixture
    def mock_grpc_channel(self):
        """模拟gRPC通道"""
        channel = Mock(spec=grpc.aio.Channel)
        return channel

    @pytest.fixture
    def sample_diagnosis_request(self):
        """样本诊断请求"""
        return DiagnosisRequest(
            user_id="test_user",
            session_id="test_session",
            patient_info={"age": 35, "gender": "female", "height": 165, "weight": 60},
            chief_complaint="头痛失眠三个月",
            symptoms=["头痛", "失眠", "心悸"],
            medical_history=["高血压"],
            current_medications=["降压药"],
            lifestyle_info={"exercise": "偶尔", "diet": "正常", "stress_level": "高"},
        )

    @pytest.mark.asyncio
    async def test_inquiry_service_integration(self, coordinator, sample_diagnosis_request):
        """测试问诊服务集成"""
        with patch.object(coordinator.inquiry_client, "conduct_inquiry") as mock_inquiry:
            # 模拟问诊服务响应
            mock_inquiry.return_value = {
                "inquiry_id": "inquiry_123",
                "questions_asked": [
                    "请描述您的头痛症状",
                    "失眠持续多长时间了？",
                    "是否有其他伴随症状？",
                ],
                "patient_responses": [
                    "头痛主要在太阳穴，胀痛",
                    "失眠大概三个月了，难以入睡",
                    "还有心悸，特别是晚上",
                ],
                "extracted_symptoms": ["头痛", "失眠", "心悸", "胀痛"],
                "confidence": 0.85,
                "additional_info": {
                    "pain_location": "太阳穴",
                    "pain_type": "胀痛",
                    "sleep_issue": "难以入睡",
                    "palpitation_timing": "晚上",
                },
            }

            # 执行问诊
            result = await coordinator._conduct_inquiry(sample_diagnosis_request)

            assert result is not None
            assert "inquiry_id" in result
            assert "extracted_symptoms" in result
            assert result["confidence"] > 0.8
            assert "头痛" in result["extracted_symptoms"]
            assert "失眠" in result["extracted_symptoms"]

    @pytest.mark.asyncio
    async def test_look_service_integration(self, coordinator):
        """测试望诊服务集成"""
        with patch.object(coordinator.look_client, "analyze_appearance") as mock_look:
            # 模拟望诊服务响应
            mock_look.return_value = {
                "analysis_id": "look_123",
                "complexion": {
                    "color": "红润",
                    "luster": "有光泽",
                    "analysis": "面色红润，提示气血充足",
                },
                "tongue": {
                    "color": "淡红",
                    "coating": "薄白",
                    "texture": "润",
                    "analysis": "舌淡红苔薄白，正常舌象",
                },
                "eyes": {
                    "spirit": "有神",
                    "color": "正常",
                    "analysis": "目光有神，精神状态良好",
                },
                "body_build": {
                    "type": "中等",
                    "posture": "正常",
                    "analysis": "体型匀称，姿态自然",
                },
                "confidence": 0.82,
            }

            # 执行望诊
            image_data = b"fake_image_data"
            result = await coordinator._conduct_look_diagnosis(
                "test_user", "test_session", image_data
            )

            assert result is not None
            assert "complexion" in result
            assert "tongue" in result
            assert result["confidence"] > 0.8

    @pytest.mark.asyncio
    async def test_listen_service_integration(self, coordinator):
        """测试闻诊服务集成"""
        with patch.object(coordinator.listen_client, "analyze_audio") as mock_listen:
            # 模拟闻诊服务响应
            mock_listen.return_value = {
                "analysis_id": "listen_123",
                "voice_analysis": {
                    "tone": "正常",
                    "volume": "适中",
                    "clarity": "清晰",
                    "rhythm": "规律",
                    "analysis": "声音洪亮清晰，提示肺气充足",
                },
                "breathing_analysis": {
                    "pattern": "正常",
                    "depth": "适中",
                    "rate": 16,
                    "analysis": "呼吸平稳，无异常",
                },
                "cough_analysis": {
                    "present": False,
                    "type": None,
                    "analysis": "无咳嗽症状",
                },
                "confidence": 0.78,
            }

            # 执行闻诊
            audio_data = b"fake_audio_data"
            result = await coordinator._conduct_listen_diagnosis(
                "test_user", "test_session", audio_data
            )

            assert result is not None
            assert "voice_analysis" in result
            assert "breathing_analysis" in result
            assert result["confidence"] > 0.7

    @pytest.mark.asyncio
    async def test_palpation_service_integration(self, coordinator):
        """测试切诊服务集成"""
        with patch.object(coordinator.palpation_client, "analyze_pulse") as mock_palpation:
            # 模拟切诊服务响应
            mock_palpation.return_value = {
                "analysis_id": "palpation_123",
                "pulse_analysis": {
                    "rate": 72,
                    "rhythm": "规律",
                    "strength": "有力",
                    "type": "平脉",
                    "position_analysis": {"cun": "正常", "guan": "正常", "chi": "正常"},
                    "analysis": "脉象平和，气血调和",
                },
                "skin_analysis": {
                    "temperature": "正常",
                    "moisture": "适中",
                    "elasticity": "良好",
                    "analysis": "皮肤温润有弹性，营卫调和",
                },
                "confidence": 0.80,
            }

            # 执行切诊
            sensor_data = {
                "pulse_data": [72, 73, 71, 74, 72],
                "temperature": 36.5,
                "pressure_points": ["寸", "关", "尺"],
            }
            result = await coordinator._conduct_palpation_diagnosis(
                "test_user", "test_session", sensor_data
            )

            assert result is not None
            assert "pulse_analysis" in result
            assert "skin_analysis" in result
            assert result["confidence"] > 0.7

    @pytest.mark.asyncio
    async def test_calculation_service_integration(self, coordinator):
        """测试计算服务集成"""
        # 准备五诊数据
        five_diagnosis_data = {
            "inquiry": {"symptoms": ["头痛", "失眠", "心悸"], "confidence": 0.85},
            "look": {
                "complexion": "红润",
                "tongue": {"color": "淡红", "coating": "薄白"},
                "confidence": 0.82,
            },
            "listen": {
                "voice_analysis": {"tone": "正常", "volume": "适中"},
                "confidence": 0.78,
            },
            "palpation": {
                "pulse_analysis": {"rate": 72, "type": "平脉"},
                "confidence": 0.80,
            },
        }

        with patch.object(coordinator.calculation_client, "calculate_syndrome") as mock_calc:
            # 模拟计算服务响应
            mock_calc.return_value = {
                "calculation_id": "calc_123",
                "syndrome_analysis": {
                    "primary_syndrome": "心脾两虚",
                    "secondary_syndromes": ["气血不足"],
                    "confidence": 0.83,
                    "analysis_method": "综合辨证",
                },
                "constitution_analysis": {
                    "primary_constitution": "气虚质",
                    "secondary_constitutions": ["血瘀质"],
                    "confidence": 0.79,
                },
                "recommendations": {
                    "treatment_principle": "补益心脾，养血安神",
                    "lifestyle_advice": [
                        "规律作息，避免熬夜",
                        "适量运动，如太极拳",
                        "饮食清淡，多食补血食物",
                    ],
                    "dietary_suggestions": ["红枣桂圆粥", "当归炖鸡汤", "莲子百合汤"],
                },
                "confidence": 0.81,
            }

            # 执行计算分析
            result = await coordinator._conduct_calculation_analysis(
                "test_user", "test_session", five_diagnosis_data
            )

            assert result is not None
            assert "syndrome_analysis" in result
            assert "constitution_analysis" in result
            assert "recommendations" in result
            assert result["confidence"] > 0.8

    @pytest.mark.asyncio
    async def test_full_diagnosis_workflow(self, coordinator, sample_diagnosis_request):
        """测试完整诊断流程"""
        with (
            patch.object(coordinator, "_conduct_inquiry") as mock_inquiry,
            patch.object(coordinator, "_conduct_look_diagnosis") as mock_look,
            patch.object(coordinator, "_conduct_listen_diagnosis") as mock_listen,
            patch.object(coordinator, "_conduct_palpation_diagnosis") as mock_palpation,
            patch.object(coordinator, "_conduct_calculation_analysis") as mock_calc,
        ):

            # 模拟各个诊断步骤的响应
            mock_inquiry.return_value = {
                "extracted_symptoms": ["头痛", "失眠", "心悸"],
                "confidence": 0.85,
            }

            mock_look.return_value = {
                "complexion": "红润",
                "tongue": {"color": "淡红", "coating": "薄白"},
                "confidence": 0.82,
            }

            mock_listen.return_value = {
                "voice_analysis": {"tone": "正常"},
                "confidence": 0.78,
            }

            mock_palpation.return_value = {
                "pulse_analysis": {"rate": 72, "type": "平脉"},
                "confidence": 0.80,
            }

            mock_calc.return_value = {
                "syndrome_analysis": {"primary_syndrome": "心脾两虚"},
                "constitution_analysis": {"primary_constitution": "气虚质"},
                "recommendations": {"treatment_principle": "补益心脾"},
                "confidence": 0.81,
            }

            # 执行完整诊断
            result = await coordinator.coordinate_diagnosis(sample_diagnosis_request)

            assert result is not None
            assert result.session_id == "test_session"
            assert result.status == "completed"
            assert result.overall_confidence > 0.8
            assert "syndrome_analysis" in result.results

    @pytest.mark.asyncio
    async def test_service_failure_handling(self, coordinator, sample_diagnosis_request):
        """测试服务故障处理"""
        with patch.object(coordinator.inquiry_client, "conduct_inquiry") as mock_inquiry:
            # 模拟服务故障
            mock_inquiry.side_effect = grpc.RpcError("Service unavailable")

            # 执行诊断，应该优雅处理故障
            result = await coordinator.coordinate_diagnosis(sample_diagnosis_request)

            assert result is not None
            assert result.status in ["partial", "failed"]
            assert "inquiry" not in result.results or result.results["inquiry"] is None

    @pytest.mark.asyncio
    async def test_concurrent_diagnosis_sessions(self, coordinator):
        """测试并发诊断会话"""
        # 创建多个诊断请求
        requests = []
        for i in range(3):
            request = DiagnosisRequest(
                user_id=f"user_{i}",
                session_id=f"session_{i}",
                symptoms=[f"symptom_{i}"],
            )
            requests.append(request)

        with (
            patch.object(coordinator, "_conduct_inquiry") as mock_inquiry,
            patch.object(coordinator, "_conduct_calculation_analysis") as mock_calc,
        ):

            mock_inquiry.return_value = {"confidence": 0.8}
            mock_calc.return_value = {"confidence": 0.8}

            # 并发执行诊断
            tasks = [coordinator.coordinate_diagnosis(request) for request in requests]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 检查所有诊断都成功完成
            assert len(results) == 3
            assert all(not isinstance(r, Exception) for r in results)
            assert all(r.session_id == f"session_{i}" for i, r in enumerate(results))

    @pytest.mark.asyncio
    async def test_service_timeout_handling(self, coordinator, sample_diagnosis_request):
        """测试服务超时处理"""
        with patch.object(coordinator.inquiry_client, "conduct_inquiry") as mock_inquiry:
            # 模拟服务超时
            async def slow_service(*args, **kwargs):
                await asyncio.sleep(10)  # 模拟慢服务
                return {"confidence": 0.8}

            mock_inquiry.side_effect = slow_service

            # 设置较短的超时时间
            coordinator.service_timeout = 2

            # 执行诊断
            result = await coordinator.coordinate_diagnosis(sample_diagnosis_request)

            # 应该在超时后返回部分结果
            assert result is not None
            assert result.status in ["partial", "timeout"]

    @pytest.mark.asyncio
    async def test_data_validation_integration(self, coordinator):
        """测试数据验证集成"""
        # 创建无效的诊断请求
        invalid_request = DiagnosisRequest(
            user_id="", session_id="test_session", symptoms=[]  # 空用户ID  # 空症状列表
        )

        # 执行诊断
        result = await coordinator.coordinate_diagnosis(invalid_request)

        # 应该返回验证错误
        assert result is not None
        assert result.status == "failed"
        assert "validation" in result.error_message.lower()

    @pytest.mark.asyncio
    async def test_service_discovery_integration(self, coordinator):
        """测试服务发现集成"""
        # 测试服务健康检查
        health_status = await coordinator.check_services_health()

        assert isinstance(health_status, dict)
        assert "inquiry_service" in health_status
        assert "look_service" in health_status
        assert "listen_service" in health_status
        assert "palpation_service" in health_status
        assert "calculation_service" in health_status

    @pytest.mark.asyncio
    async def test_result_aggregation(self, coordinator):
        """测试结果聚合"""
        # 准备各个诊断步骤的结果
        diagnosis_results = {
            "inquiry": {"symptoms": ["头痛", "失眠"], "confidence": 0.85},
            "look": {"tongue": {"color": "红", "coating": "黄"}, "confidence": 0.80},
            "listen": {"voice": {"tone": "高亢"}, "confidence": 0.75},
            "palpation": {"pulse": {"type": "数", "rate": 90}, "confidence": 0.82},
            "calculation": {"syndrome": "心火亢盛", "confidence": 0.83},
        }

        # 聚合结果
        aggregated = coordinator._aggregate_diagnosis_results(diagnosis_results)

        assert "overall_confidence" in aggregated
        assert "primary_findings" in aggregated
        assert "data_quality_score" in aggregated
        assert aggregated["overall_confidence"] > 0

    @pytest.mark.asyncio
    async def test_session_management(self, coordinator):
        """测试会话管理"""
        session_id = "test_session_mgmt"
        user_id = "test_user_mgmt"

        # 创建会话
        session = await coordinator.create_diagnosis_session(user_id, session_id)
        assert session is not None
        assert session["session_id"] == session_id
        assert session["user_id"] == user_id
        assert session["status"] == "active"

        # 获取会话
        retrieved_session = await coordinator.get_diagnosis_session(session_id)
        assert retrieved_session is not None
        assert retrieved_session["session_id"] == session_id

        # 更新会话状态
        await coordinator.update_session_status(session_id, "completed")
        updated_session = await coordinator.get_diagnosis_session(session_id)
        assert updated_session["status"] == "completed"

        # 清理会话
        await coordinator.cleanup_session(session_id)
        cleaned_session = await coordinator.get_diagnosis_session(session_id)
        assert cleaned_session is None or cleaned_session["status"] == "cleaned"
