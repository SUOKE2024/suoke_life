"""
算诊服务异常模块
索克生活 - 传统中医算诊微服务
"""

from typing import Any


class CalculationError(Exception):
    """算诊计算异常基类"""

    def __init__(
        self,
        message: str,
        error_code: str = "CALC_ERROR",
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(CalculationError):
    """数据验证异常"""

    def __init__(
        self, message: str, field: str = "", details: dict[str, Any] | None = None
    ):
        super().__init__(message, "VALIDATION_ERROR", details)
        self.field = field


class InvalidBirthInfoError(ValidationError):
    """无效出生信息异常"""

    def __init__(
        self, message: str, field: str = "", details: dict[str, Any] | None = None
    ):
        super().__init__(message, field, details)
        self.error_code = "INVALID_BIRTH_INFO"


class InvalidTimeError(ValidationError):
    """无效时间异常"""

    def __init__(
        self, message: str, field: str = "", details: dict[str, Any] | None = None
    ):
        super().__init__(message, field, details)
        self.error_code = "INVALID_TIME"


class ConfigurationError(CalculationError):
    """配置异常"""

    def __init__(
        self, message: str, config_key: str = "", details: dict[str, Any] | None = None
    ):
        super().__init__(message, "CONFIG_ERROR", details)
        self.config_key = config_key


class AlgorithmError(CalculationError):
    """算法计算异常"""

    def __init__(
        self, message: str, algorithm: str = "", details: dict[str, Any] | None = None
    ):
        super().__init__(message, "ALGORITHM_ERROR", details)
        self.algorithm = algorithm


class CacheError(CalculationError):
    """缓存异常"""

    def __init__(
        self, message: str, cache_key: str = "", details: dict[str, Any] | None = None
    ):
        super().__init__(message, "CACHE_ERROR", details)
        self.cache_key = cache_key


# 导出所有异常类
__all__ = [
    "CalculationError",
    "ValidationError",
    "InvalidBirthInfoError",
    "InvalidTimeError",
    "ConfigurationError",
    "AlgorithmError",
    "CacheError",
]
