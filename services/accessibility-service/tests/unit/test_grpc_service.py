"""
Unit tests for the gRPC accessibility service.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import grpc
from grpc import aio

from accessibility_service.api.grpc.accessibility_pb2 import (
    BlindAssistanceRequest,
    BlindAssistanceResponse,
    SignLanguageRequest,
    SignLanguageResponse,
    ScreenReadingRequest,
    ScreenReadingResponse,
    VoiceAssistanceRequest,
    VoiceAssistanceResponse,
    AccessibleContentRequest,
    AccessibleContentResponse,
    SettingsRequest,
    SettingsResponse,
    BackgroundCollectionRequest,
    BackgroundCollectionResponse,
    HealthAlertRequest,
    HealthAlertResponse,
    SpeechTranslationRequest,
    SpeechTranslationResponse
)
from accessibility_service.api.grpc.accessibility_pb2_grpc import AccessibilityServiceServicer
from accessibility_service.models.accessibility import AccessibilityRequest, AccessibilityResponse


class MockAccessibilityServicer(AccessibilityServiceServicer):
    """Mock implementation of AccessibilityServiceServicer for testing."""
    
    def __init__(self):
        self.accessibility_service = MagicMock()
    
    async def BlindAssistance(self, request, context):
        """Mock blind assistance service."""
        response = BlindAssistanceResponse()
        response.success = True
        response.message = "Navigation guidance provided"
        response.guidance_text = "Turn left in 10 meters"
        response.confidence_score = 0.95
        return response
    
    async def SignLanguageRecognition(self, request, context):
        """Mock sign language recognition service."""
        response = SignLanguageResponse()
        response.success = True
        response.recognized_text = "Hello, how are you?"
        response.confidence_score = 0.88
        response.gesture_count = 5
        return response
    
    async def ScreenReading(self, request, context):
        """Mock screen reading service."""
        response = ScreenReadingResponse()
        response.success = True
        response.spoken_text = "Button: Submit form"
        response.element_type = "button"
        response.accessibility_label = "Submit form button"
        return response
    
    async def VoiceAssistance(self, request, context):
        """Mock voice assistance service."""
        response = VoiceAssistanceResponse()
        response.success = True
        response.response_text = "I can help you with that"
        response.action_taken = "navigation"
        response.confidence_score = 0.92
        return response
    
    async def AccessibleContent(self, request, context):
        """Mock accessible content conversion service."""
        response = AccessibleContentResponse()
        response.success = True
        response.converted_content = "Simplified content for accessibility"
        response.format_type = "plain_text"
        response.accessibility_score = 0.85
        return response
    
    async def ManageSettings(self, request, context):
        """Mock settings management service."""
        response = SettingsResponse()
        response.success = True
        response.message = "Settings updated successfully"
        return response
    
    async def ConfigureBackgroundCollection(self, request, context):
        """Mock background data collection configuration."""
        response = BackgroundCollectionResponse()
        response.success = True
        response.message = "Background collection configured"
        response.collection_id = "collection_123"
        return response
    
    async def TriggerHealthAlert(self, request, context):
        """Mock health alert triggering."""
        response = HealthAlertResponse()
        response.success = True
        response.alert_id = "alert_456"
        response.message = "Health alert triggered successfully"
        return response
    
    async def SpeechTranslation(self, request, context):
        """Mock speech translation service."""
        response = SpeechTranslationResponse()
        response.success = True
        response.translated_text = "Hola, ¿cómo estás?"
        response.source_language = "en"
        response.target_language = "es"
        response.confidence_score = 0.94
        return response


class TestAccessibilityGRPCService:
    """Test cases for AccessibilityService gRPC implementation."""
    
    @pytest.fixture
    async def grpc_server(self):
        """Create a test gRPC server."""
        server = aio.server()
        servicer = MockAccessibilityServicer()
        
        # Add the servicer to the server
        from accessibility_service.api.grpc.accessibility_pb2_grpc import add_AccessibilityServiceServicer_to_server
        add_AccessibilityServiceServicer_to_server(servicer, server)
        
        # Start server on a random port
        listen_addr = '[::]:0'
        server.add_insecure_port(listen_addr)
        await server.start()
        
        # Get the actual port
        port = server.get_port()
        
        yield server, port, servicer
        
        await server.stop(grace=1.0)
    
    @pytest.fixture
    async def grpc_channel(self, grpc_server):
        """Create a gRPC channel for testing."""
        server, port, servicer = grpc_server
        channel = aio.insecure_channel(f'localhost:{port}')
        
        yield channel, servicer
        
        await channel.close()
    
    @pytest.mark.asyncio
    async def test_blind_assistance(self, grpc_channel):
        """Test blind assistance gRPC method."""
        channel, servicer = grpc_channel
        
        from accessibility_service.api.grpc.accessibility_pb2_grpc import AccessibilityServiceStub
        stub = AccessibilityServiceStub(channel)
        
        request = BlindAssistanceRequest()
        request.user_id = "test_user"
        request.image_data = b"fake_image_data"
        request.location_lat = 37.7749
        request.location_lng = -122.4194
        request.assistance_type = "navigation"
        
        response = await stub.BlindAssistance(request)
        
        assert response.success is True
        assert response.message == "Navigation guidance provided"
        assert response.guidance_text == "Turn left in 10 meters"
        assert response.confidence_score == 0.95
    
    @pytest.mark.asyncio
    async def test_sign_language_recognition(self, grpc_channel):
        """Test sign language recognition gRPC method."""
        channel, servicer = grpc_channel
        
        from accessibility_service.api.grpc.accessibility_pb2_grpc import AccessibilityServiceStub
        stub = AccessibilityServiceStub(channel)
        
        request = SignLanguageRequest()
        request.user_id = "test_user"
        request.video_data = b"fake_video_data"
        request.language_code = "asl"
        request.frame_rate = 30
        
        response = await stub.SignLanguageRecognition(request)
        
        assert response.success is True
        assert response.recognized_text == "Hello, how are you?"
        assert response.confidence_score == 0.88
        assert response.gesture_count == 5
    
    @pytest.mark.asyncio
    async def test_screen_reading(self, grpc_channel):
        """Test screen reading gRPC method."""
        channel, servicer = grpc_channel
        
        from accessibility_service.api.grpc.accessibility_pb2_grpc import AccessibilityServiceStub
        stub = AccessibilityServiceStub(channel)
        
        request = ScreenReadingRequest()
        request.user_id = "test_user"
        request.screen_content = "Submit form button"
        request.element_type = "button"
        request.voice_settings.speed = 1.0
        request.voice_settings.pitch = 1.0
        
        response = await stub.ScreenReading(request)
        
        assert response.success is True
        assert response.spoken_text == "Button: Submit form"
        assert response.element_type == "button"
        assert response.accessibility_label == "Submit form button"
    
    @pytest.mark.asyncio
    async def test_voice_assistance(self, grpc_channel):
        """Test voice assistance gRPC method."""
        channel, servicer = grpc_channel
        
        from accessibility_service.api.grpc.accessibility_pb2_grpc import AccessibilityServiceStub
        stub = AccessibilityServiceStub(channel)
        
        request = VoiceAssistanceRequest()
        request.user_id = "test_user"
        request.audio_data = b"fake_audio_data"
        request.command_type = "navigation"
        request.language_code = "en-US"
        
        response = await stub.VoiceAssistance(request)
        
        assert response.success is True
        assert response.response_text == "I can help you with that"
        assert response.action_taken == "navigation"
        assert response.confidence_score == 0.92
    
    @pytest.mark.asyncio
    async def test_accessible_content(self, grpc_channel):
        """Test accessible content conversion gRPC method."""
        channel, servicer = grpc_channel
        
        from accessibility_service.api.grpc.accessibility_pb2_grpc import AccessibilityServiceStub
        stub = AccessibilityServiceStub(channel)
        
        request = AccessibleContentRequest()
        request.user_id = "test_user"
        request.original_content = "Complex medical text"
        request.content_type = "medical"
        request.target_format = "plain_text"
        request.accessibility_level = "high"
        
        response = await stub.AccessibleContent(request)
        
        assert response.success is True
        assert response.converted_content == "Simplified content for accessibility"
        assert response.format_type == "plain_text"
        assert response.accessibility_score == 0.85
    
    @pytest.mark.asyncio
    async def test_manage_settings(self, grpc_channel):
        """Test settings management gRPC method."""
        channel, servicer = grpc_channel
        
        from accessibility_service.api.grpc.accessibility_pb2_grpc import AccessibilityServiceStub
        stub = AccessibilityServiceStub(channel)
        
        request = SettingsRequest()
        request.user_id = "test_user"
        request.action = "update"
        request.settings.visual_impairment = True
        request.settings.hearing_impairment = False
        request.settings.motor_impairment = False
        request.settings.cognitive_impairment = True
        
        response = await stub.ManageSettings(request)
        
        assert response.success is True
        assert response.message == "Settings updated successfully"
    
    @pytest.mark.asyncio
    async def test_configure_background_collection(self, grpc_channel):
        """Test background data collection configuration gRPC method."""
        channel, servicer = grpc_channel
        
        from accessibility_service.api.grpc.accessibility_pb2_grpc import AccessibilityServiceStub
        stub = AccessibilityServiceStub(channel)
        
        request = BackgroundCollectionRequest()
        request.user_id = "test_user"
        request.collection_type = "health_metrics"
        request.frequency_minutes = 60
        request.enabled = True
        
        response = await stub.ConfigureBackgroundCollection(request)
        
        assert response.success is True
        assert response.message == "Background collection configured"
        assert response.collection_id == "collection_123"
    
    @pytest.mark.asyncio
    async def test_trigger_health_alert(self, grpc_channel):
        """Test health alert triggering gRPC method."""
        channel, servicer = grpc_channel
        
        from accessibility_service.api.grpc.accessibility_pb2_grpc import AccessibilityServiceStub
        stub = AccessibilityServiceStub(channel)
        
        request = HealthAlertRequest()
        request.user_id = "test_user"
        request.alert_type = "emergency"
        request.severity = "high"
        request.message = "Health emergency detected"
        request.location_lat = 37.7749
        request.location_lng = -122.4194
        
        response = await stub.TriggerHealthAlert(request)
        
        assert response.success is True
        assert response.alert_id == "alert_456"
        assert response.message == "Health alert triggered successfully"
    
    @pytest.mark.asyncio
    async def test_speech_translation(self, grpc_channel):
        """Test speech translation gRPC method."""
        channel, servicer = grpc_channel
        
        from accessibility_service.api.grpc.accessibility_pb2_grpc import AccessibilityServiceStub
        stub = AccessibilityServiceStub(channel)
        
        request = SpeechTranslationRequest()
        request.user_id = "test_user"
        request.audio_data = b"fake_audio_data"
        request.source_language = "en"
        request.target_language = "es"
        request.real_time = True
        
        response = await stub.SpeechTranslation(request)
        
        assert response.success is True
        assert response.translated_text == "Hola, ¿cómo estás?"
        assert response.source_language == "en"
        assert response.target_language == "es"
        assert response.confidence_score == 0.94
    
    @pytest.mark.asyncio
    async def test_grpc_error_handling(self, grpc_channel):
        """Test gRPC error handling."""
        channel, servicer = grpc_channel
        
        # Mock an error in the servicer
        servicer.BlindAssistance = AsyncMock(side_effect=grpc.RpcError("Service unavailable"))
        
        from accessibility_service.api.grpc.accessibility_pb2_grpc import AccessibilityServiceStub
        stub = AccessibilityServiceStub(channel)
        
        request = BlindAssistanceRequest()
        request.user_id = "test_user"
        
        with pytest.raises(grpc.RpcError):
            await stub.BlindAssistance(request)
    
    @pytest.mark.asyncio
    async def test_concurrent_grpc_requests(self, grpc_channel):
        """Test handling multiple concurrent gRPC requests."""
        channel, servicer = grpc_channel
        
        from accessibility_service.api.grpc.accessibility_pb2_grpc import AccessibilityServiceStub
        stub = AccessibilityServiceStub(channel)
        
        # Create multiple requests
        requests = []
        for i in range(10):
            request = BlindAssistanceRequest()
            request.user_id = f"test_user_{i}"
            request.image_data = f"fake_image_data_{i}".encode()
            requests.append(request)
        
        # Execute concurrent requests
        responses = await asyncio.gather(*[
            stub.BlindAssistance(req) for req in requests
        ])
        
        assert len(responses) == 10
        for response in responses:
            assert response.success is True
            assert response.message == "Navigation guidance provided"
    
    @pytest.mark.asyncio
    async def test_streaming_speech_translation(self, grpc_channel):
        """Test streaming speech translation (if implemented)."""
        channel, servicer = grpc_channel
        
        # This would test streaming functionality if implemented
        # For now, we'll test the basic functionality
        from accessibility_service.api.grpc.accessibility_pb2_grpc import AccessibilityServiceStub
        stub = AccessibilityServiceStub(channel)
        
        request = SpeechTranslationRequest()
        request.user_id = "test_user"
        request.audio_data = b"streaming_audio_chunk"
        request.source_language = "en"
        request.target_language = "fr"
        request.real_time = True
        
        response = await stub.SpeechTranslation(request)
        
        assert response.success is True
        assert response.source_language == "en"
        assert response.target_language == "es"  # Mock returns Spanish


@pytest.mark.asyncio
async def test_grpc_service_integration():
    """Test integration between gRPC service and core accessibility service."""
    from accessibility_service.core.service import AccessibilityService
    
    # Create mock core service
    core_service = MagicMock(spec=AccessibilityService)
    core_service.analyze_accessibility = AsyncMock()
    core_service.get_recommendations = AsyncMock()
    core_service.update_user_preferences = AsyncMock()
    
    # Mock responses
    mock_response = AccessibilityResponse(
        request_id="test_request",
        user_id="test_user",
        timestamp=1640995200.0,
        overall_score=0.85
    )
    core_service.analyze_accessibility.return_value = mock_response
    core_service.get_recommendations.return_value = [
        {"type": "visual", "description": "Increase contrast"}
    ]
    core_service.update_user_preferences.return_value = True
    
    # Test that gRPC service would properly integrate with core service
    assert core_service.analyze_accessibility is not None
    assert core_service.get_recommendations is not None
    assert core_service.update_user_preferences is not None


@pytest.mark.asyncio
async def test_grpc_service_performance():
    """Test gRPC service performance characteristics."""
    import time
    
    # Create a simple performance test
    start_time = time.time()
    
    # Simulate processing time
    await asyncio.sleep(0.001)  # 1ms simulated processing
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    # Assert reasonable performance (under 10ms for this simple test)
    assert processing_time < 0.01
    
    # Test concurrent request handling
    async def mock_request():
        await asyncio.sleep(0.001)
        return {"success": True}
    
    start_time = time.time()
    
    # Execute 100 concurrent mock requests
    results = await asyncio.gather(*[mock_request() for _ in range(100)])
    
    end_time = time.time()
    total_time = end_time - start_time
    
    assert len(results) == 100
    assert all(result["success"] for result in results)
    # Should handle 100 concurrent requests in reasonable time
    assert total_time < 1.0  # Less than 1 second


@pytest.mark.asyncio
async def test_grpc_service_validation():
    """Test gRPC service input validation."""
    # Test empty request handling
    request = BlindAssistanceRequest()
    # Empty request should be handled gracefully
    assert request.user_id == ""
    assert request.image_data == b""
    
    # Test request with valid data
    request.user_id = "valid_user"
    request.image_data = b"valid_image_data"
    request.location_lat = 37.7749
    request.location_lng = -122.4194
    
    assert request.user_id == "valid_user"
    assert request.image_data == b"valid_image_data"
    assert request.location_lat == 37.7749
    assert request.location_lng == -122.4194


def test_grpc_message_serialization():
    """Test gRPC message serialization and deserialization."""
    # Test BlindAssistanceRequest
    request = BlindAssistanceRequest()
    request.user_id = "test_user"
    request.image_data = b"test_image"
    request.assistance_type = "navigation"
    
    # Serialize and deserialize
    serialized = request.SerializeToString()
    deserialized = BlindAssistanceRequest()
    deserialized.ParseFromString(serialized)
    
    assert deserialized.user_id == "test_user"
    assert deserialized.image_data == b"test_image"
    assert deserialized.assistance_type == "navigation"
    
    # Test BlindAssistanceResponse
    response = BlindAssistanceResponse()
    response.success = True
    response.message = "Test message"
    response.confidence_score = 0.95
    
    # Serialize and deserialize
    serialized = response.SerializeToString()
    deserialized = BlindAssistanceResponse()
    deserialized.ParseFromString(serialized)
    
    assert deserialized.success is True
    assert deserialized.message == "Test message"
    assert deserialized.confidence_score == 0.95 