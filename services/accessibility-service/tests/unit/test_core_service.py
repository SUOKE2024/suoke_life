"""
test_core_service - 索克生活项目模块
"""

from accessibility_service.core.service import AccessibilityService
from accessibility_service.models.accessibility import (
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
import pytest

"""
Unit tests for the core accessibility service.
"""


    AccessibilityRequest,
    AccessibilityResponse,
    VisualAnalysis,
    AudioAnalysis,
    MotorAnalysis,
    CognitiveAnalysis
)


class TestAccessibilityService:
    """Test cases for AccessibilityService."""

    @pytest.fixture
    async def service(self):
        """Create a test accessibility service instance."""
        service = AccessibilityService()
        yield service
        await service.shutdown()

    @pytest.fixture
    def sample_request(self):
        """Create a sample accessibility request."""
        return AccessibilityRequest(
            user_id="test_user_123",
            session_id="session_456",
            timestamp=1640995200.0,
            content_type="text",
            content="Sample content for accessibility analysis",
            user_preferences={
                "visual_impairment": True,
                "hearing_impairment": False,
                "motor_impairment": False,
                "cognitive_impairment": False
            },
            context={
                "device_type": "mobile",
                "platform": "ios",
                "app_version": "1.0.0"
            }
        )

    @pytest.mark.asyncio
    async def test_service_initialization(self, service):
        """Test service initialization."""
        assert not service._initialized
        
        with patch.object(service.visual_service, 'initialize', new_callable=AsyncMock) as mock_visual, \
             patch.object(service.audio_service, 'initialize', new_callable=AsyncMock) as mock_audio, \
             patch.object(service.motor_service, 'initialize', new_callable=AsyncMock) as mock_motor, \
             patch.object(service.cognitive_service, 'initialize', new_callable=AsyncMock) as mock_cognitive, \
             patch.object(service.integration_service, 'initialize', new_callable=AsyncMock) as mock_integration:
            
            await service.initialize()
            
            assert service._initialized
            mock_visual.assert_called_once()
            mock_audio.assert_called_once()
            mock_motor.assert_called_once()
            mock_cognitive.assert_called_once()
            mock_integration.assert_called_once()

    @pytest.mark.asyncio
    async def test_service_initialization_idempotent(self, service):
        """Test that service initialization is idempotent."""
        with patch.object(service.visual_service, 'initialize', new_callable=AsyncMock) as mock_init:
            await service.initialize()
            await service.initialize()  # Second call should not reinitialize
            
            mock_init.assert_called_once()

    @pytest.mark.asyncio
    async def test_service_initialization_failure(self, service):
        """Test service initialization failure handling."""
        with patch.object(service.visual_service, 'initialize', new_callable=AsyncMock) as mock_init:
            mock_init.side_effect = Exception("Initialization failed")
            
            with pytest.raises(Exception, match="Initialization failed"):
                await service.initialize()
            
            assert not service._initialized

    @pytest.mark.asyncio
    async def test_analyze_accessibility_success(self, service, sample_request):
        """Test successful accessibility analysis."""
        # Mock sub-service responses
        visual_result = {"visual_score": 0.8, "issues": ["low_contrast"]}
        audio_result = {"audio_score": 0.9, "issues": []}
        motor_result = {"motor_score": 0.7, "issues": ["small_targets"]}
        cognitive_result = {"cognitive_score": 0.85, "issues": ["complex_language"]}
        
        integrated_response = AccessibilityResponse(
            request_id=sample_request.session_id,
            user_id=sample_request.user_id,
            timestamp=sample_request.timestamp,
            overall_score=0.8,
            visual_analysis=VisualAnalysis(
                accessibility_score=0.8,
                issues=["low_contrast"],
                recommendations=["Increase contrast ratio"]
            ),
            audio_analysis=AudioAnalysis(
                accessibility_score=0.9,
                issues=[],
                recommendations=[]
            ),
            motor_analysis=MotorAnalysis(
                accessibility_score=0.7,
                issues=["small_targets"],
                recommendations=["Increase touch target size"]
            ),
            cognitive_analysis=CognitiveAnalysis(
                accessibility_score=0.85,
                issues=["complex_language"],
                recommendations=["Simplify language"]
            ),
            recommendations=["Improve contrast", "Increase target size"],
            metadata={"processing_time": 0.5}
        )

        with patch.object(service, '_analyze_visual', new_callable=AsyncMock) as mock_visual, \
             patch.object(service, '_analyze_audio', new_callable=AsyncMock) as mock_audio, \
             patch.object(service, '_analyze_motor', new_callable=AsyncMock) as mock_motor, \
             patch.object(service, '_analyze_cognitive', new_callable=AsyncMock) as mock_cognitive, \
             patch.object(service.integration_service, 'integrate_results', new_callable=AsyncMock) as mock_integrate:
            
            mock_visual.return_value = visual_result
            mock_audio.return_value = audio_result
            mock_motor.return_value = motor_result
            mock_cognitive.return_value = cognitive_result
            mock_integrate.return_value = integrated_response
            
            result = await service.analyze_accessibility(sample_request)
            
            assert result == integrated_response
            mock_visual.assert_called_once_with(sample_request)
            mock_audio.assert_called_once_with(sample_request)
            mock_motor.assert_called_once_with(sample_request)
            mock_cognitive.assert_called_once_with(sample_request)
            mock_integrate.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_accessibility_with_partial_failures(self, service, sample_request):
        """Test accessibility analysis with some sub-service failures."""
        visual_result = {"visual_score": 0.8}
        audio_exception = Exception("Audio analysis failed")
        motor_result = {"motor_score": 0.7}
        cognitive_exception = Exception("Cognitive analysis failed")
        
        integrated_response = AccessibilityResponse(
            request_id=sample_request.session_id,
            user_id=sample_request.user_id,
            timestamp=sample_request.timestamp,
            overall_score=0.75,
            visual_analysis=VisualAnalysis(accessibility_score=0.8),
            motor_analysis=MotorAnalysis(accessibility_score=0.7),
            recommendations=["Partial analysis completed"],
            metadata={"partial_failure": True}
        )

        with patch.object(service, '_analyze_visual', new_callable=AsyncMock) as mock_visual, \
             patch.object(service, '_analyze_audio', new_callable=AsyncMock) as mock_audio, \
             patch.object(service, '_analyze_motor', new_callable=AsyncMock) as mock_motor, \
             patch.object(service, '_analyze_cognitive', new_callable=AsyncMock) as mock_cognitive, \
             patch.object(service.integration_service, 'integrate_results', new_callable=AsyncMock) as mock_integrate:
            
            mock_visual.return_value = visual_result
            mock_audio.side_effect = audio_exception
            mock_motor.return_value = motor_result
            mock_cognitive.side_effect = cognitive_exception
            mock_integrate.return_value = integrated_response
            
            result = await service.analyze_accessibility(sample_request)
            
            assert result == integrated_response
            # Verify integrate_results was called with None for failed services
            args, kwargs = mock_integrate.call_args
            assert kwargs['visual'] == visual_result
            assert kwargs['audio'] is None
            assert kwargs['motor'] == motor_result
            assert kwargs['cognitive'] is None

    @pytest.mark.asyncio
    async def test_get_recommendations(self, service):
        """Test getting accessibility recommendations."""
        expected_recommendations = [
            {"type": "visual", "priority": "high", "description": "Increase contrast"},
            {"type": "motor", "priority": "medium", "description": "Larger touch targets"}
        ]
        
        with patch.object(service.integration_service, 'get_recommendations', new_callable=AsyncMock) as mock_get_rec:
            mock_get_rec.return_value = expected_recommendations
            
            result = await service.get_recommendations("test_user", "visual")
            
            assert result == expected_recommendations
            mock_get_rec.assert_called_once_with(user_id="test_user", accessibility_type="visual")

    @pytest.mark.asyncio
    async def test_update_user_preferences(self, service):
        """Test updating user preferences."""
        preferences = {
            "visual_impairment": True,
            "preferred_contrast": "high",
            "font_size": "large"
        }
        
        with patch.object(service.integration_service, 'update_user_preferences', new_callable=AsyncMock) as mock_update:
            mock_update.return_value = True
            
            result = await service.update_user_preferences("test_user", preferences)
            
            assert result is True
            mock_update.assert_called_once_with(user_id="test_user", preferences=preferences)

    @pytest.mark.asyncio
    async def test_get_service_status(self, service):
        """Test getting service status."""
        expected_status = {
            "visual_service": {"status": "healthy", "last_check": "2024-01-01T00:00:00Z"},
            "audio_service": {"status": "healthy", "last_check": "2024-01-01T00:00:00Z"},
            "motor_service": {"status": "healthy", "last_check": "2024-01-01T00:00:00Z"},
            "cognitive_service": {"status": "healthy", "last_check": "2024-01-01T00:00:00Z"}
        }
        
        with patch.object(service.visual_service, 'get_status') as mock_visual_status, \
             patch.object(service.audio_service, 'get_status') as mock_audio_status, \
             patch.object(service.motor_service, 'get_status') as mock_motor_status, \
             patch.object(service.cognitive_service, 'get_status') as mock_cognitive_status:
            
            mock_visual_status.return_value = expected_status["visual_service"]
            mock_audio_status.return_value = expected_status["audio_service"]
            mock_motor_status.return_value = expected_status["motor_service"]
            mock_cognitive_status.return_value = expected_status["cognitive_service"]
            
            result = await service.get_service_status()
            
            assert result == expected_status

    def test_get_health_status(self, service):
        """Test getting health status."""
        with patch.object(service.platform_checker, 'get_platform_info') as mock_platform:
            mock_platform.return_value = {"platform": "test", "version": "1.0"}
            
            status = service.get_health_status()
            
            assert "status" in status
            assert "timestamp" in status
            assert "version" in status
            assert "platform_info" in status
            assert status["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_shutdown(self, service):
        """Test service shutdown."""
        with patch.object(service.visual_service, 'shutdown', new_callable=AsyncMock) as mock_visual, \
             patch.object(service.audio_service, 'shutdown', new_callable=AsyncMock) as mock_audio, \
             patch.object(service.motor_service, 'shutdown', new_callable=AsyncMock) as mock_motor, \
             patch.object(service.cognitive_service, 'shutdown', new_callable=AsyncMock) as mock_cognitive, \
             patch.object(service.integration_service, 'shutdown', new_callable=AsyncMock) as mock_integration:
            
            await service.shutdown()
            
            mock_visual.assert_called_once()
            mock_audio.assert_called_once()
            mock_motor.assert_called_once()
            mock_cognitive.assert_called_once()
            mock_integration.assert_called_once()

    @pytest.mark.asyncio
    async def test_auto_initialization_on_analyze(self, service, sample_request):
        """Test that service auto-initializes when analyze is called."""
        with patch.object(service, 'initialize', new_callable=AsyncMock) as mock_init, \
             patch.object(service, '_analyze_visual', new_callable=AsyncMock), \
             patch.object(service, '_analyze_audio', new_callable=AsyncMock), \
             patch.object(service, '_analyze_motor', new_callable=AsyncMock), \
             patch.object(service, '_analyze_cognitive', new_callable=AsyncMock), \
             patch.object(service.integration_service, 'integrate_results', new_callable=AsyncMock):
            
            await service.analyze_accessibility(sample_request)
            
            mock_init.assert_called_once()

    @pytest.mark.asyncio
    async def test_auto_initialization_on_recommendations(self, service):
        """Test that service auto-initializes when getting recommendations."""
        with patch.object(service, 'initialize', new_callable=AsyncMock) as mock_init, \
             patch.object(service.integration_service, 'get_recommendations', new_callable=AsyncMock):
            
            await service.get_recommendations("test_user")
            
            mock_init.assert_called_once()

    @pytest.mark.asyncio
    async def test_auto_initialization_on_preferences_update(self, service):
        """Test that service auto-initializes when updating preferences."""
        with patch.object(service, 'initialize', new_callable=AsyncMock) as mock_init, \
             patch.object(service.integration_service, 'update_user_preferences', new_callable=AsyncMock):
            
            await service.update_user_preferences("test_user", {})
            
            mock_init.assert_called_once()

    @pytest.mark.asyncio
    async def test_auto_initialization_on_status_check(self, service):
        """Test that service auto-initializes when checking status."""
        with patch.object(service, 'initialize', new_callable=AsyncMock) as mock_init, \
             patch.object(service.visual_service, 'get_status'), \
             patch.object(service.audio_service, 'get_status'), \
             patch.object(service.motor_service, 'get_status'), \
             patch.object(service.cognitive_service, 'get_status'):
            
            await service.get_service_status()
            
            mock_init.assert_called_once()


@pytest.mark.asyncio
async def test_service_lifecycle():
    """Test complete service lifecycle."""
    service = AccessibilityService()
    
    # Test initialization
    with patch.object(service.visual_service, 'initialize', new_callable=AsyncMock), \
         patch.object(service.audio_service, 'initialize', new_callable=AsyncMock), \
         patch.object(service.motor_service, 'initialize', new_callable=AsyncMock), \
         patch.object(service.cognitive_service, 'initialize', new_callable=AsyncMock), \
         patch.object(service.integration_service, 'initialize', new_callable=AsyncMock):
        
        await service.initialize()
        assert service._initialized
    
    # Test shutdown
    with patch.object(service.visual_service, 'shutdown', new_callable=AsyncMock), \
         patch.object(service.audio_service, 'shutdown', new_callable=AsyncMock), \
         patch.object(service.motor_service, 'shutdown', new_callable=AsyncMock), \
         patch.object(service.cognitive_service, 'shutdown', new_callable=AsyncMock), \
         patch.object(service.integration_service, 'shutdown', new_callable=AsyncMock):
        
        await service.shutdown()


@pytest.mark.asyncio
async def test_concurrent_analysis_requests():
    """Test handling multiple concurrent analysis requests."""
    service = AccessibilityService()
    
    requests = [
        AccessibilityRequest(
            user_id=f"user_{i}",
            session_id=f"session_{i}",
            timestamp=1640995200.0 + i,
            content_type="text",
            content=f"Content {i}"
        )
        for i in range(5)
    ]
    
    with patch.object(service, '_analyze_visual', new_callable=AsyncMock) as mock_visual, \
         patch.object(service, '_analyze_audio', new_callable=AsyncMock) as mock_audio, \
         patch.object(service, '_analyze_motor', new_callable=AsyncMock) as mock_motor, \
         patch.object(service, '_analyze_cognitive', new_callable=AsyncMock) as mock_cognitive, \
         patch.object(service.integration_service, 'integrate_results', new_callable=AsyncMock) as mock_integrate:
        
        mock_visual.return_value = {"visual_score": 0.8}
        mock_audio.return_value = {"audio_score": 0.9}
        mock_motor.return_value = {"motor_score": 0.7}
        mock_cognitive.return_value = {"cognitive_score": 0.85}
        mock_integrate.return_value = AccessibilityResponse(
            request_id="test",
            user_id="test",
            timestamp=1640995200.0,
            overall_score=0.8
        )
        
        # Execute concurrent requests
        results = await asyncio.gather(*[
            service.analyze_accessibility(req) for req in requests
        ])
        
        assert len(results) == 5
        assert all(isinstance(result, AccessibilityResponse) for result in results)
        
        # Verify all sub-services were called for each request
        assert mock_visual.call_count == 5
        assert mock_audio.call_count == 5
        assert mock_motor.call_count == 5
        assert mock_cognitive.call_count == 5
        assert mock_integrate.call_count == 5
    
    await service.shutdown() 