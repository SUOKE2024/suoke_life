"""
response_transformer - 索克生活项目模块
"""

from fastapi import Response
from internal.model.config import GatewayConfig
from typing import Dict, List, Optional, Set
import logging

#! / usr / bin / env python
# - * - coding: utf - 8 - * -

"""
响应转换器模块，用于在API网关中转换和修改响应
支持添加CORS头、压缩响应内容、添加链路追踪ID等功能
"""



logger = logging.getLogger(__name__)


class ResponseTransformer:
    """响应转换器，用于在响应返回前进行处理"""

    def __init__(self, config: GatewayConfig):
        """
        初始化响应转换器

        Args:
            config: 网关配置
        """
        self.config = config
        self.compression_enabled = getattr(config, 'compression_enabled', False)
        self.cors_enabled = getattr(config.middleware, 'cors', {}).get('enabled', False)
        self.cors_headers = self._get_cors_headers() if self.cors_enabled else {}

    def _get_cors_headers(self) - > Dict[str, str]:
        """获取CORS头"""
        cors_config = self.config.middleware.cors
        headers = {}

        if cors_config.allow_origins:
            if len(cors_config.allow_origins) == 1 and cors_config.allow_origins[0] == " * ":
                headers["Access - Control - Allow - Origin"] = " * "
            else:
                # 实际使用时会根据请求动态设置
                headers["Access - Control - Allow - Origin"] = cors_config.allow_origins[0]

        if cors_config.allow_methods:
            headers["Access - Control - Allow - Methods"] = ", ".join(cors_config.allow_methods)

        if cors_config.allow_headers:
            headers["Access - Control - Allow - Headers"] = ", ".join(cors_config.allow_headers)

        if cors_config.allow_credentials:
            headers["Access - Control - Allow - Credentials"] = "true"

        if cors_config.max_age:
            headers["Access - Control - Max - Age"] = str(cors_config.max_age)

        return headers

    async def transform(self, response: Response, request_id: Optional[str] = None) - > Response:
        """
        转换响应

        Args:
            response: 原始响应
            request_id: 请求ID

        Returns:
            Response: 转换后的响应
        """
        # 如果启用了CORS，添加CORS头
        if self.cors_enabled:
            for key, value in self.cors_headers.items():
                response.headers[key] = value

        # 添加请求ID
        if request_id:
            response.headers["X - Request - ID"] = request_id

        # 添加网关版本信息
        response.headers["X - Gateway - Version"] = "0.1.0"

        return response