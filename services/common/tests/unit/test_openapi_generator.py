"""
test_openapi_generator - 索克生活项目模块
"""

from suoke_common.api_docs.openapi_generator import (
from unittest.mock import mock_open, patch
import json
import pytest

#!/usr/bin/env python3
"""
测试 OpenAPI 生成器功能
"""



    APIEndpoint,
    APIParameter,
    APIResponse,
    APISchema,
    HTTPMethod,
    OpenAPIGenerator,
    ParameterLocation,
    create_default_generator,
    get_openapi_generator,
    register_openapi_generator,
)


class TestOpenAPIGenerator:
    """测试 OpenAPI 生成器"""

    def test_generator_creation(self):
        """测试生成器创建"""
        generator = OpenAPIGenerator(
            title="Test API",
            version="1.0.0",
            description="Test API Description",
            base_url="http://test.com",
        )

        assert generator.title == "Test API"
        assert generator.version == "1.0.0"
        assert generator.description == "Test API Description"
        assert generator.base_url == "http://test.com"
        assert generator.endpoints == []
        assert generator.schemas == {}
        assert generator.security_schemes == {}
        assert generator.tags == []

    def test_add_endpoint(self):
        """测试添加端点"""
        generator = OpenAPIGenerator()
        endpoint = APIEndpoint(
            path="/test", method=HTTPMethod.GET, summary="Test endpoint"
        )

        generator.add_endpoint(endpoint)
        assert len(generator.endpoints) == 1
        assert generator.endpoints[0] == endpoint

    def test_add_schema(self):
        """测试添加数据模型"""
        generator = OpenAPIGenerator()
        schema = APISchema(name="TestModel", description="Test model")

        generator.add_schema(schema)
        assert "TestModel" in generator.schemas
        assert generator.schemas["TestModel"] == schema

    def test_add_security_scheme(self):
        """测试添加安全方案"""
        generator = OpenAPIGenerator()

        generator.add_security_scheme(
            name="bearerAuth", scheme_type="http", scheme="bearer", bearer_format="JWT"
        )

        assert "bearerAuth" in generator.security_schemes
        scheme = generator.security_schemes["bearerAuth"]
        assert scheme["type"] == "http"
        assert scheme["scheme"] == "bearer"
        assert scheme["bearer_format"] == "JWT"

    def test_add_tag(self):
        """测试添加标签"""
        generator = OpenAPIGenerator()

        generator.add_tag("test", "Test tag")

        assert len(generator.tags) == 1
        assert generator.tags[0]["name"] == "test"
        assert generator.tags[0]["description"] == "Test tag"

    def test_add_bearer_auth(self):
        """测试添加 Bearer 认证"""
        generator = OpenAPIGenerator()

        generator.add_bearer_auth()

        assert "bearerAuth" in generator.security_schemes
        scheme = generator.security_schemes["bearerAuth"]
        assert scheme["type"] == "http"
        assert scheme["scheme"] == "bearer"

    def test_add_api_key_auth(self):
        """测试添加 API Key 认证"""
        generator = OpenAPIGenerator()

        generator.add_api_key_auth()

        assert "apiKeyAuth" in generator.security_schemes
        scheme = generator.security_schemes["apiKeyAuth"]
        assert scheme["type"] == "apiKey"
        assert scheme["in"] == "header"
        assert scheme["name"] == "X-API-Key"

    def test_generate_openapi_spec(self):
        """测试生成 OpenAPI 规范"""
        generator = OpenAPIGenerator(
            title="Test API", version="1.0.0", description="Test Description"
        )

        # 添加一个简单的端点
        endpoint = APIEndpoint(
            path="/test", method=HTTPMethod.GET, summary="Test endpoint"
        )
        endpoint.add_response(APIResponse(status_code=200, description="Success"))
        generator.add_endpoint(endpoint)

        spec = generator.generate_openapi_spec()

        assert spec["openapi"] == "3.0.3"
        assert spec["info"]["title"] == "Test API"
        assert spec["info"]["version"] == "1.0.0"
        assert spec["info"]["description"] == "Test Description"
        assert "/test" in spec["paths"]
        assert "get" in spec["paths"]["/test"]

    def test_generate_json(self):
        """测试生成 JSON 格式文档"""
        generator = OpenAPIGenerator(title="Test API")

        json_str = generator.generate_json()

        # 验证是有效的 JSON
        spec = json.loads(json_str)
        assert spec["info"]["title"] == "Test API"

    def test_generate_yaml(self):
        """测试生成 YAML 格式文档"""
        generator = OpenAPIGenerator(title="Test API")

        yaml_str = generator.generate_yaml()

        # 验证包含预期内容
        assert "title: Test API" in yaml_str
        assert "openapi: 3.0.3" in yaml_str

    def test_save_to_file_json(self):
        """测试保存 JSON 文件"""
        generator = OpenAPIGenerator(title="Test API")

        with patch("builtins.open", mock_open()) as mock_file:
            generator.save_to_file("/tmp/test.json", "json")

            mock_file.assert_called_once_with("/tmp/test.json", "w", encoding="utf-8")
            handle = mock_file()
            handle.write.assert_called_once()

    def test_save_to_file_yaml(self):
        """测试保存 YAML 文件"""
        generator = OpenAPIGenerator(title="Test API")

        with patch("builtins.open", mock_open()) as mock_file:
            generator.save_to_file("/tmp/test.yaml", "yaml")

            mock_file.assert_called_once_with("/tmp/test.yaml", "w", encoding="utf-8")
            handle = mock_file()
            handle.write.assert_called_once()

    def test_save_to_file_invalid_format(self):
        """测试保存无效格式文件"""
        generator = OpenAPIGenerator()

        with pytest.raises(ValueError, match="格式必须是 'json' 或 'yaml'"):
            generator.save_to_file("/tmp/test.txt", "txt")

    def test_create_health_check_schema(self):
        """测试创建健康检查数据模型"""
        generator = OpenAPIGenerator()

        schema = generator.create_health_check_schema()

        assert schema.name == "HealthCheck"
        assert schema.description == "健康检查响应"
        assert "status" in schema.properties
        assert "timestamp" in schema.properties
        assert "version" in schema.properties
        assert "uptime" in schema.properties

    def test_create_user_schema(self):
        """测试创建用户数据模型"""
        generator = OpenAPIGenerator()

        schema = generator.create_user_schema()

        assert schema.name == "User"
        assert schema.description == "用户信息"
        assert "user_id" in schema.properties
        assert "name" in schema.properties
        assert "age" in schema.properties

    def test_create_health_metric_schema(self):
        """测试创建健康指标数据模型"""
        generator = OpenAPIGenerator()

        schema = generator.create_health_metric_schema()

        assert schema.name == "HealthMetric"
        assert schema.description == "健康指标"
        assert "metric_id" in schema.properties
        assert "user_id" in schema.properties
        assert "metric_type" in schema.properties


class TestAPIParameter:
    """测试 API 参数"""

    def test_parameter_creation(self):
        """测试参数创建"""
        param = APIParameter(
            name="test_param",
            location=ParameterLocation.QUERY,
            description="Test parameter",
            required=True,
            schema={"type": "string"},
            example="test_value",
        )

        assert param.name == "test_param"
        assert param.location == ParameterLocation.QUERY
        assert param.description == "Test parameter"
        assert param.required is True
        assert param.schema == {"type": "string"}
        assert param.example == "test_value"

    def test_parameter_to_openapi(self):
        """测试参数转换为 OpenAPI 格式"""
        param = APIParameter(
            name="test_param",
            location=ParameterLocation.QUERY,
            description="Test parameter",
            required=True,
            schema={"type": "string"},
            example="test_value",
        )

        openapi_param = param.to_openapi()

        assert openapi_param["name"] == "test_param"
        assert openapi_param["in"] == "query"
        assert openapi_param["description"] == "Test parameter"
        assert openapi_param["required"] is True
        assert openapi_param["schema"] == {"type": "string"}
        assert openapi_param["example"] == "test_value"


class TestAPIResponse:
    """测试 API 响应"""

    def test_response_creation(self):
        """测试响应创建"""
        response = APIResponse(
            status_code=200,
            description="Success",
            content_type="application/json",
            schema={"type": "object"},
            example={"message": "success"},
        )

        assert response.status_code == 200
        assert response.description == "Success"
        assert response.content_type == "application/json"
        assert response.schema == {"type": "object"}
        assert response.example == {"message": "success"}

    def test_response_to_openapi(self):
        """测试响应转换为 OpenAPI 格式"""
        response = APIResponse(
            status_code=200,
            description="Success",
            schema={"type": "object"},
            example={"message": "success"},
        )

        openapi_response = response.to_openapi()

        assert openapi_response["description"] == "Success"
        assert "content" in openapi_response
        assert "application/json" in openapi_response["content"]
        assert openapi_response["content"]["application/json"]["schema"] == {
            "type": "object"
        }
        assert openapi_response["content"]["application/json"]["example"] == {
            "message": "success"
        }


class TestAPISchema:
    """测试 API 数据模型"""

    def test_schema_creation(self):
        """测试数据模型创建"""
        schema = APISchema(name="TestModel", type="object", description="Test model")

        assert schema.name == "TestModel"
        assert schema.type == "object"
        assert schema.description == "Test model"
        assert schema.properties == {}
        assert schema.required == []

    def test_add_property(self):
        """测试添加属性"""
        schema = APISchema(name="TestModel")

        schema.add_property(
            name="test_field",
            prop_type="string",
            description="Test field",
            required=True,
            example="test_value",
        )

        assert "test_field" in schema.properties
        assert schema.properties["test_field"]["type"] == "string"
        assert schema.properties["test_field"]["description"] == "Test field"
        assert schema.properties["test_field"]["example"] == "test_value"
        assert "test_field" in schema.required

    def test_schema_to_openapi(self):
        """测试数据模型转换为 OpenAPI 格式"""
        schema = APISchema(name="TestModel", description="Test model")
        schema.add_property("field1", "string", "Field 1", True)
        schema.add_property("field2", "integer", "Field 2", False)

        openapi_schema = schema.to_openapi()

        assert openapi_schema["type"] == "object"
        assert openapi_schema["description"] == "Test model"
        assert "field1" in openapi_schema["properties"]
        assert "field2" in openapi_schema["properties"]
        assert openapi_schema["required"] == ["field1"]


class TestGlobalFunctions:
    """测试全局函数"""

    def test_register_and_get_generator(self):
        """测试注册和获取生成器"""
        generator = OpenAPIGenerator(title="Test API")

        register_openapi_generator("test", generator)
        retrieved = get_openapi_generator("test")

        assert retrieved is generator

    def test_get_nonexistent_generator(self):
        """测试获取不存在的生成器"""
        result = get_openapi_generator("nonexistent")
        assert result is None

    def test_create_default_generator(self):
        """测试创建默认生成器"""
        generator = create_default_generator("TestService")

        assert generator.title == "TestService API"
        assert generator.version == "1.0.0"
        assert generator.description == "TestService服务API文档"

        # 验证默认安全方案
        assert "bearerAuth" in generator.security_schemes
        assert "apiKeyAuth" in generator.security_schemes

        # 验证默认数据模型
        assert "HealthCheck" in generator.schemas
        assert "User" in generator.schemas
        assert "HealthMetric" in generator.schemas

        # 验证已注册
        retrieved = get_openapi_generator("TestService")
        assert retrieved is generator
