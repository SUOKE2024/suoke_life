/// RAG检索类型枚举
enum RAGRetrievalType {
  /// 稠密向量检索
  dense,
  
  /// 稀疏向量检索
  sparse,
  
  /// 混合检索
  hybrid,
  
  /// 多跳检索
  multiHop,
} 