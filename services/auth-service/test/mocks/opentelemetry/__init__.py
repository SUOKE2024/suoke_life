#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mock OpenTelemetry模块
"""

# 创建虚拟的trace模块
class _TraceMock:
    """Trace模块的模拟"""
    
    def get_tracer(self, name, version=None, schema_url=None):
        """获取模拟追踪器"""
        return TracerMock()
        
    def set_tracer_provider(self, provider):
        """设置模拟追踪提供者"""
        pass

# 创建虚拟的tracer类
class TracerMock:
    """追踪器的模拟"""
    
    def start_as_current_span(self, name, context=None, kind=None, attributes=None, links=None, start_time=None):
        """开始一个模拟的span"""
        return SpanContextManager()
        
    def start_span(self, name, context=None, kind=None, attributes=None, links=None, start_time=None):
        """开始一个模拟的span"""
        return SpanMock()

# 创建虚拟的span上下文管理器
class SpanContextManager:
    """Span上下文管理器的模拟"""
    
    def __enter__(self):
        """进入上下文"""
        return SpanMock()
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        pass

# 创建虚拟的span类
class SpanMock:
    """Span的模拟"""
    
    def set_attribute(self, key, value):
        """设置属性"""
        pass
        
    def add_event(self, name, attributes=None, timestamp=None):
        """添加事件"""
        pass
        
    def record_exception(self, exception, attributes=None, timestamp=None):
        """记录异常"""
        pass
        
    def set_status(self, status, description=None):
        """设置状态"""
        pass
        
    def end(self, end_time=None):
        """结束span"""
        pass

# 导出模拟的trace模块
trace = _TraceMock()

# 其他可能需要的模拟
class PropagatorMock:
    """传播器的模拟"""
    
    def inject(self, context, carrier):
        """注入上下文到载体"""
        pass
        
    def extract(self, context, carrier):
        """从载体提取上下文"""
        return {}

# 导出可能需要的其他模块
propagators = type('', (), {'get_global_textmap': lambda: PropagatorMock()})()