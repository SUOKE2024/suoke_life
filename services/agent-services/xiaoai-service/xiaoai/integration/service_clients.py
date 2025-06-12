"""
外部服务客户端

与其他诊断服务进行通信的客户端实现
"""

from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass
from datetime import datetime
import json
import logging
from typing import Any, Dict, List, Optional

import aiohttp

# 可选的 grpc 导入
try:
    from grpc import aio as aio_grpc

    GRPC_AVAILABLE = True
except ImportError:
    aio_grpc = None
    GRPC_AVAILABLE = False

from ..config.settings import get_settings
from ..utils.exceptions import CommunicationError, ServiceUnavailableError
from ..utils.retry import retry_with_backoff

logger = logging.getLogger(__name__)


@dataclass
class ServiceEndpoint:
    """服务端点配置"""

    name: str
    host: str
    port: int
    protocol: str  # http, grpc
    timeout: int = 30
    max_retries: int = 3
    health_check_path: str = "/health"


class BaseServiceClient(ABC):
    """服务客户端基类"""

    def __init__(self, endpoint: ServiceEndpoint):
        self.endpoint = endpoint
        self.settings = get_settings()
        self._client = None
        self._channel = None

    async def initialize(self) -> None:
        """初始化客户端"""
        try:
            if self.endpoint.protocol == "grpc":
                await self._initialize_grpc_client()
            elif self.endpoint.protocol == "http":
                await self._initialize_http_client()
            else:
                raise ValueError(f"不支持的协议: {self.endpoint.protocol}")

            # 健康检查
            await self.health_check()

            logger.info(f"服务客户端初始化成功: {self.endpoint.name}")

        except Exception as e:
            logger.error(f"服务客户端初始化失败: {self.endpoint.name}, 错误: {e}")
            raise ServiceUnavailableError(f"无法连接到服务: {self.endpoint.name}")

    async def _initialize_grpc_client(self) -> None:
        """初始化gRPC客户端"""
        if not GRPC_AVAILABLE:
            raise ServiceUnavailableError("gRPC 不可用，请安装 grpcio 包")

        self._channel = aio_grpc.insecure_channel(
            f"{self.endpoint.host}:{self.endpoint.port}",
            options=[
                ('grpc.keepalive_time_ms', 30000),
                ('grpc.keepalive_timeout_ms', 5000),
                ('grpc.keepalive_permit_without_calls', True),
                ('grpc.http2.max_pings_without_data', 0),
                ('grpc.http2.min_time_between_pings_ms', 10000),
                ('grpc.http2.min_ping_interval_without_data_ms', 300000),
            ],
        )

    async def _initialize_http_client(self) -> None:
        """初始化HTTP客户端"""
        timeout = aiohttp.ClientTimeout(total=self.endpoint.timeout)
        self._client = aiohttp.ClientSession(timeout=timeout)

    @abstractmethod
    async def analyze(self, user_id: str, session_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行分析"""
        pass

    async def health_check(self) -> bool:
        """健康检查"""
        try:
            if self.endpoint.protocol == "http":
                return await self._http_health_check()
            elif self.endpoint.protocol == "grpc":
                return await self._grpc_health_check()
            return False
        except Exception as e:
            logger.warning(f"健康检查失败: {self.endpoint.name}, 错误: {e}")
            return False

    async def _http_health_check(self) -> bool:
        """HTTP健康检查"""
        if not self._client:
            return False

        try:
            url = (
                f"http://{self.endpoint.host}:{self.endpoint.port}{self.endpoint.health_check_path}"
            )
            async with self._client.get(url) as response:
                return response.status == 200
        except Exception:
            return False

    async def _grpc_health_check(self) -> bool:
        """gRPC健康检查"""
        if not GRPC_AVAILABLE or not self._channel:
            return False

        try:
            # 使用gRPC健康检查协议
            from grpc_health.v1 import health_pb2, health_pb2_grpc

            stub = health_pb2_grpc.HealthStub(self._channel)
            request = health_pb2.HealthCheckRequest(service="")

            response = await stub.Check(request, timeout=5)
            return response.status == health_pb2.HealthCheckResponse.SERVING
        except Exception:
            # 如果没有健康检查服务，尝试简单的连接测试
            try:
                await self._channel.channel_ready()
                return True
            except Exception:
                return False

    async def close(self) -> None:
        """关闭客户端"""
        try:
            if self._client:
                await self._client.close()
            if self._channel:
                await self._channel.close()
        except Exception as e:
            logger.warning(f"关闭客户端失败: {self.endpoint.name}, 错误: {e}")


class LookServiceClient(BaseServiceClient):
    """望诊服务客户端"""

    def __init__(self):
        endpoint = ServiceEndpoint(
            name="look-service",
            host=get_settings().external_services.look_service.host,
            port=get_settings().external_services.look_service.port,
            protocol="grpc",
            timeout=30,
        )
        super().__init__(endpoint)

    async def _initialize_grpc_client(self) -> None:
        """初始化gRPC客户端"""
        await super()._initialize_grpc_client()

        # 导入生成的gRPC代码
        try:
            from ..api.grpc import look_service_pb2_grpc

            self._stub = look_service_pb2_grpc.LookServiceStub(self._channel)
        except ImportError:
            logger.warning("望诊服务gRPC代码未找到，使用HTTP客户端")
            self.endpoint.protocol = "http"
            await self._initialize_http_client()

    @retry_with_backoff(max_retries=3)
    async def analyze(self, user_id: str, session_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行望诊分析"""
        try:
            if self.endpoint.protocol == "grpc" and hasattr(self, '_stub'):
                return await self._grpc_analyze(user_id, session_id, data)
            else:
                return await self._http_analyze(user_id, session_id, data)
        except Exception as e:
            logger.error(f"望诊分析失败: {e}")
            raise CommunicationError(f"望诊服务通信失败: {e}")

    async def _grpc_analyze(
        self, user_id: str, session_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """gRPC望诊分析"""
        from ..api.grpc import look_service_pb2

        request = look_service_pb2.LookAnalysisRequest(
            user_id=user_id,
            session_id=session_id,
            image_data=data.get("image_data", b""),
            image_type=data.get("image_type", ""),
            metadata=json.dumps(data.get("metadata", {})),
        )

        response = await self._stub.AnalyzeLook(request, timeout=self.endpoint.timeout)

        return {
            "confidence": response.confidence,
            "features": json.loads(response.features) if response.features else {},
            "tongue_analysis": (
                json.loads(response.tongue_analysis) if response.tongue_analysis else {}
            ),
            "face_analysis": json.loads(response.face_analysis) if response.face_analysis else {},
            "body_analysis": json.loads(response.body_analysis) if response.body_analysis else {},
        }

    async def _http_analyze(
        self, user_id: str, session_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """HTTP望诊分析"""
        url = f"http://{self.endpoint.host}:{self.endpoint.port}/api/v1/analyze"

        payload = {"user_id": user_id, "session_id": session_id, "data": data}

        async with self._client.post(url, json=payload) as response:
            if response.status == 200:
                result = await response.json()
                return result.get("data", {})
            else:
                error_text = await response.text()
                raise CommunicationError(f"HTTP请求失败: {response.status}, {error_text}")


class ListenServiceClient(BaseServiceClient):
    """闻诊服务客户端"""

    def __init__(self):
        endpoint = ServiceEndpoint(
            name="listen-service",
            host=get_settings().external_services.listen_service.host,
            port=get_settings().external_services.listen_service.port,
            protocol="grpc",
            timeout=30,
        )
        super().__init__(endpoint)

    async def _initialize_grpc_client(self) -> None:
        """初始化gRPC客户端"""
        await super()._initialize_grpc_client()

        try:
            from ..api.grpc import listen_service_pb2_grpc

            self._stub = listen_service_pb2_grpc.ListenServiceStub(self._channel)
        except ImportError:
            logger.warning("闻诊服务gRPC代码未找到，使用HTTP客户端")
            self.endpoint.protocol = "http"
            await self._initialize_http_client()

    @retry_with_backoff(max_retries=3)
    async def analyze(self, user_id: str, session_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行闻诊分析"""
        try:
            if self.endpoint.protocol == "grpc" and hasattr(self, '_stub'):
                return await self._grpc_analyze(user_id, session_id, data)
            else:
                return await self._http_analyze(user_id, session_id, data)
        except Exception as e:
            logger.error(f"闻诊分析失败: {e}")
            raise CommunicationError(f"闻诊服务通信失败: {e}")

    async def _grpc_analyze(
        self, user_id: str, session_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """gRPC闻诊分析"""
        from ..api.grpc import listen_service_pb2

        request = listen_service_pb2.ListenAnalysisRequest(
            user_id=user_id,
            session_id=session_id,
            audio_data=data.get("audio_data", b""),
            audio_format=data.get("audio_format", ""),
            metadata=json.dumps(data.get("metadata", {})),
        )

        response = await self._stub.AnalyzeListen(request, timeout=self.endpoint.timeout)

        return {
            "confidence": response.confidence,
            "features": json.loads(response.features) if response.features else {},
            "voice_analysis": (
                json.loads(response.voice_analysis) if response.voice_analysis else {}
            ),
            "breathing_analysis": (
                json.loads(response.breathing_analysis) if response.breathing_analysis else {}
            ),
            "cough_analysis": (
                json.loads(response.cough_analysis) if response.cough_analysis else {}
            ),
        }

    async def _http_analyze(
        self, user_id: str, session_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """HTTP闻诊分析"""
        url = f"http://{self.endpoint.host}:{self.endpoint.port}/api/v1/analyze"

        payload = {"user_id": user_id, "session_id": session_id, "data": data}

        async with self._client.post(url, json=payload) as response:
            if response.status == 200:
                result = await response.json()
                return result.get("data", {})
            else:
                error_text = await response.text()
                raise CommunicationError(f"HTTP请求失败: {response.status}, {error_text}")


class InquiryServiceClient(BaseServiceClient):
    """问诊服务客户端"""

    def __init__(self):
        endpoint = ServiceEndpoint(
            name="inquiry-service",
            host=get_settings().external_services.inquiry_service.host,
            port=get_settings().external_services.inquiry_service.port,
            protocol="grpc",
            timeout=60,  # 问诊可能需要更长时间
        )
        super().__init__(endpoint)

    async def _initialize_grpc_client(self) -> None:
        """初始化gRPC客户端"""
        await super()._initialize_grpc_client()

        try:
            from ..api.grpc import inquiry_service_pb2_grpc

            self._stub = inquiry_service_pb2_grpc.InquiryServiceStub(self._channel)
        except ImportError:
            logger.warning("问诊服务gRPC代码未找到，使用HTTP客户端")
            self.endpoint.protocol = "http"
            await self._initialize_http_client()

    @retry_with_backoff(max_retries=3)
    async def analyze(self, user_id: str, session_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行问诊分析"""
        try:
            if self.endpoint.protocol == "grpc" and hasattr(self, '_stub'):
                return await self._grpc_analyze(user_id, session_id, data)
            else:
                return await self._http_analyze(user_id, session_id, data)
        except Exception as e:
            logger.error(f"问诊分析失败: {e}")
            raise CommunicationError(f"问诊服务通信失败: {e}")

    async def _grpc_analyze(
        self, user_id: str, session_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """gRPC问诊分析"""
        from ..api.grpc import inquiry_service_pb2

        request = inquiry_service_pb2.InquiryAnalysisRequest(
            user_id=user_id,
            session_id=session_id,
            conversation_data=json.dumps(data.get("conversation_data", {})),
            symptoms=data.get("symptoms", []),
            medical_history=json.dumps(data.get("medical_history", {})),
            metadata=json.dumps(data.get("metadata", {})),
        )

        response = await self._stub.AnalyzeInquiry(request, timeout=self.endpoint.timeout)

        return {
            "confidence": response.confidence,
            "features": json.loads(response.features) if response.features else {},
            "conversation_analysis": (
                json.loads(response.conversation_analysis) if response.conversation_analysis else {}
            ),
            "symptom_analysis": (
                json.loads(response.symptom_analysis) if response.symptom_analysis else {}
            ),
            "risk_assessment": (
                json.loads(response.risk_assessment) if response.risk_assessment else {}
            ),
        }

    async def _http_analyze(
        self, user_id: str, session_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """HTTP问诊分析"""
        url = f"http://{self.endpoint.host}:{self.endpoint.port}/api/v1/analyze"

        payload = {"user_id": user_id, "session_id": session_id, "data": data}

        async with self._client.post(url, json=payload) as response:
            if response.status == 200:
                result = await response.json()
                return result.get("data", {})
            else:
                error_text = await response.text()
                raise CommunicationError(f"HTTP请求失败: {response.status}, {error_text}")


class PalpationServiceClient(BaseServiceClient):
    """切诊服务客户端"""

    def __init__(self):
        endpoint = ServiceEndpoint(
            name="palpation-service",
            host=get_settings().external_services.palpation_service.host,
            port=get_settings().external_services.palpation_service.port,
            protocol="grpc",
            timeout=30,
        )
        super().__init__(endpoint)

    async def _initialize_grpc_client(self) -> None:
        """初始化gRPC客户端"""
        await super()._initialize_grpc_client()

        try:
            from ..api.grpc import palpation_service_pb2_grpc

            self._stub = palpation_service_pb2_grpc.PalpationServiceStub(self._channel)
        except ImportError:
            logger.warning("切诊服务gRPC代码未找到，使用HTTP客户端")
            self.endpoint.protocol = "http"
            await self._initialize_http_client()

    @retry_with_backoff(max_retries=3)
    async def analyze(self, user_id: str, session_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行切诊分析"""
        try:
            if self.endpoint.protocol == "grpc" and hasattr(self, '_stub'):
                return await self._grpc_analyze(user_id, session_id, data)
            else:
                return await self._http_analyze(user_id, session_id, data)
        except Exception as e:
            logger.error(f"切诊分析失败: {e}")
            raise CommunicationError(f"切诊服务通信失败: {e}")

    async def _grpc_analyze(
        self, user_id: str, session_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """gRPC切诊分析"""
        from ..api.grpc import palpation_service_pb2

        request = palpation_service_pb2.PalpationAnalysisRequest(
            user_id=user_id,
            session_id=session_id,
            pulse_data=json.dumps(data.get("pulse_data", {})),
            pressure_data=data.get("pressure_data", []),
            sensor_data=json.dumps(data.get("sensor_data", {})),
            metadata=json.dumps(data.get("metadata", {})),
        )

        response = await self._stub.AnalyzePalpation(request, timeout=self.endpoint.timeout)

        return {
            "confidence": response.confidence,
            "features": json.loads(response.features) if response.features else {},
            "pulse_analysis": (
                json.loads(response.pulse_analysis) if response.pulse_analysis else {}
            ),
            "pressure_analysis": (
                json.loads(response.pressure_analysis) if response.pressure_analysis else {}
            ),
            "acupoint_analysis": (
                json.loads(response.acupoint_analysis) if response.acupoint_analysis else {}
            ),
        }

    async def _http_analyze(
        self, user_id: str, session_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """HTTP切诊分析"""
        url = f"http://{self.endpoint.host}:{self.endpoint.port}/api/v1/analyze"

        payload = {"user_id": user_id, "session_id": session_id, "data": data}

        async with self._client.post(url, json=payload) as response:
            if response.status == 200:
                result = await response.json()
                return result.get("data", {})
            else:
                error_text = await response.text()
                raise CommunicationError(f"HTTP请求失败: {response.status}, {error_text}")


class CalculationServiceClient(BaseServiceClient):
    """算诊服务客户端"""

    def __init__(self):
        endpoint = ServiceEndpoint(
            name="calculation-service",
            host=get_settings().external_services.calculation_service.host,
            port=get_settings().external_services.calculation_service.port,
            protocol="grpc",
            timeout=45,  # 算诊可能需要较长计算时间
        )
        super().__init__(endpoint)

    async def _initialize_grpc_client(self) -> None:
        """初始化gRPC客户端"""
        await super()._initialize_grpc_client()

        try:
            from ..api.grpc import calculation_service_pb2_grpc

            self._stub = calculation_service_pb2_grpc.CalculationServiceStub(self._channel)
        except ImportError:
            logger.warning("算诊服务gRPC代码未找到，使用HTTP客户端")
            self.endpoint.protocol = "http"
            await self._initialize_http_client()

    @retry_with_backoff(max_retries=3)
    async def analyze(self, user_id: str, session_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行算诊分析"""
        try:
            if self.endpoint.protocol == "grpc" and hasattr(self, '_stub'):
                return await self._grpc_analyze(user_id, session_id, data)
            else:
                return await self._http_analyze(user_id, session_id, data)
        except Exception as e:
            logger.error(f"算诊分析失败: {e}")
            raise CommunicationError(f"算诊服务通信失败: {e}")

    async def _grpc_analyze(
        self, user_id: str, session_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """gRPC算诊分析"""
        from ..api.grpc import calculation_service_pb2

        request = calculation_service_pb2.CalculationAnalysisRequest(
            user_id=user_id,
            session_id=session_id,
            biomarker_data=json.dumps(data.get("biomarker_data", {})),
            vital_signs=json.dumps(data.get("vital_signs", {})),
            lab_results=json.dumps(data.get("lab_results", {})),
            metadata=json.dumps(data.get("metadata", {})),
        )

        response = await self._stub.AnalyzeCalculation(request, timeout=self.endpoint.timeout)

        return {
            "confidence": response.confidence,
            "features": json.loads(response.features) if response.features else {},
            "biomarker_analysis": (
                json.loads(response.biomarker_analysis) if response.biomarker_analysis else {}
            ),
            "risk_calculation": (
                json.loads(response.risk_calculation) if response.risk_calculation else {}
            ),
            "trend_analysis": (
                json.loads(response.trend_analysis) if response.trend_analysis else {}
            ),
        }

    async def _http_analyze(
        self, user_id: str, session_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """HTTP算诊分析"""
        url = f"http://{self.endpoint.host}:{self.endpoint.port}/api/v1/analyze"

        payload = {"user_id": user_id, "session_id": session_id, "data": data}

        async with self._client.post(url, json=payload) as response:
            if response.status == 200:
                result = await response.json()
                return result.get("data", {})
            else:
                error_text = await response.text()
                raise CommunicationError(f"HTTP请求失败: {response.status}, {error_text}")


class ServiceClientManager:
    """服务客户端管理器"""

    def __init__(self):
        self.clients = {}
        self.settings = get_settings()

    async def initialize(self) -> None:
        """初始化所有服务客户端"""
        logger.info("初始化服务客户端管理器...")

        # 创建客户端实例
        client_classes = {
            "look": LookServiceClient,
            "listen": ListenServiceClient,
            "inquiry": InquiryServiceClient,
            "palpation": PalpationServiceClient,
            "calculation": CalculationServiceClient,
        }

        # 并行初始化所有客户端
        init_tasks = []
        for service_name, client_class in client_classes.items():
            try:
                client = client_class()
                self.clients[service_name] = client
                init_tasks.append(client.initialize())
            except Exception as e:
                logger.error(f"创建{service_name}客户端失败: {e}")

        # 等待所有客户端初始化完成
        if init_tasks:
            results = await asyncio.gather(*init_tasks, return_exceptions=True)

            # 检查初始化结果
            for i, result in enumerate(results):
                service_name = list(client_classes.keys())[i]
                if isinstance(result, Exception):
                    logger.error(f"{service_name}服务客户端初始化失败: {result}")
                    # 移除失败的客户端
                    if service_name in self.clients:
                        del self.clients[service_name]
                else:
                    logger.info(f"{service_name}服务客户端初始化成功")

        logger.info(f"服务客户端管理器初始化完成，可用服务: {list(self.clients.keys())}")

    def get_client(self, service_name: str) -> Optional[BaseServiceClient]:
        """获取服务客户端"""
        return self.clients.get(service_name)

    async def health_check_all(self) -> Dict[str, bool]:
        """检查所有服务健康状态"""
        health_status = {}

        if not self.clients:
            return health_status

        # 并行检查所有服务
        check_tasks = []
        service_names = []

        for service_name, client in self.clients.items():
            check_tasks.append(client.health_check())
            service_names.append(service_name)

        results = await asyncio.gather(*check_tasks, return_exceptions=True)

        for i, result in enumerate(results):
            service_name = service_names[i]
            if isinstance(result, Exception):
                health_status[service_name] = False
                logger.warning(f"{service_name}服务健康检查异常: {result}")
            else:
                health_status[service_name] = result

        return health_status

    async def close_all(self) -> None:
        """关闭所有客户端"""
        if not self.clients:
            return

        close_tasks = []
        for client in self.clients.values():
            close_tasks.append(client.close())

        await asyncio.gather(*close_tasks, return_exceptions=True)
        self.clients.clear()

        logger.info("所有服务客户端已关闭")

    def get_available_services(self) -> List[str]:
        """获取可用服务列表"""
        return list(self.clients.keys())

    async def test_service_connectivity(self, service_name: str) -> Dict[str, Any]:
        """测试特定服务的连接性"""
        client = self.get_client(service_name)
        if not client:
            return {"service": service_name, "available": False, "error": "客户端未找到"}

        try:
            # 执行健康检查
            is_healthy = await client.health_check()

            # 尝试简单的测试调用
            test_result = None
            try:
                test_data = {"test": True, "timestamp": datetime.now().isoformat()}
                test_result = await client.analyze("test_user", "test_session", test_data)
            except Exception as e:
                test_result = {"error": str(e)}

            return {
                "service": service_name,
                "available": is_healthy,
                "health_check": is_healthy,
                "test_call": test_result,
                "endpoint": {
                    "host": client.endpoint.host,
                    "port": client.endpoint.port,
                    "protocol": client.endpoint.protocol,
                },
            }

        except Exception as e:
            return {"service": service_name, "available": False, "error": str(e)}
