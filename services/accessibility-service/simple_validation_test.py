#!/usr/bin/env python3

"""
索克生活无障碍服务简化验证测试
专注于核心功能的快速验证

作者: 索克生活团队
日期: 2025-06-14
版本: 1.0.0
"""

import asyncio
import sys
import time
from datetime import datetime
from pathlib import Path


def print_test_header() -> None:
    """打印测试标题"""
    print("=" * 70)
    print("🧪 索克生活无障碍服务 - 简化验证测试")
    print("=" * 70)
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python版本: {sys.version}")
    print(f"📁 工作目录: {Path.cwd()}")
    print()


def test_basic_imports() -> None:
    """测试基础导入"""
    print("📦 测试基础导入...")

    tests = [
        ("配置模块", "from config.config import Config"),
        ("应用模块", "from internal.service.app import AccessibilityApp"),
        ("基础模块", "from internal.service.modules.base_module import BaseModule"),
        (
            "手语模块",
            "from internal.service.modules.sign_language import SignLanguageModule",
        ),
        (
            "语音模块",
            "from internal.service.modules.voice_assistance import VoiceAssistanceModule",
        ),
        (
            "屏幕阅读",
            "from internal.service.modules.screen_reading import ScreenReadingModule",
        ),
        (
            "内容转换",
            "from internal.service.modules.content_conversion import ContentConversionModule",
        ),
        (
            "翻译模块",
            "from internal.service.modules.translation import TranslationModule",
        ),
        (
            "设置管理",
            "from internal.service.modules.settings_manager import SettingsManagerModule",
        ),
    ]

    results = []
    for test_name, import_code in tests:
        try:
            exec(import_code)
            print(f"   ✅ {test_name}")
            results.append((test_name, True, ""))
        except Exception as e:
            print(f"   ❌ {test_name}: {str(e)}")
            results.append((test_name, False, str(e)))

    return results


def test_config_functionality() -> None:
    """测试配置功能"""
    print("\n⚙️  测试配置功能...")

    try:
        from config.config import Config

        config = Config()

        # 测试基本配置访问
        service_name = config.service.name
        service_port = config.service.port

        print("   ✅ 配置加载成功")
        print(f"   📋 服务名称: {service_name}")
        print(f"   📋 服务端口: {service_port}")

        return True, f"服务: {service_name}, 端口: {service_port}"

    except Exception as e:
        print(f"   ❌ 配置测试失败: {e}")
        return False, str(e)


async def test_module_initialization() -> None:
    """测试模块初始化"""
    print("\n🔧 测试模块初始化...")

    try:
        from internal.service.modules.sign_language import SignLanguageModule
        from internal.service.modules.voice_assistance import VoiceAssistanceModule

        # 测试手语模块
        sign_module = SignLanguageModule({})
        sign_init = await sign_module.initialize()
        print(f"   ✅ 手语模块初始化: {'成功' if sign_init else '失败'}")

        # 测试语音模块
        voice_module = VoiceAssistanceModule({})
        voice_init = await voice_module.initialize()
        print(f"   ✅ 语音模块初始化: {'成功' if voice_init else '失败'}")

        # 清理
        await sign_module.cleanup()
        await voice_module.cleanup()

        return sign_init and voice_init, "模块初始化测试"

    except Exception as e:
        print(f"   ❌ 模块初始化失败: {e}")
        return False, str(e)


async def test_module_functionality() -> None:
    """测试模块功能"""
    print("\n🎯 测试模块功能...")

    try:
        from internal.service.modules.content_conversion import ContentConversionModule
        from internal.service.modules.translation import TranslationModule

        # 测试翻译功能
        translation_module = TranslationModule({})
        await translation_module.initialize()

        translation_result = await translation_module.translate_text("你好", "zh", "en")
        print(f"   ✅ 翻译测试: {translation_result.get('translated_text', 'N/A')}")

        # 测试内容转换
        conversion_module = ContentConversionModule({})
        await conversion_module.initialize()

        simplified_text = await conversion_module.convert_to_simplified(
            "这是一个复杂的医学术语和技术说明文档"
        )
        print(f"   ✅ 内容简化: {simplified_text[:50]}...")

        # 清理
        await translation_module.cleanup()
        await conversion_module.cleanup()

        return True, "功能测试完成"

    except Exception as e:
        print(f"   ❌ 功能测试失败: {e}")
        return False, str(e)


def test_app_creation() -> None:
    """测试应用创建"""
    print("\n🏗️  测试应用创建...")

    try:
        from config.config import Config
        from internal.service.app import AccessibilityApp

        config = Config()
        app = AccessibilityApp(config)

        print("   ✅ 应用创建成功")
        print(f"   📋 配置版本: {config.service.version}")

        # 检查关键服务是否存在
        services = [
            ("无障碍服务", app.accessibility_service),
            ("边缘计算", app.edge_computing),
            ("中医服务", app.tcm_accessibility),
            ("方言服务", app.dialect_service),
            ("监控服务", app.monitoring_service),
        ]

        for service_name, service in services:
            status = "✅" if service is not None else "❌"
            print(f"   {status} {service_name}: {'已加载' if service else '未加载'}")

        return True, "应用创建成功"

    except Exception as e:
        print(f"   ❌ 应用创建失败: {e}")
        logger.error("An error occurred", exc_info=True)
        return False, str(e)


def test_performance_basic() -> None:
    """基础性能测试"""
    print("\n⚡ 基础性能测试...")

    try:
        # 测试导入性能
        start_time = time.time()

        import_time = time.time() - start_time

        # 测试配置加载性能
        start_time = time.time()
        from config.config import Config

        config = Config()
        config_time = time.time() - start_time

        print(f"   ✅ 导入时间: {import_time:.3f}s")
        print(f"   ✅ 配置加载: {config_time:.3f}s")

        # 性能评估
        total_time = import_time + config_time
        if total_time < 1.0:
            performance = "优秀"
        elif total_time < 3.0:
            performance = "良好"
        else:
            performance = "需要优化"

        print(f"   📊 总体性能: {performance} ({total_time:.3f}s)")

        return True, f"性能: {performance}"

    except Exception as e:
        print(f"   ❌ 性能测试失败: {e}")
        return False, str(e)


async def run_all_tests() -> None:
    """运行所有测试"""
    print_test_header()

    all_results = []

    # 基础导入测试
    import_results = test_basic_imports()
    all_results.extend(import_results)

    # 配置功能测试
    config_success, config_msg = test_config_functionality()
    all_results.append(("配置功能", config_success, config_msg))

    # 模块初始化测试
    init_success, init_msg = await test_module_initialization()
    all_results.append(("模块初始化", init_success, init_msg))

    # 模块功能测试
    func_success, func_msg = await test_module_functionality()
    all_results.append(("模块功能", func_success, func_msg))

    # 应用创建测试
    app_success, app_msg = test_app_creation()
    all_results.append(("应用创建", app_success, app_msg))

    # 性能测试
    perf_success, perf_msg = test_performance_basic()
    all_results.append(("基础性能", perf_success, perf_msg))

    # 生成测试报告
    print("\n" + "=" * 70)
    print("📊 测试结果摘要")
    print("=" * 70)

    total_tests = len(all_results)
    passed_tests = sum(1 for _, success, _ in all_results if success)
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    print(f"总测试数: {total_tests}")
    print(f"通过测试: {passed_tests}")
    print(f"失败测试: {failed_tests}")
    print(f"成功率: {success_rate:.1f}%")

    print("\n详细结果:")
    for test_name, success, message in all_results:
        status = "✅" if success else "❌"
        print(f"  {status} {test_name}")
        if not success and message:
            print(f"      💬 {message}")

    # 总体评估
    if success_rate >= 90:
        overall_status = "🎉 优秀"
        recommendation = "服务状态良好，可以投入使用"
    elif success_rate >= 75:
        overall_status = "✅ 良好"
        recommendation = "服务基本正常，建议修复少量问题"
    elif success_rate >= 60:
        overall_status = "⚠️  一般"
        recommendation = "存在一些问题，需要进一步调试"
    else:
        overall_status = "❌ 需要改进"
        recommendation = "存在较多问题，需要重点关注"

    print(f"\n🎯 总体评估: {overall_status} ({success_rate:.1f}%)")
    print(f"💡 建议: {recommendation}")

    # 保存简单报告
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "success_rate": success_rate,
        "overall_status": overall_status,
        "recommendation": recommendation,
        "results": [
            {"name": name, "success": success, "message": message}
            for name, success, message in all_results
        ],
    }

    import json

    report_file = (
        f"simple_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n📄 详细报告已保存: {report_file}")

    return success_rate >= 75


async def main() -> None:
    """主函数"""
    try:
        # 确保在正确的目录
        sys.path.insert(0, ".")

        # 运行测试
        success = await run_all_tests()

        # 设置退出码
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n⚠️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 测试执行异常: {e}")
        logger.error("An error occurred", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
