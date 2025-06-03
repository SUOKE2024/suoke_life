#!/usr/bin/env python

"""
问诊服务入口程序
"""

import asyncio
from concurrent import futures
import logging
import os
import sys
from typing import Any

from dotenv import load_dotenv
import grpc

# 导入服务可观测性组件
from internal.observability.health_check import HealthChecker
from internal.observability.tracing import TracingManager

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 导入生成的gRPC代码
# 需要先生成proto文件的Python代码
# python -m grpc_tools.protoc -I./api/grpc --python_out=. --grpc_python_out=. ./api/grpc/inquiry_service.proto
from internal.delivery.inquiry_service_impl import InquiryServiceServicer
from internal.dialogue.dialogue_manager import DialogueManager
from internal.knowledge.tcm_knowledge_base import TCMKnowledgeBase
from internal.llm.health_risk_assessor import HealthRiskAssessor
from internal.llm.llm_client import LLMClient
from internal.llm.symptom_extractor import SymptomExtractor
from internal.llm.tcm_pattern_mapper import TCMPatternMapper
from internal.repository.session_repository import SessionRepository
from internal.repository.user_repository import UserRepository
from pkg.utils.config_loader import ConfigLoader
from pkg.utils.metrics import MetricsCollector

# 配置日志
def setup_logging(config: dict):
    """配置日志"""
    # 优先使用环境变量中的日志级别
    log_level_env = os.environ.get("LOG_LEVEL", "").upper()

    log_config = config.get("logging", {})
    log_level = getattr(
        logging, log_level_env or log_config.get("level", "INFO").upper()
    )
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # 配置根日志记录器
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(),  # 输出到控制台
        ],
    )

    # 如果需要输出到文件
    if log_config.get("output", "both") in ["file", "both"]:
        file_path = log_config.get("file_path", "./logs/inquiry_service.log")

        # 确保日志目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        file_handler = logging.FileHandler(file_path)
        file_handler.setFormatter(logging.Formatter(log_format))
        logging.getLogger().addHandler(file_handler)

    # 设置第三方库的日志级别
    logging.getLogger("grpc").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    return logging.getLogger("inquiry_service")

# 应用环境变量到配置
def apply_env_to_config(config: dict) -> dict:
    """应用环境变量覆盖配置文件中的设置"""
    # 服务配置
    if "GRPC_PORT" in os.environ:
        config["server"]["port"] = int(os.environ.get("GRPC_PORT"))

    if "GRPC_MAX_WORKERS" in os.environ:
        config["server"]["max_workers"] = int(os.environ.get("GRPC_MAX_WORKERS"))

    # 指标收集配置
    if "METRICS_PORT" in os.environ:
        config["metrics"]["port"] = int(os.environ.get("METRICS_PORT"))

    if "METRICS_ENABLED" in os.environ:
        config["metrics"]["enabled"] = os.environ.get(
            "METRICS_ENABLED", "false"
        ).lower() in ["true", "1", "yes"]

    # 日志配置
    if "LOG_LEVEL" in os.environ:
        config["logging"]["level"] = os.environ.get("LOG_LEVEL").lower()

    # LLM配置
    if "USE_MOCK_MODE" in os.environ:
        use_mock = os.environ.get("USE_MOCK_MODE", "false").lower() in [
            "true",
            "1",
            "yes",
        ]
        if "llm" not in config:
            config["llm"] = {}
        config["llm"]["use_mock_mode"] = use_mock

    # 外部服务模拟配置
    if "MOCK_EXTERNAL_SERVICES" in os.environ:
        mock_services = os.environ.get("MOCK_EXTERNAL_SERVICES", "false").lower() in [
            "true",
            "1",
            "yes",
        ]
        if "integration" in config:
            for service_name in [
                "xiaoai_service",
                "med_knowledge",
                "listen_service",
                "look_service",
            ]:
                if service_name in config["integration"]:
                    config["integration"][service_name]["mock_enabled"] = mock_services

    # 添加全局mock配置
    if "USE_MOCK_MODE" in os.environ or "MOCK_EXTERNAL_SERVICES" in os.environ:
        mock_enabled = os.environ.get("USE_MOCK_MODE", "false").lower() in [
            "true",
            "1",
            "yes",
        ] or os.environ.get("MOCK_EXTERNAL_SERVICES", "false").lower() in [
            "true",
            "1",
            "yes",
        ]
        if "mock" not in config:
            config["mock"] = {
                "enabled": mock_enabled,
                "response_delay_ms": 200,
                "random_failures": False,
                "failure_rate": 0.0,
            }
        else:
            config["mock"]["enabled"] = mock_enabled

    return config

async def init_application(config: dict[str, Any]) -> dict[str, Any]:
    """初始化应用"""
    app_components = {}

    # 初始化健康检查器
    health_checker = HealthChecker(config)
    app_components["health_checker"] = health_checker

    # 初始化分布式追踪
    tracing_manager = TracingManager(config)
    app_components["tracing_manager"] = tracing_manager

    # 初始化存储库
    session_repository = SessionRepository(config)
    user_repository = UserRepository(config)
    app_components["session_repository"] = session_repository
    app_components["user_repository"] = user_repository

    # 初始化知识库
    tcm_knowledge_base = TCMKnowledgeBase(config)
    app_components["tcm_knowledge_base"] = tcm_knowledge_base

    # 初始化LLM客户端
    llm_client = LLMClient(config)
    app_components["llm_client"] = llm_client

    # 初始化症状提取器
    symptom_extractor = SymptomExtractor(config)
    app_components["symptom_extractor"] = symptom_extractor

    # 初始化TCM证型映射器
    tcm_pattern_mapper = TCMPatternMapper(config)
    app_components["tcm_pattern_mapper"] = tcm_pattern_mapper

    # 初始化健康风险评估器
    health_risk_assessor = HealthRiskAssessor(config)
    app_components["health_risk_assessor"] = health_risk_assessor

    # 初始化对话管理器
    dialogue_manager = DialogueManager(
        llm_client=llm_client,
        session_repository=session_repository,
        user_repository=user_repository,
        config=config,
    )
    app_components["dialogue_manager"] = dialogue_manager

    # 初始化服务实现
    servicer = InquiryServiceServicer(
        dialogue_manager=dialogue_manager,
        symptom_extractor=symptom_extractor,
        tcm_pattern_mapper=tcm_pattern_mapper,
        health_risk_assessor=health_risk_assessor,
        tcm_knowledge_base=tcm_knowledge_base,
        config=config,
    )
    app_components["servicer"] = servicer

    # 注册数据库健康检查
    if health_checker.enabled:
        health_checker.register_check("database", session_repository.check_health)
        health_checker.register_check("llm", llm_client.check_health)
        health_checker.register_check("knowledge_base", tcm_knowledge_base.check_health)
        health_checker.register_check(
            "risk_assessor", health_risk_assessor.check_health
        )

    return app_components

async def run_server():
    """异步运行服务器"""
    # 加载配置
    config_loader = ConfigLoader("config/config.yaml")
    config = config_loader.load()

    # 应用环境变量覆盖配置
    config = apply_env_to_config(config)

    # 设置日志
    logger = setup_logging(config)
    logger.info("开始启动问诊服务...")

    # 打印一些关键配置
    service_env = os.environ.get("SERVICE_ENV", "development")
    logger.info(f"服务环境: {service_env}")
    logger.info(f"Mock模式: {config.get('mock', {}).get('enabled', False)}")
    logger.info(f"LLM mock模式: {config.get('llm', {}).get('use_mock_mode', False)}")

    # 获取服务器配置
    server_config = config.get("server", {})
    host = server_config.get("host", "0.0.0.0")
    port = server_config.get("port", 50052)
    max_workers = server_config.get("max_workers", 10)

    # 组件集合
    app_components = {}

    # 度量收集器
    metrics_collector = None

    try:
        # 初始化度量收集器
        metrics_config = config.get("metrics", {})
        if metrics_config.get("enabled", False):
            metrics_host = metrics_config.get("host", "0.0.0.0")
            metrics_port = metrics_config.get("port", 9090)
            metrics_path = metrics_config.get("path", "/metrics")
            metrics_collector = MetricsCollector(
                host=metrics_host,
                port=metrics_port,
                path=metrics_path,
                config=metrics_config,
            )
            metrics_collector.start()
            logger.info(
                f"度量收集器已启动: http://{metrics_host}:{metrics_port}{metrics_path}"
            )

        # 初始化gRPC服务器
        server = grpc.aio.server(
            futures.ThreadPoolExecutor(max_workers=max_workers),
            options=[
                (
                    "grpc.max_receive_message_length",
                    config.get("grpc", {}).get("max_message_size", 10485760),
                ),
                (
                    "grpc.max_send_message_length",
                    config.get("grpc", {}).get("max_message_size", 10485760),
                ),
                (
                    "grpc.keepalive_time_ms",
                    config.get("grpc", {}).get("keep_alive_time", 60000),
                ),
                (
                    "grpc.keepalive_timeout_ms",
                    config.get("grpc", {}).get("keep_alive_timeout", 20000),
                ),
                ("grpc.http2.max_pings_without_data", 0),
                ("grpc.http2.min_time_between_pings_ms", 10000),
                ("grpc.http2.min_ping_interval_without_data_ms", 5000),
            ],
        )

        # 初始化应用
        app_components = await init_application(config)
        servicer = app_components["servicer"]

        # 启动健康检查
        health_checker = app_components["health_checker"]
        await health_checker.start()
        logger.info("健康检查已启动")

        # 注册服务
        pb2_grpc.add_InquiryServiceServicer_to_server(servicer, server)

        # 添加服务器反射（用于调试）
        if server_config.get("enable_reflection", True):
            try:
                from grpc_reflection.v1alpha import reflection

                # 处理可能的导入错误，使用try/except
                try:
                    from api.grpc import inquiry_service_pb2

                    SERVICE_NAMES = (
                        inquiry_service_pb2.DESCRIPTOR.services_by_name[
                            "InquiryService"
                        ].full_name,
                        reflection.SERVICE_NAME,
                    )
                except (ImportError, AttributeError) as e:
                    logger.warning(f"服务反射导入错误: {e!s}")
                    SERVICE_NAMES = (reflection.SERVICE_NAME,)

                reflection.enable_server_reflection(SERVICE_NAMES, server)
                logger.info("已启用服务器反射")
            except Exception as e:
                logger.warning(f"启用服务器反射失败: {e!s}，继续启动服务")

        # 启动服务器
        server_address = f"{host}:{port}"
        server.add_insecure_port(server_address)
        await server.start()
        logger.info(f"问诊服务已启动，监听地址: {server_address}")

        # 保持服务运行
        try:
            await server.wait_for_termination()
        except KeyboardInterrupt:
            logger.info("收到键盘中断，准备关闭服务器...")
        finally:
            # 停止服务器
            logger.info("正在关闭服务器...")
            await server.stop(5)  # 5秒优雅关闭时间
            logger.info("服务器已关闭")

            # 关闭健康检查
            if "health_checker" in app_components:
                await app_components["health_checker"].stop()
                logger.info("健康检查已关闭")

            # 关闭分布式追踪
            if "tracing_manager" in app_components:
                app_components["tracing_manager"].shutdown()
                logger.info("分布式追踪已关闭")

            # 关闭度量收集器
            if metrics_collector:
                metrics_collector.stop()
                logger.info("度量收集器已关闭")

    except Exception as e:
        logger.error(f"启动服务器时发生错误: {e!s}", exc_info=True)
        sys.exit(1)

def serve():
    """启动gRPC服务器"""
    # Python 3.12和更高版本在Windows上有不同的默认策略
    if sys.version_info >= (3, 11) and hasattr(
        asyncio, "WindowsSelectorEventLoopPolicy"
    ):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Python 3.13 兼容性处理
    if sys.version_info >= (3, 13):
        asyncio.run(run_server())
    else:
        # Python 3.12及以下版本
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(run_server())
        except KeyboardInterrupt:
            pass
        finally:
            loop.close()

if __name__ == "__main__":
    serve()
