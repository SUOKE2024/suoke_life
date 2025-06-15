"""
索克生活闻诊服务

基于AI的中医闻诊音频分析服务，采用Python 3.13.3和现代化技术栈构建。
"""

from typing import Dict, List, Any, Optional, Union

__version__ = "1.0.0"
__author__ = "Song Xu"
__email__ = "song.xu@icloud.com"

# 导出主要类和函数
__all__ = [
    "AudioAnalyzer",
    "TCMFeatureExtractor", 
    "AudioMetadata",
    "AnalysisRequest",
    "TCMDiagnosis",
    "__version__",
]

# 延迟导入以避免循环依赖
def __getattr__(name: str) -> Any:
    """延迟导入模块组件"""
    if name == "AudioAnalyzer":
        from .core.audio_analyzer import AudioAnalyzer
        return AudioAnalyzer
    elif name == "TCMFeatureExtractor":
        from .core.tcm_analyzer import TCMFeatureExtractor
        return TCMFeatureExtractor
    elif name == "AudioMetadata":
        from .models.audio_models import AudioMetadata
        return AudioMetadata
    elif name == "AnalysisRequest":
        from .models.audio_models import AnalysisRequest
        return AnalysisRequest
    elif name == "TCMDiagnosis":
        from .models.tcm_models import TCMDiagnosis
        return TCMDiagnosis
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")