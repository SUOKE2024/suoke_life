#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API路由包
"""

from flask import Blueprint
from .web_search import web_search_bp
from .specialized_retrievers import specialized_bp

# 导出的蓝图
__all__ = [
    'web_search_bp',
    'specialized_bp',
    'api_bp'
]

# 主API蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')