#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
性能监控和健康检查系统

提供服务性能监控、健康检查和指标收集功能。
"""

import time
import psutil
import logging
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """性能指标"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_usage_percent: float
    network_io: Dict[str, int] = field(default_factory=dict)
    process_count: int = 0
    response_time_ms: float = 0.0


@dataclass
class HealthStatus:
    """健康状态"""
    status: str  # healthy, degraded, unhealthy
    timestamp: float
    checks: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, max_history: int = 1000):
        """
        初始化性能监控器
        
        Args:
            max_history: 最大历史记录数量
        """
        self.max_history = max_history
        self.metrics_history = deque(maxlen=max_history)
        self.request_times = deque(maxlen=max_history)
        self.error_counts = defaultdict(int)
        self.start_time = time.time()
        
        # 性能阈值
        self.thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_usage_percent": 90.0,
            "response_time_ms": 5000.0
        }
        
        logger.info("性能监控器初始化完成")
    
    def collect_metrics(self) -> PerformanceMetrics:
        """收集系统性能指标"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / (1024 * 1024)
            
            # 磁盘使用情况
            disk = psutil.disk_usage('/')
            disk_usage_percent = disk.percent
            
            # 网络IO
            network_io = psutil.net_io_counters()._asdict()
            
            # 进程数量
            process_count = len(psutil.pids())
            
            # 平均响应时间
            avg_response_time = self.get_average_response_time()
            
            metrics = PerformanceMetrics(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_mb=memory_used_mb,
                disk_usage_percent=disk_usage_percent,
                network_io=network_io,
                process_count=process_count,
                response_time_ms=avg_response_time
            )
            
            # 添加到历史记录
            self.metrics_history.append(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"收集性能指标失败: {str(e)}")
            return PerformanceMetrics(
                timestamp=time.time(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_mb=0.0,
                disk_usage_percent=0.0
            )
    
    def record_request_time(self, response_time: float):
        """记录请求响应时间"""
        self.request_times.append(response_time * 1000)  # 转换为毫秒
    
    def record_error(self, error_type: str):
        """记录错误"""
        self.error_counts[error_type] += 1
    
    def get_average_response_time(self) -> float:
        """获取平均响应时间（毫秒）"""
        if not self.request_times:
            return 0.0
        return sum(self.request_times) / len(self.request_times)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        if not self.metrics_history:
            return {"error": "暂无性能数据"}
        
        latest_metrics = self.metrics_history[-1]
        
        # 计算平均值（最近10个数据点）
        recent_metrics = list(self.metrics_history)[-10:]
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        
        return {
            "current": {
                "cpu_percent": latest_metrics.cpu_percent,
                "memory_percent": latest_metrics.memory_percent,
                "memory_used_mb": latest_metrics.memory_used_mb,
                "disk_usage_percent": latest_metrics.disk_usage_percent,
                "response_time_ms": latest_metrics.response_time_ms,
                "process_count": latest_metrics.process_count
            },
            "averages": {
                "cpu_percent": round(avg_cpu, 2),
                "memory_percent": round(avg_memory, 2),
                "response_time_ms": round(self.get_average_response_time(), 2)
            },
            "uptime_seconds": time.time() - self.start_time,
            "error_counts": dict(self.error_counts),
            "thresholds": self.thresholds
        }
    
    def check_performance_health(self) -> Dict[str, Any]:
        """检查性能健康状态"""
        if not self.metrics_history:
            return {"status": "unknown", "message": "暂无性能数据"}
        
        latest_metrics = self.metrics_history[-1]
        issues = []
        warnings = []
        
        # 检查CPU使用率
        if latest_metrics.cpu_percent > self.thresholds["cpu_percent"]:
            issues.append(f"CPU使用率过高: {latest_metrics.cpu_percent:.1f}%")
        elif latest_metrics.cpu_percent > self.thresholds["cpu_percent"] * 0.8:
            warnings.append(f"CPU使用率较高: {latest_metrics.cpu_percent:.1f}%")
        
        # 检查内存使用率
        if latest_metrics.memory_percent > self.thresholds["memory_percent"]:
            issues.append(f"内存使用率过高: {latest_metrics.memory_percent:.1f}%")
        elif latest_metrics.memory_percent > self.thresholds["memory_percent"] * 0.8:
            warnings.append(f"内存使用率较高: {latest_metrics.memory_percent:.1f}%")
        
        # 检查磁盘使用率
        if latest_metrics.disk_usage_percent > self.thresholds["disk_usage_percent"]:
            issues.append(f"磁盘使用率过高: {latest_metrics.disk_usage_percent:.1f}%")
        
        # 检查响应时间
        if latest_metrics.response_time_ms > self.thresholds["response_time_ms"]:
            issues.append(f"响应时间过长: {latest_metrics.response_time_ms:.1f}ms")
        
        # 确定整体状态
        if issues:
            status = "unhealthy"
        elif warnings:
            status = "degraded"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "issues": issues,
            "warnings": warnings,
            "metrics": {
                "cpu_percent": latest_metrics.cpu_percent,
                "memory_percent": latest_metrics.memory_percent,
                "disk_usage_percent": latest_metrics.disk_usage_percent,
                "response_time_ms": latest_metrics.response_time_ms
            }
        }


class HealthChecker:
    """健康检查器"""
    
    def __init__(self, performance_monitor: PerformanceMonitor):
        """
        初始化健康检查器
        
        Args:
            performance_monitor: 性能监控器实例
        """
        self.performance_monitor = performance_monitor
        self.health_history = deque(maxlen=100)
        self.last_check_time = 0
        self.check_interval = 30  # 30秒检查一次
        
        logger.info("健康检查器初始化完成")
    
    async def perform_health_check(self, service_instance=None) -> HealthStatus:
        """执行健康检查"""
        try:
            current_time = time.time()
            checks = {}
            errors = []
            warnings = []
            
            # 性能检查
            perf_health = self.performance_monitor.check_performance_health()
            checks["performance"] = perf_health
            
            if perf_health["status"] == "unhealthy":
                errors.extend(perf_health.get("issues", []))
            elif perf_health["status"] == "degraded":
                warnings.extend(perf_health.get("warnings", []))
            
            # 服务实例检查
            if service_instance:
                try:
                    service_status = service_instance.get_service_status()
                    checks["service"] = service_status
                    
                    # 检查服务是否运行
                    if not service_status.get("service", {}).get("running", False):
                        errors.append("服务未运行")
                    
                    # 检查模块状态
                    modules = service_status.get("modules", {})
                    enabled_count = sum(1 for m in modules.values() if m.get("enabled", False))
                    if enabled_count == 0:
                        warnings.append("没有启用任何模块")
                    
                except Exception as e:
                    errors.append(f"服务状态检查失败: {str(e)}")
            
            # 磁盘空间检查
            try:
                disk_usage = psutil.disk_usage('/')
                free_gb = disk_usage.free / (1024**3)
                if free_gb < 1.0:  # 少于1GB
                    errors.append(f"磁盘空间不足: {free_gb:.1f}GB")
                elif free_gb < 5.0:  # 少于5GB
                    warnings.append(f"磁盘空间较少: {free_gb:.1f}GB")
                
                checks["disk_space"] = {
                    "free_gb": round(free_gb, 1),
                    "total_gb": round(disk_usage.total / (1024**3), 1),
                    "used_percent": round(disk_usage.percent, 1)
                }
            except Exception as e:
                warnings.append(f"磁盘空间检查失败: {str(e)}")
            
            # 网络连接检查
            try:
                network_connections = len(psutil.net_connections())
                checks["network"] = {
                    "connections": network_connections,
                    "status": "normal" if network_connections < 1000 else "high"
                }
                
                if network_connections > 1000:
                    warnings.append(f"网络连接数较多: {network_connections}")
            except Exception as e:
                warnings.append(f"网络检查失败: {str(e)}")
            
            # 确定整体健康状态
            if errors:
                overall_status = "unhealthy"
            elif warnings:
                overall_status = "degraded"
            else:
                overall_status = "healthy"
            
            health_status = HealthStatus(
                status=overall_status,
                timestamp=current_time,
                checks=checks,
                errors=errors,
                warnings=warnings
            )
            
            # 添加到历史记录
            self.health_history.append(health_status)
            self.last_check_time = current_time
            
            return health_status
            
        except Exception as e:
            logger.error(f"健康检查失败: {str(e)}")
            return HealthStatus(
                status="unhealthy",
                timestamp=time.time(),
                errors=[f"健康检查失败: {str(e)}"]
            )
    
    def get_health_summary(self) -> Dict[str, Any]:
        """获取健康状态摘要"""
        if not self.health_history:
            return {"status": "unknown", "message": "暂无健康检查数据"}
        
        latest_health = self.health_history[-1]
        
        # 统计最近的健康状态
        recent_checks = list(self.health_history)[-10:]
        status_counts = defaultdict(int)
        for check in recent_checks:
            status_counts[check.status] += 1
        
        return {
            "current_status": latest_health.status,
            "last_check_time": latest_health.timestamp,
            "checks": latest_health.checks,
            "errors": latest_health.errors,
            "warnings": latest_health.warnings,
            "recent_status_distribution": dict(status_counts),
            "check_interval": self.check_interval
        }
    
    def should_check_now(self) -> bool:
        """判断是否应该进行健康检查"""
        return time.time() - self.last_check_time >= self.check_interval


class MonitoringService:
    """监控服务"""
    
    def __init__(self):
        """初始化监控服务"""
        self.performance_monitor = PerformanceMonitor()
        self.health_checker = HealthChecker(self.performance_monitor)
        self._monitoring_task = None
        self._running = False
        
        logger.info("监控服务初始化完成")
    
    async def start_monitoring(self, service_instance=None):
        """启动监控"""
        if self._running:
            logger.warning("监控服务已在运行")
            return
        
        self._running = True
        self._monitoring_task = asyncio.create_task(
            self._monitoring_loop(service_instance)
        )
        logger.info("监控服务已启动")
    
    async def stop_monitoring(self):
        """停止监控"""
        if not self._running:
            return
        
        self._running = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("监控服务已停止")
    
    async def _monitoring_loop(self, service_instance=None):
        """监控循环"""
        try:
            while self._running:
                # 收集性能指标
                self.performance_monitor.collect_metrics()
                
                # 执行健康检查
                if self.health_checker.should_check_now():
                    await self.health_checker.perform_health_check(service_instance)
                
                # 等待下一次检查
                await asyncio.sleep(10)  # 每10秒收集一次指标
                
        except asyncio.CancelledError:
            logger.info("监控循环已取消")
        except Exception as e:
            logger.error(f"监控循环异常: {str(e)}")
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """获取监控状态"""
        return {
            "monitoring_running": self._running,
            "performance": self.performance_monitor.get_performance_summary(),
            "health": self.health_checker.get_health_summary()
        }
    
    def record_request_metrics(self, response_time: float, success: bool, error_type: str = None):
        """记录请求指标"""
        self.performance_monitor.record_request_time(response_time)
        
        if not success and error_type:
            self.performance_monitor.record_error(error_type) 