"""
settings - 索克生活项目模块
"""

                    import json
    import json
from loguru import logger
from pathlib import Path
from pydantic import BaseSettings, Field, validator
from pydantic.env_settings import SettingsSourceCallable
from typing import Dict, Any, Optional, List, Union
import os
import yaml

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RAG服务配置管理
支持多环境配置、动态配置更新和配置验证
"""



class DatabaseConfig(BaseSettings):
    """数据库配置"""
    
    # 向量数据库配置
    vector_db_host: str = Field("localhost", description="向量数据库主机")
    vector_db_port: int = Field(19530, description="向量数据库端口")
    vector_db_user: str = Field("", description="向量数据库用户名")
    vector_db_password: str = Field("", description="向量数据库密码")
    vector_db_database: str = Field("rag_service", description="向量数据库名称")
    
    # Redis配置
    redis_host: str = Field("localhost", description="Redis主机")
    redis_port: int = Field(6379, description="Redis端口")
    redis_password: str = Field("", description="Redis密码")
    redis_db: int = Field(0, description="Redis数据库编号")
    redis_max_connections: int = Field(20, description="Redis最大连接数")
    
    # Neo4j配置（知识图谱）
    neo4j_uri: str = Field("bolt://localhost:7687", description="Neo4j连接URI")
    neo4j_user: str = Field("neo4j", description="Neo4j用户名")
    neo4j_password: str = Field("password", description="Neo4j密码")
    neo4j_database: str = Field("neo4j", description="Neo4j数据库名称")


class ModelConfig(BaseSettings):
    """模型配置"""
    
    # 嵌入模型配置
    embedding_model_name: str = Field("text-embedding-ada-002", description="嵌入模型名称")
    embedding_model_provider: str = Field("openai", description="嵌入模型提供商")
    embedding_dimension: int = Field(1536, description="嵌入向量维度")
    embedding_batch_size: int = Field(100, description="嵌入批处理大小")
    
    # 生成模型配置
    generation_model_name: str = Field("gpt-3.5-turbo", description="生成模型名称")
    generation_model_provider: str = Field("openai", description="生成模型提供商")
    generation_max_tokens: int = Field(2048, description="生成最大token数")
    generation_temperature: float = Field(0.7, description="生成温度")
    generation_top_p: float = Field(0.9, description="生成top_p参数")
    
    # 模型API配置
    openai_api_key: str = Field("", description="OpenAI API密钥")
    openai_api_base: str = Field("https://api.openai.com/v1", description="OpenAI API基础URL")
    openai_organization: str = Field("", description="OpenAI组织ID")
    
    # 本地模型配置
    local_model_path: str = Field("./models", description="本地模型路径")
    use_local_models: bool = Field(False, description="是否使用本地模型")
    
    @validator('embedding_dimension')
    def validate_embedding_dimension(cls, v):
        if v <= 0:
            raise ValueError('嵌入维度必须大于0')
        return v
    
    @validator('generation_temperature')
    def validate_temperature(cls, v):
        if not 0 <= v <= 2:
            raise ValueError('温度参数必须在0-2之间')
        return v


class ServiceConfig(BaseSettings):
    """服务配置"""
    
    # 基础服务配置
    service_name: str = Field("rag-service", description="服务名称")
    service_version: str = Field("1.2.0", description="服务版本")
    environment: str = Field("development", description="运行环境")
    debug: bool = Field(False, description="调试模式")
    
    # HTTP服务配置
    http_host: str = Field("0.0.0.0", description="HTTP服务主机")
    http_port: int = Field(8000, description="HTTP服务端口")
    http_workers: int = Field(1, description="HTTP工作进程数")
    
    # gRPC服务配置
    grpc_host: str = Field("0.0.0.0", description="gRPC服务主机")
    grpc_port: int = Field(9000, description="gRPC服务端口")
    grpc_max_workers: int = Field(10, description="gRPC最大工作线程数")
    
    # 安全配置
    api_key_header: str = Field("X-API-Key", description="API密钥头部名称")
    jwt_secret_key: str = Field("", description="JWT密钥")
    jwt_algorithm: str = Field("HS256", description="JWT算法")
    jwt_expire_minutes: int = Field(30, description="JWT过期时间（分钟）")
    
    # CORS配置
    cors_origins: List[str] = Field(["*"], description="CORS允许的源")
    cors_methods: List[str] = Field(["*"], description="CORS允许的方法")
    cors_headers: List[str] = Field(["*"], description="CORS允许的头部")


class RetrievalConfig(BaseSettings):
    """检索配置"""
    
    # 检索参数
    default_top_k: int = Field(5, description="默认检索数量")
    max_top_k: int = Field(50, description="最大检索数量")
    similarity_threshold: float = Field(0.7, description="相似度阈值")
    
    # 混合检索配置
    enable_hybrid_search: bool = Field(True, description="启用混合检索")
    vector_weight: float = Field(0.7, description="向量检索权重")
    keyword_weight: float = Field(0.3, description="关键词检索权重")
    
    # 重排序配置
    enable_reranking: bool = Field(True, description="启用重排序")
    rerank_model_name: str = Field("cross-encoder/ms-marco-MiniLM-L-6-v2", description="重排序模型")
    rerank_top_k: int = Field(10, description="重排序候选数量")
    
    # 知识图谱增强
    enable_kg_enhancement: bool = Field(True, description="启用知识图谱增强")
    kg_expansion_depth: int = Field(2, description="知识图谱扩展深度")
    kg_max_entities: int = Field(20, description="知识图谱最大实体数")
    
    @validator('similarity_threshold')
    def validate_similarity_threshold(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('相似度阈值必须在0-1之间')
        return v


class GenerationConfig(BaseSettings):
    """生成配置"""
    
    # 生成参数
    max_context_length: int = Field(4000, description="最大上下文长度")
    max_response_length: int = Field(1000, description="最大响应长度")
    context_window_overlap: int = Field(200, description="上下文窗口重叠")
    
    # 提示词配置
    system_prompt_template: str = Field(
        "你是一个专业的中医健康助手，基于提供的医学知识回答用户问题。",
        description="系统提示词模板"
    )
    user_prompt_template: str = Field(
        "基于以下医学知识：\n{context}\n\n请回答用户问题：{query}",
        description="用户提示词模板"
    )
    
    # 生成策略
    enable_streaming: bool = Field(True, description="启用流式生成")
    enable_citation: bool = Field(True, description="启用引用")
    citation_format: str = Field("markdown", description="引用格式")
    
    # 内容过滤
    enable_content_filter: bool = Field(True, description="启用内容过滤")
    filter_sensitive_content: bool = Field(True, description="过滤敏感内容")
    filter_medical_advice: bool = Field(True, description="过滤医疗建议")


class CacheConfig(BaseSettings):
    """缓存配置"""
    
    # 缓存策略
    enable_cache: bool = Field(True, description="启用缓存")
    cache_backend: str = Field("redis", description="缓存后端")
    default_ttl: int = Field(3600, description="默认TTL（秒）")
    
    # 缓存层级
    enable_memory_cache: bool = Field(True, description="启用内存缓存")
    memory_cache_size: int = Field(1000, description="内存缓存大小")
    memory_cache_ttl: int = Field(300, description="内存缓存TTL（秒）")
    
    # 缓存键配置
    cache_key_prefix: str = Field("rag:", description="缓存键前缀")
    cache_key_separator: str = Field(":", description="缓存键分隔符")
    
    # 缓存预热
    enable_cache_warmup: bool = Field(False, description="启用缓存预热")
    warmup_queries: List[str] = Field([], description="预热查询列表")


class MonitoringConfig(BaseSettings):
    """监控配置"""
    
    # 日志配置
    log_level: str = Field("INFO", description="日志级别")
    log_format: str = Field("json", description="日志格式")
    log_file: str = Field("", description="日志文件路径")
    log_rotation: str = Field("1 day", description="日志轮转")
    log_retention: str = Field("30 days", description="日志保留时间")
    
    # 指标配置
    enable_metrics: bool = Field(True, description="启用指标收集")
    metrics_port: int = Field(8001, description="指标端口")
    metrics_path: str = Field("/metrics", description="指标路径")
    
    # 追踪配置
    enable_tracing: bool = Field(True, description="启用分布式追踪")
    tracing_endpoint: str = Field("", description="追踪端点")
    tracing_service_name: str = Field("rag-service", description="追踪服务名称")
    
    # 健康检查配置
    health_check_interval: int = Field(30, description="健康检查间隔（秒）")
    health_check_timeout: int = Field(5, description="健康检查超时（秒）")


class PerformanceConfig(BaseSettings):
    """性能配置"""
    
    # 并发配置
    max_concurrent_requests: int = Field(100, description="最大并发请求数")
    request_timeout: int = Field(30, description="请求超时时间（秒）")
    batch_processing_size: int = Field(10, description="批处理大小")
    
    # 资源限制
    max_memory_usage: str = Field("2GB", description="最大内存使用")
    max_cpu_usage: float = Field(0.8, description="最大CPU使用率")
    
    # 优化配置
    enable_async_processing: bool = Field(True, description="启用异步处理")
    enable_connection_pooling: bool = Field(True, description="启用连接池")
    connection_pool_size: int = Field(20, description="连接池大小")


class Settings(BaseSettings):
    """主配置类"""
    
    # 子配置
    database: DatabaseConfig = DatabaseConfig()
    model: ModelConfig = ModelConfig()
    service: ServiceConfig = ServiceConfig()
    retrieval: RetrievalConfig = RetrievalConfig()
    generation: GenerationConfig = GenerationConfig()
    cache: CacheConfig = CacheConfig()
    monitoring: MonitoringConfig = MonitoringConfig()
    performance: PerformanceConfig = PerformanceConfig()
    
    # 配置文件路径
    config_file: Optional[str] = Field(None, description="配置文件路径")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 如果指定了配置文件，加载配置文件
        if self.config_file and Path(self.config_file).exists():
            self.load_from_file(self.config_file)
    
    def load_from_file(self, config_file: str):
        """从文件加载配置"""
        try:
            config_path = Path(config_file)
            if not config_path.exists():
                logger.warning(f"配置文件不存在: {config_file}")
                return
            
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yml', '.yaml']:
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
            
            # 更新配置
            self._update_from_dict(config_data)
            logger.info(f"已加载配置文件: {config_file}")
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
    
    def _update_from_dict(self, config_data: Dict[str, Any]):
        """从字典更新配置"""
        for section_name, section_data in config_data.items():
            if hasattr(self, section_name) and isinstance(section_data, dict):
                section = getattr(self, section_name)
                for key, value in section_data.items():
                    if hasattr(section, key):
                        setattr(section, key, value)
    
    def save_to_file(self, config_file: str):
        """保存配置到文件"""
        try:
            config_data = self.dict()
            config_path = Path(config_file)
            
            # 确保目录存在
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yml', '.yaml']:
                    yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
                else:
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"配置已保存到: {config_file}")
            
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
    
    def validate_config(self) -> List[str]:
        """验证配置"""
        errors = []
        
        # 验证必需的配置
        if not self.model.openai_api_key and self.model.generation_model_provider == "openai":
            errors.append("OpenAI API密钥未配置")
        
        if self.retrieval.vector_weight + self.retrieval.keyword_weight != 1.0:
            errors.append("向量检索权重和关键词检索权重之和必须为1.0")
        
        if self.service.http_port == self.service.grpc_port:
            errors.append("HTTP端口和gRPC端口不能相同")
        
        # 验证路径存在性
        if self.model.use_local_models:
            model_path = Path(self.model.local_model_path)
            if not model_path.exists():
                errors.append(f"本地模型路径不存在: {self.model.local_model_path}")
        
        return errors
    
    def get_environment_config(self) -> Dict[str, Any]:
        """获取环境特定配置"""
        env_configs = {
            "development": {
                "service.debug": True,
                "monitoring.log_level": "DEBUG",
                "cache.enable_cache": False,
                "performance.max_concurrent_requests": 10
            },
            "testing": {
                "service.debug": True,
                "monitoring.log_level": "DEBUG",
                "cache.enable_cache": False,
                "database.vector_db_database": "rag_service_test"
            },
            "production": {
                "service.debug": False,
                "monitoring.log_level": "INFO",
                "cache.enable_cache": True,
                "performance.max_concurrent_requests": 100
            }
        }
        
        return env_configs.get(self.service.environment, {})
    
    def apply_environment_config(self):
        """应用环境特定配置"""
        env_config = self.get_environment_config()
        
        for key, value in env_config.items():
            section_name, field_name = key.split('.', 1)
            if hasattr(self, section_name):
                section = getattr(self, section_name)
                if hasattr(section, field_name):
                    setattr(section, field_name, value)
    
    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要"""
        return {
            "service": {
                "name": self.service.service_name,
                "version": self.service.service_version,
                "environment": self.service.environment,
                "debug": self.service.debug
            },
            "endpoints": {
                "http": f"http://{self.service.http_host}:{self.service.http_port}",
                "grpc": f"{self.service.grpc_host}:{self.service.grpc_port}",
                "metrics": f"http://{self.service.http_host}:{self.monitoring.metrics_port}{self.monitoring.metrics_path}"
            },
            "features": {
                "hybrid_search": self.retrieval.enable_hybrid_search,
                "kg_enhancement": self.retrieval.enable_kg_enhancement,
                "reranking": self.retrieval.enable_reranking,
                "streaming": self.generation.enable_streaming,
                "caching": self.cache.enable_cache,
                "metrics": self.monitoring.enable_metrics,
                "tracing": self.monitoring.enable_tracing
            }
        }


# 全局配置实例
_settings: Optional[Settings] = None


def get_settings(config_file: Optional[str] = None) -> Settings:
    """获取配置实例"""
    global _settings
    
    if _settings is None:
        _settings = Settings(config_file=config_file)
        _settings.apply_environment_config()
        
        # 验证配置
        errors = _settings.validate_config()
        if errors:
            logger.warning(f"配置验证发现问题: {errors}")
    
    return _settings


def reload_settings(config_file: Optional[str] = None) -> Settings:
    """重新加载配置"""
    global _settings
    _settings = None
    return get_settings(config_file)


def create_default_config_file(config_file: str):
    """创建默认配置文件"""
    settings = Settings()
    settings.save_to_file(config_file)
    logger.info(f"已创建默认配置文件: {config_file}")


if __name__ == "__main__":
    # 测试配置
    settings = get_settings()
    print("配置摘要:")
    print(json.dumps(settings.get_config_summary(), indent=2, ensure_ascii=False)) 