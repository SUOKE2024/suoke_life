#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小艾智能体核心包
XiaoAI Agent Core Package

提供智能健康管理的核心功能模块
"""

__version__ = "1.0.0"

# 导出核心组件
try:
    from .agent.agent_manager import AgentManager
except ImportError:
    AgentManager = None

try:
    from .delivery.xiaoai_service_impl import XiaoAIServiceImpl
except ImportError:
    XiaoAIServiceImpl = None

try:
    from .four_diagnosis.coordinator.coordinator import FourDiagnosisCoordinator
except ImportError:
    FourDiagnosisCoordinator = None

try:
    from .service.xiaoai_service_impl import XiaoAIService
except ImportError:
    XiaoAIService = None

__all__ = [
    "AgentManager",
    "XiaoAIServiceImpl", 
    "FourDiagnosisCoordinator",
    "XiaoAIService",
] 