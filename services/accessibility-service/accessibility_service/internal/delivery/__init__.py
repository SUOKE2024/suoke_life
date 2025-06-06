"""
__init__ - 索克生活项目模块
"""

from .grpc_server import AccessibilityServicer

"""
API交付层

负责处理外部请求和响应：
- grpc: gRPC服务实现
- http: HTTP API实现
- websocket: WebSocket实时通信
"""


__all__ = [
    "AccessibilityServicer"
]
