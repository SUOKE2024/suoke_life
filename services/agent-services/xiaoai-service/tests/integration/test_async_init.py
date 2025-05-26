#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异步测试脚本
"""

import sys
import os
import asyncio

# 添加项目根目录到PYTHONPATH
sys.path.insert(0, os.path.abspath('.'))

async def test_xiaoai_service_impl_async():
    """异步测试 XiaoAIServiceImpl 初始化"""
    print("🔍 异步测试 XiaoAIServiceImpl 初始化...\n")
    
    try:
        from internal.delivery.xiaoai_service_impl import XiaoAIServiceImpl
        
        print("正在创建 XiaoAIServiceImpl 实例...")
        service_impl = XiaoAIServiceImpl()
        print(f"✓ XiaoAIServiceImpl 创建成功: {type(service_impl)}")
        
        # 测试异步初始化
        print("正在进行异步初始化...")
        if hasattr(service_impl, 'agent_manager') and hasattr(service_impl.agent_manager, 'initialize'):
            await service_impl.agent_manager.initialize()
            print("✓ AgentManager 异步初始化成功")
        
        return True
        
    except Exception as e:
        print(f"❌ XiaoAIServiceImpl 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_server_startup():
    """测试服务器启动过程"""
    print("\n🔍 测试服务器启动过程...\n")
    
    try:
        from cmd.server import XiaoAIServer
        
        print("正在创建 XiaoAIServer 实例...")
        server = XiaoAIServer("config/dev.yaml")
        print(f"✓ XiaoAIServer 创建成功: {type(server)}")
        
        # 测试服务器配置
        print(f"✓ 服务器地址: {server.host}:{server.port}")
        print(f"✓ 最大工作线程: {server.max_workers}")
        
        return True
        
    except Exception as e:
        print(f"❌ 服务器启动测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("🚀 开始异步测试\n")
    
    # 测试服务器启动
    server_ok = await test_server_startup()
    
    # 测试服务实现
    service_ok = await test_xiaoai_service_impl_async()
    
    print(f"\n📊 测试结果:")
    print(f"  服务器启动: {'✓' if server_ok else '❌'}")
    print(f"  服务实现: {'✓' if service_ok else '❌'}")
    
    if server_ok and service_ok:
        print("\n🎉 所有异步测试通过！")
        return True
    else:
        print("\n⚠️ 存在问题需要修复")
        return False

if __name__ == '__main__':
    asyncio.run(main()) 