"""
异常处理模块
"""

from typing import Any, Dict, List, Optional, Union

from .base import (
    DatabaseError,
    ImageProcessingError,
    LookServiceError,
    MLModelError,
    ValidationError,
)
from .handlers import setup_exception_handlers

__all__ = [
    "LookServiceError",
    "ValidationError", 
    "ImageProcessingError",
    "MLModelError",
    "DatabaseError",
    "setup_exception_handlers",
]


def main() -> None:
    """主函数 - 用于测试"""
    pass


if __name__ == "__main__":
    main()
