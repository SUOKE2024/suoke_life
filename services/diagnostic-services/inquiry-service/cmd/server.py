"""
问诊服务启动模块
"""

import asyncio
from concurrent import futures
import logging
import os
import signal
import sys
from typing import Any

from dotenv import load_dotenv
import grpc
from grpc_reflection.v1alpha import reflection
import yaml

from api.grpc import inquiry_service_pb2, inquiry_service_pb2_grpc
from internal.delivery.inquiry_service_impl import InquiryServiceServicer
from internal.dialogue.dialogue_manager import DialogueManager
from internal.knowledge.tcm_knowledge_base import TCMKnowledgeBase
from internal.llm.health_risk_assessor import HealthRiskAssessor
from internal.llm.llm_client import LLMClient
from internal.llm.symptom_extractor import SymptomExtractor
from internal.llm.tcm_pattern_mapper import TCMPatternMapper
from internal.observability.health_check import HealthChecker
from internal.observability.tracing import TracingManager
from internal.repository.session_repository import SessionRepository
from internal.repository.user_repository import UserRepository
from pkg.utils.metrics import MetricsCollector

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)


class InquiryServer:
    """问诊服务器类"""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.server = None
        self.health_checker = None
        self.metrics_collector = None
        self.tracing_manager = None

    async def initialize_components(self) -> tuple[
        DialogueManager,
        SymptomExtractor,
        TCMPatternMapper,
        HealthRiskAssessor,
        TCMKnowledgeBase
    ]:
        """初始化所有组件"""
        logger.info("正在初始化服务组件...")

        # 初始化存储库
        session_repository = SessionRepository(self.config)
        user_repository = UserRepository(self.config)

        # 初始化LLM客户端
        llm_client = LLMClient(self.config)

        # 初始化中医知识库
        tcm_knowledge_base = TCMKnowledgeBase(self.config)
        await tcm_knowledge_base.initialize()

        # 初始化症状提取器
        symptom_extractor = SymptomExtractor(self.config)
        await symptom_extractor.initialize()

        # 初始化TCM证型映射器
        tcm_pattern_mapper = TCMPatternMapper(self.config)

        # 初始化健康风险评估器
        health_risk_assessor = HealthRiskAssessor(self.config)
        await health_risk_assessor.initialize()

        # 初始化对话管理器
        dialogue_manager = DialogueManager(
            llm_client=llm_client,
            session_repository=session_repository,
            user_repository=user_repository,
            config=self.config
        )

        logger.info("所有服务组件初始化完成")

        return (
            dialogue_manager,
            symptom_extractor,
            tcm_pattern_mapper,
            health_risk_assessor,
            tcm_knowledge_base
        )

    async def setup_server(self) -> None:
        """设置gRPC服务器"""
        # 初始化组件
        components = await self.initialize_components()
        dialogue_manager, symptom_extractor, tcm_pattern_mapper, health_risk_assessor, tcm_knowledge_base = components

        # 创建gRPC服务器
        server_config = self.config.get("server", {})
        max_workers = server_config.get("max_workers", 10)

        self.server = grpc.aio.server(
            futures.ThreadPoolExecutor(max_workers=max_workers),
            options=[
                ('grpc.keepalive_time_ms', self.config.get("grpc", {}).get("keep_alive_time", 60000)),
                ('grpc.keepalive_timeout_ms', self.config.get("grpc", {}).get("keep_alive_timeout", 20000)),
                ('grpc.keepalive_permit_without_calls', True),
                ('grpc.http2.max_pings_without_data', 0),
                ('grpc.http2.min_time_between_pings_ms', 10000),
                ('grpc.http2.min_ping_interval_without_data_ms', 300000),
                ('grpc.max_connection_age_ms', self.config.get("grpc", {}).get("connection_age", 300000)),
                ('grpc.max_connection_age_grace_ms', self.config.get("grpc", {}).get("connection_age_grace", 10000)),
                ('grpc.max_receive_message_length', self.config.get("grpc", {}).get("max_message_size", 10485760)),
                ('grpc.max_send_message_length', self.config.get("grpc", {}).get("max_message_size", 10485760)),
            ]
        )

        # 创建服务实现
        inquiry_servicer = InquiryServiceServicer(
            dialogue_manager=dialogue_manager,
            symptom_extractor=symptom_extractor,
            tcm_pattern_mapper=tcm_pattern_mapper,
            health_risk_assessor=health_risk_assessor,
            tcm_knowledge_base=tcm_knowledge_base,
            config=self.config
        )

        # 注册服务
        inquiry_service_pb2_grpc.add_InquiryServiceServicer_to_server(
            inquiry_servicer, self.server
        )

        # 启用反射（如果配置了）
        if server_config.get("enable_reflection", True):
            SERVICE_NAMES = (
                inquiry_service_pb2.DESCRIPTOR.services_by_name['InquiryService'].full_name,
                reflection.SERVICE_NAME,
            )
            reflection.enable_server_reflection(SERVICE_NAMES, self.server)
            logger.info("gRPC反射已启用")

        # 设置监听地址
        host = server_config.get("host", "0.0.0.0")
        port = server_config.get("port", 50052)
        listen_addr = f"{host}:{port}"

        self.server.add_insecure_port(listen_addr)
        logger.info(f"gRPC服务器将监听 {listen_addr}")

    async def start_health_checker(self) -> None:
        """启动健康检查器"""
        if self.config.get("health_check", {}).get("enabled", True):
            self.health_checker = HealthChecker(self.config)
            await self.health_checker.start()
            logger.info("健康检查器已启动")

    async def start_metrics_collector(self) -> None:
        """启动指标收集器"""
        if self.config.get("metrics", {}).get("enabled", False):
            self.metrics_collector = MetricsCollector(self.config)
            await self.metrics_collector.start()
            logger.info("指标收集器已启动")

    async def start_tracing(self) -> None:
        """启动分布式追踪"""
        if self.config.get("tracing", {}).get("enabled", False):
            self.tracing_manager = TracingManager(self.config)
            await self.tracing_manager.start()
            logger.info("分布式追踪已启动")

    async def start(self) -> None:
        """启动服务器"""
        logger.info("正在启动问诊服务...")

        # 设置服务器
        await self.setup_server()

        # 启动辅助服务
        await self.start_health_checker()
        await self.start_metrics_collector()
        await self.start_tracing()

        # 启动gRPC服务器
        await self.server.start()

        server_config = self.config.get("server", {})
        host = server_config.get("host", "0.0.0.0")
        port = server_config.get("port", 50052)

        logger.info(f"问诊服务已启动，监听地址: {host}:{port}")
        logger.info("服务已准备就绪，等待客户端连接...")

        # 等待服务器终止
        await self.server.wait_for_termination()

    async def stop(self) -> None:
        """停止服务器"""
        logger.info("正在停止问诊服务...")

        if self.server:
            await self.server.stop(grace=30)
            logger.info("gRPC服务器已停止")

        if self.health_checker:
            await self.health_checker.stop()
            logger.info("健康检查器已停止")

        if self.metrics_collector:
            await self.metrics_collector.stop()
            logger.info("指标收集器已停止")

        if self.tracing_manager:
            await self.tracing_manager.stop()
            logger.info("分布式追踪已停止")

        logger.info("问诊服务已完全停止")


def load_config() -> dict[str, Any]:
    """加载配置文件"""
    config_path = os.getenv("CONFIG_PATH", "./config/config.yaml")

    try:
        with open(config_path, encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logger.info(f"配置文件已加载: {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"配置文件未找到: {config_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"配置文件格式错误: {e}")
        raise


def setup_logging(config: dict[str, Any]) -> None:
    """设置日志"""
    log_config = config.get("logging", {})
    level = log_config.get("level", "info").upper()

    # 设置日志级别
    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 设置第三方库的日志级别
    logging.getLogger("grpc").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


async def serve() -> None:
    """启动服务的主函数"""
    # 加载配置
    config = load_config()

    # 设置日志
    setup_logging(config)

    # 创建服务器实例
    server = InquiryServer(config)

    # 设置信号处理
    def signal_handler(signum, frame):
        logger.info(f"收到信号 {signum}，正在优雅关闭...")
        asyncio.create_task(server.stop())

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # 启动服务器
        await server.start()
    except KeyboardInterrupt:
        logger.info("收到键盘中断，正在停止服务...")
    except Exception as e:
        logger.error(f"服务器启动失败: {e}", exc_info=True)
        raise
    finally:
        await server.stop()


def main() -> None:
    """主函数"""
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
