#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
切诊服务入口程序
"""

import os
import sys
import argparse
import yaml
import logging
import grpc
import time
from concurrent import futures
from pathlib import Path

# 添加项目根目录到Python路径，确保能够正确导入模块
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api.grpc import palpation_service_pb2_grpc
from internal.delivery.palpation_service_impl import PalpationServiceServicer
from internal.repository.session_repository import SessionRepository
from internal.repository.user_repository import UserRepository
from internal.signal.pulse_processor import PulseProcessor
from internal.signal.abdominal_analyzer import AbdominalAnalyzer
from internal.signal.skin_analyzer import SkinAnalyzer

def load_config(config_path=None):
    """加载配置文件"""
    if not config_path:
        config_path = os.getenv('CONFIG_PATH', './config/config.yaml')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logging.error(f"加载配置文件失败: {e}")
        raise

def setup_logging(config):
    """设置日志"""
    log_level = config.get('logging', {}).get('level', 'INFO')
    log_format = config.get('logging', {}).get('format', 
                           '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format
    )

def init_repositories(config):
    """初始化数据存储仓库"""
    db_config = config.get('database', {})
    session_repo = SessionRepository(db_config)
    user_repo = UserRepository(db_config)
    return session_repo, user_repo

def init_processors(config):
    """初始化信号处理器"""
    pulse_config = config.get('pulse_analysis', {})
    abdominal_config = config.get('abdominal_analysis', {})
    skin_config = config.get('skin_analysis', {})
    
    pulse_processor = PulseProcessor(pulse_config)
    abdominal_analyzer = AbdominalAnalyzer(abdominal_config)
    skin_analyzer = SkinAnalyzer(skin_config)
    
    return pulse_processor, abdominal_analyzer, skin_analyzer

def serve(config):
    """启动gRPC服务"""
    server_config = config.get('server', {})
    port = server_config.get('port', 50053)
    max_workers = server_config.get('max_workers', 10)
    
    # 初始化仓库和处理器
    session_repo, user_repo = init_repositories(config)
    pulse_processor, abdominal_analyzer, skin_analyzer = init_processors(config)
    
    # 创建gRPC服务
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=max_workers),
        options=[
            ('grpc.max_send_message_length', server_config.get('max_message_length', 100) * 1024 * 1024),
            ('grpc.max_receive_message_length', server_config.get('max_message_length', 100) * 1024 * 1024)
        ]
    )
    
    # 注册服务实现
    service = PalpationServiceServicer(
        session_repository=session_repo,
        user_repository=user_repo,
        pulse_processor=pulse_processor,
        abdominal_analyzer=abdominal_analyzer,
        skin_analyzer=skin_analyzer,
        config=config
    )
    palpation_service_pb2_grpc.add_PalpationServiceServicer_to_server(service, server)
    
    # 启动服务
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    logging.info(f"切诊服务已启动，监听端口: {port}")
    
    try:
        # 保持服务运行
        while True:
            time.sleep(86400)  # 睡眠一天
    except KeyboardInterrupt:
        logging.info("接收到终止信号，准备关闭服务...")
        server.stop(grace=5)  # 给5秒优雅关闭时间
        logging.info("服务已关闭")

def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(description='切诊服务启动脚本')
    parser.add_argument('--config', type=str, help='配置文件路径')
    args = parser.parse_args()
    
    # 加载配置
    config = load_config(args.config)
    
    # 设置日志
    setup_logging(config)
    
    # 启动服务
    serve(config)

if __name__ == '__main__':
    main() 