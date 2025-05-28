"""
集成测试

测试整个闻诊服务的端到端功能，包括音频分析、中医诊断、缓存系统等。
"""

import asyncio
import pytest
import numpy as np
from pathlib import Path
from unittest.mock import AsyncMock, patch
import tempfile
import json
import time

from listen_service.core.audio_analyzer import AudioAnalyzer
from listen_service.core.tcm_analyzer import TCMFeatureExtractor
from listen_service.models.audio_models import (
    AudioMetadata, AudioFormat, AnalysisRequest, VoiceFeatures
)
from listen_service.models.tcm_models import (
    TCMDiagnosis, ConstitutionType, EmotionState
)
from listen_service.utils.cache import AudioCache, MemoryCache
from listen_service.utils.performance import performance_monitor
from listen_service.delivery.rest_api import create_rest_app
from listen_service.delivery.grpc_server import ListenServiceGRPCServer


class TestEndToEndWorkflow:
    """端到端工作流测试"""
    
    @pytest.mark.asyncio
    async def test_complete_audio_analysis_workflow(self, audio_analyzer, sample_audio_data):
        """测试完整的音频分析工作流"""
        # 创建分析请求
        metadata = AudioMetadata(
            sample_rate=16000,
            channels=1,
            duration=1.0,
            format=AudioFormat.WAV,
            file_size=len(sample_audio_data),
            filename="test_audio.wav",
        )
        
        request = AnalysisRequest(
            request_id="integration-test-001",
            audio_data=sample_audio_data,
            metadata=metadata,
            analysis_type="complete",
            enable_caching=True,
        )
        
        # 执行分析
        result = await audio_analyzer.analyze_audio(request)
        
        # 验证结果
        assert result.success
        assert result.voice_features is not None
        assert result.voice_features.fundamental_frequency > 0
        assert len(result.voice_features.mfcc_features) > 0
        assert result.processing_time > 0
        
        # 验证缓存
        cache_key = audio_analyzer._generate_cache_key(sample_audio_data, "complete")
        cached_result = await audio_analyzer.cache.get_analysis_result(cache_key)
        assert cached_result is not None
    
    @pytest.mark.asyncio
    async def test_complete_tcm_diagnosis_workflow(self, tcm_analyzer, sample_voice_features):
        """测试完整的中医诊断工作流"""
        # 执行中医分析
        diagnosis = await tcm_analyzer.analyze_tcm_features(
            sample_voice_features,
            audio_metadata={
                "sample_rate": 16000,
                "duration": 1.0,
                "filename": "test_audio.wav",
            }
        )
        
        # 验证诊断结果
        assert diagnosis.diagnosis_id is not None
        assert diagnosis.constitution_type in ConstitutionType
        assert diagnosis.emotion_state in EmotionState
        assert 0 <= diagnosis.confidence_score <= 1
        assert len(diagnosis.constitution_scores) == len(ConstitutionType)
        assert len(diagnosis.emotion_scores) == len(EmotionState)
        assert len(diagnosis.organ_analysis) > 0
        
        # 验证建议
        assert len(diagnosis.recommendations) > 0
        for recommendation in diagnosis.recommendations:
            assert recommendation.category is not None
            assert recommendation.content is not None
    
    @pytest.mark.asyncio
    async def test_audio_to_tcm_complete_pipeline(self, audio_analyzer, tcm_analyzer, sample_audio_data):
        """测试从音频到中医诊断的完整管道"""
        # 第一步：音频分析
        metadata = AudioMetadata(
            sample_rate=16000,
            channels=1,
            duration=1.0,
            format=AudioFormat.WAV,
            file_size=len(sample_audio_data),
        )
        
        audio_request = AnalysisRequest(
            request_id="pipeline-test-001",
            audio_data=sample_audio_data,
            metadata=metadata,
            analysis_type="tcm_pipeline",
        )
        
        audio_result = await audio_analyzer.analyze_audio(audio_request)
        assert audio_result.success
        assert audio_result.voice_features is not None
        
        # 第二步：中医诊断
        tcm_diagnosis = await tcm_analyzer.analyze_tcm_features(
            audio_result.voice_features,
            audio_metadata=metadata.model_dump(),
        )
        
        # 验证完整管道结果
        assert tcm_diagnosis.confidence_score > 0
        assert tcm_diagnosis.constitution_type is not None
        assert tcm_diagnosis.emotion_state is not None
        
        # 验证诊断的一致性
        if tcm_diagnosis.constitution_type == ConstitutionType.QI_XU:
            assert tcm_diagnosis.constitution_scores[ConstitutionType.QI_XU] > 0.3
        
        # 验证情绪分析的合理性
        emotion_scores_sum = sum(tcm_diagnosis.emotion_scores.values())
        assert abs(emotion_scores_sum - 1.0) < 0.01  # 概率和应该接近1


class TestCacheIntegration:
    """缓存集成测试"""
    
    @pytest.mark.asyncio
    async def test_cache_hit_miss_workflow(self, audio_analyzer, sample_audio_data):
        """测试缓存命中和未命中的工作流"""
        metadata = AudioMetadata(
            sample_rate=16000,
            channels=1,
            duration=1.0,
            format=AudioFormat.WAV,
            file_size=len(sample_audio_data),
        )
        
        request = AnalysisRequest(
            request_id="cache-test-001",
            audio_data=sample_audio_data,
            metadata=metadata,
            analysis_type="cache_test",
            enable_caching=True,
        )
        
        # 第一次请求 - 缓存未命中
        start_time = time.time()
        result1 = await audio_analyzer.analyze_audio(request)
        first_duration = time.time() - start_time
        
        assert result1.success
        assert result1.cache_hit is False
        
        # 第二次请求 - 缓存命中
        start_time = time.time()
        result2 = await audio_analyzer.analyze_audio(request)
        second_duration = time.time() - start_time
        
        assert result2.success
        assert result2.cache_hit is True
        assert second_duration < first_duration  # 缓存应该更快
        
        # 验证结果一致性
        assert result1.voice_features.fundamental_frequency == result2.voice_features.fundamental_frequency
        assert result1.voice_features.mfcc_features == result2.voice_features.mfcc_features
    
    @pytest.mark.asyncio
    async def test_cache_expiration(self, audio_analyzer, sample_audio_data):
        """测试缓存过期"""
        # 使用短过期时间的缓存
        cache = AudioCache(MemoryCache(), default_ttl=1)  # 1秒过期
        audio_analyzer.cache = cache
        
        metadata = AudioMetadata(
            sample_rate=16000,
            channels=1,
            duration=1.0,
            format=AudioFormat.WAV,
            file_size=len(sample_audio_data),
        )
        
        request = AnalysisRequest(
            request_id="expiration-test-001",
            audio_data=sample_audio_data,
            metadata=metadata,
            analysis_type="expiration_test",
            enable_caching=True,
        )
        
        # 第一次请求
        result1 = await audio_analyzer.analyze_audio(request)
        assert result1.success
        assert result1.cache_hit is False
        
        # 等待缓存过期
        await asyncio.sleep(1.5)
        
        # 第二次请求 - 缓存应该已过期
        result2 = await audio_analyzer.analyze_audio(request)
        assert result2.success
        assert result2.cache_hit is False  # 缓存已过期，应该重新计算


class TestConcurrencyIntegration:
    """并发集成测试"""
    
    @pytest.mark.asyncio
    async def test_concurrent_audio_analysis(self, audio_analyzer, sample_audio_data):
        """测试并发音频分析"""
        # 创建多个并发请求
        tasks = []
        for i in range(5):
            metadata = AudioMetadata(
                sample_rate=16000,
                channels=1,
                duration=1.0,
                format=AudioFormat.WAV,
                file_size=len(sample_audio_data),
                filename=f"concurrent_test_{i}.wav",
            )
            
            request = AnalysisRequest(
                request_id=f"concurrent-test-{i:03d}",
                audio_data=sample_audio_data,
                metadata=metadata,
                analysis_type="concurrent",
            )
            
            task = audio_analyzer.analyze_audio(request)
            tasks.append(task)
        
        # 并发执行
        results = await asyncio.gather(*tasks)
        
        # 验证所有请求都成功
        for i, result in enumerate(results):
            assert result.success, f"Request {i} failed: {result.error_message}"
            assert result.voice_features is not None
            assert result.request_id == f"concurrent-test-{i:03d}"
    
    @pytest.mark.asyncio
    async def test_concurrent_tcm_analysis(self, tcm_analyzer, sample_voice_features):
        """测试并发中医分析"""
        # 创建多个并发中医分析任务
        tasks = []
        for i in range(3):
            task = tcm_analyzer.analyze_tcm_features(
                sample_voice_features,
                audio_metadata={
                    "sample_rate": 16000,
                    "duration": 1.0,
                    "filename": f"tcm_concurrent_{i}.wav",
                }
            )
            tasks.append(task)
        
        # 并发执行
        results = await asyncio.gather(*tasks)
        
        # 验证所有分析都成功
        for i, diagnosis in enumerate(results):
            assert diagnosis.diagnosis_id is not None
            assert diagnosis.confidence_score > 0
            assert diagnosis.constitution_type is not None
            assert diagnosis.emotion_state is not None


class TestErrorHandlingIntegration:
    """错误处理集成测试"""
    
    @pytest.mark.asyncio
    async def test_invalid_audio_data_handling(self, audio_analyzer):
        """测试无效音频数据的处理"""
        # 测试空音频数据
        metadata = AudioMetadata(
            sample_rate=16000,
            channels=1,
            duration=0.0,
            format=AudioFormat.WAV,
            file_size=0,
        )
        
        request = AnalysisRequest(
            request_id="error-test-001",
            audio_data=b"",
            metadata=metadata,
            analysis_type="error_test",
        )
        
        result = await audio_analyzer.analyze_audio(request)
        assert not result.success
        assert "音频数据为空" in result.error_message
    
    @pytest.mark.asyncio
    async def test_corrupted_audio_handling(self, audio_analyzer):
        """测试损坏音频数据的处理"""
        # 创建无效的音频数据
        corrupted_data = b"invalid audio data"
        
        metadata = AudioMetadata(
            sample_rate=16000,
            channels=1,
            duration=1.0,
            format=AudioFormat.WAV,
            file_size=len(corrupted_data),
        )
        
        request = AnalysisRequest(
            request_id="corrupted-test-001",
            audio_data=corrupted_data,
            metadata=metadata,
            analysis_type="corrupted_test",
        )
        
        result = await audio_analyzer.analyze_audio(request)
        # 应该优雅地处理错误
        if not result.success:
            assert result.error_message is not None
            assert len(result.error_message) > 0
    
    @pytest.mark.asyncio
    async def test_cache_failure_handling(self, sample_audio_data):
        """测试缓存失败的处理"""
        # 创建一个会失败的缓存
        failing_cache = AsyncMock()
        failing_cache.get_analysis_result.side_effect = Exception("Cache failure")
        failing_cache.set_analysis_result.side_effect = Exception("Cache failure")
        
        audio_analyzer = AudioAnalyzer(cache=AudioCache(failing_cache))
        
        metadata = AudioMetadata(
            sample_rate=16000,
            channels=1,
            duration=1.0,
            format=AudioFormat.WAV,
            file_size=len(sample_audio_data),
        )
        
        request = AnalysisRequest(
            request_id="cache-failure-test-001",
            audio_data=sample_audio_data,
            metadata=metadata,
            analysis_type="cache_failure_test",
            enable_caching=True,
        )
        
        # 即使缓存失败，分析也应该继续
        result = await audio_analyzer.analyze_audio(request)
        assert result.success  # 分析应该成功，即使缓存失败


class TestPerformanceIntegration:
    """性能集成测试"""
    
    @pytest.mark.asyncio
    async def test_performance_monitoring(self, audio_analyzer, sample_audio_data):
        """测试性能监控集成"""
        # 清除之前的指标
        performance_monitor.reset_metrics()
        
        metadata = AudioMetadata(
            sample_rate=16000,
            channels=1,
            duration=1.0,
            format=AudioFormat.WAV,
            file_size=len(sample_audio_data),
        )
        
        request = AnalysisRequest(
            request_id="performance-test-001",
            audio_data=sample_audio_data,
            metadata=metadata,
            analysis_type="performance_test",
        )
        
        # 执行分析
        result = await audio_analyzer.analyze_audio(request)
        assert result.success
        
        # 检查性能指标
        metrics = performance_monitor.get_metrics()
        assert "audio_analysis" in metrics
        assert metrics["audio_analysis"]["count"] > 0
        assert metrics["audio_analysis"]["total_time"] > 0
    
    @pytest.mark.asyncio
    async def test_memory_usage_stability(self, audio_analyzer, sample_audio_data):
        """测试内存使用稳定性"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # 执行多次分析
        for i in range(10):
            metadata = AudioMetadata(
                sample_rate=16000,
                channels=1,
                duration=1.0,
                format=AudioFormat.WAV,
                file_size=len(sample_audio_data),
                filename=f"memory_test_{i}.wav",
            )
            
            request = AnalysisRequest(
                request_id=f"memory-test-{i:03d}",
                audio_data=sample_audio_data,
                metadata=metadata,
                analysis_type="memory_test",
            )
            
            result = await audio_analyzer.analyze_audio(request)
            assert result.success
        
        # 检查内存使用
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # 内存增长应该在合理范围内（小于100MB）
        assert memory_increase < 100 * 1024 * 1024, f"Memory increased by {memory_increase / 1024 / 1024:.2f} MB"


class TestDataConsistency:
    """数据一致性测试"""
    
    @pytest.mark.asyncio
    async def test_audio_features_consistency(self, audio_analyzer, sample_audio_data):
        """测试音频特征提取的一致性"""
        metadata = AudioMetadata(
            sample_rate=16000,
            channels=1,
            duration=1.0,
            format=AudioFormat.WAV,
            file_size=len(sample_audio_data),
        )
        
        request = AnalysisRequest(
            request_id="consistency-test-001",
            audio_data=sample_audio_data,
            metadata=metadata,
            analysis_type="consistency_test",
            enable_caching=False,  # 禁用缓存以确保重新计算
        )
        
        # 多次执行相同的分析
        results = []
        for i in range(3):
            request.request_id = f"consistency-test-{i:03d}"
            result = await audio_analyzer.analyze_audio(request)
            assert result.success
            results.append(result)
        
        # 验证结果一致性
        base_features = results[0].voice_features
        for i, result in enumerate(results[1:], 1):
            features = result.voice_features
            
            # 基频应该一致（允许小误差）
            freq_diff = abs(features.fundamental_frequency - base_features.fundamental_frequency)
            assert freq_diff < 1.0, f"Fundamental frequency inconsistent in result {i}"
            
            # MFCC特征应该一致
            assert len(features.mfcc_features) == len(base_features.mfcc_features)
            for j, (mfcc1, mfcc2) in enumerate(zip(features.mfcc_features, base_features.mfcc_features)):
                diff = abs(mfcc1 - mfcc2)
                assert diff < 0.01, f"MFCC feature {j} inconsistent in result {i}"
    
    @pytest.mark.asyncio
    async def test_tcm_diagnosis_stability(self, tcm_analyzer, sample_voice_features):
        """测试中医诊断的稳定性"""
        # 多次执行相同的中医分析
        diagnoses = []
        for i in range(3):
            diagnosis = await tcm_analyzer.analyze_tcm_features(
                sample_voice_features,
                audio_metadata={
                    "sample_rate": 16000,
                    "duration": 1.0,
                    "filename": f"stability_test_{i}.wav",
                }
            )
            diagnoses.append(diagnosis)
        
        # 验证诊断稳定性
        base_diagnosis = diagnoses[0]
        for i, diagnosis in enumerate(diagnoses[1:], 1):
            # 体质类型应该一致
            assert diagnosis.constitution_type == base_diagnosis.constitution_type, \
                f"Constitution type inconsistent in diagnosis {i}"
            
            # 情绪状态应该一致
            assert diagnosis.emotion_state == base_diagnosis.emotion_state, \
                f"Emotion state inconsistent in diagnosis {i}"
            
            # 置信度应该相近
            confidence_diff = abs(diagnosis.confidence_score - base_diagnosis.confidence_score)
            assert confidence_diff < 0.1, f"Confidence score inconsistent in diagnosis {i}"


@pytest.mark.integration
class TestFullSystemIntegration:
    """完整系统集成测试"""
    
    @pytest.mark.asyncio
    async def test_rest_api_integration(self, sample_audio_data):
        """测试REST API集成"""
        from fastapi.testclient import TestClient
        
        # 创建测试应用
        app = create_rest_app()
        client = TestClient(app)
        
        # 测试健康检查
        response = client.get("/health")
        assert response.status_code == 200
        health_data = response.json()
        assert health_data["status"] in ["healthy", "degraded"]
        
        # 测试统计信息
        response = client.get("/stats")
        assert response.status_code == 200
        stats_data = response.json()
        assert "total_requests" in stats_data
    
    @pytest.mark.asyncio
    async def test_grpc_server_integration(self, sample_audio_data):
        """测试gRPC服务器集成"""
        # 创建gRPC服务器
        server = ListenServiceGRPCServer()
        
        # 测试服务器创建
        assert server.audio_analyzer is not None
        assert server.tcm_analyzer is not None
        assert server.cache is not None
        
        # 测试统计信息获取
        stats = await server.get_server_stats()
        assert "uptime" in stats
        assert "total_requests" in stats 