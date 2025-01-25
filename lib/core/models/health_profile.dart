import 'dart:convert';

class HealthProfile {
  final String userId;
  final Map<String, dynamic> healthMetrics;

  const HealthProfile({
    required this.userId,
    required this.healthMetrics,
  });

  Map<String, dynamic> toMap() {
    return {
      'userId': userId,
      'healthMetrics': jsonEncode(healthMetrics), //  将 healthMetrics 转换为 JSON 字符串存储
    };
  }

  factory HealthProfile.fromMap(Map<String, dynamic> map) {
    return HealthProfile(
      userId: map['userId'] as String,
      healthMetrics: jsonDecode(map['healthMetrics'] as String) as Map<String, dynamic>, //  将 JSON 字符串解析为 Map
    );
  }
} 