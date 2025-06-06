"""
__init__ - 索克生活项目模块
"""

from .core.agent import LaoKeAgent
from .core.config import Settings, get_settings
from .core.exceptions import ConfigurationError, LaoKeServiceError, ValidationError

"""
老克智能体服务 (Laoke Service)

索克生活平台的知识传播和社区管理智能体服务
"""

__version__ = "1.0.0"
__author__ = "Suoke Life Team"
__email__ = "dev@suokelife.com"
__description__ = "老克智能体服务 - 索克生活平台的知识传播和社区管理智能体"

# 主要组件导出

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "LaoKeAgent",
    "Settings",
    "get_settings",
    "LaoKeServiceError",
    "ConfigurationError",
    "ValidationError",
]
