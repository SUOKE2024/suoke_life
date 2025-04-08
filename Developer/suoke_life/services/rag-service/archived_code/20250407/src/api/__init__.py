#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
索克生活APP - RAG服务API模块
=======================
包含HTTP API路由和处理器
"""

from .app import create_app
from .routes import register_routes, api_bp, web_search_bp, specialized_bp

__all__ = ["create_app", "register_routes", "api_bp", "web_search_bp", "specialized_bp"]