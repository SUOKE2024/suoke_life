#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mock SQLAlchemy instrumentation模块
"""

class SQLAlchemyInstrumentor:
    """Mock SQLAlchemy instrumentor"""
    
    @staticmethod
    def instrument(engine=None):
        """模拟instrumentor"""
        return engine
    
    @staticmethod
    def uninstrument(engine=None):
        """模拟uninstrumentor"""
        return engine