#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试小艾对话功能
"""

import sys
import os
import asyncio
import traceback

# 添加项目路径
sys.path.append('.')

# 设置环境变量
os.environ['DEEPSEEK_API_KEY'] = 'sk-26ac526b8c3b41c2a39bd80a156aaa68'

async def quick_chat_test():
    """快速对话测试"""
    print("🚀 快速测试小艾对话功能")
    print("="*40)
    
    try:
        from internal.agent.agent_manager import AgentManager
        
        # 初始化小艾
        print("🤖 正在初始化小艾...")
        agent_manager = AgentManager()
        await agent_manager.initialize()
        
        factory_type = type(agent_manager.model_factory).__name__
        print(f"✅ 小艾初始化成功！使用模型: {factory_type}")
        
        # 测试对话
        test_messages = [
            "你好，小艾！",
            "我最近总是感到疲劳，从中医角度应该如何调理？",
            "请简单介绍一下中医的阴阳理论"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n📝 测试 {i}: {message}")
            print("🤔 小艾正在思考...")
            
            response = await agent_manager.chat(
                user_id="test_user",
                message=message,
                session_id="quick_test"
            )
            
            print(f"🤖 小艾: {response['message']}")
            
            # 显示元数据
            metadata = response.get('metadata', {})
            if metadata:
                model = metadata.get('model', '未知')
                provider = metadata.get('provider', '未知')
                print(f"   📊 模型: {model} | 提供商: {provider} | 置信度: {response['confidence']:.2f}")
        
        print("\n✅ 小艾对话功能测试完成！")
        print("\n💡 现在您可以运行 'python3 chat_with_xiaoai.py' 开始与小艾对话")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(quick_chat_test()) 