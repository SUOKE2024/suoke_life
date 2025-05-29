#!/usr/bin/env python3
"""
小艾服务开发环境集成测试
专门用于开发环境的测试,使用模拟服务和文件存储
"""

import asyncio
import sys
import traceback
from pathlib import Path

# 添加项目路径
sys.path.append('.')

def test_imports():
    """测试所有核心组件的导入"""
    print("🔍 开始测试核心组件导入...")

    tests = [
        # 核心模型组件
        ("模拟模型工厂", "from internal.agent.mock_model_factory import get_mock_model_factory"),
        ("文件会话存储库", "from internal.repository.file_session_repository import FileSessionRepository"),
        ("智能体管理器", "from internal.agent.agent_manager import AgentManager"),

        # 配置组件
        ("配置加载器", "from pkg.utils.config_loader import get_config"),
        ("指标收集器", "from pkg.utils.metrics import get_metrics_collector"),

        # gRPC 组件
        ("gRPC protobuf", "import api.grpc.xiaoai_service_pb2 as xiaoai_pb2"),
        ("gRPC 服务", "import api.grpc.xiaoai_service_pb2_grpc as xiaoai_pb2_grpc"),
    ]

    success_count = 0
    total_count = len(tests)

    for name, import_statement in tests:
        try:
            exec(import_statement)
            print(f"  ✓ {name}")
            success_count += 1
        except Exception as e:
            print(f"  ❌ {name}: {e}")

    print(f"\n📊 导入测试结果: {success_count}/{total_count} 成功")
    return success_count == total_count

async def test_mock_model_factory():
    """测试模拟模型工厂功能"""
    print("\n🔍 测试模拟模型工厂功能...")

    try:
        from internal.agent.mock_model_factory import get_mock_model_factory

        # 获取模拟模型工厂实例
        factory = await get_mock_model_factory()
        print("  ✓ 模拟模型工厂实例创建成功")

        # 测试获取可用模型
        models = factory.get_available_models()
        print(f"  ✓ 获取可用模型: {models}")

        # 测试健康状态
        health = factory.get_model_health_status()
        print(f"  ✓ 获取健康状态: {len(health)} 个模型")

        response, metadata = await factory.generate_text("mock", "你好,我是测试用户")
        print(f"  ✓ 文本生成测试: {response[:50]}...")
        print(f"  ✓ 元数据: {metadata}")

        voice_result = await factory.process_multimodal_input("voice", "test_audio_data")
        print(f"  ✓ 语音处理测试: {voice_result}")

        # 测试健康分析
        health_result = await factory.health_analysis(["疲劳", "头痛"], {"age": 30})
        print(f"  ✓ 健康分析测试: {health_result['syndrome_analysis']}")

        return True

    except Exception as e:
        print(f"  ❌ 模拟模型工厂测试失败: {e}")
        traceback.print_exc()
        return False

async def test_file_session_repository():
    """测试文件会话存储库功能"""
    print("\n🔍 测试文件会话存储库功能...")

    try:
        from internal.repository.file_session_repository import FileSessionRepository

        repo = FileSessionRepository()
        print("  ✓ 文件会话存储库实例创建成功")

        # 测试保存会话
        test_session = {
            "session_id": "test_session_123",
            "user_id": "test_user_456",
            "messages": [
                {"role": "user", "content": "你好"},
                {"role": "assistant", "content": "您好!我是小艾"}
            ],
            "metadata": {"test": True}
        }

        save_result = await repo.save_session(test_session)
        print(f"  ✓ 保存会话测试: {save_result}")

        # 测试获取会话
        retrieved_session = await repo.get_session("test_session_123")
        print(f"  ✓ 获取会话测试: {retrieved_session is not None}")

        # 测试获取用户会话
        user_sessions = await repo.get_user_sessions("test_user_456")
        print(f"  ✓ 获取用户会话测试: {len(user_sessions)} 个会话")

        update_result = await repo.update_session_metadata("test_session_123", {"updated": True})
        print(f"  ✓ 更新元数据测试: {update_result}")

        # 测试计数活跃会话
        active_count = await repo.count_active_sessions()
        print(f"  ✓ 活跃会话计数: {active_count}")

        return True

    except Exception as e:
        print(f"  ❌ 文件会话存储库测试失败: {e}")
        traceback.print_exc()
        return False

async def test_agent_manager():
    """测试智能体管理器功能"""
    print("\n🔍 测试智能体管理器功能...")

    try:
        from internal.agent.agent_manager import AgentManager

        agent_manager = AgentManager()
        print("  ✓ 智能体管理器实例创建成功")

        await agent_manager.initialize()
        print("  ✓ 智能体管理器异步初始化成功")

        # 测试聊天功能
        chat_response = await agent_manager.chat(
            user_id="test_user",
            message="你好,我想咨询健康问题",
            session_id="test_chat_session"
        )
        print(f"  ✓ 聊天测试: {chat_response['message'][:50]}...")

        multimodal_response = await agent_manager.process_multimodal_input(
            user_id="test_user",
            input_data={"type": "text", "content": "我感觉有点累"},
            session_id="test_multimodal_session"
        )
        print(f"  ✓ 多模态处理测试: {multimodal_response.get('message', 'OK')[:50]}...")

        return True

    except Exception as e:
        print(f"  ❌ 智能体管理器测试失败: {e}")
        traceback.print_exc()
        return False

def test_config_loading():
    """测试配置加载功能"""
    print("\n🔍 测试配置加载功能...")

    try:
        from pkg.utils.config_loader import get_config

        # 获取配置实例
        config = get_config()
        print("  ✓ 配置加载器实例创建成功")

        # 测试获取配置
        service_config = config.get_section('service')
        print(f"  ✓ 服务配置: {service_config.get('name', 'unknown')}")

        # 测试开发环境配置
        dev_config = config.get_section('development')
        print(f"  ✓ 开发环境配置: mock_services={dev_config.get('mock_services', False)}")

        # 测试文件存储配置
        file_storage_config = config.get_section('file_storage')
        print(f"  ✓ 文件存储配置: enabled={file_storage_config.get('enabled', False)}")

        return True

    except Exception as e:
        print(f"  ❌ 配置加载测试失败: {e}")
        traceback.print_exc()
        return False

def test_directory_structure():
    """测试目录结构"""
    print("\n🔍 测试目录结构...")

    required_dirs = [
        "logs",
        "data",
        "data/cache",
        "data/models"
    ]

    success_count = 0
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"  ✓ 目录存在: {dir_path}")
            success_count += 1
        else:
            print(f"  ❌ 目录缺失: {dir_path}")

    print(f"\n📊 目录检查结果: {success_count}/{len(required_dirs)} 成功")
    return success_count == len(required_dirs)

async def main():
    """主测试函数"""
    print("🚀 开始小艾服务开发环境集成测试\n")

    # 测试结果统计
    test_results = []

    # 1. 测试目录结构
    test_results.append(("目录结构", test_directory_structure()))

    # 2. 测试配置加载
    test_results.append(("配置加载", test_config_loading()))

    # 3. 测试导入
    test_results.append(("导入测试", test_imports()))

    # 4. 测试模拟模型工厂
    test_results.append(("模拟模型工厂", await test_mock_model_factory()))

    # 5. 测试文件会话存储库
    test_results.append(("文件会话存储库", await test_file_session_repository()))

    # 6. 测试智能体管理器
    test_results.append(("智能体管理器", await test_agent_manager()))

    # 输出测试结果摘要
    print("\n" + "="*50)
    print("📋 测试结果摘要:")
    print("="*50)

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
        print("🎉 开发环境测试基本通过!")
        completion_level = "高"
    elif success_rate >= 60:
        print("⚠️  开发环境测试部分通过,需要进一步优化。")
        completion_level = "中"
    else:
        print("🔴 开发环境测试失败较多,需要大量修复工作。")
        completion_level = "低"

    print("\n" + "="*50)
    print("📈 开发环境完成度评估:")
    print("="*50)
    print(f"🔵 开发完成度: {completion_level} ({success_rate:.1f}%)")

    if success_rate < 100:
        print("   - 建议优先修复失败的测试项")
        print("   - 确保开发环境配置正确")
        print("   - 检查文件权限和目录结构")

if __name__ == "__main__":
    asyncio.run(main())
