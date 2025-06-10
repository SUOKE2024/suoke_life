#!/usr/bin/env python3
"""
基本导入测试
"""

def test_basic_imports():
    """测试基本模块导入"""
    try:
        # 测试异常模块
        from suoke_blockchain_service.exceptions import BlockchainServiceError
        print("✓ 异常模块导入成功")

        # 测试基本异常创建
        error = BlockchainServiceError("Test error")
        print(f"✓ 异常创建成功: {error}")

        print("🎉 基本导入测试完成!")
        return True

    except Exception as e:
        print(f"❌ 导入测试失败: {e}")
        return False

if __name__ == "__main__":
    test_basic_imports()
