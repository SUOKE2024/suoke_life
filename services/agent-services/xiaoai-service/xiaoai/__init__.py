#!/usr/bin/env python3
"""
小艾智能体核心包
XiaoAI Agent Core Package

小艾是索克生活平台的核心AI智能体, 专注于提供智能健康管理服务。
本包提供了小艾智能体的核心功能模块, 包括:

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

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional

from .agent.agent_manager import AgentManager as _AgentManager
from .delivery.xiaoai_service_impl import XiaoAIServiceImpl as _XiaoAIServiceImpl
from .service.xiaoai_service_impl import XiaoaiServiceImpl as _XiaoaiServiceImpl

# 版本信息
__version__ = "1.0.0"
__author__ = "Suoke Life Team"
__email__ = "dev@suokelife.com"
__license__ = "MIT"

# 设置日志
logger = logging.getLogger(__name__)

# 类型检查时的导入
if TYPE_CHECKING:
    from .four_diagnosis.coordinator.coordinator import (
        FourDiagnosisCoordinator,
    )

# 延迟导入的组件
AgentManager: type[_AgentManager] | None = None
XiaoAIServiceImpl: type[_XiaoAIServiceImpl] | None = None
FourDiagnosisCoordinator: type[FourDiagnosisCoordinator] | None = None
XiaoAIService: type[_XiaoaiServiceImpl] | None = None


def _lazy_import_agent_manager() -> type[_AgentManager]:
    """延迟导入 AgentManager"""
    global _AgentManager
    if _AgentManager is None:
        try:
            from .agent.agent_manager import AgentManager
            AgentManager = AgentManager
        except ImportError as e:
            logger.warning(f"Failed to import AgentManager: {e}")
            raise ImportError(
                "AgentManager is not available. "
                "Please ensure all dependencies are installed."
            ) from e
    return _AgentManager


def _lazy_import_service_impl() -> type[_XiaoAIServiceImpl]:
    """延迟导入 XiaoAIServiceImpl"""
    global _XiaoAIServiceImpl
    if _XiaoAIServiceImpl is None:
        try:
            from .delivery.xiaoai_service_impl import XiaoAIServiceImpl
            XiaoAIServiceImpl = XiaoAIServiceImpl
        except ImportError as e:
            logger.warning(f"Failed to import XiaoAIServiceImpl: {e}")
            raise ImportError(
                "XiaoAIServiceImpl is not available. "
                "Please ensure all dependencies are installed."
            ) from e
    return _XiaoAIServiceImpl


def _lazy_import_coordinator() -> type[_FourDiagnosisCoordinator]:
    """延迟导入 FourDiagnosisCoordinator"""
    global _FourDiagnosisCoordinator
    if _FourDiagnosisCoordinator is None:
        try:
            from .four_diagnosis.coordinator.coordinator import FourDiagnosisCoordinator
            FourDiagnosisCoordinator = FourDiagnosisCoordinator
        except ImportError as e:
            logger.warning(f"Failed to import FourDiagnosisCoordinator: {e}")
            raise ImportError(
                "FourDiagnosisCoordinator is not available. "
                "Please ensure all dependencies are installed."
            ) from e
    return _FourDiagnosisCoordinator


def _lazy_import_service() -> type[_XiaoaiServiceImpl]:
    """延迟导入 XiaoAIService"""
    global _XiaoaiServiceImpl
    if _XiaoaiServiceImpl is None:
        try:
            from .service.xiaoai_service_impl import XiaoaiServiceImpl
            XiaoaiServiceImpl = XiaoaiServiceImpl
        except ImportError as e:
            logger.warning(f"Failed to import XiaoAIService: {e}")
            raise ImportError(
                "XiaoAIService is not available. "
                "Please ensure all dependencies are installed."
            ) from e
    return _XiaoaiServiceImpl


# 公共API
def get_agent_manager() -> type[_AgentManager]:
    """获取 AgentManager 类"""
    return _lazy_import_agent_manager()


def get_service_impl() -> type[_XiaoAIServiceImpl]:
    """获取 XiaoAIServiceImpl 类"""
    return _lazy_import_service_impl()


def get_coordinator() -> type[_FourDiagnosisCoordinator]:
    """获取 FourDiagnosisCoordinator 类"""
    return _lazy_import_coordinator()


def get_service() -> type[_XiaoaiServiceImpl]:
    """获取 XiaoAIService 类"""
    return _lazy_import_service()


# 向后兼容的属性访问
def __getattr__(name: str) -> Any:
    """动态属性访问, 提供向后兼容性"""
    if name == "AgentManager":
        return get_agent_manager()
    elif name == "XiaoAIServiceImpl":
        return get_service_impl()
    elif name == "FourDiagnosisCoordinator":
        return get_coordinator()
    elif name == "XiaoAIService":
        return get_service()
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# 导出的公共API
__all__ = [
    "AgentManager",
    "FourDiagnosisCoordinator",
    "XiaoAIService",
    "XiaoAIServiceImpl",
    "__author__",
    "__email__",
    "__license__",
    # 版本信息
    "__version__",
    # 工厂函数
    "get_agent_manager",
    "get_coordinator",
    "get_service",
    "get_service_impl",
]
