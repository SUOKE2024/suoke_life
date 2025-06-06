"""
base - 索克生活项目模块
"""

from .exceptions import InquiryServiceError, ValidationError
from .metrics import MetricsCollector
from dataclasses import dataclass
from datetime import datetime
from typing import Any
import abc
import logging

#!/usr/bin/env python

"""
基础类和接口定义
"""




@dataclass
class SymptomInfo:
    """症状信息数据类"""

    name: str
    confidence: float
    severity: str = "unknown"
    duration: int = 0  # 持续时间（天）
    body_location: str | None = None
    context: dict[str, Any] | None = None
    extracted_at: datetime = None

    def __post_init__(self):
        if self.extracted_at is None:
            self.extracted_at = datetime.now()


@dataclass
class TCMPattern:
    """中医证型信息数据类"""

    name: str
    category: str
    confidence: float
    symptoms: list[str]
    description: str | None = None
    treatment_suggestions: list[str] | None = None


@dataclass
class HealthRisk:
    """健康风险信息数据类"""

    name: str
    probability: float
    severity: str
    time_frame: str
    description: str | None = None
    prevention_strategies: list[str] | None = None


class BaseService(abc.ABC):
    """服务基类"""

    def __init__(self, config: dict[str, Any], metrics: MetricsCollector | None = None):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.metrics = metrics or MetricsCollector()
        self._initialized = False

    async def initialize(self) -> None:
        """初始化服务"""
        if self._initialized:
            return

        try:
            await self._do_initialize()
            self._initialized = True
            self.logger.info(f"{self.__class__.__name__} 初始化完成")
        except Exception as e:
            self.logger.error(f"{self.__class__.__name__} 初始化失败: {e!s}")
            raise InquiryServiceError(f"服务初始化失败: {e!s}")

    @abc.abstractmethod
    async def _do_initialize(self) -> None:
        """子类实现的初始化逻辑"""
        pass

    async def health_check(self) -> bool:
        """健康检查"""
        try:
            return await self._do_health_check()
        except Exception as e:
            self.logger.error(f"健康检查失败: {e!s}")
            return False

    @abc.abstractmethod
    async def _do_health_check(self) -> bool:
        """子类实现的健康检查逻辑"""
        pass

    def _validate_initialized(self) -> None:
        """验证服务是否已初始化"""
        if not self._initialized:
            raise InquiryServiceError(f"{self.__class__.__name__} 尚未初始化")


class BaseExtractor(BaseService):
    """提取器基类"""

    @abc.abstractmethod
    async def extract(self, text: str, **kwargs) -> dict[str, Any]:
        """提取信息的抽象方法"""
        pass

    def _validate_text_input(self, text: str) -> None:
        """验证文本输入"""
        if not text or not isinstance(text, str):
            raise ValidationError("输入文本不能为空且必须是字符串类型")

        if len(text.strip()) == 0:
            raise ValidationError("输入文本不能为空白字符")

        max_length = self.config.get("max_text_length", 10000)
        if len(text) > max_length:
            raise ValidationError(f"输入文本长度不能超过 {max_length} 个字符")


class BaseMapper(BaseService):
    """映射器基类"""

    @abc.abstractmethod
    async def map(self, input_data: Any, **kwargs) -> dict[str, Any]:
        """映射数据的抽象方法"""
        pass


class BaseAssessor(BaseService):
    """评估器基类"""

    @abc.abstractmethod
    async def assess(self, data: dict[str, Any], **kwargs) -> dict[str, Any]:
        """评估数据的抽象方法"""
        pass


class AsyncContextManager:
    """异步上下文管理器基类"""

    async def __aenter__(self):
        await self.setup()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()

    @abc.abstractmethod
    async def setup(self) -> None:
        """设置资源"""
        pass

    @abc.abstractmethod
    async def cleanup(self) -> None:
        """清理资源"""
        pass


class ServiceRegistry:
    """服务注册表"""

    def __init__(self):
        self._services: dict[str, BaseService] = {}
        self._logger = logging.getLogger(self.__class__.__name__)

    def register(self, name: str, service: BaseService) -> None:
        """注册服务"""
        if name in self._services:
            self._logger.warning(f"服务 {name} 已存在，将被覆盖")

        self._services[name] = service
        self._logger.info(f"服务 {name} 注册成功")

    def get(self, name: str) -> BaseService | None:
        """获取服务"""
        return self._services.get(name)

    def get_required(self, name: str) -> BaseService:
        """获取必需的服务，如果不存在则抛出异常"""
        service = self.get(name)
        if service is None:
            raise InquiryServiceError(f"必需的服务 {name} 未注册")
        return service

    async def initialize_all(self) -> None:
        """初始化所有服务"""
        for name, service in self._services.items():
            try:
                await service.initialize()
            except Exception as e:
                self._logger.error(f"初始化服务 {name} 失败: {e!s}")
                raise

    async def health_check_all(self) -> dict[str, bool]:
        """检查所有服务的健康状态"""
        results = {}
        for name, service in self._services.items():
            try:
                results[name] = await service.health_check()
            except Exception as e:
                self._logger.error(f"服务 {name} 健康检查失败: {e!s}")
                results[name] = False

        return results

    def list_services(self) -> list[str]:
        """列出所有注册的服务"""
        return list(self._services.keys())


# 全局服务注册表实例
service_registry = ServiceRegistry()
