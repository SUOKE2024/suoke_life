"""
切诊服务客户端

提供与切诊服务的通信接口
"""

import logging
from typing import Dict, Any, Optional, List
import aiohttp

from ..base import BaseServiceClient
from .models import PalpationRequest, PalpationResponse
from ...utils.retry import retry_with_backoff
from ...utils.exceptions import CommunicationError
from ..config import get_settings

logger = logging.getLogger(__name__)


class PalpationServiceClient(BaseServiceClient):
    """切诊服务客户端"""
    
    def __init__(self, base_url: Optional[str] = None):
        """初始化客户端"""
        if base_url is None:
            settings = get_settings()
            base_url = f"http://{settings.external_services.palpation_service.host}:{settings.external_services.palpation_service.port}"
        
        super().__init__(base_url)
        self.service_name = "palpation-service"
    
    @retry_with_backoff(max_retries=3)
    async def analyze_pulse(self, pulse_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        进行脉象分析
        
        Args:
            pulse_data: 脉象数据
            metadata: 可选的元数据
            
        Returns:
            分析结果
        """
        try:
            request = PalpationRequest(
                pulse_data=pulse_data,
                metadata=metadata or {}
            )
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/v1/analyze",
                    json=request.dict(),
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status==200:
                        result = await response.json()
                        return PalpationResponse(**result).dict()
                    else:
                        error_text = await response.text()
                        raise CommunicationError(f"脉象分析失败: {error_text}")
                        
        except Exception as e:
            logger.error(f"脉象分析错误: {e}")
            raise CommunicationError(f"切诊服务通信错误: {e}")
    
    async def get_pulse_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取用户的脉象历史记录
        
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
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status==200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise CommunicationError(f"获取脉象历史失败: {error_text}")
                        
        except Exception as e:
            logger.error(f"获取脉象历史错误: {e}")
            raise CommunicationError(f"切诊服务通信错误: {e}")
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/health",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status==200
        except Exception:
            return False 