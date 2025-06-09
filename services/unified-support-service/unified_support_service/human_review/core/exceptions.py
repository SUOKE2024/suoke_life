from typing import Dict, List, Any, Optional, Union

"""
自定义异常类
Custom Exception Classes

定义人工审核服务的自定义异常
"""


class HumanReviewServiceError(Exception):
    """人工审核服务基础异常"""

    pass


class DatabaseError(HumanReviewServiceError):
    """数据库相关异常"""

    pass


class ReviewTaskError(HumanReviewServiceError):
    """审核任务相关异常"""

    pass


class ReviewerError(HumanReviewServiceError):
    """审核员相关异常"""

    pass


class ValidationError(HumanReviewServiceError):
    """数据验证异常"""

    pass


class AuthenticationError(HumanReviewServiceError):
    """认证异常"""

    pass


class AuthorizationError(HumanReviewServiceError):
    """授权异常"""

    pass


class ConfigurationError(HumanReviewServiceError):
    """配置异常"""

    pass


class ExternalServiceError(HumanReviewServiceError):
    """外部服务异常"""

    pass
