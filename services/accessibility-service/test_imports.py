#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试相对导入问题
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_relative_imports():
    """测试相对导入"""
    try:
        # 测试核心模块导入
        from internal.service.implementations.blind_assistance_impl import BlindAssistanceServiceImpl
        from internal.service.implementations.voice_assistance_impl import VoiceAssistanceServiceImpl
        from internal.service.coordinators.accessibility_coordinator import AccessibilityServiceCoordinator
        from internal.service.factories.accessibility_factory import AccessibilityServiceFactory
        
        print('✅ 核心服务导入成功')
        
        # 测试接口导入
        from internal.service.interfaces import (
            IBlindAssistanceService, IVoiceAssistanceService, 
            IScreenReadingService, ISignLanguageService
        )
        
        print('✅ 接口导入成功')
        
        # 测试装饰器导入
        from internal.service.decorators import performance_monitor, error_handler, cache_result
        
        print('✅ 装饰器导入成功')
        
        return True
        
    except ImportError as e:
        print(f'❌ 相对导入失败: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = test_relative_imports()
    exit(0 if result else 1) 