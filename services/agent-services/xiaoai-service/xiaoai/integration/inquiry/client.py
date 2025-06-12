"""
问诊服务客户端

提供与问诊服务的通信接口
"""

import logging
from typing import Any, Dict, List, Optional

import aiohttp

from xiaoai.integration.base import BaseServiceClient
from xiaoai.utils.exceptions import CommunicationError
from xiaoai.utils.retry import retry_with_backoff

from ..config import get_settings
from .models import InquiryRequest, InquiryResponse

logger = logging.getLogger(__name__)


class InquiryServiceClient(BaseServiceClient):
    """问诊服务客户端"""

    def __init__(self, base_url: Optional[str] = None):
        """初始化客户端"""
        if base_url is None:
            settings = get_settings()
            base_url = f"http://{settings.external_services.inquiry_service.host}:{settings.external_services.inquiry_service.port}"

        super().__init__(base_url)
        self.service_name = "inquiry-service"

    @retry_with_backoff(max_retries=3)
    async def conduct_inquiry(
        self, questions: List[str], metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        进行问诊

        Args:
            questions: 问题列表
            metadata: 可选的元数据

        Returns:
            问诊结果
        """
        try:
            request = InquiryRequest(questions=questions, metadata=metadata or {})

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/v1/inquiry",
                    json=request.dict(),
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return InquiryResponse(**result).dict()
                    else:
                        error_text = await response.text()
                        raise CommunicationError(f"问诊失败: {error_text}")

        except Exception as e:
            logger.error(f"问诊错误: {e}")
            raise CommunicationError(f"问诊服务通信错误: {e}")

    async def get_inquiry_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取用户的问诊历史记录

        Args:
            user_id: 用户ID
            limit: 返回记录数限制

        Returns:
            历史记录列表
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/v1/history/{user_id}",
                    params={"limit": limit},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise CommunicationError(f"获取问诊历史失败: {error_text}")

        except Exception as e:
            logger.error(f"获取问诊历史错误: {e}")
            raise CommunicationError(f"问诊服务通信错误: {e}")

    async def health_check(self) -> bool:
        """健康检查"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/health", timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status == 200
        except Exception:
            return False
