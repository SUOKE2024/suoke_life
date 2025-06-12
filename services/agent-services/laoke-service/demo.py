#!/usr/bin/env python3
"""
老克智能体服务演示脚本

这个脚本展示了老克智能体服务的主要功能：
1. 创建会话
2. 发送消息
3. 获取响应
4. 无障碍功能演示
5. 服务统计
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    import httpx
except ImportError:
    print("❌ 需要安装httpx: pip install httpx")
    sys.exit(1)


class LaokeServiceDemo:
    """老克服务演示类"""

    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.session_id = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def check_service_health(self) -> bool:
        """检查服务健康状态"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 服务健康状态: {data.get('status', 'unknown')}")
                return True
            else:
                print(f"❌ 服务不健康: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 无法连接到服务: {e}")
            return False

    async def get_service_info(self) -> Dict[str, Any]:
        """获取服务信息"""
        try:
            response = await self.client.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                print(f"📊 服务信息:")
                print(f"   名称: {data.get('name', 'N/A')}")
                print(f"   版本: {data.get('version', 'N/A')}")
                print(f"   环境: {data.get('environment', 'N/A')}")
                print(f"   启动时间: {data.get('start_time', 'N/A')}")
                return data
            else:
                print(f"❌ 获取服务信息失败: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ 获取服务信息失败: {e}")
            return {}

    async def create_session(self) -> str:
        """创建新会话"""
        try:
            response = await self.client.post(
                f"{self.base_url}/sessions", json={"user_id": "demo_user"}
            )
            if response.status_code == 201:
                data = response.json()
                self.session_id = data["session_id"]
                print(f"✅ 创建会话成功: {self.session_id}")
                return self.session_id
            else:
                print(f"❌ 创建会话失败: {response.status_code}")
                return ""
        except Exception as e:
            print(f"❌ 创建会话失败: {e}")
            return ""

    async def send_message(
        self, message: str, accessibility_config: Dict = None
    ) -> str:
        """发送消息并获取响应"""
        if not self.session_id:
            print("❌ 没有活跃的会话，请先创建会话")
            return ""

        try:
            payload = {"message": message, "message_type": "text"}

            if accessibility_config:
                payload["accessibility_config"] = accessibility_config

            response = await self.client.post(
                f"{self.base_url}/sessions/{self.session_id}/chat", json=payload
            )

            if response.status_code == 200:
                data = response.json()
                ai_response = data.get("response", "")
                print(f"🤖 老克: {ai_response}")
                return ai_response
            else:
                print(f"❌ 发送消息失败: {response.status_code}")
                if response.status_code == 400:
                    error_detail = response.json().get("detail", "Unknown error")
                    print(f"   错误详情: {error_detail}")
                return ""
        except Exception as e:
            print(f"❌ 发送消息失败: {e}")
            return ""

    async def get_session_info(self) -> Dict[str, Any]:
        """获取会话信息"""
        if not self.session_id:
            return {}

        try:
            response = await self.client.get(
                f"{self.base_url}/sessions/{self.session_id}"
            )
            if response.status_code == 200:
                data = response.json()
                print(f"📊 会话信息:")
                print(f"   会话ID: {data.get('session_id', 'N/A')}")
                print(f"   用户ID: {data.get('user_id', 'N/A')}")
                print(f"   创建时间: {data.get('created_at', 'N/A')}")
                print(f"   消息数量: {len(data.get('messages', []))}")
                return data
            else:
                print(f"❌ 获取会话信息失败: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ 获取会话信息失败: {e}")
            return {}

    async def get_service_stats(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        try:
            response = await self.client.get(f"{self.base_url}/stats")
            if response.status_code == 200:
                data = response.json()
                print(f"📊 服务统计:")
                print(f"   活跃会话: {data.get('active_sessions', 0)}")
                print(f"   总消息数: {data.get('total_messages', 0)}")
                print(f"   平均响应时间: {data.get('avg_response_time', 0):.2f}ms")
                return data
            else:
                print(f"❌ 获取统计信息失败: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ 获取统计信息失败: {e}")
            return {}

    async def demo_accessibility_features(self):
        """演示无障碍功能"""
        print("\n🔊 演示无障碍功能...")

        # 演示不同的无障碍配置
        accessibility_configs = [
            {
                "tts_enabled": True,
                "large_font": True,
                "high_contrast": False,
                "screen_reader": False,
                "simplified_ui": True,
            },
            {
                "tts_enabled": False,
                "large_font": False,
                "high_contrast": True,
                "screen_reader": True,
                "simplified_ui": False,
            },
        ]

        for i, config in enumerate(accessibility_configs, 1):
            print(f"\n♿ 无障碍配置 {i}:")
            for key, value in config.items():
                print(f"   {key}: {value}")

            response = await self.send_message(
                f"你好，这是无障碍配置{i}的测试消息。", accessibility_config=config
            )

            if response:
                print(f"   响应长度: {len(response)} 字符")


async def main():
    """主演示函数"""
    print("🚀 老克智能体服务演示")
    print("=" * 50)

    async with LaokeServiceDemo() as demo:
        # 1. 检查服务健康状态
        print("\n1️⃣ 检查服务健康状态...")
        if not await demo.check_service_health():
            print("❌ 服务不可用，请先启动服务: ./start_simple.sh")
            return

        # 2. 获取服务信息
        print("\n2️⃣ 获取服务信息...")
        await demo.get_service_info()

        # 3. 创建会话
        print("\n3️⃣ 创建会话...")
        session_id = await demo.create_session()
        if not session_id:
            print("❌ 无法创建会话，退出演示")
            return

        # 4. 发送消息
        print("\n4️⃣ 发送消息...")
        messages = [
            "你好，我是用户，很高兴与你交流！",
            "你能介绍一下你的功能吗？",
            "谢谢你的介绍，你真的很棒！",
        ]

        for i, message in enumerate(messages, 1):
            print(f"\n💬 用户消息 {i}: {message}")
            await demo.send_message(message)
            await asyncio.sleep(1)  # 稍微停顿

        # 5. 获取会话信息
        print("\n5️⃣ 获取会话信息...")
        await demo.get_session_info()

        # 6. 演示无障碍功能
        print("\n6️⃣ 演示无障碍功能...")
        await demo.demo_accessibility_features()

        # 7. 获取服务统计
        print("\n7️⃣ 获取服务统计...")
        await demo.get_service_stats()

        print("\n" + "=" * 50)
        print("✅ 演示完成！老克智能体服务运行正常。")
        print("")
        print("📝 更多信息:")
        print("   - 查看快速指南: cat QUICKSTART.md")
        print("   - 查看完成度报告: cat PROJECT_COMPLETION_REPORT.md")
        print("   - API文档: http://localhost:8080/docs")
        print("   - 健康检查: http://localhost:8080/health")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示运行错误: {e}")
        sys.exit(1)
