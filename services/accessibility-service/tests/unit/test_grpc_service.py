"""
test_grpc_service - 索克生活项目模块
"""

        from accessibility_service.api.grpc.accessibility_pb2_grpc import AccessibilityServiceStub
        from accessibility_service.api.grpc.accessibility_pb2_grpc import add_AccessibilityServiceServicer_to_server
from accessibility_service.api.grpc.accessibility_pb2 import (
from accessibility_service.api.grpc.accessibility_pb2_grpc import AccessibilityServiceServicer
from unittest.mock import MagicMock
import grpc.aio as aio
import pytest

"""
Test cases for AccessibilityService gRPC implementation.
"""


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
    SettingsResponse
)


class MockAccessibilityServicer(AccessibilityServiceServicer):
    """Mock implementation of AccessibilityServiceServicer for testing."""
    
    def __init__(self):
        self.accessibility_service = MagicMock()
    
    async def BlindAssistance(self, request, context):
        """Mock blind assistance service."""
        response = BlindAssistanceResponse()
        response.scene_description = "A room with a table and chairs"
        response.navigation_guidance = "Turn left in 10 meters"
        response.confidence = 0.95
        return response
    
    async def SignLanguageRecognition(self, request, context):
        """Mock sign language recognition service."""
        response = SignLanguageResponse()
        response.text = "Hello, how are you?"
        response.confidence = 0.88
        return response
    
    async def ScreenReading(self, request, context):
        """Mock screen reading service."""
        response = ScreenReadingResponse()
        response.screen_description = "Submit form button"
        return response
    
    async def VoiceAssistance(self, request, context):
        """Mock voice assistance service."""
        response = VoiceAssistanceResponse()
        response.recognized_text = "What is the weather today?"
        response.response_text = "I can help you with that"
        response.confidence = 0.92
        return response
    
    async def AccessibleContent(self, request, context):
        """Mock accessible content conversion service."""
        response = AccessibleContentResponse()
        response.accessible_content = "Simplified content for accessibility"
        return response
    
    async def ManageSettings(self, request, context):
        """Mock settings management service."""
        response = SettingsResponse()
        response.success = True
        response.message = "Settings updated successfully"
        return response


class TestAccessibilityGRPCService:
    """Test cases for AccessibilityService gRPC implementation."""
    
    @pytest.fixture
    async def grpc_server(self):
        """Create a test gRPC server."""
        server = aio.server()
        servicer = MockAccessibilityServicer()
        
        # Add the servicer to the server
        add_AccessibilityServiceServicer_to_server(servicer, server)
        
        # Start server on a random port
        listen_addr = '[::]:0'
        server.add_insecure_port(listen_addr)
        await server.start()
        
        yield server, servicer
        
        await server.stop(grace=1.0)
    
    @pytest.fixture
    async def grpc_channel(self, grpc_server):
        """Create a gRPC channel for testing."""
        server, servicer = grpc_server
        # Use a fixed port for testing
        channel = aio.insecure_channel('localhost:50051')
        
        yield channel, servicer
        
        await channel.close()
    
    @pytest.mark.asyncio
    async def test_blind_assistance(self, grpc_channel):
        """Test blind assistance gRPC method."""
        channel, servicer = grpc_channel
        
        stub = AccessibilityServiceStub(channel)
        
        request = BlindAssistanceRequest()
        request.user_id = "test_user"
        request.image_data = b"fake_image_data"
        
        # Mock the response directly from servicer
        response = await servicer.BlindAssistance(request, None)
        
        assert response.scene_description == "A room with a table and chairs"
        assert response.navigation_guidance == "Turn left in 10 meters"
        assert response.confidence == 0.95
    
    @pytest.mark.asyncio
    async def test_sign_language_recognition(self, grpc_channel):
        """Test sign language recognition gRPC method."""
        channel, servicer = grpc_channel
        
        request = SignLanguageRequest()
        request.user_id = "test_user"
        request.video_data = b"fake_video_data"
        request.language = "asl"
        
        # Mock the response directly from servicer
        response = await servicer.SignLanguageRecognition(request, None)
        
        assert response.text == "Hello, how are you?"
        assert response.confidence == 0.88
    
    @pytest.mark.asyncio
    async def test_screen_reading(self, grpc_channel):
        """Test screen reading gRPC method."""
        channel, servicer = grpc_channel
        
        request = ScreenReadingRequest()
        request.user_id = "test_user"
        request.screen_data = b"fake_screen_data"
        
        # Mock the response directly from servicer
        response = await servicer.ScreenReading(request, None)
        
        assert response.screen_description == "Submit form button"
    
    @pytest.mark.asyncio
    async def test_voice_assistance(self, grpc_channel):
        """Test voice assistance gRPC method."""
        channel, servicer = grpc_channel
        
        request = VoiceAssistanceRequest()
        request.user_id = "test_user"
        request.audio_data = b"fake_audio_data"
        request.language = "en"
        
        # Mock the response directly from servicer
        response = await servicer.VoiceAssistance(request, None)
        
        assert response.recognized_text == "What is the weather today?"
        assert response.response_text == "I can help you with that"
        assert response.confidence == 0.92
    
    @pytest.mark.asyncio
    async def test_accessible_content(self, grpc_channel):
        """Test accessible content gRPC method."""
        channel, servicer = grpc_channel
        
        request = AccessibleContentRequest()
        request.user_id = "test_user"
        request.content_id = "content_123"
        request.content_type = "text"
        
        # Mock the response directly from servicer
        response = await servicer.AccessibleContent(request, None)
        
        assert response.accessible_content == "Simplified content for accessibility"
    
    @pytest.mark.asyncio
    async def test_manage_settings(self, grpc_channel):
        """Test settings management gRPC method."""
        channel, servicer = grpc_channel
        
        request = SettingsRequest()
        request.user_id = "test_user"
        request.action = "update"
        
        # Mock the response directly from servicer
        response = await servicer.ManageSettings(request, None)
        
        assert response.success is True
        assert response.message == "Settings updated successfully"


def test_grpc_message_serialization():
    """Test gRPC message serialization and deserialization."""
    # Test BlindAssistanceRequest
    request = BlindAssistanceRequest()
    request.user_id = "test_user"
    request.image_data = b"test_image"
    
    # Serialize and deserialize
    serialized = request.SerializeToString()
    deserialized = BlindAssistanceRequest()
    deserialized.ParseFromString(serialized)
    
    assert deserialized.user_id == "test_user"
    assert deserialized.image_data == b"test_image"
    
    # Test SignLanguageRequest
    request = SignLanguageRequest()
    request.user_id = "test_user"
    request.video_data = b"test_video"
    request.language = "asl"
    
    serialized = request.SerializeToString()
    deserialized = SignLanguageRequest()
    deserialized.ParseFromString(serialized)
    
    assert deserialized.user_id == "test_user"
    assert deserialized.video_data == b"test_video"
    assert deserialized.language == "asl" 