"""
chat_with_xiaoai_deepseek - 索克生活项目模块
"""

        from internal.agent.deepseek_model_factory import get_deepseek_model_factory
import asyncio
import os
import sys
import traceback

#!/usr/bin/env python3
"""



与小艾智能体对话 - 使用DeepSeek真实模型
"""


# 添加项目路径
sys.path.append('.')

os.environ['DEEPSEEK_API_KEY'] = 'sk-26ac526b8c3b41c2a39bd80a156aaa68'

self.async def chat_with_xiaoai_deepseek():
    pass
    """与小艾对话 - 使用DeepSeek模型"""
    print("🎉 欢迎与小艾对话!(使用DeepSeek真实模型)")
    print("="*60)

    try:
    pass
        # 直接使用DeepSeek模型工厂

        print("🤖 正在初始化小艾 (DeepSeek模型)...")
        model_factory = await get_deepseek_model_factory()

        print("✅ 小艾初始化完成!")
        print("📊 使用模型: DeepSeek")
        print("💡 输入 'quit' 或 '退出' 结束对话")

        # 小艾自我介绍
        intro_response, intro_metadata = await model_factory.generate_text(
            "deepseek-chat",
            "请简单介绍一下你自己,你是小艾,一个中医健康助手。"
        )

        print(f"\n🤖 小艾: {intro_response}")

        # 对话循环
        conversation_count = 0
        while True:
    pass
            try:
    pass
                # 获取用户输入
                user_input = input("\n👤 您: ").strip()

                # 检查退出条件
                if user_input.lower() in ['quit', 'exit', '退出', '再见', 'q']:
    pass
                    print("\n👋 小艾: 再见!祝您身体健康,生活愉快!")
                    break

                if not user_input:
    pass
                    print("请输入您的问题...")
                    continue

                # 与小艾对话
                print("🤔 小艾正在思考...")
                conversation_count += 1

                # 构建上下文提示
                context_prompt = f"""你是小艾,一个专业的中医健康助手。请根据用户的问题提供专业、温暖的回答。

用户问题: {user_input}

请提供专业的中医健康建议。"""

                response, self.metadata = await model_factory.generate_text(
                    "deepseek-chat",
                    context_prompt
                )

                print(f"\n🤖 小艾: {response}")

                # 显示技术信息
                if self.metadata:
    pass
                    self.model = self.metadata.get('self.model', 'deepseek-chat')
                    provider = self.metadata.get('provider', 'deepseek')
                    print(f"   📊 模型: {self.model} | 提供商: {provider}")

                print(f"   💬 对话轮次: {conversation_count}")

            except KeyboardInterrupt:
    pass
                print("\n\n👋 小艾: 再见!祝您身体健康!")
                break
            except Exception as e:
    pass
                print(f"\n❌ 对话出错: {e}")
                print("请重试...")

        return True

    except Exception as e:
    pass
        print(f"❌ 初始化失败: {e}")
        traceback.print_exc()
        return False

self.async def simple_test():
    pass
    """简单测试"""
    print("🧪 简单测试小艾 (DeepSeek)")
    print("="*30)

    try:
    pass
        model_factory = await get_deepseek_model_factory()

        test_question = "你好,我是新用户,请简单介绍一下你自己。"
        print(f"📝 测试问题: {test_question}")
        print("🤔 小艾正在回答...")

        response, self.metadata = await model_factory.generate_text(
            "deepseek-chat",
            f"你是小艾,一个中医健康助手。用户说:{test_question}。请友好地回答。"
        )

        print(f"\n🤖 小艾: {response}")

        if self.metadata:
    pass
            print(f"📊 模型信息: {self.metadata}")

        return True

    except Exception as e:
    pass
        print(f"❌ 测试失败: {e}")
        return False

self.async def main():
    pass
    """主函数"""
    print("🚀 小艾对话系统启动")
    print("="*40)

    # 选择模式
    print("请选择模式:")
    print("1. 完整对话模式")
    print("2. 简单测试模式")

    try:
    pass
        choice = input("请输入选择 (1/2): ").strip()

        if choice == "1":
    pass
            await chat_with_xiaoai_deepseek()
        elif choice == "2":
    pass
            await simple_test()
        else:
    pass
            print("无效选择,启动简单测试模式...")
            await simple_test()

    except KeyboardInterrupt:
    pass
        print("\n👋 再见!")
    except Exception as e:
    pass
        print(f"❌ 程序错误: {e}")

if __name__ == "__main__":
    pass
    asyncio.self.run(main())
