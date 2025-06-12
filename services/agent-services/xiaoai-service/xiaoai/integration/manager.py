"""
服务客户端管理器

统一管理所有外部诊断服务的客户端实例
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from .base import BaseServiceClient
try:
    from ..config.settings import get_settings
except ImportError:
    from ..config.test_settings import get_settings


logger = logging.getLogger(__name__)


class ServiceClientManager:
    """服务客户端管理器"""
    
    def __init__(self):
        self.clients = {}
        self.settings = get_settings()
    
    async def initialize(self) -> None:
        """初始化所有服务客户端"""
        logger.info("初始化服务客户端管理器...")
        
        # 动态导入客户端类
        from .look.client import LookServiceClient
        from .listen.client import ListenServiceClient
        from .inquiry.client import InquiryServiceClient
        from .palpation.client import PalpationServiceClient
        from .calculation.client import CalculationServiceClient
        
        # 创建客户端实例
        client_classes = {
            "look": LookServiceClient,
            "listen": ListenServiceClient,
            "inquiry": InquiryServiceClient,
            "palpation": PalpationServiceClient,
            "calculation": CalculationServiceClient
        }
        
        # 并行初始化所有客户端
        init_tasks = []
        for service_name, client_class in client_classes.items():
            try:
                client = client_class()
                self.clients[service_name] = client
                init_tasks.append(client.initialize())
            except Exception as e:
                logger.error(f"创建{service_name}客户端失败: {e}")
        
        # 等待所有客户端初始化完成
        if init_tasks:
            results = await asyncio.gather(*init_tasks, return_exceptions=True)
            
            # 检查初始化结果
            for i, result in enumerate(results):
                service_name = list(client_classes.keys())[i]
                if isinstance(result, Exception):
                    logger.error(f"{service_name}服务客户端初始化失败: {result}")
                    # 移除失败的客户端
                    if service_name in self.clients:
                        del self.clients[service_name]
                else:
                    logger.info(f"{service_name}服务客户端初始化成功")
        
        logger.info(f"服务客户端管理器初始化完成，可用服务: {list(self.clients.keys())}")
    
    def get_client(self, service_name: str) -> Optional[BaseServiceClient]:
        """获取服务客户端"""
        return self.clients.get(service_name)
    
    async def health_check_all(self) -> Dict[str, bool]:
        """检查所有服务健康状态"""
        health_status = {}
        
        if not self.clients:
            return health_status
        
        # 并行检查所有服务
        check_tasks = []
        service_names = []
        
        for service_name, client in self.clients.items():
            check_tasks.append(client.health_check())
            service_names.append(service_name)
        
        results = await asyncio.gather(*check_tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            service_name = service_names[i]
            if isinstance(result, Exception):
                health_status[service_name] = False
                logger.warning(f"{service_name}服务健康检查异常: {result}")
            else:
                health_status[service_name] = result
        
        return health_status
    
    async def close_all(self) -> None:
        """关闭所有客户端"""
        if not self.clients:
            return
        
        close_tasks = []
        for client in self.clients.values():
            close_tasks.append(client.close())
        
        await asyncio.gather(*close_tasks, return_exceptions=True)
        self.clients.clear()
        
        logger.info("所有服务客户端已关闭")
    
    def get_available_services(self) -> List[str]:
        """获取可用服务列表"""
        return list(self.clients.keys())
    
    async def test_service_connectivity(self, service_name: str) -> Dict[str, Any]:
        """测试特定服务的连接性"""
        client = self.get_client(service_name)
        if not client:
            return {
                "service": service_name,
                "available": False,
                "error": "客户端未找到"
            }
        
        try:
            # 执行健康检查
            is_healthy = await client.health_check()
            
            # 尝试简单的测试调用
            test_result = None
            try:
                test_data = {"test": True, "timestamp": datetime.now().isoformat()}
                test_result = await client.analyze("test_user", "test_session", test_data)
            except Exception as e:
                test_result = {"error": str(e)}
            
            return {
                "service": service_name,
                "available": is_healthy,
                "health_check": is_healthy,
                "test_call": test_result,
                "endpoint": {
                    "host": client.endpoint.host,
                    "port": client.endpoint.port,
                    "protocol": client.endpoint.protocol
                }
            }
            
        except Exception as e:
            return {
                "service": service_name,
                "available": False,
                "error": str(e)
            } 