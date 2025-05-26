#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek集成测试脚本
测试真实的DeepSeek API集成
"""

import sys
import os
import asyncio
import traceback

# 添加项目路径
sys.path.append('.')

# 设置环境变量
os.environ['DEEPSEEK_API_KEY'] = 'sk-26ac526b8c3b41c2a39bd80a156aaa68'

def test_environment_setup():
    """测试环境设置"""
    print("🔍 测试环境设置...")
    
    # 检查API密钥
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    if api_key:
        print(f"  ✓ DeepSeek API密钥已设置: {api_key[:10]}...")
    else:
        print("  ❌ DeepSeek API密钥未设置")
        return False
    
    # 检查openai库
    try:
        import openai
        print(f"  ✓ OpenAI库版本: {openai.__version__}")
    except ImportError:
        print("  ❌ OpenAI库未安装")
        return False
    
    return True

async def test_deepseek_model_factory():
    """测试DeepSeek模型工厂"""
    print("\n🔍 测试DeepSeek模型工厂...")
    
    try:
        from internal.agent.deepseek_model_factory import get_deepseek_model_factory
        
        # 获取DeepSeek模型工厂实例
        factory = await get_deepseek_model_factory()
        print("  ✓ DeepSeek模型工厂实例创建成功")
        
        # 测试获取可用模型
        models = factory.get_available_models()
        print(f"  ✓ 获取可用模型: {models}")
        
        # 测试健康状态
        health = factory.get_model_health_status()
        print(f"  ✓ 获取健康状态: {health}")
        
        # 测试简单文本生成
        print("  🔄 测试文本生成...")
        response, metadata = await factory.generate_text(
            "deepseek-chat", 
            "你好，请简单介绍一下中医的基本理论。"
        )
        print(f"  ✓ 文本生成成功:")
        print(f"    响应: {response[:100]}...")
        print(f"    耗时: {metadata.get('processing_time', 0):.2f}秒")
        print(f"    Token使用: {metadata.get('usage', {})}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ DeepSeek模型工厂测试失败: {e}")
        traceback.print_exc()
        return False

async def test_chat_completion():
    """测试聊天完成功能"""
    print("\n🔍 测试聊天完成功能...")
    
    try:
        from internal.agent.deepseek_model_factory import get_deepseek_model_factory
        
        factory = await get_deepseek_model_factory()
        
        # 测试聊天对话
        messages = [
            {"role": "system", "content": "你是小艾，索克生活APP的中医健康助手。"},
            {"role": "user", "content": "我最近经常感到疲劳，从中医角度应该如何调理？"}
        ]
        
        print("  🔄 发送聊天请求...")
        response, metadata = await factory.generate_chat_completion(
            "deepseek-chat",
            messages,
            temperature=0.7,
            max_tokens=1024
        )
        
        print(f"  ✓ 聊天完成成功:")
        print(f"    响应: {response[:200]}...")
        print(f"    耗时: {metadata.get('processing_time', 0):.2f}秒")
        print(f"    Token使用: {metadata.get('usage', {})}")
        print(f"    置信度: {metadata.get('confidence', 0)}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 聊天完成测试失败: {e}")
        traceback.print_exc()
        return False

async def test_health_analysis():
    """测试健康分析功能"""
    print("\n🔍 测试健康分析功能...")
    
    try:
        from internal.agent.deepseek_model_factory import get_deepseek_model_factory
        
        factory = await get_deepseek_model_factory()
        
        # 测试健康分析
        symptoms = ["疲劳", "失眠", "食欲不振"]
        context = {"age": 30, "gender": "女"}
        
        print("  🔄 进行健康分析...")
        analysis = await factory.health_analysis(symptoms, context)
        
        print(f"  ✓ 健康分析成功:")
        print(f"    原始分析: {analysis['raw_analysis'][:200]}...")
        print(f"    证候分析: {analysis['syndrome_analysis']}")
        print(f"    体质类型: {analysis['constitution_type']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 健康分析测试失败: {e}")
        traceback.print_exc()
        return False

async def test_agent_manager_integration():
    """测试智能体管理器集成"""
    print("\n🔍 测试智能体管理器集成...")
    
    try:
        # 临时修改配置以使用生产环境
        from pkg.utils.config_loader import get_config
        config = get_config("config/prod.yaml")
        
        from internal.agent.agent_manager import AgentManager
        
        # 创建智能体管理器
        agent_manager = AgentManager()
        print("  ✓ 智能体管理器实例创建成功")
        
        # 异步初始化
        await agent_manager.initialize()
        print("  ✓ 智能体管理器初始化成功")
        
        # 测试聊天功能
        print("  🔄 测试聊天功能...")
        chat_response = await agent_manager.chat(
            user_id="test_user_deepseek",
            message="你好，我想了解一下中医养生的基本原则。",
            session_id="test_deepseek_session"
        )
        
        print(f"  ✓ 聊天测试成功:")
        print(f"    响应: {chat_response['message'][:200]}...")
        print(f"    置信度: {chat_response['confidence']}")
        print(f"    模型: {chat_response['metadata'].get('model', 'unknown')}")
        print(f"    提供商: {chat_response['metadata'].get('provider', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 智能体管理器集成测试失败: {e}")
        traceback.print_exc()
        return False

async def test_configuration_loading():
    """测试配置加载"""
    print("\n🔍 测试配置加载...")
    
    try:
        from pkg.utils.config_loader import ConfigLoader
        
        # 测试生产环境配置
        config = ConfigLoader("config/prod.yaml")
        
        # 检查DeepSeek配置
        deepseek_config = config.get_section('models.deepseek')
        print(f"  ✓ DeepSeek配置: {deepseek_config}")
        
        # 检查LLM配置
        llm_config = config.get_section('models.llm')
        print(f"  ✓ LLM配置: primary_model={llm_config.get('primary_model')}")
        
        # 检查开发环境配置
        dev_config = config.get_section('development')
        print(f"  ✓ 开发环境配置: mock_services={dev_config.get('mock_services')}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 配置加载测试失败: {e}")
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("🚀 开始DeepSeek集成测试\n")
    
    # 测试结果统计
    test_results = []
    
    # 1. 测试环境设置
    test_results.append(("环境设置", test_environment_setup()))
    
    # 2. 测试配置加载
    test_results.append(("配置加载", await test_configuration_loading()))
    
    # 3. 测试DeepSeek模型工厂
    test_results.append(("DeepSeek模型工厂", await test_deepseek_model_factory()))
    
    # 4. 测试聊天完成
    test_results.append(("聊天完成", await test_chat_completion()))
    
    # 5. 测试健康分析
    test_results.append(("健康分析", await test_health_analysis()))
    
    # 6. 测试智能体管理器集成
    test_results.append(("智能体管理器集成", await test_agent_manager_integration()))
    
    # 输出测试结果摘要
    print("\n" + "="*60)
    print("📋 DeepSeek集成测试结果摘要:")
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
        print("🎉 DeepSeek集成测试基本通过！")
        completion_level = "高"
    elif success_rate >= 60:
        print("⚠️  DeepSeek集成测试部分通过，需要进一步优化。")
        completion_level = "中"
    else:
        print("🔴 DeepSeek集成测试失败较多，需要大量修复工作。")
        completion_level = "低"
    
    print("\n" + "="*60)
    print("📈 DeepSeek集成完成度评估:")
    print("="*60)
    print(f"🔵 集成完成度: {completion_level} ({success_rate:.1f}%)")
    
    if success_rate < 100:
        print("   - 建议检查API密钥配置")
        print("   - 确保网络连接正常")
        print("   - 检查DeepSeek API服务状态")
        print("   - 验证配置文件格式正确")
    
    print("\n🔗 DeepSeek API文档: https://platform.deepseek.com/api-docs/")
    print("💡 如需帮助，请查看日志文件或联系技术支持")

if __name__ == "__main__":
    asyncio.run(main()) 