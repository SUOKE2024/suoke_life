#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小艾服务完整集成测试
测试所有核心组件的导入和基本功能
"""

import sys
import traceback
import asyncio

# 添加项目路径
sys.path.append('.')

def test_imports():
    """测试所有核心组件的导入"""
    print("🔍 开始测试核心组件导入...")
    
    tests = [
        # 核心模型组件
        ("模型工厂", "from internal.agent.model_factory import get_model_factory"),
        ("配置管理器", "from internal.agent.model_config_manager import get_model_config_manager"),
        ("智能体管理器", "from internal.agent.agent_manager import AgentManager"),
        
        # gRPC 服务组件
        ("gRPC 服务实现", "from internal.delivery.xiaoai_service_impl import XiaoAIServiceImpl"),
        ("服务器启动类", "from cmd.server import XiaoAIServer"),
        
        # 存储库组件
        ("会话存储库", "from internal.repository.session_repository import SessionRepository"),
        ("诊断存储库", "from internal.repository.diagnosis_repository import DiagnosisRepository"),
        
        # 协调器组件
        ("诊断协调器", "from internal.orchestrator.diagnosis_coordinator import DiagnosisCoordinator"),
        
        # 工具组件
        ("配置加载器", "from pkg.utils.config_loader import get_config"),
        ("指标收集器", "from pkg.utils.metrics import get_metrics_collector"),
        
        # gRPC 生成的代码
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

async def test_model_factory():
    """测试模型工厂功能"""
    print("\n🔍 测试模型工厂功能...")
    
    try:
        from internal.agent.model_factory import get_model_factory
        
        # 获取模型工厂实例
        factory = await get_model_factory()
        print("  ✓ 模型工厂实例创建成功")
        
        # 测试获取可用模型
        models = factory.get_available_models()
        print(f"  ✓ 获取可用模型: {len(models)} 个")
        
        # 测试健康状态
        health = factory.get_model_health_status()
        print(f"  ✓ 获取健康状态: {len(health)} 个模型")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 模型工厂测试失败: {e}")
        traceback.print_exc()
        return False

async def test_config_manager():
    """测试配置管理器功能"""
    print("\n🔍 测试配置管理器功能...")
    
    try:
        from internal.agent.model_config_manager import get_model_config_manager, ConfigScope
        
        # 获取配置管理器实例
        config_manager = await get_model_config_manager()
        print("  ✓ 配置管理器实例创建成功")
        
        # 测试列出系统配置
        system_configs = await config_manager.list_configs(ConfigScope.SYSTEM)
        print(f"  ✓ 获取系统配置: {len(system_configs)} 个")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 配置管理器测试失败: {e}")
        traceback.print_exc()
        return False

async def test_agent_manager():
    """测试智能体管理器功能"""
    print("\n🔍 测试智能体管理器功能...")
    
    try:
        from internal.agent.agent_manager import AgentManager
        
        # 创建智能体管理器实例
        agent_manager = AgentManager()
        print("  ✓ 智能体管理器实例创建成功")
        
        # 异步初始化
        await agent_manager.initialize()
        print("  ✓ 智能体管理器异步初始化成功")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 智能体管理器测试失败: {e}")
        traceback.print_exc()
        return False

def test_grpc_services():
    """测试 gRPC 服务组件"""
    print("\n🔍 测试 gRPC 服务组件...")
    
    try:
        from internal.delivery.xiaoai_service_impl import XiaoAIServiceImpl
        import api.grpc.xiaoai_service_pb2 as xiaoai_pb2
        import api.grpc.xiaoai_service_pb2_grpc as xiaoai_pb2_grpc
        
        # 创建服务实现实例
        service_impl = XiaoAIServiceImpl()
        print("  ✓ gRPC 服务实现创建成功")
        
        # 测试 protobuf 消息创建
        request = xiaoai_pb2.ChatRequest(
            user_id="test_user",
            message="测试消息",
            session_id="test_session"
        )
        print("  ✓ protobuf 消息创建成功")
        
        return True
        
    except Exception as e:
        print(f"  ❌ gRPC 服务测试失败: {e}")
        traceback.print_exc()
        return False

def test_server_startup():
    """测试服务器启动组件"""
    print("\n🔍 测试服务器启动组件...")
    
    try:
        from cmd.server import XiaoAIServer
        
        # 创建服务器实例（不启动）
        server = XiaoAIServer()
        print("  ✓ 服务器实例创建成功")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 服务器启动测试失败: {e}")
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("🚀 开始小艾服务完整集成测试\n")
    
    # 测试结果统计
    test_results = []
    
    # 1. 测试导入
    test_results.append(("导入测试", test_imports()))
    
    # 2. 测试模型工厂
    test_results.append(("模型工厂", await test_model_factory()))
    
    # 3. 测试配置管理器
    test_results.append(("配置管理器", await test_config_manager()))
    
    # 4. 测试智能体管理器
    test_results.append(("智能体管理器", await test_agent_manager()))
    
    # 5. 测试 gRPC 服务
    test_results.append(("gRPC 服务", test_grpc_services()))
    
    # 6. 测试服务器启动
    test_results.append(("服务器启动", test_server_startup()))
    
    # 输出测试结果摘要
    print("\n" + "="*50)
    print("📋 测试结果摘要:")
    print("="*50)
    
    success_count = 0
    for test_name, result in test_results:
        status = "✓ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            success_count += 1
    
    total_tests = len(test_results)
    success_rate = (success_count / total_tests) * 100
    
    print(f"\n📊 总体结果: {success_count}/{total_tests} 测试通过 ({success_rate:.1f}%)")
    
    if success_count == total_tests:
        print("🎉 所有测试通过！小艾服务集成完成度良好。")
    else:
        print("⚠️  部分测试失败，需要进一步修复。")
    
    # 输出开发完成度评估
    print("\n" + "="*50)
    print("📈 开发完成度评估:")
    print("="*50)
    
    if success_rate >= 90:
        print("🟢 开发完成度: 优秀 (90%+)")
        print("   - 核心功能已完成")
        print("   - 可以进行部署测试")
    elif success_rate >= 75:
        print("🟡 开发完成度: 良好 (75-90%)")
        print("   - 主要功能已完成")
        print("   - 需要修复少量问题")
    elif success_rate >= 50:
        print("🟠 开发完成度: 中等 (50-75%)")
        print("   - 基础功能已完成")
        print("   - 需要完善多个组件")
    else:
        print("🔴 开发完成度: 较低 (<50%)")
        print("   - 需要大量开发工作")
        print("   - 建议优先修复核心问题")

if __name__ == "__main__":
    asyncio.run(main()) 