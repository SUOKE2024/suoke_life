#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
无障碍服务主入口
"""

import os
import sys
import time
import signal
import logging
import argparse
from concurrent import futures

import grpc
from grpc_reflection.v1alpha import reflection

# 添加项目根目录到路径，以便导入其他模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from config.config import config, Config
from internal.delivery.grpc_server import AccessibilityServicer
from internal.service.app import AccessibilityApp


# 设置日志
def setup_logging():
    """设置日志配置"""
    log_level = getattr(logging, config.get("logging.level", "INFO"))
    log_format = config.get("logging.format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # 优先使用环境变量中的日志文件
    log_file = os.environ.get("LOGGING_FILE") or config.get("logging.file")
    
    handlers = [logging.StreamHandler()]
    
    if log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True)
                handlers.append(logging.FileHandler(log_file))
            except PermissionError:
                logging.warning(f"无法创建日志目录: {log_dir}，仅使用控制台日志")
        else:
            handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers
    )
    
    # 设置gRPC库的日志级别为ERROR，以减少噪音
    logging.getLogger('grpc').setLevel(logging.ERROR)


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='无障碍服务')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--port', type=int, help='服务端口号')
    parser.add_argument('--host', help='服务主机地址')
    
    return parser.parse_args()


def create_server(app, host, port):
    """
    创建gRPC服务器
    
    Args:
        app: 应用程序实例
        host: 主机地址
        port: 端口号
        
    Returns:
        gRPC服务器实例
    """
    # 创建一个gRPC服务器
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ('grpc.max_send_message_length', 50 * 1024 * 1024),  # 50MB
            ('grpc.max_receive_message_length', 50 * 1024 * 1024)  # 50MB
        ]
    )
    
    # 使用应用程序中的服务实例
    servicer = AccessibilityServicer(app.accessibility_service)
    
    # 注册服务
    from api.grpc import accessibility_pb2_grpc, accessibility_pb2
    accessibility_pb2_grpc.add_AccessibilityServiceServicer_to_server(servicer, server)
    
    # 添加反射服务（用于grpcurl等工具探索服务）
    service_names = (
        accessibility_pb2.DESCRIPTOR.services_by_name['AccessibilityService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(service_names, server)
    
    # 设置监听地址
    server_address = f"{host}:{port}"
    server.add_insecure_port(server_address)
    
    return server, server_address


def handle_sigterm(*args):
    """处理终止信号"""
    logging.info("接收到终止信号，优雅退出中...")
    raise KeyboardInterrupt


def main():
    """主函数"""
    # 解析命令行参数
    args = parse_args()
    
    # 如果指定了配置文件，则重新加载配置
    if args.config:
        global config
        config = Config(args.config)
    
    # 设置日志
    setup_logging()
    
    # 获取服务配置
    host = args.host or config.get("service.host", "0.0.0.0")
    port = args.port or config.get("service.port", 50051)
    
    # 显示欢迎信息
    service_name = config.get("service.name", "accessibility-service")
    service_version = config.get("service.version", "0.2.0")
    logging.info(f"启动 {service_name} v{service_version}")
    
    # 显示配置信息
    logging.info(f"服务地址: {host}:{port}")
    
    # 初始化应用
    app = None
    try:
        # 创建并初始化应用
        app = AccessibilityApp(config)
        
        # 显示已启用的服务
        logging.info("已启用的服务:")
        if app.edge_computing_service and hasattr(app.edge_computing_service, 'enabled') and app.edge_computing_service.enabled:
            logging.info("  - 边缘计算服务")
        if app.tcm_accessibility_service:
            logging.info("  - 中医特色无障碍适配服务")
        if app.dialect_service:
            dialects = len(app.dialect_service.supported_dialects) if hasattr(app.dialect_service, 'supported_dialects') else 0
            logging.info(f"  - 多方言支持服务 (支持 {dialects} 种方言)")
        if app.agent_coordination:
            logging.info("  - 智能体协作服务")
        if app.monitoring_service:
            logging.info("  - 监控与可观测性服务")
        if app.privacy_service:
            logging.info("  - 隐私与安全服务")
        if app.backup_scheduler and hasattr(app.backup_scheduler, 'backup_enabled') and app.backup_scheduler.backup_enabled:
            logging.info("  - 备份与容灾服务")
        
        if app.background_collection and hasattr(app.background_collection, 'enabled') and app.background_collection.enabled:
            collection_types = app.config.background_collection.collection_types.to_dict().keys() if hasattr(app.config.background_collection, 'collection_types') else []
            logging.info(f"  - 后台数据采集服务 (支持 {len(collection_types)} 种数据类型)")
            if collection_types:
                for ct in collection_types:
                    display_name = app.config.background_collection.collection_types.get(ct, {}).get('display_name', ct)
                    logging.info(f"      * {display_name}")
        
        app.start()
        
        # 注册信号处理
        signal.signal(signal.SIGTERM, handle_sigterm)
        signal.signal(signal.SIGINT, handle_sigterm)
        
        # 创建并启动服务器
        server, server_address = create_server(app, host, port)
        
        logging.info(f"无障碍服务启动于: {server_address}")
        server.start()
        
        # 保持服务运行
        while True:
            time.sleep(60 * 60)  # 每小时检查一次
    except KeyboardInterrupt:
        logging.info("关闭服务器...")
        if app:
            app.stop()
        server.stop(grace=5)  # 给5秒钟完成当前请求
        logging.info("服务器已关闭")
    except Exception as e:
        logging.exception(f"服务启动失败: {str(e)}")
        if app:
            app.stop()
        sys.exit(1)


if __name__ == "__main__":
    main() 