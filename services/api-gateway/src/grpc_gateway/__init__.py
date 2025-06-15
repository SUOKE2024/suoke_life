"""
gRPC网关模块

提供gRPC服务的HTTP/REST代理功能，支持：
- gRPC到HTTP的协议转换
- 服务发现和负载均衡
- 流式处理和双向通信
- 错误处理和重试机制
"""

from .client import GrpcClient, GrpcClientPool
from .server import GrpcGatewayServer
from .proxy import GrpcHttpProxy
from .transcoder import GrpcTranscoder
from .reflection import GrpcReflectionClient

__all__ = [
    "GrpcClient",
    "GrpcClientPool", 
    "GrpcGatewayServer",
    "GrpcHttpProxy",
    "GrpcTranscoder",
    "GrpcReflectionClient",
]

__version__ = "1.0.0"