"""
服务客户端基础类

提供所有外部服务客户端的基础功能和抽象接口
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import aiohttp

try:
    from xiaoai.config.settings import get_settings
except ImportError:
    from xiaoai.config.test_settings import get_settings
from xiaoai.utils.exceptions import ServiceUnavailableError, CommunicationError
from xiaoai.utils.retry import retry_with_backoff

logger = logging.getLogger(__name__)


class BaseServiceClient(ABC):
    """服务客户端基类"""
    
    def __init__(self, base_url: str):
        """
        初始化基础服务客户端
        
        Args:
            base_url: 服务的基础URL
        """
        self.base_url = base_url.rstrip('/')
        self.service_name = "unknown"
        self._session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
        
    async def initialize(self) -> None:
        """初始化客户端"""
        if self._session is None:
            timeout = aiohttp.ClientTimeout(total=30)
            self._session = aiohttp.ClientSession(timeout=timeout)
            
    async def close(self) -> None:
        """关闭客户端"""
        if self._session:
            await self._session.close()
            self._session = None
            
    async def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            bool: 服务是否健康
        """
        try:
            if self._session is None:
                await self.initialize()
                
            async with self._session.get(f"{self.base_url}/health") as response:
                return response.status==200
        except Exception as e:
            logger.warning(f"健康检查失败 {self.service_name}: {e}")
            return False
            
    @retry_with_backoff(max_retries=3)
    async def _make_request(self, method: str, endpoint: str,**kwargs) -> Dict[str, Any]:
        """
        发起HTTP请求
        
        Args:
            method: HTTP方法
            endpoint: 端点路径
           **kwargs: 其他请求参数
            
        Returns:
            响应数据
            
        Raises:
            CommunicationError: 通信错误
        """
        if self._session is None:
            await self.initialize()
            
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            async with self._session.request(method, url,**kwargs) as response:
                if response.status==200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise CommunicationError(f"HTTP {response.status}: {error_text}")
                    
        except aiohttp.ClientError as e:
            logger.error(f"请求失败 {self.service_name}: {e}")
            raise CommunicationError(f"网络请求失败: {e}")
        except Exception as e:
            logger.error(f"未知错误 {self.service_name}: {e}")
            raise CommunicationError(f"请求处理失败: {e}")


# 保持向后兼容性的ServiceEndpoint类
class ServiceEndpoint:
    """服务端点配置（向后兼容）"""
    def __init__(self, name: str, host: str, port: int, protocol: str = "http",**kwargs):
        self.name = name
        self.host = host
        self.port = port
        self.protocol = protocol
        self.timeout = kwargs.get('timeout', 30)
        self.max_retries = kwargs.get('max_retries', 3)
        self.health_check_path = kwargs.get('health_check_path', '/health') 