from fastapi import Depends
from functools import lru_cache

from app.core.config import get_settings
from app.repositories.neo4j_repository import Neo4jRepository
from app.services.knowledge_service import KnowledgeService
from app.services.knowledge_graph_service import KnowledgeGraphService


@lru_cache()
def get_neo4j_repository():
    """获取Neo4j仓库实例"""
    settings = get_settings()
    return Neo4jRepository(settings.database)


def get_knowledge_service(
    repository: Neo4jRepository = Depends(get_neo4j_repository),
) -> KnowledgeService:
    """获取知识服务实例"""
    return KnowledgeService(repository)


def get_knowledge_graph_service(
    repository: Neo4jRepository = Depends(get_neo4j_repository),
) -> KnowledgeGraphService:
    """获取知识图谱服务实例"""
    return KnowledgeGraphService(repository) 