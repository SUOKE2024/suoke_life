"""Base exception classes for look service."""

from typing import Any


class LookServiceError(Exception):
    """Base exception for look service."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize exception.

        Args:
            message: Error message
            error_code: Error code for client identification
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}


class ValidationError(LookServiceError):
    """Validation error."""

    def __init__(
        self,
        message: str = "Validation failed",
        field: str | None = None,
        value: Any | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize validation error.

        Args:
            message: Error message
            field: Field that failed validation
            value: Invalid value
            **kwargs: Additional arguments
        """
        details = kwargs.get("details", {})
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = value

        super().__init__(message, "VALIDATION_ERROR", details)


class NotFoundError(LookServiceError):
    """Resource not found error."""

    def __init__(
        self,
        resource: str,
        identifier: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize not found error.

        Args:
            resource: Resource type that was not found
            identifier: Resource identifier
            **kwargs: Additional arguments
        """
        message = f"{resource} not found"
        if identifier:
            message += f" with identifier: {identifier}"

        details = kwargs.get("details", {})
        details.update(
            {
                "resource": resource,
                "identifier": identifier,
            }
        )

        super().__init__(message, "NOT_FOUND", details)


class AuthenticationError(LookServiceError):
    """Authentication error."""

    def __init__(
        self,
        message: str = "Authentication failed",
        **kwargs: Any,
    ) -> None:
        """Initialize authentication error."""
        super().__init__(message, "AUTHENTICATION_ERROR", kwargs.get("details", {}))


class AuthorizationError(LookServiceError):
    """Authorization error."""

    def __init__(
        self,
        message: str = "Access denied",
        resource: str | None = None,
        action: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize authorization error.

        Args:
            message: Error message
            resource: Resource being accessed
            action: Action being performed
            **kwargs: Additional arguments
        """
        details = kwargs.get("details", {})
        if resource:
            details["resource"] = resource
        if action:
            details["action"] = action

        super().__init__(message, "AUTHORIZATION_ERROR", details)


class ExternalServiceError(LookServiceError):
    """External service error."""

    def __init__(
        self,
        service: str,
        message: str = "External service error",
        status_code: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize external service error.

        Args:
            service: External service name
            message: Error message
            status_code: HTTP status code if applicable
            **kwargs: Additional arguments
        """
        details = kwargs.get("details", {})
        details.update(
            {
                "service": service,
                "status_code": status_code,
            }
        )

        super().__init__(message, "EXTERNAL_SERVICE_ERROR", details)


class DatabaseError(LookServiceError):
    """Database error."""

    def __init__(
        self,
        message: str = "Database error",
        operation: str | None = None,
        table: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize database error.

        Args:
            message: Error message
            operation: Database operation that failed
            table: Database table involved
            **kwargs: Additional arguments
        """
        details = kwargs.get("details", {})
        if operation:
            details["operation"] = operation
        if table:
            details["table"] = table

        super().__init__(message, "DATABASE_ERROR", details)


class MLModelError(LookServiceError):
    """Machine learning model error."""

    def __init__(
        self,
        model: str,
        message: str = "ML model error",
        operation: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize ML model error.

        Args:
            model: Model name
            message: Error message
            operation: Operation that failed (load, predict, etc.)
            **kwargs: Additional arguments
        """
        details = kwargs.get("details", {})
        details.update(
            {
                "model": model,
                "operation": operation,
            }
        )

        super().__init__(message, "ML_MODEL_ERROR", details)


class ImageProcessingError(LookServiceError):
    """Image processing error."""

    def __init__(
        self,
        message: str = "Image processing error",
        operation: str | None = None,
        image_format: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize image processing error.

        Args:
            message: Error message
            operation: Processing operation that failed
            image_format: Image format
            **kwargs: Additional arguments
        """
        details = kwargs.get("details", {})
        if operation:
            details["operation"] = operation
        if image_format:
            details["image_format"] = image_format

        super().__init__(message, "IMAGE_PROCESSING_ERROR", details)
