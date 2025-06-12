from typing import Any, Dict, List, Optional, Union

"""
__init__ - 索克生活项目模块
"""

from .analysis import AnalysisService
from .calculation import CalculationService
from .recommendation import RecommendationService

"""
服务层

提供算诊相关的业务逻辑服务
"""


__all__ = [
    "CalculationService",
    "AnalysisService",
    "RecommendationService",
]
