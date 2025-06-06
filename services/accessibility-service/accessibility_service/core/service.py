"""
service - 索克生活项目模块
"""

from ..config.settings import get_settings
from ..models.accessibility import AccessibilityRequest, AccessibilityResponse
from ..services.audio import AudioAccessibilityService
from ..services.cognitive import CognitiveAccessibilityService
from ..services.integration import IntegrationService
from ..services.motor import MotorAccessibilityService
from ..services.visual import VisualAccessibilityService
from ..utils.platform_checker import PlatformChecker
from datetime import datetime
from typing import Any
import asyncio
import logging

"""
Main accessibility service implementation.
"""



logger = logging.getLogger(__name__)


class AccessibilityService:
    """
    Main accessibility service that coordinates all accessibility features.

    This service integrates multiple accessibility components:
    - Visual accessibility analysis
    - Audio accessibility processing
    - Motor accessibility assistance
    - Cognitive accessibility support
    """

    def __init__(self):
        """Initialize the accessibility service."""
        self.settings = get_settings()
        self.platform_checker = PlatformChecker()

        # Initialize sub-services
        self.visual_service = VisualAccessibilityService()
        self.audio_service = AudioAccessibilityService()
        self.motor_service = MotorAccessibilityService()
        self.cognitive_service = CognitiveAccessibilityService()
        self.integration_service = IntegrationService()

        self._initialized = False

    async def initialize(self) -> None:
        """Initialize all accessibility services."""
        if self._initialized:
            return

        logger.info("Initializing accessibility service...")

        try:
            # Initialize all sub-services
            await asyncio.gather(
                self.visual_service.initialize(),
                self.audio_service.initialize(),
                self.motor_service.initialize(),
                self.cognitive_service.initialize(),
                self.integration_service.initialize(),
            )

            self._initialized = True
            logger.info("Accessibility service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize accessibility service: {e}")
            raise

    async def analyze_accessibility(
        self,
        request: AccessibilityRequest
    ) -> AccessibilityResponse:
        """
        Perform comprehensive accessibility analysis.

        Args:
            request: Accessibility analysis request

        Returns:
            Comprehensive accessibility analysis response
        """
        if not self._initialized:
            await self.initialize()

        logger.info(f"Starting accessibility analysis for user {request.user_id}")

        try:
            # Perform parallel analysis across all domains
            results = await asyncio.gather(
                self._analyze_visual(request),
                self._analyze_audio(request),
                self._analyze_motor(request),
                self._analyze_cognitive(request),
                return_exceptions=True
            )

            # Process results and handle any exceptions
            visual_result, audio_result, motor_result, cognitive_result = results

            # Integrate all analysis results
            integrated_response = await self.integration_service.integrate_results(
                visual=visual_result if not isinstance(visual_result, Exception) else None,
                audio=audio_result if not isinstance(audio_result, Exception) else None,
                motor=motor_result if not isinstance(motor_result, Exception) else None,
                cognitive=cognitive_result if not isinstance(cognitive_result, Exception) else None,
                request=request
            )

            logger.info(f"Accessibility analysis completed for user {request.user_id}")
            return integrated_response

        except Exception as e:
            logger.error(f"Accessibility analysis failed: {e}")
            raise

    async def _analyze_visual(self, request: AccessibilityRequest) -> dict[str, Any]:
        """Perform visual accessibility analysis."""
        try:
            return await self.visual_service.analyze(request)
        except Exception as e:
            logger.error(f"Visual analysis failed: {e}")
            raise

    async def _analyze_audio(self, request: AccessibilityRequest) -> dict[str, Any]:
        """Perform audio accessibility analysis."""
        try:
            return await self.audio_service.analyze(request)
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            raise

    async def _analyze_motor(self, request: AccessibilityRequest) -> dict[str, Any]:
        """Perform motor accessibility analysis."""
        try:
            return await self.motor_service.analyze(request)
        except Exception as e:
            logger.error(f"Motor analysis failed: {e}")
            raise

    async def _analyze_cognitive(self, request: AccessibilityRequest) -> dict[str, Any]:
        """Perform cognitive accessibility analysis."""
        try:
            return await self.cognitive_service.analyze(request)
        except Exception as e:
            logger.error(f"Cognitive analysis failed: {e}")
            raise

    async def get_recommendations(
        self,
        user_id: str,
        accessibility_type: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Get personalized accessibility recommendations.

        Args:
            user_id: User identifier
            accessibility_type: Specific type of accessibility (optional)

        Returns:
            List of accessibility recommendations
        """
        if not self._initialized:
            await self.initialize()

        return await self.integration_service.get_recommendations(
            user_id=user_id,
            accessibility_type=accessibility_type
        )

    async def update_user_preferences(
        self,
        user_id: str,
        preferences: dict[str, Any]
    ) -> bool:
        """
        Update user accessibility preferences.

        Args:
            user_id: User identifier
            preferences: User accessibility preferences

        Returns:
            Success status
        """
        if not self._initialized:
            await self.initialize()

        return await self.integration_service.update_user_preferences(
            user_id=user_id,
            preferences=preferences
        )

    async def get_service_status(self) -> dict[str, Any]:
        """
        Get the status of all accessibility services.

        Returns:
            Service status information
        """
        status = {
            "service": "accessibility-service",
            "version": "1.0.0",
            "timestamp": datetime.now(datetime.UTC).isoformat(),
            "initialized": self._initialized,
            "platform": self.platform_checker.get_platform_info(),
            "sub_services": {}
        }

        if self._initialized:
            status["sub_services"] = {
                "visual": await self.visual_service.get_status(),
                "audio": await self.audio_service.get_status(),
                "motor": await self.motor_service.get_status(),
                "cognitive": await self.cognitive_service.get_status(),
                "integration": await self.integration_service.get_status(),
            }

        return status

    def get_health_status(self) -> dict[str, Any]:
        """
        Get the health status of the accessibility service.

        Returns:
            Health status information
        """
        return {
            "status": "healthy" if self._initialized else "initializing",
            "service": "accessibility-service",
            "version": "1.0.0",
            "initialized": self._initialized,
            "platform_compatible": True,
            "sub_services": {
                "visual": hasattr(self, 'visual_service') and self.visual_service is not None,
                "audio": hasattr(self, 'audio_service') and self.audio_service is not None,
                "motor": hasattr(self, 'motor_service') and self.motor_service is not None,
                "cognitive": hasattr(self, 'cognitive_service') and self.cognitive_service is not None,
                "integration": hasattr(self, 'integration_service') and self.integration_service is not None,
            }
        }

    async def shutdown(self) -> None:
        """Shutdown all accessibility services."""
        if not self._initialized:
            return

        logger.info("Shutting down accessibility service...")

        try:
            await asyncio.gather(
                self.visual_service.shutdown(),
                self.audio_service.shutdown(),
                self.motor_service.shutdown(),
                self.cognitive_service.shutdown(),
                self.integration_service.shutdown(),
                return_exceptions=True
            )

            self._initialized = False
            logger.info("Accessibility service shutdown completed")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            raise
