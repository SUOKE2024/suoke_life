#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
健康检查服务 - 实现服务健康状态监控和上报

本模块提供了符合gRPC健康检查协议的健康检查服务实现，支持服务状态监控、
资源使用率监测以及优雅的错误处理机制，确保微服务集群的稳定运行。
"""

import os
import time
import threading
import logging
import platform
import psutil
from typing import Dict, List, Optional, Tuple, Any

import grpc
from grpc_health.v1 import health_pb2, health_pb2_grpc
from prometheus_client import Gauge, Counter, Histogram, Info

logger = logging.getLogger(__name__)

# 定义指标
SYSTEM_MEMORY_USAGE = Gauge('system_memory_usage_percent', 'System memory usage in percent')
SYSTEM_CPU_USAGE = Gauge('system_cpu_usage_percent', 'System CPU usage in percent')
PROCESS_MEMORY_USAGE = Gauge('process_memory_usage_mb', 'Process memory usage in MB')
PROCESS_CPU_USAGE = Gauge('process_cpu_usage_percent', 'Process CPU usage in percent')
SERVICE_UPTIME = Gauge('service_uptime_seconds', 'Service uptime in seconds')
MODEL_LOADING_TIME = Histogram('model_loading_time_seconds', 'Time taken to load models in seconds')
SYSTEM_INFO = Info('system_info', 'System information')
GPU_MEMORY_USAGE = Gauge('gpu_memory_usage_mb', 'GPU memory usage in MB')
GPU_UTILIZATION = Gauge('gpu_utilization_percent', 'GPU utilization in percent')

# 健康状态枚举
SERVING_STATUS_UNKNOWN = health_pb2.HealthCheckResponse.UNKNOWN
SERVING_STATUS_SERVING = health_pb2.HealthCheckResponse.SERVING
SERVING_STATUS_NOT_SERVING = health_pb2.HealthCheckResponse.NOT_SERVING
SERVING_STATUS_SERVICE_UNKNOWN = health_pb2.HealthCheckResponse.SERVICE_UNKNOWN

class HealthMonitor:
    """服务健康监控器，监控系统资源和服务状态"""
    
    def __init__(self, config: Dict):
        """
        初始化健康监控器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.process = psutil.Process(os.getpid())
        self.start_time = time.time()
        
        # 监控配置
        self.check_interval = config.get('check_interval', 15)  # 秒
        self.memory_threshold = config.get('memory_threshold', 90)  # 百分比
        self.cpu_threshold = config.get('cpu_threshold', 80)  # 百分比
        self.record_metrics = config.get('record_metrics', True)
        
        # 服务端口
        self.service_port = config.get('service_port', 50051)
        
        # GPU监控设置
        self.use_gpu = config.get('use_gpu', False)
        self.gpu_memory_threshold = config.get('gpu_memory_threshold', 90)  # 百分比
        
        # 初始化系统信息
        self._init_system_info()
        
        # 监控线程
        self.monitor_thread = None
        self.stop_event = threading.Event()
        
        logger.info("健康监控器初始化完成")
    
    def start(self):
        """启动健康监控"""
        if self.monitor_thread is not None and self.monitor_thread.is_alive():
            logger.warning("监控线程已在运行")
            return
            
        self.stop_event.clear()
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("健康监控已启动")
    
    def stop(self):
        """停止健康监控"""
        if self.monitor_thread is None or not self.monitor_thread.is_alive():
            logger.warning("监控线程未在运行")
            return
            
        self.stop_event.set()
        self.monitor_thread.join(timeout=5.0)
        logger.info("健康监控已停止")
    
    def get_health_status(self) -> Dict:
        """
        获取当前健康状态
        
        Returns:
            Dict: 健康状态信息
        """
        uptime = time.time() - self.start_time
        
        mem_info = self.process.memory_info()
        mem_usage_mb = mem_info.rss / (1024 * 1024)
        
        status = {
            "service_name": self.config.get('service_name', 'look-service'),
            "uptime_seconds": uptime,
            "uptime_formatted": self._format_uptime(uptime),
            "cpu_percent": self.process.cpu_percent(),
            "memory_usage_mb": mem_usage_mb,
            "memory_usage_percent": self.process.memory_percent(),
            "system_cpu_percent": psutil.cpu_percent(),
            "system_memory_percent": psutil.virtual_memory().percent,
            "thread_count": threading.active_count(),
            "open_files": len(self.process.open_files()),
            "connections": len(self.process.connections()),
            "hostname": platform.node(),
            "serving_status": "SERVING"
        }
        
        # 添加GPU信息（如果启用）
        if self.use_gpu:
            gpu_info = self._get_gpu_info()
            if gpu_info:
                status.update(gpu_info)
        
        return status
    
    def check_thresholds(self) -> Tuple[bool, Optional[str]]:
        """
        检查资源使用是否超过阈值
        
        Returns:
            Tuple[bool, str]: (是否健康, 不健康原因)
        """
        # 检查内存使用
        sys_mem = psutil.virtual_memory().percent
        if sys_mem > self.memory_threshold:
            return False, f"系统内存使用率({sys_mem:.1f}%)超过阈值({self.memory_threshold}%)"
        
        # 检查CPU使用
        sys_cpu = psutil.cpu_percent()
        if sys_cpu > self.cpu_threshold:
            return False, f"系统CPU使用率({sys_cpu:.1f}%)超过阈值({self.cpu_threshold}%)"
        
        # 检查GPU使用（如果启用）
        if self.use_gpu:
            gpu_info = self._get_gpu_info()
            if gpu_info and gpu_info.get('gpu_memory_percent', 0) > self.gpu_memory_threshold:
                return False, f"GPU内存使用率({gpu_info['gpu_memory_percent']:.1f}%)超过阈值({self.gpu_memory_threshold}%)"
        
        return True, None
    
    def _monitor_loop(self):
        """监控循环，定期更新指标"""
        try:
            while not self.stop_event.is_set():
                try:
                    # 更新指标
                    if self.record_metrics:
                        self._update_metrics()
                    
                    # 检查资源阈值
                    healthy, reason = self.check_thresholds()
                    if not healthy:
                        logger.warning(f"资源使用超过阈值: {reason}")
                    
                    # 检查端口
                    if not self._check_port_listening(self.service_port):
                        logger.error(f"服务端口 {self.service_port} 未监听")
                    
                    # 等待下一次检查
                    self.stop_event.wait(self.check_interval)
                    
                except Exception as e:
                    logger.error(f"监控循环发生错误: {str(e)}")
                    self.stop_event.wait(self.check_interval)
                    
        except Exception as e:
            logger.error(f"监控线程异常退出: {str(e)}")
    
    def _update_metrics(self):
        """更新Prometheus指标"""
        # 系统指标
        SYSTEM_MEMORY_USAGE.set(psutil.virtual_memory().percent)
        SYSTEM_CPU_USAGE.set(psutil.cpu_percent(interval=None))
        
        # 进程指标
        mem_info = self.process.memory_info()
        PROCESS_MEMORY_USAGE.set(mem_info.rss / (1024 * 1024))
        PROCESS_CPU_USAGE.set(self.process.cpu_percent())
        
        # 服务指标
        SERVICE_UPTIME.set(time.time() - self.start_time)
        
        # GPU指标（如果启用）
        if self.use_gpu:
            gpu_info = self._get_gpu_info()
            if gpu_info:
                GPU_MEMORY_USAGE.set(gpu_info.get('gpu_memory_used_mb', 0))
                GPU_UTILIZATION.set(gpu_info.get('gpu_utilization', 0))
    
    def _init_system_info(self):
        """初始化系统信息指标"""
        system_info = {
            'hostname': platform.node(),
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': f"{psutil.virtual_memory().total / (1024*1024*1024):.2f} GB",
            'service_name': self.config.get('service_name', 'look-service'),
            'service_version': self.config.get('version', '1.0.0')
        }
        
        # 添加GPU信息（如果启用）
        if self.use_gpu:
            try:
                # 尝试使用PyTorch获取GPU信息
                import torch
                if torch.cuda.is_available():
                    system_info['gpu_count'] = torch.cuda.device_count()
                    system_info['gpu_name'] = torch.cuda.get_device_name(0)
                    system_info['cuda_version'] = torch.version.cuda
            except (ImportError, Exception) as e:
                logger.warning(f"获取GPU信息失败: {str(e)}")
        
        SYSTEM_INFO.info(system_info)
    
    def _get_gpu_info(self) -> Optional[Dict]:
        """获取GPU信息"""
        if not self.use_gpu:
            return None
            
        gpu_info = {}
        
        try:
            # 尝试使用PyTorch获取GPU信息
            import torch
            if torch.cuda.is_available():
                # 获取当前GPU内存使用情况
                torch.cuda.synchronize()
                used_memory = torch.cuda.memory_allocated(0) / (1024 * 1024)
                total_memory = torch.cuda.get_device_properties(0).total_memory / (1024 * 1024)
                memory_percent = (used_memory / total_memory) * 100
                
                gpu_info = {
                    'gpu_memory_used_mb': used_memory,
                    'gpu_memory_total_mb': total_memory,
                    'gpu_memory_percent': memory_percent,
                    'gpu_name': torch.cuda.get_device_name(0)
                }
                
                # 尝试使用pynvml获取GPU利用率
                try:
                    import pynvml
                    pynvml.nvmlInit()
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    gpu_info['gpu_utilization'] = utilization.gpu
                    pynvml.nvmlShutdown()
                except (ImportError, Exception):
                    # 如果pynvml不可用，使用简单估计
                    gpu_info['gpu_utilization'] = 0
                
        except (ImportError, Exception) as e:
            logger.warning(f"获取GPU信息失败: {str(e)}")
        
        return gpu_info
    
    def _check_port_listening(self, port: int) -> bool:
        """检查端口是否在监听"""
        for conn in psutil.net_connections(kind='inet'):
            if conn.laddr.port == port and conn.status == 'LISTEN':
                return True
        return False
    
    def _format_uptime(self, seconds: float) -> str:
        """格式化运行时间"""
        days, remainder = divmod(int(seconds), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}天 {hours}小时 {minutes}分钟"
        elif hours > 0:
            return f"{hours}小时 {minutes}分钟 {seconds}秒"
        elif minutes > 0:
            return f"{minutes}分钟 {seconds}秒"
        else:
            return f"{seconds}秒"

class HealthServicer(health_pb2_grpc.HealthServicer):
    """gRPC健康检查服务实现"""
    
    def __init__(self, health_monitor: HealthMonitor):
        """
        初始化健康检查服务
        
        Args:
            health_monitor: 健康监控器实例
        """
        self.health_monitor = health_monitor
        
        # 服务状态映射，默认所有服务都是SERVING状态
        self.status_map = {
            '': SERVING_STATUS_SERVING,  # 整体服务
            'look-service': SERVING_STATUS_SERVING,  # 主服务
            'grpc.health.v1.Health': SERVING_STATUS_SERVING,  # 健康检查服务
        }
        
        logger.info("gRPC健康检查服务初始化完成")
    
    def Check(
        self, 
        request: health_pb2.HealthCheckRequest, 
        context: grpc.ServicerContext
    ) -> health_pb2.HealthCheckResponse:
        """
        检查服务健康状态
        
        Args:
            request: 健康检查请求
            context: gRPC服务上下文
            
        Returns:
            健康检查响应
        """
        service_name = request.service
        
        # 检查资源阈值
        healthy, reason = self.health_monitor.check_thresholds()
        
        # 对于已知服务，如果资源使用异常，返回NOT_SERVING
        if service_name in self.status_map:
            status = self.status_map[service_name]
            
            # 如果资源使用超过阈值，将状态设为NOT_SERVING
            if not healthy:
                logger.warning(f"健康检查失败，服务将报告NOT_SERVING: {reason}")
                status = SERVING_STATUS_NOT_SERVING
            
            return health_pb2.HealthCheckResponse(status=status)
        
        # 未知服务
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details(f"Unknown service: {service_name}")
        return health_pb2.HealthCheckResponse(status=SERVING_STATUS_SERVICE_UNKNOWN)
    
    def Watch(
        self, 
        request: health_pb2.HealthCheckRequest, 
        context: grpc.ServicerContext
    ):
        """
        监控服务健康状态
        
        Args:
            request: 健康检查请求
            context: gRPC服务上下文
            
        Returns:
            健康检查响应流
        """
        service_name = request.service
        
        # 如果是未知服务，立即返回一个SERVICE_UNKNOWN响应
        if service_name not in self.status_map:
            yield health_pb2.HealthCheckResponse(status=SERVING_STATUS_SERVICE_UNKNOWN)
            return
        
        previous_status = None
        check_interval = self.health_monitor.check_interval
        
        try:
            while not context.is_active():
                # 检查资源阈值
                healthy, reason = self.health_monitor.check_thresholds()
                
                # 获取当前状态
                current_status = self.status_map[service_name]
                
                # 如果资源使用超过阈值，将状态设为NOT_SERVING
                if not healthy:
                    current_status = SERVING_STATUS_NOT_SERVING
                
                # 只有状态发生变化时才发送消息
                if current_status != previous_status:
                    previous_status = current_status
                    yield health_pb2.HealthCheckResponse(status=current_status)
                
                # 等待下一次检查
                time.sleep(check_interval)
                
        except Exception as e:
            logger.error(f"健康状态监控发生错误: {str(e)}")
    
    def update_status(self, service_name: str, status: int):
        """
        更新服务状态
        
        Args:
            service_name: 服务名称
            status: 服务状态
        """
        self.status_map[service_name] = status
        logger.info(f"更新服务状态: {service_name} -> {status}")
    
    def set_serving(self, service_name: str):
        """将服务设置为SERVING状态"""
        self.update_status(service_name, SERVING_STATUS_SERVING)
    
    def set_not_serving(self, service_name: str):
        """将服务设置为NOT_SERVING状态"""
        self.update_status(service_name, SERVING_STATUS_NOT_SERVING)
    
    def set_all_services(self, status: int):
        """设置所有服务状态"""
        for service_name in self.status_map:
            self.update_status(service_name, status) 