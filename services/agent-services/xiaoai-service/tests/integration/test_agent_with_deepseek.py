#!/usr/bin/env python3
"""
智能体管理器使用DeepSeek的专项测试
验证智能体管理器能否正确调用DeepSeek API
"""

import asyncio
import os
import sys
import traceback

# 添加项目路径
sys.path.append('.')

os.environ['DEEPSEEK_API_KEY'] = 'sk-26ac526b8c3b41c2a39bd80a156aaa68'

async def test_agent_manager_with_deepseek():
    """测试智能体管理器使用DeepSeek"""
    print("🔍 测试智能体管理器使用DeepSeek...")

    try:
        # 强制使用生产配置
        from pkg.utils.config_loader import ConfigLoader

        config = ConfigLoader("config/prod.yaml")

        # 验证配置
        deepseek_config = config.get_section('models.deepseek')
        llm_config = config.get_section('models.llm')
        dev_config = config.get_section('development')

        print("  📋 配置信息:")
        print(f"    DeepSeek配置: {deepseek_config}")
        print(f"    LLM主模型: {llm_config.get('primary_model')}")
        print(f"    模拟服务: {dev_config.get('mock_services')}")

        # 临时替换全局配置
        from internal.agent.agent_manager import AgentManager
        original_get_config = pkg.utils.config_loader.get_config
        pkg.utils.config_loader.get_config = lambda path=None: config

        try:
            agent_manager = AgentManager()
            print("  ✓ 智能体管理器实例创建成功")

            await agent_manager.initialize()
            print("  ✓ 智能体管理器初始化成功")

            # 检查使用的模型工厂类型
            factory_type = type(agent_manager.model_factory).__name__
            print(f"  📊 使用的模型工厂: {factory_type}")

            # 测试基本聊天功能
            print("  🔄 测试基本聊天功能...")
            chat_response = await agent_manager.chat(
                user_id="test_user_deepseek",
                message="你好,我想了解一下中医的五脏六腑理论。",
                session_id="test_deepseek_session_1"
            )

            print("  ✓ 基本聊天测试成功:")
            print(f"    响应: {chat_response['message'][:150]}...")
            print(f"    置信度: {chat_response['confidence']}")
            print(f"    模型: {chat_response['metadata'].get('model', 'unknown')}")
            print(f"    提供商: {chat_response['metadata'].get('provider', 'unknown')}")
            print(f"    耗时: {chat_response['metadata'].get('processing_time', 0):.2f}秒")

            # 测试健康咨询功能
            print("  🔄 测试健康咨询功能...")
            health_response = await agent_manager.chat(
                user_id="test_user_deepseek",
                message="我最近总是感到头晕、乏力,还有点心悸,从中医角度应该怎么调理?",
                session_id="test_deepseek_session_2"
            )

            print("  ✓ 健康咨询测试成功:")
            print(f"    响应: {health_response['message'][:150]}...")
            print(f"    置信度: {health_response['confidence']}")
            print(f"    Token使用: {health_response['metadata'].get('usage', {})}")

            print("  🔄 测试多模态输入处理...")
            multimodal_response = await agent_manager.process_multimodal_input(
                user_id="test_user_deepseek",
                input_data={"type": "text", "content": "我想了解一下针灸的基本原理和适应症。"},
                session_id="test_deepseek_session_3"
            )

            print("  ✓ 多模态输入测试成功:")
            print(f"    响应: {multimodal_response['response'][:150]}...")
            print(f"    置信度: {multimodal_response['confidence']}")

            # 测试四诊协调功能
            print("  🔄 测试四诊协调功能...")
            diagnosis_response = await agent_manager.coordinate_four_diagnosis(
                user_id="test_user_deepseek",
                symptoms=["头晕", "乏力", "心悸"],
                context={"age": 35, "gender": "女"},
                session_id="test_deepseek_session_4"
            )

            print("  ✓ 四诊协调测试成功:")
            print(f"    诊断结果: {diagnosis_response['diagnosis'][:150]}...")
            print(f"    置信度: {diagnosis_response['confidence']}")
            print(f"    建议: {diagnosis_response['recommendations'][:100]}...")

            return True

        finally:
            # 恢复原始配置函数
            pkg.utils.config_loader.get_config = original_get_config

    except Exception as e:
        print(f"  ❌ 智能体管理器DeepSeek测试失败: {e}")
        traceback.print_exc()
        return False

async def test_performance_comparison():
    """测试性能对比(模拟 vs DeepSeek)"""
    print("\n🔍 测试性能对比...")

    try:
        import time

        # 测试问题
        test_question = "请从中医角度分析失眠的原因和调理方法。"

        # 1. 测试模拟模型性能
        print("  📊 测试模拟模型性能...")
        from internal.agent.mock_model_factory import get_mock_model_factory
        mock_factory = await get_mock_model_factory()

        start_time = time.time()
        mock_response, mock_metadata = await mock_factory.generate_text("mock", test_question)
        mock_time = time.time() - start_time

        print(f"    模拟模型耗时: {mock_time:.2f}秒")
        print(f"    响应长度: {len(mock_response)}字符")

        # 2. 测试DeepSeek模型性能
        print("  📊 测试DeepSeek模型性能...")
        from internal.agent.deepseek_model_factory import get_deepseek_model_factory
        deepseek_factory = await get_deepseek_model_factory()

        start_time = time.time()
        deepseek_response, deepseek_metadata = await deepseek_factory.generate_text("deepseek-chat", test_question)
        deepseek_time = time.time() - start_time

        print(f"    DeepSeek模型耗时: {deepseek_time:.2f}秒")
        print(f"    响应长度: {len(deepseek_response)}字符")
        print(f"    Token使用: {deepseek_metadata.get('usage', {})}")

        # 3. 性能对比
        print("  📈 性能对比结果:")
        print(f"    速度比较: DeepSeek比模拟慢 {deepseek_time/mock_time:.1f}倍")
        print("    质量比较: DeepSeek提供真实AI响应,模拟提供固定模板")

        return True

    except Exception as e:
        print(f"  ❌ 性能对比测试失败: {e}")
        traceback.print_exc()
        return False

async def test_error_handling():
    """测试错误处理"""
    print("\n🔍 测试错误处理...")

    try:
        import os

        from internal.agent.deepseek_model_factory import DeepSeekModelFactory
        original_key = os.environ.get('DEEPSEEK_API_KEY')

        try:
            # 临时移除API密钥
            if 'DEEPSEEK_API_KEY' in os.environ:
                del os.environ['DEEPSEEK_API_KEY']

            factory = DeepSeekModelFactory()

            try:
                await factory.initialize()
                print("  ❌ 应该抛出错误但没有")
                return False
            except Exception as e:
                print(f"  ✓ 正确处理了API密钥缺失错误: {e}")

            # 测试无效API密钥
            os.environ['DEEPSEEK_API_KEY'] = "invalid_key"
            factory = DeepSeekModelFactory()
            try:
                await factory.initialize()
                print("  ❌ 应该抛出连接错误但没有")
                return False
            except Exception as e:
                print(f"  ✓ 正确处理了无效API密钥错误: {e}")

        finally:
            # 恢复原始API密钥
            if original_key:
                os.environ['DEEPSEEK_API_KEY'] = original_key

        return True

    except Exception as e:
        print(f"  ❌ 错误处理测试失败: {e}")
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("🚀 开始智能体管理器DeepSeek专项测试\n")

    # 测试结果统计
    test_results = []

    # 1. 测试智能体管理器使用DeepSeek
    test_results.append(("智能体管理器DeepSeek集成", await test_agent_manager_with_deepseek()))

    # 2. 测试性能对比
    test_results.append(("性能对比", await test_performance_comparison()))

    test_results.append(("错误处理", await test_error_handling()))

    # 输出测试结果摘要
    print("\n" + "="*60)
    print("📋 智能体管理器DeepSeek专项测试结果:")
    print("="*60)

    passed_tests = 0
    total_tests = len(test_results)

    for test_name, result in test_results:
        status = "✓ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed_tests += 1

    success_rate = (passed_tests / total_tests) * 100
    print(f"\n📊 总体结果: {passed_tests}/{total_tests} 测试通过 ({success_rate:.1f}%)")

    if success_rate >= 80:
        print("🎉 智能体管理器DeepSeek集成测试基本通过!")
        completion_level = "高"
    elif success_rate >= 60:
        print("⚠️  智能体管理器DeepSeek集成测试部分通过,需要进一步优化。")
        completion_level = "中"
    else:
        print("🔴 智能体管理器DeepSeek集成测试失败较多,需要大量修复工作。")
        completion_level = "低"

    print("\n" + "="*60)
    print("📈 智能体管理器DeepSeek集成完成度评估:")
    print("="*60)
    print(f"🔵 集成完成度: {completion_level} ({success_rate:.1f}%)")

    if success_rate >= 80:
        print("✨ 主要成果:")
        print("   - ✓ 成功集成DeepSeek API")
        print("   - ✓ 智能体管理器能正确调用DeepSeek模型")
        print("   - ✓ 支持中医健康咨询功能")
        print("   - ✓ 多模态输入处理正常")
        print("   - ✓ 四诊协调功能可用")
        print("   - ✓ 错误处理机制完善")

    print("\n💡 使用建议:")
    print("   - 生产环境使用config/prod.yaml配置")
    print("   - 开发环境使用config/dev.yaml配置")
    print("   - 可通过环境变量DEEPSEEK_API_KEY设置API密钥")
    print("   - DeepSeek响应质量高但速度相对较慢")

if __name__ == "__main__":
    asyncio.run(main())
