#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
小艾服务 (xiaoai-service)
启动脚本
"""

import os
import sys
import asyncio
import logging
import logging.config
import signal
import argparse
import yaml

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# 引入依赖
import grpc
from concurrent import futures

# 导入服务定义
from xiaoai_service.protos import xiaoai_service_pb2_grpc

# 导入服务实现
from internal.delivery.service import XiaoAIServicer
from internal.orchestrator.four_diagnosis_coordinator import FourDiagnosisCoordinator

# 导入集成客户端
from internal.integration.look_service_client import get_look_service_client
from internal.integration.listen_service_client import get_listen_service_client
from internal.integration.inquiry_service_client import get_inquiry_service_client
from internal.integration.palpation_service_client import get_palpation_service_client

# 导入核心组件
from internal.four_diagnosis.feature_extractor import FeatureExtractor
from internal.four_diagnosis.multimodal_fusion import MultimodalFusion
from internal.four_diagnosis.syndrome_analyzer import SyndromeAnalyzer
from internal.four_diagnosis.recommendation.health_advisor import HealthAdvisor
from internal.agent.model_factory import get_model_factory

# 导入工具类
from pkg.utils.config_manager import get_config_manager
from pkg.utils.metrics import get_metrics_collector

# 导入健康检查和弹性组件
from internal.observability.health_check import setup_health_checker
from internal.resilience.circuit_breaker import get_circuit_breaker

# 健康检查类型为可选
try:
    import grpc_health.v1.health_pb2 as health_pb2
    import grpc_health.v1.health_pb2_grpc as health_pb2_grpc
    from grpc_health.v1.health import HealthServicer
    health_check_available = True
except ImportError:
    health_check_available = False

# 反射服务类型为可选
try:
    from grpc_reflection.v1alpha import reflection
    reflection_available = True
except ImportError:
    reflection_available = False

# 设置日志
logger = logging.getLogger(__name__)

# 全局变量
server = None
is_shutting_down = False


def configure_logging(config):
    """
    配置日志
    
    Args:
        config: 配置管理器
    """
    logging_config = config.get_section('logging', {})
    log_level = logging_config.get('level', 'INFO')
    log_format = logging_config.get('format', '%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    
    # 确保日志目录存在
    log_dir = config.get_section('paths.logs', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # 配置日志
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': log_format
            },
        },
        'handlers': {
            'console': {
                'level': log_level,
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'stream': 'ext://sys.stdout',
            },
            'file': {
                'level': log_level,
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'standard',
                'filename': os.path.join(log_dir, 'xiaoai_service.log'),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 10,
                'encoding': 'utf8',
            },
        },
        'loggers': {
            '': {
                'handlers': ['console', 'file'],
                'level': log_level,
                'propagate': True,
            },
            'xiaoai_service': {
                'handlers': ['console', 'file'],
                'level': log_level,
                'propagate': False,
            },
        }
    }
    
    # 应用日志配置
    logging.config.dictConfig(logging_config)
    
    logger.info(f"日志已配置，级别: {log_level}")


def create_server():
    """
    创建gRPC服务器
    
    Returns:
        grpc.Server: gRPC服务器实例
    """
    # 获取配置
    config = get_config_manager()
    server_config = config.get_section('server', {})
    max_workers = server_config.get('workers', 4)
    
    # 创建服务器
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=max_workers),
        options=[
            ('grpc.max_send_message_length', 50 * 1024 * 1024),  # 50MB
            ('grpc.max_receive_message_length', 50 * 1024 * 1024),  # 50MB
            ('grpc.keepalive_time_ms', 10000),  # 10s
            ('grpc.keepalive_timeout_ms', 5000),  # 5s
            ('grpc.keepalive_permit_without_calls', True),
            ('grpc.http2.max_pings_without_data', 0),
            ('grpc.http2.min_time_between_pings_ms', 10000),  # 10s
        ]
    )
    
    return server


async def setup_server():
    """
    设置并启动服务器
    """
    global server
    
    # 获取配置
    config = get_config_manager()
    server_config = config.get_section('server', {})
    host = server_config.get('host', '0.0.0.0')
    port = server_config.get('port', 50051)
    
    # 创建服务器
    server = create_server()
    
    # 创建核心组件
    await setup_core_components(server)
    
    # 设置健康检查
    await setup_health_services(server)
    
    # 添加服务反射（如果可用）
    if reflection_available:
        service_names = tuple(
            service.full_name
            for service in xiaoai_service_pb2_grpc.DESCRIPTOR.services_by_name.values()
        )
        if health_check_available:
            service_names = service_names + (health_pb2.DESCRIPTOR.services_by_name['Health'].full_name,)
        
        reflection.enable_server_reflection(service_names, server)
        logger.info("已启用服务反射")
    
    # 配置服务地址
    server_address = f"{host}:{port}"
    server.add_insecure_port(server_address)
    
    # 启动服务器
    await server.start()
    logger.info(f"服务器已启动，监听地址: {server_address}")
    
    # 等待服务器终止
    await server.wait_for_termination()


async def setup_core_components(server):
    """
    设置核心组件
    
    Args:
        server: gRPC服务器实例
    """
    # 创建模型工厂
    model_factory = await get_model_factory()
    
    # 创建四诊核心组件
    feature_extractor = FeatureExtractor()
    multimodal_fusion = MultimodalFusion()
    syndrome_analyzer = SyndromeAnalyzer(model_factory)
    health_advisor = HealthAdvisor(model_factory)
    
    # 异步初始化需要模型工厂的组件
    await feature_extractor.initialize()
    await syndrome_analyzer.initialize()
    
    # 创建集成客户端
    look_client = await get_look_service_client()
    listen_client = await get_listen_service_client()
    inquiry_client = await get_inquiry_service_client()
    palpation_client = await get_palpation_service_client()
    
    # 创建四诊协调器
    coordinator = FourDiagnosisCoordinator(
        look_client=look_client,
        listen_client=listen_client,
        inquiry_client=inquiry_client,
        palpation_client=palpation_client,
        feature_extractor=feature_extractor,
        multimodal_fusion=multimodal_fusion,
        syndrome_analyzer=syndrome_analyzer,
        health_advisor=health_advisor
    )
    
    # 创建并注册服务
    service = XiaoAIServicer(
        coordinator=coordinator,
        model_factory=model_factory
    )
    xiaoai_service_pb2_grpc.add_XiaoAIServiceServicer_to_server(service, server)
    
    logger.info("核心组件已设置")


async def setup_health_services(server):
    """
    设置健康检查服务
    
    Args:
        server: gRPC服务器实例
    """
    # 设置应用健康检查器
    health_checker = await setup_health_checker()
    
    # 添加gRPC健康检查服务（如果可用）
    if health_check_available:
        health_servicer = HealthServicer()
        health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
        
        # 设置服务状态
        health_servicer.set(
            'xiaoai_service.XiaoAIService',
            health_pb2.HealthCheckResponse.SERVING
        )
        health_servicer.set(
            '',
            health_pb2.HealthCheckResponse.SERVING
        )
        
        logger.info("gRPC健康检查服务已设置")
    
    logger.info("健康检查服务已设置")


def handle_shutdown_signal(signum, frame):
    """
    处理关闭信号
    
    Args:
        signum: 信号编号
        frame: 当前帧
    """
    global is_shutting_down
    
    if is_shutting_down:
        logger.warning("已经在关闭中，忽略重复信号")
        return
    
    is_shutting_down = True
    signal_name = signal.Signals(signum).name
    
    logger.info(f"收到信号 {signal_name}，开始优雅关闭...")
    
    # 启动异步关闭
    asyncio.create_task(shutdown())


async def shutdown():
    """异步关闭服务器"""
    global server
    
    if server is not None:
        logger.info("关闭gRPC服务器...")
        
        # 为现有请求设置超时
        grace_period = 10  # 10秒优雅关闭期
        server.stop(grace_period)
        
        try:
            # 等待服务器关闭
            await asyncio.wait_for(server.wait_for_termination(), timeout=grace_period + 5)
            logger.info("gRPC服务器已关闭")
        except asyncio.TimeoutError:
            logger.warning(f"服务器关闭超时({grace_period + 5}s)，强制退出")
    
    # 停止事件循环
    logger.info("停止事件循环...")
    asyncio.get_event_loop().stop()


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='启动小艾服务')
    parser.add_argument('--config-dir', help='配置目录路径')
    parser.add_argument('--env', help='环境 (development, staging, production)')
    args = parser.parse_args()
    
    # 设置环境变量
    if args.config_dir:
        os.environ["XIAOAI_CONFIG_DIR"] = args.config_dir
    if args.env:
        os.environ["ENV"] = args.env
    
    # 获取配置并配置日志
    config = get_config_manager()
    configure_logging(config)
    
    # 注册信号处理程序
    signal.signal(signal.SIGINT, handle_shutdown_signal)
    signal.signal(signal.SIGTERM, handle_shutdown_signal)
    
    # 设置并启动服务器
    try:
        await setup_server()
    except Exception as e:
        logger.error(f"服务器启动失败: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    # 运行主函数
    asyncio.run(main()) 