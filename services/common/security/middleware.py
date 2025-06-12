from typing import Any, Dict, List, Optional, Union

"""
middleware - 索克生活项目模块
"""

from functools import wraps

from flask import Flask, g, request


def add_security_headers(app: Flask):
    """添加安全头中间件"""

    @app.after_request
    def set_security_headers(response):
        """TODO: 添加文档字符串"""
        # 防止XSS攻击
        response.headers["X - Content - Type - Options"] = "nosniff"
        response.headers["X - Frame - Options"] = "DENY"
        response.headers["X - XSS - Protection"] = "1; mode = block"

        # HTTPS相关
        response.headers["Strict - Transport - Security"] = (
            "max - age = 31536000; includeSubDomains"
        )

        # 内容安全策略
        response.headers["Content - Security - Policy"] = "default - src 'self'"

        # 隐藏服务器信息
        response.headers.pop("Server", None)

        return response


def rate_limit(max_requests: int = 100, window: int = 3600):
    """速率限制装饰器"""

    def decorator(f):
        """TODO: 添加文档字符串"""

        @wraps(f)
        def decorated_function(*args, **kwargs):
            """TODO: 添加文档字符串"""
            # 实现速率限制逻辑
            client_ip = request.remote_addr
            # 这里应该实现基于Redis的速率限制
            return f(*args, **kwargs)

        return decorated_function

    return decorator
