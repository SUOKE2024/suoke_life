#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mock OpenTelemetry SQLAlchemy instrumentation模块
"""

class SQLAlchemyInstrumentor:
    """SQLAlchemy instrumentation的模拟"""
    
    @classmethod
    def instrument(cls, engine=None, **kwargs):
        """为SQLAlchemy引擎添加instrumentation"""
        pass
        
    @classmethod
    def uninstrument(cls, engine=None):
        """移除SQLAlchemy引擎的instrumentation"""
        pass 