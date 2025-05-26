"""
Accessibility analysis engine.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from ..models.accessibility import (
    AccessibilityRequest,
    AccessibilityResponse,
    AccessibilityAnalysis,
    AccessibilityType,
    AccessibilityIssue,
    AccessibilityRecommendation
)
from ..models.analysis import (
    VisualAnalysis,
    AudioAnalysis,
    MotorAnalysis,
    CognitiveAnalysis,
    ComprehensiveAnalysis,
    AnalysisStatus
)
from ..services.visual import VisualAccessibilityService
from ..services.audio import AudioAccessibilityService
from ..services.motor import MotorAccessibilityService
from ..services.cognitive import CognitiveAccessibilityService
from ..config.settings import get_settings

logger = logging.getLogger(__name__)


class AccessibilityEngine:
    """Main accessibility analysis engine."""
    
    def __init__(self):
        """Initialize the accessibility engine."""
        self.settings = get_settings()
        self._visual_service = None
        self._audio_service = None
        self._motor_service = None
        self._cognitive_service = None
        
        # Initialize services
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize analysis services."""
        try:
            if self.settings.visual_analysis_enabled:
                self._visual_service = VisualAccessibilityService()
                logger.info("Visual accessibility service initialized")
            
            if self.settings.audio_analysis_enabled:
                self._audio_service = AudioAccessibilityService()
                logger.info("Audio accessibility service initialized")
            
            if self.settings.motor_analysis_enabled:
                self._motor_service = MotorAccessibilityService()
                logger.info("Motor accessibility service initialized")
            
            if self.settings.cognitive_analysis_enabled:
                self._cognitive_service = CognitiveAccessibilityService()
                logger.info("Cognitive accessibility service initialized")
                
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            raise
    
    async def analyze(self, request: AccessibilityRequest) -> AccessibilityResponse:
        """Perform accessibility analysis."""
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Starting accessibility analysis for user {request.user_id}")
            
            # Validate request
            self._validate_request(request)
            
            # Perform analyses
            analyses = await self._perform_analyses(request)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(analyses)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(analyses)
            
            # Count issues
            total_issues, critical_issues = self._count_issues(analyses)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Create response
            response = AccessibilityResponse(
                request_id=f"req_{request.user_id}_{int(start_time.timestamp())}",
                user_id=request.user_id,
                session_id=request.session_id,
                analyses=analyses,
                overall_score=overall_score,
                total_issues=total_issues,
                critical_issues=critical_issues,
                recommendations=recommendations,
                quick_wins=self._get_quick_wins(analyses),
                processing_time=processing_time,
                status="completed"
            )
            
            logger.info(f"Analysis completed for user {request.user_id} in {processing_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Analysis failed for user {request.user_id}: {e}")
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Return error response
            return AccessibilityResponse(
                request_id=f"req_{request.user_id}_{int(start_time.timestamp())}",
                user_id=request.user_id,
                session_id=request.session_id,
                analyses=[],
                overall_score=0.0,
                total_issues=0,
                critical_issues=0,
                recommendations=[],
                quick_wins=[],
                processing_time=processing_time,
                status=f"failed: {str(e)}"
            )
    
    def _validate_request(self, request: AccessibilityRequest):
        """Validate analysis request."""
        if not request.user_id:
            raise ValueError("User ID is required")
        
        if not request.accessibility_types:
            raise ValueError("At least one accessibility type must be specified")
        
        # Check if requested types are enabled
        for analysis_type in request.accessibility_types:
            if analysis_type == AccessibilityType.VISUAL and not self.settings.visual_analysis_enabled:
                raise ValueError("Visual analysis is not enabled")
            elif analysis_type == AccessibilityType.AUDIO and not self.settings.audio_analysis_enabled:
                raise ValueError("Audio analysis is not enabled")
            elif analysis_type == AccessibilityType.MOTOR and not self.settings.motor_analysis_enabled:
                raise ValueError("Motor analysis is not enabled")
            elif analysis_type == AccessibilityType.COGNITIVE and not self.settings.cognitive_analysis_enabled:
                raise ValueError("Cognitive analysis is not enabled")
    
    async def _perform_analyses(self, request: AccessibilityRequest) -> List[AccessibilityAnalysis]:
        """Perform the requested analyses."""
        analyses = []
        tasks = []
        
        # Create analysis tasks
        for analysis_type in request.accessibility_types:
            if analysis_type == AccessibilityType.VISUAL and self._visual_service:
                task = self._perform_visual_analysis(request)
                tasks.append((analysis_type, task))
            elif analysis_type == AccessibilityType.AUDIO and self._audio_service:
                task = self._perform_audio_analysis(request)
                tasks.append((analysis_type, task))
            elif analysis_type == AccessibilityType.MOTOR and self._motor_service:
                task = self._perform_motor_analysis(request)
                tasks.append((analysis_type, task))
            elif analysis_type == AccessibilityType.COGNITIVE and self._cognitive_service:
                task = self._perform_cognitive_analysis(request)
                tasks.append((analysis_type, task))
            elif analysis_type == AccessibilityType.MULTIMODAL:
                # Perform all available analyses
                if self._visual_service:
                    task = self._perform_visual_analysis(request)
                    tasks.append((AccessibilityType.VISUAL, task))
                if self._audio_service:
                    task = self._perform_audio_analysis(request)
                    tasks.append((AccessibilityType.AUDIO, task))
                if self._motor_service:
                    task = self._perform_motor_analysis(request)
                    tasks.append((AccessibilityType.MOTOR, task))
                if self._cognitive_service:
                    task = self._perform_cognitive_analysis(request)
                    tasks.append((AccessibilityType.COGNITIVE, task))
        
        # Execute tasks concurrently
        if tasks:
            results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
            
            for i, (analysis_type, _) in enumerate(tasks):
                result = results[i]
                if isinstance(result, Exception):
                    logger.error(f"Analysis failed for {analysis_type}: {result}")
                    # Create failed analysis
                    analysis = AccessibilityAnalysis(
                        type=analysis_type,
                        status="failed",
                        score=0.0,
                        processing_time=0.0
                    )
                else:
                    analysis = result
                
                analyses.append(analysis)
        
        return analyses
    
    async def _perform_visual_analysis(self, request: AccessibilityRequest) -> AccessibilityAnalysis:
        """Perform visual accessibility analysis."""
        start_time = datetime.utcnow()
        
        try:
            # Extract visual data
            visual_data = request.visual_data or {}
            
            # Perform analysis
            result = await self._visual_service.analyze(visual_data, request.context)
            
            # Convert to AccessibilityAnalysis
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AccessibilityAnalysis(
                type=AccessibilityType.VISUAL,
                status="completed",
                score=result.get('score', 0.0),
                metrics=result.get('metrics', {}),
                recommendations=result.get('recommendations', []),
                improvements=result.get('improvements', []),
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Visual analysis failed: {e}")
            raise
    
    async def _perform_audio_analysis(self, request: AccessibilityRequest) -> AccessibilityAnalysis:
        """Perform audio accessibility analysis."""
        start_time = datetime.utcnow()
        
        try:
            # Extract audio data
            audio_data = request.audio_data or {}
            
            # Perform analysis
            result = await self._audio_service.analyze(audio_data, request.context)
            
            # Convert to AccessibilityAnalysis
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AccessibilityAnalysis(
                type=AccessibilityType.AUDIO,
                status="completed",
                score=result.get('score', 0.0),
                metrics=result.get('metrics', {}),
                recommendations=result.get('recommendations', []),
                improvements=result.get('improvements', []),
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            raise
    
    async def _perform_motor_analysis(self, request: AccessibilityRequest) -> AccessibilityAnalysis:
        """Perform motor accessibility analysis."""
        start_time = datetime.utcnow()
        
        try:
            # Extract motor data
            motor_data = request.motor_data or {}
            
            # Perform analysis
            result = await self._motor_service.analyze(motor_data, request.context)
            
            # Convert to AccessibilityAnalysis
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AccessibilityAnalysis(
                type=AccessibilityType.MOTOR,
                status="completed",
                score=result.get('score', 0.0),
                metrics=result.get('metrics', {}),
                recommendations=result.get('recommendations', []),
                improvements=result.get('improvements', []),
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Motor analysis failed: {e}")
            raise
    
    async def _perform_cognitive_analysis(self, request: AccessibilityRequest) -> AccessibilityAnalysis:
        """Perform cognitive accessibility analysis."""
        start_time = datetime.utcnow()
        
        try:
            # Extract cognitive data
            cognitive_data = request.cognitive_data or {}
            
            # Perform analysis
            result = await self._cognitive_service.analyze(cognitive_data, request.context)
            
            # Convert to AccessibilityAnalysis
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AccessibilityAnalysis(
                type=AccessibilityType.COGNITIVE,
                status="completed",
                score=result.get('score', 0.0),
                metrics=result.get('metrics', {}),
                recommendations=result.get('recommendations', []),
                improvements=result.get('improvements', []),
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Cognitive analysis failed: {e}")
            raise
    
    def _calculate_overall_score(self, analyses: List[AccessibilityAnalysis]) -> float:
        """Calculate overall accessibility score."""
        if not analyses:
            return 0.0
        
        # Calculate weighted average
        total_score = sum(analysis.score for analysis in analyses)
        return total_score / len(analyses)
    
    def _generate_recommendations(self, analyses: List[AccessibilityAnalysis]) -> List[AccessibilityRecommendation]:
        """Generate accessibility recommendations."""
        recommendations = []
        
        for analysis in analyses:
            for i, rec_text in enumerate(analysis.recommendations):
                recommendation = AccessibilityRecommendation(
                    recommendation_id=f"rec_{analysis.type}_{i}",
                    type=analysis.type,
                    priority="medium",  # Default priority
                    title=f"{analysis.type.value.title()} Improvement",
                    description=rec_text,
                    expected_impact="Improved accessibility for users",
                    confidence=0.8
                )
                recommendations.append(recommendation)
        
        return recommendations
    
    def _count_issues(self, analyses: List[AccessibilityAnalysis]) -> tuple:
        """Count total and critical issues."""
        total_issues = 0
        critical_issues = 0
        
        for analysis in analyses:
            # Count issues based on score
            if analysis.score < 50:
                critical_issues += 1
            if analysis.score < 80:
                total_issues += 1
        
        return total_issues, critical_issues
    
    def _get_quick_wins(self, analyses: List[AccessibilityAnalysis]) -> List[str]:
        """Get quick win suggestions."""
        quick_wins = []
        
        for analysis in analyses:
            quick_wins.extend(analysis.improvements[:2])  # Take first 2 improvements
        
        return quick_wins[:5]  # Limit to 5 quick wins
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get engine health status."""
        return {
            "status": "healthy",
            "services": {
                "visual": self._visual_service is not None,
                "audio": self._audio_service is not None,
                "motor": self._motor_service is not None,
                "cognitive": self._cognitive_service is not None,
            },
            "settings": {
                "visual_enabled": self.settings.visual_analysis_enabled,
                "audio_enabled": self.settings.audio_analysis_enabled,
                "motor_enabled": self.settings.motor_analysis_enabled,
                "cognitive_enabled": self.settings.cognitive_analysis_enabled,
            }
        } 