"""
无障碍服务模块化组件

将原有的大型服务类拆分为更小、更专注的模块，提高代码的可维护性和可测试性。
"""

from .blind_assistance import BlindAssistanceModule
# from .sign_language import SignLanguageModule
# from .voice_assistance import VoiceAssistanceModule
# from .screen_reading import ScreenReadingModule
# from .content_conversion import ContentConversionModule
# from .translation import TranslationModule
# from .settings_manager import SettingsManagerModule

__all__ = [
    'BlindAssistanceModule',
    # 'SignLanguageModule', 
    # 'VoiceAssistanceModule',
    # 'ScreenReadingModule',
    # 'ContentConversionModule',
    # 'TranslationModule',
    # 'SettingsManagerModule'
] 