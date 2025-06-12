"""
增强错误处理机制
"""

import logging
import traceback
from functools import wraps
from typing import Any, Dict, Optional


class DiagnosticError(Exception):
    """诊断服务基础异常"""

    pass


class ValidationError(DiagnosticError):
    """数据验证异常"""

    pass


class ProcessingError(DiagnosticError):
    """处理异常"""

    pass


class ServiceUnavailableError(DiagnosticError):
    """服务不可用异常"""

    pass


def error_handler(func):
    """错误处理装饰器"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ValidationError as e:
            logging.error(f"Validation error in {func.__name__}: {e}")
            return {"error": "validation_error", "message": str(e)}
        except ProcessingError as e:
            logging.error(f"Processing error in {func.__name__}: {e}")
            return {"error": "processing_error", "message": str(e)}
        except ServiceUnavailableError as e:
            logging.error(f"Service unavailable in {func.__name__}: {e}")
            return {"error": "service_unavailable", "message": str(e)}
        except Exception as e:
            logging.error(f"Unexpected error in {func.__name__}: {e}")
            logging.error(traceback.format_exc())
            return {"error": "internal_error", "message": "Internal server error"}

    return wrapper


class ErrorHandler:
    """统一错误处理器"""

    @staticmethod
    def validate_input(data: Dict[str, Any]) -> None:
        """验证输入数据"""
        if not data:
            raise ValidationError("Input data cannot be empty")

        if "symptoms" not in data:
            raise ValidationError("Symptoms are required")

        if not isinstance(data["symptoms"], list):
            raise ValidationError("Symptoms must be a list")

        if len(data["symptoms"]) == 0:
            raise ValidationError("At least one symptom is required")

    @staticmethod
    def handle_processing_error(error: Exception, context: str) -> Dict[str, Any]:
        """处理处理错误"""
        logging.error(f"Processing error in {context}: {error}")
        return {"error": "processing_error", "context": context, "message": str(error)}

    @staticmethod
    def handle_service_error(service_name: str, error: Exception) -> Dict[str, Any]:
        """处理服务错误"""
        logging.error(f"Service error in {service_name}: {error}")
        return {
            "error": "service_error",
            "service": service_name,
            "message": str(error),
        }


# 测试错误处理
class TestErrorHandling:
    """错误处理测试"""

    def test_validation_errors(self):
        """测试验证错误"""
        handler = ErrorHandler()

        # 测试空数据
        try:
            handler.validate_input({})
            assert False, "Should raise ValidationError"
        except ValidationError as e:
            assert "empty" in str(e)

        # 测试缺少症状
        try:
            handler.validate_input({"patient": "test"})
            assert False, "Should raise ValidationError"
        except ValidationError as e:
            assert "required" in str(e)

    def test_error_handler_decorator(self):
        """测试错误处理装饰器"""

        @error_handler
        async def test_function():
            raise ValidationError("Test validation error")

        import asyncio

        result = asyncio.run(test_function())
        assert result["error"] == "validation_error"
        assert "Test validation error" in result["message"]
