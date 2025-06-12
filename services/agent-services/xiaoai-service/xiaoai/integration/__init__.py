"""
外部服务集成模块

提供与所有外部诊断服务的统一集成接口
"""

from .base import BaseServiceClient, ServiceEndpoint

# 导入管理器和基础类
from .manager import ServiceClientManager


# 导入各服务客户端 (延迟导入以避免循环依赖)
def _get_look_client():
    from .look.client import LookServiceClient

    return LookServiceClient


def _get_listen_client():
    from .listen.client import ListenServiceClient

    return ListenServiceClient


def _get_inquiry_client():
    from .inquiry.client import InquiryServiceClient

    return InquiryServiceClient


def _get_palpation_client():
    from .palpation.client import PalpationServiceClient

    return PalpationServiceClient


def _get_calculation_client():
    from .calculation.client import CalculationServiceClient

    return CalculationServiceClient


# 为了向后兼容，提供直接导入（延迟导入）
def __getattr__(name):
    if name == "LookServiceClient":
        return _get_look_client()
    elif name == "ListenServiceClient":
        return _get_listen_client()
    elif name == "InquiryServiceClient":
        return _get_inquiry_client()
    elif name == "PalpationServiceClient":
        return _get_palpation_client()
    elif name == "CalculationServiceClient":
        return _get_calculation_client()
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    # 管理器和基础类
    "ServiceClientManager",
    "BaseServiceClient",
    "ServiceEndpoint",
    # 服务客户端
    "LookServiceClient",
    "ListenServiceClient",
    "InquiryServiceClient",
    "PalpationServiceClient",
    "CalculationServiceClient",
]
