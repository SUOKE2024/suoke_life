from typing import Dict, List, Any, Optional, Union

"""
__init__ - 索克生活项目模块
"""

from .core.agent import LaokeAgent
from .core.config import Config, get_config
from .core.exceptions import ConfigurationException, LaokeServiceException, ValidationException

"""
老克智能体服务 (Laoke Service)

索克生活平台的知识传播和社区管理智能体服务
"""

__version__ = "1.0.0"
__author__ = "Suoke Life Team"
__email__ = "dev@suoke.life"
__description__ = "老克智能体服务 - 索克生活平台的知识传播和社区管理智能体"

# 主要组件导出

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "LaokeAgent",
    "Config",
    "get_config",
    "LaokeServiceException",
    "ConfigurationException",
    "ValidationException",
]
