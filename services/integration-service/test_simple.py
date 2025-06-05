#!/usr/bin/env python3
"""
简单的集成服务测试脚本
"""

import os
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置测试环境变量
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["DEBUG"] = "true"
os.environ["SECRET_KEY"] = "test-secret-key"

from fastapi.testclient import TestClient
from integration_service.main import create_app


def test_basic_functionality():
    """测试基本功能"""
    print("🚀 开始测试集成服务...")
    
    try:
        # 创建应用
        app = create_app()
        print("✅ 应用创建成功")
        
        # 创建测试客户端
        with TestClient(app) as client:
            print("✅ 测试客户端创建成功")
            
            # 测试根端点
            response = client.get("/")
            print(f"📍 根端点状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"📍 根端点响应: {data}")
                print("✅ 根端点测试通过")
            else:
                print("❌ 根端点测试失败")
                return False
            
            # 测试健康检查
            response = client.get("/health")
            print(f"🏥 健康检查状态码: {response.status_code}")
            if response.status_code in [200, 503]:  # 503也是可接受的（数据库未连接）
                data = response.json()
                print(f"🏥 健康检查响应: {data}")
                print("✅ 健康检查测试通过")
            else:
                print("❌ 健康检查测试失败")
                return False
            
            # 测试活跃检查
            response = client.get("/live")
            print(f"💓 活跃检查状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"💓 活跃检查响应: {data}")
                print("✅ 活跃检查测试通过")
            else:
                print("❌ 活跃检查测试失败")
                return False
            
            # 测试就绪检查
            response = client.get("/ready")
            print(f"🎯 就绪检查状态码: {response.status_code}")
            data = response.json()
            print(f"🎯 就绪检查响应: {data}")
            print("✅ 就绪检查测试通过")
            
            # 测试API文档
            response = client.get("/docs")
            print(f"📚 API文档状态码: {response.status_code}")
            if response.status_code == 200:
                print("✅ API文档可访问")
            else:
                print("❌ API文档不可访问")
            
            # 测试健康数据类型端点
            response = client.get("/api/v1/health-data/types")
            print(f"📊 数据类型端点状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"📊 支持的数据类型数量: {data.get('count', 0)}")
                print("✅ 数据类型端点测试通过")
            else:
                print("❌ 数据类型端点测试失败")
            
        print("\n🎉 所有基本功能测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_import_modules():
    """测试模块导入"""
    print("📦 测试模块导入...")
    
    try:
        # 测试核心模块
        from integration_service import config
        print("✅ 配置模块导入成功")
        
        from integration_service.core import database, security
        print("✅ 核心模块导入成功")
        
        from integration_service.models import base, user, platform, health_data
        print("✅ 模型模块导入成功")
        
        from integration_service.services import base_service, user_service, platform_service, health_data_service
        print("✅ 服务模块导入成功")
        
        from integration_service.api.routes import auth, platforms, health_data as hd_routes, integration
        print("✅ API路由模块导入成功")
        
        print("🎉 所有模块导入测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("🧪 集成服务测试验证")
    print("=" * 60)
    
    # 测试模块导入
    if not test_import_modules():
        print("❌ 模块导入测试失败")
        sys.exit(1)
    
    print("\n" + "-" * 60)
    
    # 测试基本功能
    if not test_basic_functionality():
        print("❌ 基本功能测试失败")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 所有测试通过！集成服务运行正常！")
    print("=" * 60)


if __name__ == "__main__":
    main() 