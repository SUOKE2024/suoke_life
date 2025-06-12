#!/usr/bin/env python3
"""老克智能体服务启动测试脚本"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_imports():
    """测试模块导入"""
    print("📦 测试模块导入...")

    try:
        # 测试基本依赖
        import fastapi
        import pydantic
        import uvicorn

        print("✅ FastAPI相关依赖导入成功")

        import loguru
        import yaml

        print("✅ 日志和配置依赖导入成功")

        import aiohttp
        import openai

        print("✅ AI和HTTP依赖导入成功")

        return True

    except ImportError as e:
        print(f"❌ 依赖导入失败: {e}")
        return False


def test_config():
    """测试配置加载"""
    print("⚙️  测试配置加载...")

    try:
        from laoke_service.core.config import get_config

        config = get_config()
        print(f"✅ 配置加载成功: {config.service.name}")
        return True

    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False


def test_agent():
    """测试智能体创建"""
    print("🤖 测试智能体创建...")

    try:
        from laoke_service.core.agent import get_agent

        agent = get_agent()
        print(f"✅ 智能体创建成功")
        return True

    except Exception as e:
        print(f"❌ 智能体创建失败: {e}")
        return False


def test_api():
    """测试API创建"""
    print("🔗 测试API创建...")

    try:
        from laoke_service.api.routes import app

        print(f"✅ API应用创建成功")
        return True

    except Exception as e:
        print(f"❌ API应用创建失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 老克智能体服务启动测试")
    print("=" * 50)

    # 设置环境变量
    os.environ["SERVICE__ENVIRONMENT"] = "development"
    # os.environ["SERVICE__DEBUG"] = "true"  # 测试环境可选

    tests = [test_imports, test_config, test_agent, test_api]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")

    if passed == total:
        print("✅ 所有测试通过，服务可以正常启动！")
        return True
    else:
        print("❌ 部分测试失败，请检查依赖和配置")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
