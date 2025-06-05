"""
独立的异常处理测试，避免复杂依赖
"""
import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_basic_exception_classes():
    """测试基本异常类定义"""
    # 直接导入异常模块，避免通过__init__.py
    from suoke_blockchain_service.exceptions import (
        BlockchainServiceError,
        ValidationError,
        EncryptionError,
        BlockchainError,
        IPFSError,
        ZKPError,
        DatabaseError,
        ConfigurationError,
        RateLimitError,
        TimeoutError
    )
    
    # 测试基本异常类
    error = BlockchainServiceError("Test error")
    assert str(error) == "Test error"
    assert error.error_code == "BLOCKCHAIN_SERVICE_ERROR"
    
    # 测试带详细信息的异常
    validation_error = ValidationError(
        "Invalid data",
        error_code="INVALID_DATA",
        details={"field": "user_id", "value": ""}
    )
    assert validation_error.error_code == "INVALID_DATA"
    assert validation_error.details["field"] == "user_id"
    
    # 测试异常序列化
    error_dict = validation_error.to_dict()
    assert error_dict["error_code"] == "INVALID_DATA"
    assert error_dict["message"] == "Invalid data"
    assert error_dict["details"]["field"] == "user_id"

def test_validation_functions():
    """测试验证函数"""
    from suoke_blockchain_service.exceptions import (
        validate_required_fields,
        validate_field_type,
        validate_field_length,
        validate_enum_value,
        ValidationError
    )
    
    # 测试必填字段验证
    data = {"name": "test", "age": 25}
    validate_required_fields(data, ["name", "age"])  # 应该通过
    
    with pytest.raises(ValidationError):
        validate_required_fields(data, ["name", "email"])  # 缺少email
    
    # 测试类型验证
    validate_field_type("test", str, "name")  # 应该通过
    
    with pytest.raises(ValidationError):
        validate_field_type(123, str, "name")  # 类型错误
    
    # 测试长度验证
    validate_field_length("test", 1, 10, "name")  # 应该通过
    
    with pytest.raises(ValidationError):
        validate_field_length("", 1, 10, "name")  # 太短
    
    with pytest.raises(ValidationError):
        validate_field_length("a" * 20, 1, 10, "name")  # 太长
    
    # 测试枚举值验证
    validate_enum_value("active", ["active", "inactive"], "status")  # 应该通过
    
    with pytest.raises(ValidationError):
        validate_enum_value("unknown", ["active", "inactive"], "status")  # 无效值

def test_exception_inheritance():
    """测试异常继承关系"""
    from suoke_blockchain_service.exceptions import (
        BlockchainServiceError,
        ValidationError,
        EncryptionError
    )
    
    # 测试继承关系
    validation_error = ValidationError("Test")
    assert isinstance(validation_error, BlockchainServiceError)
    assert isinstance(validation_error, Exception)
    
    encryption_error = EncryptionError("Test")
    assert isinstance(encryption_error, BlockchainServiceError)
    assert isinstance(encryption_error, Exception)

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 