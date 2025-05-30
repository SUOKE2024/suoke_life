"""
Analysis-related data models for accessibility service.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, validator


class AnalysisStatus(str, Enum):
    """Analysis status values."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AnalysisType(str, Enum):
    """Types of accessibility analysis."""
    VISUAL = "visual"
    AUDIO = "audio"
    MOTOR = "motor"
    COGNITIVE = "cognitive"


class BaseAnalysis(BaseModel):
    """Base analysis model."""

    analysis_id: str = Field(..., description="Unique analysis identifier")
    status: AnalysisStatus = Field(..., description="Analysis status")
    processing_time: float = Field(..., description="Processing time in seconds")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = Field(None, description="Completion timestamp")

    # Error information (if failed)
    error_message: str | None = Field(None, description="Error message if failed")
    error_code: str | None = Field(None, description="Error code if failed")


class VisualAnalysis(BaseAnalysis):
    """Visual accessibility analysis results."""

    # Color and contrast analysis
    color_contrast_ratio: float = Field(..., description="Overall color contrast ratio")
    contrast_issues: list[dict[str, Any]] = Field(
        default_factory=list,
        description="List of contrast issues found"
    )
    contrast_recommendations: list[str] = Field(
        default_factory=list,
        description="Contrast improvement recommendations"
    )

    # Text readability analysis
    text_readability_score: float = Field(..., ge=0.0, le=100.0, description="Text readability score")
    readability_issues: list[dict[str, Any]] = Field(
        default_factory=list,
        description="List of readability issues"
    )
    readability_recommendations: list[str] = Field(
        default_factory=list,
        description="Readability improvement recommendations"
    )

    # Image and media analysis
    image_alt_text_coverage: float = Field(..., ge=0.0, le=100.0, description="Alt text coverage percentage")
    missing_alt_text: list[str] = Field(
        default_factory=list,
        description="Images missing alt text"
    )

    # Layout and structure
    layout_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Layout accessibility score")
    structure_issues: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Layout and structure issues"
    )

    # Focus and navigation
    focus_indicators: bool = Field(default=True, description="Has visible focus indicators")
    tab_order_logical: bool = Field(default=True, description="Tab order is logical")


class AudioAnalysis(BaseAnalysis):
    """Audio accessibility analysis results."""

    # Volume and clarity
    volume_level: float = Field(..., ge=0.0, le=100.0, description="Audio volume level")
    clarity_score: float = Field(..., ge=0.0, le=100.0, description="Audio clarity score")

    # Speech analysis
    speech_rate: float = Field(..., description="Speech rate in words per minute")
    speech_clarity: float = Field(default=0.0, ge=0.0, le=100.0, description="Speech clarity score")

    # Accessibility features
    has_captions: bool = Field(default=False, description="Has captions available")
    has_transcript: bool = Field(default=False, description="Has transcript available")
    has_audio_description: bool = Field(default=False, description="Has audio description")
    has_sign_language: bool = Field(default=False, description="Has sign language interpretation")

    # Audio quality metrics
    background_noise_level: float = Field(default=0.0, ge=0.0, le=100.0, description="Background noise level")
    frequency_range: dict[str, float] = Field(
        default_factory=dict,
        description="Audio frequency range analysis"
    )

    # Recommendations
    audio_recommendations: list[str] = Field(
        default_factory=list,
        description="Audio accessibility recommendations"
    )


class MotorAnalysis(BaseAnalysis):
    """Motor accessibility analysis results."""

    # Click targets and touch
    click_target_size: float = Field(..., description="Average click target size in pixels")
    min_target_size: float = Field(default=44.0, description="Minimum recommended target size")
    target_spacing: float = Field(default=8.0, description="Spacing between targets")

    # Navigation methods
    keyboard_navigation_score: float = Field(..., ge=0.0, le=100.0, description="Keyboard navigation score")
    keyboard_accessible: bool = Field(default=True, description="Fully keyboard accessible")
    touch_accessible: bool = Field(default=True, description="Touch accessible")
    voice_control_compatible: bool = Field(default=False, description="Voice control compatible")

    # Gesture complexity
    gesture_complexity_score: float = Field(..., ge=0.0, le=100.0, description="Gesture complexity score")
    complex_gestures: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Complex gestures that may be difficult"
    )

    # Timing and delays
    timeout_warnings: bool = Field(default=True, description="Has timeout warnings")
    adjustable_timing: bool = Field(default=False, description="Timing is adjustable")

    # Motor recommendations
    motor_recommendations: list[str] = Field(
        default_factory=list,
        description="Motor accessibility recommendations"
    )


class CognitiveAnalysis(BaseAnalysis):
    """Cognitive accessibility analysis results."""

    # Content complexity
    complexity_score: float = Field(..., ge=0.0, le=100.0, description="Content complexity score")
    reading_level: str = Field(..., description="Reading level (e.g., 'Grade 8')")
    sentence_complexity: float = Field(default=0.0, ge=0.0, le=100.0, description="Sentence complexity score")

    # Attention and focus
    attention_load_score: float = Field(..., ge=0.0, le=100.0, description="Cognitive attention load score")
    distracting_elements: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Elements that may be distracting"
    )

    # Structure and organization
    has_clear_structure: bool = Field(default=True, description="Has clear content structure")
    has_consistent_navigation: bool = Field(default=True, description="Has consistent navigation")
    has_breadcrumbs: bool = Field(default=False, description="Has breadcrumb navigation")

    # Error handling and help
    has_error_prevention: bool = Field(default=False, description="Has error prevention features")
    has_help_system: bool = Field(default=False, description="Has help system available")
    error_messages_clear: bool = Field(default=True, description="Error messages are clear")

    # Memory and processing
    memory_load_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Memory load score")
    processing_time_adequate: bool = Field(default=True, description="Processing time is adequate")

    # Cognitive recommendations
    cognitive_recommendations: list[str] = Field(
        default_factory=list,
        description="Cognitive accessibility recommendations"
    )


class ComprehensiveAnalysis(BaseAnalysis):
    """Comprehensive analysis combining all accessibility types."""

    # Individual analysis results
    visual_analysis: VisualAnalysis | None = Field(None, description="Visual analysis results")
    audio_analysis: AudioAnalysis | None = Field(None, description="Audio analysis results")
    motor_analysis: MotorAnalysis | None = Field(None, description="Motor analysis results")
    cognitive_analysis: CognitiveAnalysis | None = Field(None, description="Cognitive analysis results")

    # Overall scores
    overall_accessibility_score: float = Field(..., ge=0.0, le=100.0, description="Overall accessibility score")
    wcag_compliance_level: str = Field(default="AA", description="WCAG compliance level")

    # Issue summary
    total_issues: int = Field(default=0, description="Total number of issues found")
    critical_issues: int = Field(default=0, description="Number of critical issues")
    medium_issues: int = Field(default=0, description="Number of medium priority issues")
    low_issues: int = Field(default=0, description="Number of low priority issues")

    # Recommendations summary
    priority_recommendations: list[str] = Field(
        default_factory=list,
        description="High priority recommendations"
    )
    all_recommendations: list[str] = Field(
        default_factory=list,
        description="All recommendations"
    )

    # Compliance information
    wcag_violations: list[dict[str, Any]] = Field(
        default_factory=list,
        description="WCAG guideline violations"
    )
    compliance_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Compliance percentage")


class AnalysisReport(BaseModel):
    """Detailed analysis report."""

    report_id: str = Field(..., description="Unique report identifier")
    user_id: str = Field(..., description="User identifier")
    analysis: ComprehensiveAnalysis = Field(..., description="Comprehensive analysis results")

    # Report metadata
    report_type: str = Field(default="comprehensive", description="Type of report")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(default="1.0.0", description="Report version")

    # Executive summary
    executive_summary: str = Field(..., description="Executive summary of findings")
    key_findings: list[str] = Field(default_factory=list, description="Key findings")

    # Improvement plan
    improvement_plan: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Step-by-step improvement plan"
    )
    estimated_effort: str = Field(default="medium", description="Estimated implementation effort")

    # Historical comparison (if available)
    previous_score: float | None = Field(None, description="Previous accessibility score")
    improvement_percentage: float | None = Field(None, description="Improvement percentage")

    @validator('compliance_percentage', check_fields=False)
    def validate_compliance_percentage(cls, v):
        """Validate compliance percentage."""
        if not 0 <= v <= 100:
            raise ValueError("Compliance percentage must be between 0 and 100")
        return v
