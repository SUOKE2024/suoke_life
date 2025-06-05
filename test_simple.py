#!/usr/bin/env python3
"""
简单的异常模块测试脚本
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, '.')

def test_exceptions():
    """测试异常模块"""
    try:
        # 直接导入异常模块
        from suoke_blockchain_service.exceptions import (
            BlockchainServiceError, 
            ValidationError,
            validate_required_fields,
            validate_field_type
        )
        print("✓ 成功导入异常类")
        
        # 测试基本异常
        error = BlockchainServiceError("Test error")
        print(f"✓ 异常消息: {error}")
        print(f"✓ 错误代码: {error.error_code}")
        
        # 测试带详细信息的异常
        validation_error = ValidationError(
            "Invalid data",
            error_code="INVALID_DATA",
            details={"field": "user_id"}
        )
        print(f"✓ 验证错误: {validation_error.error_code}")
        
        # 测试异常序列化
        error_dict = validation_error.to_dict()
        print(f"✓ 异常序列化: {error_dict}")
        
        # 测试验证函数
        data = {"name": "test", "age": 25}
        validate_required_fields(data, ["name", "age"])
        print("✓ 必填字段验证通过")
        
        validate_field_type("test", str, "name")
        print("✓ 类型验证通过")
        
        print("\n🎉 所有异常测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_exceptions()
    sys.exit(0 if success else 1) 