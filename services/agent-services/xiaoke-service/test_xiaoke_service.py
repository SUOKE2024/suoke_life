#!/usr/bin/env python3
"""
小克智能体服务测试脚本

验证所有核心服务组件的基本功能。
"""

import asyncio
import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from xiaoke_service.services.database import DatabaseManager
from xiaoke_service.services.health import HealthChecker
from xiaoke_service.services.ai_service import AIService
from xiaoke_service.services.knowledge_service import KnowledgeService
from xiaoke_service.services.accessibility_service import AccessibilityService
from xiaoke_service.core.logging import get_logger

logger = get_logger(__name__)


async def test_database_service():
    """测试数据库服务"""
    print("🔍 测试数据库服务...")
    
    try:
        db_manager = DatabaseManager()
        await db_manager.initialize()
        
        # 测试健康检查
        health_status = await db_manager.health_check()
        print(f"  ✅ 数据库健康状态: {health_status}")
        
        await db_manager.close()
        print("  ✅ 数据库服务测试通过")
        return True
        
    except Exception as e:
        print(f"  ❌ 数据库服务测试失败: {e}")
        return False


async def test_health_service():
    """测试健康检查服务"""
    print("🔍 测试健康检查服务...")
    
    try:
        health_checker = HealthChecker()
        await health_checker.initialize()
        
        # 测试基础健康检查
        basic_health = await health_checker.check_basic()
        print(f"  ✅ 基础健康检查: {basic_health['status']}")
        
        # 测试系统资源检查
        system_health = await health_checker.check_system_resources()
        print(f"  ✅ 系统资源检查: CPU {system_health['cpu']['usage_percent']:.1f}%")
        
        await health_checker.close()
        print("  ✅ 健康检查服务测试通过")
        return True
        
    except Exception as e:
        print(f"  ❌ 健康检查服务测试失败: {e}")
        return False


async def test_ai_service():
    """测试AI服务"""
    print("🔍 测试AI服务...")
    
    try:
        ai_service = AIService()
        await ai_service.initialize()
        
        # 测试聊天完成
        messages = [
            {"role": "user", "content": "你好，我是用户，请介绍一下你自己。"}
        ]
        
        response = await ai_service.chat_completion(
            messages=messages,
            session_id="test_session"
        )
        
        print(f"  ✅ AI聊天响应: {response.content[:50]}...")
        print(f"  ✅ 处理时间: {response.processing_time:.2f}秒")
        
        # 测试健康数据分析
        analysis = await ai_service.analyze_health_data(
            symptoms=["疲劳", "失眠"],
            constitution_data={"type": "气虚质"},
            lifestyle_data={"exercise": "少", "diet": "不规律"}
        )
        
        print(f"  ✅ 健康分析: {analysis['tcm_diagnosis']['syndrome']}")
        
        await ai_service.close()
        print("  ✅ AI服务测试通过")
        return True
        
    except Exception as e:
        print(f"  ❌ AI服务测试失败: {e}")
        return False


async def test_knowledge_service():
    """测试知识库服务"""
    print("🔍 测试知识库服务...")
    
    try:
        knowledge_service = KnowledgeService()
        await knowledge_service.initialize()
        
        # 测试搜索功能
        search_result = await knowledge_service.search(
            query="气血两虚",
            limit=3
        )
        
        print(f"  ✅ 搜索结果: 找到 {len(search_result.items)} 条相关知识")
        print(f"  ✅ 搜索时间: {search_result.search_time:.3f}秒")
        
        if search_result.items:
            first_item = search_result.items[0]
            print(f"  ✅ 第一条结果: {first_item.title}")
        
        # 测试分类获取
        categories = await knowledge_service.get_categories()
        print(f"  ✅ 知识分类: {len(categories)} 个分类")
        
        # 测试统计信息
        stats = await knowledge_service.get_statistics()
        print(f"  ✅ 知识库统计: {stats['total_items']} 条知识")
        
        await knowledge_service.close()
        print("  ✅ 知识库服务测试通过")
        return True
        
    except Exception as e:
        print(f"  ❌ 知识库服务测试失败: {e}")
        return False


async def test_accessibility_service():
    """测试无障碍服务"""
    print("🔍 测试无障碍服务...")
    
    try:
        accessibility_service = AccessibilityService()
        await accessibility_service.initialize()
        
        # 测试文本转语音
        tts_result = await accessibility_service.text_to_speech(
            text="您好，我是小克，很高兴为您服务。",
            output_format="wav"
        )
        
        print(f"  ✅ TTS转换: 生成 {len(tts_result.audio_data)} 字节音频")
        print(f"  ✅ 音频时长: {tts_result.duration:.1f}秒")
        
        # 测试语音转文本
        mock_audio = b"mock_audio_data_for_testing"
        asr_result = await accessibility_service.speech_to_text(
            audio_data=mock_audio,
            language="zh-CN"
        )
        
        print(f"  ✅ ASR转写: {asr_result.text}")
        print(f"  ✅ 置信度: {asr_result.confidence:.2f}")
        
        # 测试支持的语言
        languages = await accessibility_service.get_supported_languages()
        print(f"  ✅ 支持语言: {len(languages)} 种")
        
        # 测试语音配置
        voice_profiles = await accessibility_service.get_voice_profiles()
        print(f"  ✅ 语音配置: {len(voice_profiles)} 个")
        
        await accessibility_service.close()
        print("  ✅ 无障碍服务测试通过")
        return True
        
    except Exception as e:
        print(f"  ❌ 无障碍服务测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("🚀 开始测试小克智能体服务...")
    print("=" * 50)
    
    start_time = time.time()
    test_results = []
    
    # 运行所有测试
    tests = [
        ("数据库服务", test_database_service),
        ("健康检查服务", test_health_service),
        ("AI服务", test_ai_service),
        ("知识库服务", test_knowledge_service),
        ("无障碍服务", test_accessibility_service),
    ]
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name}测试异常: {e}")
            test_results.append((test_name, False))
        
        print()  # 空行分隔
    
    # 汇总结果
    print("=" * 50)
    print("📊 测试结果汇总:")
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        
        if result:
            passed += 1
        else:
            failed += 1
    
    total_time = time.time() - start_time
    
    print(f"\n📈 测试统计:")
    print(f"  总测试数: {len(test_results)}")
    print(f"  通过: {passed}")
    print(f"  失败: {failed}")
    print(f"  成功率: {passed/len(test_results)*100:.1f}%")
    print(f"  总耗时: {total_time:.2f}秒")
    
    if failed == 0:
        print("\n🎉 所有测试通过！小克智能体服务运行正常。")
        return 0
    else:
        print(f"\n⚠️  有 {failed} 个测试失败，请检查相关服务。")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 测试过程中发生异常: {e}")
        sys.exit(1) 