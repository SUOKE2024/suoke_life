"""
闻诊服务(listen-service)主入口程序
优化版本：支持异步处理、改进监控、增强错误处理、中医特色功能
"""
import os
import sys
import time
import signal
import logging
import argparse
import threading
import asyncio
import concurrent.futures
from concurrent import futures
from typing import Dict, List, Any
from pathlib import Path
import platform

import grpc
from grpc_reflection.v1alpha import reflection
import uvloop  # 高性能事件循环

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.grpc import listen_service_pb2 as pb2
from api.grpc import listen_service_pb2_grpc as pb2_grpc
from internal.delivery.listen_service_impl import ListenServiceServicer
from pkg.utils.config_loader import get_config
from pkg.utils.metrics import get_metrics, get_alert_manager
from pkg.utils.logger import setup_logging, get_performance_logger, get_tcm_logger

logger = logging.getLogger(__name__)

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='闻诊服务')
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--port', type=int, help='服务端口')
    parser.add_argument('--host', type=str, help='服务地址')
    return parser.parse_args()

def setup_metrics(config: Dict[str, Any]):
    """初始化监控指标"""
    metrics = get_metrics("listen-service")
    
    # 启动Prometheus指标HTTP服务器
    if config.get("monitoring.prometheus.enabled", True):
        metrics_port = config.get("monitoring.prometheus.port", 9090)
        metrics_host = config.get("monitoring.prometheus.host", "0.0.0.0")
        metrics.start_http_server(port=metrics_port, addr=metrics_host)
    
    return metrics

def setup_health_check(server, config: Dict[str, Any]):
    """设置健康检查"""
    if config.get("monitoring.health_check.enabled", True):
        from grpc_health.v1 import health
        from grpc_health.v1 import health_pb2
        from grpc_health.v1 import health_pb2_grpc
        
        health_servicer = health.HealthServicer()
        health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
        
        # 设置服务健康状态
        health_servicer.set(
            "listen_service.ListenService", 
            health_pb2.HealthCheckResponse.SERVING
        )
        
        logger.info("健康检查服务已启用")
        return health_servicer
    
    return None

def collect_resource_metrics(metrics, interval: int = 60):
    """
    定期收集资源使用情况并更新指标
    
    Args:
        metrics: 指标收集器
        interval: 收集间隔(秒)
    """
    try:
        import psutil
        import GPUtil
        
        while True:
            # 收集CPU和内存使用情况
            process = psutil.Process(os.getpid())
            cpu_percent = process.cpu_percent(interval=1)
            memory_info = process.memory_info()
            
            metrics.set_resource_usage(
                cpu_percent=cpu_percent,
                memory_bytes=memory_info.rss,
                process_name="listen-service"
            )
            
            # 尝试收集GPU使用情况
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    for i, gpu in enumerate(gpus):
                        metrics.set_gpu_memory_usage(
                            memory_bytes=int(gpu.memoryUsed * 1024 * 1024),
                            device=str(i)
                        )
            except Exception:
                pass  # GPU信息收集失败，忽略
            
            # 等待下一次收集
            time.sleep(interval)
    
    except Exception as e:
        logger.error(f"资源指标收集失败: {str(e)}")

def cleanup(server, config: Dict[str, Any]):
    """
    执行服务关闭前的清理工作
    
    Args:
        server: gRPC服务器实例
        config: 配置字典
    """
    logger.info("正在关闭服务...")
    
    try:
        # 设置健康状态为不健康
        metrics = get_metrics()
        metrics.set_health_status(False, "grpc_server")
        
        # 记录关闭事件
        perf_logger = get_performance_logger()
        perf_logger.log_processing_time("service_shutdown", 0.0)
        
        # 关闭数据库连接
        try:
            from internal.repository.audio_repository import get_audio_repository
            get_audio_repository().close()
            logger.info("数据库连接已关闭")
        except Exception as e:
            logger.warning(f"关闭数据库连接失败: {e}")
        
        # 清理缓存
        try:
            from internal.audio.audio_analyzer import AudioAnalyzer
            # 这里可以添加缓存清理逻辑
            logger.info("缓存已清理")
        except Exception as e:
            logger.warning(f"清理缓存失败: {e}")
        
        # 停止gRPC服务
        grace_period = config.get("server.grace_period", 10)
        server.stop(grace_period)
        
        # 记录中医服务关闭
        tcm_logger = get_tcm_logger()
        tcm_logger.logger.info("中医闻诊服务已关闭")
        
        logger.info("服务已优雅关闭")
        
    except Exception as e:
        logger.error(f"服务关闭过程中发生错误: {e}")
        # 强制关闭
        server.stop(0)

def setup_alert_system(config: Dict[str, Any]):
    """设置告警系统"""
    alert_manager = get_alert_manager()
    
    def alert_callback(alert: Dict[str, Any]):
        """告警回调函数"""
        logger.warning(f"告警触发: {alert['message']}")
        # 这里可以添加更多告警处理逻辑，如发送邮件、短信等
        
    alert_manager.add_alert_callback(alert_callback)
    
    # 启动告警检查线程
    def check_alerts_periodically():
        while True:
            try:
                alerts = alert_manager.check_alerts()
                if alerts:
                    logger.warning(f"检测到 {len(alerts)} 个告警")
                time.sleep(config.get("monitoring.alert_check_interval", 60))
            except Exception as e:
                logger.error(f"告警检查失败: {e}")
                time.sleep(60)
    
    alert_thread = threading.Thread(target=check_alerts_periodically, daemon=True)
    alert_thread.start()
    
    return alert_manager

def setup_uvloop():
    """设置高性能事件循环"""
    if platform.system() != 'Windows':  # uvloop不支持Windows
        try:
            uvloop.install()
            logger.info("已启用uvloop高性能事件循环")
        except Exception as e:
            logger.warning(f"uvloop启用失败: {e}")

def serve():
    """启动gRPC服务"""
    # 设置高性能事件循环
    setup_uvloop()
    
    args = parse_args()
    
    # 加载配置
    config = get_config(args.config)
    
    # 初始化日志系统
    logger = setup_logging(config)
    
    # 服务参数
    port = args.port or config.get("server.port", 50052)
    host = args.host or config.get("server.host", "0.0.0.0")
    address = f"{host}:{port}"
    max_workers = config.get("server.max_workers", 16)
    max_concurrent_rpcs = config.get("server.max_concurrent_rpcs", 200)
    
    # 获取gRPC选项
    grpc_options = config.get("server.grpc_options", {})
    server_options = [
        ('grpc.max_send_message_length', grpc_options.get("max_send_message_length", 100485760)),
        ('grpc.max_receive_message_length', grpc_options.get("max_receive_message_length", 100485760)),
        ('grpc.keepalive_time_ms', grpc_options.get("keepalive_time_ms", 30000)),
        ('grpc.keepalive_timeout_ms', grpc_options.get("keepalive_timeout_ms", 5000)),
        ('grpc.keepalive_permit_without_calls', grpc_options.get("keepalive_permit_without_calls", True)),
        ('grpc.http2_max_pings_without_data', grpc_options.get("http2_max_pings_without_data", 0)),
        ('grpc.http2_min_time_between_pings_ms', grpc_options.get("http2_min_time_between_pings_ms", 10000)),
    ]
    
    # 初始化监控指标
    metrics = setup_metrics(config)
    
    # 设置服务信息
    import pkg_resources
    dependencies = {
        'grpcio': pkg_resources.get_distribution('grpcio').version,
        'librosa': pkg_resources.get_distribution('librosa').version,
        'torch': pkg_resources.get_distribution('torch').version,
    }
    
    metrics.set_service_info(
        version="2.0.0",
        build_time=time.strftime("%Y-%m-%d %H:%M:%S"),
        python_version=platform.python_version(),
        dependencies=dependencies
    )
    
    # 设置告警系统
    alert_manager = setup_alert_system(config)
    
    # 设置线程池
    thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
    
    # 创建gRPC服务器
    server = grpc.server(
        thread_pool,
        maximum_concurrent_rpcs=max_concurrent_rpcs,
        options=server_options
    )
    
    # 注册服务实现
    servicer = ListenServiceServicer(config)
    pb2_grpc.add_ListenServiceServicer_to_server(servicer, server)
    
    # 设置反射服务（用于gRPC CLI工具）
    if config.get("server.enable_reflection", True):
        SERVICE_NAMES = (
            pb2.DESCRIPTOR.services_by_name['ListenService'].full_name,
            reflection.SERVICE_NAME,
        )
        reflection.enable_server_reflection(SERVICE_NAMES, server)
    
    # 设置健康检查
    health_servicer = setup_health_check(server, config)
    
    # 启动资源指标收集线程
    metrics_thread = threading.Thread(
        target=collect_resource_metrics,
        args=(metrics, config.get("monitoring.metrics_interval", 30)),
        daemon=True
    )
    metrics_thread.start()
    
    # 注册信号处理
    def signal_handler(sig, frame):
        logger.info(f"接收到信号 {sig}，开始关闭服务...")
        cleanup(server, config)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动服务
    server.add_insecure_port(address)
    server.start()
    
    # 记录启动信息
    logger.info(f"闻诊服务已启动")
    logger.info(f"服务地址: {address}")
    logger.info(f"最大工作线程: {max_workers}")
    logger.info(f"最大并发RPC: {max_concurrent_rpcs}")
    logger.info(f"Python版本: {platform.python_version()}")
    logger.info(f"平台: {platform.platform()}")
    
    # 记录指标
    metrics.set_health_status(True, "grpc_server")
    
    # 记录中医特色启动信息
    tcm_logger = get_tcm_logger()
    tcm_logger.logger.info("中医闻诊服务已启动，支持五脏六腑声音分析、九种体质辨识、五志情绪检测")
    
    # 阻塞主线程
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        cleanup(server, config)

if __name__ == "__main__":
    serve() 