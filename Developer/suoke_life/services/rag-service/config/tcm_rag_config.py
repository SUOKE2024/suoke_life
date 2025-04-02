from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

class TCMDocumentType(Enum):
    """中医文档类型"""
    CLASSIC_LITERATURE = "经典文献"      # 经典医著
    CLINICAL_CASES = "临床案例"          # 临床案例
    PRESCRIPTION = "方剂"               # 方剂
    HERB = "中药"                      # 中药
    ACUPUNCTURE = "针灸"               # 针灸
    MASSAGE = "推拿"                   # 推拿
    HEALTH_CULTIVATION = "养生"         # 养生
    CONSTITUTION = "体质"              # 体质
    SYNDROME = "证候"                  # 证候
    DISEASE = "疾病"                   # 疾病

class RetrievalStrategy(Enum):
    """检索策略"""
    HYBRID = "hybrid"                 # 混合检索
    SEMANTIC = "semantic"             # 语义检索
    KEYWORD = "keyword"               # 关键词检索
    KNOWLEDGE_GRAPH = "kg"            # 知识图谱检索

@dataclass
class EmbeddingConfig:
    """向量嵌入配置"""
    model_name: str = "BAAI/bge-large-zh-v1.5"
    max_length: int = 512
    batch_size: int = 32
    device: str = "cuda"
    normalize_embeddings: bool = True

@dataclass
class VectorStoreConfig:
    """向量存储配置"""
    engine: str = "milvus"           # milvus, chromadb, qdrant
    collection_name: str = "tcm_vectors"
    dimension: int = 1024
    metric_type: str = "COSINE"      # COSINE, IP, L2
    index_type: str = "IVF_FLAT"     # IVF_FLAT, IVF_SQ8, IVF_PQ
    index_params: Dict = None
    search_params: Dict = None
    
    def __post_init__(self):
        if self.index_params is None:
            self.index_params = {
                "nlist": 1024,        # 聚类单元数
                "nprobe": 16          # 搜索聚类单元数
            }
        if self.search_params is None:
            self.search_params = {
                "metric_type": self.metric_type,
                "params": {"nprobe": 16}
            }

@dataclass
class DocumentProcessConfig:
    """文档处理配置"""
    chunk_size: int = 500            # 文档分块大小
    chunk_overlap: int = 50          # 分块重叠大小
    min_chunk_size: int = 100        # 最小分块大小
    max_chunk_size: int = 1000       # 最大分块大小
    
    # 文档类型权重
    type_weights: Dict[TCMDocumentType, float] = None
    
    def __post_init__(self):
        if self.type_weights is None:
            self.type_weights = {
                TCMDocumentType.CLASSIC_LITERATURE: 1.0,
                TCMDocumentType.CLINICAL_CASES: 1.2,
                TCMDocumentType.PRESCRIPTION: 1.1,
                TCMDocumentType.HERB: 1.0,
                TCMDocumentType.ACUPUNCTURE: 1.0,
                TCMDocumentType.MASSAGE: 1.0,
                TCMDocumentType.HEALTH_CULTIVATION: 0.9,
                TCMDocumentType.CONSTITUTION: 1.1,
                TCMDocumentType.SYNDROME: 1.2,
                TCMDocumentType.DISEASE: 1.1
            }

@dataclass
class RerankerConfig:
    """重排序配置"""
    model_name: str = "BAAI/bge-reranker-large"
    max_length: int = 512
    batch_size: int = 16
    device: str = "cuda"
    top_k: int = 50                  # 重排序候选数量
    score_threshold: float = 0.6     # 相关性分数阈值

@dataclass
class TCMPromptConfig:
    """中医提示词配置"""
    system_prompt: str = """你是一位经验丰富的中医专家，精通中医理论与实践。
在回答问题时，请遵循以下原则：
1. 基于检索到的中医文献和临床案例进行分析
2. 运用中医理论，说明诊断和推理过程
3. 使用专业而易懂的语言
4. 必要时提供养生保健建议
5. 明确指出需要就医的情况
6. 避免做出确诊或处方建议"""

    query_prefix: str = """请基于中医理论，分析以下问题：
"""

    query_suffix: str = """
请结合检索到的相关文献和案例进行分析。如果信息不足，请说明需要了解的其他情况。
"""

@dataclass
class TCMRAGConfig:
    """中医 RAG 总配置"""
    embedding: EmbeddingConfig = EmbeddingConfig()
    vector_store: VectorStoreConfig = VectorStoreConfig()
    document_process: DocumentProcessConfig = DocumentProcessConfig()
    reranker: RerankerConfig = RerankerConfig()
    prompt: TCMPromptConfig = TCMPromptConfig()
    
    # 默认检索策略
    default_strategy: RetrievalStrategy = RetrievalStrategy.HYBRID
    
    # 混合检索权重
    hybrid_weights: Dict[RetrievalStrategy, float] = None
    
    # 上下文窗口大小
    context_window: int = 4096
    
    # 知识图谱配置
    use_knowledge_graph: bool = True
    kg_weight: float = 0.3
    
    def __post_init__(self):
        if self.hybrid_weights is None:
            self.hybrid_weights = {
                RetrievalStrategy.SEMANTIC: 0.6,
                RetrievalStrategy.KEYWORD: 0.2,
                RetrievalStrategy.KNOWLEDGE_GRAPH: 0.2
            }

# 默认配置实例
default_config = TCMRAGConfig() 