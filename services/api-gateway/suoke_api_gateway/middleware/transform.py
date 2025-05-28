#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
请求/响应转换中间件

支持数据格式转换、字段映射、数据验证、内容压缩等功能。
"""

import json
import gzip
import zlib
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Union
from enum import Enum

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response as StarletteResponse
from pydantic import BaseModel, ValidationError

from ..core.logging import get_logger

logger = get_logger(__name__)


class TransformType(Enum):
    """转换类型"""
    REQUEST = "request"
    RESPONSE = "response"
    BOTH = "both"


class ContentType(Enum):
    """内容类型"""
    JSON = "application/json"
    XML = "application/xml"
    FORM = "application/x-www-form-urlencoded"
    TEXT = "text/plain"
    BINARY = "application/octet-stream"


class Transformer(ABC):
    """转换器基类"""
    
    @abstractmethod
    async def transform_request(self, request: Request, body: bytes) -> bytes:
        """转换请求"""
        pass
    
    @abstractmethod
    async def transform_response(self, response: Response, body: bytes) -> bytes:
        """转换响应"""
        pass
    
    def should_transform_request(self, request: Request) -> bool:
        """判断是否应该转换请求"""
        return True
    
    def should_transform_response(self, request: Request, response: Response) -> bool:
        """判断是否应该转换响应"""
        return True


class JSONFieldMapper(Transformer):
    """JSON 字段映射转换器"""
    
    def __init__(
        self,
        request_mapping: Optional[Dict[str, str]] = None,
        response_mapping: Optional[Dict[str, str]] = None,
        remove_null_fields: bool = False,
        case_conversion: Optional[str] = None,  # 'snake_case', 'camelCase', 'PascalCase'
    ):
        self.request_mapping = request_mapping or {}
        self.response_mapping = response_mapping or {}
        self.remove_null_fields = remove_null_fields
        self.case_conversion = case_conversion
    
    async def transform_request(self, request: Request, body: bytes) -> bytes:
        """转换请求"""
        if not body or not self._is_json_content(request):
            return body
        
        try:
            data = json.loads(body.decode('utf-8'))
            transformed_data = self._transform_data(data, self.request_mapping, True)
            return json.dumps(transformed_data).encode('utf-8')
        except Exception as e:
            logger.warning("Failed to transform request JSON", error=str(e))
            return body
    
    async def transform_response(self, response: Response, body: bytes) -> bytes:
        """转换响应"""
        if not body or not self._is_json_response(response):
            return body
        
        try:
            data = json.loads(body.decode('utf-8'))
            transformed_data = self._transform_data(data, self.response_mapping, False)
            return json.dumps(transformed_data).encode('utf-8')
        except Exception as e:
            logger.warning("Failed to transform response JSON", error=str(e))
            return body
    
    def _transform_data(self, data: Any, mapping: Dict[str, str], is_request: bool) -> Any:
        """转换数据"""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                # 字段映射
                new_key = mapping.get(key, key)
                
                # 大小写转换
                if self.case_conversion:
                    new_key = self._convert_case(new_key, self.case_conversion)
                
                # 递归转换嵌套对象
                new_value = self._transform_data(value, mapping, is_request)
                
                # 移除空值字段
                if self.remove_null_fields and new_value is None:
                    continue
                
                result[new_key] = new_value
            
            return result
        
        elif isinstance(data, list):
            return [self._transform_data(item, mapping, is_request) for item in data]
        
        else:
            return data
    
    def _convert_case(self, text: str, case_type: str) -> str:
        """转换大小写"""
        if case_type == 'snake_case':
            return self._to_snake_case(text)
        elif case_type == 'camelCase':
            return self._to_camel_case(text)
        elif case_type == 'PascalCase':
            return self._to_pascal_case(text)
        return text
    
    def _to_snake_case(self, text: str) -> str:
        """转换为蛇形命名"""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def _to_camel_case(self, text: str) -> str:
        """转换为驼峰命名"""
        components = text.split('_')
        return components[0] + ''.join(word.capitalize() for word in components[1:])
    
    def _to_pascal_case(self, text: str) -> str:
        """转换为帕斯卡命名"""
        components = text.split('_')
        return ''.join(word.capitalize() for word in components)
    
    def _is_json_content(self, request: Request) -> bool:
        """检查是否是 JSON 内容"""
        content_type = request.headers.get('content-type', '')
        return 'application/json' in content_type
    
    def _is_json_response(self, response: Response) -> bool:
        """检查是否是 JSON 响应"""
        content_type = response.headers.get('content-type', '')
        return 'application/json' in content_type


class DataValidator(Transformer):
    """数据验证转换器"""
    
    def __init__(
        self,
        request_schema: Optional[BaseModel] = None,
        response_schema: Optional[BaseModel] = None,
        strict_validation: bool = False,
    ):
        self.request_schema = request_schema
        self.response_schema = response_schema
        self.strict_validation = strict_validation
    
    async def transform_request(self, request: Request, body: bytes) -> bytes:
        """验证并转换请求"""
        if not body or not self.request_schema:
            return body
        
        try:
            data = json.loads(body.decode('utf-8'))
            validated_data = self.request_schema(**data)
            return validated_data.model_dump_json().encode('utf-8')
        except ValidationError as e:
            if self.strict_validation:
                raise ValueError(f"Request validation failed: {e}")
            logger.warning("Request validation failed", error=str(e))
            return body
        except Exception as e:
            logger.warning("Failed to validate request", error=str(e))
            return body
    
    async def transform_response(self, response: Response, body: bytes) -> bytes:
        """验证并转换响应"""
        if not body or not self.response_schema:
            return body
        
        try:
            data = json.loads(body.decode('utf-8'))
            validated_data = self.response_schema(**data)
            return validated_data.model_dump_json().encode('utf-8')
        except ValidationError as e:
            if self.strict_validation:
                raise ValueError(f"Response validation failed: {e}")
            logger.warning("Response validation failed", error=str(e))
            return body
        except Exception as e:
            logger.warning("Failed to validate response", error=str(e))
            return body


class ContentCompressor(Transformer):
    """内容压缩转换器"""
    
    def __init__(
        self,
        compression_type: str = 'gzip',  # 'gzip', 'deflate'
        min_size: int = 1024,  # 最小压缩大小
        compression_level: int = 6,
    ):
        self.compression_type = compression_type
        self.min_size = min_size
        self.compression_level = compression_level
    
    async def transform_request(self, request: Request, body: bytes) -> bytes:
        """压缩请求（通常不需要）"""
        return body
    
    async def transform_response(self, response: Response, body: bytes) -> bytes:
        """压缩响应"""
        if len(body) < self.min_size:
            return body
        
        # 检查客户端是否支持压缩
        accept_encoding = response.headers.get('accept-encoding', '')
        
        if self.compression_type == 'gzip' and 'gzip' in accept_encoding:
            compressed_body = gzip.compress(body, compresslevel=self.compression_level)
            response.headers['content-encoding'] = 'gzip'
            response.headers['content-length'] = str(len(compressed_body))
            return compressed_body
        
        elif self.compression_type == 'deflate' and 'deflate' in accept_encoding:
            compressed_body = zlib.compress(body, level=self.compression_level)
            response.headers['content-encoding'] = 'deflate'
            response.headers['content-length'] = str(len(compressed_body))
            return compressed_body
        
        return body
    
    def should_transform_response(self, request: Request, response: Response) -> bool:
        """判断是否应该压缩响应"""
        # 检查客户端是否支持压缩
        accept_encoding = request.headers.get('accept-encoding', '')
        return self.compression_type in accept_encoding


class FormatConverter(Transformer):
    """格式转换器"""
    
    def __init__(
        self,
        input_format: ContentType = ContentType.JSON,
        output_format: ContentType = ContentType.JSON,
    ):
        self.input_format = input_format
        self.output_format = output_format
    
    async def transform_request(self, request: Request, body: bytes) -> bytes:
        """转换请求格式"""
        if not body:
            return body
        
        try:
            # 解析输入格式
            data = self._parse_content(body, self.input_format)
            
            # 转换为输出格式
            converted_body = self._serialize_content(data, self.output_format)
            
            # 更新 Content-Type 头部
            request.headers['content-type'] = self.output_format.value
            
            return converted_body
        except Exception as e:
            logger.warning("Failed to convert request format", error=str(e))
            return body
    
    async def transform_response(self, response: Response, body: bytes) -> bytes:
        """转换响应格式"""
        if not body:
            return body
        
        try:
            # 解析输入格式
            data = self._parse_content(body, self.input_format)
            
            # 转换为输出格式
            converted_body = self._serialize_content(data, self.output_format)
            
            # 更新 Content-Type 头部
            response.headers['content-type'] = self.output_format.value
            
            return converted_body
        except Exception as e:
            logger.warning("Failed to convert response format", error=str(e))
            return body
    
    def _parse_content(self, body: bytes, content_type: ContentType) -> Any:
        """解析内容"""
        content_str = body.decode('utf-8')
        
        if content_type == ContentType.JSON:
            return json.loads(content_str)
        elif content_type == ContentType.XML:
            import xml.etree.ElementTree as ET
            return self._xml_to_dict(ET.fromstring(content_str))
        elif content_type == ContentType.FORM:
            from urllib.parse import parse_qs
            return parse_qs(content_str)
        elif content_type == ContentType.TEXT:
            return content_str
        else:
            return body
    
    def _serialize_content(self, data: Any, content_type: ContentType) -> bytes:
        """序列化内容"""
        if content_type == ContentType.JSON:
            return json.dumps(data).encode('utf-8')
        elif content_type == ContentType.XML:
            return self._dict_to_xml(data).encode('utf-8')
        elif content_type == ContentType.FORM:
            from urllib.parse import urlencode
            return urlencode(data).encode('utf-8')
        elif content_type == ContentType.TEXT:
            return str(data).encode('utf-8')
        else:
            return data if isinstance(data, bytes) else str(data).encode('utf-8')
    
    def _xml_to_dict(self, element) -> Dict[str, Any]:
        """XML 转字典"""
        result = {}
        
        # 处理属性
        if element.attrib:
            result['@attributes'] = element.attrib
        
        # 处理文本内容
        if element.text and element.text.strip():
            if len(element) == 0:
                return element.text.strip()
            result['#text'] = element.text.strip()
        
        # 处理子元素
        for child in element:
            child_data = self._xml_to_dict(child)
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        
        return result
    
    def _dict_to_xml(self, data: Dict[str, Any], root_name: str = 'root') -> str:
        """字典转 XML"""
        import xml.etree.ElementTree as ET
        
        def build_element(parent, key, value):
            if isinstance(value, dict):
                elem = ET.SubElement(parent, key)
                for k, v in value.items():
                    if k == '@attributes':
                        elem.attrib.update(v)
                    elif k == '#text':
                        elem.text = str(v)
                    else:
                        build_element(elem, k, v)
            elif isinstance(value, list):
                for item in value:
                    build_element(parent, key, item)
            else:
                elem = ET.SubElement(parent, key)
                elem.text = str(value)
        
        root = ET.Element(root_name)
        for key, value in data.items():
            build_element(root, key, value)
        
        return ET.tostring(root, encoding='unicode')


class TransformMiddleware(BaseHTTPMiddleware):
    """转换中间件"""
    
    def __init__(
        self,
        app,
        transformers: Optional[List[Transformer]] = None,
        transform_type: TransformType = TransformType.BOTH,
    ):
        super().__init__(app)
        self.transformers = transformers or []
        self.transform_type = transform_type
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """处理请求"""
        try:
            # 读取请求体
            request_body = await request.body()
            
            # 转换请求
            if self.transform_type in [TransformType.REQUEST, TransformType.BOTH]:
                request_body = await self._transform_request(request, request_body)
            
            # 创建新的请求对象（如果请求体被修改）
            if request_body != await request.body():
                request = self._create_modified_request(request, request_body)
            
            # 调用下一个中间件
            response = await call_next(request)
            
            # 转换响应
            if self.transform_type in [TransformType.RESPONSE, TransformType.BOTH]:
                response = await self._transform_response(request, response)
            
            return response
            
        except Exception as e:
            logger.error("Transform middleware error", error=str(e))
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error in transform middleware"}
            )
    
    async def _transform_request(self, request: Request, body: bytes) -> bytes:
        """转换请求"""
        for transformer in self.transformers:
            if transformer.should_transform_request(request):
                try:
                    body = await transformer.transform_request(request, body)
                except Exception as e:
                    logger.warning(
                        "Request transformer failed",
                        transformer=transformer.__class__.__name__,
                        error=str(e)
                    )
        
        return body
    
    async def _transform_response(self, request: Request, response: Response) -> Response:
        """转换响应"""
        # 读取响应体
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
        
        # 应用转换器
        for transformer in self.transformers:
            if transformer.should_transform_response(request, response):
                try:
                    response_body = await transformer.transform_response(response, response_body)
                except Exception as e:
                    logger.warning(
                        "Response transformer failed",
                        transformer=transformer.__class__.__name__,
                        error=str(e)
                    )
        
        # 创建新的响应
        return StarletteResponse(
            content=response_body,
            status_code=response.status_code,
            headers=response.headers,
            media_type=response.media_type,
        )
    
    def _create_modified_request(self, request: Request, new_body: bytes) -> Request:
        """创建修改后的请求对象"""
        # 这是一个简化的实现，实际可能需要更复杂的处理
        request._body = new_body
        return request
    
    def add_transformer(self, transformer: Transformer) -> None:
        """添加转换器"""
        self.transformers.append(transformer)
        logger.info("Transformer added", transformer=transformer.__class__.__name__)
    
    def remove_transformer(self, transformer_class: type) -> bool:
        """移除转换器"""
        for i, transformer in enumerate(self.transformers):
            if isinstance(transformer, transformer_class):
                del self.transformers[i]
                logger.info("Transformer removed", transformer=transformer_class.__name__)
                return True
        return False


def create_transform_middleware(
    transformers: Optional[List[Transformer]] = None,
    transform_type: TransformType = TransformType.BOTH,
) -> Callable:
    """创建转换中间件"""
    
    def middleware_factory(app):
        return TransformMiddleware(
            app,
            transformers=transformers,
            transform_type=transform_type,
        )
    
    return middleware_factory 