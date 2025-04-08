import 'dart:convert';
import 'package:suoke_life/domain/entities/constitution_type.dart';

/// 体质数据实体类
///
/// 存储用户的体质辨识结果，包括各体质类型的评分和主体质类型
class ConstitutionData {
  /// 所有体质类型的评分 (0-100)
  final Map<ConstitutionType, double> scores;

  /// 体质评估的时间戳
  final DateTime timestamp;

  /// 用户ID
  final String userId;

  /// 构造函数
  ConstitutionData({
    required this.scores,
    required this.timestamp,
    required this.userId,
  });

  /// 获取主体质类型
  ConstitutionType? get primaryType {
    if (scores.isEmpty) return null;

    // 找出评分最高的体质类型
    ConstitutionType maxType = scores.keys.first;
    double maxScore = scores[maxType] ?? 0;

    for (final entry in scores.entries) {
      if (entry.value > maxScore) {
        maxType = entry.key;
        maxScore = entry.value;
      }
    }

    // 只有当评分高于60分时，才认为是主体质类型
    return maxScore >= 60 ? maxType : null;
  }

  /// 获取体质类型列表（按评分降序排列）
  List<ConstitutionType> get constitutionTypes {
    final types = scores.keys.toList();
    types.sort((a, b) => (scores[b] ?? 0).compareTo(scores[a] ?? 0));
    return types;
  }

  /// 获取特定体质类型的评分
  double getScoreForType(ConstitutionType type) {
    return scores[type] ?? 0;
  }

  /// 从JSON创建体质数据
  factory ConstitutionData.fromJson(Map<String, dynamic> json) {
    final Map<ConstitutionType, double> scores = {};

    // 解析评分
    if (json['scores'] != null) {
      final scoreMap = json['scores'] as Map<String, dynamic>;
      for (final entry in scoreMap.entries) {
        try {
          final type =
              ConstitutionType.values.firstWhere((t) => t.name == entry.key);
          scores[type] = (entry.value as num).toDouble();
        } catch (e) {
          // 忽略无法解析的体质类型
        }
      }
    }

    return ConstitutionData(
      scores: scores,
      timestamp: DateTime.parse(json['timestamp'] as String),
      userId: json['userId'] as String,
    );
  }

  /// 转换为JSON
  Map<String, dynamic> toJson() {
    final Map<String, dynamic> scoreMap = {};

    for (final entry in scores.entries) {
      scoreMap[entry.key.name] = entry.value;
    }

    return {
      'scores': scoreMap,
      'timestamp': timestamp.toIso8601String(),
      'userId': userId,
    };
  }

  /// 创建体质数据副本
  ConstitutionData copyWith({
    Map<ConstitutionType, double>? scores,
    DateTime? timestamp,
    String? userId,
  }) {
    return ConstitutionData(
      scores: scores ?? Map.from(this.scores),
      timestamp: timestamp ?? this.timestamp,
      userId: userId ?? this.userId,
    );
  }

  @override
  String toString() {
    return 'ConstitutionData(primaryType: ${primaryType?.name}, scores: $scores)';
  }
}
