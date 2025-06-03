#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
指标收集器
用于收集和导出服务指标
"""

import logging
import time
from typing import Dict, Any, Optional
from collections import defaultdict
import threading

logger = logging.getLogger(__name__)

class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化指标收集器
        
        Args:
            config: 配置信息
        """
        self.config = config
        self.enabled = config.get('enabled', True)
        
        # 指标存储
        self.counters = defaultdict(lambda: defaultdict(int))
        self.gauges = defaultdict(lambda: defaultdict(float))
        self.histograms = defaultdict(list)
        
        # 线程锁
        self.lock = threading.Lock()
        
        # Prometheus注册表（如果启用）
        self.prometheus_enabled = config.get('prometheus', {}).get('enabled', False)
        if self.prometheus_enabled:
            self._init_prometheus()
        
        logger.info("指标收集器初始化完成")
    
    def _init_prometheus(self):
        """初始化Prometheus指标"""
        try:
            from prometheus_client import Counter, Gauge, Histogram, CollectorRegistry
            
            self.registry = CollectorRegistry()
            
            # 定义Prometheus指标
            self.prom_counters = {}
            self.prom_gauges = {}
            self.prom_histograms = {}
            
            # 预定义一些常用指标
            self.prom_counters['requests_total'] = Counter(
                'palpation_service_requests_total',
                'Total number of requests',
                ['method', 'status'],
                registry=self.registry
            )
            
            self.prom_counters['errors_total'] = Counter(
                'palpation_service_errors_total',
                'Total number of errors',
                ['error_type'],
                registry=self.registry
            )
            
            self.prom_gauges['active_sessions'] = Gauge(
                'palpation_service_active_sessions',
                'Number of active sessions',
                registry=self.registry
            )
            
            self.prom_histograms['request_duration'] = Histogram(
                'palpation_service_request_duration_seconds',
                'Request duration in seconds',
                ['method'],
                registry=self.registry
            )
            
            logger.info("Prometheus指标初始化完成")
            
        except ImportError:
            logger.warning("prometheus_client未安装，禁用Prometheus指标")
            self.prometheus_enabled = False
    
    def record_counter(self, name: str, value: int = 1, labels: Optional[Dict[str, str]] = None):
        """
        记录计数器指标
        
        Args:
            name: 指标名称
            value: 增量值
            labels: 标签字典
        """
        if not self.enabled:
            return
        
        with self.lock:
            # 记录到内部存储
            label_key = self._labels_to_key(labels)
            self.counters[name][label_key] += value
            
            # 如果启用Prometheus
            if self.prometheus_enabled and name in self.prom_counters:
                try:
                    if labels:
                        self.prom_counters[name].labels(**labels).inc(value)
                    else:
                        self.prom_counters[name].inc(value)
                except Exception as e:
                    logger.error(f"记录Prometheus计数器失败: {e}")
    
    def record_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """
        记录仪表指标
        
        Args:
            name: 指标名称
            value: 当前值
            labels: 标签字典
        """
        if not self.enabled:
            return
        
        with self.lock:
            # 记录到内部存储
            label_key = self._labels_to_key(labels)
            self.gauges[name][label_key] = value
            
            # 如果启用Prometheus
            if self.prometheus_enabled and name in self.prom_gauges:
                try:
                    if labels:
                        self.prom_gauges[name].labels(**labels).set(value)
                    else:
                        self.prom_gauges[name].set(value)
                except Exception as e:
                    logger.error(f"记录Prometheus仪表失败: {e}")
    
    def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """
        记录直方图指标
        
        Args:
            name: 指标名称
            value: 观测值
            labels: 标签字典
        """
        if not self.enabled:
            return
        
        with self.lock:
            # 记录到内部存储
            if name not in self.histograms:
                self.histograms[name] = []
            self.histograms[name].append(value)
            
            # 保持最近1000个值
            if len(self.histograms[name]) > 1000:
                self.histograms[name] = self.histograms[name][-1000:]
            
            # 如果启用Prometheus
            if self.prometheus_enabled and name in self.prom_histograms:
                try:
                    if labels:
                        self.prom_histograms[name].labels(**labels).observe(value)
                    else:
                        self.prom_histograms[name].observe(value)
                except Exception as e:
                    logger.error(f"记录Prometheus直方图失败: {e}")
    
    def _labels_to_key(self, labels: Optional[Dict[str, str]]) -> str:
        """将标签字典转换为键"""
        if not labels:
            return "default"
        
        # 按键排序以确保一致性
        sorted_items = sorted(labels.items())
        return ",".join([f"{k}={v}" for k, v in sorted_items])
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        获取指标摘要
        
        Returns:
            指标摘要字典
        """
        with self.lock:
            summary = {
                'counters': {},
                'gauges': {},
                'histograms': {}
            }
            
            # 汇总计数器
            for name, label_values in self.counters.items():
                total = sum(label_values.values())
                summary['counters'][name] = {
                    'total': total,
                    'by_label': dict(label_values)
                }
            
            # 汇总仪表
            for name, label_values in self.gauges.items():
                summary['gauges'][name] = dict(label_values)
            
            # 汇总直方图
            for name, values in self.histograms.items():
                if values:
                    summary['histograms'][name] = {
                        'count': len(values),
                        'mean': np.mean(values),
                        'min': np.min(values),
                        'max': np.max(values),
                        'p50': np.percentile(values, 50),
                        'p90': np.percentile(values, 90),
                        'p99': np.percentile(values, 99)
                    }
            
            return summary
    
    def reset_metrics(self):
        """重置所有指标"""
        with self.lock:
            self.counters.clear()
            self.gauges.clear()
            self.histograms.clear()
            
            logger.info("指标已重置")
    
    def export_prometheus(self):
        """导出Prometheus格式的指标"""
        if not self.prometheus_enabled:
            return ""
        
        try:
            from prometheus_client import generate_latest
            return generate_latest(self.registry)
        except Exception as e:
            logger.error(f"导出Prometheus指标失败: {e}")
            return ""

class Timer:
    """计时器上下文管理器"""
    
    def __init__(self, metrics_collector: MetricsCollector, metric_name: str, labels: Optional[Dict[str, str]] = None):
        """
        初始化计时器
        
        Args:
            metrics_collector: 指标收集器
            metric_name: 指标名称
            labels: 标签字典
        """
        self.metrics_collector = metrics_collector
        self.metric_name = metric_name
        self.labels = labels
        self.start_time = None
    
    def __enter__(self):
        """进入上下文"""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        if self.start_time:
            duration = time.time() - self.start_time
            self.metrics_collector.record_histogram(self.metric_name, duration, self.labels)