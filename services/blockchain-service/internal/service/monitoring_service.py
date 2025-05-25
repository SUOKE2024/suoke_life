#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
性能监控和健康检查服务

该模块提供系统性能监控、健康检查、指标收集和告警功能，
帮助运维人员及时发现和解决系统问题。
"""

import asyncio
import json
import logging
import psutil
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
import statistics
import threading

from internal.model.config import AppConfig


class HealthStatus(Enum):
    """健康状态枚举"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class MetricType(Enum):
    """指标类型枚举"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class HealthCheckResult:
    """健康检查结果"""
    component: str
    status: HealthStatus
    message: str
    timestamp: datetime
    response_time: float
    details: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['status'] = self.status.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class Metric:
    """指标数据类"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    labels: Dict[str, str] = None
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'name': self.name,
            'value': self.value,
            'type': self.metric_type.value,
            'timestamp': self.timestamp.isoformat(),
            'labels': self.labels
        }


class MonitoringService:
    """性能监控和健康检查服务"""

    def __init__(self, config: AppConfig):
        """
        初始化监控服务
        
        Args:
            config: 应用配置对象
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # 健康检查器注册表
        self.health_checkers: Dict[str, Callable] = {}
        
        # 指标存储
        self.metrics: Dict[str, List[Metric]] = {}
        self.metrics_lock = threading.Lock()
        
        # 健康检查结果
        self.health_results: Dict[str, HealthCheckResult] = {}
        
        # 监控配置
        self.health_check_interval = 30  # 秒
        self.metrics_retention_hours = 24  # 小时
        self.max_metrics_per_name = 1000
        
        # 监控状态
        self.is_running = False
        self.monitoring_tasks: List[asyncio.Task] = []
        
        # 系统指标收集器
        self.system_metrics_enabled = True
        
        # 告警配置
        self.alert_thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'disk_usage': 90.0,
            'response_time': 5.0,
            'error_rate': 0.1
        }
        
        # 注册默认健康检查器
        self._register_default_health_checkers()
        
        self.logger.info("监控服务初始化完成")
    
    def register_health_checker(self, component: str, checker: Callable):
        """
        注册健康检查器
        
        Args:
            component: 组件名称
            checker: 健康检查函数
        """
        self.health_checkers[component] = checker
        self.logger.info(f"注册健康检查器: {component}")
    
    def record_metric(
        self,
        name: str,
        value: float,
        metric_type: MetricType = MetricType.GAUGE,
        labels: Dict[str, str] = None
    ):
        """
        记录指标
        
        Args:
            name: 指标名称
            value: 指标值
            metric_type: 指标类型
            labels: 标签
        """
        metric = Metric(
            name=name,
            value=value,
            metric_type=metric_type,
            timestamp=datetime.now(),
            labels=labels or {}
        )
        
        with self.metrics_lock:
            if name not in self.metrics:
                self.metrics[name] = []
            
            self.metrics[name].append(metric)
            
            # 限制指标数量
            if len(self.metrics[name]) > self.max_metrics_per_name:
                self.metrics[name] = self.metrics[name][-self.max_metrics_per_name:]
    
    def increment_counter(self, name: str, value: float = 1.0, labels: Dict[str, str] = None):
        """
        递增计数器
        
        Args:
            name: 计数器名称
            value: 递增值
            labels: 标签
        """
        self.record_metric(name, value, MetricType.COUNTER, labels)
    
    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """
        设置仪表盘指标
        
        Args:
            name: 指标名称
            value: 指标值
            labels: 标签
        """
        self.record_metric(name, value, MetricType.GAUGE, labels)
    
    def record_histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """
        记录直方图指标
        
        Args:
            name: 指标名称
            value: 指标值
            labels: 标签
        """
        self.record_metric(name, value, MetricType.HISTOGRAM, labels)
    
    async def start_monitoring(self):
        """启动监控"""
        if self.is_running:
            self.logger.warning("监控服务已在运行")
            return
        
        self.is_running = True
        
        # 启动健康检查任务
        health_check_task = asyncio.create_task(
            self._health_check_loop(),
            name="health_check_loop"
        )
        self.monitoring_tasks.append(health_check_task)
        
        # 启动系统指标收集任务
        if self.system_metrics_enabled:
            system_metrics_task = asyncio.create_task(
                self._system_metrics_loop(),
                name="system_metrics_loop"
            )
            self.monitoring_tasks.append(system_metrics_task)
        
        # 启动指标清理任务
        cleanup_task = asyncio.create_task(
            self._metrics_cleanup_loop(),
            name="metrics_cleanup_loop"
        )
        self.monitoring_tasks.append(cleanup_task)
        
        self.logger.info("监控服务已启动")
    
    async def stop_monitoring(self):
        """停止监控"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # 取消所有监控任务
        for task in self.monitoring_tasks:
            task.cancel()
        
        # 等待所有任务完成
        await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
        
        self.monitoring_tasks.clear()
        self.logger.info("监控服务已停止")
    
    async def _health_check_loop(self):
        """健康检查循环"""
        while self.is_running:
            try:
                await self._run_all_health_checks()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"健康检查循环错误: {str(e)}")
                await asyncio.sleep(5)
    
    async def _run_all_health_checks(self):
        """运行所有健康检查"""
        for component, checker in self.health_checkers.items():
            try:
                start_time = time.time()
                
                # 执行健康检查
                if asyncio.iscoroutinefunction(checker):
                    result = await checker()
                else:
                    result = checker()
                
                response_time = time.time() - start_time
                
                # 处理检查结果
                if isinstance(result, dict):
                    status = HealthStatus(result.get('status', 'unknown'))
                    message = result.get('message', 'No message')
                    details = result.get('details', {})
                else:
                    status = HealthStatus.HEALTHY if result else HealthStatus.CRITICAL
                    message = "Health check passed" if result else "Health check failed"
                    details = {}
                
                # 记录结果
                health_result = HealthCheckResult(
                    component=component,
                    status=status,
                    message=message,
                    timestamp=datetime.now(),
                    response_time=response_time,
                    details=details
                )
                
                self.health_results[component] = health_result
                
                # 记录响应时间指标
                self.record_histogram(
                    f"health_check_response_time",
                    response_time,
                    {"component": component}
                )
                
                # 记录状态指标
                status_value = 1 if status == HealthStatus.HEALTHY else 0
                self.set_gauge(
                    f"health_check_status",
                    status_value,
                    {"component": component}
                )
                
            except Exception as e:
                # 健康检查失败
                error_result = HealthCheckResult(
                    component=component,
                    status=HealthStatus.CRITICAL,
                    message=f"Health check error: {str(e)}",
                    timestamp=datetime.now(),
                    response_time=0.0
                )
                
                self.health_results[component] = error_result
                self.logger.error(f"健康检查失败 {component}: {str(e)}")
    
    async def _system_metrics_loop(self):
        """系统指标收集循环"""
        while self.is_running:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(10)  # 每10秒收集一次
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"系统指标收集错误: {str(e)}")
                await asyncio.sleep(5)
    
    async def _collect_system_metrics(self):
        """收集系统指标"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            self.set_gauge("system_cpu_usage_percent", cpu_percent)
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            self.set_gauge("system_memory_usage_percent", memory.percent)
            self.set_gauge("system_memory_used_bytes", memory.used)
            self.set_gauge("system_memory_available_bytes", memory.available)
            
            # 磁盘使用情况
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.set_gauge("system_disk_usage_percent", disk_percent)
            self.set_gauge("system_disk_used_bytes", disk.used)
            self.set_gauge("system_disk_free_bytes", disk.free)
            
            # 网络IO
            net_io = psutil.net_io_counters()
            self.set_gauge("system_network_bytes_sent", net_io.bytes_sent)
            self.set_gauge("system_network_bytes_recv", net_io.bytes_recv)
            
            # 进程信息
            process = psutil.Process()
            self.set_gauge("process_cpu_percent", process.cpu_percent())
            self.set_gauge("process_memory_percent", process.memory_percent())
            self.set_gauge("process_memory_rss_bytes", process.memory_info().rss)
            self.set_gauge("process_num_threads", process.num_threads())
            
            # 检查告警阈值
            self._check_alert_thresholds(cpu_percent, memory.percent, disk_percent)
            
        except Exception as e:
            self.logger.error(f"收集系统指标失败: {str(e)}")
    
    def _check_alert_thresholds(self, cpu_percent: float, memory_percent: float, disk_percent: float):
        """
        检查告警阈值
        
        Args:
            cpu_percent: CPU使用率
            memory_percent: 内存使用率
            disk_percent: 磁盘使用率
        """
        alerts = []
        
        if cpu_percent > self.alert_thresholds['cpu_usage']:
            alerts.append(f"CPU使用率过高: {cpu_percent:.1f}%")
        
        if memory_percent > self.alert_thresholds['memory_usage']:
            alerts.append(f"内存使用率过高: {memory_percent:.1f}%")
        
        if disk_percent > self.alert_thresholds['disk_usage']:
            alerts.append(f"磁盘使用率过高: {disk_percent:.1f}%")
        
        for alert in alerts:
            self.logger.warning(f"系统告警: {alert}")
            self.increment_counter("system_alerts_total", labels={"type": "threshold"})
    
    async def _metrics_cleanup_loop(self):
        """指标清理循环"""
        while self.is_running:
            try:
                await asyncio.sleep(3600)  # 每小时清理一次
                self._cleanup_old_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"指标清理错误: {str(e)}")
    
    def _cleanup_old_metrics(self):
        """清理过期指标"""
        cutoff_time = datetime.now() - timedelta(hours=self.metrics_retention_hours)
        
        with self.metrics_lock:
            for metric_name, metric_list in self.metrics.items():
                # 过滤掉过期的指标
                self.metrics[metric_name] = [
                    metric for metric in metric_list
                    if metric.timestamp > cutoff_time
                ]
        
        self.logger.debug("完成指标清理")
    
    def _register_default_health_checkers(self):
        """注册默认健康检查器"""
        
        def check_system_resources():
            """检查系统资源"""
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_percent = psutil.virtual_memory().percent
                disk_percent = psutil.disk_usage('/').percent
                
                if cpu_percent > 90 or memory_percent > 95 or disk_percent > 95:
                    return {
                        'status': 'critical',
                        'message': f'System resources critical: CPU={cpu_percent:.1f}%, Memory={memory_percent:.1f}%, Disk={disk_percent:.1f}%',
                        'details': {
                            'cpu_percent': cpu_percent,
                            'memory_percent': memory_percent,
                            'disk_percent': disk_percent
                        }
                    }
                elif cpu_percent > 80 or memory_percent > 85 or disk_percent > 90:
                    return {
                        'status': 'warning',
                        'message': f'System resources warning: CPU={cpu_percent:.1f}%, Memory={memory_percent:.1f}%, Disk={disk_percent:.1f}%',
                        'details': {
                            'cpu_percent': cpu_percent,
                            'memory_percent': memory_percent,
                            'disk_percent': disk_percent
                        }
                    }
                else:
                    return {
                        'status': 'healthy',
                        'message': 'System resources normal',
                        'details': {
                            'cpu_percent': cpu_percent,
                            'memory_percent': memory_percent,
                            'disk_percent': disk_percent
                        }
                    }
            except Exception as e:
                return {
                    'status': 'unknown',
                    'message': f'Failed to check system resources: {str(e)}'
                }
        
        def check_process_health():
            """检查进程健康状态"""
            try:
                process = psutil.Process()
                
                # 检查进程状态
                if process.status() != psutil.STATUS_RUNNING:
                    return {
                        'status': 'critical',
                        'message': f'Process not running: {process.status()}'
                    }
                
                # 检查内存泄漏
                memory_percent = process.memory_percent()
                if memory_percent > 50:  # 超过50%内存使用
                    return {
                        'status': 'warning',
                        'message': f'High memory usage: {memory_percent:.1f}%',
                        'details': {'memory_percent': memory_percent}
                    }
                
                return {
                    'status': 'healthy',
                    'message': 'Process healthy',
                    'details': {
                        'memory_percent': memory_percent,
                        'num_threads': process.num_threads()
                    }
                }
            except Exception as e:
                return {
                    'status': 'unknown',
                    'message': f'Failed to check process health: {str(e)}'
                }
        
        # 注册默认检查器
        self.register_health_checker("system_resources", check_system_resources)
        self.register_health_checker("process_health", check_process_health)
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        获取整体健康状态
        
        Returns:
            健康状态信息
        """
        if not self.health_results:
            return {
                'overall_status': 'unknown',
                'message': 'No health checks performed yet',
                'components': {},
                'timestamp': datetime.now().isoformat()
            }
        
        # 计算整体状态
        statuses = [result.status for result in self.health_results.values()]
        
        if HealthStatus.CRITICAL in statuses:
            overall_status = HealthStatus.CRITICAL
        elif HealthStatus.WARNING in statuses:
            overall_status = HealthStatus.WARNING
        elif HealthStatus.UNKNOWN in statuses:
            overall_status = HealthStatus.UNKNOWN
        else:
            overall_status = HealthStatus.HEALTHY
        
        # 构建响应
        components = {}
        for component, result in self.health_results.items():
            components[component] = result.to_dict()
        
        return {
            'overall_status': overall_status.value,
            'message': f'System status: {overall_status.value}',
            'components': components,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_metrics_summary(self, metric_name: str = None) -> Dict[str, Any]:
        """
        获取指标摘要
        
        Args:
            metric_name: 指定的指标名称，如果为None则返回所有指标
            
        Returns:
            指标摘要信息
        """
        with self.metrics_lock:
            if metric_name:
                if metric_name not in self.metrics:
                    return {}
                
                metrics = self.metrics[metric_name]
                if not metrics:
                    return {}
                
                values = [m.value for m in metrics]
                return {
                    'name': metric_name,
                    'count': len(values),
                    'latest_value': values[-1],
                    'min_value': min(values),
                    'max_value': max(values),
                    'avg_value': statistics.mean(values),
                    'latest_timestamp': metrics[-1].timestamp.isoformat()
                }
            else:
                summary = {}
                for name, metric_list in self.metrics.items():
                    if metric_list:
                        values = [m.value for m in metric_list]
                        summary[name] = {
                            'count': len(values),
                            'latest_value': values[-1],
                            'min_value': min(values),
                            'max_value': max(values),
                            'avg_value': statistics.mean(values),
                            'latest_timestamp': metric_list[-1].timestamp.isoformat()
                        }
                
                return summary
    
    def get_metrics_data(
        self,
        metric_name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        获取指标数据
        
        Args:
            metric_name: 指标名称
            start_time: 开始时间
            end_time: 结束时间
            limit: 返回数据点数量限制
            
        Returns:
            指标数据列表
        """
        with self.metrics_lock:
            if metric_name not in self.metrics:
                return []
            
            metrics = self.metrics[metric_name]
            
            # 时间过滤
            if start_time or end_time:
                filtered_metrics = []
                for metric in metrics:
                    if start_time and metric.timestamp < start_time:
                        continue
                    if end_time and metric.timestamp > end_time:
                        continue
                    filtered_metrics.append(metric)
                metrics = filtered_metrics
            
            # 限制数量
            if len(metrics) > limit:
                metrics = metrics[-limit:]
            
            return [metric.to_dict() for metric in metrics]
    
    def set_alert_threshold(self, metric_name: str, threshold: float):
        """
        设置告警阈值
        
        Args:
            metric_name: 指标名称
            threshold: 阈值
        """
        self.alert_thresholds[metric_name] = threshold
        self.logger.info(f"设置告警阈值: {metric_name} = {threshold}")
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """
        获取监控统计信息
        
        Returns:
            监控统计信息
        """
        with self.metrics_lock:
            total_metrics = sum(len(metric_list) for metric_list in self.metrics.values())
            
            return {
                'is_running': self.is_running,
                'health_checkers_count': len(self.health_checkers),
                'health_results_count': len(self.health_results),
                'metrics_names_count': len(self.metrics),
                'total_metrics_count': total_metrics,
                'alert_thresholds': self.alert_thresholds.copy(),
                'system_metrics_enabled': self.system_metrics_enabled,
                'health_check_interval': self.health_check_interval,
                'metrics_retention_hours': self.metrics_retention_hours
            } 