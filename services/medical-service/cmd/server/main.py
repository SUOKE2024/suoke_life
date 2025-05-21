#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import yaml
import grpc
import signal
import argparse
import concurrent.futures
from concurrent import futures

# 添加项目根目录到 Python 路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from internal.delivery.grpc.server import create_grpc_server
from internal.delivery.rest.server import create_rest_server
from internal.model.config import Config
from internal.service.medical_record_service import MedicalRecordService
from internal.service.diagnosis_service import DiagnosisService
from internal.service.treatment_service import TreatmentService
from internal.service.health_risk_service import HealthRiskService
from internal.service.medical_query_service import MedicalQueryService
from internal.repository.medical_record_repository import MedicalRecordRepository
from internal.repository.diagnosis_repository import DiagnosisRepository
from internal.repository.treatment_repository import TreatmentRepository
from internal.repository.health_risk_repository import HealthRiskRepository
from internal.repository.medical_query_repository import MedicalQueryRepository
from pkg.utils.logger import setup_logger
from pkg.utils.observability import setup_tracing, setup_metrics

# 全局变量
config = None
grpc_server = None
rest_server = None
logger = None


def load_config(config_path):
    """加载配置文件"""
    try:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
            return Config(**config_data)
    except Exception as e:
        logger.error(f"加载配置文件失败: {str(e)}")
        sys.exit(1)


def setup_services(config):
    """初始化服务组件"""
    try:
        # 初始化存储库
        medical_record_repo = MedicalRecordRepository(config.database)
        diagnosis_repo = DiagnosisRepository(config.database)
        treatment_repo = TreatmentRepository(config.database)
        health_risk_repo = HealthRiskRepository(config.database)
        medical_query_repository = MedicalQueryRepository(config.database)
        
        # 初始化服务
        medical_record_service = MedicalRecordService(medical_record_repo)
        diagnosis_service = DiagnosisService(diagnosis_repo, config.services)
        treatment_service = TreatmentService(treatment_repo, config.services)
        health_risk_service = HealthRiskService(health_risk_repo, config.services)
        
        # 配置外部服务
        services_config = {
            'rag': {
                'host': os.environ.get('RAG_SERVICE_HOST', config.services.rag.host),
                'port': int(os.environ.get('RAG_SERVICE_PORT', config.services.rag.port))
            },
            'med_knowledge': {
                'host': os.environ.get('MED_KNOWLEDGE_SERVICE_HOST', config.services.med_knowledge.host),
                'port': int(os.environ.get('MED_KNOWLEDGE_SERVICE_PORT', config.services.med_knowledge.port))
            },
            'health_data': {
                'host': os.environ.get('HEALTH_DATA_SERVICE_HOST', config.services.health_data.host),
                'port': int(os.environ.get('HEALTH_DATA_SERVICE_PORT', config.services.health_data.port))
            },
            'inquiry': {
                'host': os.environ.get('INQUIRY_SERVICE_HOST', config.services.inquiry.host),
                'port': int(os.environ.get('INQUIRY_SERVICE_PORT', config.services.inquiry.port))
            },
            'listen': {
                'host': os.environ.get('LISTEN_SERVICE_HOST', config.services.listen.host),
                'port': int(os.environ.get('LISTEN_SERVICE_PORT', config.services.listen.port))
            },
            'look': {
                'host': os.environ.get('LOOK_SERVICE_HOST', config.services.look.host),
                'port': int(os.environ.get('LOOK_SERVICE_PORT', config.services.look.port))
            },
            'palpation': {
                'host': os.environ.get('PALPATION_SERVICE_HOST', config.services.palpation.host),
                'port': int(os.environ.get('PALPATION_SERVICE_PORT', config.services.palpation.port))
            }
        }
        
        # 创建服务
        medical_query_service = MedicalQueryService(medical_query_repository, services_config)
        
        # 将服务打包返回
        services = {
            'medical_record_service': medical_record_service,
            'diagnosis_service': diagnosis_service,
            'treatment_service': treatment_service,
            'health_risk_service': health_risk_service,
            'medical_query_service': medical_query_service
        }
        
        logger.info("服务初始化完成")
        return services
        
    except Exception as e:
        logger.error(f"初始化服务失败: {str(e)}")
        sys.exit(1)


def start_servers(config, services):
    """启动 gRPC 和 REST 服务器"""
    global grpc_server, rest_server
    
    # 创建并启动 gRPC 服务器
    logger.info("Starting gRPC server...")
    grpc_server = create_grpc_server(config, services)
    grpc_server.start()
    logger.info(f"gRPC server started on port {config.server.grpc.port}")
    
    # 创建并启动 REST 服务器
    if hasattr(config.server, 'rest'):
        logger.info("Starting REST server...")
        rest_server = create_rest_server(config, services)
        rest_server.start()
        logger.info(f"REST server started on port {config.server.rest.port}")


def stop_servers():
    """停止服务器"""
    if grpc_server:
        logger.info("Stopping gRPC server...")
        grpc_server.stop(0)  # 立即停止，不等待
    
    if rest_server:
        logger.info("Stopping REST server...")
        rest_server.stop()


def signal_handler(sig, frame):
    """处理终止信号"""
    logger.info(f"Received signal {sig}. Shutting down...")
    stop_servers()
    sys.exit(0)


def main():
    global config, logger
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='医疗服务')
    parser.add_argument('--config', default='config/config.yaml', help='配置文件路径')
    args = parser.parse_args()
    
    # 加载配置
    config = load_config(args.config)
    
    # 设置日志
    logger = setup_logger(config.observability.logging)
    
    # 设置可观测性
    if config.observability.tracing.enabled:
        setup_tracing(config.observability.tracing)
    
    if config.observability.metrics.enabled:
        setup_metrics(config.observability.metrics)
    
    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 初始化服务
    services = setup_services(config)
    
    # 启动服务器
    start_servers(config, services)
    
    # 等待终止
    logger.info("Medical service is running. Press CTRL+C to exit.")
    try:
        # 阻塞主线程，直到接收到终止信号
        signal.pause()
    except KeyboardInterrupt:
        logger.info("Interrupted by user. Shutting down...")
    finally:
        stop_servers()


if __name__ == "__main__":
    main() 