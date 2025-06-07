#!/usr/bin/env python3
"""
小艾智能体核心包
XiaoAI Agent Core Package

小艾是索克生活平台的核心AI智能体,专注于提供智能健康管理服务.
本包提供了小艾智能体的核心功能模块,包括:
- 智能体管理 (Agent Management)
- 四诊协调 (Four Diagnosis Coordination)
- 服务实现 (Service Implementation)
- 配置管理 (Configuration Management)
- 工具集成 (Utility Integration)

主要特性:
- 基于中医理论的智能诊断
- 多模态数据处理
- 个性化健康建议
- 实时健康监测
- 预防性健康管理

使用示例:
    >>> from xiaoai import AgentManager
    >>> manager = AgentManager()
    >>> await manager.initialize()
"""

import logging
from typing import TYPE_CHECKING, Any, Optional

# 版本信息
__version__ = "1.0.0"
__author__ = "Suoke Life Team"
__email__ = "dev@suokelife.com"
__license__ = "MIT"

# 设置日志
_logger = logging.getLogger(__name__)

# 类型检查时的导入
if TYPE_CHECKING:
    from .agent.agent_manager import AgentManager as _AgentManager
    from .service.xiaoai_service_impl import XiaoaiServiceImpl as _XiaoaiServiceImpl

# 延迟导入的组件
_AgentManager: type | None = None
_XiaoaiServiceImpl: type | None = None

def _lazy_import_agent_manager() -> type:
    """延迟导入 AgentManager"""
    global _AgentManager
    if _AgentManager is None:
        try:
            from .agent.agent_manager import AgentManager
            _AgentManager = AgentManager
        except ImportError as e:
            _logger.warning(f"Failed to import AgentManager: {e}")
            raise ImportError(
                "AgentManager is not available. "
                "Please ensure all dependencies are installed."
            ) from e
    return _AgentManager

def _lazy_import_service_impl() -> type:
    """延迟导入 XiaoaiServiceImpl"""
    global _XiaoaiServiceImpl
    if _XiaoaiServiceImpl is None:
        try:
            from .service.xiaoai_service_impl import XiaoaiServiceImpl
            _XiaoaiServiceImpl = XiaoaiServiceImpl
        except ImportError as e:
            _logger.warning(f"Failed to import XiaoaiServiceImpl: {e}")
            raise ImportError(
                "XiaoaiServiceImpl is not available. "
                "Please ensure all dependencies are installed."
            ) from e
    return _XiaoaiServiceImpl

# 公共API
def get_agent_manager() -> type:
    """获取 AgentManager 类"""
    return _lazy_import_agent_manager()

def get_service_impl() -> type:
    """获取 XiaoaiServiceImpl 类"""
    return _lazy_import_service_impl()

# 向后兼容的属性访问
def __getattr__(name: str) -> Any:
    """动态属性访问,提供向后兼容性"""
    if name == "AgentManager":
        return get_agent_manager()
    elif name == "XiaoaiServiceImpl":
        return get_service_impl()
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# 导出的公共API
__all__ = [
    "AgentManager",
    "XiaoaiServiceImpl",
    "__author__",
    "__email__",
    "__license__",
    "__version__",
    "get_agent_manager",
    "get_service_impl",
]
