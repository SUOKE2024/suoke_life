#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小艾服务客户端测试脚本
"""

import sys
import os
import asyncio
import grpc

# 添加项目根目录到PYTHONPATH
sys.path.insert(0, os.path.abspath('.'))

# 导入gRPC生成的代码
import api.grpc.xiaoai_service_pb2 as xiaoai_pb2
import api.grpc.xiaoai_service_pb2_grpc as xiaoai_pb2_grpc

async def test_chat_service():
    """测试聊天服务"""
    print("🔍 测试小艾聊天服务...\n")
    
    try:
        # 创建gRPC通道
        channel = grpc.aio.insecure_channel('localhost:50053')
        
        # 创建客户端存根
        stub = xiaoai_pb2_grpc.XiaoAIServiceStub(channel)
        
        # 创建聊天请求
        request = xiaoai_pb2.ChatRequest(
            user_id="test_user_001",
            message="你好，我想咨询健康问题",
            session_id="test_session_001"
        )
        
        print(f"📤 发送消息: {request.message}")
        
        # 发送请求（使用流式接口）
        async for response in stub.ChatStream(request, timeout=30):
            break  # 只获取第一个响应
        
        print(f"📥 收到回复: {response.message}")
        print(f"🎯 置信度: {response.confidence}")
        print(f"🆔 消息ID: {response.message_id}")
        print(f"⏰ 时间戳: {response.timestamp}")
        
        # 关闭通道
        await channel.close()
        
        print("\n✅ 聊天服务测试成功！")
        return True
        
    except Exception as e:
        print(f"\n❌ 聊天服务测试失败: {e}")
        return False

async def test_health_check():
    """测试健康检查服务"""
    print("🔍 测试健康检查服务...\n")
    
    try:
        # 创建gRPC通道
        channel = grpc.aio.insecure_channel('localhost:50053')
        
        # 创建客户端存根
        stub = xiaoai_pb2_grpc.XiaoAIServiceStub(channel)
        
        # 创建健康检查请求
        request = xiaoai_pb2.HealthCheckRequest()
        
        print("📤 发送健康检查请求")
        
        # 发送请求
        response = await stub.HealthCheck(request, timeout=10)
        
        print(f"📥 服务状态: {response.status}")
        
        # 显示详细信息
        if response.details:
            print("📊 服务详细信息:")
            for key, value in response.details.items():
                print(f"  - {key}: {value}")
        
        # 关闭通道
        await channel.close()
        
        print("\n✅ 健康检查测试成功！")
        return True
        
    except Exception as e:
        print(f"\n❌ 健康检查测试失败: {e}")
        return False

async def test_multimodal_input():
    """测试多模态输入服务"""
    print("🔍 测试多模态输入服务...\n")
    
    try:
        # 创建gRPC通道
        channel = grpc.aio.insecure_channel('localhost:50053')
        
        # 创建客户端存根
        stub = xiaoai_pb2_grpc.XiaoAIServiceStub(channel)
        
        # 创建多模态输入请求
        text_input = xiaoai_pb2.TextInput(
            text="我感觉有点不舒服，请帮我分析一下",
            language="zh-CN"
        )
        request = xiaoai_pb2.MultimodalRequest(
            user_id="test_user_001",
            session_id="test_session_001",
            text=text_input
        )
        
        print(f"📤 发送多模态输入: {request.text.text}")
        
        # 发送请求
        response = await stub.ProcessMultimodalInput(request, timeout=30)
        
        print(f"🎯 置信度: {response.confidence}")
        print(f"🆔 请求ID: {response.request_id}")
        
        # 检查具体的处理结果
        if response.HasField('text_result'):
            print(f"📥 文本处理结果: {response.text_result.processed_text}")
        elif response.HasField('voice_result'):
            print(f"📥 语音识别结果: {response.voice_result.transcription}")
        elif response.HasField('image_result'):
            print(f"📥 图像分析结果: {response.image_result.image_type}")
        elif response.HasField('sign_result'):
            print(f"📥 手语识别结果: {response.sign_result.transcription}")
        else:
            print(f"📥 处理完成，无具体结果")
        
        # 关闭通道
        await channel.close()
        
        print("\n✅ 多模态输入测试成功！")
        return True
        
    except Exception as e:
        print(f"\n❌ 多模态输入测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("=" * 60)
    print("小艾服务客户端测试")
    print("=" * 60)
    
    # 测试健康检查
    health_ok = await test_health_check()
    
    # 测试聊天服务
    chat_ok = await test_chat_service()
    
    # 测试多模态输入
    multimodal_ok = await test_multimodal_input()
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"健康检查: {'✅ 通过' if health_ok else '❌ 失败'}")
    print(f"聊天服务: {'✅ 通过' if chat_ok else '❌ 失败'}")
    print(f"多模态输入: {'✅ 通过' if multimodal_ok else '❌ 失败'}")
    
    if health_ok and chat_ok and multimodal_ok:
        print("\n🎉 所有客户端测试通过！小艾服务运行正常！")
        return True
    else:
        print("\n⚠️ 部分测试失败，请检查服务状态")
        return False

if __name__ == '__main__':
    asyncio.run(main()) 