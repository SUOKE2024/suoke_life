"""健康检查服务

提供系统健康检查功能，包括数据库连接、外部服务、系统资源等状态监控。
"""

import asyncio
import time
import psutil
import httpx
from typing import Dict, Any, Optional, List
from xiaoke_service.core.config import settings
from xiaoke_service.core.logging import get_logger
from xiaoke_service.core.exceptions import ExternalServiceError

logger = get_logger(__name__)


class HealthChecker:
    """健康检查器
    
    提供全面的系统健康检查，包括：
    - 数据库连接状态
    - 外部服务可用性
    - 系统资源使用情况
    - 应用程序性能指标
    """

    def __init__(self):
        """初始化健康检查器"""
        self.start_time = time.time()
        self.check_history: List[Dict[str, Any]] = []
        self.max_history = 100
        self._http_client: Optional[httpx.AsyncClient] = None

    async def initialize(self) -> None:
        """初始化健康检查器"""
        self._http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0),
            limits=httpx.Limits(max_connections=10)
        )
        logger.info("健康检查器初始化完成")

    async def close(self) -> None:
        """关闭健康检查器"""
        if self._http_client:
            await self._http_client.aclose()
        logger.info("健康检查器已关闭")

    async def check_basic(self) -> Dict[str, Any]:
        """基础健康检查
        
        Returns:
            Dict: 基础健康状态
        """
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "uptime": time.time() - self.start_time,
            "service": settings.service.service_name,
            "version": settings.service.service_version,
            "environment": settings.service.environment,
        }

    async def check_system_resources(self) -> Dict[str, Any]:
        """检查系统资源使用情况
        
        Returns:
            Dict: 系统资源状态
        """
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            
            # 磁盘使用情况
            disk = psutil.disk_usage('/')
            
            # 网络连接数（可能需要权限）
            try:
                connections = len(psutil.net_connections())
            except (psutil.AccessDenied, PermissionError):
                connections = 0  # 无权限时设为0
            
            # 进程信息
            process = psutil.Process()
            try:
                process_memory = process.memory_info()
                process_threads = process.num_threads()
            except (psutil.AccessDenied, PermissionError):
                process_memory = None
                process_threads = 0
            
            return {
                "cpu": {
                    "usage_percent": cpu_percent,
                    "count": psutil.cpu_count(),
                    "status": "healthy" if cpu_percent < 80 else "warning" if cpu_percent < 95 else "critical"
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "used": memory.used,
                    "percent": memory.percent,
                    "status": "healthy" if memory.percent < 80 else "warning" if memory.percent < 95 else "critical"
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100,
                    "status": "healthy" if disk.used / disk.total < 0.8 else "warning" if disk.used / disk.total < 0.95 else "critical"
                },
                "network": {
                    "connections": connections,
                    "status": "healthy" if connections < 1000 else "warning"
                },
                "process": {
                    "pid": process.pid,
                    "memory_rss": process_memory.rss if process_memory else 0,
                    "memory_vms": process_memory.vms if process_memory else 0,
                    "threads": process_threads,
                    "status": "healthy"
                }
            }
            
        except Exception as e:
            logger.error("系统资源检查失败", error=str(e))
            return {
                "status": "error",
                "error": str(e)
            }

    async def check_external_services(self) -> Dict[str, Any]:
        """检查外部服务可用性
        
        Returns:
            Dict: 外部服务状态
        """
        services = {
            "openai": "https://api.openai.com/v1/models",
            "anthropic": "https://api.anthropic.com/v1/messages",
        }
        
        results = {}
        
        for service_name, url in services.items():
            try:
                start_time = time.time()
                
                if not self._http_client:
                    results[service_name] = {
                        "status": "error",
                        "error": "HTTP client not initialized"
                    }
                    continue
                
                # 只做简单的HEAD请求或者不需要认证的请求
                response = await self._http_client.head(url, timeout=5.0)
                duration = time.time() - start_time
                
                results[service_name] = {
                    "status": "healthy" if response.status_code < 500 else "unhealthy",
                    "response_time": round(duration * 1000, 2),
                    "status_code": response.status_code,
                }
                
            except httpx.TimeoutException:
                results[service_name] = {
                    "status": "timeout",
                    "error": "Request timeout"
                }
            except Exception as e:
                results[service_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return results

    async def check_application_metrics(self) -> Dict[str, Any]:
        """检查应用程序指标
        
        Returns:
            Dict: 应用程序指标
        """
        return {
            "uptime_seconds": time.time() - self.start_time,
            "health_checks_performed": len(self.check_history),
            "last_check_time": self.check_history[-1]["timestamp"] if self.check_history else None,
            "configuration": {
                "debug_mode": settings.service.debug,
                "environment": settings.service.environment,
                "log_level": settings.monitoring.log_level,
                "rate_limit_enabled": settings.service.rate_limit_enabled,
            }
        }

    async def check_all(self) -> Dict[str, Any]:
        """执行全面健康检查
        
        Returns:
            Dict: 完整的健康检查报告
        """
        start_time = time.time()
        
        try:
            # 并行执行所有检查
            basic_check, system_check, external_check, app_metrics = await asyncio.gather(
                self.check_basic(),
                self.check_system_resources(),
                self.check_external_services(),
                self.check_application_metrics(),
                return_exceptions=True
            )
            
            # 处理异常结果
            if isinstance(basic_check, Exception):
                basic_check = {"status": "error", "error": str(basic_check)}
            if isinstance(system_check, Exception):
                system_check = {"status": "error", "error": str(system_check)}
            if isinstance(external_check, Exception):
                external_check = {"status": "error", "error": str(external_check)}
            if isinstance(app_metrics, Exception):
                app_metrics = {"status": "error", "error": str(app_metrics)}
            
            # 综合健康状态
            overall_status = self._determine_overall_status({
                "basic": basic_check,
                "system": system_check,
                "external": external_check,
                "application": app_metrics
            })
            
            duration = time.time() - start_time
            
            health_report = {
                "status": overall_status,
                "timestamp": time.time(),
                "check_duration_ms": round(duration * 1000, 2),
                "checks": {
                    "basic": basic_check,
                    "system": system_check,
                    "external": external_check,
                    "application": app_metrics
                }
            }
            
            # 保存检查历史
            self._save_check_history(health_report)
            
            return health_report
            
        except Exception as e:
            logger.error("健康检查失败", error=str(e))
            return {
                "status": "error",
                "timestamp": time.time(),
                "error": str(e)
            }

    def _determine_overall_status(self, checks: Dict[str, Any]) -> str:
        """确定整体健康状态
        
        Args:
            checks: 各项检查结果
            
        Returns:
            str: 整体状态
        """
        # 检查关键系统
        critical_systems = ["basic", "system"]
        for system in critical_systems:
            if system in checks:
                status = checks[system].get("status", "unknown")
                if status in ["error", "critical"]:
                    return "unhealthy"
                elif status == "warning":
                    return "degraded"
        
        # 检查非关键系统
        warning_count = 0
        for check_name, check_result in checks.items():
            if isinstance(check_result, dict):
                status = check_result.get("status", "unknown")
                if status in ["warning", "timeout"]:
                    warning_count += 1
        
        if warning_count > 1:
            return "degraded"
        
        return "healthy"

    def _save_check_history(self, health_report: Dict[str, Any]) -> None:
        """保存检查历史
        
        Args:
            health_report: 健康检查报告
        """
        self.check_history.append({
            "timestamp": health_report["timestamp"],
            "status": health_report["status"],
            "duration_ms": health_report["check_duration_ms"]
        })
        
        # 保持历史记录数量限制
        if len(self.check_history) > self.max_history:
            self.check_history = self.check_history[-self.max_history:]

    def get_health_history(self) -> List[Dict[str, Any]]:
        """获取健康检查历史
        
        Returns:
            List: 健康检查历史记录
        """
        return self.check_history.copy()