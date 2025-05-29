"""
gRPC 服务器模块

提供区块链服务的 gRPC 接口实现。
"""

from __future__ import annotations

from grpc import aio
from grpc_health.v1 import health, health_pb2, health_pb2_grpc
from grpc_reflection.v1alpha import reflection

from .config import settings
from .logging import grpc_logger as logger


class GRPCServer:
    """gRPC 服务器"""

    def __init__(self) -> None:
        self._server: aio.Server | None = None
        self._health_servicer = health.HealthServicer()

    async def start(self, host: str | None = None, port: int | None = None) -> None:
        """启动 gRPC 服务器"""
        actual_host = host or settings.grpc.host
        actual_port = port or settings.grpc.port

        logger.info("启动 gRPC 服务器", host=actual_host, port=actual_port)

        # 创建服务器
        self._server = aio.server(
            options=[
                ("grpc.keepalive_time_ms", 30000),
                ("grpc.keepalive_timeout_ms", 5000),
                ("grpc.keepalive_permit_without_calls", True),
                ("grpc.http2.max_pings_without_data", 0),
                ("grpc.http2.min_time_between_pings_ms", 10000),
                ("grpc.http2.min_ping_interval_without_data_ms", 300000),
                ("grpc.max_receive_message_length", settings.grpc.max_receive_message_length),
                ("grpc.max_send_message_length", settings.grpc.max_send_message_length),
            ]
        )

        # 添加健康检查服务
        if settings.grpc.enable_health_check:
            health_pb2_grpc.add_HealthServicer_to_server(
                self._health_servicer, self._server
            )
            # 设置服务状态为健康
            self._health_servicer.set("", health_pb2.HealthCheckResponse.SERVING)

        # 添加反射服务(用于调试)
        if settings.grpc.enable_reflection:
            service_names = [
                "blockchain.BlockchainService",
                health.SERVICE_NAME,
            ]
            reflection.enable_server_reflection(service_names, self._server)

        # 添加区块链服务
        # TODO: 实现具体的区块链服务
        # blockchain_pb2_grpc.add_BlockchainServiceServicer_to_server(
        #     BlockchainServicer(), self._server
        # )

        # 绑定端口
        listen_addr = f"{actual_host}:{actual_port}"
        self._server.add_insecure_port(listen_addr)

        # 启动服务器
        await self._server.start()
        logger.info("gRPC 服务器启动完成", address=listen_addr)

    async def stop(self) -> None:
        """停止 gRPC 服务器"""
        if self._server:
            logger.info("正在停止 gRPC 服务器")
            await self._server.stop(grace=5.0)
            logger.info("gRPC 服务器已停止")

    async def wait_for_termination(self) -> None:
        """等待服务器终止"""
        if self._server:
            await self._server.wait_for_termination()


# TODO: 实现具体的区块链服务接口
# class BlockchainServicer(blockchain_pb2_grpc.BlockchainServiceServicer):
#     """区块链服务实现"""
#
#     async def StoreHealthData(
#         self,
#         request: blockchain_pb2.StoreHealthDataRequest,
#         context: grpc.aio.ServicerContext,
#     ) -> blockchain_pb2.StoreHealthDataResponse:
#         """存储健康数据到区块链"""
#         try:
#             # 实现存储逻辑
#             pass
#         except Exception as e:
#             logger.error("存储健康数据失败", error=str(e))
#             await context.abort(grpc.StatusCode.INTERNAL, str(e))
#
#     async def VerifyHealthData(
#         self,
#         request: blockchain_pb2.VerifyHealthDataRequest,
#         context: grpc.aio.ServicerContext,
#     ) -> blockchain_pb2.VerifyHealthDataResponse:
#         """验证健康数据"""
#         try:
#             # 实现验证逻辑
#             pass
#         except Exception as e:
#             logger.error("验证健康数据失败", error=str(e))
#             await context.abort(grpc.StatusCode.INTERNAL, str(e))
