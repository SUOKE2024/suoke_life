"""Exception handlers for FastAPI application."""

import traceback
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from ..core.logging import get_logger, log_error
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

logger = get_logger(__name__)


def create_error_response(
    error_code: str,
    message: str,
    details: dict[str, Any],
    status_code: int,
) -> JSONResponse:
    """Create standardized error response.

    Args:
        error_code: Error code
        message: Error message
        details: Error details
        status_code: HTTP status code

    Returns:
        JSON response with error information
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": error_code,
                "message": message,
                "details": details,
            }
        },
    )


async def handle_look_service_error(
    request: Request, exc: LookServiceError
) -> JSONResponse:
    """Handle LookServiceError exceptions."""
    log_error(exc, {"path": str(request.url), "method": request.method})

    # Map exception types to HTTP status codes
    status_code_map = {
        ValidationError: status.HTTP_400_BAD_REQUEST,
        NotFoundError: status.HTTP_404_NOT_FOUND,
        AuthenticationError: status.HTTP_401_UNAUTHORIZED,
        AuthorizationError: status.HTTP_403_FORBIDDEN,
        ExternalServiceError: status.HTTP_502_BAD_GATEWAY,
        DatabaseError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        MLModelError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ImageProcessingError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    }

    status_code = status_code_map.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)

    return create_error_response(
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        status_code=status_code,
    )


async def handle_validation_error(
    request: Request, exc: PydanticValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    logger.warning(
        "Validation error",
        path=str(request.url),
        method=request.method,
        errors=exc.errors(),
    )

    # Format validation errors
    formatted_errors = []
    for error in exc.errors():
        formatted_errors.append(
            {
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
                "input": error.get("input"),
            }
        )

    return create_error_response(
        error_code="VALIDATION_ERROR",
        message="Request validation failed",
        details={"errors": formatted_errors},
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


async def handle_not_found_error(request: Request, exc: Exception) -> JSONResponse:
    """Handle 404 Not Found errors."""
    logger.warning(
        "Not found",
        path=str(request.url),
        method=request.method,
    )

    return create_error_response(
        error_code="NOT_FOUND",
        message="The requested resource was not found",
        details={"path": str(request.url)},
        status_code=status.HTTP_404_NOT_FOUND,
    )


async def handle_internal_error(request: Request, exc: Exception) -> JSONResponse:
    """Handle internal server errors."""
    logger.error(
        "Internal server error",
        path=str(request.url),
        method=request.method,
        error=str(exc),
        traceback=traceback.format_exc(),
    )

    return create_error_response(
        error_code="INTERNAL_ERROR",
        message="An internal server error occurred",
        details={},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


async def handle_method_not_allowed(request: Request, exc: Exception) -> JSONResponse:
    """Handle method not allowed errors."""
    logger.warning(
        "Method not allowed",
        path=str(request.url),
        method=request.method,
    )

    return create_error_response(
        error_code="METHOD_NOT_ALLOWED",
        message=f"Method {request.method} not allowed for this endpoint",
        details={"method": request.method, "path": str(request.url)},
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup exception handlers for the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    # Custom exception handlers
    app.add_exception_handler(LookServiceError, handle_look_service_error)  # type: ignore[arg-type]
    app.add_exception_handler(PydanticValidationError, handle_validation_error)  # type: ignore[arg-type]

    # HTTP exception handlers
    app.add_exception_handler(404, handle_not_found_error)
    app.add_exception_handler(405, handle_method_not_allowed)
    app.add_exception_handler(500, handle_internal_error)

    # Catch-all exception handler
    app.add_exception_handler(Exception, handle_internal_error)

    logger.info("Exception handlers configured")
