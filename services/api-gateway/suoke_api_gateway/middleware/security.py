"""
security - 索克生活项目模块
"""

from ..core.config import get_settings
from ..core.logging import get_logger
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

"""
安全中间件

添加安全头、防止常见攻击等。
"""



logger = get_logger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """安全中间件"""
    
    def __init__(self, app, settings=None):
        super().__init__(app)
        self.settings = settings or get_settings()
    
    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        # 处理请求
        response = await call_next(request)
        
        # 添加安全头
        self._add_security_headers(response)
        
        return response
    
    def _add_security_headers(self, response: Response) -> None:
        """添加安全响应头"""
        # 防止点击劫持
        response.headers["X-Frame-Options"] = "DENY"
        
        # 防止 MIME 类型嗅探
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # XSS 保护
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # 引用者策略
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # 内容安全策略
        if not self.settings.is_development():
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none';"
            )
        
        # HSTS (仅在 HTTPS 时)
        if not self.settings.is_development():
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )
        
        # 权限策略
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "speaker=()"
        )
        
        # 移除服务器信息
        response.headers.pop("Server", None) 