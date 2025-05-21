"""
闻诊服务(listen-service)主入口程序
"""
import os
import sys
import time
import signal
import logging
import argparse
import threading
import concurrent.futures
from concurrent import futures
from typing import Dict, List, Any

import grpc
from grpc_reflection.v1alpha import reflection

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.grpc import listen_service_pb2 as pb2
from api.grpc import listen_service_pb2_grpc as pb2_grpc
from internal.delivery.listen_service_impl import ListenServiceServicer
from pkg.utils.config_loader import get_config
from pkg.utils.metrics import get_metrics

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("listen_service.log")
    ]
)
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

def cleanup(server):
    """
    执行服务关闭前的清理工作
    
    Args:
        server: gRPC服务器实例
    """
    logger.info("正在关闭服务...")
    
    # 关闭数据库连接
    from internal.repository.audio_repository import get_audio_repository
    get_audio_repository().close()
    
    # 停止gRPC服务
    server.stop(5)  # 5秒优雅停止期
    
    logger.info("服务已关闭")

def serve():
    """启动gRPC服务"""
    args = parse_args()
    
    # 加载配置
    config = get_config(args.config)
    
    # 服务参数
    port = args.port or config.get("server.port", 50052)
    host = args.host or config.get("server.host", "0.0.0.0")
    address = f"{host}:{port}"
    max_workers = config.get("server.max_workers", 10)
    max_concurrent_rpcs = config.get("server.max_concurrent_rpcs", 100)
    
    # 初始化监控指标
    metrics = setup_metrics(config)
    
    # 设置线程池
    thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
    
    # 创建gRPC服务器
    server = grpc.server(
        thread_pool,
        maximum_concurrent_rpcs=max_concurrent_rpcs,
        options=[
            ('grpc.max_send_message_length', 50 * 1024 * 1024),  # 50MB
            ('grpc.max_receive_message_length', 50 * 1024 * 1024)  # 50MB
        ]
    )
    
    # 注册服务实现
    servicer = ListenServiceServicer()
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
        args=(metrics, config.get("monitoring.metrics_interval", 60)),
        daemon=True
    )
    metrics_thread.start()
    
    # 注册信号处理
    def signal_handler(sig, frame):
        logger.info(f"接收到信号 {sig}，开始关闭服务...")
        cleanup(server)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动服务
    server.add_insecure_port(address)
    server.start()
    logger.info(f"闻诊服务已启动: {address}")
    
    # 记录指标
    metrics.set_health_status(True, "grpc_server")
    
    # 阻塞主线程
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        cleanup(server)

if __name__ == "__main__":
    serve() 