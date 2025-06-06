"""
enhanced_grpc_server - 索克生活项目模块
"""

from api.grpc import soer_service_pb2, soer_service_pb2_grpc
from grpc import aio
from internal.agent.enhanced_agent_manager import EnhancedAgentManager
from pkg.utils.dependency_injection import get_container
from pkg.utils.error_handling import ErrorSeverity, SoerServiceException, handle_error
from pkg.utils.metrics import get_metrics_collector
import grpc
import json
import logging

"""
增强的gRPC服务实现
集成依赖注入、错误处理、指标收集等功能
"""



logger = logging.getLogger(__name__)

class EnhancedSoerServicer(soer_service_pb2_grpc.SoerServiceServicer):
    """增强的索儿服务gRPC实现"""

    def __init__(self):
        self.container = get_container()
        self.metrics = get_metrics_collector()
        self.agent_manager: EnhancedAgentManager | None = None

    async def initialize(self) -> None:
        """初始化服务"""
        try:
            self.agent_manager = self.container.get_service("agent_manager")
            logger.info("gRPC服务初始化成功")
        except Exception as e:
            logger.error(f"gRPC服务初始化失败: {e}")
            raise

    async def Chat(
        self,
        request: soer_service_pb2.ChatRequest,
        context: grpc.aio.ServicerContext
    ) -> soer_service_pb2.ChatResponse:
        """聊天接口"""
        # 记录请求指标
        self.metrics.increment_counter("soer_grpc_requests", {"method": "Chat"})

        try:
            with self.metrics.timer("soer_grpc_request_duration", {"method": "Chat"}):
                # 验证输入
                if not request.message.strip():
                    raise SoerServiceException(
                        "消息内容不能为空",
                        error_code="INVALID_INPUT",
                        severity=ErrorSeverity.LOW
                    )

                # 构建会话上下文
                conversation_context = {
                    "user_id": request.user_id,
                    "session_id": request.session_id,
                    "message": request.message,
                    "context": json.loads(request.context) if request.context else {},
                    "preferences": json.loads(request.preferences) if request.preferences else {}
                }

                # 调用智能体管理器
                response = await self.agent_manager.process_message(conversation_context)

                # 构建响应
                grpc_response = soer_service_pb2.ChatResponse(
                    message=response.get("message", ""),
                    session_id=response.get("session_id", request.session_id),
                    context=json.dumps(response.get("context", {}), ensure_ascii=False),
                    suggestions=response.get("suggestions", []),
                    health_insights=response.get("health_insights", []),
                    recommendations=response.get("recommendations", [])
                )

                # 记录成功指标
                self.metrics.increment_counter("soer_grpc_responses", {
                    "method": "Chat",
                    "status": "success"
                })

                return grpc_response

        except SoerServiceException as e:
            # 处理业务异常
            await handle_error(e, {"method": "Chat", "user_id": request.user_id})

            # 设置gRPC状态
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))

        except Exception as e:
            # 处理未知异常
            logger.error(f"Chat方法发生未知错误: {e}")
            self.metrics.increment_counter("soer_grpc_errors", {"method": "Chat"})

            await context.abort(grpc.StatusCode.INTERNAL, "内部服务错误")

    async def GetHealthInsights(
        self,
        request: soer_service_pb2.HealthInsightsRequest,
        context: grpc.aio.ServicerContext
    ) -> soer_service_pb2.HealthInsightsResponse:
        """获取健康洞察"""
        self.metrics.increment_counter("soer_grpc_requests", {"method": "GetHealthInsights"})

        try:
            with self.metrics.timer("soer_grpc_request_duration", {"method": "GetHealthInsights"}):
                # 验证输入
                if not request.user_id:
                    raise SoerServiceException(
                        "用户ID不能为空",
                        error_code="INVALID_INPUT",
                        severity=ErrorSeverity.LOW
                    )

                # 获取健康洞察
                insights = await self.agent_manager.get_health_insights(
                    user_id=request.user_id,
                    time_range=request.time_range,
                    categories=list(request.categories) if request.categories else None
                )

                # 构建响应
                grpc_response = soer_service_pb2.HealthInsightsResponse(
                    insights=insights.get("insights", []),
                    trends=insights.get("trends", []),
                    recommendations=insights.get("recommendations", []),
                    risk_factors=insights.get("risk_factors", [])
                )

                self.metrics.increment_counter("soer_grpc_responses", {
                    "method": "GetHealthInsights",
                    "status": "success"
                })

                return grpc_response

        except SoerServiceException as e:
            await handle_error(e, {"method": "GetHealthInsights", "user_id": request.user_id})
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))

        except Exception as e:
            logger.error(f"GetHealthInsights方法发生未知错误: {e}")
            self.metrics.increment_counter("soer_grpc_errors", {"method": "GetHealthInsights"})
            await context.abort(grpc.StatusCode.INTERNAL, "内部服务错误")

    async def GetPersonalizedRecommendations(
        self,
        request: soer_service_pb2.RecommendationsRequest,
        context: grpc.aio.ServicerContext
    ) -> soer_service_pb2.RecommendationsResponse:
        """获取个性化推荐"""
        self.metrics.increment_counter("soer_grpc_requests", {"method": "GetPersonalizedRecommendations"})

        try:
            with self.metrics.timer("soer_grpc_request_duration", {"method": "GetPersonalizedRecommendations"}):
                # 验证输入
                if not request.user_id:
                    raise SoerServiceException(
                        "用户ID不能为空",
                        error_code="INVALID_INPUT",
                        severity=ErrorSeverity.LOW
                    )

                # 获取个性化推荐
                recommendations = await self.agent_manager.get_personalized_recommendations(
                    user_id=request.user_id,
                    recommendation_type=request.type,
                    preferences=json.loads(request.preferences) if request.preferences else {},
                    limit=request.limit if request.limit > 0 else 10
                )

                # 构建响应
                grpc_response = soer_service_pb2.RecommendationsResponse(
                    food_recommendations=recommendations.get("food", []),
                    exercise_recommendations=recommendations.get("exercise", []),
                    lifestyle_recommendations=recommendations.get("lifestyle", []),
                    tcm_recommendations=recommendations.get("tcm", [])
                )

                self.metrics.increment_counter("soer_grpc_responses", {
                    "method": "GetPersonalizedRecommendations",
                    "status": "success"
                })

                return grpc_response

        except SoerServiceException as e:
            await handle_error(e, {"method": "GetPersonalizedRecommendations", "user_id": request.user_id})
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))

        except Exception as e:
            logger.error(f"GetPersonalizedRecommendations方法发生未知错误: {e}")
            self.metrics.increment_counter("soer_grpc_errors", {"method": "GetPersonalizedRecommendations"})
            await context.abort(grpc.StatusCode.INTERNAL, "内部服务错误")

    async def AnalyzeHealthData(
        self,
        request: soer_service_pb2.HealthDataRequest,
        context: grpc.aio.ServicerContext
    ) -> soer_service_pb2.HealthDataResponse:
        """分析健康数据"""
        self.metrics.increment_counter("soer_grpc_requests", {"method": "AnalyzeHealthData"})

        try:
            with self.metrics.timer("soer_grpc_request_duration", {"method": "AnalyzeHealthData"}):
                # 验证输入
                if not request.user_id or not request.data:
                    raise SoerServiceException(
                        "用户ID和健康数据不能为空",
                        error_code="INVALID_INPUT",
                        severity=ErrorSeverity.LOW
                    )

                # 解析健康数据
                health_data = json.loads(request.data)

                # 分析健康数据
                analysis = await self.agent_manager.analyze_health_data(
                    user_id=request.user_id,
                    data_type=request.data_type,
                    health_data=health_data,
                    analysis_options=json.loads(request.options) if request.options else {}
                )

                # 构建响应
                grpc_response = soer_service_pb2.HealthDataResponse(
                    analysis_result=json.dumps(analysis.get("result", {}), ensure_ascii=False),
                    insights=analysis.get("insights", []),
                    alerts=analysis.get("alerts", []),
                    trends=analysis.get("trends", []),
                    recommendations=analysis.get("recommendations", [])
                )

                self.metrics.increment_counter("soer_grpc_responses", {
                    "method": "AnalyzeHealthData",
                    "status": "success"
                })

                return grpc_response

        except SoerServiceException as e:
            await handle_error(e, {"method": "AnalyzeHealthData", "user_id": request.user_id})
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))

        except Exception as e:
            logger.error(f"AnalyzeHealthData方法发生未知错误: {e}")
            self.metrics.increment_counter("soer_grpc_errors", {"method": "AnalyzeHealthData"})
            await context.abort(grpc.StatusCode.INTERNAL, "内部服务错误")

    async def GetSessionHistory(
        self,
        request: soer_service_pb2.SessionHistoryRequest,
        context: grpc.aio.ServicerContext
    ) -> soer_service_pb2.SessionHistoryResponse:
        """获取会话历史"""
        self.metrics.increment_counter("soer_grpc_requests", {"method": "GetSessionHistory"})

        try:
            with self.metrics.timer("soer_grpc_request_duration", {"method": "GetSessionHistory"}):
                # 验证输入
                if not request.user_id:
                    raise SoerServiceException(
                        "用户ID不能为空",
                        error_code="INVALID_INPUT",
                        severity=ErrorSeverity.LOW
                    )

                # 获取会话历史
                history = await self.agent_manager.get_session_history(
                    user_id=request.user_id,
                    session_id=request.session_id if request.session_id else None,
                    limit=request.limit if request.limit > 0 else 20
                )

                # 构建响应
                grpc_response = soer_service_pb2.SessionHistoryResponse(
                    sessions=history.get("sessions", []),
                    messages=history.get("messages", []),
                    total_count=history.get("total_count", 0)
                )

                self.metrics.increment_counter("soer_grpc_responses", {
                    "method": "GetSessionHistory",
                    "status": "success"
                })

                return grpc_response

        except SoerServiceException as e:
            await handle_error(e, {"method": "GetSessionHistory", "user_id": request.user_id})
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))

        except Exception as e:
            logger.error(f"GetSessionHistory方法发生未知错误: {e}")
            self.metrics.increment_counter("soer_grpc_errors", {"method": "GetSessionHistory"})
            await context.abort(grpc.StatusCode.INTERNAL, "内部服务错误")

class EnhancedGrpcServer:
    """增强的gRPC服务器"""

    def __init__(self, host: str = "0.0.0.0", port: int = 50051):
        self.host = host
        self.port = port
        self.server: aio.Server | None = None
        self.servicer: EnhancedSoerServicer | None = None
        self.metrics = get_metrics_collector()

    async def start(self) -> None:
        """启动gRPC服务器"""
        try:
            # 创建服务器
            self.server = aio.server()

            # 创建并初始化服务实现
            self.servicer = EnhancedSoerServicer()
            await self.servicer.initialize()

            # 注册服务
            soer_service_pb2_grpc.add_SoerServiceServicer_to_server(
                self.servicer,
                self.server
            )

            # 添加监听端口
            listen_addr = f"{self.host}:{self.port}"
            self.server.add_insecure_port(listen_addr)

            # 启动服务器
            await self.server.start()

            logger.info(f"gRPC服务器已启动，监听地址: {listen_addr}")

            # 记录启动指标
            self.metrics.increment_counter("soer_grpc_server_starts")

        except Exception as e:
            logger.error(f"gRPC服务器启动失败: {e}")
            raise

    async def stop(self) -> None:
        """停止gRPC服务器"""
        if self.server:
            try:
                # 优雅停止服务器
                await self.server.stop(grace=30)
                logger.info("gRPC服务器已停止")

                # 记录停止指标
                self.metrics.increment_counter("soer_grpc_server_stops")

            except Exception as e:
                logger.error(f"gRPC服务器停止失败: {e}")

    async def wait_for_termination(self) -> None:
        """等待服务器终止"""
        if self.server:
            await self.server.wait_for_termination()

    async def health_check(self) -> bool:
        """健康检查"""
        try:
            if not self.server or not self.servicer:
                return False

            # 检查服务器状态
            # 这里可以添加更详细的健康检查逻辑
            return True

        except Exception as e:
            logger.error(f"gRPC服务器健康检查失败: {e}")
            return False
