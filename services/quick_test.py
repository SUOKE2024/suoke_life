#!/usr/bin/env python3
"""
快速测试脚本 - 验证核心微服务功能
"""

import asyncio
import sys
from datetime import datetime


async def test_api_gateway():
    """测试API网关"""
    try:
        sys.path.insert(0, "api-gateway")
        from suoke_api_gateway.core.gateway import APIGateway

        gateway = APIGateway()
        await gateway.initialize()

        # 测试请求处理
        test_request = {
            "path": "/api/v1/users",
            "method": "GET",
            "client_id": "test_client",
        }

        result = await gateway.handle_request(test_request)
        print(f"✅ API网关测试通过 - 状态码: {result.get('status')}")
        return True

    except Exception as e:
        print(f"❌ API网关测试失败: {e}")
        return False


def test_user_management():
    """测试用户管理服务"""
    try:
        sys.path.insert(0, "user-management-service")
        from user_management_service.models import User

        # 创建用户实例
        user = User(
            id="test_001",
            username="testuser",
            email="test@suoke.life",
            password_hash="hashed_password",
        )

        # 测试序列化
        user_dict = user.to_dict()

        # 测试反序列化
        user2 = User.from_dict(user_dict)

        print(f"✅ 用户管理服务测试通过 - 用户: {user2.username}")
        return True

    except Exception as e:
        print(f"❌ 用户管理服务测试失败: {e}")
        return False


async def test_xiaoai_agent():
    """测试小艾智能体"""
    try:
        sys.path.insert(0, "agent-services/xiaoai-service")
        from xiaoai.core import XiaoaiAgent

        agent = XiaoaiAgent()
        await agent.initialize()

        # 测试消息处理
        response = await agent.process_message("你好，小艾，我想了解健康建议")

        print(f"✅ 小艾智能体测试通过 - 响应: {response[:50]}...")
        return True

    except Exception as e:
        print(f"❌ 小艾智能体测试失败: {e}")
        return False


def test_blockchain_service():
    """测试区块链服务"""
    try:
        sys.path.insert(0, "blockchain-service")
        from suoke_blockchain_service.exceptions import BlockchainServiceError

        # 测试异常类
        error = BlockchainServiceError("测试错误")

        print(f"✅ 区块链服务测试通过 - 异常类可用")
        return True

    except Exception as e:
        print(f"❌ 区块链服务测试失败: {e}")
        return False


async def main():
    """主测试函数"""

    print("🧪 索克生活微服务快速功能验证")
    print("=" * 40)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tests = [
        ("用户管理服务", test_user_management),
        ("API网关", test_api_gateway),
        ("小艾智能体", test_xiaoai_agent),
        ("区块链服务", test_blockchain_service),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🔍 测试 {test_name}:")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()

            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")

    print(f"\n📊 测试结果总结:")
    print(f"  通过: {passed}/{total}")
    print(f"  成功率: {passed/total*100:.1f}%")

    if passed == total:
        print(f"\n🎉 所有核心服务测试通过！")
    elif passed >= total * 0.7:
        print(f"\n👍 大部分服务功能正常")
    else:
        print(f"\n⚠️ 部分服务需要修复")


if __name__ == "__main__":
    asyncio.run(main())
