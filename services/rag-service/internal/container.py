#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
依赖注入容器，管理RAG服务的所有组件依赖
"""

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject
from typing import Dict, Any

from .service.rag_service import RagService
from .service.embedding_service import EmbeddingService
from .service.cache_service import CacheService
from .service.kg_integration_service import KnowledgeGraphIntegrationService
from .service.health_check import HealthCheckService
from .retriever.hybrid_retriever import HybridRetriever
from .retriever.kg_enhanced_retriever import KGEnhancedRetriever
from .generator.openai_generator import OpenAIGenerator
from .generator.local_generator import LocalGenerator
from .repository.milvus_repository import MilvusRepository
from .observability.metrics import MetricsCollector
from .observability.tracer import TracingService
from .resilience.circuit_breaker import CircuitBreakerService
from .tcm.syndrome_analyzer import SyndromeAnalyzer
from .tcm.herb_recommender import HerbRecommender
from .tcm.pulse_analyzer import PulseAnalyzer


class Container(containers.DeclarativeContainer):
    """依赖注入容器"""
    
    # 配置
    config = providers.Configuration()
    
    # 基础设施组件
    milvus_repository = providers.Singleton(
        MilvusRepository,
        config=config.vector_database
    )
    
    cache_service = providers.Singleton(
        CacheService,
        config=config.cache
    )
    
    # 可观测性组件
    metrics_collector = providers.Singleton(
        MetricsCollector,
        config=config.observability.metrics
    )
    
    tracing_service = providers.Singleton(
        TracingService,
        config=config.observability.tracing
    )
    
    # 弹性组件
    circuit_breaker_service = providers.Singleton(
        CircuitBreakerService,
        config=config.resilience.circuit_breaker
    )
    
    # 嵌入服务
    embedding_service = providers.Singleton(
        EmbeddingService,
        config=config.embedding,
        metrics_collector=metrics_collector,
        circuit_breaker=circuit_breaker_service
    )
    
    # 检索器（根据配置选择）
    retriever = providers.Factory(
        lambda config, milvus_repo, embedding_svc, metrics, cb: (
            KGEnhancedRetriever(config, milvus_repo, embedding_svc, metrics, cb)
            if config.get('knowledge_graph', {}).get('enabled', False)
            else HybridRetriever(config, milvus_repo, embedding_svc, metrics, cb)
        ),
        config=config.retriever,
        milvus_repo=milvus_repository,
        embedding_svc=embedding_service,
        metrics=metrics_collector,
        cb=circuit_breaker_service
    )
    
    # 生成器（根据配置选择）
    generator = providers.Factory(
        lambda config, metrics, cb: (
            LocalGenerator(config, metrics, cb)
            if config.get('model_type') == 'local'
            else OpenAIGenerator(config, metrics, cb)
        ),
        config=config.generator,
        metrics=metrics_collector,
        cb=circuit_breaker_service
    )
    
    # 中医特色组件
    syndrome_analyzer = providers.Singleton(
        SyndromeAnalyzer,
        config=config.tcm.syndrome_analysis,
        embedding_service=embedding_service
    )
    
    herb_recommender = providers.Singleton(
        HerbRecommender,
        config=config.tcm.herb_recommendation,
        embedding_service=embedding_service
    )
    
    pulse_analyzer = providers.Singleton(
        PulseAnalyzer,
        config=config.tcm.pulse_analysis
    )
    
    # 知识图谱集成服务
    kg_integration_service = providers.Singleton(
        KnowledgeGraphIntegrationService,
        config=config.knowledge_graph,
        syndrome_analyzer=syndrome_analyzer,
        herb_recommender=herb_recommender
    )
    
    # 健康检查服务
    health_check_service = providers.Singleton(
        HealthCheckService,
        milvus_repository=milvus_repository,
        cache_service=cache_service,
        embedding_service=embedding_service
    )
    
    # 主要RAG服务
    rag_service = providers.Singleton(
        RagService,
        config=config,
        milvus_repository=milvus_repository,
        embedding_service=embedding_service,
        retriever=retriever,
        generator=generator,
        cache_service=cache_service,
        kg_integration_service=kg_integration_service,
        syndrome_analyzer=syndrome_analyzer,
        herb_recommender=herb_recommender,
        pulse_analyzer=pulse_analyzer,
        metrics_collector=metrics_collector,
        tracing_service=tracing_service,
        circuit_breaker_service=circuit_breaker_service
    )


def create_container(config: Dict[str, Any]) -> Container:
    """
    创建并配置依赖注入容器
    
    Args:
        config: 配置字典
        
    Returns:
        配置好的容器实例
    """
    container = Container()
    container.config.from_dict(config)
    
    # 配置模块的依赖注入
    container.wire(modules=[
        "services.rag_service.internal.service",
        "services.rag_service.internal.delivery",
        "services.rag_service.cmd.server"
    ])
    
    return container


# 全局容器实例
container: Container = None


def get_container() -> Container:
    """获取全局容器实例"""
    global container
    if container is None:
        raise RuntimeError("Container not initialized. Call create_container() first.")
    return container


def init_container(config: Dict[str, Any]) -> None:
    """初始化全局容器"""
    global container
    container = create_container(config) 