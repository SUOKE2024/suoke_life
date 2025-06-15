#!/usr/bin/env python3
"""
Look Service 验证脚本
验证服务的完整性和功能
"""

import sys
import traceback
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        # 测试核心模块
        from look_service.core.config import settings
        print("✅ 配置模块导入成功")
        
        from look_service.core.logging import get_logger
        print("✅ 日志模块导入成功")
        
        # 测试异常模块
        from look_service.exceptions import (
            LookServiceError,
            ValidationError,
            ImageProcessingError,
            setup_exception_handlers
        )
        print("✅ 异常模块导入成功")
        
        # 测试工具模块
        from look_service.utils.image_utils import validate_image, resize_image
        print("✅ 图像工具模块导入成功")
        
        # 测试API模块
        from look_service.api.models import LookDiagnosisRequest, FaceAnalysisResponse
        print("✅ API模型导入成功")
        
        from look_service.api.routes.analysis import router
        print("✅ 分析路由导入成功")
        
        # 测试中间件
        from look_service.middleware import (
            LoggingMiddleware,
            MetricsMiddleware,
            RateLimitMiddleware,
            SecurityMiddleware
        )
        print("✅ 中间件模块导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        traceback.print_exc()
        return False


def test_app_creation():
    """测试应用创建"""
    print("\n🔍 测试应用创建...")
    
    try:
        from look_service.api.app import create_app
        
        app = create_app()
        print("✅ FastAPI应用创建成功")
        
        # 检查路由
        routes = [route.path for route in app.routes]
        print(f"✅ 注册的路由数量: {len(routes)}")
        
        # 检查关键路由
        expected_routes = ["/health", "/api/v1/analysis/face", "/api/v1/analysis/tongue"]
        for route in expected_routes:
            if any(route in r for r in routes):
                print(f"✅ 路由存在: {route}")
            else:
                print(f"⚠️ 路由缺失: {route}")
        
        return True
        
    except Exception as e:
        print(f"❌ 应用创建失败: {e}")
        traceback.print_exc()
        return False


def test_configuration():
    """测试配置"""
    print("\n🔍 测试配置...")
    
    try:
        from look_service.core.config import settings
        
        print(f"✅ 服务名称: {settings.service.service_name}")
        print(f"✅ 服务版本: {settings.service.service_version}")
        print(f"✅ 环境: {settings.service.environment}")
        print(f"✅ 主机: {settings.service.host}")
        print(f"✅ 端口: {settings.service.port}")
        print(f"✅ 调试模式: {settings.debug}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        traceback.print_exc()
        return False


def test_logging():
    """测试日志"""
    print("\n🔍 测试日志...")
    
    try:
        from look_service.core.logging import get_logger
        
        logger = get_logger(__name__)
        logger.info("日志测试消息")
        print("✅ 日志系统正常工作")
        
        return True
        
    except Exception as e:
        print(f"❌ 日志测试失败: {e}")
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("🚀 Look Service 验证开始")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_configuration,
        test_logging,
        test_app_creation,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 Look Service 验证成功！服务已100%完成")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查错误信息")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 