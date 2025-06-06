"""
dependencies - 索克生活项目模块
"""

from fastapi import Depends, Request
from internal.agent.agent_manager import AgentManager
from internal.community.community_service import CommunityService
from internal.knowledge.knowledge_service import KnowledgeService
from internal.repository.community_repository import CommunityRepository
from internal.repository.knowledge_repository import KnowledgeRepository
from internal.repository.session_repository import SessionRepository
from pkg.utils.config import Config
from pkg.utils.metrics import MetricsCollector
import logging

#!/usr/bin/env python

"""
老克智能体服务 - 依赖注入模块
提供FastAPI应用中使用的依赖注入函数
"""




logger = logging.getLogger(__name__)

# 全局实例，只初始化一次
_agent_manager: AgentManager | None = None
_session_repository: SessionRepository | None = None
_knowledge_repository: KnowledgeRepository | None = None
_community_repository: CommunityRepository | None = None
_knowledge_service: KnowledgeService | None = None
_community_service: CommunityService | None = None
_metrics_collector: MetricsCollector | None = None
_config: Config | None = None

def get_config() -> Config:
    """获取配置实例"""
    global _config
    if _config is None:
        _config = Config()
    return _config

def get_metrics_collector() -> MetricsCollector:
    """获取指标收集器实例"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector("laoke_service")
    return _metrics_collector

def get_session_repository() -> SessionRepository:
    """获取会话存储库实例"""
    global _session_repository
    if _session_repository is None:
        _session_repository = SessionRepository()
    return _session_repository

def get_knowledge_repository() -> KnowledgeRepository:
    """获取知识库存储库实例"""
    global _knowledge_repository
    if _knowledge_repository is None:
        _knowledge_repository = KnowledgeRepository()
    return _knowledge_repository

def get_community_repository() -> CommunityRepository:
    """获取社区存储库实例"""
    global _community_repository
    if _community_repository is None:
        _community_repository = CommunityRepository()
    return _community_repository

def get_knowledge_service(
    request: Request = None,
    knowledge_repository: KnowledgeRepository = Depends(get_knowledge_repository)
) -> KnowledgeService:
    """获取知识服务实例"""
    global _knowledge_service
    if _knowledge_service is None:
        _knowledge_service = KnowledgeService(
            repository=knowledge_repository
        )
    return _knowledge_service

def get_community_service(
    request: Request = None,
    community_repository: CommunityRepository = Depends(get_community_repository)
) -> CommunityService:
    """获取社区服务实例"""
    global _community_service
    if _community_service is None:
        _community_service = CommunityService(
            repository=community_repository
        )
    return _community_service

def get_agent_manager(
    request: Request = None,
    session_repository: SessionRepository = Depends(get_session_repository),
    knowledge_repository: KnowledgeRepository = Depends(get_knowledge_repository)
) -> AgentManager:
    """获取智能体管理器实例"""
    global _agent_manager
    if _agent_manager is None:
        _agent_manager = AgentManager(
            session_repository=session_repository,
            knowledge_repository=knowledge_repository
        )
    return _agent_manager

async def shutdown_resources():
    """关闭资源连接"""
    global _agent_manager
    if _agent_manager:
        await _agent_manager.close()
        _agent_manager = None
        logger.info("已关闭智能体管理器")

    # 关闭其他资源
    # TODO: 实现其他资源的关闭逻辑
