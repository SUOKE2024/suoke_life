"""
User-related data models.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, validator


class UserRole(str, Enum):
    """User roles."""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


class AccessibilityNeed(str, Enum):
    """Types of accessibility needs."""
    VISUAL_IMPAIRMENT = "visual_impairment"
    HEARING_IMPAIRMENT = "hearing_impairment"
    MOTOR_IMPAIRMENT = "motor_impairment"
    COGNITIVE_IMPAIRMENT = "cognitive_impairment"
    NONE = "none"


class User(BaseModel):
    """User model."""

    user_id: str = Field(..., description="Unique user identifier")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="User email")

    # Profile information
    first_name: str | None = Field(None, description="First name")
    last_name: str | None = Field(None, description="Last name")
    date_of_birth: datetime | None = Field(None, description="Date of birth")

    # Account information
    role: UserRole = Field(default=UserRole.USER, description="User role")
    is_active: bool = Field(default=True, description="Account active status")
    is_verified: bool = Field(default=False, description="Email verification status")

    # Accessibility information
    accessibility_needs: list[AccessibilityNeed] = Field(
        default_factory=list,
        description="User's accessibility needs"
    )

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: datetime | None = Field(None, description="Last login timestamp")

    @validator('email')
    def validate_email(cls, v):
        """Validate email format."""
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower()

    @validator('username')
    def validate_username(cls, v):
        """Validate username."""
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        return v


class UserProfile(BaseModel):
    """Extended user profile information."""

    user_id: str = Field(..., description="User identifier")

    # Personal information
    bio: str | None = Field(None, description="User biography")
    avatar_url: str | None = Field(None, description="Avatar image URL")
    timezone: str | None = Field(None, description="User timezone")
    language: str = Field(default="en", description="Preferred language")

    # Accessibility profile
    visual_preferences: dict[str, Any] = Field(
        default_factory=dict,
        description="Visual accessibility preferences"
    )
    audio_preferences: dict[str, Any] = Field(
        default_factory=dict,
        description="Audio accessibility preferences"
    )
    motor_preferences: dict[str, Any] = Field(
        default_factory=dict,
        description="Motor accessibility preferences"
    )
    cognitive_preferences: dict[str, Any] = Field(
        default_factory=dict,
        description="Cognitive accessibility preferences"
    )

    # Usage statistics
    total_analyses: int = Field(default=0, description="Total accessibility analyses performed")
    last_analysis: datetime | None = Field(None, description="Last analysis timestamp")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserPreferences(BaseModel):
    """User preferences for accessibility service."""

    user_id: str = Field(..., description="User identifier")

    # Analysis preferences
    default_analysis_types: list[str] = Field(
        default_factory=lambda: ["multimodal"],
        description="Default analysis types"
    )
    detailed_analysis: bool = Field(default=True, description="Enable detailed analysis")
    real_time_analysis: bool = Field(default=False, description="Enable real-time analysis")

    # Notification preferences
    email_notifications: bool = Field(default=True, description="Enable email notifications")
    push_notifications: bool = Field(default=True, description="Enable push notifications")
    analysis_complete_notification: bool = Field(
        default=True,
        description="Notify when analysis is complete"
    )

    # Privacy preferences
    data_sharing: bool = Field(default=False, description="Allow data sharing for research")
    anonymous_analytics: bool = Field(default=True, description="Allow anonymous analytics")

    # Interface preferences
    theme: str = Field(default="light", description="UI theme preference")
    font_size: str = Field(default="medium", description="Font size preference")
    high_contrast: bool = Field(default=False, description="High contrast mode")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('theme')
    def validate_theme(cls, v):
        """Validate theme preference."""
        allowed_themes = ['light', 'dark', 'auto']
        if v not in allowed_themes:
            raise ValueError(f'Theme must be one of: {allowed_themes}')
        return v

    @validator('font_size')
    def validate_font_size(cls, v):
        """Validate font size preference."""
        allowed_sizes = ['small', 'medium', 'large', 'extra-large']
        if v not in allowed_sizes:
            raise ValueError(f'Font size must be one of: {allowed_sizes}')
        return v
