#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
集成测试
测试服务之间的协调工作和完整业务流程
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

# 导入服务组件
from internal.service.coordinators import AccessibilityServiceCoordinator
from internal.service.factories import AccessibilityServiceFactory
from internal.service.implementations import (
    BlindAssistanceServiceImpl,
    VoiceAssistanceServiceImpl,
    SignLanguageServiceImpl,
    ScreenReadingServiceImpl,
    ContentConversionServiceImpl
)


class TestServiceIntegration:
    """服务集成测试类"""
    
    @pytest.fixture
    async def mock_dependencies(self):
        """模拟依赖组件"""
        mock_model_manager = Mock()
        mock_model_manager.load_model = AsyncMock(return_value=Mock())
        mock_model_manager.unload_model = AsyncMock()
        
        mock_cache_manager = Mock()
        mock_cache_manager.get = AsyncMock(return_value=None)
        mock_cache_manager.set = AsyncMock()
        mock_cache_manager.delete = AsyncMock()
        
        return {
            'model_manager': mock_model_manager,
            'cache_manager': mock_cache_manager
        }
    
    @pytest.fixture
    async def service_factory(self, mock_dependencies):
        """创建服务工厂"""
        factory = AccessibilityServiceFactory()
        
        # 注入模拟依赖
        factory._model_manager = mock_dependencies['model_manager']
        factory._cache_manager = mock_dependencies['cache_manager']
        
        await factory.initialize()
        return factory
    
    @pytest.fixture
    async def coordinator(self, service_factory):
        """创建服务协调器"""
        coordinator = AccessibilityServiceCoordinator(service_factory)
        await coordinator.initialize()
        return coordinator
    
    @pytest.mark.asyncio
    async def test_coordinator_initialization(self, coordinator):
        """测试协调器初始化"""
        assert coordinator is not None
        assert coordinator._initialized is True
        
        # 检查所有服务是否正确初始化
        status = await coordinator.get_status()
        assert status['coordinator_status'] == 'healthy'
        assert 'services' in status
        
        # 验证服务状态
        services = status['services']
        expected_services = [
            'blind_assistance', 'voice_assistance', 'sign_language',
            'screen_reading', 'content_conversion'
        ]
        
        for service_name in expected_services:
            assert service_name in services
            assert services[service_name]['enabled'] is True
    
    @pytest.mark.asyncio
    async def test_cross_service_coordination(self, coordinator):
        """测试跨服务协调"""
        # 测试综合辅助场景：场景分析 + 语音输出
        request_data = {
            'type': 'scene_analysis_with_voice',
            'image_data': b'fake_image_data',
            'preferences': {
                'voice_enabled': True,
                'language': 'zh-CN',
                'detail_level': 'detailed'
            }
        }
        
        result = await coordinator.comprehensive_assistance(request_data, 'test_user')
        
        assert result is not None
        assert 'scene_analysis' in result
        assert 'voice_output' in result
        assert result['user_id'] == 'test_user'
        assert result['coordination_success'] is True
    
    @pytest.mark.asyncio
    async def test_service_chain_execution(self, coordinator):
        """测试服务链执行"""
        # 测试：屏幕阅读 -> 内容转换 -> 语音输出
        request_data = {
            'type': 'screen_reading_chain',
            'screen_data': b'fake_screen_data',
            'conversion_options': {
                'simplify': True,
                'target_language': 'zh-CN'
            },
            'voice_options': {
                'speed': 'normal',
                'pitch': 'medium'
            }
        }
        
        result = await coordinator.comprehensive_assistance(request_data, 'test_user')
        
        assert result is not None
        assert 'screen_content' in result
        assert 'converted_content' in result
        assert 'voice_output' in result
        
        # 验证数据流传递
        assert result['screen_content']['ui_elements'] is not None
        assert result['converted_content']['simplified_text'] is not None
    
    @pytest.mark.asyncio
    async def test_parallel_service_execution(self, coordinator):
        """测试并行服务执行"""
        # 同时执行多个独立服务
        tasks = []
        
        # 场景分析任务
        scene_task = coordinator.analyze_scene(
            b'fake_image_data', 'user1', {}, {'lat': 39.9, 'lng': 116.4}
        )
        tasks.append(scene_task)
        
        # 手语识别任务
        sign_task = coordinator._sign_language_service.recognize_sign_language(
            b'fake_video_data', 'CSL', 'user2'
        )
        tasks.append(sign_task)
        
        # 内容转换任务
        conversion_task = coordinator._content_conversion_service.simplify_text(
            '这是一个复杂的文本内容，需要进行简化处理。', 'easy'
        )
        tasks.append(conversion_task)
        
        # 并行执行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 验证所有任务都成功完成
        assert len(results) == 3
        for result in results:
            assert not isinstance(result, Exception)
    
    @pytest.mark.asyncio
    async def test_error_handling_and_fallback(self, coordinator):
        """测试错误处理和降级"""
        # 模拟服务故障
        with patch.object(coordinator._blind_assistance_service, 'analyze_scene', 
                         side_effect=Exception("Service temporarily unavailable")):
            
            request_data = {
                'type': 'scene_analysis_with_fallback',
                'image_data': b'fake_image_data',
                'preferences': {'enable_fallback': True}
            }
            
            result = await coordinator.comprehensive_assistance(request_data, 'test_user')
            
            # 验证降级处理
            assert result is not None
            assert result['fallback_used'] is True
            assert 'error_message' in result
            assert result['partial_success'] is True
    
    @pytest.mark.asyncio
    async def test_service_health_monitoring(self, coordinator):
        """测试服务健康监控"""
        # 获取所有服务的健康状态
        health_status = await coordinator.get_health_status()
        
        assert health_status is not None
        assert 'overall_health' in health_status
        assert 'service_health' in health_status
        
        # 验证各服务健康状态
        service_health = health_status['service_health']
        for service_name, health in service_health.items():
            assert 'status' in health
            assert 'response_time' in health
            assert 'error_rate' in health
            assert health['status'] in ['healthy', 'degraded', 'unhealthy']
    
    @pytest.mark.asyncio
    async def test_configuration_hot_reload(self, coordinator):
        """测试配置热重载"""
        # 获取当前配置
        original_config = await coordinator.get_configuration()
        
        # 更新配置
        new_config = {
            'services': {
                'blind_assistance': {
                    'enabled': True,
                    'max_concurrent_requests': 20  # 修改并发数
                }
            }
        }
        
        # 应用新配置
        reload_result = await coordinator.reload_configuration(new_config)
        
        assert reload_result['success'] is True
        assert reload_result['changes_applied'] > 0
        
        # 验证配置已更新
        updated_config = await coordinator.get_configuration()
        assert updated_config['services']['blind_assistance']['max_concurrent_requests'] == 20


class TestServiceDataFlow:
    """服务数据流测试类"""
    
    @pytest.fixture
    async def initialized_services(self):
        """初始化所有服务"""
        mock_model_manager = Mock()
        mock_model_manager.load_model = AsyncMock(return_value=Mock())
        mock_model_manager.unload_model = AsyncMock()
        
        mock_cache_manager = Mock()
        mock_cache_manager.get = AsyncMock(return_value=None)
        mock_cache_manager.set = AsyncMock()
        mock_cache_manager.delete = AsyncMock()
        
        services = {
            'blind_assistance': BlindAssistanceServiceImpl(
                mock_model_manager, mock_cache_manager, enabled=True
            ),
            'voice_assistance': VoiceAssistanceServiceImpl(
                mock_model_manager, mock_cache_manager, enabled=True
            ),
            'sign_language': SignLanguageServiceImpl(
                mock_model_manager, mock_cache_manager, enabled=True
            ),
            'screen_reading': ScreenReadingServiceImpl(
                mock_model_manager, mock_cache_manager, enabled=True
            ),
            'content_conversion': ContentConversionServiceImpl(
                mock_model_manager, mock_cache_manager, enabled=True
            )
        }
        
        # 初始化所有服务
        for service in services.values():
            await service.initialize()
        
        return services
    
    @pytest.mark.asyncio
    async def test_data_transformation_pipeline(self, initialized_services):
        """测试数据转换管道"""
        # 1. 屏幕阅读获取原始内容
        screen_data = b'fake_screen_data'
        screen_result = await initialized_services['screen_reading'].read_screen(
            screen_data, 'test_user', 'web_page', {'reading_mode': 'detailed'}
        )
        
        assert 'text_content' in screen_result
        original_text = screen_result['text_content']['full_text']
        
        # 2. 内容转换简化文本
        simplified_text = await initialized_services['content_conversion'].simplify_text(
            original_text, 'easy'
        )
        
        assert simplified_text is not None
        assert len(simplified_text) > 0
        
        # 3. 语音输出转换
        voice_result = await initialized_services['voice_assistance'].text_to_speech(
            simplified_text, 'zh-CN', {'speed': 'normal'}
        )
        
        assert voice_result is not None
        assert 'audio_data' in voice_result
        assert voice_result['text'] == simplified_text
    
    @pytest.mark.asyncio
    async def test_multimodal_input_processing(self, initialized_services):
        """测试多模态输入处理"""
        # 同时处理图像、语音和手语输入
        
        # 图像场景分析
        image_task = initialized_services['blind_assistance'].analyze_scene(
            b'fake_image_data', 'test_user', {}, {'lat': 39.9, 'lng': 116.4}
        )
        
        # 语音命令处理
        voice_task = initialized_services['voice_assistance'].process_voice_command(
            b'fake_audio_data', 'zh-CN', 'test_user', {}
        )
        
        # 手语识别
        sign_task = initialized_services['sign_language'].recognize_sign_language(
            b'fake_video_data', 'CSL', 'test_user'
        )
        
        # 并行处理
        results = await asyncio.gather(image_task, voice_task, sign_task)
        
        # 验证所有模态都有结果
        image_result, voice_result, sign_result = results
        
        assert image_result['confidence'] > 0
        assert voice_result['intent'] is not None
        assert sign_result['semantic'] is not None
        
        # 验证结果可以融合
        combined_confidence = (
            image_result['confidence'] + 
            voice_result['confidence'] + 
            sign_result['confidence']
        ) / 3
        
        assert combined_confidence > 0.5
    
    @pytest.mark.asyncio
    async def test_context_preservation(self, initialized_services):
        """测试上下文保持"""
        user_id = 'test_user'
        
        # 第一次交互：场景分析
        scene_result = await initialized_services['blind_assistance'].analyze_scene(
            b'fake_image_data', user_id, {}, {'lat': 39.9, 'lng': 116.4}
        )
        
        # 第二次交互：基于场景的语音查询
        voice_context = {
            'previous_scene': scene_result['scene_type'],
            'location': scene_result['location']
        }
        
        voice_result = await initialized_services['voice_assistance'].process_voice_command(
            b'fake_audio_data', 'zh-CN', user_id, voice_context
        )
        
        # 验证上下文被正确使用
        assert voice_result['context_used'] is True
        assert voice_result['previous_scene'] == scene_result['scene_type']


class TestServiceResilience:
    """服务弹性测试类"""
    
    @pytest.mark.asyncio
    async def test_service_isolation(self):
        """测试服务隔离"""
        mock_model_manager = Mock()
        mock_model_manager.load_model = AsyncMock(return_value=Mock())
        mock_model_manager.unload_model = AsyncMock()
        
        mock_cache_manager = Mock()
        mock_cache_manager.get = AsyncMock(return_value=None)
        mock_cache_manager.set = AsyncMock()
        mock_cache_manager.delete = AsyncMock()
        
        # 创建服务实例
        blind_service = BlindAssistanceServiceImpl(
            mock_model_manager, mock_cache_manager, enabled=True
        )
        voice_service = VoiceAssistanceServiceImpl(
            mock_model_manager, mock_cache_manager, enabled=True
        )
        
        await blind_service.initialize()
        await voice_service.initialize()
        
        # 模拟一个服务故障
        with patch.object(blind_service, 'analyze_scene', 
                         side_effect=Exception("Service error")):
            
            # 验证故障服务不影响其他服务
            with pytest.raises(Exception):
                await blind_service.analyze_scene(
                    b'fake_data', 'user', {}, {}
                )
            
            # 其他服务仍然正常工作
            voice_result = await voice_service.process_voice_command(
                b'fake_audio', 'zh-CN', 'user', {}
            )
            
            assert voice_result is not None
    
    @pytest.mark.asyncio
    async def test_graceful_degradation(self):
        """测试优雅降级"""
        mock_model_manager = Mock()
        mock_cache_manager = Mock()
        
        # 模拟模型加载失败
        mock_model_manager.load_model = AsyncMock(
            side_effect=Exception("Model loading failed")
        )
        mock_model_manager.unload_model = AsyncMock()
        
        mock_cache_manager.get = AsyncMock(return_value=None)
        mock_cache_manager.set = AsyncMock()
        mock_cache_manager.delete = AsyncMock()
        
        service = BlindAssistanceServiceImpl(
            mock_model_manager, mock_cache_manager, enabled=True
        )
        
        # 初始化应该失败，但服务应该能够处理
        with pytest.raises(Exception):
            await service.initialize()
        
        # 服务状态应该反映故障
        status = await service.get_status()
        assert status['initialized'] is False
        assert status['error_count'] > 0


if __name__ == "__main__":
    # 运行集成测试
    pytest.main([__file__, "-v"]) 