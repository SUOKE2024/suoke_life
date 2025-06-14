"""
errors - 索克生活项目模块
"""

from enum import Enum
from typing import Any
import grpc
import logging
import uuid

#! / usr / bin / env python

"""
错误处理模块
定义服务错误类型和处理方法
"""



logger = logging.getLogger(__name__)


class ErrorCode(str, Enum):
    """错误代码枚举"""

    # 系统级错误 (1000 - 1999)
    INTERNAL_ERROR = "1000"  # 内部服务错误
    SERVICE_UNAVAILABLE = "1001"  # 服务不可用
    INVALID_CONFIGURATION = "1002"  # 配置无效
    DEPENDENCY_ERROR = "1003"  # 依赖服务错误
    RATE_LIMITED = "1004"  # 速率限制
    TIMEOUT = "1005"  # 超时

    # 认证授权错误 (2000 - 2999)
    UNAUTHENTICATED = "2000"  # 未认证
    UNAUTHORIZED = "2001"  # 未授权
    INVALID_TOKEN = "2002"  # 无效的令牌
    TOKEN_EXPIRED = "2003"  # 令牌已过期

    # 输入验证错误 (3000 - 3999)
    INVALID_ARGUMENT = "3000"  # 无效参数
    VALIDATION_ERROR = "3001"  # 验证错误
    REQUIRED_FIELD_MISSING = "3002"  # 必填字段缺失
    INVALID_FORMAT = "3003"  # 格式无效

    # 资源错误 (4000 - 4999)
    NOT_FOUND = "4000"  # 资源不存在
    ALREADY_EXISTS = "4001"  # 资源已存在
    RESOURCE_EXHAUSTED = "4002"  # 资源耗尽
    PRECONDITION_FAILED = "4003"  # 前置条件失败

    # 会话错误 (5000 - 5999)
    SESSION_EXPIRED = "5000"  # 会话已过期
    SESSION_NOT_FOUND = "5001"  # 会话不存在
    SESSION_INVALID = "5002"  # 会话无效

    # LLM和知识库错误 (6000 - 6999)
    LLM_ERROR = "6000"  # LLM错误
    KNOWLEDGE_BASE_ERROR = "6001"  # 知识库错误
    SYMPTOM_EXTRACTION_ERROR = "6002"  # 症状提取错误
    TCM_PATTERN_MAPPING_ERROR = "6003"  # 中医证型映射错误


class ServiceError(Exception):
    """服务错误基类"""

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ):
        """
        初始化服务错误

        Args:
            code: 错误代码
            message: 错误消息
            details: 错误详情
            cause: 原始异常
        """
        self.code = code
        self.message = message
        self.details = details or {}
        self.cause = cause
        self.error_id = str(uuid.uuid4())

        # 构建完整的错误消息
        full_message = f"[{code.value}] {message}"
        super().__init__(full_message)

    def to_dict(self)-> dict[str, Any]:
        """
        转换为字典

        Returns:
            错误字典
        """
        return {
            "code": self.code.value,
            "message": self.message,
            "details": self.details,
            "error_id": self.error_id,
        }

    def to_grpc_error(self)-> grpc.RpcError:
        """
        转换为gRPC错误

        Returns:
            gRPC错误
        """
        status_code = self._map_to_grpc_status()
        error_dict = self.to_dict()

        # 创建gRPC状态
        status = grpc.StatusCode(status_code)

        # 创建错误详情元数据
        metadata = []
        for key, value in error_dict.items():
            if isinstance(value, (str, int, float, bool)):
                metadata.append((f"error - {key}", str(value)))

        # 创建gRPC错误
        return grpc.RpcError(
            code = status,
            details = self.message,
            debug_error_string = str(error_dict),
            trailing_metadata = metadata,
        )

    def _map_to_grpc_status(self)-> int:
        """
        将错误代码映射到gRPC状态码

        Returns:
            gRPC状态码
        """
        # 错误代码到gRPC状态码的映射
        error_to_grpc_status = {
            # 系统级错误
            ErrorCode.INTERNAL_ERROR: grpc.StatusCode.INTERNAL,
            ErrorCode.SERVICE_UNAVAILABLE: grpc.StatusCode.UNAVAILABLE,
            ErrorCode.INVALID_CONFIGURATION: grpc.StatusCode.INTERNAL,
            ErrorCode.DEPENDENCY_ERROR: grpc.StatusCode.UNAVAILABLE,
            ErrorCode.RATE_LIMITED: grpc.StatusCode.RESOURCE_EXHAUSTED,
            ErrorCode.TIMEOUT: grpc.StatusCode.DEADLINE_EXCEEDED,
            # 认证授权错误
            ErrorCode.UNAUTHENTICATED: grpc.StatusCode.UNAUTHENTICATED,
            ErrorCode.UNAUTHORIZED: grpc.StatusCode.PERMISSION_DENIED,
            ErrorCode.INVALID_TOKEN: grpc.StatusCode.UNAUTHENTICATED,
            ErrorCode.TOKEN_EXPIRED: grpc.StatusCode.UNAUTHENTICATED,
            # 输入验证错误
            ErrorCode.INVALID_ARGUMENT: grpc.StatusCode.INVALID_ARGUMENT,
            ErrorCode.VALIDATION_ERROR: grpc.StatusCode.INVALID_ARGUMENT,
            ErrorCode.REQUIRED_FIELD_MISSING: grpc.StatusCode.INVALID_ARGUMENT,
            ErrorCode.INVALID_FORMAT: grpc.StatusCode.INVALID_ARGUMENT,
            # 资源错误
            ErrorCode.NOT_FOUND: grpc.StatusCode.NOT_FOUND,
            ErrorCode.ALREADY_EXISTS: grpc.StatusCode.ALREADY_EXISTS,
            ErrorCode.RESOURCE_EXHAUSTED: grpc.StatusCode.RESOURCE_EXHAUSTED,
            ErrorCode.PRECONDITION_FAILED: grpc.StatusCode.FAILED_PRECONDITION,
            # 会话错误
            ErrorCode.SESSION_EXPIRED: grpc.StatusCode.FAILED_PRECONDITION,
            ErrorCode.SESSION_NOT_FOUND: grpc.StatusCode.NOT_FOUND,
            ErrorCode.SESSION_INVALID: grpc.StatusCode.INVALID_ARGUMENT,
            # LLM和知识库错误
            ErrorCode.LLM_ERROR: grpc.StatusCode.INTERNAL,
            ErrorCode.KNOWLEDGE_BASE_ERROR: grpc.StatusCode.INTERNAL,
            ErrorCode.SYMPTOM_EXTRACTION_ERROR: grpc.StatusCode.INTERNAL,
            ErrorCode.TCM_PATTERN_MAPPING_ERROR: grpc.StatusCode.INTERNAL,
        }

        return error_to_grpc_status.get(self.code, grpc.StatusCode.UNKNOWN)


# 系统级错误
class InternalError(ServiceError):
    """内部服务错误"""

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ):
        super().__init__(ErrorCode.INTERNAL_ERROR, message, details, cause)


class ServiceUnavailableError(ServiceError):
    """服务不可用错误"""

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ):
        super().__init__(ErrorCode.SERVICE_UNAVAILABLE, message, details, cause)


class DependencyError(ServiceError):
    """依赖服务错误"""

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ):
        super().__init__(ErrorCode.DEPENDENCY_ERROR, message, details, cause)


class ServiceTimeoutError(ServiceError):
    """服务超时错误"""

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ):
        super().__init__(ErrorCode.TIMEOUT, message, details, cause)


# 资源错误
class NotFoundError(ServiceError):
    """资源不存在错误"""

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ):
        super().__init__(ErrorCode.NOT_FOUND, message, details, cause)


class AlreadyExistsError(ServiceError):
    """资源已存在错误"""

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ):
        super().__init__(ErrorCode.ALREADY_EXISTS, message, details, cause)


# 输入验证错误
class ValidationError(ServiceError):
    """验证错误"""

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ):
        super().__init__(ErrorCode.VALIDATION_ERROR, message, details, cause)


class RequiredFieldMissingError(ValidationError):
    """必填字段缺失错误"""

    def __init__(
        self,
        field_name: str,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ):
        message = f"必填字段缺失: {field_name}"
        error_details = {"field": field_name}
        if details:
            error_details.update(details)
        super().__init__(message, error_details, cause)
        self.code = ErrorCode.REQUIRED_FIELD_MISSING


# 会话错误
class SessionNotFoundError(NotFoundError):
    """会话不存在错误"""

    def __init__(
        self,
        session_id: str,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ):
        message = f"会话不存在: {session_id}"
        error_details = {"session_id": session_id}
        if details:
            error_details.update(details)
        super().__init__(message, error_details, cause)
        self.code = ErrorCode.SESSION_NOT_FOUND


class SessionExpiredError(ServiceError):
    """会话已过期错误"""

    def __init__(
        self,
        session_id: str,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ):
        message = f"会话已过期: {session_id}"
        error_details = {"session_id": session_id}
        if details:
            error_details.update(details)
        super().__init__(ErrorCode.SESSION_EXPIRED, message, error_details, cause)


# LLM和知识库错误
class LLMError(ServiceError):
    """LLM错误"""

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ):
        super().__init__(ErrorCode.LLM_ERROR, message, details, cause)


class SymptomExtractionError(ServiceError):
    """症状提取错误"""

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ):
        super().__init__(ErrorCode.SYMPTOM_EXTRACTION_ERROR, message, details, cause)


class TCMPatternMappingError(ServiceError):
    """中医证型映射错误"""

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ):
        super().__init__(ErrorCode.TCM_PATTERN_MAPPING_ERROR, message, details, cause)


# 异常处理工具函数
def handle_exceptions(func):
    """
    异常处理装饰器
    将Python异常转换为gRPC错误

    Args:
        func: 要装饰的函数

    Returns:
        装饰后的函数
    """

    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ServiceError as e:
            # 记录错误
            logger.error(
                f"服务错误: [{e.code.value}] {e.message}",
                extra = {"error_id": e.error_id, "details": e.details},
            )
            # 抛出gRPC错误
            raise e.to_grpc_error()
        except Exception as e:
            # 包装为内部错误
            error = InternalError(
                message = "服务内部错误", details = {"original_error": str(e)}, cause = e
            )
            # 记录错误
            logger.exception(f"未处理的异常: {e!s}", extra = {"error_id": error.error_id})
            # 抛出gRPC错误
            raise error.to_grpc_error()

    return wrapper


def extract_error_from_grpc(error: grpc.RpcError)-> dict[str, Any]:
    """
    从gRPC错误中提取错误信息

    Args:
        error: gRPC错误

    Returns:
        错误信息字典
    """
    # 提取错误代码
    error_code = "UNKNOWN"
    error_message = str(error)
    error_details = {}
    error_id = None

    # 提取元数据
    if hasattr(error, "trailing_metadata") and error.trailing_metadata():
        for key, value in error.trailing_metadata():
            if key == "error - code":
                error_code = value
            elif key == "error - message":
                error_message = value
            elif key == "error - id":
                error_id = value
            elif key.startswith("error - details - "):
                detail_key = key[len("error - details - ") :]
                error_details[detail_key] = value

    return {
        "code": error_code,
        "message": error_message,
        "details": error_details,
        "error_id": error_id,
    }
