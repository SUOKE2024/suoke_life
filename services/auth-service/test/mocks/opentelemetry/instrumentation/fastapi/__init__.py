#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mock OpenTelemetry FastAPI instrumentation模块
"""

class FastAPIInstrumentor:
    """FastAPI instrumentation的模拟"""
    
    @classmethod
    def instrument_app(cls, app, **kwargs):
        """为FastAPI应用程序添加instrumentation"""
        return app
        
    @classmethod
    def uninstrument_app(cls, app):
        """移除FastAPI应用程序的instrumentation"""
        return app 