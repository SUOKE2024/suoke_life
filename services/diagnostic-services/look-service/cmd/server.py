#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
望诊服务入口点

启动gRPC服务器，提供面色分析和形体分析功能。
"""

import os
import sys
import time
import signal
import logging
import argparse
import concurrent.futures
from concurrent import futures

import grpc
from prometheus_client import start_http_server
from structlog import get_logger

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from api.grpc import look_service_pb2_grpc
from internal.delivery.look_service_impl import LookServiceServicer
from config.config import get_config

# 设置日志
logger = get_logger()


def setup_logging():
    """设置日志配置"""
    config = get_config()
    log_level = getattr(logging, config.get("logging.level", "INFO"))
    log_file = config.get("logging.file", "./logs/look_service.log")
    console = config.get("logging.console", True)
    
    # 确保日志目录存在
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 配置日志
    handlers = []
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    if console:
        handlers.append(logging.StreamHandler())
    
    logging.basicConfig(
        level=log_level,
        format=config.get("logging.format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
        handlers=handlers
    )
    
    logger.info("日志配置完成", level=config.get("logging.level", "INFO"))


def setup_metrics():
    """设置Prometheus指标服务器"""
    config = get_config()
    if config.get("monitoring.prometheus.enabled", True):
        metrics_port = config.get("monitoring.prometheus.port", 9090)
        start_http_server(metrics_port)
        logger.info("Prometheus指标服务器已启动", port=metrics_port)


def serve(host, port, max_workers):
    """
    启动gRPC服务
    
    Args:
        host: 主机地址
        port: 端口号
        max_workers: 最大工作线程数
    """
    config = get_config()
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=max_workers),
        options=[
            ('grpc.max_send_message_length', config.get("server.grpc.max_message_size", 10485760)),
            ('grpc.max_receive_message_length', config.get("server.grpc.max_message_size", 10485760)),
            ('grpc.keepalive_time_ms', config.get("server.grpc.keepalive_time_ms", 7200000)),
            ('grpc.keepalive_timeout_ms', config.get("server.grpc.keepalive_timeout_ms", 20000)),
            ('grpc.http2.max_pings_without_data', 0),
            ('grpc.http2.min_time_between_pings_ms', 300000),
            ('grpc.http2.min_ping_interval_without_data_ms', 300000)
        ]
    )
    
    # 创建服务实现
    servicer = LookServiceServicer()
    
    # 注册服务
    look_service_pb2_grpc.add_LookServiceServicer_to_server(servicer, server)
    
    # 添加端口
    server_address = f"{host}:{port}"
    server.add_insecure_port(server_address)
    
    # 启动服务
    server.start()
    logger.info("望诊服务已启动", address=server_address, workers=max_workers)
    
    # 设置信号处理
    def handle_signal(signum, frame):
        logger.info("收到终止信号，准备优雅关闭", signal=signum)
        # 设置优雅关闭超时（30秒）
        grace_period = 30
        try:
            # 尝试优雅关闭
            server.stop(grace_period)
            logger.info("服务已优雅关闭")
        except Exception as e:
            logger.error("服务关闭时出错", error=str(e))
        finally:
            sys.exit(0)
    
    # 注册信号处理器
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    
    # 保持运行状态
    try:
        while True:
            time.sleep(3600)  # 每小时进行一次检查
            logger.debug("服务运行中...")
    except KeyboardInterrupt:
        logger.info("收到键盘中断，准备关闭...")
        server.stop(30)  # 30秒超时的优雅关闭
        logger.info("服务已关闭")


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="望诊服务")
    parser.add_argument("--host", help="监听主机地址")
    parser.add_argument("--port", type=int, help="监听端口")
    parser.add_argument("--workers", type=int, help="工作线程数")
    parser.add_argument("--config", help="配置文件路径")
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()
    
    # 设置配置文件路径
    if args.config:
        os.environ["CONFIG_PATH"] = args.config
    
    # 加载配置
    config = get_config()
    
    # 设置日志
    setup_logging()
    
    # 设置监控指标
    setup_metrics()
    
    # 获取服务配置，命令行参数优先
    host = args.host or config.get("server.host", "0.0.0.0")
    port = args.port or config.get("server.port", 50053)
    max_workers = args.workers or config.get("server.grpc.max_workers", 10)
    
    # 启动服务
    serve(host, port, max_workers)


if __name__ == "__main__":
    main() 