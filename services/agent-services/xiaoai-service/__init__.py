#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小艾智能体服务包
XiaoAI Agent Service Package

提供基于大模型的智能健康咨询和四诊协调服务
"""

__version__ = "1.0.0"
__author__ = "SUOKE Team"
__description__ = "小艾智能体服务 - 智能健康管理助手"

# 导出主要组件
try:
    from .xiaoai.agent.agent_manager import AgentManager
    from .xiaoai.delivery.xiaoai_service_impl import XiaoAIServiceImpl
    __all__ = [
        "AgentManager",
        "XiaoAIServiceImpl",
    ]
except ImportError:
    # 在测试环境中，相对导入可能失败
    __all__ = [] 