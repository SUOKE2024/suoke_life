"""Exception handling for look service."""

from .base import (
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
from .handlers import (
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
