"""
__init__ - 索克生活项目模块
"""

from .calculation import router as calculation_router
from .calendar import router as calendar_router
from .constitution import router as constitution_router

"""
API v1版本

算诊微服务的API接口第一版本
"""


__all__ = [
    "calculation_router",
    "calendar_router", 
    "constitution_router",
] 