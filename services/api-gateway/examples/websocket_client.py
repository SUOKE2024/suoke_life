"""
websocket_client - 索克生活项目模块
"""

import asyncio
import json
from typing import Any
import uuid

import websockets
from websockets.exceptions import ConnectionClosed

#! / usr / bin / env python
# - * - coding: utf - 8 - * -

"""
WebSocket 客户端示例

展示如何使用 API 网关的 WebSocket 功能。
"""




class WebSocketClient:
    """WebSocket 客户端"""

    def __init__(self, url: str, user_id: str | None = None):
"""TODO: 添加文档字符串"""
self.url = url
self.user_id = user_id or str(uuid.uuid4())
self.connection_id = str(uuid.uuid4())
self.websocket = None
self.running = False

    async def connect(self, room: str | None = None):
"""连接到 WebSocket 服务器"""
try:
            # 构建连接 URL
            params = [f"user_id = {self.user_id}", f"connection_id = {self.connection_id}"]
            if room:
                params.append(f"room = {room}")

            full_url = f"{self.url}?{'&'.join(params)}"

            print(f"连接到: {full_url}")
            self.websocket = await websockets.connect(full_url)
            self.running = True

            print(f"✓ 已连接 (用户: {self.user_id}, 连接: {self.connection_id})")

            # 启动消息监听
            await self._listen_messages()

except Exception as e:
            print(f"✗ 连接失败: {e}")

    async def disconnect(self) -> None:
"""断开连接"""
self.running = False
if self.websocket:
            await self.websocket.close()
            print("✓ 已断开连接")

    async def send_message(self, message: dict[str, Any]):
"""发送消息"""
if self.websocket:
            try:
                await self.websocket.send(json.dumps(message))
                print(f"→ 发送: {message}")
            except Exception as e:
                print(f"✗ 发送失败: {e}")

    async def join_room(self, room: str):
"""加入房间"""
await self.send_message({
            "type": "room_join",
            "room": room,
})

    async def leave_room(self, room: str):
"""离开房间"""
await self.send_message({
            "type": "room_leave",
            "room": room,
})

    async def send_chat_message(self, content: str, room: str | None = None):
"""发送聊天消息"""
message = {
            "type": "message",
            "content": content,
            "timestamp": asyncio.get_event_loop().time(),
}
if room:
            message["room"] = room

await self.send_message(message)

    async def ping(self) -> None:
"""发送 ping"""
await self.send_message({"type": "ping"})

    async def _listen_messages(self) -> None:
"""监听消息"""
try:
            while self.running:
                try:
                    message = await asyncio.wait_for(
                        self.websocket.recv(),
                        timeout = 1.0
                    )

                    try:
                        data = json.loads(message)
                        await self._handle_message(data)
                    except json.JSONDecodeError:
                        print(f"← 收到文本: {message}")

                except TimeoutError:
                    continue
                except ConnectionClosed:
                    print("✗ 连接已关闭")
                    break

except Exception as e:
            print(f"✗ 监听消息时出错: {e}")
finally:
            self.running = False

    async def _handle_message(self, data: dict[str, Any]):
"""处理收到的消息"""
msg_type = data.get("type", "unknown")

if msg_type=="connect":
            print(f"← 连接确认: {data}")
elif msg_type=="pong":
            print(f"← Pong: {data}")
elif msg_type=="message":
            sender = data.get("sender", "unknown")
            content = data.get("content", "")
            room = data.get("room", "")
            room_info = f" [房间: {room}]" if room else ""
            print(f"← 消息{room_info}: {sender}: {content}")
elif msg_type=="broadcast":
            content = data.get("content", "")
            print(f"← 广播: {content}")
elif msg_type=="room_joined":
            room = data.get("room", "")
            print(f"← 已加入房间: {room}")
elif msg_type=="room_left":
            room = data.get("room", "")
            print(f"← 已离开房间: {room}")
elif msg_type=="error":
            error = data.get("error", "")
            print(f"← 错误: {error}")
else:
            print(f"← 未知消息: {data}")


async def interactive_client() -> None:
    """交互式客户端"""
    print(" === WebSocket 客户端示例 === ")

    # 配置
    url = "ws: / /localhost:8000 / ws / connect"
    user_id = input("输入用户ID (回车使用随机ID): ").strip()
    if not user_id:
user_id = f"user_{uuid.uuid4().hex[:8]}"

    room = input("输入初始房间 (可选): ").strip() or None

    # 创建客户端
    client = WebSocketClient(url, user_id)

    # 连接
    try:
# 在后台运行连接
asyncio.create_task(client.connect(room))

# 等待连接建立
await asyncio.sleep(1)

if not client.running:
            print("连接失败，退出")
            return

print("\n可用命令:")
print("  / join <room>     - 加入房间")
print("  / leave <room>    - 离开房间")
print("  / ping            - 发送 ping")
print("  / quit            - 退出")
print("  其他文本         - 发送聊天消息")
print()

# 交互循环
while client.running:
            try:
                command = await asyncio.wait_for(
                    asyncio.to_thread(input, ">>> "),
                    timeout = 0.1
                )

                if command.startswith(" / "):
                    await handle_command(client, command)
                else:
                    await client.send_chat_message(command)

            except TimeoutError:
                continue
            except KeyboardInterrupt:
                break
            except EOFError:
                break

    except KeyboardInterrupt:
pass
    finally:
await client.disconnect()


async def handle_command(client: WebSocketClient, command: str):
    """处理命令"""
    parts = command.split()
    cmd = parts[0].lower()

    if cmd==" / quit":
await client.disconnect()
    elif cmd==" / ping":
await client.ping()
    elif cmd==" / join" and len(parts) > 1:
room = parts[1]
await client.join_room(room)
    elif cmd==" / leave" and len(parts) > 1:
room = parts[1]
await client.leave_room(room)
    else:
print(f"未知命令: {command}")


async def demo_multiple_clients() -> None:
    """演示多个客户端"""
    print(" === 多客户端演示 === ")

    url = "ws: / /localhost:8000 / ws / connect"
    clients = []

    try:
# 创建多个客户端
for i in range(3):
            client = WebSocketClient(url, f"user_{i + 1}")
            clients.append(client)

            # 连接客户端
            asyncio.create_task(client.connect("demo_room"))
            await asyncio.sleep(0.5)

# 等待连接建立
await asyncio.sleep(2)

# 发送一些测试消息
for i, client in enumerate(clients):
            await client.send_chat_message(f"Hello from user {i + 1}!", "demo_room")
            await asyncio.sleep(1)

# 演示房间切换
await clients[0].leave_room("demo_room")
await clients[0].join_room("private_room")
await asyncio.sleep(1)

await clients[0].send_chat_message("This is a private message", "private_room")
await asyncio.sleep(1)

# 演示 ping / pong
for client in clients:
            await client.ping()
            await asyncio.sleep(0.5)

# 保持连接一段时间
print("保持连接 10 秒...")
await asyncio.sleep(10)

    finally:
# 断开所有连接
for client in clients:
            await client.disconnect()


async def stress_test() -> None:
    """压力测试"""
    print(" === 压力测试 === ")

    url = "ws: / /localhost:8000 / ws / connect"
    num_clients = 10
    clients = []

    try:
# 创建多个客户端
print(f"创建 {num_clients} 个客户端...")
for i in range(num_clients):
            client = WebSocketClient(url, f"stress_user_{i}")
            clients.append(client)

            # 连接客户端
            asyncio.create_task(client.connect("stress_room"))
            await asyncio.sleep(0.1)  # 避免连接过快

# 等待连接建立
await asyncio.sleep(2)

print("发送消息...")
# 每个客户端发送多条消息
for round_num in range(5):
            for i, client in enumerate(clients):
                await client.send_chat_message(
                    f"Message {round_num + 1} from client {i + 1}",
                    "stress_room"
                )
            await asyncio.sleep(1)

print("压力测试完成")
await asyncio.sleep(5)

    finally:
# 断开所有连接
for client in clients:
            await client.disconnect()


async def main() -> None:
    """主函数"""
    print("WebSocket 客户端示例")
    print("1. 交互式客户端")
    print("2. 多客户端演示")
    print("3. 压力测试")

    choice = input("选择模式 (1 - 3): ").strip()

    if choice=="1":
await interactive_client()
    elif choice=="2":
await demo_multiple_clients()
    elif choice=="3":
await stress_test()
    else:
print("无效选择")


if __name__=="__main__":
    try:
asyncio.run(main())
    except KeyboardInterrupt:
print("\n程序被中断")
