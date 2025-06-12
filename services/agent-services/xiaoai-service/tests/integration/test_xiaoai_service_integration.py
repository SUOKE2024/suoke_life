"""
小艾智能体服务集成测试
"""

import asyncio
import json
from datetime import datetime, timezone
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock, patch

import pytest
from xiaoai.accessibility.accessibility_service import AccessibilityService
from xiaoai.core.constitution_analyzer import ConstitutionAnalyzer
from xiaoai.core.five_diagnosis_coordinator import (
    DiagnosisRequest,
    DiagnosisStatus,
    DiagnosisType,
    FiveDiagnosisCoordinator,
)
from xiaoai.core.multimodal_processor import ModalityType, MultimodalProcessor
from xiaoai.core.recommendation_engine import RecommendationEngine
from xiaoai.core.syndrome_analyzer import SyndromeAnalyzer
from xiaoai.data.repositories import PostgreSQLRepository, RedisRepository
from xiaoai.integration.service_clients import ServiceClientManager


class TestXiaoAIServiceIntegration:
    """小艾智能体服务集成测试"""

    @pytest.fixture
    async def coordinator(self):
        """创建五诊协调器"""
        coordinator = FiveDiagnosisCoordinator()

        # 模拟初始化
        with patch.object(coordinator, "_initialize_service_clients"):
            await coordinator.initialize()

        yield coordinator
        await coordinator.close()

    @pytest.fixture
    def syndrome_analyzer(self):
        """创建辨证分析器"""
        return SyndromeAnalyzer()

    @pytest.fixture
    def constitution_analyzer(self):
        """创建体质分析器"""
        return ConstitutionAnalyzer()

    @pytest.fixture
    async def multimodal_processor(self):
        """创建多模态处理器"""
        processor = MultimodalProcessor()

        # 模拟初始化
        with patch.object(processor, "_initialize_text_processor"), patch.object(
            processor, "_initialize_audio_processor"
        ), patch.object(processor, "_initialize_image_processor"), patch.object(
            processor, "_initialize_accessibility_services"
        ):
            await processor.initialize()

        yield processor
        await processor.close()

    @pytest.fixture
    def recommendation_engine(self):
        """创建建议引擎"""
        return RecommendationEngine()

    @pytest.fixture
    async def service_client_manager(self):
        """创建服务客户端管理器"""
        manager = ServiceClientManager()

        # 模拟初始化
        with patch.object(manager, "_initialize_clients"):
            await manager.initialize()

        yield manager
        await manager.close()

    @pytest.mark.asyncio
    async def test_complete_diagnosis_workflow(
        self,
        coordinator,
        syndrome_analyzer,
        constitution_analyzer,
        recommendation_engine,
    ):
        """测试完整的诊断工作流程"""

        # 1. 创建诊断请求
        user_id = "test_user_123"
        session_id = "test_session_456"

        diagnosis_data = {
            DiagnosisType.LOOKING: {
                "tongue_image": "base64_encoded_image",
                "face_image": "base64_encoded_image",
                "complexion": "红润",
                "spirit": "精神饱满",
            },
            DiagnosisType.LISTENING: {
                "voice_audio": "base64_encoded_audio",
                "breathing_sound": "平稳",
                "cough_type": "无咳嗽",
            },
            DiagnosisType.INQUIRY: {
                "chief_complaint": "最近感觉疲劳",
                "present_illness": "持续一周的疲劳感",
                "past_history": "无特殊病史",
                "family_history": "父亲有高血压",
                "personal_history": "作息规律，饮食正常",
            },
            DiagnosisType.PALPATION: {
                "pulse_type": "脉象平和",
                "pulse_rate": 72,
                "pulse_strength": "中等",
                "abdomen_examination": "腹部柔软",
            },
        }

        # 2. 模拟服务客户端响应
        mock_responses = {
            DiagnosisType.LOOKING: {
                "confidence": 0.85,
                "features": {
                    "tongue_color": "淡红",
                    "tongue_coating": "薄白",
                    "face_color": "红润",
                    "spirit_state": "良好",
                },
                "analysis": "望诊显示整体状态良好",
            },
            DiagnosisType.LISTENING: {
                "confidence": 0.80,
                "features": {
                    "voice_quality": "清晰",
                    "breathing_pattern": "平稳",
                    "sound_analysis": "无异常",
                },
                "analysis": "闻诊未发现异常",
            },
            DiagnosisType.INQUIRY: {
                "confidence": 0.90,
                "features": {
                    "symptom_severity": "轻度",
                    "duration": "一周",
                    "pattern": "持续性疲劳",
                },
                "analysis": "问诊提示气虚可能",
            },
            DiagnosisType.PALPATION: {
                "confidence": 0.88,
                "features": {
                    "pulse_category": "平脉",
                    "pulse_characteristics": "和缓有力",
                    "physical_signs": "正常",
                },
                "analysis": "切诊显示脉象正常",
            },
        }

        # 模拟服务客户端
        with patch.object(coordinator, "service_manager") as mock_service_manager:
            mock_clients = {}
            for diagnosis_type in diagnosis_data.keys():
                mock_client = AsyncMock()
                mock_client.analyze.return_value = mock_responses[diagnosis_type]
                mock_clients[diagnosis_type.value] = mock_client

            mock_service_manager.get_client.side_effect = lambda name: mock_clients.get(
                name
            )

            # 3. 执行诊断流程
            diagnosis_results = await coordinator.start_diagnosis_process(
                user_id, session_id, diagnosis_data
            )

            # 4. 验证诊断结果
            assert len(diagnosis_results) == len(diagnosis_data)

            for result in diagnosis_results:
                assert result.status == DiagnosisStatus.COMPLETED
                assert result.confidence > 0.7
                assert result.features is not None
                assert result.raw_result is not None

            # 5. 执行辨证分析
            syndrome_result = syndrome_analyzer.analyze_syndrome(diagnosis_results)

            assert syndrome_result is not None
            assert syndrome_result.primary_syndromes is not None
            assert syndrome_result.overall_confidence > 0.0

            # 6. 执行体质分析
            constitution_result = constitution_analyzer.analyze_constitution(
                diagnosis_results
            )

            assert constitution_result is not None
            assert constitution_result.constitution_scores is not None
            assert constitution_result.overall_confidence > 0.0

            # 7. 生成建议
            recommendations = recommendation_engine.generate_recommendations(
                user_id=user_id,
                session_id=session_id,
                syndrome_analysis=syndrome_result,
                constitution_analysis=constitution_result,
                diagnosis_results=diagnosis_results,
            )

            assert recommendations is not None
            assert len(recommendations.recommendations) > 0
            assert recommendations.overall_strategy is not None

    @pytest.mark.asyncio
    async def test_multimodal_data_processing_integration(self, multimodal_processor):
        """测试多模态数据处理集成"""

        # 准备测试数据
        test_inputs = [
            {
                "modality_type": ModalityType.TEXT,
                "data": "患者主诉：最近感觉疲劳乏力，食欲不振",
                "metadata": {"language": "zh", "source": "inquiry"},
            },
            {
                "modality_type": ModalityType.IMAGE,
                "data": b"fake_image_data",
                "metadata": {"image_type": "tongue", "resolution": [640, 480]},
            },
            {
                "modality_type": ModalityType.AUDIO,
                "data": b"fake_audio_data",
                "metadata": {"format": "wav", "sample_rate": 16000},
            },
        ]

        # 模拟处理器方法
        with patch.object(
            multimodal_processor, "_process_text"
        ) as mock_text, patch.object(
            multimodal_processor, "_process_image"
        ) as mock_image, patch.object(
            multimodal_processor, "_process_audio"
        ) as mock_audio:

            # 设置模拟返回值
            mock_text.return_value = {
                "processed_data": {"symptoms": ["疲劳", "乏力", "食欲不振"]},
                "features": {"sentiment": "negative", "severity": "mild"},
                "confidence": 0.85,
            }

            mock_image.return_value = {
                "processed_data": {"tongue_analysis": "舌淡红，苔薄白"},
                "features": {"color": "淡红", "coating": "薄白"},
                "confidence": 0.80,
            }

            mock_audio.return_value = {
                "processed_data": {"voice_analysis": "声音低微"},
                "features": {"volume": "low", "clarity": "clear"},
                "confidence": 0.75,
            }

            # 执行批量处理
            results = await multimodal_processor.process_batch(test_inputs)

            # 验证结果
            assert len(results) == 3

            for result in results:
                assert result.status.value == "completed"
                assert result.confidence > 0.7
                assert result.processed_data is not None
                assert result.features is not None

    @pytest.mark.asyncio
    async def test_accessibility_service_integration(self):
        """测试无障碍服务集成"""

        accessibility_service = AccessibilityService()

        # 模拟初始化
        with patch.object(accessibility_service, "_initialize_tts"), patch.object(
            accessibility_service, "_initialize_stt"
        ), patch.object(accessibility_service, "_initialize_gesture_recognition"):

            await accessibility_service.initialize()

            # 测试文本转语音
            with patch.object(accessibility_service, "text_to_speech") as mock_tts:
                mock_tts.return_value = b"fake_audio_data"

                audio_data = await accessibility_service.text_to_speech(
                    "您的体质分析结果显示为气虚质，建议多休息"
                )

                assert audio_data is not None
                mock_tts.assert_called_once()

            # 测试语音转文本
            with patch.object(accessibility_service, "speech_to_text") as mock_stt:
                mock_stt.return_value = "我最近感觉很疲劳"

                text = await accessibility_service.speech_to_text(b"fake_audio_data")

                assert text == "我最近感觉很疲劳"
                mock_stt.assert_called_once()

            # 测试手势识别
            with patch.object(
                accessibility_service, "recognize_gesture"
            ) as mock_gesture:
                mock_gesture.return_value = "thumbs_up"

                gesture = await accessibility_service.recognize_gesture(
                    b"fake_video_frame"
                )

                assert gesture == "thumbs_up"
                mock_gesture.assert_called_once()

    @pytest.mark.asyncio
    async def test_data_persistence_integration(self):
        """测试数据持久化集成"""

        # 创建仓库实例
        pg_repo = PostgreSQLRepository()
        redis_repo = RedisRepository()

        # 模拟数据库连接
        with patch.object(pg_repo, "initialize") as mock_pg_init, patch.object(
            redis_repo, "initialize"
        ) as mock_redis_init:

            await pg_repo.initialize()
            await redis_repo.initialize()

            mock_pg_init.assert_called_once()
            mock_redis_init.assert_called_once()

            # 测试诊断数据存储
            test_diagnosis_data = {
                "user_id": "test_user_123",
                "session_id": "test_session_456",
                "diagnosis_type": "looking",
                "result": {"confidence": 0.85, "features": {"test": "data"}},
                "timestamp": datetime.now(timezone.utc),
            }

            with patch.object(pg_repo, "save_diagnosis_result") as mock_save:
                mock_save.return_value = "diagnosis_id_123"

                diagnosis_id = await pg_repo.save_diagnosis_result(test_diagnosis_data)

                assert diagnosis_id == "diagnosis_id_123"
                mock_save.assert_called_once_with(test_diagnosis_data)

            # 测试缓存操作
            with patch.object(redis_repo, "set") as mock_set, patch.object(
                redis_repo, "get"
            ) as mock_get:

                mock_get.return_value = None
                mock_set.return_value = True

                # 设置缓存
                await redis_repo.set("test_key", {"test": "value"}, ttl=3600)
                mock_set.assert_called_once()

                # 获取缓存
                cached_value = await redis_repo.get("test_key")
                mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_service_communication_integration(self, service_client_manager):
        """测试服务间通信集成"""

        # 模拟外部服务响应
        mock_responses = {
            "look": {
                "status": "success",
                "confidence": 0.85,
                "analysis": "望诊分析结果",
            },
            "listen": {
                "status": "success",
                "confidence": 0.80,
                "analysis": "闻诊分析结果",
            },
            "inquiry": {
                "status": "success",
                "confidence": 0.90,
                "analysis": "问诊分析结果",
            },
            "palpation": {
                "status": "success",
                "confidence": 0.88,
                "analysis": "切诊分析结果",
            },
        }

        # 模拟客户端调用
        for service_name, expected_response in mock_responses.items():
            mock_client = AsyncMock()
            mock_client.analyze.return_value = expected_response

            with patch.object(service_client_manager, "get_client") as mock_get_client:
                mock_get_client.return_value = mock_client

                client = service_client_manager.get_client(service_name)
                response = await client.analyze(
                    user_id="test_user",
                    session_id="test_session",
                    data={"test": "data"},
                )

                assert response == expected_response
                mock_client.analyze.assert_called_once()

    @pytest.mark.asyncio
    async def test_error_handling_integration(self, coordinator):
        """测试错误处理集成"""

        user_id = "test_user_123"
        session_id = "test_session_456"

        # 测试服务不可用的情况
        with patch.object(coordinator, "service_manager") as mock_service_manager:
            mock_client = AsyncMock()
            mock_client.analyze.side_effect = Exception("服务不可用")
            mock_service_manager.get_client.return_value = mock_client

            diagnosis_data = {DiagnosisType.LOOKING: {"test": "data"}}

            results = await coordinator.start_diagnosis_process(
                user_id, session_id, diagnosis_data
            )

            # 验证错误处理
            assert len(results) == 1
            assert results[0].status == DiagnosisStatus.FAILED
            assert results[0].error_message is not None

    @pytest.mark.asyncio
    async def test_performance_monitoring_integration(self, coordinator):
        """测试性能监控集成"""

        user_id = "test_user_123"
        session_id = "test_session_456"

        # 模拟正常的诊断流程
        with patch.object(coordinator, "service_manager") as mock_service_manager:
            mock_client = AsyncMock()
            mock_client.analyze.return_value = {
                "confidence": 0.85,
                "features": {"test": "feature"},
                "analysis": "测试分析",
            }
            mock_service_manager.get_client.return_value = mock_client

            diagnosis_data = {DiagnosisType.LOOKING: {"test": "data"}}

            start_time = datetime.now(timezone.utc)
            results = await coordinator.start_diagnosis_process(
                user_id, session_id, diagnosis_data
            )
            end_time = datetime.now(timezone.utc)

            # 验证性能指标
            assert len(results) == 1
            assert results[0].processing_time_ms > 0

            # 验证总体处理时间
            total_time = (end_time - start_time).total_seconds() * 1000
            assert total_time > 0
            assert results[0].processing_time_ms <= total_time

    @pytest.mark.asyncio
    async def test_concurrent_diagnosis_sessions(self, coordinator):
        """测试并发诊断会话"""

        # 创建多个并发会话
        sessions = []
        for i in range(5):
            user_id = f"user_{i}"
            session_id = f"session_{i}"
            sessions.append((user_id, session_id))

        # 模拟服务响应
        with patch.object(coordinator, "service_manager") as mock_service_manager:
            mock_client = AsyncMock()
            mock_client.analyze.return_value = {
                "confidence": 0.85,
                "features": {"test": "feature"},
                "analysis": "并发测试分析",
            }
            mock_service_manager.get_client.return_value = mock_client

            # 并发执行诊断
            tasks = []
            for user_id, session_id in sessions:
                diagnosis_data = {DiagnosisType.LOOKING: {"user": user_id}}
                task = coordinator.start_diagnosis_process(
                    user_id, session_id, diagnosis_data
                )
                tasks.append(task)

            # 等待所有任务完成
            all_results = await asyncio.gather(*tasks, return_exceptions=True)

            # 验证结果
            assert len(all_results) == 5

            for i, results in enumerate(all_results):
                assert not isinstance(results, Exception)
                assert len(results) == 1
                assert results[0].status == DiagnosisStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_session_management_integration(self, coordinator):
        """测试会话管理集成"""

        user_id = "test_user_123"
        metadata = {"source": "mobile_app", "version": "1.0.0"}

        # 创建诊断会话
        session = await coordinator.create_diagnosis_session(user_id, metadata)

        assert session.user_id == user_id
        assert session.metadata == metadata
        assert session.session_id is not None

        # 验证会话存储
        assert session.session_id in coordinator.active_sessions

        # 获取会话
        retrieved_session = await coordinator.get_diagnosis_session(session.session_id)
        assert retrieved_session.session_id == session.session_id
        assert retrieved_session.user_id == user_id

        # 关闭会话
        await coordinator.close_diagnosis_session(session.session_id)

        # 验证会话已移除
        assert session.session_id not in coordinator.active_sessions
