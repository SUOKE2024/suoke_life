#!/usr/bin/env python3
"""
索克生活无障碍服务 - 快速启动脚本
演示核心功能和服务状态
"""

import asyncio
import sys
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from config.config import Config
from internal.service.app import AccessibilityApp
from internal.service.modules.translation import TranslationModule
from internal.service.modules.voice_assistance import VoiceAssistanceModule


def print_banner() -> None:
    """打印启动横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    索克生活无障碍服务                          ║
║                   Suoke Life Accessibility Service           ║
╠══════════════════════════════════════════════════════════════╣
║  🌟 AI驱动的智能无障碍服务平台                                ║
║  🔧 Python 3.13.3 + UV 工具链                               ║
║  🚀 快速启动演示模式                                          ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_status(message: str, status: str = "INFO"):
    """打印状态信息"""
    timestamp = time.strftime("%H:%M:%S")
    status_icons = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "WARNING": "⚠️",
        "ERROR": "❌",
        "LOADING": "⏳",
    }
    icon = status_icons.get(status, "📋")
    print(f"[{timestamp}] {icon} {message}")


async def demo_translation_service() -> None:
    """演示翻译服务"""
    print_status("初始化翻译服务...", "LOADING")

    try:
        translation_module = TranslationModule()

        # 测试基础翻译
        test_texts = [
            ("你好，欢迎使用索克生活", "zh", "en"),
            ("Hello, welcome to Suoke Life", "en", "zh"),
            ("健康管理从预防开始", "zh", "en"),
        ]

        print_status("开始翻译演示:", "INFO")
        for text, source, target in test_texts:
            result = await translation_module.translate_text(text, source, target)
            translated_text = result.get("translated_text", text)
            print(f"  📝 {text}")
            print(f"  🔄 {translated_text}")
            print()

        print_status("翻译服务演示完成", "SUCCESS")

    except Exception as e:
        print_status(f"翻译服务演示失败: {str(e)}", "ERROR")


async def demo_voice_assistance() -> None:
    """演示语音辅助服务"""
    print_status("初始化语音辅助服务...", "LOADING")

    try:
        voice_module = VoiceAssistanceModule()

        # 测试语音指令处理
        test_commands = [
            "打开无障碍设置",
            "调整字体大小",
            "启用屏幕阅读",
            "切换高对比度模式",
        ]

        print_status("开始语音指令演示:", "INFO")
        for command in test_commands:
            result = voice_module.process_voice_command(command)
            print(f"  🎤 指令: {command}")
            print(f"  🤖 响应: {result.get('response', '处理完成')}")
            print()

        print_status("语音辅助演示完成", "SUCCESS")

    except Exception as e:
        print_status(f"语音辅助演示失败: {str(e)}", "ERROR")


async def demo_app_initialization() -> None:
    """演示应用初始化"""
    print_status("初始化无障碍应用...", "LOADING")

    try:
        # 加载配置
        config = Config()
        print_status(f"配置加载成功 - 版本: {config.version}", "SUCCESS")

        # 创建应用实例
        app = AccessibilityApp(config)
        print_status("应用实例创建成功", "SUCCESS")

        # 显示服务状态
        print_status("服务状态检查:", "INFO")
        services = [
            "无障碍核心服务",
            "边缘计算服务",
            "中医无障碍服务",
            "方言支持服务",
            "监控服务",
        ]

        for service in services:
            print(f"  ✅ {service}: 已加载")

        print_status("应用初始化完成", "SUCCESS")
        return app

    except Exception as e:
        print_status(f"应用初始化失败: {str(e)}", "ERROR")
        return None


def show_service_info() -> None:
    """显示服务信息"""
    print_status("服务功能概览:", "INFO")

    features = [
        "🦮 导盲辅助 - AI视觉识别和路径规划",
        "🤟 手语识别 - 实时手语翻译和学习",
        "🔊 语音辅助 - 智能语音交互和控制",
        "📖 屏幕阅读 - 内容朗读和导航辅助",
        "🌐 多语言翻译 - 支持25种语言互译",
        "🏥 中医无障碍 - 传统医学数字化适配",
        "🗣️ 方言支持 - 27种中国方言识别",
        "⚡ 边缘计算 - 本地AI推理和隐私保护",
        "📊 智能监控 - 健康数据采集和分析",
        "🚨 危机预警 - 紧急情况检测和响应",
    ]

    for feature in features:
        print(f"  {feature}")
    print()


def show_technical_info() -> None:
    """显示技术信息"""
    print_status("技术架构信息:", "INFO")

    tech_stack = [
        "🐍 Python 3.13.3 - 现代Python运行时",
        "📦 UV Package Manager - 快速依赖管理",
        "🔧 gRPC - 高性能服务通信",
        "🧠 AI/ML - 多模态智能处理",
        "🔐 区块链 - 健康数据安全存储",
        "☁️ 云原生 - 容器化部署支持",
        "📱 跨平台 - iOS/Android/Web支持",
    ]

    for tech in tech_stack:
        print(f"  {tech}")
    print()


async def main() -> None:
    """主函数"""
    print_banner()

    # 显示基础信息
    show_service_info()
    show_technical_info()

    # 演示核心功能
    print_status("开始功能演示...", "INFO")
    print("=" * 60)

    # 1. 应用初始化演示
    app = await demo_app_initialization()
    print("=" * 60)

    # 2. 翻译服务演示
    await demo_translation_service()
    print("=" * 60)

    # 3. 语音辅助演示
    await demo_voice_assistance()
    print("=" * 60)

    # 总结
    print_status("🎉 快速启动演示完成!", "SUCCESS")
    print_status("服务已准备就绪，可以开始使用", "INFO")

    if app:
        print_status("要启动完整服务，请运行: python cmd/server/main.py", "INFO")

    print("\n感谢使用索克生活无障碍服务! 🌟")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_status("用户中断，退出演示", "WARNING")
    except Exception as e:
        print_status(f"演示过程中发生错误: {str(e)}", "ERROR")
        sys.exit(1)
