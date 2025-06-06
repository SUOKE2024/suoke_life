"""
test_integration_complete - 索克生活项目模块
"""

        from cmd.server import XiaoAIServer
        from internal.agent.agent_manager import AgentManager
        from internal.delivery.xiaoai_service_impl import XiaoAIServiceImpl
        from internal.orchestrator.diagnosis_coordinator import DiagnosisCoordinator
        from internal.repository.diagnosis_repository import DiagnosisRepository
        from internal.repository.session_repository import SessionRepository
        from pkg.utils.config_loader import get_config
        from pkg.utils.metrics import get_metrics_collector
        import traceback
from pathlib import Path
import asyncio
import sys

#!/usr/bin/env python3
"""
完整集成测试脚本
验证小艾服务的完整启动和基本功能
"""


# 添加项目根目录到PYTHONPATH
sys.path.insert(0, Path().resolve())

async def test_complete_integration():
    """完整集成测试"""
    print("🚀 开始完整集成测试\n")

    try:
        # 1. 测试配置加载
        print("1. 测试配置加载...")
        config = get_config("config/dev.yaml")
        print(f"✓ 配置加载成功: {type(config)}")

        # 2. 测试指标收集器
        print("\n2. 测试指标收集器...")
        metrics = get_metrics_collector()
        print(f"✓ 指标收集器初始化成功: {type(metrics)}")

        # 3. 测试存储库
        print("\n3. 测试存储库...")

        session_repo = SessionRepository()
        diagnosis_repo = DiagnosisRepository()
        print(f"✓ 会话存储库: {type(session_repo)}")
        print(f"✓ 诊断存储库: {type(diagnosis_repo)}")

        # 4. 测试智能体管理器
        print("\n4. 测试智能体管理器...")

        agent_manager = AgentManager()
        print(f"✓ 智能体管理器创建成功: {type(agent_manager)}")

        await agent_manager.initialize()
        print("✓ 智能体管理器异步初始化成功")

        # 5. 测试四诊协调器
        print("\n5. 测试四诊协调器...")

        coordinator = DiagnosisCoordinator(agent_manager, diagnosis_repo)
        print(f"✓ 四诊协调器创建成功: {type(coordinator)}")

        # 6. 测试服务实现
        print("\n6. 测试服务实现...")

        service_impl = XiaoAIServiceImpl()
        print(f"✓ 服务实现创建成功: {type(service_impl)}")

        # 7. 测试服务器
        print("\n7. 测试服务器...")

        server = XiaoAIServer("config/dev.yaml")
        print(f"✓ 服务器创建成功: {type(server)}")
        print(f"✓ 服务器配置: {server.host}:{server.port}")

        # 8. 测试基本聊天功能
        print("\n8. 测试基本聊天功能...")
        test_user_id = "test_user_001"
        test_message = "你好,我想咨询健康问题"

        chat_result = await agent_manager.chat(test_user_id, test_message)
        print("✓ 聊天功能测试成功")
        print(f"  用户消息: {test_message}")
        print(f"  AI回复: {chat_result['message'][:50]}...")
        print(f"  置信度: {chat_result['confidence']}")

        print("\n9. 测试多模态处理...")
        multimodal_input = {
            'text': '我感觉有点不舒服,请帮我分析一下'
        }

        multimodal_result = await agent_manager.process_multimodal_input(
            test_user_id, multimodal_input
        )
        print("✓ 多模态处理测试成功")
        print(f"  处理结果: {multimodal_result['response'][:50]}...")

        # 10. 测试设备状态
        print("\n10. 测试设备状态...")
        device_status = await agent_manager.get_device_status()
        print("✓ 设备状态获取成功")
        print(f"  摄像头可用: {device_status.get('camera', {}).get('available', False)}")
        print(f"  麦克风可用: {device_status.get('microphone', {}).get('available', False)}")
        print(f"  屏幕可用: {device_status.get('screen', {}).get('available', False)}")

        # 11. 测试指标收集
        print("\n11. 测试指标收集...")
        metrics_summary = metrics.get_summary()
        print("✓ 指标收集测试成功")
        print(f"  运行时间: {metrics_summary['uptime_seconds']:.2f}秒")
        print(f"  请求总数: {metrics_summary['requests_total']}")
        print(f"  错误总数: {metrics_summary['errors_total']}")

        # 12. 清理资源
        print("\n12. 清理资源...")
        await agent_manager.close()
        await coordinator.close()
        print("✓ 资源清理完成")

        print("\n🎉 完整集成测试成功!")
        return True

    except Exception as e:
        print(f"\n❌ 集成测试失败: {e}")
        traceback.print_exc()
        return False

async def test_service_startup():
    """测试服务启动(不实际启动服务器)"""
    print("\n🔍 测试服务启动流程...\n")

    try:

        server = XiaoAIServer("config/dev.yaml")
        print("✓ 服务器实例创建成功")

        # 验证服务器配置
        print(f"✓ 监听地址: {server.host}:{server.port}")
        print(f"✓ 工作线程数: {server.max_workers}")
        print(f"✓ 服务实现: {type(server.service_impl)}")

        # 验证gRPC服务器配置
        print(f"✓ gRPC服务器: {type(server.server)}")

        print("✓ 服务启动流程验证成功")
        return True

    except Exception as e:
        print(f"❌ 服务启动流程验证失败: {e}")
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("=" * 60)
    print("小艾服务完整集成测试")
    print("=" * 60)

    # 运行完整集成测试
    integration_ok = await test_complete_integration()

    # 运行服务启动测试
    startup_ok = await test_service_startup()

    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"完整集成测试: {'✓ 通过' if integration_ok else '❌ 失败'}")
    print(f"服务启动测试: {'✓ 通过' if startup_ok else '❌ 失败'}")

    if integration_ok and startup_ok:
        print("\n🎉 所有测试通过!小艾服务已准备就绪!")
        print("\n📝 启动服务命令:")
        print("   python3 cmd/server.py --config config/dev.yaml")
        return True
    else:
        print("\n⚠️ 存在问题需要修复")
        return False

if __name__ == '__main__':
    asyncio.run(main())
