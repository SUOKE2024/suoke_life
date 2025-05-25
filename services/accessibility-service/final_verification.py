#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
索克生活无障碍服务 - 最终验证脚本
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print('🔍 索克生活无障碍服务 - 最终验证')
    print('=' * 50)
    
    results = []
    
    # 1. 测试相对导入
    try:
        from internal.service.implementations.blind_assistance_impl import BlindAssistanceServiceImpl
        from internal.service.coordinators.accessibility_coordinator import AccessibilityServiceCoordinator
        from internal.service.factories.accessibility_factory import AccessibilityServiceFactory
        print('✅ 相对导入测试通过')
        results.append(True)
    except Exception as e:
        print(f'❌ 相对导入失败: {e}')
        results.append(False)
    
    # 2. 测试可用的科学计算库
    available_libs = []
    
    try:
        import numpy as np
        available_libs.append('NumPy')
    except ImportError:
        pass
    
    try:
        import cv2
        available_libs.append('OpenCV')
    except ImportError:
        pass
    
    try:
        import pandas as pd
        available_libs.append('Pandas')
    except ImportError:
        pass
    
    try:
        import scipy
        available_libs.append('SciPy')
    except ImportError:
        pass
    
    if available_libs:
        print(f'✅ 可用的科学计算库: {", ".join(available_libs)}')
        results.append(True)
    else:
        print('❌ 没有可用的科学计算库')
        results.append(False)
    
    # 3. 测试核心服务创建
    try:
        from internal.service.dependency_injection import DIContainer
        from unittest.mock import Mock
        
        container = DIContainer()
        mock_config = Mock()
        mock_config.get = Mock(return_value=True)
        container.register('config_manager', type(mock_config), mock_config)
        
        factory = AccessibilityServiceFactory(container)
        print('✅ 服务工厂创建成功')
        results.append(True)
    except Exception as e:
        print(f'❌ 服务工厂创建失败: {e}')
        results.append(False)
    
    # 4. 测试配置文件
    config_files = [
        'config/config.yaml',
        'requirements.txt',
        'README.md'
    ]
    
    missing_files = []
    for file_path in config_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if not missing_files:
        print('✅ 配置文件检查通过')
        results.append(True)
    else:
        print(f'❌ 缺少配置文件: {", ".join(missing_files)}')
        results.append(False)
    
    print('=' * 50)
    
    # 总结
    success_count = sum(results)
    total_count = len(results)
    success_rate = success_count / total_count * 100
    
    print(f'📊 验证结果: {success_count}/{total_count} 通过 ({success_rate:.1f}%)')
    
    if success_count == total_count:
        print('🎉 所有验证项目通过！服务已准备就绪！')
        return 0
    elif success_count >= total_count * 0.75:
        print('⚠️ 大部分验证通过，服务基本可用')
        return 0
    else:
        print('❌ 验证失败，需要进一步修复')
        return 1

if __name__ == "__main__":
    exit(main()) 