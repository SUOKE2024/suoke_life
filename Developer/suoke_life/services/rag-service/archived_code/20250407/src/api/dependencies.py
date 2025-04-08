from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from utils.dictionary import Dictionary
from retrievers.retriever import Retriever
from knowledge_graph.knowledge_graph import KnowledgeGraph
from retrievers.keyword_search import KeywordSearcher
from retrievers.reranker import Reranker

@lru_cache()
def get_dictionary() -> Dictionary:
    """获取词典单例"""
    return Dictionary()

@lru_cache()
def get_knowledge_graph() -> KnowledgeGraph:
    """获取知识图谱单例"""
    # 这里应从配置中获取连接信息
    return KnowledgeGraph(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="password"
    )
    
@lru_cache()
def get_keyword_searcher() -> KeywordSearcher:
    """获取关键词搜索器单例"""
    return KeywordSearcher()
    
@lru_cache()
def get_reranker() -> Reranker:
    """获取重排序器单例"""
    return Reranker()
    
@lru_cache()
def get_retriever(
    kg: Annotated[KnowledgeGraph, Depends(get_knowledge_graph)],
    keyword_searcher: Annotated[KeywordSearcher, Depends(get_keyword_searcher)],
    reranker: Annotated[Reranker, Depends(get_reranker)]
) -> Retriever:
    """获取检索器单例"""
    return Retriever(
        knowledge_graph=kg,
        keyword_searcher=keyword_searcher,
        reranker=reranker
    ) 