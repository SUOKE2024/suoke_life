"""
openapi_generator - 索克生活项目模块
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import inspect
import json
import logging
import yaml

#! / usr / bin / env python3
"""
OpenAPI文档生成器
自动生成OpenAPI 3.0规范的API文档
"""



logger = logging.getLogger(__name__)


class ParameterLocation(Enum):
    """参数位置"""

    QUERY = "query"
    PATH = "path"
    HEADER = "header"
    COOKIE = "cookie"


class HTTPMethod(Enum):
    """HTTP方法"""

    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"
    PATCH = "patch"
    HEAD = "head"
    OPTIONS = "options"


@dataclass
class APIParameter:
    """API参数"""

    name: str
    location: ParameterLocation
    description: str = ""
    required: bool = True
    schema: dict[str, Any] = field(default_factory = dict)
    example: Any = None

    def to_openapi(self) -> dict[str, Any]:
        """转换为OpenAPI格式"""
        param = {
            "name": self.name,
            "in": self.location.value,
            "description": self.description,
            "required": self.required,
            "schema": self.schema,
        }

        if self.example is not None:
            param["example"] = self.example

        return param


@dataclass
class APIResponse:
    """API响应"""

    status_code: int
    description: str = ""
    content_type: str = "application / json"
    schema: dict[str, Any] = field(default_factory = dict)
    example: Any = None
    headers: dict[str, dict[str, Any]] = field(default_factory = dict)

    def to_openapi(self) -> dict[str, Any]:
        """转换为OpenAPI格式"""
        response = {"description": self.description}

        if self.schema:
            response["content"] = {self.content_type: {"schema": self.schema}}

            if self.example is not None:
                response["content"][self.content_type]["example"] = self.example

        if self.headers:
            response["headers"] = self.headers

        return response


@dataclass
class APISchema:
    """API数据模型"""

    name: str
    type: str = "object"
    properties: dict[str, dict[str, Any]] = field(default_factory = dict)
    required: list[str] = field(default_factory = list)
    description: str = ""
    example: Any = None

    def add_property(
        self,
        name: str,
        prop_type: str,
        description: str = "",
        required: bool = False,
        example: Any = None,
        **kwargs,
    ):
        """添加属性"""
        prop = {"type": prop_type, "description": description, **kwargs}

        if example is not None:
            prop["example"] = example

        self.properties[name] = prop

        if required:
            self.required.append(name)

    def to_openapi(self) -> dict[str, Any]:
        """转换为OpenAPI格式"""
        schema = {
            "type": self.type,
            "description": self.description,
            "properties": self.properties,
        }

        if self.required:
            schema["required"] = self.required

        if self.example is not None:
            schema["example"] = self.example

        return schema


@dataclass
class APIEndpoint:
    """API端点"""

    path: str
    method: HTTPMethod
    summary: str = ""
    description: str = ""
    tags: list[str] = field(default_factory = list)
    parameters: list[APIParameter] = field(default_factory = list)
    request_body: dict[str, Any] | None = None
    responses: dict[int, APIResponse] = field(default_factory = dict)
    security: list[dict[str, list[str]]] = field(default_factory = list)
    deprecated: bool = False
    operation_id: str | None = None

    def add_parameter(self, parameter: APIParameter):
        """添加参数"""
        self.parameters.append(parameter)

    def add_response(self, response: APIResponse):
        """添加响应"""
        self.responses[response.status_code] = response

    def set_request_body(
        self,
        schema: dict[str, Any],
        description: str = "",
        content_type: str = "application / json",
        required: bool = True,
        example: Any = None,
    ):
        """设置请求体"""
        content = {content_type: {"schema": schema}}

        if example is not None:
            content[content_type]["example"] = example

        self.request_body = {
            "description": description,
            "required": required,
            "content": content,
        }

    def to_openapi(self) -> dict[str, Any]:
        """转换为OpenAPI格式"""
        operation = {
            "summary": self.summary,
            "description": self.description,
            "tags": self.tags,
            "parameters": [param.to_openapi() for param in self.parameters],
            "responses": {
                str(code): response.to_openapi()
                for code, response in self.responses.items()
            },
        }

        if self.request_body:
            operation["requestBody"] = self.request_body

        if self.security:
            operation["security"] = self.security

        if self.deprecated:
            operation["deprecated"] = True

        if self.operation_id:
            operation["operationId"] = self.operation_id

        return operation


class OpenAPIGenerator:
    """OpenAPI文档生成器"""

    def __init__(
        self,
        title: str = "API文档",
        version: str = "1.0.0",
        description: str = "",
        base_url: str = "http: / /localhost:8000",
    ):
        self.title = title
        self.version = version
        self.description = description
        self.base_url = base_url

        self.endpoints: list[APIEndpoint] = []
        self.schemas: dict[str, APISchema] = {}
        self.security_schemes: dict[str, dict[str, Any]] = {}
        self.tags: list[dict[str, str]] = []

    def add_endpoint(self, endpoint: APIEndpoint):
        """添加API端点"""
        self.endpoints.append(endpoint)
        logger.info(f"添加API端点: {endpoint.method.value.upper()} {endpoint.path}")

    def add_schema(self, schema: APISchema):
        """添加数据模型"""
        self.schemas[schema.name] = schema
        logger.info(f"添加数据模型: {schema.name}")

    def add_security_scheme(
        self, name: str, scheme_type: str, description: str = "", **kwargs
    ):
        """添加安全方案"""
        scheme = {"type": scheme_type, "description": description, **kwargs}

        self.security_schemes[name] = scheme
        logger.info(f"添加安全方案: {name}")

    def add_tag(self, name: str, description: str = ""):
        """添加标签"""
        self.tags.append({"name": name, "description": description})

    def add_bearer_auth(
        self, name: str = "bearerAuth", description: str = "JWT Bearer Token"
    ):
        """添加Bearer认证"""
        self.add_security_scheme(
            name = name,
            scheme_type = "http",
            scheme = "bearer",
            bearer_format = "JWT",
            description = description,
        )

    def add_api_key_auth(
        self,
        name: str = "apiKeyAuth",
        location: str = "header",
        key_name: str = "X - API - Key",
        description: str = "API Key认证",
    ):
        """添加API Key认证"""
        # 直接构建 API Key 安全方案
        scheme = {
            "type": "apiKey",
            "in": location,
            "name": key_name,
            "description": description,
        }

        self.security_schemes[name] = scheme
        logger.info(f"添加安全方案: {name}")

    def generate_openapi_spec(self) -> dict[str, Any]:
        """生成OpenAPI规范"""
        # 基本信息
        spec = {
            "openapi": "3.0.3",
            "info": {
                "title": self.title,
                "version": self.version,
                "description": self.description,
            },
            "servers": [{"url": self.base_url, "description": "API服务器"}],
        }

        # 标签
        if self.tags:
            spec["tags"] = self.tags

        # 路径
        paths = {}
        for endpoint in self.endpoints:
            if endpoint.path not in paths:
                paths[endpoint.path] = {}

            paths[endpoint.path][endpoint.method.value] = endpoint.to_openapi()

        spec["paths"] = paths

        # 组件
        components = {}

        # 数据模型
        if self.schemas:
            components["schemas"] = {
                name: schema.to_openapi() for name, schema in self.schemas.items()
            }

        # 安全方案
        if self.security_schemes:
            components["securitySchemes"] = self.security_schemes

        if components:
            spec["components"] = components

        return spec

    def generate_json(self, indent: int = 2) -> str:
        """生成JSON格式的文档"""
        spec = self.generate_openapi_spec()
        return json.dumps(spec, indent = indent, ensure_ascii = False)

    def generate_yaml(self) -> str:
        """生成YAML格式的文档"""
        spec = self.generate_openapi_spec()
        return yaml.dump(spec, default_flow_style = False, allow_unicode = True)

    def save_to_file(self, file_path: str, format: str = "json"):
        """保存到文件"""
        if format.lower() == "json":
            content = self.generate_json()
        elif format.lower() == "yaml":
            content = self.generate_yaml()
        else:
            raise ValueError("格式必须是 'json' 或 'yaml'")

        with open(file_path, "w", encoding = "utf - 8") as f:
            f.write(content)

        logger.info(f"API文档已保存到: {file_path}")

    def from_function(
        self,
        func: callable,
        path: str,
        method: HTTPMethod,
        summary: str = "",
        description: str = "",
        tags: list[str] | None = None,
    ) -> APIEndpoint:
        """从函数自动生成API端点"""
        if not summary:
            summary = func.__name__.replace("_", " ").title()

        if not description and func.__doc__:
            description = func.__doc__.strip()

        endpoint = APIEndpoint(
            path = path,
            method = method,
            summary = summary,
            description = description,
            tags = tags or [],
        )

        # 分析函数签名
        sig = inspect.signature(func)
        for param_name, param in sig.parameters.items():
            if param_name in ["self", "cls", "request", "response"]:
                continue

            # 确定参数类型
            param_type = "string"
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"

            # 确定参数位置
            location = ParameterLocation.QUERY
            if f"{{{param_name}}}" in path:
                location = ParameterLocation.PATH

            api_param = APIParameter(
                name = param_name,
                location = location,
                required = param.default == inspect.Parameter.empty,
                schema = {"type": param_type},
            )

            endpoint.add_parameter(api_param)

        # 添加默认响应
        endpoint.add_response(APIResponse(status_code = 200, description = "成功响应"))

        return endpoint

    def create_health_check_schema(self) -> APISchema:
        """创建健康检查数据模型（索克生活平台专用）"""
        schema = APISchema(name = "HealthCheck", description = "健康检查响应")

        schema.add_property("status", "string", "服务状态", True, "healthy")
        schema.add_property(
            "timestamp", "string", "检查时间", True, "2024 - 12 - 01T10:00:00Z"
        )
        schema.add_property("version", "string", "服务版本", True, "1.0.0")
        schema.add_property("uptime", "integer", "运行时间（秒）", True, 3600)

        return schema

    def create_user_schema(self) -> APISchema:
        """创建用户数据模型（索克生活平台专用）"""
        schema = APISchema(name = "User", description = "用户信息")

        schema.add_property("user_id", "string", "用户ID", True, "user123")
        schema.add_property("name", "string", "用户姓名", True, "张三")
        schema.add_property("age", "integer", "年龄", False, 30)
        schema.add_property("gender", "string", "性别", False, "male")
        schema.add_property("phone", "string", "手机号", False, "13800138000")
        schema.add_property("email", "string", "邮箱", False, "user@example.com")

        return schema

    def create_health_metric_schema(self) -> APISchema:
        """创建健康指标数据模型（索克生活平台专用）"""
        schema = APISchema(name = "HealthMetric", description = "健康指标")

        schema.add_property("metric_id", "string", "指标ID", True, "metric123")
        schema.add_property("user_id", "string", "用户ID", True, "user123")
        schema.add_property("metric_type", "string", "指标类型", True, "heart_rate")
        schema.add_property("value", "number", "指标值", True, 72.5)
        schema.add_property("unit", "string", "单位", True, "bpm")
        schema.add_property(
            "timestamp", "string", "测量时间", True, "2024 - 12 - 01T10:00:00Z"
        )
        schema.add_property("device_id", "string", "设备ID", False, "device123")

        return schema


# 全局OpenAPI生成器注册表
_generators: dict[str, OpenAPIGenerator] = {}


def register_openapi_generator(name: str, generator: OpenAPIGenerator):
    """注册OpenAPI生成器"""
    _generators[name] = generator
    logger.info(f"注册OpenAPI生成器: {name}")


def get_openapi_generator(name: str) -> OpenAPIGenerator | None:
    """获取OpenAPI生成器"""
    return _generators.get(name)


def create_default_generator(service_name: str) -> OpenAPIGenerator:
    """创建默认的OpenAPI生成器"""
    generator = OpenAPIGenerator(
        title = f"{service_name} API",
        version = "1.0.0",
        description = f"{service_name}服务API文档",
    )

    # 添加常用的安全方案
    generator.add_bearer_auth()
    generator.add_api_key_auth()

    # 添加常用的数据模型
    generator.add_schema(generator.create_health_check_schema())
    generator.add_schema(generator.create_user_schema())
    generator.add_schema(generator.create_health_metric_schema())

    # 注册生成器
    register_openapi_generator(service_name, generator)

    return generator
