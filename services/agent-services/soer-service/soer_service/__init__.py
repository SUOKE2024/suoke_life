from typing import Any, Dict, List, Optional, Union

"""
__init__ - 索克生活项目模块
"""

from .main import create_app

"""
索儿智能体服务 (Soer Agent Service)

索克生活平台的营养与生活方式管理智能体，专注于：
- 营养分析与膳食建议
- 生活方式优化
- 健康数据监测
- 个性化健康方案制定
"""

__version__ = "0.1.0"
__author__ = "Suoke Life Team"
__email__ = "dev@suoke.life"


__all__ = ["create_app", "__version__"]
