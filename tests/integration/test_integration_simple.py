"""
test_integration_simple - 索克生活项目模块
"""

import aiohttp
import asyncio

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的无障碍服务集成测试
"""


async def test_simple_integration():
    """简化的集成测试"""
    print("🔍 开始简化的无障碍服务集成测试...")

    base_url = "http://localhost:50051"

    async with aiohttp.ClientSession() as session:
        try:
            # 测试健康检查
            print("🏥 测试健康检查...")
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ 健康检查成功: {data}")
                else:
                    print(f"   ❌ 健康检查失败: {response.status}")
                    return False

            # 测试根端点
            print("🏠 测试根端点...")
            async with session.get(f"{base_url}/") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ 根端点成功: {data}")
                else:
                    print(f"   ❌ 根端点失败: {response.status}")
                    return False

            # 测试API端点
            print("🔧 测试API端点...")
            async with session.get(f"{base_url}/api/v1/accessibility/test") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ API端点成功: {data}")
                    print(f"   📋 支持的功能: {', '.join(data.get('features', []))}")
                else:
                    print(f"   ❌ API端点失败: {response.status}")
                    return False

            print("🎉 所有简化集成测试通过！")
            return True

        except Exception as e:
            print(f"❌ 集成测试失败: {e}")
            return False

async def main():
    """主函数"""
    success = await test_simple_integration()

    if success:
        print("\n📊 测试总结:")
        print("✅ 无障碍服务基础功能正常")
        print("✅ HTTP API端点可访问")
        print("✅ 健康检查通过")
        print("✅ 服务状态良好")

        print("\n🔄 下一步:")
        print("• 完善缺失的模块文件")
        print("• 实现完整的gRPC服务")
        print("• 集成小艾智能体客户端")
        print("• 添加更多无障碍功能")
    else:
        print("\n❌ 测试失败，需要进一步调试")

if __name__ == "__main__":
    asyncio.run(main())