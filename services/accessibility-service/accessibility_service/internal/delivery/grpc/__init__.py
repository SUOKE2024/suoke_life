"""
__init__ - 索克生活项目模块
"""

from .servicer import AccessibilityServicer
from .translation_handler import TranslationHandler

"""
gRPC服务实现

包含gRPC服务的具体实现：
- servicer: gRPC服务器实现
- translation_handler: 翻译处理器
"""


__all__ = [
    "AccessibilityServicer",
    "TranslationHandler"
]
