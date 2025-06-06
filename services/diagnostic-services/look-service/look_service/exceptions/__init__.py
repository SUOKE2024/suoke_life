"""
__init__ - 索克生活项目模块
"""

from .base import (
from .handlers import (

"""Exception handling for look service."""

    AuthenticationError,
    AuthorizationError,
    DatabaseError,
    ExternalServiceError,
    ImageProcessingError,
    LookServiceError,
    MLModelError,
    NotFoundError,
    ValidationError,
)
    handle_internal_error,
    handle_not_found_error,
    handle_validation_error,
    setup_exception_handlers,
)

__all__ = [
    # Base exceptions
    "LookServiceError",
    "ValidationError",
    "NotFoundError",
    "AuthenticationError",
    "AuthorizationError",
    "ExternalServiceError",
    "DatabaseError",
    "MLModelError",
    "ImageProcessingError",
    # Exception handlers
    "setup_exception_handlers",
    "handle_validation_error",
    "handle_not_found_error",
    "handle_internal_error",
]
