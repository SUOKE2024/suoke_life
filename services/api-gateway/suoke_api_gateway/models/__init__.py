"""数据模型模块"""

from .gateway import GatewayRequest, GatewayResponse
from .service import ServiceInfo, ServiceStatus

__all__ = [
    "GatewayRequest",
    "GatewayResponse", 
    "ServiceInfo",
    "ServiceStatus",
] 