#!/usr/bin/env python3
"""
索克生活 API 网关数据转换中间件

处理请求和响应的数据转换、压缩、格式化等。
"""

from ..core.logging import get_logger
from abc import ABC, abstractmethod
from enum import Enum
from fastapi import Request, Response
from pydantic import BaseModel, ValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response as StarletteResponse
from typing import Any, Dict, List, Optional, Callable, Union
from urllib.parse import parse_qs, urlencode
import gzip
import json
import re
import zlib

logger = get_logger(__name__)


class CompressionType(Enum):
    """压缩类型"""
    NONE = "none"
    GZIP = "gzip"
    DEFLATE = "deflate"
    BROTLI = "brotli"


class TransformationType(Enum):
    """转换类型"""
    JSON_TO_XML = "json_to_xml"
    XML_TO_JSON = "xml_to_json"
    CAMEL_TO_SNAKE = "camel_to_snake"
    SNAKE_TO_CAMEL = "snake_to_camel"
    UPPERCASE_KEYS = "uppercase_keys"
    LOWERCASE_KEYS = "lowercase_keys"


class DataTransformer(ABC):
    """数据转换器基类"""

    @abstractmethod
    async def transform_request(self, data: Any) -> Any:
        """转换请求数据"""
        pass

    @abstractmethod
    async def transform_response(self, data: Any) -> Any:
        """转换响应数据"""
        pass


class CaseTransformer(DataTransformer):
    """大小写转换器"""

    def __init__(self, request_transform: TransformationType, response_transform: TransformationType):
        self.request_transform = request_transform
        self.response_transform = response_transform

    async def transform_request(self, data: Any) -> Any:
        """转换请求数据"""
        if self.request_transform == TransformationType.CAMEL_TO_SNAKE:
            return self._camel_to_snake(data)
        elif self.request_transform == TransformationType.SNAKE_TO_CAMEL:
            return self._snake_to_camel(data)
        elif self.request_transform == TransformationType.UPPERCASE_KEYS:
            return self._uppercase_keys(data)
        elif self.request_transform == TransformationType.LOWERCASE_KEYS:
            return self._lowercase_keys(data)
        return data

    async def transform_response(self, data: Any) -> Any:
        """转换响应数据"""
        if self.response_transform == TransformationType.CAMEL_TO_SNAKE:
            return self._camel_to_snake(data)
        elif self.response_transform == TransformationType.SNAKE_TO_CAMEL:
            return self._snake_to_camel(data)
        elif self.response_transform == TransformationType.UPPERCASE_KEYS:
            return self._uppercase_keys(data)
        elif self.response_transform == TransformationType.LOWERCASE_KEYS:
            return self._lowercase_keys(data)
        return data

    def _camel_to_snake(self, data: Any) -> Any:
        """驼峰转下划线"""
        if isinstance(data, dict):
            return {
                self._camel_to_snake_str(k): self._camel_to_snake(v)
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [self._camel_to_snake(item) for item in data]
        return data

    def _snake_to_camel(self, data: Any) -> Any:
        """下划线转驼峰"""
        if isinstance(data, dict):
            return {
                self._snake_to_camel_str(k): self._snake_to_camel(v)
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [self._snake_to_camel(item) for item in data]
        return data

    def _uppercase_keys(self, data: Any) -> Any:
        """键名转大写"""
        if isinstance(data, dict):
            return {
                k.upper(): self._uppercase_keys(v)
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [self._uppercase_keys(item) for item in data]
        return data

    def _lowercase_keys(self, data: Any) -> Any:
        """键名转小写"""
        if isinstance(data, dict):
            return {
                k.lower(): self._lowercase_keys(v)
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [self._lowercase_keys(item) for item in data]
        return data

    def _camel_to_snake_str(self, name: str) -> str:
        """驼峰字符串转下划线"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def _snake_to_camel_str(self, name: str) -> str:
        """下划线字符串转驼峰"""
        components = name.split('_')
        return components[0] + ''.join(x.capitalize() for x in components[1:])


class CompressionHandler:
    """压缩处理器"""

    @staticmethod
    def compress(data: bytes, compression_type: CompressionType) -> bytes:
        """压缩数据"""
        if compression_type == CompressionType.GZIP:
            return gzip.compress(data)
        elif compression_type == CompressionType.DEFLATE:
            return zlib.compress(data)
        elif compression_type == CompressionType.BROTLI:
            try:
                import brotli
                return brotli.compress(data)
            except ImportError:
                logger.warning("Brotli compression not available, falling back to gzip")
                return gzip.compress(data)
        return data

    @staticmethod
    def decompress(data: bytes, compression_type: CompressionType) -> bytes:
        """解压数据"""
        if compression_type == CompressionType.GZIP:
            return gzip.decompress(data)
        elif compression_type == CompressionType.DEFLATE:
            return zlib.decompress(data)
        elif compression_type == CompressionType.BROTLI:
            try:
                import brotli
                return brotli.decompress(data)
            except ImportError:
                logger.warning("Brotli decompression not available")
                raise
        return data

    @staticmethod
    def get_compression_type(accept_encoding: str) -> CompressionType:
        """根据Accept-Encoding头确定压缩类型"""
        if not accept_encoding:
            return CompressionType.NONE

        accept_encoding = accept_encoding.lower()
        
        if "br" in accept_encoding:
            return CompressionType.BROTLI
        elif "gzip" in accept_encoding:
            return CompressionType.GZIP
        elif "deflate" in accept_encoding:
            return CompressionType.DEFLATE
        
        return CompressionType.NONE


class TransformMiddleware(BaseHTTPMiddleware):
    """数据转换中间件"""

    def __init__(self, app, transformers: Optional[List[DataTransformer]] = None, enable_compression: bool = True):
        """初始化转换中间件"""
        super().__init__(app)
        self.transformers = transformers or []
        self.enable_compression = enable_compression
        self.compression_handler = CompressionHandler()

        # 不处理的路径
        self.skip_paths = {
            "/health",
            "/health/ready",
            "/health/live",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json"
        }

        # 不压缩的内容类型
        self.no_compress_types = {
            "image/",
            "video/",
            "audio/",
            "application/zip",
            "application/gzip",
            "application/x-rar-compressed"
        }

    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        # 跳过不需要处理的路径
        if request.url.path in self.skip_paths:
            return await call_next(request)

        # 处理请求转换
        await self._transform_request(request)

        # 处理响应
        response = await call_next(request)

        # 处理响应转换和压缩
        response = await self._transform_response(request, response)

        return response

    async def _transform_request(self, request: Request) -> None:
        """转换请求数据"""
        if not self.transformers:
            return

        try:
            # 只处理JSON请求
            content_type = request.headers.get("content-type", "")
            if not content_type.startswith("application/json"):
                return

            # 读取请求体
            body = await request.body()
            if not body:
                return

            # 解析JSON
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                return

            # 应用转换器
            for transformer in self.transformers:
                data = await transformer.transform_request(data)

            # 更新请求体
            new_body = json.dumps(data).encode()
            request._body = new_body

        except Exception as e:
            logger.error("Request transformation failed", error=str(e), exc_info=True)

    async def _transform_response(self, request: Request, response: Response) -> Response:
        """转换响应数据"""
        try:
            # 处理数据转换
            if self.transformers:
                response = await self._apply_response_transformers(response)

            # 处理压缩
            if self.enable_compression:
                response = await self._apply_compression(request, response)

            return response

        except Exception as e:
            logger.error("Response transformation failed", error=str(e), exc_info=True)
            return response

    async def _apply_response_transformers(self, response: Response) -> Response:
        """应用响应转换器"""
        try:
            # 只处理JSON响应
            content_type = response.headers.get("content-type", "")
            if not content_type.startswith("application/json"):
                return response

            # 获取响应体
            if hasattr(response, 'body'):
                body = response.body
            else:
                return response

            if not body:
                return response

            # 解析JSON
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                return response

            # 应用转换器
            for transformer in self.transformers:
                data = await transformer.transform_response(data)

            # 创建新响应
            new_body = json.dumps(data).encode()
            new_response = Response(
                content=new_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type="application/json"
            )

            return new_response

        except Exception as e:
            logger.error("Response transformer application failed", error=str(e))
            return response

    async def _apply_compression(self, request: Request, response: Response) -> Response:
        """应用压缩"""
        try:
            # 检查是否需要压缩
            if not self._should_compress(request, response):
                return response

            # 确定压缩类型
            accept_encoding = request.headers.get("accept-encoding", "")
            compression_type = self.compression_handler.get_compression_type(accept_encoding)

            if compression_type == CompressionType.NONE:
                return response

            # 获取响应体
            if hasattr(response, 'body'):
                body = response.body
            else:
                return response

            if not body:
                return response

            # 压缩数据
            compressed_body = self.compression_handler.compress(body, compression_type)

            # 创建新响应
            new_headers = dict(response.headers)
            new_headers["content-encoding"] = compression_type.value
            new_headers["content-length"] = str(len(compressed_body))

            new_response = Response(
                content=compressed_body,
                status_code=response.status_code,
                headers=new_headers
            )

            return new_response

        except Exception as e:
            logger.error("Compression application failed", error=str(e))
            return response

    def _should_compress(self, request: Request, response: Response) -> bool:
        """判断是否应该压缩"""
        # 检查响应大小
        content_length = response.headers.get("content-length")
        if content_length and int(content_length) < 1024:  # 小于1KB不压缩
            return False

        # 检查内容类型
        content_type = response.headers.get("content-type", "")
        for no_compress_type in self.no_compress_types:
            if content_type.startswith(no_compress_type):
                return False

        # 检查是否已经压缩
        if response.headers.get("content-encoding"):
            return False

        return True