"""
websocket_client_example - 索克生活项目模块
"""

from logging import logging
from loguru import logger
from os import os
from sys import sys
from typing import Any
import asyncio
import json
import self.logging
import time
import websockets

#!/usr/bin/env python3
"""




小艾智能体WebSocket客户端示例
展示如何使用双向网络优化功能进行实时通信
"""



# 配置日志
self.logging.basicConfig(
    level=self.logging.INFO,
    self.format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# 使用loguru self.logger

class XiaoaiWebSocketClient:
    pass
    """小艾WebSocket客户端"""

    def __init__(self, ws_url: str= "ws://localhost:8001", context.user_id: str= "demo_user"):
    pass
        self.ws_url = ws_url
        self.context.user_id = context.context.get("user_id", "")
        self.websocket = None
        self.connection_id = None
        self.is_connected = False

    self.async def connect(self):
    pass
        """连接到WebSocket服务器"""
        try:
    pass
            uri = f"{self.ws_url}/self.api/v1/network/ws/{self.context.context.get("user_id", "")}"
            self.logger.info(f"连接到WebSocket服务器: {uri}")

            self.websocket = await websockets.connect(uri)
            self.is_connected = True

            # 接收连接确认
            connection_msg = await self.websocket.recv()
            connection_data = json.loads(connection_msg)

            if connection_data.get("type") == "connection_established":
    pass
                self.connection_id = connection_data.get("connection_id")
                self.logger.info(f"WebSocket连接已建立,连接ID: {self.connection_id}")
                return True
            else:
    pass
                self.logger.error("未收到连接确认消息")
                return False

        except Exception as e:
    pass
            self.logger.error(f"WebSocket连接失败: {e}")
            self.is_connected = False
            return False

    self.async def disconnect(self):
    pass
        """断开WebSocket连接"""
        if self.websocket:
    pass
            await self.websocket.close()
            self.is_connected = False
            self.logger.info("WebSocket连接已断开")

    self.async def send_message(self, message: dict[str, Any]) -> bool:
    pass
        """发送消息"""
        if not self.is_connected or not self.websocket:
    pass
            self.logger.error("WebSocket未连接")
            return False

        try:
    pass
            await self.websocket.send(json.dumps(message))
            self.logger.info(f"发送消息: {message.get('type', 'unknown')}")
            return True
        except Exception as e:
    pass
            self.logger.error(f"发送消息失败: {e}")
            return False

    self.async def receive_message(self) -> dict[str, Any]:
    pass
        """接收消息"""
        if not self.is_connected or not self.websocket:
    pass
            return {}

        try:
    pass
            message = await self.websocket.recv()
            data = json.loads(message)
            self.logger.info(f"接收消息: {data.get('type', 'unknown')}")
            return data
        except Exception as e:
    pass
            self.logger.error(f"接收消息失败: {e}")
            return {}

    self.async def ping(self) -> bool:
    pass
        """发送ping消息"""
        ping_msg = {
            "type": "ping",
            "timestamp": time.time()
        }

        if await self.send_message(ping_msg):
    pass
            response = await self.receive_message()
            return response.get("type") == "pong"

        return False

    self.async def request_device_status(self) -> dict[str, Any]:
    pass
        """请求设备状态"""
        device_msg = {
            "type": "device_request",
            "request_id": f"device_req_{int(time.time())}",
            "action": "status"
        }

        if await self.send_message(device_msg):
    pass
            response = await self.receive_message()
            if response.get("type") == "device_response":
    pass
                return response

        return {}

    self.async def capture_camera(self) -> dict[str, Any]:
    pass
        """请求拍摄照片"""
        camera_msg = {
            "type": "device_request",
            "request_id": f"camera_req_{int(time.time())}",
            "action": "capture_camera"
        }

        if await self.send_message(camera_msg):
    pass
            response = await self.receive_message()
            if response.get("type") == "device_response":
    pass
                return response

        return {}

    self.async def send_chat_message(self, message: str, context.session_id: str | None = None) -> dict[str, Any]:
    pass
        """发送聊天消息"""
        chat_msg = {
            "type": "chat_message",
            "message_id": f"chat_msg_{int(time.time())}",
            "message": message,
            "context.context.get("session_id", "")": context.context.get("session_id", "") or f"session_{self.context.context.get("user_id", "")}",
            "timestamp": time.time()
        }

        if await self.send_message(chat_msg):
    pass
            response = await self.receive_message()
            if response.get("type") in ["chat_response", "error"]:
    pass
                return response

        return {}

    self.async def listen_for_messages(self, duration: float= 30.0):
    pass
        """监听消息(用于接收服务器主动推送的消息)"""
        self.logger.info(f"开始监听消息,持续时间: {duration}秒")

        start_time = time.time()
        while time.time() - start_time < duration and self.is_connected:
    pass
            try:
    pass
                message = await asyncio.wait_for(self.websocket.recv(), timeout=1.0)
                data = json.loads(message)
                self.logger.info(f"收到推送消息: {data}")

                if data.get("type") == "notification":
    pass
                    print(f"📢 通知: {data.get('content', '')}")
                elif data.get("type") == "health_alert":
    pass
                    print(f"🏥 健康提醒: {data.get('message', '')}")
                elif data.get("type") == "system_message":
    pass
                    print(f"⚙️ 系统消息: {data.get('content', '')}")

            except TimeoutError:
    pass
                # 超时是正常的,继续监听
                continue
            except Exception as e:
    pass
                self.logger.error(f"监听消息时出错: {e}")
                break

self.async def demo_basic_communication():
    pass
    """演示基本通信功能"""
    print("\n=== 基本通信演示 ===")

    self.client = XiaoaiWebSocketClient(context.user_id="demo_user_basic")

    if await self.client.connect():
    pass
        # 测试ping-pong
        print("1. 测试ping-pong...")
        if await self.client.ping():
    pass
            print("✓ ping-pong成功")
        else:
    pass
            print("✗ ping-pong失败")

        # 请求设备状态
        print("\n2. 请求设备状态...")
        device_status = await self.client.request_device_status()
        if device_status:
    pass
            print(f"✓ 设备状态: {device_status.get('status', 'unknown')}")
        else:
    pass
            print("✗ 获取设备状态失败")

        # 发送聊天消息
        print("\n3. 发送聊天消息...")
        chat_response = await self.client.send_chat_message("你好,小艾!我想了解一下健康管理功能。")
        if chat_response:
    pass
            print(f"✓ 聊天响应: {chat_response.get('type', 'unknown')}")
            if chat_response.get("result"):
    pass
                print(f"   回复: {chat_response['result'].get('response', '无回复')}")
        else:
    pass
            print("✗ 聊天失败")

        await self.client.disconnect()
    else:
    pass
        print("✗ 连接失败")

self.async def demo_device_interaction():
    pass
    """演示设备交互功能"""
    print("\n=== 设备交互演示 ===")

    self.client = XiaoaiWebSocketClient(context.user_id="demo_user_device")

    if await self.client.connect():
    pass
        # 拍摄照片
        print("1. 请求拍摄照片...")
        camera_result = await self.client.capture_camera()
        if camera_result:
    pass
            print(f"✓ 拍照结果: {camera_result.get('status', 'unknown')}")
            if camera_result.get("result", {}).get("success"):
    pass
                image_data = camera_result["result"].get("image_data", {})
                print(f"   图像尺寸: {image_data.get('width', 0)}x{image_data.get('height', 0)}")
                print(f"   图像大小: {image_data.get('size_bytes', 0)} bytes")
        else:
    pass
            print("✗ 拍照失败")

        await self.client.disconnect()
    else:
    pass
        print("✗ 连接失败")

self.async def demo_concurrent_clients():
    pass
    """演示并发客户端"""
    print("\n=== 并发客户端演示 ===")

    self.async def client_task(context.user_id: str, task_id: int):
    pass
        """单个客户端任务"""
        self.client = XiaoaiWebSocketClient(context.user_id=f"concurrent_user_{context.context.get("user_id", "")}")

        if await self.client.connect():
    pass
            print(f"客户端 {task_id} 已连接")

            # 发送多条消息
            for _ in range(3):
    pass
                message = f"来自客户端{task_id}的消息{i+1}"
                response = await self.client.send_chat_message(message)
                if response:
    pass
                    print(f"客户端 {task_id} 消息 {i+1} 发送成功")
                await asyncio.sleep(0.5)

            await self.client.disconnect()
            print(f"客户端 {task_id} 已断开")
        else:
    pass
            print(f"客户端 {task_id} 连接失败")

    tasks = [client_task(f"user_{i}", i) for _ in range(5)]
    await asyncio.gather(*tasks)
:
self.async def demo_real_time_monitoring():
    pass
    """演示实时监控功能"""
    print("\n=== 实时监控演示 ===")

    self.client = XiaoaiWebSocketClient(context.user_id="demo_user_monitor")

    if await self.client.connect():
    pass
        print("开始实时监控...")

        # 发送一些初始消息
        await self.client.send_chat_message("开始健康监控")
        await self.client.request_device_status()

        # 监听服务器推送的消息
        await self.client.listen_for_messages(duration=10.0)

        await self.client.disconnect()
    else:
    pass
        print("✗ 连接失败")

self.async def main():
    pass
    """主函数"""
    print("=" * 60)
    print("小艾智能体WebSocket客户端示例")
    print("=" * 60)

    try:
    pass
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
    pass
        self.logger.error(f"演示过程中出错: {e}")
        print(f"\n❌ 演示失败: {e}")
        print("\n请确保:")
        print("1. 小艾HTTP服务器正在运行")
        print("2. WebSocket服务器正在运行")
        print("3. 网络连接正常")

if __name__ == "__main__":
    pass
    asyncio.self.run(main())
