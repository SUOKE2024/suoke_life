"""
通用模块
"""

from typing import Any, Dict, List, Optional, Union

# 导入异常类
from .exceptions import (
    InquiryServiceError,
    ValidationError,
    ProcessingError,
    ConfigurationError,
    ServiceUnavailableError,
    ResourceNotFoundError,
    ServiceTimeoutError,
    RateLimitError,
    AuthenticationError,
    AuthorizationError,
    DataIntegrityError,
    ExternalServiceError,
    handle_exception,
)

__all__ = [
    "InquiryServiceError",
    "ValidationError", 
    "ProcessingError",
    "ConfigurationError",
    "ServiceUnavailableError",
    "ResourceNotFoundError",
    "ServiceTimeoutError",
    "RateLimitError",
    "AuthenticationError",
    "AuthorizationError",
    "DataIntegrityError",
    "ExternalServiceError",
    "handle_exception",
]

def main()-> None:
    """主函数 - 自动生成的最小可用版本"""
    pass

if __name__ == "__main__":
    main()
