"""
test_full_service_integration - 索克生活项目模块
"""

        import time
from accessibility_service.ai_models.audio_model import AudioModel
from accessibility_service.ai_models.vision_model import VisionModel
from accessibility_service.api.grpc.accessibility_pb2 import (
from accessibility_service.api.grpc.accessibility_pb2_grpc import AccessibilityServiceStub
from accessibility_service.api.grpc.accessibility_service import AccessibilityServiceImpl
from accessibility_service.core.service import AccessibilityService
from grpc import aio
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
import grpc
import io
import numpy as np
import pytest
import wave

"""
Comprehensive integration tests for the accessibility service.
Tests all major functionality and integration points.
"""


    BlindAssistanceRequest, BlindAssistanceResponse,
    SignLanguageRequest, SignLanguageResponse,
    ScreenReadingRequest, ScreenReadingResponse,
    VoiceAssistanceRequest, VoiceAssistanceResponse,
    AccessibleContentRequest, AccessibleContentResponse,
    SettingsRequest, SettingsResponse,
    BackgroundCollectionRequest, BackgroundCollectionResponse,
    HealthAlertRequest, HealthAlertResponse,
    SpeechTranslationRequest, SpeechTranslationResponse
)


class TestAccessibilityServiceIntegration:
    """Comprehensive integration tests for accessibility service."""
    
    @pytest.fixture
    async def service_impl(self):
        """Create and initialize service implementation."""
        service = AccessibilityServiceImpl()
        
        # Mock AI models to avoid loading actual models in tests
        service.vision_model = AsyncMock(spec=VisionModel)
        service.audio_model = AsyncMock(spec=AudioModel)
        service.accessibility_service = AsyncMock(spec=AccessibilityService)
        
        # Configure mock responses
        await self._configure_mock_responses(service)
        
        # Initialize service
        await service.initialize()
        
        yield service
        
        # Cleanup
        await service.shutdown()
    
    async def _configure_mock_responses(self, service):
        """Configure mock responses for AI models."""
        # Vision model mock responses
        service.vision_model.analyze_image.return_value = MagicMock(
            scene_description="A well-lit indoor room with furniture",
            navigation_guidance="Clear path ahead, no obstacles detected",
            detected_objects=[
                {"label": "chair", "confidence": 0.95, "bbox": [100, 100, 200, 200]},
                {"label": "table", "confidence": 0.88, "bbox": [300, 150, 450, 250]}
            ],
            accessibility_score=0.85,
            text_content="Welcome to our accessibility service",
            accessibility_barriers=["Low lighting in corner"],
            accessibility_info={"barrier": False}
        )
        
        # Audio model mock responses
        service.audio_model.recognize_speech.return_value = {
            "success": True,
            "text": "Hello, please describe what you see",
            "confidence": 0.92,
            "language": "en",
            "supported_language": True,
            "audio_quality": {"volume": 0.7, "clarity": 0.8}
        }
        
        service.audio_model.synthesize_speech.return_value = {
            "success": True,
            "audio_data": self._generate_mock_audio_data(),
            "sample_rate": 16000,
            "duration": 2.5,
            "language": "en",
            "voice_settings": {},
            "accessibility_enhancements": ["Volume normalization", "Speech enhancement"]
        }
        
        service.audio_model.analyze_audio.return_value = MagicMock(
            accessibility_score=0.8,
            issues=["Background noise detected"],
            recommendations=["Use noise cancellation"],
            speech_clarity=0.75,
            background_noise_level=0.3,
            volume_level=0.6,
            frequency_analysis={"low": 0.2, "mid": 0.6, "high": 0.2},
            detected_sounds=["speech", "background_noise"],
            language_detected="en"
        )
    
    def _generate_mock_audio_data(self) -> bytes:
        """Generate mock audio data for testing."""
        # Generate a simple sine wave
        sample_rate = 16000
        duration = 1.0  # 1 second
        frequency = 440  # A4 note
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = np.sin(2 * np.pi * frequency * t) * 0.3
        
        # Convert to 16-bit PCM
        audio_int16 = (audio_data * 32767).astype(np.int16)
        
        # Create WAV file in memory
        audio_io = io.BytesIO()
        with wave.open(audio_io, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_int16.tobytes())
        
        return audio_io.getvalue()
    
    @pytest.mark.asyncio
    async def test_blind_assistance_complete_workflow(self, service_impl):
        """Test complete blind assistance workflow."""
        # Create request with image and audio data
        request = BlindAssistanceRequest(
            user_id="test_user_001",
            image_data=b"mock_image_data",
            audio_data=self._generate_mock_audio_data(),
            language="en",
            detailed_descriptions=True,
            audio_feedback=True
        )
        
        # Create mock context
        context = MagicMock()
        context.peer.return_value = "test_peer"
        
        # Execute request
        response = await service_impl.BlindAssistance(request, context)
        
        # Verify response
        assert response.success is True
        assert response.scene_description != ""
        assert response.navigation_guidance != ""
        assert len(response.detected_objects) > 0
        assert response.accessibility_score > 0
        assert response.voice_command_recognized != ""
        assert response.error_message == ""
        
        # Verify AI models were called
        service_impl.vision_model.analyze_image.assert_called_once()
        service_impl.audio_model.recognize_speech.assert_called_once()
        service_impl.audio_model.synthesize_speech.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_sign_language_recognition_workflow(self, service_impl):
        """Test sign language recognition workflow."""
        request = SignLanguageRequest(
            user_id="test_user_002",
            image_data=b"mock_sign_language_image",
            sign_language_type="ASL",
            target_language="en"
        )
        
        context = MagicMock()
        
        response = await service_impl.SignLanguageRecognition(request, context)
        
        assert response.success is True
        assert response.recognized_text != ""
        assert response.translated_text != ""
        assert response.confidence > 0
        assert response.sign_language_detected == "ASL"
        
        service_impl.vision_model.analyze_image.assert_called()
    
    @pytest.mark.asyncio
    async def test_screen_reading_workflow(self, service_impl):
        """Test screen reading workflow."""
        request = ScreenReadingRequest(
            user_id="test_user_003",
            screen_data=b"mock_screen_capture",
            language="en",
            reading_speed=1.0,
            voice_type="default",
            generate_audio=True
        )
        
        context = MagicMock()
        
        response = await service_impl.ScreenReading(request, context)
        
        assert response.success is True
        assert response.extracted_text != ""
        assert len(response.ui_elements) >= 0
        assert len(response.reading_order) >= 0
        assert len(response.audio_data) > 0  # Audio should be generated
        
        service_impl.vision_model.analyze_image.assert_called()
        service_impl.audio_model.synthesize_speech.assert_called()
    
    @pytest.mark.asyncio
    async def test_voice_assistance_workflow(self, service_impl):
        """Test voice assistance workflow."""
        request = VoiceAssistanceRequest(
            user_id="test_user_004",
            audio_data=self._generate_mock_audio_data(),
            language="en",
            context="navigation_help",
            sensitivity=0.7
        )
        
        context = MagicMock()
        
        response = await service_impl.VoiceAssistance(request, context)
        
        assert response.success is True
        assert response.recognized_command != ""
        assert response.response_text != ""
        assert len(response.audio_response) > 0
        assert response.confidence > 0
        
        service_impl.audio_model.recognize_speech.assert_called()
        service_impl.audio_model.synthesize_speech.assert_called()
    
    @pytest.mark.asyncio
    async def test_accessible_content_generation_image(self, service_impl):
        """Test accessible content generation for images."""
        request = AccessibleContentRequest(
            user_id="test_user_005",
            content_type="image",
            input_data=b"mock_image_data",
            language="en",
            complexity_level="medium",
            output_format="text"
        )
        
        context = MagicMock()
        
        response = await service_impl.AccessibleContentGeneration(request, context)
        
        assert response.success is True
        assert response.accessible_content != ""
        assert response.alt_text != ""
        assert response.content_format == "text"
        
        service_impl.vision_model.analyze_image.assert_called()
    
    @pytest.mark.asyncio
    async def test_accessible_content_generation_audio(self, service_impl):
        """Test accessible content generation with audio output."""
        request = AccessibleContentRequest(
            user_id="test_user_006",
            content_type="image",
            input_data=b"mock_image_data",
            language="en",
            complexity_level="simple",
            output_format="audio"
        )
        
        context = MagicMock()
        
        response = await service_impl.AccessibleContentGeneration(request, context)
        
        assert response.success is True
        assert response.accessible_content != ""
        assert response.audio_description != ""  # Should contain hex-encoded audio
        assert response.content_format == "audio"
        
        service_impl.vision_model.analyze_image.assert_called()
        service_impl.audio_model.synthesize_speech.assert_called()
    
    @pytest.mark.asyncio
    async def test_settings_management(self, service_impl):
        """Test user settings management."""
        request = SettingsRequest(
            user_id="test_user_007",
            visual_impairment=True,
            hearing_impairment=False,
            motor_impairment=False,
            cognitive_impairment=False,
            preferred_language="en",
            voice_speed=1.2,
            font_size=16,
            high_contrast=True,
            audio_descriptions=True
        )
        
        context = MagicMock()
        context.peer.return_value = "test_peer_settings"
        
        response = await service_impl.UpdateSettings(request, context)
        
        assert response.success is True
        assert response.message == "Settings updated successfully"
        assert response.error_message == ""
        
        # Verify settings are stored
        assert "test_user_007" in service_impl._user_sessions
        user_settings = service_impl._user_sessions["test_user_007"]["settings"]
        assert user_settings["visual_impairment"] is True
        assert user_settings["preferred_language"] == "en"
        assert user_settings["voice_speed"] == 1.2
    
    @pytest.mark.asyncio
    async def test_background_data_collection(self, service_impl):
        """Test background data collection workflow."""
        request = BackgroundCollectionRequest(
            user_id="test_user_008",
            consent_given=True,
            data_types=["usage_patterns", "performance_metrics"],
            usage_data="mock_usage_data",
            performance_data="mock_performance_data",
            accessibility_feedback="Service works well, but could be faster"
        )
        
        context = MagicMock()
        
        response = await service_impl.BackgroundDataCollection(request, context)
        
        assert response.success is True
        assert response.collection_id != ""
        assert response.collection_id.startswith("bg_collection_test_user_008_")
        assert response.error_message == ""
        
        # Verify background task is stored
        assert response.collection_id in service_impl._background_tasks
        task_data = service_impl._background_tasks[response.collection_id]
        assert task_data["user_id"] == "test_user_008"
        assert task_data["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_background_data_collection_no_consent(self, service_impl):
        """Test background data collection without consent."""
        request = BackgroundCollectionRequest(
            user_id="test_user_009",
            consent_given=False,
            data_types=["usage_patterns"]
        )
        
        context = MagicMock()
        
        response = await service_impl.BackgroundDataCollection(request, context)
        
        assert response.success is False
        assert response.collection_id == ""
        assert "consent required" in response.error_message.lower()
    
    @pytest.mark.asyncio
    async def test_health_alert_emergency(self, service_impl):
        """Test emergency health alert processing."""
        request = HealthAlertRequest(
            user_id="test_user_010",
            alert_type="emergency",
            alert_data="User has fallen and needs immediate help",
            timestamp=1234567890
        )
        
        context = MagicMock()
        
        response = await service_impl.HealthAlert(request, context)
        
        assert response.success is True
        assert response.alert_processed is True
        assert response.severity_level == "emergency"
        assert len(response.response_actions) > 0
        assert len(response.notifications_sent) > 0
        assert "Emergency services contacted" in response.response_actions
        assert "Emergency services" in response.notifications_sent
    
    @pytest.mark.asyncio
    async def test_health_alert_warning(self, service_impl):
        """Test warning health alert processing."""
        request = HealthAlertRequest(
            user_id="test_user_011",
            alert_type="warning",
            alert_data="Blood pressure reading is elevated",
            timestamp=1234567890
        )
        
        context = MagicMock()
        
        response = await service_impl.HealthAlert(request, context)
        
        assert response.success is True
        assert response.alert_processed is True
        assert response.severity_level == "warning"
        assert len(response.response_actions) > 0
        assert "Health status logged" in response.response_actions
        assert "Primary caregiver" in response.notifications_sent
    
    @pytest.mark.asyncio
    async def test_speech_translation_workflow(self, service_impl):
        """Test speech translation workflow."""
        request = SpeechTranslationRequest(
            user_id="test_user_012",
            audio_data=self._generate_mock_audio_data(),
            source_language="en",
            target_language="es",
            generate_audio=True
        )
        
        context = MagicMock()
        
        response = await service_impl.SpeechTranslation(request, context)
        
        assert response.success is True
        assert response.recognized_text != ""
        assert response.translated_text != ""
        assert len(response.translated_audio) > 0
        assert response.confidence > 0
        assert response.source_language_detected == "en"
        
        service_impl.audio_model.recognize_speech.assert_called()
        service_impl.audio_model.synthesize_speech.assert_called()
    
    @pytest.mark.asyncio
    async def test_user_preferences_persistence(self, service_impl):
        """Test that user preferences persist across requests."""
        # First, set user preferences
        settings_request = SettingsRequest(
            user_id="test_user_013",
            visual_impairment=True,
            preferred_language="es",
            voice_speed=0.8
        )
        
        context = MagicMock()
        context.peer.return_value = "test_peer"
        
        await service_impl.UpdateSettings(settings_request, context)
        
        # Then make a request that should use these preferences
        blind_assistance_request = BlindAssistanceRequest(
            user_id="test_user_013",
            image_data=b"mock_image_data",
            audio_feedback=True
        )
        
        response = await service_impl.BlindAssistance(blind_assistance_request, context)
        
        assert response.success is True
        
        # Verify that the user preferences were used
        # Check the calls to AI models to see if preferences were passed
        vision_call_args = service_impl.vision_model.analyze_image.call_args
        user_prefs = vision_call_args[1]["user_preferences"]
        assert user_prefs["visual_impairment"] is True
        assert user_prefs["preferred_language"] == "es"
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_image_data(self, service_impl):
        """Test error handling with invalid image data."""
        # Configure vision model to raise an exception
        service_impl.vision_model.analyze_image.side_effect = Exception("Invalid image format")
        
        request = BlindAssistanceRequest(
            user_id="test_user_014",
            image_data=b"invalid_image_data",
            language="en"
        )
        
        context = MagicMock()
        
        response = await service_impl.BlindAssistance(request, context)
        
        assert response.success is False
        assert response.error_message != ""
        assert "Invalid image format" in response.error_message
        
        # Verify error metrics are updated
        assert service_impl.metrics["errors_encountered"] > 0
    
    @pytest.mark.asyncio
    async def test_error_handling_audio_processing_failure(self, service_impl):
        """Test error handling with audio processing failure."""
        # Configure audio model to raise an exception
        service_impl.audio_model.recognize_speech.side_effect = Exception("Audio processing failed")
        
        request = VoiceAssistanceRequest(
            user_id="test_user_015",
            audio_data=self._generate_mock_audio_data(),
            language="en"
        )
        
        context = MagicMock()
        
        response = await service_impl.VoiceAssistance(request, context)
        
        assert response.success is False
        assert response.error_message != ""
        assert "Audio processing failed" in response.error_message
    
    @pytest.mark.asyncio
    async def test_service_metrics_tracking(self, service_impl):
        """Test that service metrics are properly tracked."""
        initial_requests = service_impl.metrics["requests_processed"]
        initial_errors = service_impl.metrics["errors_encountered"]
        
        # Make a successful request
        request = BlindAssistanceRequest(
            user_id="test_user_016",
            image_data=b"mock_image_data"
        )
        
        context = MagicMock()
        
        await service_impl.BlindAssistance(request, context)
        
        # Verify metrics are updated
        assert service_impl.metrics["requests_processed"] == initial_requests + 1
        assert service_impl.metrics["average_response_time"] > 0
        
        # Make a request that causes an error
        service_impl.vision_model.analyze_image.side_effect = Exception("Test error")
        
        await service_impl.BlindAssistance(request, context)
        
        # Verify error metrics are updated
        assert service_impl.metrics["errors_encountered"] == initial_errors + 1
    
    @pytest.mark.asyncio
    async def test_concurrent_requests_handling(self, service_impl):
        """Test handling of concurrent requests."""
        # Create multiple requests
        requests = []
        contexts = []
        
        for i in range(5):
            request = BlindAssistanceRequest(
                user_id=f"test_user_concurrent_{i}",
                image_data=b"mock_image_data"
            )
            context = MagicMock()
            context.peer.return_value = f"test_peer_{i}"
            
            requests.append(request)
            contexts.append(context)
        
        # Execute requests concurrently
        tasks = [
            service_impl.BlindAssistance(req, ctx)
            for req, ctx in zip(requests, contexts)
        ]
        
        responses = await asyncio.gather(*tasks)
        
        # Verify all requests succeeded
        for response in responses:
            assert response.success is True
        
        # Verify metrics reflect all requests
        assert service_impl.metrics["requests_processed"] >= 5
    
    @pytest.mark.asyncio
    async def test_service_info_endpoint(self, service_impl):
        """Test service information retrieval."""
        service_info = service_impl.get_service_info()
        
        assert service_info["service_name"] == "AccessibilityService"
        assert service_info["version"] == "1.0.0"
        assert service_info["initialized"] is True
        assert "features_enabled" in service_info
        assert "metrics" in service_info
        assert "ai_models" in service_info
        
        # Verify feature flags
        features = service_info["features_enabled"]
        assert features["blind_assistance"] is True
        assert features["sign_language"] is True
        assert features["screen_reading"] is True
        assert features["voice_assistance"] is True
    
    @pytest.mark.asyncio
    async def test_service_shutdown_cleanup(self, service_impl):
        """Test proper cleanup during service shutdown."""
        # Add some session data
        service_impl._user_sessions["test_user"] = {"settings": {}}
        service_impl._background_tasks["test_task"] = {"status": "running"}
        
        # Shutdown service
        await service_impl.shutdown()
        
        # Verify cleanup
        assert len(service_impl._user_sessions) == 0
        assert len(service_impl._background_tasks) == 0
        assert service_impl._initialized is False
        
        # Verify AI models were shutdown
        service_impl.vision_model.shutdown.assert_called_once()
        service_impl.audio_model.shutdown.assert_called_once()
        service_impl.accessibility_service.shutdown.assert_called_once()


class TestAccessibilityServicePerformance:
    """Performance tests for accessibility service."""
    
    @pytest.fixture
    async def service_impl(self):
        """Create service implementation for performance testing."""
        service = AccessibilityServiceImpl()
        
        # Use lightweight mocks for performance testing
        service.vision_model = AsyncMock()
        service.audio_model = AsyncMock()
        service.accessibility_service = AsyncMock()
        
        # Configure fast mock responses
        service.vision_model.analyze_image.return_value = MagicMock(
            scene_description="Test scene",
            navigation_guidance="Test guidance",
            detected_objects=[],
            accessibility_score=0.8,
            text_content="Test text",
            accessibility_barriers=[],
            accessibility_info={"barrier": False}
        )
        
        service.audio_model.recognize_speech.return_value = {
            "success": True,
            "text": "Test command",
            "confidence": 0.9,
            "language": "en"
        }
        
        service.audio_model.synthesize_speech.return_value = {
            "success": True,
            "audio_data": b"mock_audio",
            "sample_rate": 16000
        }
        
        await service.initialize()
        yield service
        await service.shutdown()
    
    @pytest.mark.asyncio
    async def test_response_time_blind_assistance(self, service_impl):
        """Test response time for blind assistance requests."""
        
        request = BlindAssistanceRequest(
            user_id="perf_test_user",
            image_data=b"mock_image_data"
        )
        
        context = MagicMock()
        
        start_time = time.time()
        response = await service_impl.BlindAssistance(request, context)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.success is True
        assert response_time < 1.0  # Should respond within 1 second
        
        # Verify average response time is tracked
        assert service_impl.metrics["average_response_time"] > 0
    
    @pytest.mark.asyncio
    async def test_throughput_multiple_requests(self, service_impl):
        """Test service throughput with multiple concurrent requests."""
        
        num_requests = 10
        requests = []
        contexts = []
        
        for i in range(num_requests):
            request = VoiceAssistanceRequest(
                user_id=f"perf_user_{i}",
                audio_data=b"mock_audio_data",
                language="en"
            )
            context = MagicMock()
            
            requests.append(request)
            contexts.append(context)
        
        start_time = time.time()
        
        # Execute all requests concurrently
        tasks = [
            service_impl.VoiceAssistance(req, ctx)
            for req, ctx in zip(requests, contexts)
        ]
        
        responses = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify all requests succeeded
        for response in responses:
            assert response.success is True
        
        # Calculate throughput
        throughput = num_requests / total_time
        
        # Should handle at least 5 requests per second
        assert throughput >= 5.0
        
        print(f"Throughput: {throughput:.2f} requests/second")


class TestAccessibilityServiceEdgeCases:
    """Edge case tests for accessibility service."""
    
    @pytest.fixture
    async def service_impl(self):
        """Create service implementation for edge case testing."""
        service = AccessibilityServiceImpl()
        
        # Configure mocks for edge cases
        service.vision_model = AsyncMock()
        service.audio_model = AsyncMock()
        service.accessibility_service = AsyncMock()
        
        await service.initialize()
        yield service
        await service.shutdown()
    
    @pytest.mark.asyncio
    async def test_empty_image_data(self, service_impl):
        """Test handling of empty image data."""
        request = BlindAssistanceRequest(
            user_id="edge_case_user_001",
            image_data=b"",  # Empty image data
            language="en"
        )
        
        context = MagicMock()
        
        response = await service_impl.BlindAssistance(request, context)
        
        # Should handle gracefully
        assert response.scene_description == ""
        assert response.navigation_guidance == ""
        assert len(response.detected_objects) == 0
    
    @pytest.mark.asyncio
    async def test_unsupported_language(self, service_impl):
        """Test handling of unsupported language."""
        # Configure audio model to return unsupported language
        service_impl.audio_model.recognize_speech.return_value = {
            "success": True,
            "text": "Unsupported language text",
            "confidence": 0.8,
            "language": "xyz",  # Unsupported language code
            "supported_language": False
        }
        
        request = VoiceAssistanceRequest(
            user_id="edge_case_user_002",
            audio_data=b"mock_audio_data",
            language="xyz"  # Unsupported language
        )
        
        context = MagicMock()
        
        response = await service_impl.VoiceAssistance(request, context)
        
        # Should still process but may have limitations
        assert response.recognized_command != ""
    
    @pytest.mark.asyncio
    async def test_very_long_text_content(self, service_impl):
        """Test handling of very long text content."""
        # Create very long text (10,000 characters)
        long_text = "This is a very long text. " * 400
        
        request = AccessibleContentRequest(
            user_id="edge_case_user_003",
            content_type="text",
            text_content=long_text,
            language="en",
            complexity_level="simple"
        )
        
        context = MagicMock()
        
        response = await service_impl.AccessibleContentGeneration(request, context)
        
        # Should handle long text gracefully
        assert response.success is True
        assert response.accessible_content != ""
        # Simplified text should be shorter than original
        assert len(response.accessible_content) <= len(long_text)
    
    @pytest.mark.asyncio
    async def test_malformed_audio_data(self, service_impl):
        """Test handling of malformed audio data."""
        # Configure audio model to handle malformed data
        service_impl.audio_model.recognize_speech.return_value = {
            "success": False,
            "text": "",
            "confidence": 0.0,
            "language": "unknown",
            "error": "Invalid audio format"
        }
        
        request = SpeechTranslationRequest(
            user_id="edge_case_user_004",
            audio_data=b"malformed_audio_data",
            source_language="en",
            target_language="es"
        )
        
        context = MagicMock()
        
        response = await service_impl.SpeechTranslation(request, context)
        
        # Should handle gracefully without crashing
        assert response.recognized_text == ""
        assert response.translated_text == ""
        assert response.confidence == 0.0
    
    @pytest.mark.asyncio
    async def test_maximum_concurrent_users(self, service_impl):
        """Test handling of maximum concurrent users."""
        max_users = 100
        tasks = []
        
        for i in range(max_users):
            request = SettingsRequest(
                user_id=f"concurrent_user_{i:03d}",
                visual_impairment=True,
                preferred_language="en"
            )
            
            context = MagicMock()
            context.peer.return_value = f"peer_{i}"
            
            task = service_impl.UpdateSettings(request, context)
            tasks.append(task)
        
        # Execute all settings updates concurrently
        responses = await asyncio.gather(*tasks)
        
        # Verify all succeeded
        for response in responses:
            assert response.success is True
        
        # Verify all users are tracked
        assert len(service_impl._user_sessions) == max_users
    
    @pytest.mark.asyncio
    async def test_service_recovery_after_error(self, service_impl):
        """Test service recovery after encountering errors."""
        # First request that causes an error
        service_impl.vision_model.analyze_image.side_effect = Exception("Temporary error")
        
        request1 = BlindAssistanceRequest(
            user_id="recovery_test_user",
            image_data=b"mock_image_data"
        )
        
        context = MagicMock()
        
        response1 = await service_impl.BlindAssistance(request1, context)
        assert response1.success is False
        
        # Reset the mock to work normally
        service_impl.vision_model.analyze_image.side_effect = None
        service_impl.vision_model.analyze_image.return_value = MagicMock(
            scene_description="Recovery test scene",
            navigation_guidance="Recovery guidance",
            detected_objects=[],
            accessibility_score=0.8,
            text_content="",
            accessibility_barriers=[],
            accessibility_info={"barrier": False}
        )
        
        # Second request should succeed
        response2 = await service_impl.BlindAssistance(request1, context)
        assert response2.success is True
        assert response2.scene_description == "Recovery test scene"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--asyncio-mode=auto"]) 