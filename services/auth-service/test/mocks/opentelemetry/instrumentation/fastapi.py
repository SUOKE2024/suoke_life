#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mock FastAPI instrumentation模块
"""

class FastAPIInstrumentor:
    """Mock FastAPI instrumentor"""
    
    @staticmethod
    def instrument_app(app):
        """模拟instrumentor"""
        return app
    
    @staticmethod
    def uninstrument_app(app):
        """模拟uninstrumentor"""
        return app