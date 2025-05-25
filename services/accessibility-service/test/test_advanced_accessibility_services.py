#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
高级无障碍服务测试套件
测试VR/AR适配、记忆辅助、音频可视化三个新服务
"""

import pytest
import asyncio
import json
import time
import numpy as np
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone, timedelta

# 导入服务实现
from ..internal.service.implementations.vr_accessibility_impl import (
    VRAccessibilityServiceImpl, VRPlatform, AccessibilityFeature
)
from ..internal.service.implementations.memory_assistance_impl import (
    MemoryAssistanceServiceImpl, MemoryType, ReminderType
)
from ..internal.service.implementations.audio_visualization_impl import (
    AudioVisualizationServiceImpl, VisualizationType, ColorScheme
)


class TestVRAccessibilityService:
    """VR/AR无障碍适配服务测试"""
    
    @pytest.fixture
    async def vr_service(self):
        """创建VR无障碍服务实例"""
        model_manager = Mock()
        cache_manager = AsyncMock()
        
        service = VRAccessibilityServiceImpl(
            model_manager=model_manager,
            cache_manager=cache_manager,
            enabled=True
        )
        
        await service.initialize()
        return service
    
    @pytest.mark.asyncio
    async def test_detect_vr_platform(self, vr_service):
        """测试VR平台检测"""
        device_info = {
            "device_name": "Oculus Quest 2",
            "manufacturer": "Meta",
            "model": "Quest2",
            "capabilities": ["6dof", "hand_tracking", "eye_tracking"]
        }
        
        result = await vr_service.detect_vr_platform(device_info)
        
        assert result["success"] is True
        assert "platform" in result
        assert "confidence" in result
        assert result["confidence"] > 0.8
    
    @pytest.mark.asyncio
    async def test_create_accessibility_session(self, vr_service):
        """测试创建无障碍会话"""
        user_id = "test_user_001"
        platform = VRPlatform.OCULUS_QUEST
        accessibility_profile = {
            "visual_impairment": "moderate",
            "hearing_impairment": "none",
            "motor_impairment": "mild",
            "cognitive_impairment": "none",
            "preferences": {
                "audio_enhancement": True,
                "haptic_feedback": True,
                "voice_control": True
            }
        }
        
        result = await vr_service.create_accessibility_session(
            user_id, platform, accessibility_profile
        )
        
        assert result["success"] is True
        assert "session_id" in result
        assert result["user_id"] == user_id
        assert "accessibility_features" in result
    
    @pytest.mark.asyncio
    async def test_configure_spatial_audio(self, vr_service):
        """测试空间音频配置"""
        user_id = "test_user_001"
        session_id = "session_001"
        audio_config = {
            "enhancement_level": 0.8,
            "directional_audio": True,
            "frequency_adjustment": {
                "low": 1.2,
                "mid": 1.0,
                "high": 1.5
            },
            "spatial_mapping": True
        }
        
        result = await vr_service.configure_spatial_audio(
            user_id, session_id, audio_config
        )
        
        assert result["success"] is True
        assert "audio_profile" in result
    
    @pytest.mark.asyncio
    async def test_setup_haptic_feedback(self, vr_service):
        """测试触觉反馈设置"""
        user_id = "test_user_001"
        session_id = "session_001"
        haptic_config = {
            "intensity": 0.7,
            "patterns": ["notification", "warning", "success"],
            "frequency_range": [20, 1000],
            "adaptive": True
        }
        
        result = await vr_service.setup_haptic_feedback(
            user_id, session_id, haptic_config
        )
        
        assert result["success"] is True
        assert "haptic_profile" in result
    
    @pytest.mark.asyncio
    async def test_enable_voice_control(self, vr_service):
        """测试语音控制启用"""
        user_id = "test_user_001"
        session_id = "session_001"
        voice_config = {
            "language": "zh-CN",
            "sensitivity": 0.8,
            "wake_word": "小艾",
            "commands": ["导航", "选择", "返回", "帮助"]
        }
        
        result = await vr_service.enable_voice_control(
            user_id, session_id, voice_config
        )
        
        assert result["success"] is True
        assert "voice_profile" in result
    
    @pytest.mark.asyncio
    async def test_setup_eye_tracking(self, vr_service):
        """测试眼动追踪设置"""
        user_id = "test_user_001"
        session_id = "session_001"
        eye_tracking_config = {
            "calibration_points": 9,
            "tracking_frequency": 120,
            "gaze_interaction": True,
            "dwell_time": 800
        }
        
        result = await vr_service.setup_eye_tracking(
            user_id, session_id, eye_tracking_config
        )
        
        assert result["success"] is True
        assert "eye_tracking_profile" in result
    
    @pytest.mark.asyncio
    async def test_enable_subtitle_overlay(self, vr_service):
        """测试字幕叠加启用"""
        user_id = "test_user_001"
        session_id = "session_001"
        subtitle_config = {
            "font_size": 24,
            "background_opacity": 0.8,
            "position": "bottom_center",
            "language": "zh-CN",
            "real_time": True
        }
        
        result = await vr_service.enable_subtitle_overlay(
            user_id, session_id, subtitle_config
        )
        
        assert result["success"] is True
        assert "subtitle_profile" in result
    
    @pytest.mark.asyncio
    async def test_monitor_user_comfort(self, vr_service):
        """测试用户舒适度监控"""
        user_id = "test_user_001"
        session_id = "session_001"
        
        result = await vr_service.monitor_user_comfort(user_id, session_id)
        
        assert result["success"] is True
        assert "comfort_metrics" in result
        assert "recommendations" in result
    
    @pytest.mark.asyncio
    async def test_handle_emergency_situation(self, vr_service):
        """测试紧急情况处理"""
        user_id = "test_user_001"
        session_id = "session_001"
        emergency_type = "motion_sickness"
        context = {
            "severity": "moderate",
            "duration": 120,
            "symptoms": ["nausea", "dizziness"]
        }
        
        result = await vr_service.handle_emergency_situation(
            user_id, session_id, emergency_type, context
        )
        
        assert result["success"] is True
        assert "emergency_response" in result
        assert "immediate_actions" in result


class TestMemoryAssistanceService:
    """记忆辅助服务测试"""
    
    @pytest.fixture
    async def memory_service(self):
        """创建记忆辅助服务实例"""
        model_manager = Mock()
        cache_manager = AsyncMock()
        
        service = MemoryAssistanceServiceImpl(
            model_manager=model_manager,
            cache_manager=cache_manager,
            enabled=True
        )
        
        await service.initialize()
        return service
    
    @pytest.mark.asyncio
    async def test_create_memory_aid(self, memory_service):
        """测试创建记忆辅助"""
        user_id = "test_user_001"
        memory_config = {
            "type": MemoryType.SHORT_TERM.value,
            "content": "今天下午3点有医生预约",
            "importance": "high",
            "context": {
                "location": "医院",
                "people": ["张医生"],
                "category": "医疗"
            }
        }
        
        result = await memory_service.create_memory_aid(user_id, memory_config)
        
        assert result["success"] is True
        assert "memory_id" in result
        assert result["user_id"] == user_id
    
    @pytest.mark.asyncio
    async def test_create_reminder(self, memory_service):
        """测试创建提醒"""
        user_id = "test_user_001"
        reminder_config = {
            "type": ReminderType.MEDICATION.value,
            "title": "服用降压药",
            "description": "每天早上8点服用降压药一片",
            "schedule": {
                "frequency": "daily",
                "time": "08:00",
                "days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            },
            "notification_methods": ["audio", "visual", "haptic"]
        }
        
        result = await memory_service.create_reminder(user_id, reminder_config)
        
        assert result["success"] is True
        assert "reminder_id" in result
        assert result["user_id"] == user_id
    
    @pytest.mark.asyncio
    async def test_cognitive_training_session(self, memory_service):
        """测试认知训练会话"""
        user_id = "test_user_001"
        training_config = {
            "type": "memory_enhancement",
            "difficulty": "medium",
            "duration": 15,
            "focus_areas": ["working_memory", "attention", "processing_speed"]
        }
        
        result = await memory_service.start_cognitive_training_session(
            user_id, training_config
        )
        
        assert result["success"] is True
        assert "session_id" in result
        assert "exercises" in result
    
    @pytest.mark.asyncio
    async def test_memory_assessment(self, memory_service):
        """测试记忆评估"""
        user_id = "test_user_001"
        assessment_config = {
            "type": "comprehensive",
            "areas": ["short_term", "long_term", "working", "episodic"],
            "duration": 20
        }
        
        result = await memory_service.conduct_memory_assessment(
            user_id, assessment_config
        )
        
        assert result["success"] is True
        assert "assessment_id" in result
        assert "baseline_scores" in result
    
    @pytest.mark.asyncio
    async def test_memory_retrieval_assistance(self, memory_service):
        """测试记忆检索辅助"""
        user_id = "test_user_001"
        query = "昨天的医生预约"
        context = {
            "time_range": "yesterday",
            "category": "medical",
            "importance": "high"
        }
        
        result = await memory_service.assist_memory_retrieval(
            user_id, query, context
        )
        
        assert result["success"] is True
        assert "retrieved_memories" in result
        assert "confidence_scores" in result
    
    @pytest.mark.asyncio
    async def test_create_memory_palace(self, memory_service):
        """测试创建记忆宫殿"""
        user_id = "test_user_001"
        palace_config = {
            "name": "我的家",
            "description": "以家为背景的记忆宫殿",
            "rooms": [
                {"name": "客厅", "capacity": 10},
                {"name": "卧室", "capacity": 8},
                {"name": "厨房", "capacity": 6}
            ],
            "theme": "familiar_environment"
        }
        
        result = await memory_service.create_memory_palace(
            user_id, palace_config
        )
        
        assert result["success"] is True
        assert "palace_id" in result
        assert "visualization_data" in result
    
    @pytest.mark.asyncio
    async def test_emergency_contact_assistance(self, memory_service):
        """测试紧急联系人辅助"""
        user_id = "test_user_001"
        emergency_type = "medical"
        
        result = await memory_service.provide_emergency_contact_assistance(
            user_id, emergency_type
        )
        
        assert result["success"] is True
        assert "emergency_contacts" in result
        assert "instructions" in result
    
    @pytest.mark.asyncio
    async def test_medication_management(self, memory_service):
        """测试药物管理"""
        user_id = "test_user_001"
        medication_data = {
            "name": "阿司匹林",
            "dosage": "100mg",
            "frequency": "daily",
            "time": "09:00",
            "duration": "30 days",
            "side_effects": ["胃部不适", "头晕"]
        }
        
        result = await memory_service.add_medication_reminder(
            user_id, medication_data
        )
        
        assert result["success"] is True
        assert "medication_id" in result
        assert "reminder_schedule" in result


class TestAudioVisualizationService:
    """音频可视化服务测试"""
    
    @pytest.fixture
    async def audio_viz_service(self):
        """创建音频可视化服务实例"""
        model_manager = Mock()
        cache_manager = AsyncMock()
        
        service = AudioVisualizationServiceImpl(
            model_manager=model_manager,
            cache_manager=cache_manager,
            enabled=True
        )
        
        await service.initialize()
        return service
    
    @pytest.mark.asyncio
    async def test_create_visualization_stream(self, audio_viz_service):
        """测试创建可视化流"""
        user_id = "test_user_001"
        audio_source = {
            "type": "microphone",
            "device_id": "default",
            "sample_rate": 44100,
            "channels": 2
        }
        visualization_config = {
            "type": VisualizationType.SPECTRUM.value,
            "color_scheme": ColorScheme.RAINBOW.value,
            "width": 800,
            "height": 600,
            "fps": 30,
            "sensitivity": 0.8
        }
        
        result = await audio_viz_service.create_visualization_stream(
            user_id, audio_source, visualization_config
        )
        
        assert result["success"] is True
        assert "stream_id" in result
        assert result["user_id"] == user_id
    
    @pytest.mark.asyncio
    async def test_get_visualization_frame(self, audio_viz_service):
        """测试获取可视化帧"""
        user_id = "test_user_001"
        stream_id = "vis_stream_test_001"
        
        # 模拟活跃流
        audio_viz_service._active_streams[stream_id] = {
            "stream_id": stream_id,
            "user_id": user_id,
            "status": "active",
            "frame_count": 100,
            "last_frame_time": datetime.now(timezone.utc).isoformat()
        }
        
        # 模拟缓存帧数据
        frame_data = b"fake_frame_data"
        audio_viz_service.cache_manager.get.return_value = frame_data
        
        result = await audio_viz_service.get_visualization_frame(
            user_id, stream_id
        )
        
        assert result["success"] is True
        assert "frame_data" in result
        assert result["stream_id"] == stream_id
    
    @pytest.mark.asyncio
    async def test_audio_feature_extraction(self, audio_viz_service):
        """测试音频特征提取"""
        # 创建模拟音频数据
        audio_data = np.random.randn(1024).astype(np.float32)
        features = [
            audio_viz_service.AudioFeature.AMPLITUDE,
            audio_viz_service.AudioFeature.FREQUENCY,
            audio_viz_service.AudioFeature.PITCH
        ]
        
        result = await audio_viz_service._extract_audio_features(
            audio_data, features
        )
        
        assert isinstance(result, dict)
        assert "amplitude" in result
        assert "frequency" in result
        assert "pitch" in result
    
    @pytest.mark.asyncio
    async def test_visualization_presets(self, audio_viz_service):
        """测试可视化预设"""
        # 测试音乐预设
        music_config = {"preset": "music"}
        parsed_config = await audio_viz_service._parse_visualization_config(music_config)
        
        assert parsed_config["type"] == VisualizationType.SPECTRUM
        assert parsed_config["color_scheme"] == ColorScheme.RAINBOW
        assert parsed_config["sensitivity"] == 0.8
        
        # 测试语音预设
        speech_config = {"preset": "speech"}
        parsed_config = await audio_viz_service._parse_visualization_config(speech_config)
        
        assert parsed_config["type"] == VisualizationType.WAVEFORM
        assert parsed_config["color_scheme"] == ColorScheme.BLUE_GRADIENT
        assert parsed_config["sensitivity"] == 0.6
    
    @pytest.mark.asyncio
    async def test_color_mapping(self, audio_viz_service):
        """测试颜色映射"""
        # 测试彩虹色映射
        rainbow_colors = audio_viz_service._create_rainbow_colormap()
        assert rainbow_colors.shape == (256, 3)
        assert rainbow_colors.dtype == np.uint8
        
        # 测试火焰色映射
        fire_colors = audio_viz_service._create_fire_colormap()
        assert fire_colors.shape == (256, 3)
        assert fire_colors.dtype == np.uint8
        
        # 测试高对比度映射
        contrast_colors = audio_viz_service._create_high_contrast_colormap()
        assert contrast_colors.shape == (256, 3)
        assert contrast_colors.dtype == np.uint8
    
    @pytest.mark.asyncio
    async def test_spectrum_visualizer(self, audio_viz_service):
        """测试频谱可视化器"""
        from ..internal.service.implementations.audio_visualization_impl import SpectrumVisualizer
        
        visualizer = SpectrumVisualizer()
        config = {
            "width": 800,
            "height": 600,
            "sensitivity": 0.8,
            "color_scheme": ColorScheme.RAINBOW
        }
        
        await visualizer.initialize(config)
        
        # 模拟音频特征
        features = {
            "frequency": np.random.rand(400) * 100
        }
        
        frame = await visualizer.generate_frame(features, config)
        
        assert frame.shape == (600, 800, 3)
        assert frame.dtype == np.uint8
    
    @pytest.mark.asyncio
    async def test_waveform_visualizer(self, audio_viz_service):
        """测试波形可视化器"""
        from ..internal.service.implementations.audio_visualization_impl import WaveformVisualizer
        
        visualizer = WaveformVisualizer()
        config = {
            "width": 800,
            "height": 600,
            "sensitivity": 0.8,
            "color_scheme": ColorScheme.BLUE_GRADIENT
        }
        
        await visualizer.initialize(config)
        
        # 模拟音频特征
        features = {
            "amplitude": np.sin(np.linspace(0, 4*np.pi, 800)) * 0.5
        }
        
        frame = await visualizer.generate_frame(features, config)
        
        assert frame.shape == (600, 800, 3)
        assert frame.dtype == np.uint8


class TestIntegratedAccessibilityServices:
    """集成无障碍服务测试"""
    
    @pytest.fixture
    async def integrated_services(self):
        """创建集成服务实例"""
        model_manager = Mock()
        cache_manager = AsyncMock()
        
        vr_service = VRAccessibilityServiceImpl(
            model_manager=model_manager,
            cache_manager=cache_manager,
            enabled=True
        )
        
        memory_service = MemoryAssistanceServiceImpl(
            model_manager=model_manager,
            cache_manager=cache_manager,
            enabled=True
        )
        
        audio_viz_service = AudioVisualizationServiceImpl(
            model_manager=model_manager,
            cache_manager=cache_manager,
            enabled=True
        )
        
        await vr_service.initialize()
        await memory_service.initialize()
        await audio_viz_service.initialize()
        
        return {
            "vr": vr_service,
            "memory": memory_service,
            "audio_viz": audio_viz_service
        }
    
    @pytest.mark.asyncio
    async def test_service_status_integration(self, integrated_services):
        """测试服务状态集成"""
        vr_status = await integrated_services["vr"].get_service_status()
        memory_status = await integrated_services["memory"].get_service_status()
        audio_viz_status = await integrated_services["audio_viz"].get_service_status()
        
        assert vr_status["service_name"] == "VRAccessibilityService"
        assert vr_status["enabled"] is True
        assert vr_status["initialized"] is True
        
        assert memory_status["service_name"] == "MemoryAssistanceService"
        assert memory_status["enabled"] is True
        assert memory_status["initialized"] is True
        
        assert audio_viz_status["service_name"] == "AudioVisualizationService"
        assert audio_viz_status["enabled"] is True
        assert audio_viz_status["initialized"] is True
    
    @pytest.mark.asyncio
    async def test_cross_service_scenario(self, integrated_services):
        """测试跨服务场景"""
        user_id = "test_user_001"
        
        # 1. 创建VR会话
        vr_result = await integrated_services["vr"].create_accessibility_session(
            user_id,
            VRPlatform.OCULUS_QUEST,
            {"visual_impairment": "moderate"}
        )
        assert vr_result["success"] is True
        session_id = vr_result["session_id"]
        
        # 2. 创建记忆辅助
        memory_result = await integrated_services["memory"].create_memory_aid(
            user_id,
            {
                "type": "short_term",
                "content": f"VR会话 {session_id} 已开始",
                "context": {"session_id": session_id}
            }
        )
        assert memory_result["success"] is True
        
        # 3. 创建音频可视化流
        audio_result = await integrated_services["audio_viz"].create_visualization_stream(
            user_id,
            {"type": "vr_audio", "session_id": session_id},
            {"preset": "ambient"}
        )
        assert audio_result["success"] is True
    
    @pytest.mark.asyncio
    async def test_performance_monitoring(self, integrated_services):
        """测试性能监控"""
        # 并发测试
        tasks = []
        
        for i in range(10):
            user_id = f"test_user_{i:03d}"
            
            # VR会话创建任务
            vr_task = integrated_services["vr"].create_accessibility_session(
                user_id,
                VRPlatform.GENERIC_VR,
                {"preferences": {"test": True}}
            )
            tasks.append(vr_task)
            
            # 记忆辅助创建任务
            memory_task = integrated_services["memory"].create_memory_aid(
                user_id,
                {"type": "short_term", "content": f"测试记忆 {i}"}
            )
            tasks.append(memory_task)
            
            # 音频可视化流创建任务
            audio_task = integrated_services["audio_viz"].create_visualization_stream(
                user_id,
                {"type": "test"},
                {"preset": "music"}
            )
            tasks.append(audio_task)
        
        # 执行并发任务
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # 验证结果
        successful_results = [r for r in results if isinstance(r, dict) and r.get("success")]
        assert len(successful_results) >= 20  # 至少2/3的任务成功
        
        # 验证性能
        total_time = end_time - start_time
        assert total_time < 10.0  # 10秒内完成所有任务
        
        avg_response_time = total_time / len(tasks)
        assert avg_response_time < 0.5  # 平均响应时间小于500ms
    
    @pytest.mark.asyncio
    async def test_error_handling_integration(self, integrated_services):
        """测试错误处理集成"""
        user_id = "test_user_error"
        
        # 测试无效参数处理
        vr_result = await integrated_services["vr"].create_accessibility_session(
            user_id,
            "invalid_platform",  # 无效平台
            {}
        )
        # 应该优雅处理错误
        assert "error" in vr_result or vr_result["success"] is False
        
        # 测试空数据处理
        memory_result = await integrated_services["memory"].create_memory_aid(
            user_id,
            {}  # 空配置
        )
        # 应该优雅处理错误
        assert "error" in memory_result or memory_result["success"] is False
        
        # 测试无效流ID
        audio_result = await integrated_services["audio_viz"].get_visualization_frame(
            user_id,
            "non_existent_stream"
        )
        assert audio_result["success"] is False
    
    @pytest.mark.asyncio
    async def test_cleanup_integration(self, integrated_services):
        """测试清理集成"""
        # 执行清理
        await integrated_services["vr"].cleanup()
        await integrated_services["memory"].cleanup()
        await integrated_services["audio_viz"].cleanup()
        
        # 验证清理后状态
        vr_status = await integrated_services["vr"].get_service_status()
        memory_status = await integrated_services["memory"].get_service_status()
        audio_viz_status = await integrated_services["audio_viz"].get_service_status()
        
        assert vr_status["initialized"] is False
        assert memory_status["initialized"] is False
        assert audio_viz_status["initialized"] is False


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])