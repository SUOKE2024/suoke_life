#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小艾智能体服务的主入口程序
负责启动gRPC服务器并处理服务生命周期
"""

import os
import sys
import asyncio
import logging
import signal
import argparse
import time
import grpc
from concurrent import futures

# 添加项目根目录到PYTHONPATH
sys.path.insert(0, os.path.abspath('.'))

from internal.delivery.xiaoai_service_impl import XiaoAIServiceImpl
from ..utils.config_loader import get_config
from ..utils.metrics import get_metrics_collector

# 导入gRPC生成的代码
try:
    import api.grpc.xiaoai_service_pb2_grpc as xiaoai_pb2_grpc
except ImportError:
    logging.error("无法导入gRPC生成的代码。请确保先运行 'python -m grpc_tools.protoc' 命令来生成。")
    sys.exit(1)

# 初始化日志配置
def init_logging(config):
    """初始化日志配置"""
    log_config = config.get_section('logging')
    log_level = getattr(logging, log_config.get('level', 'INFO'))
    log_format = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_file = log_config.get('file', None)
    
    # 配置根日志记录器
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(),  # 控制台处理器
            logging.FileHandler(log_file) if log_file else logging.NullHandler()  # 文件处理器（如果配置了文件）
        ]
    )
    
    # 设置gRPC日志级别
    logging.getLogger('grpc').setLevel(logging.WARNING)

class XiaoAIServer:
    """小艾智能体服务器类"""
    
    def __init__(self, config_path=None):
        """
        初始化服务器
        
        Args:
            config_path: 配置文件路径
        """
        # 加载配置
        self.config = get_config(config_path)
        
        # 初始化日志
        init_logging(self.config)
        self.logger = logging.getLogger(__name__)
        
        # 获取服务配置
        self.service_config = self.config.get_section('service')
        self.host = self.service_config.get('host', '0.0.0.0')
        self.port = self.service_config.get('port', 50053)
        self.max_workers = self.config.get_nested('performance', 'max_workers', default=10)
        
        # 获取指标收集器
        self.metrics = get_metrics_collector()
        
        # 初始化gRPC服务器
        self.server = None
        self.service_impl = None
        
        self.logger.info("小艾服务器初始化完成，配置加载自: %s", self.config.config_path or "默认配置")
    
    def start(self):
        """启动服务器（同步方法）"""
        try:
            asyncio.run(self._async_start())
        except KeyboardInterrupt:
            self.logger.info("接收到中断信号，正在关闭服务器...")
        except Exception as e:
            self.logger.error("服务器运行失败: %s", str(e))
            raise
    
    async def _async_start(self):
        """异步启动服务器"""
        try:
            # 创建gRPC服务器
            self.server = grpc.aio.server(
                futures.ThreadPoolExecutor(max_workers=self.max_workers),
                options=[
                    ('grpc.max_send_message_length', 100 * 1024 * 1024),  # 100MB
                    ('grpc.max_receive_message_length', 100 * 1024 * 1024),  # 100MB
                    ('grpc.keepalive_time_ms', 30000),  # 30秒
                    ('grpc.keepalive_timeout_ms', 10000),  # 10秒
                    ('grpc.keepalive_permit_without_calls', True),
                    ('grpc.http2.max_pings_without_data', 0),
                    ('grpc.http2.min_time_between_pings_ms', 10000),  # 10秒
                ]
            )
            
            # 创建服务实现
            self.service_impl = XiaoAIServiceImpl()
            
            # 注册服务
            xiaoai_pb2_grpc.add_XiaoAIServiceServicer_to_server(self.service_impl, self.server)
            
            # 绑定地址和端口
            server_address = f"{self.host}:{self.port}"
            self.server.add_insecure_port(server_address)
            
            # 启动服务器
            await self.server.start()
            self.logger.info("小艾服务器启动成功，监听地址: %s", server_address)
            
            # 注册信号处理器
            self._register_signal_handlers()
            
            # 等待服务器终止
            await self.server.wait_for_termination()
            
        except Exception as e:
            self.logger.error("启动服务器失败: %s", str(e))
            raise
    
    def _register_signal_handlers(self):
        """注册信号处理器"""
        loop = asyncio.get_event_loop()
        
        # 处理Ctrl+C (SIGINT)
        loop.add_signal_handler(
            signal.SIGINT,
            lambda: asyncio.create_task(self.shutdown("接收到 SIGINT 信号，正在关闭服务器..."))
        )
        
        # 处理SIGTERM
        loop.add_signal_handler(
            signal.SIGTERM,
            lambda: asyncio.create_task(self.shutdown("接收到 SIGTERM 信号，正在关闭服务器..."))
        )
    
    async def shutdown(self, reason="服务器正在关闭..."):
        """
        优雅关闭服务器
        
        Args:
            reason: 关闭原因
        """
        self.logger.info(reason)
        
        if self.server:
            # 停止接受新请求
            self.logger.info("停止接受新请求...")
            self.server.stop(grace=None)
            
            # 等待所有请求完成
            self.logger.info("等待所有请求完成...")
            await asyncio.sleep(5)  # 给请求一些时间完成
            
            # 关闭依赖组件
            if self.service_impl and hasattr(self.service_impl, 'diagnosis_coordinator'):
                self.logger.info("关闭四诊协调器...")
                await self.service_impl.diagnosis_coordinator.close()
            
            self.logger.info("服务器已成功关闭")

def main():
    """命令行入口点"""
    parser = argparse.ArgumentParser(description='启动小艾智能体服务')
    parser.add_argument('--config', '-c', type=str, 
                       default='config/dev.yaml',
                       help='配置文件路径 (默认: config/dev.yaml)')
    parser.add_argument('--host', type=str,
                       help='监听主机地址')
    parser.add_argument('--port', type=int,
                       help='监听端口')
    
    args = parser.parse_args()
    
    try:
        # 创建服务器
        server = XiaoAIServer(args.config)
        
        # 如果命令行指定了主机和端口，覆盖配置
        if args.host:
            server.host = args.host
        if args.port:
            server.port = args.port
        
        print(f"🚀 启动小艾服务...")
        print(f"📍 监听地址: {server.host}:{server.port}")
        print(f"📁 配置文件: {args.config}")
        print(f"🔧 工作线程: {server.max_workers}")
        
        # 启动服务器
        server.start()
        
    except KeyboardInterrupt:
        print("\n⏹️  服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 