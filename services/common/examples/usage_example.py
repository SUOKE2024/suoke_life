#!/usr/bin/env python3
"""
索克生活通用组件库使用示例

演示如何在实际项目中使用suoke_common组件库
"""

import asyncio
import logging
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def basic_usage_example():
    """基本使用示例"""
    print("=" * 50)
    print("基本使用示例")
    print("=" * 50)
    
    try:
        from services.common.suoke_common import get_components, shutdown_components
        
        # 配置组件
        config = {
            "health": {
                "check_interval": 30,
                "timeout": 10
            },
            "observability": {
                "metrics": {"port": 8080},
                "logging": {"level": "INFO"}
            }
        }
        
        # 初始化组件
        print("🚀 初始化组件...")
        components = await get_components(config)
        
        # 列出已初始化的组件
        print("📋 已初始化的组件:")
        for component_name in components.list_components():
            print(f"  ✅ {component_name}")
        
        # 关闭组件
        print("🔄 关闭组件...")
        await shutdown_components()
        print("✅ 组件已关闭")
        
    except Exception as e:
        print(f"❌ 基本使用示例失败: {e}")
        import traceback
        traceback.print_exc()


async def health_check_example():
    """健康检查示例"""
    print("\n" + "=" * 50)
    print("健康检查示例")
    print("=" * 50)
    
    try:
        from services.common.suoke_common import get_health_checker
        
        # 获取健康检查器
        print("🏥 获取健康检查器...")
        health_checker = await get_health_checker()
        
        # 执行健康检查
        print("🔍 执行健康检查...")
        status = await health_checker.check()
        print(f"📊 健康状态: {status}")
        
    except Exception as e:
        print(f"❌ 健康检查示例失败: {e}")


async def component_test_example():
    """组件测试示例"""
    print("\n" + "=" * 50)
    print("组件测试示例")
    print("=" * 50)
    
    try:
        from services.common.suoke_common import SuokeCommonComponents
        
        # 创建组件管理器
        print("🔧 创建组件管理器...")
        components = SuokeCommonComponents()
        
        # 初始化组件（使用简单配置）
        simple_config = {
            "health": {"check_interval": 60}
        }
        
        print("⚙️ 初始化组件...")
        await components.initialize(simple_config)
        
        # 列出组件
        print("📋 已初始化的组件:")
        for component_name in components.list_components():
            print(f"  ✅ {component_name}")
        
        # 测试获取组件
        if components.list_components():
            first_component_name = components.list_components()[0]
            component = components.get_component(first_component_name)
            print(f"🎯 成功获取组件: {first_component_name}")
        
        # 关闭组件
        print("🔄 关闭组件...")
        await components.shutdown()
        print("✅ 组件已关闭")
        
    except Exception as e:
        print(f"❌ 组件测试示例失败: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """主函数"""
    print("🌿 索克生活通用组件库使用示例")
    print("=" * 60)
    
    # 运行示例
    await basic_usage_example()
    await health_check_example()
    await component_test_example()
    
    print("\n" + "=" * 60)
    print("🎉 示例执行完成！")
    print("📖 更多信息请参考: services/common/README.md")


if __name__ == "__main__":
    asyncio.run(main()) 