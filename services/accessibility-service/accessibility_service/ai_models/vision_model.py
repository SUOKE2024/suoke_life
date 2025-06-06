"""
vision_model - 索克生活项目模块
"""

        from io import BytesIO
from ..config.settings import get_settings
from ..models.accessibility import VisualAnalysis
from PIL import Image
from pathlib import Path
from transformers import (
from typing import Dict, List, Optional, Tuple, Any
import asyncio
import cv2
import logging
import numpy as np
import torch
import torchvision.transforms as transforms

"""
Vision AI model for accessibility analysis.
Provides computer vision capabilities for visual accessibility features.
"""

    BlipProcessor, BlipForConditionalGeneration,
    DetrImageProcessor, DetrForObjectDetection,
    pipeline
)


logger = logging.getLogger(__name__)


class VisionModel:
    """
    Advanced vision AI model for accessibility analysis.
    
    Provides:
    - Scene understanding and description
    - Object detection and recognition
    - Text extraction (OCR)
    - Navigation assistance
    - Accessibility barrier detection
    """
    
    def __init__(self):
        """Initialize the vision model."""
        self.settings = get_settings()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Model components
        self.image_captioning_model = None
        self.image_captioning_processor = None
        self.object_detection_model = None
        self.object_detection_processor = None
        self.ocr_pipeline = None
        self.depth_estimation_pipeline = None
        
        # Model configurations
        self.image_caption_model_name = "Salesforce/blip-image-captioning-base"
        self.object_detection_model_name = "facebook/detr-resnet-50"
        
        # Accessibility-specific configurations
        self.accessibility_classes = {
            "stairs": {"barrier": True, "description": "Stairs detected - mobility barrier"},
            "ramp": {"barrier": False, "description": "Ramp detected - accessible path"},
            "door": {"barrier": False, "description": "Door detected"},
            "elevator": {"barrier": False, "description": "Elevator detected - accessible vertical transport"},
            "escalator": {"barrier": True, "description": "Escalator detected - potential mobility barrier"},
            "curb": {"barrier": True, "description": "Curb detected - potential mobility barrier"},
            "crosswalk": {"barrier": False, "description": "Crosswalk detected"},
            "traffic_light": {"barrier": False, "description": "Traffic light detected"},
            "sign": {"barrier": False, "description": "Sign detected - may contain important information"},
            "obstacle": {"barrier": True, "description": "Obstacle detected in path"}
        }
        
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize all vision models."""
        if self._initialized:
            return
        
        logger.info("Initializing vision AI models...")
        
        try:
            # Initialize image captioning model
            await self._initialize_image_captioning()
            
            # Initialize object detection model
            await self._initialize_object_detection()
            
            # Initialize OCR pipeline
            await self._initialize_ocr()
            
            # Initialize depth estimation
            await self._initialize_depth_estimation()
            
            self._initialized = True
            logger.info("Vision AI models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize vision models: {e}")
            raise
    
    async def _initialize_image_captioning(self) -> None:
        """Initialize image captioning model."""
        try:
            self.image_captioning_processor = BlipProcessor.from_pretrained(
                self.image_caption_model_name
            )
            self.image_captioning_model = BlipForConditionalGeneration.from_pretrained(
                self.image_caption_model_name
            ).to(self.device)
            logger.info("Image captioning model loaded")
        except Exception as e:
            logger.error(f"Failed to load image captioning model: {e}")
            # Fallback to basic implementation
            self.image_captioning_model = None
            self.image_captioning_processor = None
    
    async def _initialize_object_detection(self) -> None:
        """Initialize object detection model."""
        try:
            self.object_detection_processor = DetrImageProcessor.from_pretrained(
                self.object_detection_model_name
            )
            self.object_detection_model = DetrForObjectDetection.from_pretrained(
                self.object_detection_model_name
            ).to(self.device)
            logger.info("Object detection model loaded")
        except Exception as e:
            logger.error(f"Failed to load object detection model: {e}")
            # Fallback to basic implementation
            self.object_detection_model = None
            self.object_detection_processor = None
    
    async def _initialize_ocr(self) -> None:
        """Initialize OCR pipeline."""
        try:
            self.ocr_pipeline = pipeline(
                "image-to-text",
                model="microsoft/trocr-base-printed",
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info("OCR pipeline loaded")
        except Exception as e:
            logger.error(f"Failed to load OCR pipeline: {e}")
            # Fallback to basic OCR
            self.ocr_pipeline = None
    
    async def _initialize_depth_estimation(self) -> None:
        """Initialize depth estimation pipeline."""
        try:
            self.depth_estimation_pipeline = pipeline(
                "depth-estimation",
                model="Intel/dpt-large",
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info("Depth estimation pipeline loaded")
        except Exception as e:
            logger.error(f"Failed to load depth estimation pipeline: {e}")
            # Fallback implementation
            self.depth_estimation_pipeline = None
    
    async def analyze_image(
        self,
        image_data: bytes,
        analysis_type: str = "comprehensive",
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> VisualAnalysis:
        """
        Perform comprehensive visual analysis of an image.
        
        Args:
            image_data: Raw image data
            analysis_type: Type of analysis to perform
            user_preferences: User accessibility preferences
            
        Returns:
            Visual analysis results
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Convert image data to PIL Image
            image = self._bytes_to_image(image_data)
            
            # Perform different types of analysis based on request
            if analysis_type == "navigation":
                return await self._analyze_for_navigation(image, user_preferences)
            elif analysis_type == "reading":
                return await self._analyze_for_reading(image, user_preferences)
            elif analysis_type == "object_recognition":
                return await self._analyze_objects(image, user_preferences)
            else:
                return await self._comprehensive_analysis(image, user_preferences)
                
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return VisualAnalysis(
                accessibility_score=0.0,
                issues=["Analysis failed"],
                recommendations=["Please try again with a different image"],
                scene_description="Unable to analyze image",
                detected_objects=[],
                text_content="",
                navigation_guidance="",
                accessibility_barriers=["Analysis error"]
            )
    
    async def _comprehensive_analysis(
        self,
        image: Image.Image,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> VisualAnalysis:
        """Perform comprehensive visual analysis."""
        # Run all analysis components in parallel
        results = await asyncio.gather(
            self._generate_scene_description(image),
            self._detect_objects(image),
            self._extract_text(image),
            self._analyze_accessibility_barriers(image),
            self._estimate_depth(image),
            return_exceptions=True
        )
        
        scene_description, objects, text_content, barriers, depth_info = results
        
        # Handle any exceptions in results
        scene_description = scene_description if not isinstance(scene_description, Exception) else "Scene analysis unavailable"
        objects = objects if not isinstance(objects, Exception) else []
        text_content = text_content if not isinstance(text_content, Exception) else ""
        barriers = barriers if not isinstance(barriers, Exception) else []
        depth_info = depth_info if not isinstance(depth_info, Exception) else {}
        
        # Calculate accessibility score
        accessibility_score = self._calculate_accessibility_score(
            objects, barriers, text_content, user_preferences
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            objects, barriers, text_content, user_preferences
        )
        
        # Generate navigation guidance
        navigation_guidance = self._generate_navigation_guidance(
            objects, barriers, depth_info
        )
        
        return VisualAnalysis(
            accessibility_score=accessibility_score,
            issues=barriers,
            recommendations=recommendations,
            scene_description=scene_description,
            detected_objects=objects,
            text_content=text_content,
            navigation_guidance=navigation_guidance,
            accessibility_barriers=barriers,
            depth_information=depth_info
        )
    
    async def _analyze_for_navigation(
        self,
        image: Image.Image,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> VisualAnalysis:
        """Analyze image specifically for navigation assistance."""
        # Focus on navigation-relevant objects and barriers
        objects = await self._detect_navigation_objects(image)
        barriers = await self._detect_navigation_barriers(image)
        depth_info = await self._estimate_depth(image)
        
        # Generate specific navigation guidance
        navigation_guidance = self._generate_detailed_navigation_guidance(
            objects, barriers, depth_info, user_preferences
        )
        
        accessibility_score = self._calculate_navigation_score(objects, barriers)
        
        return VisualAnalysis(
            accessibility_score=accessibility_score,
            issues=barriers,
            recommendations=self._generate_navigation_recommendations(barriers),
            scene_description=f"Navigation analysis: {len(objects)} objects detected",
            detected_objects=objects,
            text_content="",
            navigation_guidance=navigation_guidance,
            accessibility_barriers=barriers,
            depth_information=depth_info
        )
    
    async def _analyze_for_reading(
        self,
        image: Image.Image,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> VisualAnalysis:
        """Analyze image specifically for reading assistance."""
        # Focus on text extraction and readability
        text_content = await self._extract_text_detailed(image)
        text_analysis = self._analyze_text_accessibility(text_content, user_preferences)
        
        return VisualAnalysis(
            accessibility_score=text_analysis["score"],
            issues=text_analysis["issues"],
            recommendations=text_analysis["recommendations"],
            scene_description="Text reading analysis",
            detected_objects=[],
            text_content=text_content,
            navigation_guidance="",
            accessibility_barriers=text_analysis["issues"]
        )
    
    async def _generate_scene_description(self, image: Image.Image) -> str:
        """Generate natural language description of the scene."""
        if not self.image_captioning_model:
            return "Scene description unavailable"
        
        try:
            inputs = self.image_captioning_processor(image, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                out = self.image_captioning_model.generate(**inputs, max_length=100)
            
            description = self.image_captioning_processor.decode(out[0], skip_special_tokens=True)
            return description
            
        except Exception as e:
            logger.error(f"Scene description generation failed: {e}")
            return "Unable to generate scene description"
    
    async def _detect_objects(self, image: Image.Image) -> List[Dict[str, Any]]:
        """Detect and classify objects in the image."""
        if not self.object_detection_model:
            return []
        
        try:
            inputs = self.object_detection_processor(images=image, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.object_detection_model(**inputs)
            
            # Process detection results
            target_sizes = torch.tensor([image.size[::-1]]).to(self.device)
            results = self.object_detection_processor.post_process_object_detection(
                outputs, target_sizes=target_sizes, threshold=0.5
            )[0]
            
            objects = []
            for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
                label_name = self.object_detection_model.config.id2label[label.item()]
                objects.append({
                    "label": label_name,
                    "confidence": score.item(),
                    "bbox": box.tolist(),
                    "accessibility_info": self.accessibility_classes.get(
                        label_name, {"barrier": False, "description": f"{label_name} detected"}
                    )
                })
            
            return objects
            
        except Exception as e:
            logger.error(f"Object detection failed: {e}")
            return []
    
    async def _extract_text(self, image: Image.Image) -> str:
        """Extract text from the image using OCR."""
        if not self.ocr_pipeline:
            return ""
        
        try:
            result = self.ocr_pipeline(image)
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "")
            return ""
            
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return ""
    
    async def _extract_text_detailed(self, image: Image.Image) -> str:
        """Extract text with detailed analysis for reading assistance."""
        # Enhanced OCR with preprocessing
        try:
            # Convert PIL to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Preprocess for better OCR
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Convert back to PIL
            processed_image = Image.fromarray(thresh)
            
            # Extract text
            if self.ocr_pipeline:
                result = self.ocr_pipeline(processed_image)
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "")
            
            return ""
            
        except Exception as e:
            logger.error(f"Detailed text extraction failed: {e}")
            return ""
    
    async def _analyze_accessibility_barriers(self, image: Image.Image) -> List[str]:
        """Detect accessibility barriers in the image."""
        objects = await self._detect_objects(image)
        barriers = []
        
        for obj in objects:
            if obj["accessibility_info"]["barrier"]:
                barriers.append(obj["accessibility_info"]["description"])
        
        # Additional barrier detection logic
        barriers.extend(await self._detect_visual_barriers(image))
        
        return barriers
    
    async def _detect_visual_barriers(self, image: Image.Image) -> List[str]:
        """Detect visual accessibility barriers."""
        barriers = []
        
        try:
            # Convert to numpy array for analysis
            img_array = np.array(image)
            
            # Check contrast levels
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            contrast = gray.std()
            
            if contrast < 30:
                barriers.append("Low contrast detected - may be difficult to see")
            
            # Check for very bright or dark areas
            mean_brightness = gray.mean()
            if mean_brightness < 50:
                barriers.append("Very dark image - may be difficult to navigate")
            elif mean_brightness > 200:
                barriers.append("Very bright image - may cause glare")
            
            # Check for motion blur (if applicable)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            if laplacian_var < 100:
                barriers.append("Image appears blurry - details may be unclear")
            
        except Exception as e:
            logger.error(f"Visual barrier detection failed: {e}")
        
        return barriers
    
    async def _estimate_depth(self, image: Image.Image) -> Dict[str, Any]:
        """Estimate depth information for navigation."""
        if not self.depth_estimation_pipeline:
            return {}
        
        try:
            depth_result = self.depth_estimation_pipeline(image)
            
            # Process depth information
            depth_map = depth_result["depth"]
            
            # Calculate depth statistics
            depth_array = np.array(depth_map)
            
            return {
                "has_depth_info": True,
                "average_depth": float(depth_array.mean()),
                "min_depth": float(depth_array.min()),
                "max_depth": float(depth_array.max()),
                "depth_variance": float(depth_array.var()),
                "obstacles_detected": self._analyze_depth_obstacles(depth_array)
            }
            
        except Exception as e:
            logger.error(f"Depth estimation failed: {e}")
            return {"has_depth_info": False}
    
    def _analyze_depth_obstacles(self, depth_array: np.ndarray) -> List[Dict[str, Any]]:
        """Analyze depth map for obstacles."""
        obstacles = []
        
        try:
            # Simple obstacle detection based on depth discontinuities
            height, width = depth_array.shape
            
            # Divide image into grid and analyze each section
            grid_size = 32
            for i in range(0, height, grid_size):
                for j in range(0, width, grid_size):
                    section = depth_array[i:i+grid_size, j:j+grid_size]
                    
                    if section.size > 0:
                        depth_var = section.var()
                        if depth_var > 0.1:  # High variance indicates potential obstacle
                            obstacles.append({
                                "position": {"x": j, "y": i},
                                "size": {"width": min(grid_size, width-j), "height": min(grid_size, height-i)},
                                "confidence": min(depth_var * 10, 1.0)
                            })
        
        except Exception as e:
            logger.error(f"Depth obstacle analysis failed: {e}")
        
        return obstacles
    
    def _calculate_accessibility_score(
        self,
        objects: List[Dict[str, Any]],
        barriers: List[str],
        text_content: str,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calculate overall accessibility score."""
        base_score = 1.0
        
        # Deduct points for barriers
        barrier_penalty = len(barriers) * 0.1
        base_score -= barrier_penalty
        
        # Bonus for accessible features
        accessible_objects = [obj for obj in objects if not obj["accessibility_info"]["barrier"]]
        accessibility_bonus = len(accessible_objects) * 0.05
        base_score += accessibility_bonus
        
        # Text readability bonus
        if text_content and len(text_content) > 10:
            base_score += 0.1
        
        # User preference adjustments
        if user_preferences:
            if user_preferences.get("visual_impairment") and text_content:
                base_score += 0.15  # Bonus for text availability for visually impaired users
            
            if user_preferences.get("motor_impairment"):
                # Check for accessible paths
                accessible_paths = [obj for obj in objects if obj["label"] in ["ramp", "elevator"]]
                if accessible_paths:
                    base_score += 0.2
        
        return max(0.0, min(1.0, base_score))
    
    def _generate_recommendations(
        self,
        objects: List[Dict[str, Any]],
        barriers: List[str],
        text_content: str,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Generate accessibility recommendations."""
        recommendations = []
        
        # Barrier-specific recommendations
        if barriers:
            recommendations.append("Accessibility barriers detected - consider alternative routes")
        
        # Object-specific recommendations
        stairs_detected = any(obj["label"] == "stairs" for obj in objects)
        ramp_detected = any(obj["label"] == "ramp" for obj in objects)
        
        if stairs_detected and not ramp_detected:
            recommendations.append("Stairs detected - look for ramp or elevator access")
        
        # Text-specific recommendations
        if not text_content:
            recommendations.append("No text detected - use voice assistance for information")
        elif len(text_content) > 100:
            recommendations.append("Large amount of text detected - consider using text-to-speech")
        
        # User preference-specific recommendations
        if user_preferences:
            if user_preferences.get("visual_impairment"):
                recommendations.append("Use voice guidance for navigation assistance")
            
            if user_preferences.get("motor_impairment"):
                recommendations.append("Look for accessible entrances and pathways")
        
        return recommendations
    
    def _generate_navigation_guidance(
        self,
        objects: List[Dict[str, Any]],
        barriers: List[str],
        depth_info: Dict[str, Any]
    ) -> str:
        """Generate navigation guidance based on analysis."""
        guidance_parts = []
        
        # Object-based guidance
        if objects:
            important_objects = [obj for obj in objects if obj["label"] in 
                               ["door", "stairs", "ramp", "elevator", "crosswalk"]]
            
            for obj in important_objects[:3]:  # Limit to top 3 important objects
                guidance_parts.append(f"{obj['label']} detected ahead")
        
        # Barrier warnings
        if barriers:
            guidance_parts.append(f"Warning: {len(barriers)} accessibility barriers detected")
        
        # Depth-based guidance
        if depth_info.get("obstacles_detected"):
            obstacle_count = len(depth_info["obstacles_detected"])
            guidance_parts.append(f"{obstacle_count} potential obstacles in path")
        
        if not guidance_parts:
            guidance_parts.append("Path appears clear for navigation")
        
        return ". ".join(guidance_parts)
    
    async def _detect_navigation_objects(self, image: Image.Image) -> List[Dict[str, Any]]:
        """Detect objects specifically relevant for navigation."""
        all_objects = await self._detect_objects(image)
        
        navigation_relevant = [
            "door", "stairs", "ramp", "elevator", "escalator", "crosswalk",
            "traffic_light", "sign", "curb", "sidewalk", "road"
        ]
        
        return [obj for obj in all_objects if obj["label"] in navigation_relevant]
    
    async def _detect_navigation_barriers(self, image: Image.Image) -> List[str]:
        """Detect barriers specifically for navigation."""
        objects = await self._detect_navigation_objects(image)
        barriers = []
        
        for obj in objects:
            if obj["accessibility_info"]["barrier"]:
                barriers.append(f"{obj['label']} blocking path")
        
        return barriers
    
    def _generate_detailed_navigation_guidance(
        self,
        objects: List[Dict[str, Any]],
        barriers: List[str],
        depth_info: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate detailed navigation guidance."""
        guidance = []
        
        # Priority guidance for mobility impairments
        if user_preferences and user_preferences.get("motor_impairment"):
            accessible_routes = [obj for obj in objects if obj["label"] in ["ramp", "elevator"]]
            if accessible_routes:
                guidance.append(f"Accessible route available: {accessible_routes[0]['label']}")
            elif barriers:
                guidance.append("No accessible route detected - seek alternative path")
        
        # Visual guidance for visual impairments
        if user_preferences and user_preferences.get("visual_impairment"):
            if depth_info.get("obstacles_detected"):
                guidance.append("Multiple obstacles detected - proceed with caution")
            else:
                guidance.append("Path appears clear")
        
        # General navigation guidance
        if objects:
            nearest_landmark = min(objects, key=lambda x: x["bbox"][0])  # Leftmost object
            guidance.append(f"Nearest landmark: {nearest_landmark['label']}")
        
        return ". ".join(guidance) if guidance else "Continue forward"
    
    def _calculate_navigation_score(
        self,
        objects: List[Dict[str, Any]],
        barriers: List[str]
    ) -> float:
        """Calculate navigation-specific accessibility score."""
        base_score = 1.0
        
        # Heavy penalty for navigation barriers
        base_score -= len(barriers) * 0.2
        
        # Bonus for navigation aids
        nav_aids = [obj for obj in objects if obj["label"] in ["ramp", "elevator", "crosswalk"]]
        base_score += len(nav_aids) * 0.15
        
        return max(0.0, min(1.0, base_score))
    
    def _generate_navigation_recommendations(self, barriers: List[str]) -> List[str]:
        """Generate navigation-specific recommendations."""
        if not barriers:
            return ["Path appears accessible for navigation"]
        
        recommendations = []
        for barrier in barriers:
            if "stairs" in barrier.lower():
                recommendations.append("Look for ramp or elevator access")
            elif "curb" in barrier.lower():
                recommendations.append("Look for curb cut or accessible crossing")
            else:
                recommendations.append(f"Navigate around {barrier}")
        
        return recommendations
    
    def _analyze_text_accessibility(
        self,
        text_content: str,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze text for accessibility issues."""
        issues = []
        recommendations = []
        score = 1.0
        
        if not text_content:
            issues.append("No text detected")
            recommendations.append("Use voice assistance for information")
            score = 0.5
        else:
            # Check text length
            if len(text_content) > 500:
                issues.append("Large amount of text detected")
                recommendations.append("Consider using text-to-speech for easier consumption")
                score -= 0.1
            
            # Check for complex language (simple heuristic)
            words = text_content.split()
            avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
            
            if avg_word_length > 6:
                issues.append("Complex language detected")
                recommendations.append("Text may be difficult to understand")
                score -= 0.1
            
            # User preference adjustments
            if user_preferences:
                if user_preferences.get("cognitive_impairment"):
                    recommendations.append("Use simplified language mode")
                    score += 0.1  # Bonus for having text available
                
                if user_preferences.get("visual_impairment"):
                    recommendations.append("Use text-to-speech for audio output")
                    score += 0.2  # High bonus for text availability
        
        return {
            "score": max(0.0, min(1.0, score)),
            "issues": issues,
            "recommendations": recommendations
        }
    
    def _bytes_to_image(self, image_data: bytes) -> Image.Image:
        """Convert bytes to PIL Image."""
        return Image.open(BytesIO(image_data)).convert("RGB")
    
    async def shutdown(self) -> None:
        """Shutdown the vision model and free resources."""
        logger.info("Shutting down vision model...")
        
        # Clear model references to free GPU memory
        if self.image_captioning_model:
            del self.image_captioning_model
            self.image_captioning_model = None
        
        if self.object_detection_model:
            del self.object_detection_model
            self.object_detection_model = None
        
        # Clear CUDA cache if available
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        self._initialized = False
        logger.info("Vision model shutdown complete")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models."""
        return {
            "image_captioning": {
                "model": self.image_caption_model_name,
                "loaded": self.image_captioning_model is not None
            },
            "object_detection": {
                "model": self.object_detection_model_name,
                "loaded": self.object_detection_model is not None
            },
            "ocr": {
                "loaded": self.ocr_pipeline is not None
            },
            "depth_estimation": {
                "loaded": self.depth_estimation_pipeline is not None
            },
            "device": str(self.device),
            "initialized": self._initialized
        } 