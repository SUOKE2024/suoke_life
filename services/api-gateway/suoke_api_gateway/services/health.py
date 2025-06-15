#!/usr/bin/env python3
"""
索克生活 API 网关健康检查服务

提供系统和服务健康检查功能。
"""

from ..core.config import get_settings
from ..core.logging import get_logger
from typing import Dict, Any, List, Optional
import asyncio
import psutil
import time
from datetime import datetime, timedelta

logger = get_logger(__name__)


class HealthService:
    """健康检查服务"""

    def __init__(self, settings=None):
        """初始化健康检查服务"""
        self.settings = settings or get_settings()
        self.start_time = time.time()
        self.checks = {}
        self._initialized = False

    async def initialize(self) -> None:
        """初始化服务"""
        if self._initialized:
            return

        logger.info("Initializing health service")
        
        # 注册基本健康检查
        self.register_check("system", self._check_system_health)
        self.register_check("memory", self._check_memory_health)
        self.register_check("disk", self._check_disk_health)
        
        self._initialized = True
        logger.info("Health service initialized")

    async def cleanup(self) -> None:
        """清理资源"""
        logger.info("Cleaning up health service")
        self.checks.clear()
        self._initialized = False

    def register_check(self, name: str, check_func) -> None:
        """注册健康检查"""
        self.checks[name] = check_func
        logger.debug(f"Registered health check: {name}")

    def unregister_check(self, name: str) -> None:
        """注销健康检查"""
        if name in self.checks:
            del self.checks[name]
            logger.debug(f"Unregistered health check: {name}")

    async def get_system_health(self) -> Dict[str, Any]:
        """获取系统健康状态"""
        try:
            health_results = {}
            overall_healthy = True

            # 执行所有健康检查
            for check_name, check_func in self.checks.items():
                try:
                    result = await check_func()
                    health_results[check_name] = result
                    
                    if not result.get("healthy", False):
                        overall_healthy = False
                        
                except Exception as e:
                    logger.error(f"Health check '{check_name}' failed", error=str(e))
                    health_results[check_name] = {
                        "healthy": False,
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    overall_healthy = False

            # 添加运行时信息
            uptime = time.time() - self.start_time
            health_results["runtime"] = {
                "healthy": True,
                "uptime_seconds": uptime,
                "uptime_human": self._format_uptime(uptime),
                "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
                "timestamp": datetime.utcnow().isoformat()
            }

            return {
                "healthy": overall_healthy,
                "timestamp": datetime.utcnow().isoformat(),
                "checks": health_results
            }

        except Exception as e:
            logger.error("Failed to get system health", error=str(e), exc_info=True)
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def is_ready(self) -> bool:
        """检查服务是否准备就绪"""
        try:
            # 检查基本系统资源
            memory = psutil.virtual_memory()
            if memory.percent > 95:  # 内存使用超过95%
                return False

            disk = psutil.disk_usage("/")
            if disk.percent > 95:  # 磁盘使用超过95%
                return False

            # 检查是否已初始化
            if not self._initialized:
                return False

            return True

        except Exception as e:
            logger.error("Readiness check failed", error=str(e))
            return False

    async def is_alive(self) -> bool:
        """检查服务是否存活"""
        try:
            # 简单的存活检查
            return True

        except Exception as e:
            logger.error("Liveness check failed", error=str(e))
            return False

    async def _check_system_health(self) -> Dict[str, Any]:
        """检查系统健康状态"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
            
            # 判断系统是否健康
            healthy = cpu_percent < 90  # CPU使用率低于90%
            
            return {
                "healthy": healthy,
                "cpu_percent": cpu_percent,
                "load_average": {
                    "1min": load_avg[0],
                    "5min": load_avg[1],
                    "15min": load_avg[2]
                },
                "cpu_count": psutil.cpu_count(),
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def _check_memory_health(self) -> Dict[str, Any]:
        """检查内存健康状态"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # 判断内存是否健康
            healthy = memory.percent < 85  # 内存使用率低于85%
            
            return {
                "healthy": healthy,
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used,
                    "free": memory.free
                },
                "swap": {
                    "total": swap.total,
                    "used": swap.used,
                    "free": swap.free,
                    "percent": swap.percent
                },
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def _check_disk_health(self) -> Dict[str, Any]:
        """检查磁盘健康状态"""
        try:
            disk = psutil.disk_usage("/")
            
            # 判断磁盘是否健康
            healthy = disk.percent < 85  # 磁盘使用率低于85%
            
            return {
                "healthy": healthy,
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent
                },
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def _format_uptime(self, uptime_seconds: float) -> str:
        """格式化运行时间"""
        try:
            uptime = int(uptime_seconds)
            days = uptime // 86400
            hours = (uptime % 86400) // 3600
            minutes = (uptime % 3600) // 60
            seconds = uptime % 60

            parts = []
            if days > 0:
                parts.append(f"{days}天")
            if hours > 0:
                parts.append(f"{hours}小时")
            if minutes > 0:
                parts.append(f"{minutes}分钟")
            if seconds > 0 or not parts:
                parts.append(f"{seconds}秒")

            return "".join(parts)

        except Exception:
            return f"{uptime_seconds:.1f}秒"


# 全局健康服务实例
_health_service: Optional[HealthService] = None


async def get_health_service() -> HealthService:
    """获取健康服务实例"""
    global _health_service
    
    if _health_service is None:
        _health_service = HealthService()
        await _health_service.initialize()
    
    return _health_service


async def cleanup_health_service() -> None:
    """清理健康服务"""
    global _health_service
    
    if _health_service is not None:
        await _health_service.cleanup()
        _health_service = None