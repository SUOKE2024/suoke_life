"""
无障碍服务模块化组件

将原有的大型服务类拆分为更小、更专注的模块，提高代码的可维护性和可测试性。
"""

from .blind_assistance import BlindAssistanceModule
from .content_conversion import ContentConversionModule
from .screen_reading import ScreenReadingModule
from .settings_manager import SettingsManagerModule
from .sign_language import SignLanguageModule
from .translation import TranslationModule
from .voice_assistance import VoiceAssistanceModule

__all__ = [
    "BlindAssistanceModule",
    "ContentConversionModule",
    "ScreenReadingModule",
    "SettingsManagerModule",
    "SignLanguageModule",
    "TranslationModule",
    "VoiceAssistanceModule",
]
