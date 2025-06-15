"""
索克生活无障碍服务核心服务模块

提供无障碍功能的核心实现，包括：
- 导盲服务
- 手语识别
- 屏幕阅读
- 语音辅助
- 内容转换
- 后台数据收集
- 危机报警服务
- 实时语音翻译
"""

from .app import AccessibilityApp

__version__ = "2.0.0"
__all__ = ["AccessibilityApp"]
