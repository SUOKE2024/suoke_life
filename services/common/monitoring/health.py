"""
health - 索克生活项目模块
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List

import aiohttp

logger = logging.getLogger(__name__)


class HealthMonitor:
    """健康监控器"""

    def __init__(self, services: List[str]):
        """TODO: 添加文档字符串"""
        self.services = services
        self.health_status = {}

    async def check_service_health(self, service_url: str) -> Dict[str, Any]:
        """检查单个服务健康状态"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{service_url} / health", timeout=5
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "service": service_url,
                            "status": "healthy",
                            "response_time": response.headers.get(
                                "X - Response - Time", "unknown"
                            ),
                            "timestamp": datetime.utcnow().isoformat(),
                            "details": data,
                        }
                    else:
                        return {
                            "service": service_url,
                            "status": "unhealthy",
                            "error": f"HTTP {response.status}",
                            "timestamp": datetime.utcnow().isoformat(),
                        }
        except Exception as e:
            return {
                "service": service_url,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def check_all_services(self) -> Dict[str, Any]:
        """检查所有服务健康状态"""
        tasks = [self.check_service_health(service) for service in self.services]
        results = await asyncio.gather(*tasks)

        healthy_count = sum(1 for result in results if result["status"] == "healthy")
        total_count = len(results)

        return {
            "overall_health": "healthy" if healthy_count == total_count else "degraded",
            "healthy_services": healthy_count,
            "total_services": total_count,
            "services": results,
            "timestamp": datetime.utcnow().isoformat(),
        }
