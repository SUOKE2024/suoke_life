"""
接口层

提供gRPC和REST API接口，处理外部请求和响应。
"""

from .grpc_server import ListenServiceGRPCServer
from .rest_api import create_rest_app

__all__ = [
    "ListenServiceGRPCServer",
    "create_rest_app",
]
