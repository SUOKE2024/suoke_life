"""
小艾智能体代理模块

提供XiaoaiAgent类的兼容性导入
"""

# 从当前模块的__init__.py导入XiaoaiAgent
from . import XiaoaiAgent

# 为了兼容性, 提供多种别名
XiaoAiAgent = XiaoaiAgent
XiaoAIAgent = XiaoaiAgent

__all__ = ["XiaoAiAgent", "XiaoaiAgent", "XiaoAIAgent"]
