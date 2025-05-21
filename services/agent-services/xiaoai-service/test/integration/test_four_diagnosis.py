#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
四诊协调器集成测试
测试四诊服务的协调与融合功能
"""

import os
import sys
import unittest
import asyncio
import tempfile
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
import grpc
import pytest
import numpy as np
from PIL import Image

# 将项目根目录添加到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from xiaoai_service.internal.four_diagnosis.coordinator.coordinator import FourDiagnosisCoordinator
from xiaoai_service.internal.four_diagnosis.fusion.engine import MultimodalFusionEngine
from xiaoai_service.internal.four_diagnosis.reasoning.engine import TCMReasoningEngine
from xiaoai_service.internal.four_diagnosis.validation.validator import DiagnosticValidator
from xiaoai_service.integration.look_service.client import LookServiceClient
from xiaoai_service.integration.listen_service.client import ListenServiceClient
from xiaoai_service.integration.inquiry_service.client import InquiryServiceClient
from xiaoai_service.integration.palpation_service.client import PalpationServiceClient
from xiaoai_service.protos import four_diagnosis_pb2 as diagnosis_pb


@pytest.mark.asyncio
class TestFourDiagnosisCoordinator:
    """四诊协调器集成测试类"""
    
    @pytest.fixture
    async def setup_coordinator(self):
        """设置测试环境"""
        # 创建各服务客户端的模拟
        self.look_client = AsyncMock(spec=LookServiceClient)
        self.listen_client = AsyncMock(spec=ListenServiceClient)
        self.inquiry_client = AsyncMock(spec=InquiryServiceClient)
        self.palpation_client = AsyncMock(spec=PalpationServiceClient)
        
        # 创建引擎模拟
        self.fusion_engine = AsyncMock(spec=MultimodalFusionEngine)
        self.reasoning_engine = AsyncMock(spec=TCMReasoningEngine)
        self.validator = AsyncMock(spec=DiagnosticValidator)
        
        # 创建协调器实例
        self.coordinator = FourDiagnosisCoordinator(
            self.look_client,
            self.listen_client,
            self.inquiry_client,
            self.palpation_client,
            self.fusion_engine,
            self.reasoning_engine,
            self.validator
        )
        
        # 创建测试数据
        self.user_id = "test_user_123"
        self.session_id = str(uuid.uuid4())
        
        # 准备数据
        with tempfile.NamedTemporaryFile(suffix='.jpg') as f:
            # 创建一个简单的测试图像
            img = Image.new('RGB', (100, 100), color='red')
            img.save(f.name)
            with open(f.name, 'rb') as img_file:
                self.test_image_data = img_file.read()
        
        # 创建样本音频数据
        self.test_audio_data = b'\x00\x01\x02\x03' * 1000
        
        # 模拟望诊分析响应
        self.tongue_analysis_response = MagicMock()
        self.tongue_analysis_response.analysis_id = str(uuid.uuid4())
        self.tongue_analysis_response.tongue_color = "淡红"
        self.tongue_analysis_response.tongue_shape = "正常"
        self.tongue_analysis_response.coating_color = "薄白"
        self.tongue_analysis_response.coating_distribution = "均匀"
        self.tongue_analysis_response.features = ["淡红舌", "薄白苔"]
        self.tongue_analysis_response.metrics = {"舌色饱和度": 0.8, "舌色亮度": 0.7}
        self.tongue_analysis_response.analysis_summary = "舌质淡红，舌苔薄白，舌体正常"
        self.tongue_analysis_response.confidence = 0.92
        self.tongue_analysis_response.body_constitution = [
            {"constitution_type": "平和质", "confidence": 0.85},
            {"constitution_type": "气虚质", "confidence": 0.15}
        ]
        
        # 模拟闻诊分析响应
        self.voice_analysis_response = MagicMock()
        self.voice_analysis_response.analysis_id = str(uuid.uuid4())
        self.voice_analysis_response.voice_quality = "中等"
        self.voice_analysis_response.voice_strength = "适中"
        self.voice_analysis_response.voice_rhythm = "均匀"
        self.voice_analysis_response.voice_tone = "中等"
        self.voice_analysis_response.features = ["声音清亮", "语速适中"]
        self.voice_analysis_response.analysis_summary = "声音清亮，语速适中，指示气血调和"
        self.voice_analysis_response.confidence = 0.85
        
        # 设置客户端模拟响应
        self.look_client.analyze_tongue.return_value = self.tongue_analysis_response
        self.listen_client.analyze_voice.return_value = self.voice_analysis_response
        
        # 模拟融合结果
        self.fusion_result = diagnosis_pb.FusionResult(
            fusion_id=str(uuid.uuid4()),
            user_id=self.user_id,
            session_id=self.session_id,
            feature_weights={"tongue_color": 0.6, "voice_quality": 0.4},
            overall_confidence=0.88
        )
        self.fusion_engine.fuse_diagnostic_data.return_value = self.fusion_result
        
        # 模拟辨证结果
        self.syndrome_result = diagnosis_pb.SyndromeAnalysis(
            syndrome_type="脾胃虚弱",
            confidence=0.87,
            features=["舌淡", "声音低弱"],
            recommendations=["健脾和胃"]
        )
        self.constitution_result = diagnosis_pb.ConstitutionAnalysis(
            constitution_type="气虚质",
            confidence=0.82,
            features=["舌淡", "声音低弱"],
            recommendations=["补气健脾"]
        )
        self.reasoning_engine.analyze_fusion_result.return_value = (
            self.syndrome_result, 
            self.constitution_result
        )
        
        yield
        
        # 清理
        pass
    
    @pytest.mark.asyncio
    async def test_generate_diagnosis_report_with_look_and_listen(self, setup_coordinator):
        """测试生成包含望诊和闻诊数据的诊断报告"""
        # 创建请求对象
        look_data = diagnosis_pb.LookData()
        look_data.tongue_image = self.test_image_data
        look_data.metadata.device_id = "test_device_001"
        look_data.metadata.capture_time = "2024-05-16T10:30:00Z"
        look_data.metadata.lighting_condition = "natural"
        
        listen_data = diagnosis_pb.ListenData()
        listen_data.voice_audio = self.test_audio_data
        listen_data.audio_format = "wav"
        listen_data.sample_rate = 16000
        listen_data.channels = 1
        
        request = diagnosis_pb.DiagnosisRequest(
            user_id=self.user_id,
            session_id=self.session_id,
            include_look=True,
            include_listen=True,
            look_data=look_data,
            listen_data=listen_data
        )
        
        # 调用协调器生成报告
        report = await self.coordinator.generate_diagnosis_report(request)
        
        # 验证报告内容
        assert report.user_id == self.user_id
        assert report.session_id == self.session_id
        
        # 验证望诊结果
        assert hasattr(report, 'look_result')
        assert report.look_result.diagnosis_type == "look"
        
        # 验证闻诊结果
        assert hasattr(report, 'listen_result')
        assert report.listen_result.diagnosis_type == "listen"
        
        # 验证辨证结果
        assert hasattr(report, 'syndrome_analysis')
        assert report.syndrome_analysis.syndrome_type == "脾胃虚弱"
        assert report.syndrome_analysis.confidence > 0.8
        
        # 验证体质结果
        assert hasattr(report, 'constitution_analysis')
        assert report.constitution_analysis.constitution_type == "气虚质"
        assert report.constitution_analysis.confidence > 0.8
        
        # 验证客户端调用
        self.look_client.analyze_tongue.assert_called_once()
        self.listen_client.analyze_voice.assert_called_once()
        self.fusion_engine.fuse_diagnostic_data.assert_called_once()
        self.reasoning_engine.analyze_fusion_result.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_diagnosis_report_with_invalid_data(self, setup_coordinator):
        """测试使用无效数据生成诊断报告时的错误处理"""
        # 创建请求对象，但不包含任何诊断数据
        request = diagnosis_pb.DiagnosisRequest(
            user_id=self.user_id,
            session_id=self.session_id,
            include_look=True,
            include_listen=False
        )
        
        # 添加错误的望诊数据（空数据）
        request.look_data.CopyFrom(diagnosis_pb.LookData())
        
        # 调用协调器生成报告
        report = await self.coordinator.generate_diagnosis_report(request)
        
        # 验证报告包含错误信息
        assert "可用的诊断数据不足" in report.diagnostic_summary
        
        # 验证没有调用融合和推理
        self.fusion_engine.fuse_diagnostic_data.assert_not_called()
        self.reasoning_engine.analyze_fusion_result.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_service_failure_handling(self, setup_coordinator):
        """测试服务失败时的故障恢复"""
        # 模拟望诊服务失败
        self.look_client.analyze_tongue.side_effect = grpc.RpcError("服务不可用")
        
        # 创建请求对象
        look_data = diagnosis_pb.LookData()
        look_data.tongue_image = self.test_image_data
        
        listen_data = diagnosis_pb.ListenData()
        listen_data.voice_audio = self.test_audio_data
        listen_data.audio_format = "wav"
        
        request = diagnosis_pb.DiagnosisRequest(
            user_id=self.user_id,
            session_id=self.session_id,
            include_look=True,
            include_listen=True,
            look_data=look_data,
            listen_data=listen_data
        )
        
        # 调用协调器生成报告
        report = await self.coordinator.generate_diagnosis_report(request)
        
        # 验证仍然有闻诊结果
        assert hasattr(report, 'listen_result')
        assert report.listen_result.diagnosis_type == "listen"
        
        # 验证没有望诊结果
        assert not hasattr(report, 'look_result') or report.look_result.ByteSize() == 0
        
        # 验证诊断总结中包含错误信息
        assert "处理过程中的错误" in report.diagnostic_summary or "可用的诊断数据不足" in report.diagnostic_summary
    
    @pytest.mark.asyncio
    async def test_progress_tracking(self, setup_coordinator):
        """测试诊断进度跟踪"""
        # 创建请求对象
        look_data = diagnosis_pb.LookData()
        look_data.tongue_image = self.test_image_data
        
        request = diagnosis_pb.DiagnosisRequest(
            user_id=self.user_id,
            session_id=self.session_id,
            include_look=True,
            include_listen=False,
            look_data=look_data
        )
        
        # 调用协调器生成报告
        report = await self.coordinator.generate_diagnosis_report(request)
        
        # 获取进度
        progress_request = diagnosis_pb.DiagnosisProgressRequest(
            user_id=self.user_id,
            session_id=self.session_id
        )
        progress = await self.coordinator.get_diagnosis_progress(progress_request)
        
        # 验证进度值
        assert progress.user_id == self.user_id
        assert progress.session_id == self.session_id
        assert progress.look_completed == True
        assert progress.listen_completed == False
        
        # 由于只有望诊数据，验证融合未完成
        assert progress.fusion_completed == False
        assert progress.analysis_completed == False
        assert progress.overall_progress < 1.0


if __name__ == "__main__":
    # 如果直接运行此文件
    pytest.main(["-xvs", __file__]) 