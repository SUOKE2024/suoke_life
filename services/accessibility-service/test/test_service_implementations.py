#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
服务实现基础测试
验证所有服务实现是否能正确导入和初始化
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

# 导入服务实现
from internal.service.implementations import (
    BlindAssistanceServiceImpl,
    VoiceAssistanceServiceImpl,
    SignLanguageServiceImpl,
    ScreenReadingServiceImpl,
    ContentConversionServiceImpl
)


class TestServiceImplementations:
    """服务实现基础测试类"""
    
    @pytest.fixture
    def mock_model_manager(self):
        """模拟模型管理器"""
        mock = Mock()
        mock.load_model = AsyncMock(return_value=Mock())
        mock.unload_model = AsyncMock()
        return mock
    
    @pytest.fixture
    def mock_cache_manager(self):
        """模拟缓存管理器"""
        mock = Mock()
        mock.get = AsyncMock(return_value=None)
        mock.set = AsyncMock()
        mock.delete = AsyncMock()
        return mock
    
    @pytest.mark.asyncio
    async def test_blind_assistance_service_init(self, mock_model_manager, mock_cache_manager):
        """测试导盲服务初始化"""
        service = BlindAssistanceServiceImpl(
            model_manager=mock_model_manager,
            cache_manager=mock_cache_manager,
            enabled=True
        )
        
        assert service is not None
        assert service.enabled is True
        assert service._initialized is False
        
        # 测试初始化
        await service.initialize()
        assert service._initialized is True
        
        # 测试状态获取
        status = await service.get_status()
        assert status['service_name'] == 'BlindAssistanceService'
        assert status['enabled'] is True
        assert status['initialized'] is True
        
        # 清理
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_voice_assistance_service_init(self, mock_model_manager, mock_cache_manager):
        """测试语音辅助服务初始化"""
        service = VoiceAssistanceServiceImpl(
            model_manager=mock_model_manager,
            cache_manager=mock_cache_manager,
            enabled=True
        )
        
        assert service is not None
        assert service.enabled is True
        assert service._initialized is False
        
        # 测试初始化
        await service.initialize()
        assert service._initialized is True
        
        # 测试状态获取
        status = await service.get_status()
        assert status['service_name'] == 'VoiceAssistanceService'
        assert status['enabled'] is True
        assert status['initialized'] is True
        
        # 清理
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_sign_language_service_init(self, mock_model_manager, mock_cache_manager):
        """测试手语识别服务初始化"""
        service = SignLanguageServiceImpl(
            model_manager=mock_model_manager,
            cache_manager=mock_cache_manager,
            enabled=True
        )
        
        assert service is not None
        assert service.enabled is True
        assert service._initialized is False
        
        # 测试初始化
        await service.initialize()
        assert service._initialized is True
        
        # 测试状态获取
        status = await service.get_status()
        assert status['service_name'] == 'SignLanguageService'
        assert status['enabled'] is True
        assert status['initialized'] is True
        
        # 测试支持的语言
        languages = await service.get_supported_languages()
        assert 'ASL' in languages
        assert 'CSL' in languages
        
        # 清理
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_screen_reading_service_init(self, mock_model_manager, mock_cache_manager):
        """测试屏幕阅读服务初始化"""
        service = ScreenReadingServiceImpl(
            model_manager=mock_model_manager,
            cache_manager=mock_cache_manager,
            enabled=True
        )
        
        assert service is not None
        assert service.enabled is True
        assert service._initialized is False
        
        # 测试初始化
        await service.initialize()
        assert service._initialized is True
        
        # 测试状态获取
        status = await service.get_status()
        assert status['service_name'] == 'ScreenReadingService'
        assert status['enabled'] is True
        assert status['initialized'] is True
        
        # 清理
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_content_conversion_service_init(self, mock_model_manager, mock_cache_manager):
        """测试内容转换服务初始化"""
        service = ContentConversionServiceImpl(
            model_manager=mock_model_manager,
            cache_manager=mock_cache_manager,
            enabled=True
        )
        
        assert service is not None
        assert service.enabled is True
        assert service._initialized is False
        
        # 测试初始化
        await service.initialize()
        assert service._initialized is True
        
        # 测试状态获取
        status = await service.get_status()
        assert status['service_name'] == 'ContentConversionService'
        assert status['enabled'] is True
        assert status['initialized'] is True
        
        # 测试支持的转换类型
        conversions = await service.get_supported_conversions()
        assert 'text_simplification' in conversions
        assert 'text_summarization' in conversions
        assert 'language_translation' in conversions
        
        # 测试支持的语言
        languages = await service.get_supported_languages()
        assert 'zh-CN' in languages
        assert 'en-US' in languages
        
        # 清理
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_all_services_disabled(self, mock_model_manager, mock_cache_manager):
        """测试所有服务禁用状态"""
        services = [
            BlindAssistanceServiceImpl(mock_model_manager, mock_cache_manager, enabled=False),
            VoiceAssistanceServiceImpl(mock_model_manager, mock_cache_manager, enabled=False),
            SignLanguageServiceImpl(mock_model_manager, mock_cache_manager, enabled=False),
            ScreenReadingServiceImpl(mock_model_manager, mock_cache_manager, enabled=False),
            ContentConversionServiceImpl(mock_model_manager, mock_cache_manager, enabled=False)
        ]
        
        for service in services:
            assert service.enabled is False
            
            # 禁用的服务初始化应该直接返回
            await service.initialize()
            assert service._initialized is False
            
            # 状态应该显示禁用
            status = await service.get_status()
            assert status['enabled'] is False
            assert status['initialized'] is False
    
    def test_service_imports(self):
        """测试服务导入"""
        # 验证所有服务类都能正确导入
        assert BlindAssistanceServiceImpl is not None
        assert VoiceAssistanceServiceImpl is not None
        assert SignLanguageServiceImpl is not None
        assert ScreenReadingServiceImpl is not None
        assert ContentConversionServiceImpl is not None
        
        # 验证类名正确
        assert BlindAssistanceServiceImpl.__name__ == 'BlindAssistanceServiceImpl'
        assert VoiceAssistanceServiceImpl.__name__ == 'VoiceAssistanceServiceImpl'
        assert SignLanguageServiceImpl.__name__ == 'SignLanguageServiceImpl'
        assert ScreenReadingServiceImpl.__name__ == 'ScreenReadingServiceImpl'
        assert ContentConversionServiceImpl.__name__ == 'ContentConversionServiceImpl'


class TestServiceFunctionality:
    """服务功能测试类"""
    
    @pytest.fixture
    def mock_model_manager(self):
        """模拟模型管理器"""
        mock = Mock()
        mock.load_model = AsyncMock(return_value=Mock())
        mock.unload_model = AsyncMock()
        return mock
    
    @pytest.fixture
    def mock_cache_manager(self):
        """模拟缓存管理器"""
        mock = Mock()
        mock.get = AsyncMock(return_value=None)
        mock.set = AsyncMock()
        mock.delete = AsyncMock()
        return mock
    
    @pytest.mark.asyncio
    async def test_sign_language_recognition(self, mock_model_manager, mock_cache_manager):
        """测试手语识别功能"""
        service = SignLanguageServiceImpl(
            model_manager=mock_model_manager,
            cache_manager=mock_cache_manager,
            enabled=True
        )
        
        await service.initialize()
        
        # 测试手语识别
        video_data = b"fake_video_data"
        result = await service.recognize_sign_language(
            video_data=video_data,
            language="CSL",
            user_id="test_user"
        )
        
        assert result is not None
        assert result['user_id'] == "test_user"
        assert result['language'] == "CSL"
        assert 'gestures' in result
        assert 'recognition' in result
        assert 'semantic' in result
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_content_conversion_text_simplification(self, mock_model_manager, mock_cache_manager):
        """测试文本简化功能"""
        service = ContentConversionServiceImpl(
            model_manager=mock_model_manager,
            cache_manager=mock_cache_manager,
            enabled=True
        )
        
        await service.initialize()
        
        # 测试文本简化
        text = "通过优化配置来提升系统性能"
        simplified = await service.simplify_text(text, "easy")
        
        assert simplified is not None
        assert isinstance(simplified, str)
        # 验证简化规则是否应用
        assert "用" in simplified or "做" in simplified
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_screen_reading_ui_extraction(self, mock_model_manager, mock_cache_manager):
        """测试UI元素提取功能"""
        service = ScreenReadingServiceImpl(
            model_manager=mock_model_manager,
            cache_manager=mock_cache_manager,
            enabled=True
        )
        
        await service.initialize()
        
        # 测试UI元素提取
        screen_data = b"fake_screen_data"
        ui_elements = await service.extract_ui_elements(screen_data)
        
        assert ui_elements is not None
        assert isinstance(ui_elements, list)
        assert len(ui_elements) > 0
        
        # 验证UI元素结构
        for element in ui_elements:
            assert 'id' in element
            assert 'type' in element
            assert 'text' in element
            assert 'bbox' in element
            assert 'confidence' in element
        
        await service.cleanup()


if __name__ == "__main__":
    # 运行基础导入测试
    test_instance = TestServiceImplementations()
    test_instance.test_service_imports()
    print("✅ 所有服务实现导入测试通过")
    
    # 运行异步测试需要事件循环
    async def run_async_tests():
        mock_model_manager = Mock()
        mock_model_manager.load_model = AsyncMock(return_value=Mock())
        mock_model_manager.unload_model = AsyncMock()
        
        mock_cache_manager = Mock()
        mock_cache_manager.get = AsyncMock(return_value=None)
        mock_cache_manager.set = AsyncMock()
        mock_cache_manager.delete = AsyncMock()
        
        # 测试所有服务初始化
        services = [
            BlindAssistanceServiceImpl(mock_model_manager, mock_cache_manager, enabled=True),
            VoiceAssistanceServiceImpl(mock_model_manager, mock_cache_manager, enabled=True),
            SignLanguageServiceImpl(mock_model_manager, mock_cache_manager, enabled=True),
            ScreenReadingServiceImpl(mock_model_manager, mock_cache_manager, enabled=True),
            ContentConversionServiceImpl(mock_model_manager, mock_cache_manager, enabled=True)
        ]
        
        for service in services:
            await service.initialize()
            status = await service.get_status()
            print(f"✅ {status['service_name']} 初始化成功")
            await service.cleanup()
    
    # 运行异步测试
    asyncio.run(run_async_tests())
    print("✅ 所有服务实现功能测试通过") 