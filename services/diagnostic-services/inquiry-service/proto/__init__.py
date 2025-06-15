"""
Proto模块 - gRPC协议缓冲区定义
"""

from .inquiry_service_pb2 import *
from .inquiry_service_pb2_grpc import *

__all__ = [
    "inquiry_service_pb2",
    "inquiry_service_pb2_grpc",
] 