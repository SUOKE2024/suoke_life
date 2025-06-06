"""
doc_decorators - 索克生活项目模块
"""

from .openapi_generator import (
from collections.abc import Callable
from functools import wraps
from typing import Any
import logging

#!/usr/bin/env python3
"""
API文档装饰器
提供便捷的装饰器来自动生成API文档
"""


    APIParameter,
    APIResponse,
    HTTPMethod,
    ParameterLocation,
    get_openapi_generator,
)

logger = logging.getLogger(__name__)


def api_doc(
    path: str,
    method: str | HTTPMethod = HTTPMethod.GET,
    summary: str = "",
    description: str = "",
    tags: list[str] | None = None,
    generator_name: str = "default",
    deprecated: bool = False,
    operation_id: str | None = None,
):
    """
    API文档装饰器

    Args:
        path: API路径
        method: HTTP方法
        summary: 接口摘要
        description: 接口描述
        tags: 标签列表
        generator_name: 生成器名称
        deprecated: 是否已废弃
        operation_id: 操作ID
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # 获取生成器
        generator = get_openapi_generator(generator_name)
        if not generator:
            logger.warning(f"未找到OpenAPI生成器: {generator_name}")
            return wrapper

        # 转换HTTP方法
        if isinstance(method, str):
            try:
                http_method = HTTPMethod(method.lower())
            except ValueError:
                logger.error(f"不支持的HTTP方法: {method}")
                return wrapper
        else:
            http_method = method

        # 从函数生成端点
        endpoint = generator.from_function(
            func=func,
            path=path,
            method=http_method,
            summary=summary,
            description=description,
            tags=tags or [],
        )

        # 设置额外属性
        endpoint.deprecated = deprecated
        endpoint.operation_id = operation_id

        # 添加到生成器
        generator.add_endpoint(endpoint)

        # 保存端点信息到函数属性
        wrapper._api_endpoint = endpoint
        wrapper._api_generator = generator_name

        return wrapper

    return decorator


def api_parameter(
    name: str,
    location: str | ParameterLocation = ParameterLocation.QUERY,
    description: str = "",
    required: bool = True,
    param_type: str = "string",
    example: Any = None,
    **schema_kwargs,
):
    """
    API参数装饰器

    Args:
        name: 参数名
        location: 参数位置
        description: 参数描述
        required: 是否必需
        param_type: 参数类型
        example: 示例值
        **schema_kwargs: 额外的schema属性
    """

    def decorator(func: Callable) -> Callable:
        # 转换参数位置
        if isinstance(location, str):
            try:
                param_location = ParameterLocation(location.lower())
            except ValueError:
                logger.error(f"不支持的参数位置: {location}")
                return func
        else:
            param_location = location

        # 创建参数对象
        parameter = APIParameter(
            name=name,
            location=param_location,
            description=description,
            required=required,
            schema={"type": param_type, **schema_kwargs},
            example=example,
        )

        # 添加参数到函数的端点
        if hasattr(func, "_api_endpoint"):
            func._api_endpoint.add_parameter(parameter)
        else:
            # 如果还没有端点，先保存参数
            if not hasattr(func, "_api_parameters"):
                func._api_parameters = []
            func._api_parameters.append(parameter)

        return func

    return decorator


def api_response(
    status_code: int,
    description: str = "",
    content_type: str = "application/json",
    schema: dict[str, Any] | None = None,
    example: Any = None,
    headers: dict[str, dict[str, Any]] | None = None,
):
    """
    API响应装饰器

    Args:
        status_code: 状态码
        description: 响应描述
        content_type: 内容类型
        schema: 响应数据模型
        example: 示例响应
        headers: 响应头
    """

    def decorator(func: Callable) -> Callable:
        # 创建响应对象
        response = APIResponse(
            status_code=status_code,
            description=description,
            content_type=content_type,
            schema=schema or {},
            example=example,
            headers=headers or {},
        )

        # 添加响应到函数的端点
        if hasattr(func, "_api_endpoint"):
            func._api_endpoint.add_response(response)
        else:
            # 如果还没有端点，先保存响应
            if not hasattr(func, "_api_responses"):
                func._api_responses = []
            func._api_responses.append(response)

        return func

    return decorator


def api_request_body(
    schema: dict[str, Any],
    description: str = "",
    content_type: str = "application/json",
    required: bool = True,
    example: Any = None,
):
    """
    API请求体装饰器

    Args:
        schema: 请求体数据模型
        description: 请求体描述
        content_type: 内容类型
        required: 是否必需
        example: 示例请求
    """

    def decorator(func: Callable) -> Callable:
        # 设置请求体到函数的端点
        if hasattr(func, "_api_endpoint"):
            func._api_endpoint.set_request_body(
                schema=schema,
                description=description,
                content_type=content_type,
                required=required,
                example=example,
            )
        else:
            # 如果还没有端点，先保存请求体信息
            func._api_request_body = {
                "schema": schema,
                "description": description,
                "content_type": content_type,
                "required": required,
                "example": example,
            }

        return func

    return decorator


def api_security(security_schemes: list[dict[str, list[str]]]):
    """
    API安全装饰器

    Args:
        security_schemes: 安全方案列表
    """

    def decorator(func: Callable) -> Callable:
        # 设置安全方案到函数的端点
        if hasattr(func, "_api_endpoint"):
            func._api_endpoint.security = security_schemes
        else:
            # 如果还没有端点，先保存安全方案
            func._api_security = security_schemes

        return func

    return decorator


def api_tag(name: str, description: str = ""):
    """
    API标签装饰器

    Args:
        name: 标签名
        description: 标签描述
    """

    def decorator(func: Callable) -> Callable:
        # 添加标签到函数的端点
        if hasattr(func, "_api_endpoint"):
            if name not in func._api_endpoint.tags:
                func._api_endpoint.tags.append(name)
        else:
            # 如果还没有端点，先保存标签
            if not hasattr(func, "_api_tags"):
                func._api_tags = []
            if name not in func._api_tags:
                func._api_tags.append(name)

        return func

    return decorator


# 便捷装饰器
def get_api(path: str, **kwargs):
    """GET请求装饰器"""
    return api_doc(path, HTTPMethod.GET, **kwargs)


def post_api(path: str, **kwargs):
    """POST请求装饰器"""
    return api_doc(path, HTTPMethod.POST, **kwargs)


def put_api(path: str, **kwargs):
    """PUT请求装饰器"""
    return api_doc(path, HTTPMethod.PUT, **kwargs)


def delete_api(path: str, **kwargs):
    """DELETE请求装饰器"""
    return api_doc(path, HTTPMethod.DELETE, **kwargs)


def patch_api(path: str, **kwargs):
    """PATCH请求装饰器"""
    return api_doc(path, HTTPMethod.PATCH, **kwargs)


# 常用参数装饰器
def query_param(name: str, description: str = "", required: bool = False, **kwargs):
    """查询参数装饰器"""
    return api_parameter(name, ParameterLocation.QUERY, description, required, **kwargs)


def path_param(name: str, description: str = "", **kwargs):
    """路径参数装饰器"""
    return api_parameter(name, ParameterLocation.PATH, description, True, **kwargs)


def header_param(name: str, description: str = "", required: bool = False, **kwargs):
    """请求头参数装饰器"""
    return api_parameter(
        name, ParameterLocation.HEADER, description, required, **kwargs
    )


# 常用响应装饰器
def success_response(
    description: str = "成功", schema: dict[str, Any] | None = None, **kwargs
):
    """成功响应装饰器"""
    return api_response(200, description, schema=schema, **kwargs)


def created_response(
    description: str = "创建成功", schema: dict[str, Any] | None = None, **kwargs
):
    """创建成功响应装饰器"""
    return api_response(201, description, schema=schema, **kwargs)


def error_response(status_code: int = 400, description: str = "错误", **kwargs):
    """错误响应装饰器"""
    return api_response(status_code, description, **kwargs)


def not_found_response(description: str = "未找到", **kwargs):
    """未找到响应装饰器"""
    return api_response(404, description, **kwargs)


def unauthorized_response(description: str = "未授权", **kwargs):
    """未授权响应装饰器"""
    return api_response(401, description, **kwargs)


# 常用安全装饰器
def bearer_auth():
    """Bearer认证装饰器"""
    return api_security([{"bearerAuth": []}])


def api_key_auth():
    """API Key认证装饰器"""
    return api_security([{"apiKeyAuth": []}])


def no_auth():
    """无需认证装饰器"""
    return api_security([])


# 健康管理平台专用装饰器
def health_api(path: str, **kwargs):
    """健康相关API装饰器"""
    kwargs.setdefault("tags", []).append("健康管理")
    return get_api(path, **kwargs)


def user_api(path: str, **kwargs):
    """用户相关API装饰器"""
    kwargs.setdefault("tags", []).append("用户管理")
    return api_doc(path, **kwargs)


def metric_api(path: str, **kwargs):
    """指标相关API装饰器"""
    kwargs.setdefault("tags", []).append("健康指标")
    return api_doc(path, **kwargs)
