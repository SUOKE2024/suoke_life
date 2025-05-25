#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
统一配置管理系统
支持多环境配置、验证和动态加载
"""

import os
from typing import Dict, Any, Optional, List
from pathlib import Path
from pydantic import BaseSettings, Field, validator
from dynaconf import Dynaconf
from enum import Enum


class Environment(str, Enum):
    """环境枚举"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class DatabaseConfig(BaseSettings):
    """数据库配置"""
    host: str = Field(default="localhost", description="数据库主机")
    port: int = Field(default=5432, description="数据库端口")
    username: str = Field(default="postgres", description="数据库用户名")
    password: str = Field(default="", description="数据库密码")
    database: str = Field(default="rag_service", description="数据库名称")
    pool_size: int = Field(default=10, description="连接池大小")
    max_overflow: int = Field(default=20, description="最大溢出连接数")
    
    @property
    def url(self) -> str:
        """获取数据库连接URL"""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


class VectorDatabaseConfig(BaseSettings):
    """向量数据库配置"""
    type: str = Field(default="milvus", description="向量数据库类型")
    host: str = Field(default="localhost", description="向量数据库主机")
    port: int = Field(default=19530, description="向量数据库端口")
    collection_name: str = Field(default="rag_vectors", description="集合名称")
    dimension: int = Field(default=768, description="向量维度")
    index_type: str = Field(default="IVF_FLAT", description="索引类型")
    metric_type: str = Field(default="L2", description="距离度量类型")
    nlist: int = Field(default=1024, description="聚类中心数量")
    
    # Qdrant特定配置
    qdrant_url: Optional[str] = Field(default=None, description="Qdrant连接URL")
    qdrant_api_key: Optional[str] = Field(default=None, description="Qdrant API密钥")
    
    @validator('type')
    def validate_type(cls, v):
        allowed_types = ['milvus', 'qdrant', 'weaviate']
        if v not in allowed_types:
            raise ValueError(f"向量数据库类型必须是 {allowed_types} 之一")
        return v


class CacheConfig(BaseSettings):
    """缓存配置"""
    type: str = Field(default="redis", description="缓存类型")
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis连接URL")
    ttl: int = Field(default=3600, description="默认TTL（秒）")
    max_connections: int = Field(default=100, description="最大连接数")
    
    # 内存缓存配置
    memory_cache_size: int = Field(default=1000, description="内存缓存大小")
    
    # 磁盘缓存配置
    disk_cache_dir: str = Field(default="/tmp/rag_cache", description="磁盘缓存目录")
    disk_cache_size: int = Field(default=1024*1024*1024, description="磁盘缓存大小（字节）")


class EmbeddingConfig(BaseSettings):
    """嵌入模型配置"""
    model_name: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", description="模型名称")
    model_path: Optional[str] = Field(default=None, description="本地模型路径")
    device: str = Field(default="cpu", description="计算设备")
    batch_size: int = Field(default=32, description="批处理大小")
    max_length: int = Field(default=512, description="最大序列长度")
    normalize_embeddings: bool = Field(default=True, description="是否标准化嵌入")
    
    # 中医特色嵌入配置
    tcm_model_name: Optional[str] = Field(default=None, description="中医专用嵌入模型")
    use_tcm_enhancement: bool = Field(default=True, description="是否使用中医增强")


class GeneratorConfig(BaseSettings):
    """生成器配置"""
    model_type: str = Field(default="openai", description="生成器类型")
    
    # OpenAI配置
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API密钥")
    openai_model: str = Field(default="gpt-3.5-turbo", description="OpenAI模型名称")
    openai_temperature: float = Field(default=0.7, description="生成温度")
    openai_max_tokens: int = Field(default=1000, description="最大生成token数")
    
    # 本地模型配置
    local_model_path: Optional[str] = Field(default=None, description="本地模型路径")
    local_model_name: str = Field(default="chatglm2-6b", description="本地模型名称")
    
    # 生成参数
    max_new_tokens: int = Field(default=512, description="最大新生成token数")
    do_sample: bool = Field(default=True, description="是否采样")
    top_k: int = Field(default=50, description="Top-K采样")
    top_p: float = Field(default=0.95, description="Top-P采样")
    repetition_penalty: float = Field(default=1.1, description="重复惩罚")


class RetrieverConfig(BaseSettings):
    """检索器配置"""
    type: str = Field(default="hybrid", description="检索器类型")
    top_k: int = Field(default=10, description="检索Top-K")
    similarity_threshold: float = Field(default=0.7, description="相似度阈值")
    
    # 混合检索配置
    vector_weight: float = Field(default=0.7, description="向量检索权重")
    keyword_weight: float = Field(default=0.3, description="关键词检索权重")
    
    # 重排序配置
    enable_reranking: bool = Field(default=True, description="是否启用重排序")
    rerank_model: str = Field(default="cross-encoder/ms-marco-MiniLM-L-6-v2", description="重排序模型")
    
    # 查询扩展配置
    enable_query_expansion: bool = Field(default=True, description="是否启用查询扩展")
    expansion_terms: int = Field(default=3, description="扩展词数量")


class TCMConfig(BaseSettings):
    """中医特色配置"""
    # 辨证分析配置
    syndrome_analysis: Dict[str, Any] = Field(default_factory=lambda: {
        "confidence_threshold": 0.6,
        "max_syndromes": 3,
        "enable_reasoning_chain": True
    })
    
    # 方剂推荐配置
    herb_recommendation: Dict[str, Any] = Field(default_factory=lambda: {
        "max_formulas": 5,
        "safety_check": True,
        "personalization": True
    })
    
    # 脉象分析配置
    pulse_analysis: Dict[str, Any] = Field(default_factory=lambda: {
        "enable_ai_analysis": True,
        "confidence_threshold": 0.7
    })
    
    # 中医知识库配置
    knowledge_base: Dict[str, Any] = Field(default_factory=lambda: {
        "herbs_db_path": "data/tcm/herbs.json",
        "formulas_db_path": "data/tcm/formulas.json",
        "syndromes_db_path": "data/tcm/syndromes.json"
    })


class KnowledgeGraphConfig(BaseSettings):
    """知识图谱配置"""
    enabled: bool = Field(default=True, description="是否启用知识图谱")
    neo4j_url: str = Field(default="bolt://localhost:7687", description="Neo4j连接URL")
    neo4j_username: str = Field(default="neo4j", description="Neo4j用户名")
    neo4j_password: str = Field(default="password", description="Neo4j密码")
    
    # 图谱查询配置
    max_depth: int = Field(default=3, description="最大查询深度")
    max_nodes: int = Field(default=100, description="最大节点数")
    
    # 中医知识图谱配置
    tcm_graph_enabled: bool = Field(default=True, description="是否启用中医知识图谱")


class ObservabilityConfig(BaseSettings):
    """可观测性配置"""
    # 指标配置
    metrics: Dict[str, Any] = Field(default_factory=lambda: {
        "enabled": True,
        "port": 8080,
        "path": "/metrics"
    })
    
    # 追踪配置
    tracing: Dict[str, Any] = Field(default_factory=lambda: {
        "enabled": True,
        "jaeger_endpoint": "http://localhost:14268/api/traces",
        "service_name": "rag-service"
    })
    
    # 日志配置
    logging: Dict[str, Any] = Field(default_factory=lambda: {
        "level": "INFO",
        "format": "json",
        "file_path": "logs/rag-service.log"
    })


class ResilienceConfig(BaseSettings):
    """弹性配置"""
    # 断路器配置
    circuit_breaker: Dict[str, Any] = Field(default_factory=lambda: {
        "failure_threshold": 5,
        "recovery_timeout": 60,
        "expected_exception": "Exception"
    })
    
    # 重试配置
    retry: Dict[str, Any] = Field(default_factory=lambda: {
        "max_attempts": 3,
        "backoff_factor": 2,
        "max_delay": 60
    })
    
    # 超时配置
    timeout: Dict[str, Any] = Field(default_factory=lambda: {
        "request_timeout": 30,
        "embedding_timeout": 10,
        "generation_timeout": 60
    })


class SecurityConfig(BaseSettings):
    """安全配置"""
    # JWT配置
    jwt_secret_key: str = Field(default="your-secret-key", description="JWT密钥")
    jwt_algorithm: str = Field(default="HS256", description="JWT算法")
    jwt_expiration: int = Field(default=3600, description="JWT过期时间（秒）")
    
    # API密钥配置
    api_keys: List[str] = Field(default_factory=list, description="API密钥列表")
    
    # 速率限制配置
    rate_limit: Dict[str, Any] = Field(default_factory=lambda: {
        "requests_per_minute": 100,
        "burst_size": 10
    })


class Settings(BaseSettings):
    """主配置类"""
    # 基础配置
    environment: Environment = Field(default=Environment.DEVELOPMENT, description="运行环境")
    debug: bool = Field(default=False, description="调试模式")
    host: str = Field(default="0.0.0.0", description="服务主机")
    port: int = Field(default=8000, description="服务端口")
    workers: int = Field(default=1, description="工作进程数")
    
    # 组件配置
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    vector_database: VectorDatabaseConfig = Field(default_factory=VectorDatabaseConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    generator: GeneratorConfig = Field(default_factory=GeneratorConfig)
    retriever: RetrieverConfig = Field(default_factory=RetrieverConfig)
    tcm: TCMConfig = Field(default_factory=TCMConfig)
    knowledge_graph: KnowledgeGraphConfig = Field(default_factory=KnowledgeGraphConfig)
    observability: ObservabilityConfig = Field(default_factory=ObservabilityConfig)
    resilience: ResilienceConfig = Field(default_factory=ResilienceConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    @validator('environment', pre=True)
    def validate_environment(cls, v):
        if isinstance(v, str):
            return Environment(v.lower())
        return v
    
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.environment == Environment.PRODUCTION
    
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.environment == Environment.DEVELOPMENT


def load_settings() -> Settings:
    """
    加载配置
    支持从环境变量、配置文件等多种方式加载
    """
    # 获取当前环境
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    # 使用Dynaconf加载配置
    config_dir = Path(__file__).parent
    dynaconf_settings = Dynaconf(
        envvar_prefix="RAG",
        settings_files=[
            config_dir / "settings.yaml",
            config_dir / f"settings.{env}.yaml",
        ],
        environments=True,
        load_dotenv=True,
        env_switcher="ENVIRONMENT",
    )
    
    # 转换为Pydantic设置
    settings_dict = dynaconf_settings.as_dict()
    return Settings(**settings_dict)


def get_config_dict(settings: Settings) -> Dict[str, Any]:
    """将设置转换为字典格式"""
    return {
        "environment": settings.environment.value,
        "debug": settings.debug,
        "host": settings.host,
        "port": settings.port,
        "workers": settings.workers,
        "database": settings.database.dict(),
        "vector_database": settings.vector_database.dict(),
        "cache": settings.cache.dict(),
        "embedding": settings.embedding.dict(),
        "generator": settings.generator.dict(),
        "retriever": settings.retriever.dict(),
        "tcm": settings.tcm.dict(),
        "knowledge_graph": settings.knowledge_graph.dict(),
        "observability": settings.observability.dict(),
        "resilience": settings.resilience.dict(),
        "security": settings.security.dict(),
    }


# 全局设置实例
settings = load_settings() 