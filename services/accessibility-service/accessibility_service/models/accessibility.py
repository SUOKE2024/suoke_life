"""
Accessibility-related data models.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, validator


class AccessibilityType(str, Enum):
    """Types of accessibility analysis."""
    VISUAL = "visual"
    AUDIO = "audio"
    MOTOR = "motor"
    COGNITIVE = "cognitive"
    MULTIMODAL = "multimodal"


class SeverityLevel(str, Enum):
    """Severity levels for accessibility issues."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AccessibilityRequest(BaseModel):
    """Request for accessibility analysis."""

    user_id: str = Field(..., description="User identifier")
    session_id: str | None = Field(None, description="Session identifier")
    accessibility_types: list[AccessibilityType] = Field(
        default=[AccessibilityType.MULTIMODAL],
        description="Types of accessibility analysis to perform"
    )

    # Input data
    visual_data: dict[str, Any] | None = Field(None, description="Visual input data")
    audio_data: dict[str, Any] | None = Field(None, description="Audio input data")
    motor_data: dict[str, Any] | None = Field(None, description="Motor input data")
    cognitive_data: dict[str, Any] | None = Field(None, description="Cognitive input data")

    # Context information
    context: dict[str, Any] | None = Field(None, description="Additional context")
    user_preferences: dict[str, Any] | None = Field(None, description="User preferences")
    device_info: dict[str, Any] | None = Field(None, description="Device information")

    # Analysis options
    detailed_analysis: bool = Field(True, description="Whether to perform detailed analysis")
    real_time: bool = Field(False, description="Whether this is real-time analysis")

    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @validator('accessibility_types')
    def validate_accessibility_types(cls, v):
        """Validate accessibility types."""
        if not v:
            return [AccessibilityType.MULTIMODAL]
        return v


class AccessibilityIssue(BaseModel):
    """Individual accessibility issue."""

    issue_id: str = Field(..., description="Unique issue identifier")
    type: AccessibilityType = Field(..., description="Type of accessibility issue")
    severity: SeverityLevel = Field(..., description="Severity level")

    title: str = Field(..., description="Issue title")
    description: str = Field(..., description="Detailed description")

    # Location and context
    location: dict[str, Any] | None = Field(None, description="Issue location")
    context: dict[str, Any] | None = Field(None, description="Issue context")

    # Recommendations
    recommendations: list[str] = Field(default_factory=list, description="Recommendations")
    quick_fixes: list[str] = Field(default_factory=list, description="Quick fix suggestions")

    # Metadata
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    detected_at: datetime = Field(default_factory=datetime.utcnow)


class AccessibilityAnalysis(BaseModel):
    """Analysis results for a specific accessibility type."""

    type: AccessibilityType = Field(..., description="Type of analysis")
    status: str = Field(..., description="Analysis status")

    # Results
    issues: list[AccessibilityIssue] = Field(default_factory=list)
    score: float = Field(..., ge=0.0, le=100.0, description="Accessibility score")

    # Metrics
    metrics: dict[str, float] = Field(default_factory=dict, description="Analysis metrics")

    # Recommendations
    recommendations: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)

    # Processing info
    processing_time: float = Field(..., description="Processing time in seconds")
    analysis_model_version: str | None = Field(None, description="Model version used")

    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AccessibilityRecommendation(BaseModel):
    """Accessibility improvement recommendation."""

    recommendation_id: str = Field(..., description="Unique recommendation identifier")
    type: AccessibilityType = Field(..., description="Type of recommendation")
    priority: SeverityLevel = Field(..., description="Priority level")

    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="Detailed description")

    # Implementation
    implementation_steps: list[str] = Field(default_factory=list)
    estimated_effort: str | None = Field(None, description="Estimated implementation effort")

    # Impact
    expected_impact: str = Field(..., description="Expected impact description")
    affected_users: list[str] | None = Field(None, description="Affected user groups")

    # Resources
    resources: list[str] = Field(default_factory=list, description="Helpful resources")
    tools: list[str] = Field(default_factory=list, description="Recommended tools")

    # Metadata
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AccessibilityResponse(BaseModel):
    """Response from accessibility analysis."""

    request_id: str = Field(..., description="Request identifier")
    user_id: str = Field(..., description="User identifier")
    session_id: str | None = Field(None, description="Session identifier")

    # Analysis results
    analyses: list[AccessibilityAnalysis] = Field(default_factory=list)
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Overall accessibility score")

    # Summary
    total_issues: int = Field(..., description="Total number of issues found")
    critical_issues: int = Field(..., description="Number of critical issues")

    # Recommendations
    recommendations: list[AccessibilityRecommendation] = Field(default_factory=list)
    quick_wins: list[str] = Field(default_factory=list, description="Quick improvement suggestions")

    # Processing info
    processing_time: float = Field(..., description="Total processing time in seconds")
    status: str = Field(..., description="Response status")

    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(default="1.0.0", description="API version")

    @validator('overall_score')
    def validate_overall_score(cls, v, values):
        """Validate overall score consistency."""
        if 'analyses' in values and values['analyses']:
            # Calculate weighted average if analyses exist
            total_weight = len(values['analyses'])
            if total_weight > 0:
                calculated_score = sum(analysis.score for analysis in values['analyses']) / total_weight
                # Allow some tolerance for rounding
                if abs(v - calculated_score) > 1.0:
                    raise ValueError("Overall score inconsistent with individual analysis scores")
        return v


class AccessibilityProfile(BaseModel):
    """User accessibility profile."""

    user_id: str = Field(..., description="User identifier")

    # Accessibility needs
    visual_needs: dict[str, Any] | None = Field(None, description="Visual accessibility needs")
    audio_needs: dict[str, Any] | None = Field(None, description="Audio accessibility needs")
    motor_needs: dict[str, Any] | None = Field(None, description="Motor accessibility needs")
    cognitive_needs: dict[str, Any] | None = Field(None, description="Cognitive accessibility needs")

    # Preferences
    preferences: dict[str, Any] = Field(default_factory=dict, description="User preferences")

    # History
    assessment_history: list[str] = Field(default_factory=list, description="Assessment history")
    improvement_tracking: dict[str, Any] = Field(default_factory=dict, description="Improvement tracking")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = Field(default=1, description="Profile version")
