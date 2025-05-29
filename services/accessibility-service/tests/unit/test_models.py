"""
Unit tests for accessibility service models.
"""

from datetime import datetime

import pytest
from accessibility_service.models.accessibility import (
    AccessibilityAnalysis,
    AccessibilityIssue,
    AccessibilityRequest,
    AccessibilityResponse,
    AccessibilityType,
    SeverityLevel,
)
from pydantic import ValidationError


class TestAccessibilityRequest:
    """Test AccessibilityRequest model."""

    def test_valid_request(self):
        """Test creating a valid accessibility request."""
        request = AccessibilityRequest(
            user_id="user123",
            accessibility_types=[AccessibilityType.VISUAL]
        )

        assert request.user_id == "user123"
        assert request.accessibility_types == [AccessibilityType.VISUAL]
        assert request.detailed_analysis is True
        assert request.real_time is False
        assert isinstance(request.timestamp, datetime)

    def test_default_accessibility_types(self):
        """Test default accessibility types."""
        request = AccessibilityRequest(user_id="user123")
        assert request.accessibility_types == [AccessibilityType.MULTIMODAL]

    def test_empty_accessibility_types(self):
        """Test empty accessibility types defaults to multimodal."""
        request = AccessibilityRequest(
            user_id="user123",
            accessibility_types=[]
        )
        assert request.accessibility_types == [AccessibilityType.MULTIMODAL]

    def test_invalid_user_id(self):
        """Test validation with invalid user ID."""
        with pytest.raises(ValidationError):
            AccessibilityRequest(user_id="")


class TestAccessibilityIssue:
    """Test AccessibilityIssue model."""

    def test_valid_issue(self):
        """Test creating a valid accessibility issue."""
        issue = AccessibilityIssue(
            issue_id="issue123",
            type=AccessibilityType.VISUAL,
            severity=SeverityLevel.HIGH,
            title="Color contrast issue",
            description="Insufficient color contrast ratio",
            confidence=0.95
        )

        assert issue.issue_id == "issue123"
        assert issue.type == AccessibilityType.VISUAL
        assert issue.severity == SeverityLevel.HIGH
        assert issue.confidence == 0.95
        assert isinstance(issue.detected_at, datetime)

    def test_confidence_validation(self):
        """Test confidence score validation."""
        # Valid confidence
        issue = AccessibilityIssue(
            issue_id="issue123",
            type=AccessibilityType.VISUAL,
            severity=SeverityLevel.HIGH,
            title="Test issue",
            description="Test description",
            confidence=0.5
        )
        assert issue.confidence == 0.5

        # Invalid confidence - too high
        with pytest.raises(ValidationError):
            AccessibilityIssue(
                issue_id="issue123",
                type=AccessibilityType.VISUAL,
                severity=SeverityLevel.HIGH,
                title="Test issue",
                description="Test description",
                confidence=1.5
            )

        # Invalid confidence - too low
        with pytest.raises(ValidationError):
            AccessibilityIssue(
                issue_id="issue123",
                type=AccessibilityType.VISUAL,
                severity=SeverityLevel.HIGH,
                title="Test issue",
                description="Test description",
                confidence=-0.1
            )


class TestAccessibilityAnalysis:
    """Test AccessibilityAnalysis model."""

    def test_valid_analysis(self):
        """Test creating a valid accessibility analysis."""
        analysis = AccessibilityAnalysis(
            type=AccessibilityType.VISUAL,
            status="completed",
            score=85.5,
            processing_time=2.5
        )

        assert analysis.type == AccessibilityType.VISUAL
        assert analysis.status == "completed"
        assert analysis.score == 85.5
        assert analysis.processing_time == 2.5
        assert isinstance(analysis.timestamp, datetime)

    def test_score_validation(self):
        """Test score validation."""
        # Valid score
        analysis = AccessibilityAnalysis(
            type=AccessibilityType.VISUAL,
            status="completed",
            score=50.0,
            processing_time=1.0
        )
        assert analysis.score == 50.0

        # Invalid score - too high
        with pytest.raises(ValidationError):
            AccessibilityAnalysis(
                type=AccessibilityType.VISUAL,
                status="completed",
                score=150.0,
                processing_time=1.0
            )

        # Invalid score - too low
        with pytest.raises(ValidationError):
            AccessibilityAnalysis(
                type=AccessibilityType.VISUAL,
                status="completed",
                score=-10.0,
                processing_time=1.0
            )


class TestAccessibilityResponse:
    """Test AccessibilityResponse model."""

    def test_valid_response(self):
        """Test creating a valid accessibility response."""
        analysis = AccessibilityAnalysis(
            type=AccessibilityType.VISUAL,
            status="completed",
            score=80.0,
            processing_time=1.5
        )

        response = AccessibilityResponse(
            request_id="req123",
            user_id="user123",
            analyses=[analysis],
            overall_score=80.0,
            total_issues=2,
            critical_issues=0,
            processing_time=2.0,
            status="completed"
        )

        assert response.request_id == "req123"
        assert response.user_id == "user123"
        assert len(response.analyses) == 1
        assert response.overall_score == 80.0
        assert response.total_issues == 2
        assert response.critical_issues == 0
        assert isinstance(response.timestamp, datetime)

    def test_overall_score_validation(self):
        """Test overall score validation against individual analyses."""
        analysis1 = AccessibilityAnalysis(
            type=AccessibilityType.VISUAL,
            status="completed",
            score=80.0,
            processing_time=1.0
        )

        analysis2 = AccessibilityAnalysis(
            type=AccessibilityType.AUDIO,
            status="completed",
            score=90.0,
            processing_time=1.0
        )

        # Valid overall score (average of 80 and 90 is 85)
        response = AccessibilityResponse(
            request_id="req123",
            user_id="user123",
            analyses=[analysis1, analysis2],
            overall_score=85.0,
            total_issues=0,
            critical_issues=0,
            processing_time=2.0,
            status="completed"
        )
        assert response.overall_score == 85.0

        # Invalid overall score (too far from average)
        with pytest.raises(ValidationError):
            AccessibilityResponse(
                request_id="req123",
                user_id="user123",
                analyses=[analysis1, analysis2],
                overall_score=95.0,  # Too far from 85
                total_issues=0,
                critical_issues=0,
                processing_time=2.0,
                status="completed"
            )
