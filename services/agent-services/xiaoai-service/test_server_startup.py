#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试服务器启动脚本
"""

import sys
import os
import asyncio

# 添加项目根目录到PYTHONPATH
sys.path.insert(0, os.path.abspath('.'))

async def test_server_startup():
    """测试服务器启动"""
    print("🔍 测试服务器启动...\n")
    
    try:
        from cmd.server import XiaoAIServer
        
        # 创建服务器实例
        server = XiaoAIServer("config/dev.yaml")
        print(f"✓ 服务器实例创建成功")
        print(f"✓ 监听地址: {server.host}:{server.port}")
        print(f"✓ 工作线程数: {server.max_workers}")
        
        # 测试组件初始化
        print("\n🔧 测试服务器组件初始化...")
        
        # 创建gRPC服务器
        import grpc
        from concurrent import futures
        import api.grpc.xiaoai_service_pb2_grpc as xiaoai_pb2_grpc
        
        test_server = grpc.aio.server(
            futures.ThreadPoolExecutor(max_workers=server.max_workers)
        )
        print("✓ gRPC服务器创建成功")
        
        # 创建服务实现
        from internal.delivery.xiaoai_service_impl import XiaoAIServiceImpl
        service_impl = XiaoAIServiceImpl()
        print("✓ 服务实现创建成功")
        
        # 注册服务
        xiaoai_pb2_grpc.add_XiaoAIServiceServicer_to_server(service_impl, test_server)
        print("✓ 服务注册成功")
        
        # 测试端口绑定
        server_address = f"{server.host}:{server.port}"
        test_server.add_insecure_port(server_address)
        print(f"✓ 端口绑定成功: {server_address}")
        
        # 启动服务器（短暂启动后关闭）
        print("\n🚀 启动服务器进行测试...")
        await test_server.start()
        print("✓ 服务器启动成功")
        
        # 等待一秒钟
        await asyncio.sleep(1)
        
        # 关闭服务器
        test_server.stop(grace=None)
        print("✓ 服务器关闭成功")
        
        print("\n🎉 服务器启动测试成功！")
        return True
        
    except Exception as e:
        print(f"\n❌ 服务器启动测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("=" * 60)
    print("小艾服务启动测试")
    print("=" * 60)
    
    # 运行服务器启动测试
    startup_ok = await test_server_startup()
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"服务器启动测试: {'✓ 通过' if startup_ok else '❌ 失败'}")
    
    if startup_ok:
        print("\n🎉 测试通过！小艾服务可以正常启动！")
        print("\n📝 启动服务命令:")
        print("   python3 cmd/server.py --config config/dev.yaml")
        return True
    else:
        print("\n⚠️ 存在问题需要修复")
        return False

if __name__ == '__main__':
    asyncio.run(main()) 