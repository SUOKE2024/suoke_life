"""
__init__ - 索克生活项目模块
"""

from .internal.service.app import AccessibilityService

"""
无障碍服务 (Accessibility Service)

为索克生活项目提供全面的无障碍功能支持，包括：
- 导盲服务
- 语音辅助
- 屏幕阅读
- 手语识别
- 内容转换
- 多语言翻译

版本: 2.1.0
作者: 索克生活团队
"""

__version__ = "2.1.0"
__author__ = "索克生活团队"
__email__ = "support@suokelife.com"

# 导出主要组件

__all__ = [
    "AccessibilityService",
    "__version__",
    "__author__",
    "__email__"
]
