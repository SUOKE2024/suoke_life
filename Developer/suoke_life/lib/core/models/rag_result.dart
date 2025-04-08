/// RAG检索结果模型
///
/// 封装从知识库检索得到的结果，包括内容、评分和元数据
class RagResult {
  /// 唯一标识符
  final String id;

  /// 检索到的文本内容
  final String content;

  /// 相似度评分（0-1之间，越高越相关）
  final double score;

  /// 元数据信息，包含来源、类型等信息
  final Map<String, dynamic> metadata;

  const RagResult({
    required this.id,
    required this.content,
    required this.score,
    this.metadata = const {},
  });

  /// 创建一个带有更新属性的副本
  RagResult copyWith({
    String? id,
    String? content,
    double? score,
    Map<String, dynamic>? metadata,
  }) {
    return RagResult(
      id: id ?? this.id,
      content: content ?? this.content,
      score: score ?? this.score,
      metadata: metadata ?? this.metadata,
    );
  }

  /// 将RAG结果转换为JSON格式
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'content': content,
      'score': score,
      'metadata': metadata,
    };
  }

  /// 从JSON创建RAG结果
  factory RagResult.fromJson(Map<String, dynamic> json) {
    return RagResult(
      id: json['id'] as String,
      content: json['content'] as String,
      score: (json['score'] as num).toDouble(),
      metadata: json['metadata'] as Map<String, dynamic>? ?? {},
    );
  }

  @override
  String toString() {
    return 'RagResult(id: $id, score: $score, content: ${content.substring(0, content.length > 50 ? 50 : content.length)}...)';
  }
}
