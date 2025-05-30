"""
Accessibility data processor.
"""

import logging
from typing import Any

from ..config.settings import get_settings
from ..models.accessibility import AccessibilityRequest, AccessibilityType

logger = logging.getLogger(__name__)


class AccessibilityProcessor:
    """Data processor for accessibility analysis."""

    def __init__(self):
        """Initialize the processor."""
        self.settings = get_settings()

    def preprocess_request(self, request: AccessibilityRequest) -> AccessibilityRequest:
        """Preprocess accessibility request."""
        try:
            logger.debug(f"Preprocessing request for user {request.user_id}")

            # Validate and clean data
            processed_request = self._validate_and_clean_request(request)

            # Enhance with defaults
            processed_request = self._enhance_with_defaults(processed_request)

            # Normalize data formats
            processed_request = self._normalize_data_formats(processed_request)

            logger.debug(f"Request preprocessing completed for user {request.user_id}")
            return processed_request

        except Exception as e:
            logger.error(f"Request preprocessing failed: {e}")
            raise

    def _validate_and_clean_request(self, request: AccessibilityRequest) -> AccessibilityRequest:
        """Validate and clean request data."""
        # Create a copy to avoid modifying original
        cleaned_data = request.dict()

        # Clean visual data
        if cleaned_data.get('visual_data'):
            cleaned_data['visual_data'] = self._clean_visual_data(cleaned_data['visual_data'])

        # Clean audio data
        if cleaned_data.get('audio_data'):
            cleaned_data['audio_data'] = self._clean_audio_data(cleaned_data['audio_data'])

        # Clean motor data
        if cleaned_data.get('motor_data'):
            cleaned_data['motor_data'] = self._clean_motor_data(cleaned_data['motor_data'])

        # Clean cognitive data
        if cleaned_data.get('cognitive_data'):
            cleaned_data['cognitive_data'] = self._clean_cognitive_data(cleaned_data['cognitive_data'])

        return AccessibilityRequest(**cleaned_data)

    def _enhance_with_defaults(self, request: AccessibilityRequest) -> AccessibilityRequest:
        """Enhance request with default values."""
        enhanced_data = request.dict()

        # Set default accessibility types if none specified
        if not enhanced_data.get('accessibility_types'):
            enhanced_data['accessibility_types'] = [AccessibilityType.MULTIMODAL]

        # Set default context if none provided
        if not enhanced_data.get('context'):
            enhanced_data['context'] = {
                'platform': 'web',
                'device_type': 'desktop',
                'analysis_mode': 'comprehensive'
            }

        # Set default user preferences
        if not enhanced_data.get('user_preferences'):
            enhanced_data['user_preferences'] = {
                'detailed_analysis': True,
                'include_recommendations': True,
                'language': 'en'
            }

        return AccessibilityRequest(**enhanced_data)

    def _normalize_data_formats(self, request: AccessibilityRequest) -> AccessibilityRequest:
        """Normalize data formats."""
        normalized_data = request.dict()

        # Normalize visual data
        if normalized_data.get('visual_data'):
            normalized_data['visual_data'] = self._normalize_visual_data(normalized_data['visual_data'])

        # Normalize audio data
        if normalized_data.get('audio_data'):
            normalized_data['audio_data'] = self._normalize_audio_data(normalized_data['audio_data'])

        # Normalize motor data
        if normalized_data.get('motor_data'):
            normalized_data['motor_data'] = self._normalize_motor_data(normalized_data['motor_data'])

        # Normalize cognitive data
        if normalized_data.get('cognitive_data'):
            normalized_data['cognitive_data'] = self._normalize_cognitive_data(normalized_data['cognitive_data'])

        return AccessibilityRequest(**normalized_data)

    def _clean_visual_data(self, visual_data: dict[str, Any]) -> dict[str, Any]:
        """Clean visual data."""
        cleaned = {}

        # Clean image data
        if 'images' in visual_data:
            cleaned['images'] = self._clean_image_list(visual_data['images'])

        # Clean color data
        if 'colors' in visual_data:
            cleaned['colors'] = self._clean_color_data(visual_data['colors'])

        # Clean text data
        if 'text' in visual_data:
            cleaned['text'] = self._clean_text_data(visual_data['text'])

        # Clean layout data
        if 'layout' in visual_data:
            cleaned['layout'] = self._clean_layout_data(visual_data['layout'])

        return cleaned

    def _clean_audio_data(self, audio_data: dict[str, Any]) -> dict[str, Any]:
        """Clean audio data."""
        cleaned = {}

        # Clean audio files
        if 'audio_files' in audio_data:
            cleaned['audio_files'] = self._clean_audio_files(audio_data['audio_files'])

        # Clean speech data
        if 'speech' in audio_data:
            cleaned['speech'] = self._clean_speech_data(audio_data['speech'])

        # Clean sound effects
        if 'sound_effects' in audio_data:
            cleaned['sound_effects'] = self._clean_sound_effects(audio_data['sound_effects'])

        return cleaned

    def _clean_motor_data(self, motor_data: dict[str, Any]) -> dict[str, Any]:
        """Clean motor data."""
        cleaned = {}

        # Clean interaction data
        if 'interactions' in motor_data:
            cleaned['interactions'] = self._clean_interaction_data(motor_data['interactions'])

        # Clean gesture data
        if 'gestures' in motor_data:
            cleaned['gestures'] = self._clean_gesture_data(motor_data['gestures'])

        # Clean navigation data
        if 'navigation' in motor_data:
            cleaned['navigation'] = self._clean_navigation_data(motor_data['navigation'])

        return cleaned

    def _clean_cognitive_data(self, cognitive_data: dict[str, Any]) -> dict[str, Any]:
        """Clean cognitive data."""
        cleaned = {}

        # Clean content data
        if 'content' in cognitive_data:
            cleaned['content'] = self._clean_content_data(cognitive_data['content'])

        # Clean structure data
        if 'structure' in cognitive_data:
            cleaned['structure'] = self._clean_structure_data(cognitive_data['structure'])

        # Clean complexity data
        if 'complexity' in cognitive_data:
            cleaned['complexity'] = self._clean_complexity_data(cognitive_data['complexity'])

        return cleaned

    def _normalize_visual_data(self, visual_data: dict[str, Any]) -> dict[str, Any]:
        """Normalize visual data formats."""
        normalized = visual_data.copy()

        # Normalize image formats
        if 'images' in normalized:
            normalized['images'] = self._normalize_image_formats(normalized['images'])

        # Normalize color formats
        if 'colors' in normalized:
            normalized['colors'] = self._normalize_color_formats(normalized['colors'])

        return normalized

    def _normalize_audio_data(self, audio_data: dict[str, Any]) -> dict[str, Any]:
        """Normalize audio data formats."""
        normalized = audio_data.copy()

        # Normalize audio formats
        if 'audio_files' in normalized:
            normalized['audio_files'] = self._normalize_audio_formats(normalized['audio_files'])

        return normalized

    def _normalize_motor_data(self, motor_data: dict[str, Any]) -> dict[str, Any]:
        """Normalize motor data formats."""
        normalized = motor_data.copy()

        # Normalize interaction formats
        if 'interactions' in normalized:
            normalized['interactions'] = self._normalize_interaction_formats(normalized['interactions'])

        return normalized

    def _normalize_cognitive_data(self, cognitive_data: dict[str, Any]) -> dict[str, Any]:
        """Normalize cognitive data formats."""
        normalized = cognitive_data.copy()

        # Normalize content formats
        if 'content' in normalized:
            normalized['content'] = self._normalize_content_formats(normalized['content'])

        return normalized

    # Helper methods for specific data cleaning
    def _clean_image_list(self, images: list[Any]) -> list[dict[str, Any]]:
        """Clean image list."""
        cleaned_images = []
        for img in images:
            if isinstance(img, dict):
                cleaned_img = {
                    'url': img.get('url', ''),
                    'alt_text': img.get('alt_text', ''),
                    'width': img.get('width', 0),
                    'height': img.get('height', 0)
                }
                cleaned_images.append(cleaned_img)
        return cleaned_images

    def _clean_color_data(self, colors: dict[str, Any]) -> dict[str, Any]:
        """Clean color data."""
        return {
            'background': colors.get('background', '#ffffff'),
            'foreground': colors.get('foreground', '#000000'),
            'accent': colors.get('accent', '#0066cc')
        }

    def _clean_text_data(self, text: dict[str, Any]) -> dict[str, Any]:
        """Clean text data."""
        return {
            'content': text.get('content', ''),
            'font_size': text.get('font_size', 16),
            'font_family': text.get('font_family', 'Arial'),
            'line_height': text.get('line_height', 1.5)
        }

    def _clean_layout_data(self, layout: dict[str, Any]) -> dict[str, Any]:
        """Clean layout data."""
        return {
            'structure': layout.get('structure', 'linear'),
            'spacing': layout.get('spacing', 'normal'),
            'alignment': layout.get('alignment', 'left')
        }

    def _clean_audio_files(self, audio_files: list[Any]) -> list[dict[str, Any]]:
        """Clean audio files."""
        cleaned_files = []
        for audio in audio_files:
            if isinstance(audio, dict):
                cleaned_audio = {
                    'url': audio.get('url', ''),
                    'duration': audio.get('duration', 0),
                    'format': audio.get('format', 'mp3'),
                    'has_captions': audio.get('has_captions', False)
                }
                cleaned_files.append(cleaned_audio)
        return cleaned_files

    def _clean_speech_data(self, speech: dict[str, Any]) -> dict[str, Any]:
        """Clean speech data."""
        return {
            'text': speech.get('text', ''),
            'rate': speech.get('rate', 'normal'),
            'volume': speech.get('volume', 'normal'),
            'language': speech.get('language', 'en')
        }

    def _clean_sound_effects(self, sound_effects: list[Any]) -> list[dict[str, Any]]:
        """Clean sound effects."""
        cleaned_effects = []
        for effect in sound_effects:
            if isinstance(effect, dict):
                cleaned_effect = {
                    'type': effect.get('type', 'notification'),
                    'volume': effect.get('volume', 'medium'),
                    'duration': effect.get('duration', 1.0)
                }
                cleaned_effects.append(cleaned_effect)
        return cleaned_effects

    def _clean_interaction_data(self, interactions: list[Any]) -> list[dict[str, Any]]:
        """Clean interaction data."""
        cleaned_interactions = []
        for interaction in interactions:
            if isinstance(interaction, dict):
                cleaned_interaction = {
                    'type': interaction.get('type', 'click'),
                    'target_size': interaction.get('target_size', 44),
                    'spacing': interaction.get('spacing', 8)
                }
                cleaned_interactions.append(cleaned_interaction)
        return cleaned_interactions

    def _clean_gesture_data(self, gestures: list[Any]) -> list[dict[str, Any]]:
        """Clean gesture data."""
        cleaned_gestures = []
        for gesture in gestures:
            if isinstance(gesture, dict):
                cleaned_gesture = {
                    'type': gesture.get('type', 'tap'),
                    'complexity': gesture.get('complexity', 'simple'),
                    'required': gesture.get('required', False)
                }
                cleaned_gestures.append(cleaned_gesture)
        return cleaned_gestures

    def _clean_navigation_data(self, navigation: dict[str, Any]) -> dict[str, Any]:
        """Clean navigation data."""
        return {
            'type': navigation.get('type', 'hierarchical'),
            'depth': navigation.get('depth', 3),
            'breadcrumbs': navigation.get('breadcrumbs', False)
        }

    def _clean_content_data(self, content: dict[str, Any]) -> dict[str, Any]:
        """Clean content data."""
        return {
            'text': content.get('text', ''),
            'complexity': content.get('complexity', 'medium'),
            'reading_level': content.get('reading_level', 'grade-8')
        }

    def _clean_structure_data(self, structure: dict[str, Any]) -> dict[str, Any]:
        """Clean structure data."""
        return {
            'headings': structure.get('headings', []),
            'sections': structure.get('sections', []),
            'navigation': structure.get('navigation', {})
        }

    def _clean_complexity_data(self, complexity: dict[str, Any]) -> dict[str, Any]:
        """Clean complexity data."""
        return {
            'cognitive_load': complexity.get('cognitive_load', 'medium'),
            'attention_required': complexity.get('attention_required', 'normal'),
            'memory_load': complexity.get('memory_load', 'low')
        }

    # Normalization helper methods
    def _normalize_image_formats(self, images: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Normalize image formats."""
        for img in images:
            # Ensure dimensions are integers
            img['width'] = int(img.get('width', 0))
            img['height'] = int(img.get('height', 0))
        return images

    def _normalize_color_formats(self, colors: dict[str, Any]) -> dict[str, Any]:
        """Normalize color formats."""
        # Ensure colors are in hex format
        for key, value in colors.items():
            if isinstance(value, str) and not value.startswith('#'):
                colors[key] = f"#{value}"
        return colors

    def _normalize_audio_formats(self, audio_files: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Normalize audio formats."""
        for audio in audio_files:
            # Ensure duration is float
            audio['duration'] = float(audio.get('duration', 0))
        return audio_files

    def _normalize_interaction_formats(self, interactions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Normalize interaction formats."""
        for interaction in interactions:
            # Ensure sizes are integers
            interaction['target_size'] = int(interaction.get('target_size', 44))
            interaction['spacing'] = int(interaction.get('spacing', 8))
        return interactions

    def _normalize_content_formats(self, content: dict[str, Any]) -> dict[str, Any]:
        """Normalize content formats."""
        # Ensure text is string
        content['text'] = str(content.get('text', ''))
        return content
