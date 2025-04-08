#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
索克生活APP - RAG服务配置
=======================
包含所有RAG服务的配置参数
"""

import os
import yaml
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# 服务基本配置
SERVICE_NAME = "索克生活RAG服务"
VERSION = os.environ.get("RAG_VERSION", "2.0.0")
API_PREFIX = "/api"

# 环境配置
ENVIRONMENT = os.environ.get("RAG_ENV", "production")
DEBUG = os.environ.get("RAG_DEBUG", "false").lower() == "true"
LOG_LEVEL = os.environ.get("RAG_LOG_LEVEL", "INFO").upper()

# 服务端口
PORT = int(os.environ.get("RAG_PORT", "8000"))
HOST = os.environ.get("RAG_HOST", "0.0.0.0")
WORKERS = int(os.environ.get("RAG_WORKERS", "1"))
THREADS = int(os.environ.get("RAG_THREADS", "4"))

# Redis配置
REDIS_URL = os.environ.get("RAG_REDIS_URL", "redis://redis:6379/0")
REDIS_TTL = int(os.environ.get("RAG_REDIS_TTL", "3600"))

# MongoDB配置
MONGODB_URI = os.environ.get("RAG_MONGODB_URI", "mongodb://mongodb:27017/")
MONGODB_DB = os.environ.get("RAG_MONGODB_DB", "suoke_life")
MONGODB_COLLECTION = os.environ.get("RAG_MONGODB_COLLECTION", "rag_data")

# 向量数据库配置
VECTOR_DB_TYPE = os.environ.get("RAG_VECTOR_DB_TYPE", "chroma")  # chroma, faiss, qdrant, milvus
VECTOR_DB_PATH = os.environ.get("RAG_VECTOR_DB_PATH", "/app/data/vectors")
VECTOR_DB_COLLECTION = os.environ.get("RAG_VECTOR_DB_COLLECTION", "suoke_vectors")
VECTOR_DIMENSION = int(os.environ.get("RAG_VECTOR_DIMENSION", "768"))

# Qdrant配置
QDRANT_URL = os.environ.get("QDRANT_URL", "http://qdrant:6333")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", "0"))
QDRANT_COLLECTION_NAME = os.environ.get("QDRANT_COLLECTION_NAME", "suoke_vectors")

# Milvus配置
MILVUS_URI = os.environ.get("MILVUS_URI", "http://milvus:19530")
MILVUS_COLLECTION_NAME = os.environ.get("MILVUS_COLLECTION_NAME", "suoke_vectors")

# 模型配置
ENABLE_LOCAL_MODELS = os.environ.get("ENABLE_LOCAL_MODELS", "true").lower() == "true"
MODEL_CACHE_DIR = os.environ.get("MODEL_CACHE_DIR", "/app/models/cache")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "BAAI/bge-small-zh")
EMBEDDING_MODEL_KWARGS = {
    "device": os.environ.get("EMBEDDING_DEVICE", "cpu"),
    "max_length": int(os.environ.get("EMBEDDING_MAX_LENGTH", "512"))
}

# RAG配置
TOP_K = int(os.environ.get("TOP_K", "5"))
SIMILARITY_THRESHOLD = float(os.environ.get("SIMILARITY_THRESHOLD", "0.7"))

# 重排序配置
RERANK_ENABLED = os.environ.get("RERANK_ENABLED", "true").lower() == "true"
RERANK_TYPE = os.environ.get("RERANK_TYPE", "bge")  # bge, cross_encoder, ensemble
RERANK_MODEL = os.environ.get("RERANK_MODEL", "BAAI/bge-reranker-base")
RERANK_TOP_N = int(os.environ.get("RERANK_TOP_N", "10"))

# LLM客户端配置
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "openai")  # openai, zhipu, baidu, alibaba, local
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_API_BASE = os.environ.get("LLM_API_BASE", "")
LLM_MODEL_NAME = os.environ.get("LLM_MODEL_NAME", "gpt-3.5-turbo")
LLM_MAX_TOKENS = int(os.environ.get("LLM_MAX_TOKENS", "4096"))
LLM_TEMPERATURE = float(os.environ.get("LLM_TEMPERATURE", "0.7"))

# 路径配置
DATA_DIR = "/app/data"
LOGS_DIR = "/app/logs"
CONFIG_DIR = "/app/config"
MODELS_DIR = "/app/models"

# 健康检查配置
HEALTH_CHECK_DEPENDENCIES = ["redis", "mongodb", "vector_db"]

# 安全配置
JWT_SECRET = os.environ.get("JWT_SECRET", "default_secret_key_change_in_production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY = int(os.environ.get("JWT_EXPIRY", "86400"))  # 24小时

# 跨域配置
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")

# 缓存配置
CACHE_ENABLED = os.environ.get("CACHE_ENABLED", "true").lower() == "true"
CACHE_TTL = int(os.environ.get("CACHE_TTL", "3600"))  # 1小时
CACHE_MAX_ENTRIES = int(os.environ.get("CACHE_MAX_ENTRIES", "1000"))

# 限流配置
RATE_LIMIT_ENABLED = os.environ.get("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT = int(os.environ.get("RATE_LIMIT", "60"))  # 每分钟请求数
RATE_LIMIT_PERIOD = int(os.environ.get("RATE_LIMIT_PERIOD", "60"))  # 时间窗口(秒)

# 中文特定配置
CHINESE_SEGMENTATION = os.environ.get("CHINESE_SEGMENTATION", "jieba")  # jieba, pkuseg

# HTTP请求配置
REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", "30"))  # 秒
MAX_REQUEST_SIZE_MB = int(os.environ.get("MAX_REQUEST_SIZE_MB", "50"))  # MB

# Gunicorn配置
WORKER_CLASS = os.environ.get("WORKER_CLASS", "gthread")
WORKER_TIMEOUT = int(os.environ.get("WORKER_TIMEOUT", "120"))
WORKER_KEEPALIVE = int(os.environ.get("WORKER_KEEPALIVE", "5"))

DEFAULT_CONFIG = {
    "app": {
        "name": "rag-service",
        "port": PORT,
        "log_level": LOG_LEVEL
    },
    "web_search": {
        "api_keys": {
            "brave": os.environ.get("RAG_BRAVE_API_KEY", ""),
            "google": os.environ.get("RAG_GOOGLE_API_KEY", "")
        },
        "search": {
            "default_engine": "brave",
            "max_results": TOP_K,
            "timeout": REQUEST_TIMEOUT
        },
        "content": {
            "summarization_enabled": True,
            "max_summary_length": 200,
            "translation_enabled": False,
            "target_language": "zh",
            "filtering_enabled": True,
            "blocked_domains": ["spam.com", "ads.example.com"]
        },
        "knowledge": {
            "knowledge_base_url": os.environ.get("KB_URL", "http://localhost:8000/api"),
            "knowledge_graph_url": os.environ.get("KG_URL", "http://localhost:8000/api"),
            "api_key": os.environ.get("RAG_KB_API_KEY", ""),
            "timeout": 5
        }
    },
    "embeddings": {
        "model": EMBEDDING_MODEL,
        "dimension": VECTOR_DIMENSION
    },
    "knowledge_base": {
        "index_path": VECTOR_DB_PATH,
        "document_store": VECTOR_DB_TYPE
    },
    "knowledge_graph": {
        "graph_store": "neo4j",
        "uri": os.environ.get("NEO4J_URI", "bolt://neo4j:7687"),
        "user": os.environ.get("NEO4J_USER", "neo4j"),
        "password": os.environ.get("NEO4J_PASSWORD", "password")
    }
}

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径，如果为None则使用默认配置
        
    Returns:
        配置字典
    """
    config = DEFAULT_CONFIG.copy()
    
    # 如果提供了配置文件路径，尝试加载它
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                yaml_config = yaml.safe_load(f)
                if yaml_config:
                    # 递归更新配置
                    deep_update(config, yaml_config)
                    logger.info(f"从 {config_path} 加载配置成功")
        except Exception as e:
            logger.error(f"从 {config_path} 加载配置失败: {str(e)}")
    else:
        logger.info("使用默认配置")
    
    # 从环境变量加载敏感配置
    load_sensitive_config_from_env(config)
    
    return config

def load_sensitive_config_from_env(config: Dict[str, Any]) -> None:
    """
    从环境变量加载敏感配置
    
    Args:
        config: 配置字典，将被就地修改
    """
    # Web搜索API密钥
    if os.environ.get("RAG_BRAVE_API_KEY"):
        config["web_search"]["api_keys"]["brave"] = os.environ["RAG_BRAVE_API_KEY"]
    
    if os.environ.get("RAG_GOOGLE_API_KEY"):
        config["web_search"]["api_keys"]["google"] = os.environ["RAG_GOOGLE_API_KEY"]
    
    # 知识库API密钥
    if os.environ.get("RAG_KB_API_KEY"):
        config["web_search"]["knowledge"]["api_key"] = os.environ["RAG_KB_API_KEY"]
    
    # Neo4j凭据
    if os.environ.get("NEO4J_URI"):
        config["knowledge_graph"]["uri"] = os.environ["NEO4J_URI"]
    
    if os.environ.get("NEO4J_USER"):
        config["knowledge_graph"]["user"] = os.environ["NEO4J_USER"]
        
    if os.environ.get("NEO4J_PASSWORD"):
        config["knowledge_graph"]["password"] = os.environ["NEO4J_PASSWORD"]

def deep_update(d: Dict[str, Any], u: Dict[str, Any]) -> Dict[str, Any]:
    """
    递归更新嵌套字典
    
    Args:
        d: 要更新的目标字典
        u: 源字典，其值将覆盖目标字典中的对应值
        
    Returns:
        更新后的字典
    """
    for k, v in u.items():
        if isinstance(v, dict) and k in d and isinstance(d[k], dict):
            deep_update(d[k], v)
        else:
            d[k] = v
    return d

def get_web_search_config() -> Dict[str, Any]:
    """
    获取Web搜索模块的配置
    
    Returns:
        Web搜索配置字典
    """
    config = load_config()
    return config.get("web_search", {}) 