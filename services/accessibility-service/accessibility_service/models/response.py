"""
Response-related data models.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ResponseStatus(str, Enum):
    """Response status values."""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"
    TIMEOUT = "timeout"


class ErrorCode(str, Enum):
    """Error codes for API responses."""
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    NOT_FOUND = "not_found"
    INTERNAL_ERROR = "internal_error"
    SERVICE_UNAVAILABLE = "service_unavailable"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    INVALID_INPUT = "invalid_input"
    PROCESSING_ERROR = "processing_error"


class ServiceResponse(BaseModel):
    """Base service response model."""

    status: ResponseStatus = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: str | None = Field(None, description="Request identifier")

    # Metadata
    version: str = Field(default="1.0.0", description="API version")
    processing_time: float | None = Field(None, description="Processing time in seconds")


class SuccessResponse(ServiceResponse):
    """Success response model."""

    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS)
    data: dict[str, Any] | None = Field(None, description="Response data")

    # Pagination (if applicable)
    pagination: dict[str, Any] | None = Field(None, description="Pagination information")

    # Additional metadata
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")


class ErrorResponse(ServiceResponse):
    """Error response model."""

    status: ResponseStatus = Field(default=ResponseStatus.ERROR)
    error_code: ErrorCode = Field(..., description="Error code")
    error_details: dict[str, Any] | None = Field(None, description="Error details")

    # Debugging information (only in development)
    debug_info: dict[str, Any] | None = Field(None, description="Debug information")

    # Suggestions for fixing the error
    suggestions: list[str] = Field(default_factory=list, description="Error resolution suggestions")


class ValidationErrorResponse(ErrorResponse):
    """Validation error response model."""

    error_code: ErrorCode = Field(default=ErrorCode.VALIDATION_ERROR)
    validation_errors: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Detailed validation errors"
    )


class AnalysisResponse(SuccessResponse):
    """Response for accessibility analysis requests."""

    analysis_id: str = Field(..., description="Analysis identifier")
    user_id: str = Field(..., description="User identifier")

    # Analysis results
    accessibility_score: float = Field(..., ge=0.0, le=100.0, description="Overall accessibility score")
    analysis_summary: dict[str, Any] = Field(..., description="Analysis summary")

    # Issues and recommendations
    issues_found: int = Field(..., description="Number of issues found")
    critical_issues: int = Field(..., description="Number of critical issues")
    recommendations: list[dict[str, Any]] = Field(default_factory=list)

    # Processing information
    analysis_types: list[str] = Field(..., description="Types of analysis performed")
    processing_details: dict[str, Any] = Field(default_factory=dict)


class StatusResponse(SuccessResponse):
    """Service status response."""

    service_name: str = Field(..., description="Service name")
    service_version: str = Field(..., description="Service version")
    health_status: str = Field(..., description="Health status")

    # Service metrics
    uptime: float = Field(..., description="Service uptime in seconds")
    total_requests: int = Field(..., description="Total requests processed")
    active_analyses: int = Field(..., description="Currently active analyses")

    # Dependencies status
    dependencies: dict[str, str] = Field(default_factory=dict, description="Dependencies status")

    # System resources
    system_info: dict[str, Any] | None = Field(None, description="System information")


class RecommendationResponse(SuccessResponse):
    """Response for recommendation requests."""

    user_id: str = Field(..., description="User identifier")
    recommendation_type: str = Field(..., description="Type of recommendations")

    # Recommendations
    recommendations: list[dict[str, Any]] = Field(..., description="List of recommendations")
    priority_recommendations: list[dict[str, Any]] = Field(
        default_factory=list,
        description="High priority recommendations"
    )

    # Personalization info
    personalization_score: float = Field(
        ..., ge=0.0, le=1.0,
        description="How personalized these recommendations are"
    )
    based_on: list[str] = Field(..., description="What the recommendations are based on")


class BatchResponse(SuccessResponse):
    """Response for batch operations."""

    batch_id: str = Field(..., description="Batch identifier")
    total_items: int = Field(..., description="Total items in batch")
    processed_items: int = Field(..., description="Successfully processed items")
    failed_items: int = Field(..., description="Failed items")

    # Results
    results: list[dict[str, Any]] = Field(default_factory=list, description="Batch results")
    errors: list[dict[str, Any]] = Field(default_factory=list, description="Batch errors")

    # Progress information
    progress_percentage: float = Field(..., ge=0.0, le=100.0, description="Progress percentage")
    estimated_completion: datetime | None = Field(None, description="Estimated completion time")


class PaginatedResponse(SuccessResponse):
    """Paginated response model."""

    items: list[dict[str, Any]] = Field(..., description="Items in current page")

    # Pagination info
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Items per page")
    total_items: int = Field(..., ge=0, description="Total number of items")
    total_pages: int = Field(..., ge=0, description="Total number of pages")

    # Navigation
    has_next: bool = Field(..., description="Has next page")
    has_previous: bool = Field(..., description="Has previous page")
    next_page: int | None = Field(None, description="Next page number")
    previous_page: int | None = Field(None, description="Previous page number")
