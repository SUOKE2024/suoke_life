#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小艾智能体WebSocket客户端示例
展示如何使用双向网络优化功能进行实时通信
"""

import asyncio
import json
import time
import logging
import websockets
from typing import Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class XiaoaiWebSocketClient:
    """小艾WebSocket客户端"""
    
    def __init__(self, ws_url: str = "ws://localhost:8001", user_id: str = "demo_user"):
        self.ws_url = ws_url
        self.user_id = user_id
        self.websocket = None
        self.connection_id = None
        self.is_connected = False
        
    async def connect(self):
        """连接到WebSocket服务器"""
        try:
            uri = f"{self.ws_url}/api/v1/network/ws/{self.user_id}"
            logger.info(f"连接到WebSocket服务器: {uri}")
            
            self.websocket = await websockets.connect(uri)
            self.is_connected = True
            
            # 接收连接确认
            connection_msg = await self.websocket.recv()
            connection_data = json.loads(connection_msg)
            
            if connection_data.get("type") == "connection_established":
                self.connection_id = connection_data.get("connection_id")
                logger.info(f"WebSocket连接已建立，连接ID: {self.connection_id}")
                return True
            else:
                logger.error("未收到连接确认消息")
                return False
                
        except Exception as e:
            logger.error(f"WebSocket连接失败: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """断开WebSocket连接"""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
            logger.info("WebSocket连接已断开")
    
    async def send_message(self, message: Dict[str, Any]) -> bool:
        """发送消息"""
        if not self.is_connected or not self.websocket:
            logger.error("WebSocket未连接")
            return False
        
        try:
            await self.websocket.send(json.dumps(message))
            logger.info(f"发送消息: {message.get('type', 'unknown')}")
            return True
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            return False
    
    async def receive_message(self) -> Dict[str, Any]:
        """接收消息"""
        if not self.is_connected or not self.websocket:
            return {}
        
        try:
            message = await self.websocket.recv()
            data = json.loads(message)
            logger.info(f"接收消息: {data.get('type', 'unknown')}")
            return data
        except Exception as e:
            logger.error(f"接收消息失败: {e}")
            return {}
    
    async def ping(self) -> bool:
        """发送ping消息"""
        ping_msg = {
            "type": "ping",
            "timestamp": time.time()
        }
        
        if await self.send_message(ping_msg):
            response = await self.receive_message()
            return response.get("type") == "pong"
        
        return False
    
    async def request_device_status(self) -> Dict[str, Any]:
        """请求设备状态"""
        device_msg = {
            "type": "device_request",
            "request_id": f"device_req_{int(time.time())}",
            "action": "status"
        }
        
        if await self.send_message(device_msg):
            response = await self.receive_message()
            if response.get("type") == "device_response":
                return response
        
        return {}
    
    async def capture_camera(self) -> Dict[str, Any]:
        """请求拍摄照片"""
        camera_msg = {
            "type": "device_request",
            "request_id": f"camera_req_{int(time.time())}",
            "action": "capture_camera"
        }
        
        if await self.send_message(camera_msg):
            response = await self.receive_message()
            if response.get("type") == "device_response":
                return response
        
        return {}
    
    async def send_chat_message(self, message: str, session_id: str = None) -> Dict[str, Any]:
        """发送聊天消息"""
        chat_msg = {
            "type": "chat_message",
            "message_id": f"chat_msg_{int(time.time())}",
            "message": message,
            "session_id": session_id or f"session_{self.user_id}",
            "timestamp": time.time()
        }
        
        if await self.send_message(chat_msg):
            response = await self.receive_message()
            if response.get("type") in ["chat_response", "error"]:
                return response
        
        return {}
    
    async def listen_for_messages(self, duration: float = 30.0):
        """监听消息（用于接收服务器主动推送的消息）"""
        logger.info(f"开始监听消息，持续时间: {duration}秒")
        
        start_time = time.time()
        while time.time() - start_time < duration and self.is_connected:
            try:
                # 设置超时以避免无限等待
                message = await asyncio.wait_for(self.websocket.recv(), timeout=1.0)
                data = json.loads(message)
                logger.info(f"收到推送消息: {data}")
                
                # 处理不同类型的推送消息
                if data.get("type") == "notification":
                    print(f"📢 通知: {data.get('content', '')}")
                elif data.get("type") == "health_alert":
                    print(f"🏥 健康提醒: {data.get('message', '')}")
                elif data.get("type") == "system_message":
                    print(f"⚙️ 系统消息: {data.get('content', '')}")
                
            except asyncio.TimeoutError:
                # 超时是正常的，继续监听
                continue
            except Exception as e:
                logger.error(f"监听消息时出错: {e}")
                break

async def demo_basic_communication():
    """演示基本通信功能"""
    print("\n=== 基本通信演示 ===")
    
    client = XiaoaiWebSocketClient(user_id="demo_user_basic")
    
    if await client.connect():
        # 测试ping-pong
        print("1. 测试ping-pong...")
        if await client.ping():
            print("✓ ping-pong成功")
        else:
            print("✗ ping-pong失败")
        
        # 请求设备状态
        print("\n2. 请求设备状态...")
        device_status = await client.request_device_status()
        if device_status:
            print(f"✓ 设备状态: {device_status.get('status', 'unknown')}")
        else:
            print("✗ 获取设备状态失败")
        
        # 发送聊天消息
        print("\n3. 发送聊天消息...")
        chat_response = await client.send_chat_message("你好，小艾！我想了解一下健康管理功能。")
        if chat_response:
            print(f"✓ 聊天响应: {chat_response.get('type', 'unknown')}")
            if chat_response.get("result"):
                print(f"   回复: {chat_response['result'].get('response', '无回复')}")
        else:
            print("✗ 聊天失败")
        
        await client.disconnect()
    else:
        print("✗ 连接失败")

async def demo_device_interaction():
    """演示设备交互功能"""
    print("\n=== 设备交互演示 ===")
    
    client = XiaoaiWebSocketClient(user_id="demo_user_device")
    
    if await client.connect():
        # 拍摄照片
        print("1. 请求拍摄照片...")
        camera_result = await client.capture_camera()
        if camera_result:
            print(f"✓ 拍照结果: {camera_result.get('status', 'unknown')}")
            if camera_result.get("result", {}).get("success"):
                image_data = camera_result["result"].get("image_data", {})
                print(f"   图像尺寸: {image_data.get('width', 0)}x{image_data.get('height', 0)}")
                print(f"   图像大小: {image_data.get('size_bytes', 0)} bytes")
        else:
            print("✗ 拍照失败")
        
        await client.disconnect()
    else:
        print("✗ 连接失败")

async def demo_concurrent_clients():
    """演示并发客户端"""
    print("\n=== 并发客户端演示 ===")
    
    async def client_task(user_id: str, task_id: int):
        """单个客户端任务"""
        client = XiaoaiWebSocketClient(user_id=f"concurrent_user_{user_id}")
        
        if await client.connect():
            print(f"客户端 {task_id} 已连接")
            
            # 发送多条消息
            for i in range(3):
                message = f"来自客户端{task_id}的消息{i+1}"
                response = await client.send_chat_message(message)
                if response:
                    print(f"客户端 {task_id} 消息 {i+1} 发送成功")
                await asyncio.sleep(0.5)
            
            await client.disconnect()
            print(f"客户端 {task_id} 已断开")
        else:
            print(f"客户端 {task_id} 连接失败")
    
    # 创建5个并发客户端
    tasks = [client_task(f"user_{i}", i) for i in range(5)]
    await asyncio.gather(*tasks)

async def demo_real_time_monitoring():
    """演示实时监控功能"""
    print("\n=== 实时监控演示 ===")
    
    client = XiaoaiWebSocketClient(user_id="demo_user_monitor")
    
    if await client.connect():
        print("开始实时监控...")
        
        # 发送一些初始消息
        await client.send_chat_message("开始健康监控")
        await client.request_device_status()
        
        # 监听服务器推送的消息
        await client.listen_for_messages(duration=10.0)
        
        await client.disconnect()
    else:
        print("✗ 连接失败")

async def main():
    """主函数"""
    print("=" * 60)
    print("小艾智能体WebSocket客户端示例")
    print("=" * 60)
    
    try:
        # 运行各种演示
        await demo_basic_communication()
        await asyncio.sleep(1)
        
        await demo_device_interaction()
        await asyncio.sleep(1)
        
        await demo_concurrent_clients()
        await asyncio.sleep(1)
        
        await demo_real_time_monitoring()
        
        print("\n✅ 所有演示完成!")
        
    except Exception as e:
        logger.error(f"演示过程中出错: {e}")
        print(f"\n❌ 演示失败: {e}")
        print("\n请确保:")
        print("1. 小艾HTTP服务器正在运行")
        print("2. WebSocket服务器正在运行")
        print("3. 网络连接正常")

if __name__ == "__main__":
    asyncio.run(main()) 