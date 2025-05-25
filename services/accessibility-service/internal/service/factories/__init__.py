#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
服务工厂模块
提供服务实例的创建和配置
"""

from .service_factory import ServiceFactory
from .accessibility_factory import AccessibilityServiceFactory

__all__ = [
    'ServiceFactory',
    'AccessibilityServiceFactory'
] 