"""
__init__ - 索克生活项目模块
"""

from .doc_decorators import api_doc, api_parameter, api_response
from .openapi_generator import (
from .swagger_ui import SwaggerUIServer

#!/usr/bin/env python3
"""
API文档生成模块
提供自动生成OpenAPI/Swagger文档的功能
"""

    APIEndpoint,
    APIParameter,
    APIResponse,
    APISchema,
    OpenAPIGenerator,
    get_openapi_generator,
)

__all__ = [
    "APIEndpoint",
    "APIParameter",
    "APIResponse",
    "APISchema",
    # 核心类
    "OpenAPIGenerator",
    # UI服务器
    "SwaggerUIServer",
    # 装饰器
    "api_doc",
    "api_parameter",
    "api_response",
    "get_openapi_generator",
]
