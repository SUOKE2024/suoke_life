#!/usr/bin/env python3
"""
与小艾智能体交互对话脚本
让用户可以直接与小艾进行实时对话
"""

import asyncio
import os
import sys
import traceback
import uuid
from datetime import datetime

# 添加项目路径
sys.path.append('.')

os.environ['DEEPSEEK_API_KEY'] = 'sk-26ac526b8c3b41c2a39bd80a156aaa68'

class XiaoaiChatInterface:
    """小艾对话界面"""

    def __init__(self):
        self.agent_manager = None
        self.user_id = f"user_{uuid.uuid4().hex[:8]}"
        self.session_id = f"session_{uuid.uuid4().hex[:8]}"
        self.conversation_history = []

    async def initialize(self):
        """初始化小艾智能体"""
        try:
            from internal.agent.agent_manager import AgentManager

            print("🤖 正在初始化小艾智能体...")
            self.agent_manager = AgentManager()
            await self.agent_manager.initialize()

            # 获取模型信息
            factory_type = type(self.agent_manager.model_factory).__name__
            print("✅ 小艾初始化完成!")
            print(f"📊 使用模型: {factory_type}")
            print(f"👤 用户ID: {self.user_id}")
            print(f"💬 会话ID: {self.session_id}")

            return True

        except Exception as e:
            print(f"❌ 小艾初始化失败: {e}")
            traceback.print_exc()
            return False

    async def chat(self, message):
        """与小艾对话"""
        try:
            # 记录用户消息
            self.conversation_history.append({
                "role": "user",
                "message": message,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })

            response = await self.agent_manager.chat(
                user_id=self.user_id,
                message=message,
                session_id=self.session_id
            )

            # 记录小艾回复
            self.conversation_history.append({
                "role": "xiaoai",
                "message": response['message'],
                "confidence": response['confidence'],
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "metadata": response.get('metadata', {})
            })

            return response

        except Exception as e:
            error_msg = f"对话出错: {e}"
            print(f"❌ {error_msg}")
            return {
                "message": "抱歉,我现在有点问题,请稍后再试。",
                "confidence": 0.0,
                "metadata": {"error": str(e)}
            }

    def display_response(self, _response):
        """显示小艾的回复"""
        print(f"\n🤖 小艾: {response['message']}")

        # 显示元数据(如果有)
        metadata = response.get('metadata', {})
        if metadata:
            model = metadata.get('model', '未知')
            provider = metadata.get('provider', '未知')
            print(f"   📊 模型: {model} | 提供商: {provider} | 置信度: {response['confidence']:.2f}")

    def show_help(self):
        """显示帮助信息"""
        print("\n" + "="*50)
        print("💡 小艾对话帮助:")
        print("="*50)
        print("📝 直接输入消息与小艾对话")
        print("🔍 /help - 显示帮助信息")
        print("📋 /history - 查看对话历史")
        print("🔄 /clear - 清空对话历史")
        print("📊 /status - 查看系统状态")
        print("👋 /quit 或 /exit - 退出对话")
        print("="*50)

    def show_history(self):
        """显示对话历史"""
        print("\n" + "="*50)
        print("📋 对话历史:")
        print("="*50)

        if not self.conversation_history:
            print("暂无对话记录")
            return

        for i, _ in enumerate(self.conversation_history, 1):
            role_icon = "👤" if entry['role'] == 'user' else "🤖"
            role_name = "您" if entry['role'] == 'user' else "小艾"

            print(f"{i}. [{entry['timestamp']}] {role_icon} {role_name}: {entry['message']}")

            if entry['role'] == 'xiaoai' and 'confidence' in entry:
                print(f"   置信度: {entry['confidence']:.2f}")

        print("="*50)

    def clear_history(self):
        """清空对话历史"""
        self.conversation_history.clear()
        self.session_id = f"session_{uuid.uuid4().hex[:8]}"
        print("✅ 对话历史已清空,开始新的会话")

    def show_status(self):
        """显示系统状态"""
        print("\n" + "="*50)
        print("📊 系统状态:")
        print("="*50)

        if self.agent_manager:
            factory_type = type(self.agent_manager.model_factory).__name__
            print("🤖 智能体状态: 已初始化")
            print(f"📊 模型工厂: {factory_type}")
            print(f"👤 用户ID: {self.user_id}")
            print(f"💬 会话ID: {self.session_id}")
            print(f"📝 对话轮数: {len([h for h in self.conversation_history if h['role'] == 'user'])}")
        else:
            print("❌ 智能体状态: 未初始化")

        print("="*50)

    async def run(self):
        """运行对话界面"""
        # 显示欢迎信息
        print("🎉 欢迎使用小艾智能体对话系统!")
        print("="*60)

        if not await self.initialize():
            print("❌ 无法启动小艾,请检查配置")
            return

        # 显示帮助
        self.show_help()

        # 小艾自我介绍
        print("\n🤖 小艾: 您好!我是小艾,您的中医健康助手。我可以为您提供中医养生建议、健康咨询和生活指导。请问有什么可以帮助您的吗?")

        # 开始对话循环
        while True:
            try:
                # 获取用户输入
                user_input = input("\n👤 您: ").strip()

                if user_input.lower() in ['/quit', '/exit', '退出', '再见']:
                    print("\n👋 小艾: 再见!祝您身体健康,生活愉快!")
                    break
                elif user_input.lower() == '/help':
                    self.show_help()
                    continue
                elif user_input.lower() == '/history':
                    self.show_history()
                    continue
                elif user_input.lower() == '/clear':
                    self.clear_history()
                    continue
                elif user_input.lower() == '/status':
                    self.show_status()
                    continue
                elif not user_input:
                    print("请输入您的问题,或输入 /help 查看帮助")
                    continue

                # 与小艾对话
                print("🤔 小艾正在思考...")
                response = await self.chat(user_input)
                self.display_response(response)

            except KeyboardInterrupt:
                print("\n\n👋 小艾: 再见!祝您身体健康!")
                break
            except Exception as e:
                print(f"\n❌ 系统错误: {e}")
                print("请重试或输入 /quit 退出")

async def main():
    """主函数"""
    chat_interface = XiaoaiChatInterface()
    await chat_interface.run()

if __name__ == "__main__":
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    asyncio.run(main())
