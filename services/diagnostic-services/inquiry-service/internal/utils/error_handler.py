"""
全局错误处理器 - 统一的错误处理和异常管理
"""

import asyncio
from datetime import datetime
from enum import Enum
import json
import logging
import traceback
from typing import Any

logger = logging.getLogger(__name__)


class ErrorCode(Enum):
    """错误代码枚举"""

    # 通用错误 (1000-1999)
    UNKNOWN_ERROR = 1000
    INVALID_REQUEST = 1001
    MISSING_PARAMETER = 1002
    INVALID_PARAMETER = 1003
    PERMISSION_DENIED = 1004
    RATE_LIMIT_EXCEEDED = 1005

    # 会话相关错误 (2000-2999)
    SESSION_NOT_FOUND = 2000
    SESSION_EXPIRED = 2001
    SESSION_LIMIT_EXCEEDED = 2002
    INVALID_SESSION_STATE = 2003
    SESSION_CREATION_FAILED = 2004

    # 用户交互错误 (3000-3999)
    EMPTY_MESSAGE = 3000
    MESSAGE_TOO_LONG = 3001
    UNSUPPORTED_MESSAGE_TYPE = 3002
    MESSAGE_PROCESSING_FAILED = 3003

    # LLM服务错误 (4000-4999)
    LLM_SERVICE_UNAVAILABLE = 4000
    LLM_REQUEST_TIMEOUT = 4001
    LLM_RESPONSE_INVALID = 4002
    LLM_QUOTA_EXCEEDED = 4003

    # 症状提取错误 (5000-5999)
    SYMPTOM_EXTRACTION_FAILED = 5000
    NO_SYMPTOMS_DETECTED = 5001
    SYMPTOM_CONFIDENCE_TOO_LOW = 5002

    # 中医证型映射错误 (6000-6999)
    TCM_MAPPING_FAILED = 6000
    NO_PATTERNS_MATCHED = 6001
    PATTERN_CONFIDENCE_TOO_LOW = 6002

    # 数据库错误 (7000-7999)
    DATABASE_CONNECTION_FAILED = 7000
    DATABASE_QUERY_FAILED = 7001
    DATABASE_TRANSACTION_FAILED = 7002
    DATA_NOT_FOUND = 7003
    DATA_INTEGRITY_ERROR = 7004

    # 缓存错误 (8000-8999)
    CACHE_CONNECTION_FAILED = 8000
    CACHE_OPERATION_FAILED = 8001

    # 外部服务错误 (9000-9999)
    EXTERNAL_SERVICE_UNAVAILABLE = 9000
    EXTERNAL_SERVICE_TIMEOUT = 9001
    EXTERNAL_SERVICE_ERROR = 9002


class InquiryServiceError(Exception):
    """问诊服务基础异常类"""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.cause = cause
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {
            "error_code": self.error_code.value,
            "error_name": self.error_code.name,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "cause": str(self.cause) if self.cause else None
        }


class ErrorHandler:
    """全局错误处理器"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化错误处理器
        
        Args:
            config: 配置信息
        """
        self.config = config
        self.error_config = config.get("error_handling", {})

        # 错误处理配置
        self.enable_detailed_errors = self.error_config.get("enable_detailed_errors", True)
        self.log_stack_trace = self.error_config.get("log_stack_trace", True)
        self.max_error_details_length = self.error_config.get("max_error_details_length", 1000)

        # 错误统计
        self.error_counts = {}
        self.last_errors = []
        self.max_last_errors = self.error_config.get("max_last_errors", 100)

        logger.info("错误处理器初始化完成")

    def handle_error(
        self,
        error: Exception,
        context: dict[str, Any] | None = None,
        user_friendly: bool = True
    ) -> dict[str, Any]:
        """
        处理错误
        
        Args:
            error: 异常对象
            context: 错误上下文
            user_friendly: 是否返回用户友好的错误信息
            
        Returns:
            Dict: 错误响应
        """
        try:
            # 记录错误统计
            error_type = type(error).__name__
            self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

            # 创建错误记录
            error_record = {
                "error_type": error_type,
                "message": str(error),
                "timestamp": datetime.utcnow().isoformat(),
                "context": context or {}
            }

            # 处理不同类型的错误
            if isinstance(error, InquiryServiceError):
                response = self._handle_service_error(error, context)
            elif isinstance(error, asyncio.TimeoutError):
                response = self._handle_timeout_error(error, context)
            elif isinstance(error, ConnectionError):
                response = self._handle_connection_error(error, context)
            elif isinstance(error, ValueError):
                response = self._handle_value_error(error, context)
            elif isinstance(error, KeyError):
                response = self._handle_key_error(error, context)
            else:
                response = self._handle_unknown_error(error, context)

            # 记录错误日志
            self._log_error(error, context, response)

            # 保存最近的错误
            self._save_recent_error(error_record)

            # 返回用户友好的错误信息
            if user_friendly:
                response = self._make_user_friendly(response)

            return response

        except Exception as handler_error:
            logger.error(f"错误处理器本身发生错误: {handler_error}")
            return self._get_fallback_error_response()

    def _handle_service_error(
        self,
        error: InquiryServiceError,
        context: dict[str, Any] | None
    ) -> dict[str, Any]:
        """处理服务错误"""
        return {
            "success": False,
            "error_code": error.error_code.value,
            "error_name": error.error_code.name,
            "error_message": error.message,
            "details": error.details,
            "timestamp": error.timestamp.isoformat(),
            "context": context
        }

    def _handle_timeout_error(
        self,
        error: asyncio.TimeoutError,
        context: dict[str, Any] | None
    ) -> dict[str, Any]:
        """处理超时错误"""
        return {
            "success": False,
            "error_code": ErrorCode.LLM_REQUEST_TIMEOUT.value,
            "error_name": ErrorCode.LLM_REQUEST_TIMEOUT.name,
            "error_message": "请求超时，请稍后重试",
            "details": {"timeout_context": context},
            "timestamp": datetime.utcnow().isoformat()
        }

    def _handle_connection_error(
        self,
        error: ConnectionError,
        context: dict[str, Any] | None
    ) -> dict[str, Any]:
        """处理连接错误"""
        return {
            "success": False,
            "error_code": ErrorCode.EXTERNAL_SERVICE_UNAVAILABLE.value,
            "error_name": ErrorCode.EXTERNAL_SERVICE_UNAVAILABLE.name,
            "error_message": "服务暂时不可用，请稍后重试",
            "details": {"connection_error": str(error)},
            "timestamp": datetime.utcnow().isoformat()
        }

    def _handle_value_error(
        self,
        error: ValueError,
        context: dict[str, Any] | None
    ) -> dict[str, Any]:
        """处理值错误"""
        return {
            "success": False,
            "error_code": ErrorCode.INVALID_PARAMETER.value,
            "error_name": ErrorCode.INVALID_PARAMETER.name,
            "error_message": "参数值无效",
            "details": {"value_error": str(error), "context": context},
            "timestamp": datetime.utcnow().isoformat()
        }

    def _handle_key_error(
        self,
        error: KeyError,
        context: dict[str, Any] | None
    ) -> dict[str, Any]:
        """处理键错误"""
        return {
            "success": False,
            "error_code": ErrorCode.MISSING_PARAMETER.value,
            "error_name": ErrorCode.MISSING_PARAMETER.name,
            "error_message": f"缺少必需的参数: {error!s}",
            "details": {"missing_key": str(error), "context": context},
            "timestamp": datetime.utcnow().isoformat()
        }

    def _handle_unknown_error(
        self,
        error: Exception,
        context: dict[str, Any] | None
    ) -> dict[str, Any]:
        """处理未知错误"""
        return {
            "success": False,
            "error_code": ErrorCode.UNKNOWN_ERROR.value,
            "error_name": ErrorCode.UNKNOWN_ERROR.name,
            "error_message": "系统内部错误，请联系技术支持",
            "details": {
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    def _log_error(
        self,
        error: Exception,
        context: dict[str, Any] | None,
        response: dict[str, Any]
    ) -> None:
        """记录错误日志"""
        try:
            log_message = f"错误处理: {type(error).__name__}: {error!s}"

            if context:
                log_message += f" | 上下文: {json.dumps(context, ensure_ascii=False)}"

            # 记录堆栈跟踪
            if self.log_stack_trace:
                stack_trace = traceback.format_exc()
                logger.error(f"{log_message}\n堆栈跟踪:\n{stack_trace}")
            else:
                logger.error(log_message)

        except Exception as log_error:
            logger.error(f"记录错误日志失败: {log_error}")

    def _save_recent_error(self, error_record: dict[str, Any]) -> None:
        """保存最近的错误记录"""
        try:
            self.last_errors.append(error_record)

            # 保持最大数量限制
            if len(self.last_errors) > self.max_last_errors:
                self.last_errors = self.last_errors[-self.max_last_errors:]

        except Exception as save_error:
            logger.error(f"保存错误记录失败: {save_error}")

    def _make_user_friendly(self, response: dict[str, Any]) -> dict[str, Any]:
        """生成用户友好的错误信息"""
        if not self.enable_detailed_errors:
            # 隐藏详细错误信息
            response = {
                "success": False,
                "error_message": "服务暂时不可用，请稍后重试",
                "timestamp": response.get("timestamp")
            }
        # 限制错误详情长度
        elif "details" in response and isinstance(response["details"], dict):
            details_str = json.dumps(response["details"], ensure_ascii=False)
            if len(details_str) > self.max_error_details_length:
                response["details"] = {"truncated": True, "message": "详细信息过长，已截断"}

        return response

    def _get_fallback_error_response(self) -> dict[str, Any]:
        """获取后备错误响应"""
        return {
            "success": False,
            "error_code": ErrorCode.UNKNOWN_ERROR.value,
            "error_message": "系统发生未知错误",
            "timestamp": datetime.utcnow().isoformat()
        }

    def get_error_statistics(self) -> dict[str, Any]:
        """获取错误统计信息"""
        return {
            "error_counts": self.error_counts.copy(),
            "total_errors": sum(self.error_counts.values()),
            "recent_errors_count": len(self.last_errors),
            "most_common_errors": sorted(
                self.error_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }


def create_service_error(
    message: str,
    error_code: ErrorCode,
    details: dict[str, Any] | None = None,
    cause: Exception | None = None
) -> InquiryServiceError:
    """创建服务错误"""
    return InquiryServiceError(message, error_code, details, cause)


def validate_required_params(params: dict[str, Any], required_keys: list) -> None:
    """验证必需参数"""
    missing_keys = [key for key in required_keys if key not in params or params[key] is None]
    if missing_keys:
        raise InquiryServiceError(
            f"缺少必需的参数: {', '.join(missing_keys)}",
            ErrorCode.MISSING_PARAMETER,
            {"missing_keys": missing_keys}
        )
