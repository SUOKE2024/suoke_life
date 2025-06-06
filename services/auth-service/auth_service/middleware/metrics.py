"""
metrics - 索克生活项目模块
"""

from fastapi import Request, Response
from prometheus_client import Counter, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import structlog
import time

"""指标中间件"""



logger = structlog.get_logger(__name__)

# Prometheus指标
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

REQUEST_SIZE = Histogram(
    'http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint']
)

RESPONSE_SIZE = Histogram(
    'http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint']
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """指标中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """收集请求指标"""
        
        # 记录开始时间
        start_time = time.time()
        
        # 获取请求信息
        method = request.method
        endpoint = self._get_endpoint(request)
        
        # 获取请求大小
        request_size = self._get_request_size(request)
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算处理时间
            duration = time.time() - start_time
            
            # 获取响应信息
            status_code = str(response.status_code)
            response_size = self._get_response_size(response)
            
            # 记录指标
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()
            
            REQUEST_DURATION.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            REQUEST_SIZE.labels(
                method=method,
                endpoint=endpoint
            ).observe(request_size)
            
            RESPONSE_SIZE.labels(
                method=method,
                endpoint=endpoint
            ).observe(response_size)
            
            return response
            
        except Exception as e:
            # 计算处理时间
            duration = time.time() - start_time
            
            # 记录错误指标
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status_code="500"
            ).inc()
            
            REQUEST_DURATION.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            raise
    
    def _get_endpoint(self, request: Request) -> str:
        """获取端点路径"""
        # 获取路由模式而不是实际路径
        if hasattr(request, 'scope') and 'route' in request.scope:
            route = request.scope['route']
            if hasattr(route, 'path'):
                return route.path
        
        # 回退到URL路径
        return request.url.path
    
    def _get_request_size(self, request: Request) -> int:
        """获取请求大小"""
        content_length = request.headers.get('content-length')
        if content_length:
            try:
                return int(content_length)
            except ValueError:
                pass
        return 0
    
    def _get_response_size(self, response: Response) -> int:
        """获取响应大小"""
        content_length = response.headers.get('content-length')
        if content_length:
            try:
                return int(content_length)
            except ValueError:
                pass
        
        # 如果没有content-length头，尝试从body获取
        if hasattr(response, 'body') and response.body:
            return len(response.body)
        
        return 0


def get_metrics() -> str:
    """获取Prometheus指标"""
    return generate_latest() 