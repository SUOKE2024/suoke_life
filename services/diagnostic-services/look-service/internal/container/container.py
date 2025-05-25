#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
依赖注入容器

管理所有服务依赖，提供统一的依赖注入和生命周期管理。
"""

import os
import asyncio
from typing import Dict, Any, Optional, TypeVar, Type, Callable
from dataclasses import dataclass
from contextlib import asynccontextmanager

import redis.asyncio as redis
from structlog import get_logger

from config.config import get_config
from internal.analysis.face_analyzer import FaceAnalyzer
from internal.analysis.body_analyzer import BodyAnalyzer
from internal.analysis.tongue_analyzer import TongueAnalyzer
from internal.analysis.image_quality_assessor import ImageQualityAssessor
from internal.model.model_factory import ModelFactory
from internal.repository.analysis_repository import AnalysisRepository
from internal.integration.xiaoai_client import XiaoaiServiceClient
from internal.service.cache_service import CacheService
from internal.service.metrics_service import MetricsService
from internal.service.notification_service import NotificationService
from internal.service.task_processor import AsyncTaskProcessor
from internal.service.validation_service import validation_service, serialization_service
from internal.service.resilience_service import ResilienceService, PresetConfigs

logger = get_logger()

T = TypeVar('T')


@dataclass
class ServiceHealth:
    """服务健康状态"""
    name: str
    status: str
    last_check: float
    details: Dict[str, Any]


class Container:
    """
    依赖注入容器
    
    负责管理所有服务依赖的创建、配置和生命周期。
    支持单例模式、工厂模式和异步初始化。
    """
    
    def __init__(self):
        self._instances: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._config = get_config()
        self._initialized = False
        self._health_status: Dict[str, ServiceHealth] = {}
        
    async def initialize(self):
        """异步初始化容器"""
        if self._initialized:
            return
            
        logger.info("开始初始化依赖注入容器")
        
        try:
            # 初始化核心服务
            await self._register_core_services()
            
            # 初始化分析器
            await self._init_analyzers()
            
            # 初始化存储库
            await self._init_repositories()
            
            # 初始化外部集成
            await self._init_integrations()
            
            self._initialized = True
            logger.info("依赖注入容器初始化完成")
            
        except Exception as e:
            logger.error("依赖注入容器初始化失败", error=str(e))
            raise
    
    async def _register_core_services(self):
        """注册核心服务"""
        try:
            # 缓存服务
            cache_config = self._config.get("cache", {})
            cache_service = CacheService(cache_config)
            await cache_service.initialize()
            self._instances["cache_service"] = cache_service
            
            # 健康检查
            self._health_status["cache"] = ServiceHealth(
                name="cache",
                status="healthy",
                last_check=asyncio.get_event_loop().time(),
                details={"type": "redis", "host": cache_config.get("redis", {}).get("host")}
            )
            
            # 监控指标服务
            metrics_config = self._config.get("monitoring", {})
            metrics_service = MetricsService(metrics_config)
            await metrics_service.initialize()
            self._instances["metrics_service"] = metrics_service
            
            self._health_status["metrics"] = ServiceHealth(
                name="metrics",
                status="healthy",
                last_check=asyncio.get_event_loop().time(),
                details={"prometheus_enabled": metrics_config.get("prometheus", {}).get("enabled", True)}
            )
            
            # 通知服务
            notification_config = self._config.get("notification", {})
            notification_service = NotificationService(notification_config)
            await notification_service.initialize()
            self._instances["notification_service"] = notification_service
            
            self._health_status["notification"] = ServiceHealth(
                name="notification",
                status="healthy",
                last_check=asyncio.get_event_loop().time(),
                details={"enabled": notification_config.get("enabled", True)}
            )
            
            # 验证服务（全局单例）
            self.register("validation_service", validation_service)
            self.register("serialization_service", serialization_service)
            
            # 任务处理器
            task_config = self._config.get("task_processor", {
                "max_workers": 10,
                "queue_size": 1000,
                "cleanup_interval": 300,
                "max_result_age": 3600
            })
            task_processor = AsyncTaskProcessor(task_config)
            await task_processor.initialize()
            self._instances["task_processor"] = task_processor
            
            # 弹性服务
            analysis_resilience = PresetConfigs.analysis_resilience()
            external_resilience = PresetConfigs.external_service_resilience()
            self._instances["analysis_resilience"] = analysis_resilience
            self._instances["external_resilience"] = external_resilience
            
            logger.info("核心服务注册完成")
            
        except Exception as e:
            logger.error("核心服务注册失败", error=str(e))
            raise
    
    async def _init_analyzers(self):
        """初始化分析器"""
        model_config = self._config.get("models", {})
        
        # 模型工厂
        model_factory = ModelFactory(model_config)
        await model_factory.initialize()
        self._instances["model_factory"] = model_factory
        
        # 图像质量评估器
        quality_config = model_config.get("image_quality", {})
        image_quality_assessor = ImageQualityAssessor(
            model_path=quality_config.get("model_path", "./models/image_quality.onnx"),
            device=quality_config.get("device", "cpu"),
            confidence_threshold=quality_config.get("confidence_threshold", 0.7)
        )
        self._instances["image_quality_assessor"] = image_quality_assessor
        
        # 面色分析器
        face_config = model_config.get("face_analysis", {})
        face_analyzer = FaceAnalyzer(
            model_path=face_config.get("model_path", "./models/face_analysis.onnx"),
            device=face_config.get("device", "cpu"),
            confidence_threshold=face_config.get("confidence_threshold", 0.7),
            input_size=tuple(face_config.get("input_size", [224, 224])),
            batch_size=face_config.get("batch_size", 1),
            quantized=face_config.get("quantized", False)
        )
        self._instances["face_analyzer"] = face_analyzer
        
        # 形体分析器
        body_config = model_config.get("body_analysis", {})
        body_analyzer = BodyAnalyzer(
            model_path=body_config.get("model_path", "./models/body_analysis.onnx"),
            device=body_config.get("device", "cpu"),
            confidence_threshold=body_config.get("confidence_threshold", 0.7)
        )
        self._instances["body_analyzer"] = body_analyzer
        
        # 舌象分析器
        tongue_config = model_config.get("tongue_analysis", {})
        tongue_analyzer = TongueAnalyzer(
            model_path=tongue_config.get("model_path", "./models/tongue_analysis.onnx"),
            device=tongue_config.get("device", "cpu"),
            confidence_threshold=tongue_config.get("confidence_threshold", 0.7)
        )
        self._instances["tongue_analyzer"] = tongue_analyzer
        
        self._health_status["analyzers"] = ServiceHealth(
            name="analyzers",
            status="healthy",
            last_check=asyncio.get_event_loop().time(),
            details={
                "face_analyzer": True,
                "body_analyzer": True,
                "tongue_analyzer": True,
                "image_quality_assessor": True
            }
        )
    
    async def _init_repositories(self):
        """初始化存储库"""
        db_config = self._config.get("database", {})
        analysis_repository = AnalysisRepository(db_config)
        await analysis_repository.initialize()
        self._instances["analysis_repository"] = analysis_repository
        
        self._health_status["database"] = ServiceHealth(
            name="database",
            status="healthy",
            last_check=asyncio.get_event_loop().time(),
            details={"type": "sqlite", "path": db_config.get("path", "./data/analysis.db")}
        )
    
    async def _init_integrations(self):
        """初始化外部集成"""
        xiaoai_config = self._config.get("integration", {}).get("xiaoai_service", {})
        
        if xiaoai_config.get("enabled", True):
            xiaoai_client = XiaoaiServiceClient(
                host=xiaoai_config.get("host", "xiaoai-service"),
                port=xiaoai_config.get("port", 50050),
                timeout=xiaoai_config.get("timeout", 30),
                max_retries=xiaoai_config.get("max_retries", 3)
            )
            await xiaoai_client.initialize()
            self._instances["xiaoai_client"] = xiaoai_client
            
            self._health_status["xiaoai_integration"] = ServiceHealth(
                name="xiaoai_integration",
                status="healthy",
                last_check=asyncio.get_event_loop().time(),
                details={"host": xiaoai_config.get("host"), "port": xiaoai_config.get("port")}
            )
    
    def get(self, service_name: str, service_type: Type[T] = None) -> T:
        """获取服务实例"""
        if not self._initialized:
            raise RuntimeError("容器尚未初始化")
            
        if service_name not in self._instances:
            raise KeyError(f"服务 {service_name} 未注册")
            
        return self._instances[service_name]
    
    def register(self, service_name: str, instance: Any):
        """注册服务实例"""
        self._instances[service_name] = instance
        logger.info("服务已注册", service_name=service_name, type=type(instance).__name__)
    
    def register_factory(self, service_name: str, factory: Callable):
        """注册服务工厂"""
        self._factories[service_name] = factory
        logger.info("服务工厂已注册", service_name=service_name)
    
    async def health_check(self) -> Dict[str, ServiceHealth]:
        """执行健康检查"""
        current_time = asyncio.get_event_loop().time()
        
        # 检查缓存服务
        if "cache_service" in self._instances:
            try:
                cache_service = self._instances["cache_service"]
                await cache_service.ping()
                self._health_status["cache"].status = "healthy"
                self._health_status["cache"].last_check = current_time
            except Exception as e:
                self._health_status["cache"].status = "unhealthy"
                self._health_status["cache"].details["error"] = str(e)
        
        # 检查数据库
        if "analysis_repository" in self._instances:
            try:
                repository = self._instances["analysis_repository"]
                await repository.health_check()
                self._health_status["database"].status = "healthy"
                self._health_status["database"].last_check = current_time
            except Exception as e:
                self._health_status["database"].status = "unhealthy"
                self._health_status["database"].details["error"] = str(e)
        
        # 检查外部集成
        if "xiaoai_client" in self._instances:
            try:
                xiaoai_client = self._instances["xiaoai_client"]
                await xiaoai_client.health_check()
                self._health_status["xiaoai_integration"].status = "healthy"
                self._health_status["xiaoai_integration"].last_check = current_time
            except Exception as e:
                self._health_status["xiaoai_integration"].status = "unhealthy"
                self._health_status["xiaoai_integration"].details["error"] = str(e)
        
        return self._health_status
    
    async def shutdown(self):
        """关闭容器，清理资源"""
        logger.info("开始关闭依赖注入容器")
        
        # 关闭缓存服务
        if "cache_service" in self._instances:
            try:
                await self._instances["cache_service"].close()
            except Exception as e:
                logger.error("关闭缓存服务失败", error=str(e))
        
        # 关闭数据库连接
        if "analysis_repository" in self._instances:
            try:
                await self._instances["analysis_repository"].close()
            except Exception as e:
                logger.error("关闭数据库连接失败", error=str(e))
        
        # 关闭外部集成
        if "xiaoai_client" in self._instances:
            try:
                await self._instances["xiaoai_client"].close()
            except Exception as e:
                logger.error("关闭小艾客户端失败", error=str(e))
        
        self._instances.clear()
        self._initialized = False
        logger.info("依赖注入容器已关闭")


# 全局容器实例
_container: Optional[Container] = None


def get_container() -> Container:
    """获取全局容器实例"""
    global _container
    if _container is None:
        _container = Container()
    return _container


@asynccontextmanager
async def container_context():
    """容器上下文管理器"""
    container = get_container()
    try:
        await container.initialize()
        yield container
    finally:
        await container.shutdown() 