"""
security - 索克生活项目模块
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import structlog

"""安全中间件"""



logger = structlog.get_logger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    """安全中间件"""

    async def dispatch(self, request: Request, call_next: Callable) - > Response:
        """处理安全相关功能"""

        # 处理请求
        response = await call_next(request)

        # 添加安全头部
        self._add_security_headers(response)

        return response

    def _add_security_headers(self, response: Response) - > None:
        """添加安全头部"""

        # 防止点击劫持
        response.headers["X - Frame - Options"] = "DENY"

        # 防止MIME类型嗅探
        response.headers["X - Content - Type - Options"] = "nosniff"

        # XSS保护
        response.headers["X - XSS - Protection"] = "1; mode = block"

        # 引用者策略
        response.headers["Referrer - Policy"] = "strict - origin - when - cross - origin"

        # 内容安全策略
        response.headers["Content - Security - Policy"] = (
            "default - src 'self'; "
            "script - src 'self' 'unsafe - inline'; "
            "style - src 'self' 'unsafe - inline'; "
            "img - src 'self' data: https:; "
            "font - src 'self'; "
            "connect - src 'self'; "
            "frame - ancestors 'none';"
        )

        # 严格传输安全（仅HTTPS）
        if hasattr(response, 'url') and response.url and response.url.startswith('https'):
            response.headers["Strict - Transport - Security"] = (
                "max - age = 31536000; includeSubDomains; preload"
            )

        # 权限策略
        response.headers["Permissions - Policy"] = (
            "geolocation = (), "
            "microphone = (), "
            "camera = (), "
            "payment = (), "
            "usb = (), "
            "magnetometer = (), "
            "gyroscope = (), "
            "speaker = ()"
        )