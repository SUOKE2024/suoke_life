"""
自定义异常类

定义小艾智能体服务的自定义异常
"""


class XiaoaiServiceError(Exception):
    """小艾服务基础异常"""
    pass


class CommunicationError(XiaoaiServiceError):
    """通信错误"""
    pass


class ServiceUnavailableError(XiaoaiServiceError):
    """服务不可用错误"""
    pass


class ConfigurationError(XiaoaiServiceError):
    """配置错误"""
    pass


class ValidationError(XiaoaiServiceError):
    """验证错误"""
    pass


class TimeoutError(XiaoaiServiceError):
    """超时错误"""
    pass


class AuthenticationError(XiaoaiServiceError):
    """认证错误"""
    pass


class AuthorizationError(XiaoaiServiceError):
    """授权错误"""
    pass


class DiagnosisError(XiaoaiServiceError):
    """诊断错误"""
    pass


class ModelError(XiaoaiServiceError):
    """模型相关错误"""
    pass


class ModelNotFoundError(ModelError):
    """模型未找到错误"""
    pass


class ProcessingError(XiaoaiServiceError):
    """数据处理错误"""
    pass


class UnsupportedFormatError(ProcessingError):
    """不支持的格式错误"""
    pass


class MonitoringError(XiaoaiServiceError):
    """监控相关错误"""
    pass


class AccessibilityError(XiaoaiServiceError):
    """无障碍服务错误"""
    pass


class HealthCheckError(XiaoaiServiceError):
    """健康检查错误"""
    pass