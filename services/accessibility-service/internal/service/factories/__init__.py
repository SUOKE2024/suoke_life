#!/usr/bin/env python

"""
服务工厂模块
提供服务实例的创建和配置
"""

from .accessibility_factory import AccessibilityServiceFactory
from .service_factory import ServiceFactory

__all__ = ["AccessibilityServiceFactory", "ServiceFactory"]
