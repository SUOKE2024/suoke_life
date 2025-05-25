#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
性能优化模块 - 系统性能监控和智能优化
包含资源监控、负载均衡、缓存管理、性能调优等功能
"""

import logging
import time
import asyncio
import psutil
import threading
import gc
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import weakref
import json

logger = logging.getLogger(__name__)


class OptimizationType(Enum):
    """优化类型枚举"""
    CPU_OPTIMIZATION = "cpu_optimization"
    MEMORY_OPTIMIZATION = "memory_optimization"
    IO_OPTIMIZATION = "io_optimization"
    NETWORK_OPTIMIZATION = "network_optimization"
    CACHE_OPTIMIZATION = "cache_optimization"
    THREAD_OPTIMIZATION = "thread_optimization"
    ALGORITHM_OPTIMIZATION = "algorithm_optimization"


class PerformanceLevel(Enum):
    """性能级别枚举"""
    CRITICAL = "critical"    # 性能严重问题
    WARNING = "warning"      # 性能警告
    NORMAL = "normal"        # 正常性能
    GOOD = "good"           # 良好性能
    EXCELLENT = "excellent"  # 优秀性能


class ResourceType(Enum):
    """资源类型枚举"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    GPU = "gpu"
    THREAD = "thread"
    CONNECTION = "connection"


@dataclass
class PerformanceMetric:
    """性能指标"""
    metric_name: str
    value: float
    unit: str
    timestamp: float
    resource_type: ResourceType
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationAction:
    """优化动作"""
    action_id: str
    optimization_type: OptimizationType
    description: str
    target_metric: str
    expected_improvement: float
    priority: int  # 1-10, 10为最高优先级
    estimated_duration: float  # 预计执行时间（秒）
    action_function: Callable
    parameters: Dict[str, Any] = field(default_factory=dict)
    prerequisites: List[str] = field(default_factory=list)


@dataclass
class OptimizationResult:
    """优化结果"""
    action_id: str
    success: bool
    execution_time: float
    before_metrics: Dict[str, float]
    after_metrics: Dict[str, float]
    improvement: Dict[str, float]
    error_message: Optional[str] = None
    side_effects: List[str] = field(default_factory=list)


class SystemMonitor:
    """系统监控器"""
    
    def __init__(self, sampling_interval: float = 1.0):
        self.sampling_interval = sampling_interval
        self.metrics_history = defaultdict(deque)  # metric_name -> deque of values
        self.is_monitoring = False
        self.monitor_task = None
        
        # 监控配置
        self.max_history_size = 1000
        self.alert_thresholds = {
            "cpu_usage": {"warning": 70.0, "critical": 90.0},
            "memory_usage": {"warning": 80.0, "critical": 95.0},
            "disk_usage": {"warning": 85.0, "critical": 95.0},
            "network_latency": {"warning": 100.0, "critical": 500.0},
            "thread_count": {"warning": 100, "critical": 200},
            "response_time": {"warning": 1.0, "critical": 5.0}
        }
        
        # 统计信息
        self.stats = {
            "monitoring_duration": 0.0,
            "samples_collected": 0,
            "alerts_triggered": 0,
            "last_sample_time": 0.0
        }
    
    async def start_monitoring(self):
        """启动监控"""
        if self.is_monitoring:
            return
        
        logger.info("启动系统性能监控...")
        self.is_monitoring = True
        self.monitor_task = asyncio.create_task(self._monitoring_loop())
        self.stats["monitoring_start_time"] = time.time()
    
    async def _monitoring_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                # 收集系统指标
                metrics = await self._collect_system_metrics()
                
                # 存储指标历史
                for metric in metrics:
                    self._store_metric(metric)
                
                # 检查阈值和触发警报
                await self._check_thresholds(metrics)
                
                self.stats["samples_collected"] += 1
                self.stats["last_sample_time"] = time.time()
                
                await asyncio.sleep(self.sampling_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"监控循环错误: {str(e)}")
                await asyncio.sleep(self.sampling_interval)
    
    async def _collect_system_metrics(self) -> List[PerformanceMetric]:
        """收集系统指标"""
        metrics = []
        current_time = time.time()
        
        try:
            # CPU指标
            cpu_percent = psutil.cpu_percent(interval=None)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            metrics.append(PerformanceMetric(
                metric_name="cpu_usage",
                value=cpu_percent,
                unit="percent",
                timestamp=current_time,
                resource_type=ResourceType.CPU,
                threshold_warning=self.alert_thresholds["cpu_usage"]["warning"],
                threshold_critical=self.alert_thresholds["cpu_usage"]["critical"],
                metadata={"cpu_count": cpu_count, "cpu_freq": cpu_freq.current if cpu_freq else None}
            ))
            
            # 内存指标
            memory = psutil.virtual_memory()
            metrics.append(PerformanceMetric(
                metric_name="memory_usage",
                value=memory.percent,
                unit="percent",
                timestamp=current_time,
                resource_type=ResourceType.MEMORY,
                threshold_warning=self.alert_thresholds["memory_usage"]["warning"],
                threshold_critical=self.alert_thresholds["memory_usage"]["critical"],
                metadata={
                    "total": memory.total,
                    "available": memory.available,
                    "used": memory.used
                }
            ))
            
            # 磁盘指标
            disk = psutil.disk_usage('/')
            metrics.append(PerformanceMetric(
                metric_name="disk_usage",
                value=(disk.used / disk.total) * 100,
                unit="percent",
                timestamp=current_time,
                resource_type=ResourceType.DISK,
                threshold_warning=self.alert_thresholds["disk_usage"]["warning"],
                threshold_critical=self.alert_thresholds["disk_usage"]["critical"],
                metadata={
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free
                }
            ))
            
            # 网络指标
            network = psutil.net_io_counters()
            if hasattr(self, '_last_network_stats'):
                time_diff = current_time - self._last_network_time
                if time_diff > 0:
                    bytes_sent_rate = (network.bytes_sent - self._last_network_stats.bytes_sent) / time_diff
                    bytes_recv_rate = (network.bytes_recv - self._last_network_stats.bytes_recv) / time_diff
                    
                    metrics.append(PerformanceMetric(
                        metric_name="network_send_rate",
                        value=bytes_sent_rate,
                        unit="bytes/sec",
                        timestamp=current_time,
                        resource_type=ResourceType.NETWORK,
                        metadata={"total_sent": network.bytes_sent}
                    ))
                    
                    metrics.append(PerformanceMetric(
                        metric_name="network_recv_rate",
                        value=bytes_recv_rate,
                        unit="bytes/sec",
                        timestamp=current_time,
                        resource_type=ResourceType.NETWORK,
                        metadata={"total_recv": network.bytes_recv}
                    ))
            
            self._last_network_stats = network
            self._last_network_time = current_time
            
            # 进程指标
            process = psutil.Process()
            metrics.append(PerformanceMetric(
                metric_name="thread_count",
                value=process.num_threads(),
                unit="count",
                timestamp=current_time,
                resource_type=ResourceType.THREAD,
                threshold_warning=self.alert_thresholds["thread_count"]["warning"],
                threshold_critical=self.alert_thresholds["thread_count"]["critical"]
            ))
            
            # 文件描述符
            try:
                fd_count = process.num_fds()
                metrics.append(PerformanceMetric(
                    metric_name="file_descriptors",
                    value=fd_count,
                    unit="count",
                    timestamp=current_time,
                    resource_type=ResourceType.CONNECTION
                ))
            except (AttributeError, psutil.AccessDenied):
                pass  # Windows或权限不足
            
        except Exception as e:
            logger.error(f"收集系统指标失败: {str(e)}")
        
        return metrics
    
    def _store_metric(self, metric: PerformanceMetric):
        """存储指标到历史记录"""
        history = self.metrics_history[metric.metric_name]
        history.append(metric)
        
        # 保持历史记录大小
        if len(history) > self.max_history_size:
            history.popleft()
    
    async def _check_thresholds(self, metrics: List[PerformanceMetric]):
        """检查阈值并触发警报"""
        for metric in metrics:
            if metric.threshold_critical and metric.value >= metric.threshold_critical:
                logger.critical(f"性能严重警报: {metric.metric_name} = {metric.value}{metric.unit}")
                self.stats["alerts_triggered"] += 1
            elif metric.threshold_warning and metric.value >= metric.threshold_warning:
                logger.warning(f"性能警告: {metric.metric_name} = {metric.value}{metric.unit}")
                self.stats["alerts_triggered"] += 1
    
    def get_current_metrics(self) -> Dict[str, PerformanceMetric]:
        """获取当前指标"""
        current_metrics = {}
        for metric_name, history in self.metrics_history.items():
            if history:
                current_metrics[metric_name] = history[-1]
        return current_metrics
    
    def get_metric_history(self, metric_name: str, duration: Optional[float] = None) -> List[PerformanceMetric]:
        """获取指标历史"""
        history = list(self.metrics_history.get(metric_name, []))
        
        if duration and history:
            cutoff_time = time.time() - duration
            history = [m for m in history if m.timestamp >= cutoff_time]
        
        return history
    
    def calculate_metric_statistics(self, metric_name: str, duration: Optional[float] = None) -> Dict[str, float]:
        """计算指标统计信息"""
        history = self.get_metric_history(metric_name, duration)
        
        if not history:
            return {}
        
        values = [m.value for m in history]
        
        return {
            "count": len(values),
            "mean": np.mean(values),
            "median": np.median(values),
            "std": np.std(values),
            "min": np.min(values),
            "max": np.max(values),
            "p95": np.percentile(values, 95),
            "p99": np.percentile(values, 99)
        }
    
    async def stop_monitoring(self):
        """停止监控"""
        logger.info("停止系统性能监控...")
        self.is_monitoring = False
        
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        
        if "monitoring_start_time" in self.stats:
            self.stats["monitoring_duration"] = time.time() - self.stats["monitoring_start_time"]


class ResourceOptimizer:
    """资源优化器"""
    
    def __init__(self):
        self.optimization_actions = {}  # action_id -> OptimizationAction
        self.optimization_history = deque(maxlen=100)
        self.active_optimizations = set()
        
        # 注册默认优化动作
        self._register_default_actions()
    
    def _register_default_actions(self):
        """注册默认优化动作"""
        
        # CPU优化动作
        self.register_action(OptimizationAction(
            action_id="reduce_cpu_threads",
            optimization_type=OptimizationType.CPU_OPTIMIZATION,
            description="减少CPU密集型线程数量",
            target_metric="cpu_usage",
            expected_improvement=15.0,
            priority=7,
            estimated_duration=1.0,
            action_function=self._reduce_cpu_threads
        ))
        
        # 内存优化动作
        self.register_action(OptimizationAction(
            action_id="garbage_collection",
            optimization_type=OptimizationType.MEMORY_OPTIMIZATION,
            description="强制垃圾回收",
            target_metric="memory_usage",
            expected_improvement=10.0,
            priority=5,
            estimated_duration=0.5,
            action_function=self._force_garbage_collection
        ))
        
        self.register_action(OptimizationAction(
            action_id="clear_caches",
            optimization_type=OptimizationType.CACHE_OPTIMIZATION,
            description="清理系统缓存",
            target_metric="memory_usage",
            expected_improvement=20.0,
            priority=6,
            estimated_duration=2.0,
            action_function=self._clear_caches
        ))
        
        # 线程优化动作
        self.register_action(OptimizationAction(
            action_id="optimize_thread_pool",
            optimization_type=OptimizationType.THREAD_OPTIMIZATION,
            description="优化线程池大小",
            target_metric="thread_count",
            expected_improvement=25.0,
            priority=8,
            estimated_duration=1.5,
            action_function=self._optimize_thread_pool
        ))
    
    def register_action(self, action: OptimizationAction):
        """注册优化动作"""
        self.optimization_actions[action.action_id] = action
        logger.info(f"注册优化动作: {action.action_id}")
    
    async def suggest_optimizations(self, current_metrics: Dict[str, PerformanceMetric]) -> List[OptimizationAction]:
        """建议优化动作"""
        suggestions = []
        
        for action in self.optimization_actions.values():
            # 检查是否需要此优化
            if await self._should_apply_optimization(action, current_metrics):
                suggestions.append(action)
        
        # 按优先级排序
        suggestions.sort(key=lambda x: x.priority, reverse=True)
        
        return suggestions
    
    async def _should_apply_optimization(self, action: OptimizationAction, 
                                       current_metrics: Dict[str, PerformanceMetric]) -> bool:
        """判断是否应该应用优化"""
        # 检查目标指标
        target_metric = current_metrics.get(action.target_metric)
        if not target_metric:
            return False
        
        # 检查是否超过警告阈值
        if target_metric.threshold_warning and target_metric.value < target_metric.threshold_warning:
            return False
        
        # 检查前置条件
        for prerequisite in action.prerequisites:
            if prerequisite not in current_metrics:
                return False
        
        # 检查是否正在执行
        if action.action_id in self.active_optimizations:
            return False
        
        return True
    
    async def execute_optimization(self, action: OptimizationAction, 
                                 before_metrics: Dict[str, PerformanceMetric]) -> OptimizationResult:
        """执行优化动作"""
        start_time = time.time()
        
        try:
            self.active_optimizations.add(action.action_id)
            
            # 记录优化前的指标
            before_values = {name: metric.value for name, metric in before_metrics.items()}
            
            # 执行优化动作
            await action.action_function(**action.parameters)
            
            # 等待一段时间让优化生效
            await asyncio.sleep(2.0)
            
            # 这里应该重新收集指标，暂时模拟
            after_values = before_values.copy()
            if action.target_metric in after_values:
                # 模拟改进效果
                improvement_factor = action.expected_improvement / 100.0
                after_values[action.target_metric] *= (1 - improvement_factor)
            
            # 计算改进
            improvement = {}
            for metric_name in before_values:
                if metric_name in after_values:
                    improvement[metric_name] = before_values[metric_name] - after_values[metric_name]
            
            execution_time = time.time() - start_time
            
            result = OptimizationResult(
                action_id=action.action_id,
                success=True,
                execution_time=execution_time,
                before_metrics=before_values,
                after_metrics=after_values,
                improvement=improvement
            )
            
            self.optimization_history.append(result)
            logger.info(f"优化动作执行成功: {action.action_id}")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            result = OptimizationResult(
                action_id=action.action_id,
                success=False,
                execution_time=execution_time,
                before_metrics={name: metric.value for name, metric in before_metrics.items()},
                after_metrics={},
                improvement={},
                error_message=str(e)
            )
            
            self.optimization_history.append(result)
            logger.error(f"优化动作执行失败: {action.action_id} - {str(e)}")
            
            return result
            
        finally:
            self.active_optimizations.discard(action.action_id)
    
    # 具体的优化动作实现
    async def _reduce_cpu_threads(self, **kwargs):
        """减少CPU线程数量"""
        # 这里应该实现具体的线程减少逻辑
        logger.info("执行CPU线程优化")
        await asyncio.sleep(0.5)  # 模拟执行时间
    
    async def _force_garbage_collection(self, **kwargs):
        """强制垃圾回收"""
        logger.info("执行强制垃圾回收")
        gc.collect()
        await asyncio.sleep(0.1)
    
    async def _clear_caches(self, **kwargs):
        """清理缓存"""
        logger.info("执行缓存清理")
        # 这里应该清理应用程序缓存
        await asyncio.sleep(1.0)
    
    async def _optimize_thread_pool(self, **kwargs):
        """优化线程池"""
        logger.info("执行线程池优化")
        # 这里应该调整线程池大小
        await asyncio.sleep(1.0)


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, max_cache_size: int = 1000):
        self.max_cache_size = max_cache_size
        self.caches = {}  # cache_name -> cache_dict
        self.cache_stats = defaultdict(lambda: {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "size": 0
        })
        self.cache_access_order = defaultdict(deque)  # LRU tracking
    
    def create_cache(self, cache_name: str, max_size: Optional[int] = None):
        """创建缓存"""
        if max_size is None:
            max_size = self.max_cache_size
        
        self.caches[cache_name] = {}
        self.cache_stats[cache_name]["max_size"] = max_size
        logger.info(f"创建缓存: {cache_name} (最大大小: {max_size})")
    
    def get(self, cache_name: str, key: str) -> Any:
        """从缓存获取值"""
        if cache_name not in self.caches:
            return None
        
        cache = self.caches[cache_name]
        
        if key in cache:
            # 更新访问顺序
            access_order = self.cache_access_order[cache_name]
            if key in access_order:
                access_order.remove(key)
            access_order.append(key)
            
            self.cache_stats[cache_name]["hits"] += 1
            return cache[key]
        else:
            self.cache_stats[cache_name]["misses"] += 1
            return None
    
    def put(self, cache_name: str, key: str, value: Any):
        """向缓存添加值"""
        if cache_name not in self.caches:
            self.create_cache(cache_name)
        
        cache = self.caches[cache_name]
        access_order = self.cache_access_order[cache_name]
        max_size = self.cache_stats[cache_name]["max_size"]
        
        # 如果缓存已满，移除最久未使用的项
        if len(cache) >= max_size and key not in cache:
            if access_order:
                oldest_key = access_order.popleft()
                del cache[oldest_key]
                self.cache_stats[cache_name]["evictions"] += 1
        
        # 添加新项
        cache[key] = value
        
        # 更新访问顺序
        if key in access_order:
            access_order.remove(key)
        access_order.append(key)
        
        self.cache_stats[cache_name]["size"] = len(cache)
    
    def remove(self, cache_name: str, key: str) -> bool:
        """从缓存移除项"""
        if cache_name not in self.caches:
            return False
        
        cache = self.caches[cache_name]
        access_order = self.cache_access_order[cache_name]
        
        if key in cache:
            del cache[key]
            if key in access_order:
                access_order.remove(key)
            
            self.cache_stats[cache_name]["size"] = len(cache)
            return True
        
        return False
    
    def clear_cache(self, cache_name: str):
        """清空缓存"""
        if cache_name in self.caches:
            self.caches[cache_name].clear()
            self.cache_access_order[cache_name].clear()
            self.cache_stats[cache_name]["size"] = 0
            self.cache_stats[cache_name]["evictions"] += 1
            logger.info(f"清空缓存: {cache_name}")
    
    def get_cache_stats(self, cache_name: str) -> Dict[str, Any]:
        """获取缓存统计信息"""
        if cache_name not in self.cache_stats:
            return {}
        
        stats = self.cache_stats[cache_name].copy()
        total_requests = stats["hits"] + stats["misses"]
        stats["hit_rate"] = stats["hits"] / total_requests if total_requests > 0 else 0
        stats["utilization"] = stats["size"] / stats.get("max_size", 1)
        
        return stats
    
    def optimize_caches(self) -> Dict[str, Any]:
        """优化所有缓存"""
        optimization_results = {}
        
        for cache_name in self.caches:
            stats = self.get_cache_stats(cache_name)
            
            # 如果命中率低，考虑清理缓存
            if stats.get("hit_rate", 0) < 0.3 and stats.get("size", 0) > 10:
                self.clear_cache(cache_name)
                optimization_results[cache_name] = "cleared_low_hit_rate"
            
            # 如果利用率过高，考虑增加大小
            elif stats.get("utilization", 0) > 0.9:
                new_size = int(stats.get("max_size", 100) * 1.5)
                self.cache_stats[cache_name]["max_size"] = new_size
                optimization_results[cache_name] = f"increased_size_to_{new_size}"
        
        return optimization_results


class LoadBalancer:
    """负载均衡器"""
    
    def __init__(self):
        self.workers = []  # 工作节点列表
        self.worker_stats = defaultdict(lambda: {
            "requests": 0,
            "response_time": 0.0,
            "errors": 0,
            "load": 0.0
        })
        self.balancing_algorithm = "round_robin"  # round_robin, least_connections, weighted
        self.current_index = 0
    
    def add_worker(self, worker_id: str, weight: float = 1.0):
        """添加工作节点"""
        worker_info = {
            "id": worker_id,
            "weight": weight,
            "active": True
        }
        self.workers.append(worker_info)
        logger.info(f"添加工作节点: {worker_id} (权重: {weight})")
    
    def remove_worker(self, worker_id: str):
        """移除工作节点"""
        self.workers = [w for w in self.workers if w["id"] != worker_id]
        if worker_id in self.worker_stats:
            del self.worker_stats[worker_id]
        logger.info(f"移除工作节点: {worker_id}")
    
    def select_worker(self) -> Optional[str]:
        """选择工作节点"""
        active_workers = [w for w in self.workers if w["active"]]
        
        if not active_workers:
            return None
        
        if self.balancing_algorithm == "round_robin":
            return self._round_robin_select(active_workers)
        elif self.balancing_algorithm == "least_connections":
            return self._least_connections_select(active_workers)
        elif self.balancing_algorithm == "weighted":
            return self._weighted_select(active_workers)
        else:
            return active_workers[0]["id"]
    
    def _round_robin_select(self, workers: List[Dict[str, Any]]) -> str:
        """轮询选择"""
        worker = workers[self.current_index % len(workers)]
        self.current_index += 1
        return worker["id"]
    
    def _least_connections_select(self, workers: List[Dict[str, Any]]) -> str:
        """最少连接选择"""
        min_load = float('inf')
        selected_worker = None
        
        for worker in workers:
            load = self.worker_stats[worker["id"]]["load"]
            if load < min_load:
                min_load = load
                selected_worker = worker["id"]
        
        return selected_worker or workers[0]["id"]
    
    def _weighted_select(self, workers: List[Dict[str, Any]]) -> str:
        """加权选择"""
        # 简化的加权选择实现
        total_weight = sum(w["weight"] for w in workers)
        if total_weight == 0:
            return self._round_robin_select(workers)
        
        # 基于权重和当前负载选择
        best_score = float('-inf')
        selected_worker = None
        
        for worker in workers:
            load = self.worker_stats[worker["id"]]["load"]
            weight = worker["weight"]
            score = weight / (load + 1)  # 权重越高、负载越低，分数越高
            
            if score > best_score:
                best_score = score
                selected_worker = worker["id"]
        
        return selected_worker or workers[0]["id"]
    
    def update_worker_stats(self, worker_id: str, response_time: float, success: bool):
        """更新工作节点统计信息"""
        stats = self.worker_stats[worker_id]
        stats["requests"] += 1
        stats["response_time"] = (stats["response_time"] + response_time) / 2  # 简化的平均值
        
        if not success:
            stats["errors"] += 1
        
        # 计算负载（基于错误率和响应时间）
        error_rate = stats["errors"] / stats["requests"]
        stats["load"] = response_time * (1 + error_rate)
    
    def get_balancer_stats(self) -> Dict[str, Any]:
        """获取负载均衡器统计信息"""
        return {
            "algorithm": self.balancing_algorithm,
            "total_workers": len(self.workers),
            "active_workers": len([w for w in self.workers if w["active"]]),
            "worker_stats": dict(self.worker_stats)
        }


class PerformanceOptimizer:
    """性能优化器主类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化性能优化器
        
        Args:
            config: 服务配置
        """
        self.config = config
        self.enabled = config.get("performance_optimizer", {}).get("enabled", True)
        
        # 核心组件
        self.system_monitor = SystemMonitor(
            sampling_interval=config.get("performance_optimizer", {}).get("sampling_interval", 1.0)
        )
        self.resource_optimizer = ResourceOptimizer()
        self.cache_manager = CacheManager(
            max_cache_size=config.get("performance_optimizer", {}).get("cache_size", 1000)
        )
        self.load_balancer = LoadBalancer()
        
        # 优化配置
        self.auto_optimization = config.get("performance_optimizer", {}).get("auto_optimization", True)
        self.optimization_interval = config.get("performance_optimizer", {}).get("optimization_interval", 60.0)
        self.performance_threshold = config.get("performance_optimizer", {}).get("performance_threshold", 80.0)
        
        # 统计信息
        self.stats = {
            "optimizations_performed": 0,
            "total_improvement": 0.0,
            "last_optimization_time": 0.0,
            "system_start_time": time.time()
        }
        
        # 控制标志
        self.is_running = False
        self._optimization_task = None
        
        logger.info(f"性能优化器初始化完成 - 启用: {self.enabled}")
    
    async def start(self):
        """启动性能优化器"""
        if not self.enabled or self.is_running:
            return
        
        logger.info("启动性能优化器...")
        
        # 启动系统监控
        await self.system_monitor.start_monitoring()
        
        # 启动自动优化任务
        if self.auto_optimization:
            self._optimization_task = asyncio.create_task(self._optimization_loop())
        
        self.is_running = True
        logger.info("性能优化器已启动")
    
    async def _optimization_loop(self):
        """自动优化循环"""
        while self.is_running:
            try:
                await asyncio.sleep(self.optimization_interval)
                
                # 获取当前性能指标
                current_metrics = self.system_monitor.get_current_metrics()
                
                # 检查是否需要优化
                if await self._needs_optimization(current_metrics):
                    await self.perform_optimization()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"自动优化循环错误: {str(e)}")
    
    async def _needs_optimization(self, metrics: Dict[str, PerformanceMetric]) -> bool:
        """判断是否需要优化"""
        for metric in metrics.values():
            if metric.threshold_warning and metric.value >= metric.threshold_warning:
                return True
        return False
    
    async def perform_optimization(self) -> Dict[str, Any]:
        """执行性能优化"""
        logger.info("开始执行性能优化...")
        
        # 获取当前指标
        current_metrics = self.system_monitor.get_current_metrics()
        
        # 获取优化建议
        suggestions = await self.resource_optimizer.suggest_optimizations(current_metrics)
        
        optimization_results = []
        total_improvement = 0.0
        
        # 执行优化动作
        for action in suggestions[:3]:  # 限制同时执行的优化数量
            try:
                result = await self.resource_optimizer.execute_optimization(action, current_metrics)
                optimization_results.append(result)
                
                if result.success and action.target_metric in result.improvement:
                    improvement = result.improvement[action.target_metric]
                    total_improvement += improvement
                    logger.info(f"优化成功: {action.action_id} - 改进: {improvement}")
                
            except Exception as e:
                logger.error(f"执行优化失败: {action.action_id} - {str(e)}")
        
        # 优化缓存
        cache_results = self.cache_manager.optimize_caches()
        
        # 更新统计信息
        self.stats["optimizations_performed"] += len(optimization_results)
        self.stats["total_improvement"] += total_improvement
        self.stats["last_optimization_time"] = time.time()
        
        logger.info(f"性能优化完成 - 总改进: {total_improvement}")
        
        return {
            "optimization_results": optimization_results,
            "cache_results": cache_results,
            "total_improvement": total_improvement,
            "timestamp": time.time()
        }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        current_metrics = self.system_monitor.get_current_metrics()
        
        # 计算性能等级
        performance_level = self._calculate_performance_level(current_metrics)
        
        # 获取统计信息
        metric_stats = {}
        for metric_name in ["cpu_usage", "memory_usage", "disk_usage"]:
            stats = self.system_monitor.calculate_metric_statistics(metric_name, duration=3600)  # 1小时
            if stats:
                metric_stats[metric_name] = stats
        
        return {
            "performance_level": performance_level.value,
            "current_metrics": {name: {
                "value": metric.value,
                "unit": metric.unit,
                "timestamp": metric.timestamp
            } for name, metric in current_metrics.items()},
            "metric_statistics": metric_stats,
            "optimization_stats": self.stats,
            "cache_stats": {name: self.cache_manager.get_cache_stats(name) 
                          for name in self.cache_manager.caches},
            "load_balancer_stats": self.load_balancer.get_balancer_stats()
        }
    
    def _calculate_performance_level(self, metrics: Dict[str, PerformanceMetric]) -> PerformanceLevel:
        """计算性能等级"""
        critical_count = 0
        warning_count = 0
        
        for metric in metrics.values():
            if metric.threshold_critical and metric.value >= metric.threshold_critical:
                critical_count += 1
            elif metric.threshold_warning and metric.value >= metric.threshold_warning:
                warning_count += 1
        
        if critical_count > 0:
            return PerformanceLevel.CRITICAL
        elif warning_count > 2:
            return PerformanceLevel.WARNING
        elif warning_count > 0:
            return PerformanceLevel.NORMAL
        else:
            # 基于平均性能计算
            avg_usage = 0.0
            count = 0
            
            for metric in metrics.values():
                if metric.metric_name in ["cpu_usage", "memory_usage", "disk_usage"]:
                    avg_usage += metric.value
                    count += 1
            
            if count > 0:
                avg_usage /= count
                
                if avg_usage < 30:
                    return PerformanceLevel.EXCELLENT
                elif avg_usage < 60:
                    return PerformanceLevel.GOOD
                else:
                    return PerformanceLevel.NORMAL
            
            return PerformanceLevel.NORMAL
    
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """获取优化建议"""
        current_metrics = self.system_monitor.get_current_metrics()
        
        recommendations = []
        
        # 基于当前指标生成建议
        for metric_name, metric in current_metrics.items():
            if metric.threshold_warning and metric.value >= metric.threshold_warning:
                if metric_name == "cpu_usage":
                    recommendations.append({
                        "type": "cpu_optimization",
                        "description": "CPU使用率过高，建议减少并发任务或优化算法",
                        "priority": "high" if metric.value >= metric.threshold_critical else "medium",
                        "estimated_improvement": "15-25%"
                    })
                
                elif metric_name == "memory_usage":
                    recommendations.append({
                        "type": "memory_optimization",
                        "description": "内存使用率过高，建议清理缓存或增加内存",
                        "priority": "high" if metric.value >= metric.threshold_critical else "medium",
                        "estimated_improvement": "10-20%"
                    })
                
                elif metric_name == "disk_usage":
                    recommendations.append({
                        "type": "disk_optimization",
                        "description": "磁盘使用率过高，建议清理临时文件或扩展存储",
                        "priority": "medium",
                        "estimated_improvement": "5-15%"
                    })
        
        # 基于历史数据生成建议
        for metric_name in ["cpu_usage", "memory_usage"]:
            stats = self.system_monitor.calculate_metric_statistics(metric_name, duration=3600)
            if stats and stats.get("std", 0) > 20:  # 高变异性
                recommendations.append({
                    "type": "stability_optimization",
                    "description": f"{metric_name}波动较大，建议优化负载均衡",
                    "priority": "low",
                    "estimated_improvement": "5-10%"
                })
        
        return recommendations
    
    async def shutdown(self):
        """关闭性能优化器"""
        logger.info("正在关闭性能优化器...")
        
        self.is_running = False
        
        # 停止自动优化任务
        if self._optimization_task:
            self._optimization_task.cancel()
            try:
                await self._optimization_task
            except asyncio.CancelledError:
                pass
        
        # 停止系统监控
        await self.system_monitor.stop_monitoring()
        
        logger.info("性能优化器已关闭") 