"""
accessibility - 索克生活项目模块
"""

from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field, field_validator
from typing import Any

"""
Accessibility-related data models.
"""




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

    user_id: str = Field(..., min_length=1, description="User identifier")
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

    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator('accessibility_types')
    @classmethod
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
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


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

    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


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
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = Field(default="1.0.0", description="API version")

    @field_validator('overall_score')
    @classmethod
    def validate_overall_score(cls, v, info):
        """Validate overall score consistency."""
        if info.data and 'analyses' in info.data and info.data['analyses']:
            # Calculate weighted average if analyses exist
            total_weight = len(info.data['analyses'])
            if total_weight > 0:
                calculated_score = sum(analysis.score for analysis in info.data['analyses']) / total_weight
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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = Field(default=1, description="Profile version")


class VisualAnalysis(BaseModel):
    """Visual analysis results for accessibility."""
    
    accessibility_score: float = Field(..., ge=0.0, le=100.0, description="Visual accessibility score")
    issues: list[str] = Field(default_factory=list, description="Identified visual issues")
    recommendations: list[str] = Field(default_factory=list, description="Visual improvement recommendations")
    
    # Scene analysis
    scene_description: str = Field(..., description="Description of the visual scene")
    detected_objects: list[dict[str, Any]] = Field(default_factory=list, description="Detected objects in scene")
    navigation_guidance: str = Field(default="", description="Navigation guidance for blind users")
    
    # Text analysis
    extracted_text: str = Field(default="", description="Text extracted from image")
    text_accessibility: dict[str, Any] = Field(default_factory=dict, description="Text accessibility metrics")
    
    # Barrier analysis
    barriers: list[str] = Field(default_factory=list, description="Identified accessibility barriers")
    depth_info: dict[str, Any] = Field(default_factory=dict, description="Depth and spatial information")
    
    # Metadata
    processing_time: float = Field(..., description="Processing time in seconds")
    model_version: str = Field(default="1.0.0", description="Model version used")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AudioAnalysis(BaseModel):
    """Audio analysis results for accessibility."""
    
    accessibility_score: float = Field(..., ge=0.0, le=100.0, description="Audio accessibility score")
    issues: list[str] = Field(default_factory=list, description="Identified audio issues")
    recommendations: list[str] = Field(default_factory=list, description="Audio improvement recommendations")
    
    # Speech analysis
    transcribed_text: str = Field(default="", description="Transcribed speech content")
    speech_clarity: float = Field(default=0.0, ge=0.0, le=1.0, description="Speech clarity score")
    language_detected: str = Field(default="", description="Detected language")
    
    # Audio quality
    quality_metrics: dict[str, Any] = Field(default_factory=dict, description="Audio quality metrics")
    noise_analysis: dict[str, Any] = Field(default_factory=dict, description="Background noise analysis")
    
    # Accessibility features
    sound_events: list[dict[str, Any]] = Field(default_factory=list, description="Detected sound events")
    frequency_analysis: dict[str, Any] = Field(default_factory=dict, description="Frequency spectrum analysis")
    
    # Metadata
    processing_time: float = Field(..., description="Processing time in seconds")
    model_version: str = Field(default="1.0.0", description="Model version used")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MotorAnalysis(BaseModel):
    """Motor analysis results for accessibility."""
    
    accessibility_score: float = Field(..., ge=0.0, le=100.0, description="Motor accessibility score")
    issues: list[str] = Field(default_factory=list, description="Identified motor issues")
    recommendations: list[str] = Field(default_factory=list, description="Motor improvement recommendations")
    
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
    
    # Metadata
    processing_time: float = Field(..., description="Processing time in seconds")
    model_version: str = Field(default="1.0.0", description="Model version used")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CognitiveAnalysis(BaseModel):
    """Cognitive analysis results for accessibility."""
    
    accessibility_score: float = Field(..., ge=0.0, le=100.0, description="Cognitive accessibility score")
    issues: list[str] = Field(default_factory=list, description="Identified cognitive issues")
    recommendations: list[str] = Field(default_factory=list, description="Cognitive improvement recommendations")
    
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
    
    # Metadata
    processing_time: float = Field(..., description="Processing time in seconds")
    model_version: str = Field(default="1.0.0", description="Model version used")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
