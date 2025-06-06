"""
exceptions - 索克生活项目模块
"""

    import functools
    import logging
from typing import Optional, Dict, Any

"""
区块链服务异常定义

定义服务中使用的各种异常类型。
"""



class BlockchainServiceError(Exception):
    """区块链服务基础异常"""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.cause = cause
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


class ValidationError(BlockchainServiceError):
    """数据验证异常"""
    
    def __init__(
        self, 
        message: str, 
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs
    ):
        super().__init__(message, error_code="VALIDATION_ERROR", **kwargs)
        self.field = field
        self.value = value
        if field:
            self.details["field"] = field
        if value is not None:
            self.details["value"] = str(value)


class NotFoundError(BlockchainServiceError):
    """资源未找到异常"""
    
    def __init__(
        self, 
        message: str, 
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="NOT_FOUND", **kwargs)
        self.resource_type = resource_type
        self.resource_id = resource_id
        if resource_type:
            self.details["resource_type"] = resource_type
        if resource_id:
            self.details["resource_id"] = resource_id


class PermissionError(BlockchainServiceError):
    """权限异常"""
    
    def __init__(
        self, 
        message: str, 
        user_id: Optional[str] = None,
        required_permission: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="PERMISSION_DENIED", **kwargs)
        self.user_id = user_id
        self.required_permission = required_permission
        if user_id:
            self.details["user_id"] = user_id
        if required_permission:
            self.details["required_permission"] = required_permission


class IntegrationError(BlockchainServiceError):
    """外部集成异常"""
    
    def __init__(
        self, 
        message: str, 
        service: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="INTEGRATION_ERROR", **kwargs)
        self.service = service
        self.operation = operation
        if service:
            self.details["service"] = service
        if operation:
            self.details["operation"] = operation


class ContractError(BlockchainServiceError):
    """智能合约错误"""
    
    def __init__(
        self, 
        message: str, 
        contract_address: Optional[str] = None,
        function_name: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="CONTRACT_ERROR", **kwargs)
        self.contract_address = contract_address
        self.function_name = function_name
        if contract_address:
            self.details["contract_address"] = contract_address
        if function_name:
            self.details["function_name"] = function_name


class TransactionError(BlockchainServiceError):
    """交易错误"""
    
    def __init__(
        self, 
        message: str, 
        transaction_hash: Optional[str] = None,
        block_number: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, error_code="TRANSACTION_ERROR", **kwargs)
        self.transaction_hash = transaction_hash
        self.block_number = block_number
        if transaction_hash:
            self.details["transaction_hash"] = transaction_hash
        if block_number:
            self.details["block_number"] = block_number


class EncryptionError(BlockchainServiceError):
    """加密相关异常"""
    
    def __init__(
        self, 
        message: str, 
        operation: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="ENCRYPTION_ERROR", **kwargs)
        self.operation = operation
        if operation:
            self.details["operation"] = operation


class ZKProofError(BlockchainServiceError):
    """零知识证明异常"""
    
    def __init__(
        self, 
        message: str, 
        circuit: Optional[str] = None,
        proof_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="ZK_PROOF_ERROR", **kwargs)
        self.circuit = circuit
        self.proof_type = proof_type
        if circuit:
            self.details["circuit"] = circuit
        if proof_type:
            self.details["proof_type"] = proof_type


class IPFSError(BlockchainServiceError):
    """IPFS操作异常"""
    
    def __init__(
        self, 
        message: str, 
        ipfs_hash: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="IPFS_ERROR", **kwargs)
        self.ipfs_hash = ipfs_hash
        self.operation = operation
        if ipfs_hash:
            self.details["ipfs_hash"] = ipfs_hash
        if operation:
            self.details["operation"] = operation


class DatabaseError(BlockchainServiceError):
    """数据库操作异常"""
    
    def __init__(
        self, 
        message: str, 
        table: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="DATABASE_ERROR", **kwargs)
        self.table = table
        self.operation = operation
        if table:
            self.details["table"] = table
        if operation:
            self.details["operation"] = operation


class ConfigurationError(BlockchainServiceError):
    """配置异常"""
    
    def __init__(
        self, 
        message: str, 
        config_key: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="CONFIGURATION_ERROR", **kwargs)
        self.config_key = config_key
        if config_key:
            self.details["config_key"] = config_key


class RateLimitError(BlockchainServiceError):
    """速率限制异常"""
    
    def __init__(
        self, 
        message: str, 
        limit: Optional[int] = None,
        window: Optional[int] = None,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, error_code="RATE_LIMIT_EXCEEDED", **kwargs)
        self.limit = limit
        self.window = window
        self.retry_after = retry_after
        if limit:
            self.details["limit"] = limit
        if window:
            self.details["window"] = window
        if retry_after:
            self.details["retry_after"] = retry_after


class TimeoutError(BlockchainServiceError):
    """超时异常"""
    
    def __init__(
        self, 
        message: str, 
        timeout: Optional[float] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="TIMEOUT_ERROR", **kwargs)
        self.timeout = timeout
        self.operation = operation
        if timeout:
            self.details["timeout"] = timeout
        if operation:
            self.details["operation"] = operation


def handle_exception(func):
    """异常处理装饰器"""
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except BlockchainServiceError:
            # 重新抛出已知的业务异常
            raise
        except Exception as e:
            # 包装未知异常
            logger = logging.getLogger(func.__module__)
            logger.error(f"未处理的异常在 {func.__name__}: {e}", exc_info=True)
            raise BlockchainServiceError(
                f"操作失败: {str(e)}",
                error_code="INTERNAL_ERROR",
                cause=e
            )
    
    return wrapper


def validate_required_fields(data: Dict[str, Any], required_fields: list) -> None:
    """验证必需字段"""
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)
        elif isinstance(data[field], str) and not data[field].strip():
            missing_fields.append(field)
    
    if missing_fields:
        raise ValidationError(
            f"缺少必需字段: {', '.join(missing_fields)}",
            details={"missing_fields": missing_fields}
        )


def validate_field_type(value: Any, expected_type: type, field_name: str) -> None:
    """验证字段类型"""
    if not isinstance(value, expected_type):
        raise ValidationError(
            f"字段 {field_name} 类型错误，期望 {expected_type.__name__}，实际 {type(value).__name__}",
            field=field_name,
            value=value
        )


def validate_field_length(value: str, max_length: int, field_name: str) -> None:
    """验证字段长度"""
    if len(value) > max_length:
        raise ValidationError(
            f"字段 {field_name} 长度超过限制，最大 {max_length}，实际 {len(value)}",
            field=field_name,
            value=value
        )


def validate_enum_value(value: Any, enum_class, field_name: str) -> None:
    """验证枚举值"""
    if value not in [e.value for e in enum_class]:
        valid_values = [e.value for e in enum_class]
        raise ValidationError(
            f"字段 {field_name} 值无效，有效值: {valid_values}",
            field=field_name,
            value=value,
            details={"valid_values": valid_values}
        ) 