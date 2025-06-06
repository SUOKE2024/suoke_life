"""
__init__ - 索克生活项目模块
"""

from .grpc_server import ListenServiceGRPCServer
from .rest_api import create_rest_app

"""
接口层

提供gRPC和REST API接口，处理外部请求和响应。
"""


__all__ = [
    "ListenServiceGRPCServer",
    "create_rest_app",
]
