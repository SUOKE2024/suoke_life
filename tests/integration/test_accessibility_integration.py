#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小艾智能体与无障碍服务集成测试
"""

import asyncio
import sys
import os
sys.path.append('.')

from internal.integration.accessibility_client import AccessibilityServiceClient, AccessibilityConfig

async def test_integration():
    """测试小艾智能体与无障碍服务的集成"""
    print("🔍 开始测试小艾智能体与无障碍服务集成...")
    
    config = AccessibilityConfig(service_url='http://localhost:50051')
    client = AccessibilityServiceClient(config)
    
    try:
        # 初始化客户端
        print("📡 初始化无障碍服务客户端...")
        await client.initialize()
        
        # 健康检查
        print("🏥 执行健康检查...")
        health = await client.health_check()
        print(f"   健康检查结果: {health}")
        
        if health:
            print("✅ 无障碍服务连接成功！")
            
            # 测试语音输入处理（模拟）
            print("🎤 测试语音输入处理...")
            voice_result = await client.process_voice_input(
                audio_data=b'test_audio_data',
                user_id='test_user',
                context='health_consultation'
            )
            print(f"   语音处理结果: {voice_result}")
            
            # 测试图像输入处理（模拟）
            print("📷 测试图像输入处理...")
            image_result = await client.process_image_input(
                image_data=b'test_image_data',
                user_id='test_user',
                image_type='tongue',
                context='visual_diagnosis'
            )
            print(f"   图像处理结果: {image_result}")
            
            # 测试内容转换
            print("🔄 测试内容转换...")
            conversion_result = await client.convert_content(
                content="这是一个健康建议测试",
                user_id='test_user',
                content_type='health_advice',
                target_format='audio'
            )
            print(f"   内容转换结果: {conversion_result}")
            
            print("🎉 所有集成测试完成！")
            
        else:
            print("❌ 无障碍服务连接失败")
            
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()
        print("🔚 测试完成，客户端已关闭")

if __name__ == "__main__":
    asyncio.run(test_integration()) 