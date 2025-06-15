#!/usr/bin/env python

"""
无障碍服务接口包
包含所有服务接口定义
"""

# 导入基础接口
from .audio_visualization_interface import (
    AnimationType,
    AudioFeature,
    ColorScheme,
    IAudioVisualizationService,
    VisualizationStyle,
    VisualizationType,
)
from .base_interfaces import (
    IBlindAssistanceService,
    ICacheManager,
    IContentConversionService,
    IHealthMonitor,
    IModelManager,
    IScreenReadingService,
    ISettingsService,
    ISignLanguageService,
    ITranslationService,
    IVoiceAssistanceService,
)

# 导入高级接口
from .bci_interface import (
    BCICommand,
    BCIDeviceType,
    BCIState,
    IBCIService,
    NeurofeedbackType,
    SignalType,
)
from .eye_tracking_interface import IEyeTrackingService
from .haptic_feedback_interface import (
    HapticDeviceType,
    HapticIntensity,
    HapticLocation,
    HapticModality,
    HapticPattern,
    IHapticFeedbackService,
)
from .memory_assistance_interface import (
    AssistanceLevel,
    IMemoryAssistanceService,
    MemoryCategory,
    MemoryTrigger,
    MemoryType,
    ReminderType,
)
from .spatial_audio_interface import (
    AudioLayer,
    AudioRenderingEngine,
    AudioSourceType,
    ISpatialAudioService,
    RoomAcoustics,
    SpatialAudioFormat,
)
from .subtitle_generation_interface import ISubtitleGenerationService
from .vr_accessibility_interface import (
    IVRAccessibilityService,
    VRAccessibilityFeature,
    VRDeviceType,
    VRDisplayMode,
    VRInteractionMode,
    VRTrackingType,
)

__all__ = [
    # 基础接口
    "IBlindAssistanceService",
    "ISignLanguageService",
    "IScreenReadingService",
    "IVoiceAssistanceService",
    "IContentConversionService",
    "ITranslationService",
    "ISettingsService",
    "IModelManager",
    "IHealthMonitor",
    "ICacheManager",
    # BCI接口
    "IBCIService",
    "BCIDeviceType",
    "SignalType",
    "BCICommand",
    "NeurofeedbackType",
    "BCIState",
    # 触觉反馈接口
    "IHapticFeedbackService",
    "HapticDeviceType",
    "HapticModality",
    "HapticPattern",
    "HapticIntensity",
    "HapticLocation",
    # 空间音频接口
    "ISpatialAudioService",
    "AudioRenderingEngine",
    "SpatialAudioFormat",
    "AudioSourceType",
    "RoomAcoustics",
    "AudioLayer",
    # VR无障碍接口
    "IVRAccessibilityService",
    "VRDeviceType",
    "VRInteractionMode",
    "VRAccessibilityFeature",
    "VRTrackingType",
    "VRDisplayMode",
    # 音频可视化接口
    "IAudioVisualizationService",
    "VisualizationType",
    "AudioFeature",
    "VisualizationStyle",
    "ColorScheme",
    "AnimationType",
    # 记忆辅助接口
    "IMemoryAssistanceService",
    "MemoryType",
    "ReminderType",
    "MemoryTrigger",
    "MemoryCategory",
    "AssistanceLevel",
    # 字幕生成接口
    "ISubtitleGenerationService",
    # 眼动追踪接口
    "IEyeTrackingService",
]
