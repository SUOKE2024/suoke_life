import 'dart:convert';
import 'dart:math';
import 'dart:typed_data';

/// 文本嵌入模型
class Embedding {
  /// 嵌入向量
  final List<double> vector;
  
  /// 文档ID（如果适用）
  final String? documentId;
  
  /// 嵌入对应的原始文本
  final String? text;
  
  /// 嵌入的维度
  int get dimension => vector.length;
  
  Embedding({
    required this.vector,
    this.documentId,
    this.text,
  });
  
  /// 计算与另一个嵌入的余弦相似度
  double cosineSimilarity(Embedding other) {
    if (dimension != other.dimension) {
      throw ArgumentError('维度不匹配：$dimension 与 ${other.dimension}');
    }
    
    double dotProduct = 0.0;
    double normA = 0.0;
    double normB = 0.0;
    
    for (int i = 0; i < dimension; i++) {
      dotProduct += vector[i] * other.vector[i];
      normA += vector[i] * vector[i];
      normB += other.vector[i] * other.vector[i];
    }
    
    normA = sqrt(normA);
    normB = sqrt(normB);
    
    if (normA == 0 || normB == 0) {
      return 0;
    }
    
    return dotProduct / (normA * normB);
  }
  
  /// 计算与另一个嵌入的欧几里得距离
  double euclideanDistance(Embedding other) {
    if (dimension != other.dimension) {
      throw ArgumentError('维度不匹配：$dimension 与 ${other.dimension}');
    }
    
    double sumSquaredDiff = 0.0;
    
    for (int i = 0; i < dimension; i++) {
      final diff = vector[i] - other.vector[i];
      sumSquaredDiff += diff * diff;
    }
    
    return sqrt(sumSquaredDiff);
  }
  
  /// 计算与另一个嵌入的点积
  double dotProduct(Embedding other) {
    if (dimension != other.dimension) {
      throw ArgumentError('维度不匹配：$dimension 与 ${other.dimension}');
    }
    
    double result = 0.0;
    
    for (int i = 0; i < dimension; i++) {
      result += vector[i] * other.vector[i];
    }
    
    return result;
  }
  
  /// 缩放向量（每个元素乘以标量）
  Embedding scale(double scalar) {
    return Embedding(
      vector: vector.map((v) => v * scalar).toList(),
      documentId: documentId,
      text: text,
    );
  }
  
  /// 将嵌入向量序列化为Base64字符串
  String toBase64() {
    final bytes = Float64List.fromList(vector).buffer.asUint8List();
    return base64Encode(bytes);
  }
  
  /// 从Base64字符串创建嵌入向量
  factory Embedding.fromBase64(String base64String, {String? documentId, String? text}) {
    final bytes = base64Decode(base64String);
    
    final byteData = ByteData.sublistView(Uint8List.fromList(bytes));
    final vector = <double>[];
    
    for (int i = 0; i < bytes.length; i += 8) {
      if (i + 8 <= bytes.length) {
        final value = byteData.getFloat64(i, Endian.little);
        vector.add(value);
      }
    }
    
    return Embedding(
      vector: vector,
      documentId: documentId,
      text: text,
    );
  }
  
  /// 转换为Map
  Map<String, dynamic> toMap() {
    return {
      'vector': vector,
      'documentId': documentId,
      'text': text,
    };
  }
  
  /// 从Map创建
  factory Embedding.fromMap(Map<String, dynamic> map) {
    return Embedding(
      vector: List<double>.from(map['vector']),
      documentId: map['documentId'],
      text: map['text'],
    );
  }
  
  /// 转换为JSON
  String toJson() {
    return jsonEncode(toMap());
  }
  
  /// 从JSON创建
  factory Embedding.fromJson(String json) {
    return Embedding.fromMap(jsonDecode(json));
  }
}

/// 检索结果类
class SearchResult {
  /// 检索到的文档内容
  final String content;
  
  /// 文档ID
  final String documentId;
  
  /// 文档元数据
  final Map<String, dynamic>? metadata;
  
  /// 相似度分数（0-1之间）
  final double score;
  
  SearchResult({
    required this.content,
    required this.documentId,
    this.metadata,
    required this.score,
  });
}

/// 向量索引存储接口
abstract class VectorStore {
  /// 添加文档并创建嵌入索引
  Future<String> addDocument({
    required String content,
    required Embedding embedding,
    required String collection,
    Map<String, dynamic>? metadata,
  });
  
  /// 相似度搜索
  Future<List<SearchResult>> similaritySearch({
    required Embedding embedding,
    required String collection,
    int limit = 5,
    double minScore = 0.0,
    Map<String, dynamic>? filter,
  });
  
  /// 删除文档
  Future<void> deleteDocument({
    required String documentId,
    required String collection,
  });
  
  /// 创建集合
  Future<void> createCollection(String collection);
  
  /// 删除集合
  Future<void> deleteCollection(String collection);
  
  /// 列出所有集合
  Future<List<String>> listCollections();
} 