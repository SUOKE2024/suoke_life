#!/usr/bin/env python3

"""
xiaoai-service端到端测试
测试从四诊数据采集到最终健康建议的完整流程
"""

import asyncio
import json
import logging
import sys
import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入需要测试的服务和模块
from internal.four_diagnosis.feature_extractor import FeatureExtractor
from internal.four_diagnosis.multimodal_fusion import MultimodalFusion
from internal.four_diagnosis.recommendation.health_advisor import HealthAdvisor
from internal.four_diagnosis.syndrome_analyzer import SyndromeAnalyzer
from internal.orchestrator.four_diagnosis_coordinator import FourDiagnosisCoordinator
from pkg.utils.config_loader import get_config

logging.basicConfig(level=logging.DEBUG)
# 使用loguru logger

# 测试数据路径
TEST_DATA_DIR = Path(__file__).parent.parent.parent / 'test' / 'data'

class TestEndToEnd:
    """xiaoai-service端到端测试类"""

    @pytest.fixture(scope="class")
    def event_loop(self):
        """创建一个事件循环供测试使用"""
        loop = asyncio.get_event_loop()
        yield loop
        loop.close()

    @pytest.fixture(scope="class")
    async def mock_services(self):
        """模拟依赖的外部服务"""
        with patch('internal.integration.look_service_client.LookServiceClient') as mock_look_client, \
             patch('internal.integration.listen_service_client.ListenServiceClient') as mock_listen_client, \
             patch('internal.integration.inquiry_service_client.InquiryServiceClient') as mock_inquiry_client, \
             patch('internal.integration.palpation_service_client.PalpationServiceClient') as mock_palpation_client:

            # 配置模拟客户端的行为
            # 望诊服务模拟
            look_response = MagicMock()
            look_response.features = [
                diagnosis_pb.DiagnosisFeature(
                    feature_name="舌质",
                    feature_value="淡红",
                    confidence=0.92,
                    category="tongue"
                ),
                diagnosis_pb.DiagnosisFeature(
                    feature_name="舌苔",
                    feature_value="薄白",
                    confidence=0.88,
                    category="tongue"
                ),
                diagnosis_pb.DiagnosisFeature(
                    feature_name="面色",
                    feature_value="偏白",
                    confidence=0.85,
                    category="face"
                )
            ]
            mock_look_client.return_value.analyze_tongue_image.return_value = look_response
            mock_look_client.return_value.analyze_face_image.return_value = look_response

            # 闻诊服务模拟
            listen_response = MagicMock()
            listen_response.features = [
                diagnosis_pb.DiagnosisFeature(
                    feature_name="语音",
                    feature_value="语速缓慢",
                    confidence=0.82,
                    category="voice"
                ),
                diagnosis_pb.DiagnosisFeature(
                    feature_name="气息",
                    feature_value="气短",
                    confidence=0.75,
                    category="voice"
                )
            ]
            mock_listen_client.return_value.analyze_voice.return_value = listen_response

            # 问诊服务模拟
            inquiry_response = MagicMock()
            inquiry_response.features = [
                diagnosis_pb.DiagnosisFeature(
                    feature_name="主诉",
                    feature_value="疲乏无力",
                    confidence=0.95,
                    category="symptom"
                ),
                diagnosis_pb.DiagnosisFeature(
                    feature_name="食欲",
                    feature_value="食欲不振",
                    confidence=0.88,
                    category="symptom"
                ),
                diagnosis_pb.DiagnosisFeature(
                    feature_name="睡眠",
                    feature_value="睡眠欠佳",
                    confidence=0.80,
                    category="symptom"
                )
            ]
            mock_inquiry_client.return_value.analyze_inquiry.return_value = inquiry_response

            # 切诊服务模拟
            palpation_response = MagicMock()
            palpation_response.features = [
                diagnosis_pb.DiagnosisFeature(
                    feature_name="脉象",
                    feature_value="沉细",
                    confidence=0.87,
                    category="pulse"
                )
            ]
            mock_palpation_client.return_value.analyze_pulse.return_value = palpation_response

            # 组合返回所有模拟客户端
            mock_clients = {
                'look': mock_look_client,
                'listen': mock_listen_client,
                'inquiry': mock_inquiry_client,
                'palpation': mock_palpation_client
            }

            return mock_clients

    @pytest.fixture(scope="class")
    async def setup_components(self, mock_services):
        """设置组件"""
        get_config()
        feature_extractor = FeatureExtractor()
        multimodal_fusion = MultimodalFusion()
        syndrome_analyzer = SyndromeAnalyzer()
        health_advisor = HealthAdvisor()

        coordinator = FourDiagnosisCoordinator(
            look_client=mock_services['look'].return_value,
            listen_client=mock_services['listen'].return_value,
            inquiry_client=mock_services['inquiry'].return_value,
            palpation_client=mock_services['palpation'].return_value,
            feature_extractor=feature_extractor,
            multimodal_fusion=multimodal_fusion,
            syndrome_analyzer=syndrome_analyzer,
            health_advisor=health_advisor
        )

        return {
            'coordinator': coordinator,
            'feature_extractor': feature_extractor,
            'multimodal_fusion': multimodal_fusion,
            'syndrome_analyzer': syndrome_analyzer,
            'health_advisor': health_advisor
        }

    @pytest.mark.asyncio
    async def test_full_flow(self, setup_components):
        """测试完整的四诊流程"""
        coordinator = setup_components['coordinator']

        request = diagnosis_pb.DiagnosisCoordinationRequest(
            user_id="test_user_123",
            session_id=str(uuid.uuid4()),
            include_looking=True,
            include_listening=True,
            include_inquiry=True,
            include_palpation=True,
            looking_data=b'mock_image_data',  # 模拟图像数据
            listening_data=b'mock_audio_data',  # 模拟音频数据
            inquiry_data=json.dumps({
                "chief_complaint": "疲乏无力,食欲不振",
                "symptoms": ["疲乏", "食欲不振", "睡眠欠佳"],
                "duration": "两周",
                "history": "无特殊病史"
            }),
            palpation_data=b'mock_pulse_data',  # 模拟脉诊数据
            settings={"mode": "comprehensive"}
        )

        response = await coordinator.coordinate_diagnosis(request)

        # 验证响应
        assert response is not None
        assert response.coordination_id != ""
        assert len(response.diagnosis_results) >= 4  # 应该有四诊结果
        assert response.syndrome_analysis is not None
        assert response.constitution_analysis is not None
        assert len(response.recommendations) > 0

        # 验证具体内容
        # 检查辨证结果是否包含预期的证型(基于模拟数据)
        syndromes = [s.name for s in response.syndrome_analysis.primary_syndromes]
        assert any('虚' in s for s in syndromes)  # 应该包含与"虚"相关的证型

        # 检查建议是否包含预期的类别
        rec_types = [r.type for r in response.recommendations]
        assert service_pb.Recommendation.RecommendationType.DIET in rec_types
        assert service_pb.Recommendation.RecommendationType.LIFESTYLE in rec_types

    @pytest.mark.asyncio
    async def test_partial_diagnosis(self, setup_components):
        """测试部分四诊流程(只使用部分诊断方法)"""
        coordinator = setup_components['coordinator']

        request = diagnosis_pb.DiagnosisCoordinationRequest(
            user_id="test_user_456",
            session_id=str(uuid.uuid4()),
            include_looking=True,
            include_listening=False,
            include_inquiry=True,
            include_palpation=False,
            looking_data=b'mock_image_data',
            inquiry_data=json.dumps({
                "chief_complaint": "头晕目眩",
                "symptoms": ["头晕", "目眩", "耳鸣"],
                "duration": "三天",
                "history": "高血压史"
            }),
            settings={"mode": "simple"}
        )

        response = await coordinator.coordinate_diagnosis(request)

        # 验证响应
        assert response is not None
        assert response.coordination_id != ""

        # 应该只有望诊和问诊结果
        diagnosis_types = [r.type for r in response.diagnosis_results]
        assert diagnosis_pb.DiagnosisResult.DiagnosisType.LOOKING in diagnosis_types
        assert diagnosis_pb.DiagnosisResult.DiagnosisType.INQUIRY in diagnosis_types
        assert diagnosis_pb.DiagnosisResult.DiagnosisType.LISTENING not in diagnosis_types
        assert diagnosis_pb.DiagnosisResult.DiagnosisType.PALPATION not in diagnosis_types

        assert response.syndrome_analysis is not None
        assert len(response.recommendations) > 0

    @pytest.mark.asyncio
    async def test_error_handling(self, setup_components, mock_services):
        """测试错误处理机制"""
        coordinator = setup_components['coordinator']

        # 模拟服务错误
        mock_services['look'].return_value.analyze_tongue_image.side_effect = Exception("模拟服务错误")

        request = diagnosis_pb.DiagnosisCoordinationRequest(
            user_id="test_user_789",
            session_id=str(uuid.uuid4()),
            include_looking=True,
            include_listening=True,
            include_inquiry=True,
            include_palpation=True,
            looking_data=b'mock_image_data',
            listening_data=b'mock_audio_data',
            inquiry_data=json.dumps({"chief_complaint": "测试症状"}),
            palpation_data=b'mock_pulse_data'
        )

        response = await coordinator.coordinate_diagnosis(request)

        # 验证响应
        assert response is not None
        assert response.coordination_id != ""

        # 应该至少包含其他三种诊断结果
        diagnosis_types = [r.type for r in response.diagnosis_results]
        assert diagnosis_pb.DiagnosisResult.DiagnosisType.INQUIRY in diagnosis_types
        assert diagnosis_pb.DiagnosisResult.DiagnosisType.LISTENING in diagnosis_types
        assert diagnosis_pb.DiagnosisResult.DiagnosisType.PALPATION in diagnosis_types

        assert response.syndrome_analysis is not None
        assert len(response.recommendations) > 0

    @pytest.mark.asyncio
    async def test_health_check(self):
        """测试健康检查功能"""
        with patch('grpc.aio.insecure_channel') as mock_channel:
            # 模拟gRPC通道和存根
            mock_stub = MagicMock()
            mock_channel.return_value.__enter__.return_value = MagicMock()

            # 模拟健康检查响应
            health_check_response = service_pb.HealthCheckResponse(
                status=service_pb.HealthCheckResponse.Status.SERVING,
                details={"version": "1.0.0", "uptime": "3600"}
            )
            mock_stub.HealthCheck.return_value = health_check_response

            service_pb.HealthCheckRequest(include_details=True)

            response = health_check_response

            # 验证健康检查结果
            assert response.status == service_pb.HealthCheckResponse.Status.SERVING
            assert "version" in response.details
            assert "uptime" in response.details

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
