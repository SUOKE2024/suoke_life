#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mock OpenTelemetry Redis instrumentation模块
"""

class RedisInstrumentor:
    """Redis instrumentation的模拟"""
    
    @classmethod
    def instrument(cls, **kwargs):
        """为Redis客户端添加instrumentation"""
        pass
        
    @classmethod
    def uninstrument(cls):
        """移除Redis客户端的instrumentation"""
        pass 