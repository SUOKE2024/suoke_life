import 'package:flutter/foundation.dart';
import 'dart:math';

/// RAG查询结果模型
///
/// 存储检索增强生成的查询结果，包括问题、答案、来源和时间戳
class RAGResult {
  /// 用户的原始查询
  final String query;
  
  /// 生成的回答
  final String answer;
  
  /// 回答的来源列表
  final List<Map<String, dynamic>> sources;
  
  /// 查询时间戳
  final DateTime timestamp;
  
  /// 构造函数
  RAGResult({
    required this.query,
    required this.answer,
    required this.sources,
    required this.timestamp,
  });
  
  /// 从JSON创建RAGResult实例
  factory RAGResult.fromJson(Map<String, dynamic> json) {
    return RAGResult(
      query: json['query'] as String,
      answer: json['answer'] as String,
      sources: List<Map<String, dynamic>>.from(json['sources']),
      timestamp: DateTime.parse(json['timestamp'] as String),
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'query': query,
      'answer': answer,
      'sources': sources,
      'timestamp': timestamp.toIso8601String(),
    };
  }
  
  /// 复制并修改RAGResult实例
  RAGResult copyWith({
    String? query,
    String? answer,
    List<Map<String, dynamic>>? sources,
    DateTime? timestamp,
  }) {
    return RAGResult(
      query: query ?? this.query,
      answer: answer ?? this.answer,
      sources: sources ?? this.sources,
      timestamp: timestamp ?? this.timestamp,
    );
  }
  
  @override
  String toString() {
    return 'RAGResult(query: $query, answer: ${answer.substring(0, min(50, answer.length))}..., sources: ${sources.length}, timestamp: $timestamp)';
  }
  
  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    
    return other is RAGResult &&
        other.query == query &&
        other.answer == answer &&
        listEquals(other.sources, sources) &&
        other.timestamp == timestamp;
  }
  
  @override
  int get hashCode {
    return query.hashCode ^
        answer.hashCode ^
        sources.hashCode ^
        timestamp.hashCode;
  }
} 