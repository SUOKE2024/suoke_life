#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速核心服务测试
"""

import asyncio
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_core_services():
    try:
        # 测试核心服务导入
        from internal.service.dependency_injection import DIContainer
        from internal.service.factories import AccessibilityServiceFactory
        from internal.service.coordinators import AccessibilityServiceCoordinator
        
        print('✅ 核心模块导入成功')
        
        # 创建容器和工厂
        container = DIContainer()
        factory = AccessibilityServiceFactory(container)
        coordinator = AccessibilityServiceCoordinator(factory)
        
        print('✅ 服务组件创建成功')
        
        # 测试初始化
        await factory.initialize()
        await coordinator.initialize()
        
        print('✅ 服务初始化成功')
        
        # 获取状态
        status = await coordinator.get_status()
        print(f'✅ 协调器状态: 初始化={status["coordinator"]["initialized"]}')
        print(f'✅ 请求计数: {status["coordinator"]["request_count"]}')
        print(f'✅ 错误计数: {status["coordinator"]["error_count"]}')
        
        # 测试服务工厂状态
        factory_status = await factory.get_service_status()
        print(f'✅ 服务工厂状态: {len(factory_status)} 个服务配置')
        
        return True
        
    except Exception as e:
        print(f'❌ 核心服务测试失败: {str(e)}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_core_services())
    exit(0 if result else 1) 