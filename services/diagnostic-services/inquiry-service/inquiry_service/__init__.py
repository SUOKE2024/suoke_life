from typing import Dict, List, Any, Optional, Union

"""
__init__ - 索克生活项目模块
"""

from inquiry_service.core.exceptions import InquiryServiceError

"""
问诊服务 (Inquiry Service)

索克生活智能健康管理平台的核心诊断服务，负责通过智能对话收集用户的健康信息，
提取症状，进行中医证型匹配，并评估健康风险。

主要功能：
- 智能问诊对话管理
- 症状提取与分析
- 中医证型匹配
- 健康风险评估
- 中医知识库管理
"""

__version__ = "1.0.0"
__author__ = "Suoke Life Team"
__email__ = "dev@suokelife.com"


__all__ = [
    "InquiryServiceError",
    "__author__",
    "__email__",
    "__version__",
]
