"""
test_exceptions - 索克生活项目模块
"""

from suoke_blockchain_service.exceptions import (
from suoke_blockchain_service.models import DataType
import pytest

"""
异常处理测试

测试增强的异常处理功能。
"""

    BlockchainServiceError,
    ValidationError,
    NotFoundError,
    PermissionError,
    IntegrationError,
    ContractError,
    TransactionError,
    EncryptionError,
    ZKProofError,
    IPFSError,
    DatabaseError,
    ConfigurationError,
    RateLimitError,
    TimeoutError,
    validate_required_fields,
    validate_field_type,
    validate_field_length,
    validate_enum_value
)


class TestEnhancedExceptions:
    """测试增强的异常类"""

    def test_blockchain_service_error_basic(self):
        """测试基础异常"""
        error = BlockchainServiceError("测试错误")
        assert str(error) == "测试错误"
        assert error.message == "测试错误"
        assert error.error_code is None
        assert error.details == {}

    def test_blockchain_service_error_with_details(self):
        """测试带详细信息的异常"""
        details = {"key": "value", "number": 123}
        error = BlockchainServiceError(
            "测试错误",
            error_code="TEST_ERROR",
            details=details
        )
        
        assert error.error_code == "TEST_ERROR"
        assert error.details == details
        
        error_dict = error.to_dict()
        assert error_dict["error"] == "BlockchainServiceError"
        assert error_dict["message"] == "测试错误"
        assert error_dict["error_code"] == "TEST_ERROR"
        assert error_dict["details"] == details

    def test_validation_error(self):
        """测试验证异常"""
        error = ValidationError(
            "字段验证失败",
            field="user_id",
            value="invalid_value"
        )
        
        assert error.error_code == "VALIDATION_ERROR"
        assert error.field == "user_id"
        assert error.value == "invalid_value"
        assert error.details["field"] == "user_id"
        assert error.details["value"] == "invalid_value"

    def test_not_found_error(self):
        """测试未找到异常"""
        error = NotFoundError(
            "资源未找到",
            resource_type="health_record",
            resource_id="123456"
        )
        
        assert error.error_code == "NOT_FOUND"
        assert error.resource_type == "health_record"
        assert error.resource_id == "123456"
        assert error.details["resource_type"] == "health_record"
        assert error.details["resource_id"] == "123456"

    def test_permission_error(self):
        """测试权限异常"""
        error = PermissionError(
            "权限不足",
            user_id="user123",
            required_permission="read"
        )
        
        assert error.error_code == "PERMISSION_DENIED"
        assert error.user_id == "user123"
        assert error.required_permission == "read"

    def test_integration_error(self):
        """测试集成异常"""
        error = IntegrationError(
            "外部服务调用失败",
            service="ipfs",
            operation="upload"
        )
        
        assert error.error_code == "INTEGRATION_ERROR"
        assert error.service == "ipfs"
        assert error.operation == "upload"

    def test_contract_error(self):
        """测试合约异常"""
        error = ContractError(
            "智能合约调用失败",
            contract_address="0x123456789",
            function_name="storeHealthData"
        )
        
        assert error.error_code == "CONTRACT_ERROR"
        assert error.contract_address == "0x123456789"
        assert error.function_name == "storeHealthData"

    def test_transaction_error(self):
        """测试交易异常"""
        error = TransactionError(
            "交易失败",
            transaction_hash="0xabcdef",
            block_number=12345
        )
        
        assert error.error_code == "TRANSACTION_ERROR"
        assert error.transaction_hash == "0xabcdef"
        assert error.block_number == 12345

    def test_encryption_error(self):
        """测试加密异常"""
        error = EncryptionError(
            "加密操作失败",
            operation="encrypt"
        )
        
        assert error.error_code == "ENCRYPTION_ERROR"
        assert error.operation == "encrypt"

    def test_zkproof_error(self):
        """测试零知识证明异常"""
        error = ZKProofError(
            "证明生成失败",
            circuit="health_data",
            proof_type="groth16"
        )
        
        assert error.error_code == "ZK_PROOF_ERROR"
        assert error.circuit == "health_data"
        assert error.proof_type == "groth16"

    def test_ipfs_error(self):
        """测试IPFS异常"""
        error = IPFSError(
            "IPFS操作失败",
            ipfs_hash="QmTestHash",
            operation="upload"
        )
        
        assert error.error_code == "IPFS_ERROR"
        assert error.ipfs_hash == "QmTestHash"
        assert error.operation == "upload"

    def test_database_error(self):
        """测试数据库异常"""
        error = DatabaseError(
            "数据库操作失败",
            table="health_records",
            operation="insert"
        )
        
        assert error.error_code == "DATABASE_ERROR"
        assert error.table == "health_records"
        assert error.operation == "insert"

    def test_configuration_error(self):
        """测试配置异常"""
        error = ConfigurationError(
            "配置错误",
            config_key="database_url"
        )
        
        assert error.error_code == "CONFIGURATION_ERROR"
        assert error.config_key == "database_url"

    def test_rate_limit_error(self):
        """测试速率限制异常"""
        error = RateLimitError(
            "请求频率过高",
            limit=100,
            window=60,
            retry_after=30
        )
        
        assert error.error_code == "RATE_LIMIT_EXCEEDED"
        assert error.limit == 100
        assert error.window == 60
        assert error.retry_after == 30

    def test_timeout_error(self):
        """测试超时异常"""
        error = TimeoutError(
            "操作超时",
            timeout=30.0,
            operation="blockchain_call"
        )
        
        assert error.error_code == "TIMEOUT_ERROR"
        assert error.timeout == 30.0
        assert error.operation == "blockchain_call"


class TestValidationFunctions:
    """测试验证函数"""

    def test_validate_required_fields_success(self):
        """测试必需字段验证成功"""
        data = {
            "user_id": "user123",
            "data": {"heart_rate": 72},
            "data_type": "heart_rate"
        }
        required_fields = ["user_id", "data", "data_type"]
        
        # 不应该抛出异常
        validate_required_fields(data, required_fields)

    def test_validate_required_fields_missing(self):
        """测试必需字段缺失"""
        data = {
            "user_id": "user123",
            "data": {"heart_rate": 72}
            # 缺少 data_type
        }
        required_fields = ["user_id", "data", "data_type"]
        
        with pytest.raises(ValidationError) as exc_info:
            validate_required_fields(data, required_fields)
        
        error = exc_info.value
        assert "缺少必需字段" in error.message
        assert "data_type" in error.message
        assert "missing_fields" in error.details

    def test_validate_required_fields_empty_string(self):
        """测试空字符串字段"""
        data = {
            "user_id": "   ",  # 空白字符串
            "data": {"heart_rate": 72},
            "data_type": "heart_rate"
        }
        required_fields = ["user_id", "data", "data_type"]
        
        with pytest.raises(ValidationError) as exc_info:
            validate_required_fields(data, required_fields)
        
        error = exc_info.value
        assert "user_id" in error.details["missing_fields"]

    def test_validate_required_fields_none_value(self):
        """测试None值字段"""
        data = {
            "user_id": "user123",
            "data": None,  # None值
            "data_type": "heart_rate"
        }
        required_fields = ["user_id", "data", "data_type"]
        
        with pytest.raises(ValidationError) as exc_info:
            validate_required_fields(data, required_fields)
        
        error = exc_info.value
        assert "data" in error.details["missing_fields"]

    def test_validate_field_type_success(self):
        """测试字段类型验证成功"""
        # 不应该抛出异常
        validate_field_type("test_string", str, "test_field")
        validate_field_type(123, int, "number_field")
        validate_field_type({"key": "value"}, dict, "dict_field")

    def test_validate_field_type_failure(self):
        """测试字段类型验证失败"""
        with pytest.raises(ValidationError) as exc_info:
            validate_field_type(123, str, "string_field")
        
        error = exc_info.value
        assert "类型错误" in error.message
        assert error.field == "string_field"
        assert error.value == "123"

    def test_validate_field_length_success(self):
        """测试字段长度验证成功"""
        # 不应该抛出异常
        validate_field_length("short", 10, "test_field")
        validate_field_length("exactly_ten", 10, "test_field")

    def test_validate_field_length_failure(self):
        """测试字段长度验证失败"""
        with pytest.raises(ValidationError) as exc_info:
            validate_field_length("this_is_too_long", 5, "test_field")
        
        error = exc_info.value
        assert "长度超过限制" in error.message
        assert error.field == "test_field"

    def test_validate_enum_value_success(self):
        """测试枚举值验证成功"""
        # 不应该抛出异常
        validate_enum_value("heart_rate", DataType, "data_type")
        validate_enum_value("blood_pressure", DataType, "data_type")

    def test_validate_enum_value_failure(self):
        """测试枚举值验证失败"""
        with pytest.raises(ValidationError) as exc_info:
            validate_enum_value("invalid_type", DataType, "data_type")
        
        error = exc_info.value
        assert "值无效" in error.message
        assert error.field == "data_type"
        assert "valid_values" in error.details


class TestExceptionInheritance:
    """测试异常继承关系"""

    def test_all_exceptions_inherit_from_base(self):
        """测试所有异常都继承自基础异常"""
        exceptions = [
            ValidationError("test"),
            NotFoundError("test"),
            PermissionError("test"),
            IntegrationError("test"),
            ContractError("test"),
            TransactionError("test"),
            EncryptionError("test"),
            ZKProofError("test"),
            IPFSError("test"),
            DatabaseError("test"),
            ConfigurationError("test"),
            RateLimitError("test"),
            TimeoutError("test"),
        ]
        
        for exception in exceptions:
            assert isinstance(exception, BlockchainServiceError)
            assert isinstance(exception, Exception)

    def test_exception_error_codes(self):
        """测试异常错误代码"""
        error_codes = {
            ValidationError("test"): "VALIDATION_ERROR",
            NotFoundError("test"): "NOT_FOUND",
            PermissionError("test"): "PERMISSION_DENIED",
            IntegrationError("test"): "INTEGRATION_ERROR",
            ContractError("test"): "CONTRACT_ERROR",
            TransactionError("test"): "TRANSACTION_ERROR",
            EncryptionError("test"): "ENCRYPTION_ERROR",
            ZKProofError("test"): "ZK_PROOF_ERROR",
            IPFSError("test"): "IPFS_ERROR",
            DatabaseError("test"): "DATABASE_ERROR",
            ConfigurationError("test"): "CONFIGURATION_ERROR",
            RateLimitError("test"): "RATE_LIMIT_EXCEEDED",
            TimeoutError("test"): "TIMEOUT_ERROR",
        }
        
        for exception, expected_code in error_codes.items():
            assert exception.error_code == expected_code 