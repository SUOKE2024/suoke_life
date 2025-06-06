"""
__init__ - 索克生活项目模块
"""

from .calculator import BaguaCalculator
from .data import BAGUA_DATA, BAGUA_ORGAN_MAP

"""
八卦配属算法模块

实现八卦与人体脏腑对应的分析功能
"""


__all__ = [
    "BaguaCalculator",
    "BAGUA_DATA",
    "BAGUA_ORGAN_MAP",
] 