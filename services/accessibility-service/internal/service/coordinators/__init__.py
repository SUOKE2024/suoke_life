#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
服务协调器模块
提供服务间的协调和统一的API接口
"""

from .accessibility_coordinator import AccessibilityServiceCoordinator

__all__ = [
    'AccessibilityServiceCoordinator'
] 