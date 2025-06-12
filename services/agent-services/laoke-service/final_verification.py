#!/usr/bin/env python3
"""
老克智能体服务最终验证脚本

这个脚本验证服务的所有核心功能是否正常工作：
1. 模块导入验证
2. 配置系统验证
3. 智能体功能验证
4. API接口验证
5. 无障碍服务验证
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ["SERVICE__ENVIRONMENT"] = "development"
# os.environ["SERVICE__DEBUG"] = "true"  # 验证环境可选
os.environ["MODELS__API_KEY"] = "sk-test-key-for-development"


class ServiceVerification:
    """服务验证类"""

    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0

    def add_result(self, test_name: str, success: bool, message: str = ""):
        """添加测试结果"""
        self.results.append({"test": test_name, "success": success, "message": message})
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            print(f"✅ {test_name}: {message}")
        else:
            print(f"❌ {test_name}: {message}")

    def test_imports(self):
        """测试模块导入"""
        print("\n📦 测试模块导入...")

        # 测试核心依赖
        try:
            import fastapi
            import httpx
            import loguru
            import openai
            import pydantic
            import uvicorn
            import yaml

            self.add_result("核心依赖导入", True, "所有核心依赖导入成功")
        except ImportError as e:
            self.add_result("核心依赖导入", False, f"依赖导入失败: {e}")
            return

        # 测试项目模块
        try:
            from laoke_service.api.routes import app
            from laoke_service.core.agent import LaokeAgent
            from laoke_service.core.config import Config, get_config
            from laoke_service.core.exceptions import LaokeServiceException
            from laoke_service.integrations.accessibility import AccessibilityClient

            self.add_result("项目模块导入", True, "所有项目模块导入成功")
        except ImportError as e:
            self.add_result("项目模块导入", False, f"项目模块导入失败: {e}")

    def test_config(self):
        """测试配置系统"""
        print("\n⚙️  测试配置系统...")

        try:
            from laoke_service.core.config import get_config

            config = get_config()

            # 验证配置结构
            assert hasattr(config, "service"), "缺少service配置"
            assert hasattr(config, "database"), "缺少database配置"
            assert hasattr(config, "agent"), "缺少agent配置"

            self.add_result("配置加载", True, f"配置加载成功: {config.service.name}")

            # 测试配置验证
            assert config.service.name == "laoke-service", "服务名称不正确"
            assert config.service.environment in [
                "development",
                "testing",
                "production",
            ], "环境配置无效"

            self.add_result("配置验证", True, "配置验证通过")

        except Exception as e:
            self.add_result("配置系统", False, f"配置系统测试失败: {e}")

    async def test_agent(self):
        """测试智能体功能"""
        print("\n🤖 测试智能体功能...")

        try:
            from laoke_service.core.agent import get_agent

            agent = get_agent()

            # 测试会话创建
            session_id = await agent.create_session("test_user")
            self.add_result("会话创建", True, f"会话创建成功: {session_id}")

            # 测试会话信息获取
            session_info = await agent.get_session_info(session_id)
            assert session_info is not None, "会话信息为空"
            assert session_info["session_id"] == session_id, "会话ID不匹配"
            self.add_result("会话信息", True, "会话信息获取成功")

            # 测试会话终止
            await agent.terminate_session(session_id)
            self.add_result("会话终止", True, "会话终止成功")

        except Exception as e:
            self.add_result("智能体功能", False, f"智能体测试失败: {e}")

    def test_api(self):
        """测试API接口"""
        print("\n🔗 测试API接口...")

        try:
            from fastapi.testclient import TestClient
            from laoke_service.api.routes import app

            client = TestClient(app)

            # 测试健康检查
            response = client.get("/health")
            assert response.status_code == 200, f"健康检查失败: {response.status_code}"
            self.add_result("健康检查", True, "健康检查接口正常")

            # 测试服务信息
            response = client.get("/info")
            assert (
                response.status_code == 200
            ), f"服务信息获取失败: {response.status_code}"
            data = response.json()
            assert "service_name" in data, "服务信息缺少service_name"
            self.add_result("服务信息", True, "服务信息接口正常")

            # 测试统计信息
            response = client.get("/stats")
            assert (
                response.status_code == 200
            ), f"统计信息获取失败: {response.status_code}"
            self.add_result("统计信息", True, "统计信息接口正常")

        except Exception as e:
            self.add_result("API接口", False, f"API测试失败: {e}")

    def test_accessibility(self):
        """测试无障碍服务"""
        print("\n♿ 测试无障碍服务...")

        try:
            from laoke_service.integrations.accessibility import (
                AccessibilityClient,
                AccessibilityFeature,
                AccessibilityProfile,
                STTRequest,
                TTSRequest,
            )

            # 测试类创建
            client = AccessibilityClient()
            self.add_result("无障碍客户端", True, "无障碍客户端创建成功")

            # 测试配置创建
            profile = AccessibilityProfile(
                user_id="test_user",
                enabled_features=[
                    AccessibilityFeature.TEXT_TO_SPEECH,
                    AccessibilityFeature.LARGE_TEXT,
                ],
                tts_preferences={"voice": "female_standard", "speed": "normal"},
                ui_preferences={"font_size_multiplier": 1.2, "high_contrast": False},
                navigation_preferences={
                    "screen_reader_compatible": True,
                    "simplified_interface": False,
                },
            )
            self.add_result("无障碍配置", True, "无障碍配置创建成功")

            # 测试请求对象创建
            tts_request = TTSRequest(text="测试文本", language="zh-CN")
            self.add_result("TTS请求", True, "TTS请求对象创建成功")

        except Exception as e:
            self.add_result("无障碍服务", False, f"无障碍服务测试失败: {e}")

    def test_file_structure(self):
        """测试文件结构"""
        print("\n📁 测试文件结构...")

        required_files = [
            "laoke_service/__init__.py",
            "laoke_service/core/__init__.py",
            "laoke_service/core/config.py",
            "laoke_service/core/agent.py",
            "laoke_service/core/exceptions.py",
            "laoke_service/core/logging.py",
            "laoke_service/api/__init__.py",
            "laoke_service/api/routes.py",
            "laoke_service/integrations/__init__.py",
            "laoke_service/integrations/accessibility.py",
            "config/config.yaml",
            "tests/test_agent.py",
            "tests/test_integration.py",
            "main.py",
            "pyproject.toml",
            "QUICKSTART.md",
            "PROJECT_COMPLETION_REPORT.md",
        ]

        missing_files = []
        for file_path in required_files:
            full_path = project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)

        if missing_files:
            self.add_result("文件结构", False, f"缺少文件: {', '.join(missing_files)}")
        else:
            self.add_result("文件结构", True, "所有必需文件存在")

    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 老克智能体服务最终验证")
        print("=" * 60)

        # 运行测试
        self.test_file_structure()
        self.test_imports()
        self.test_config()
        await self.test_agent()
        self.test_api()
        self.test_accessibility()

        # 输出结果
        print("\n" + "=" * 60)
        print(f"📊 测试结果: {self.passed_tests}/{self.total_tests} 通过")
        print(f"📈 完成度: {(self.passed_tests/self.total_tests)*100:.1f}%")

        if self.passed_tests == self.total_tests:
            print("\n🎉 所有测试通过！老克智能体服务已达到100%完成度")
            print("✅ 服务已准备好投入生产使用")
            return True
        else:
            print(f"\n⚠️  有 {self.total_tests - self.passed_tests} 个测试失败")
            print("❌ 请检查失败的测试项目")
            return False

    def print_summary(self):
        """打印详细摘要"""
        print("\n📋 详细测试报告:")
        print("-" * 40)
        for result in self.results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['message']}")


async def main():
    """主函数"""
    verifier = ServiceVerification()
    success = await verifier.run_all_tests()
    verifier.print_summary()

    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
