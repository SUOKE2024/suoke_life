class HealthRecord {
  final String id;
  final String userId;
  final String type; // 记录类型
  final Map<String, dynamic> data; // 健康数据
  final DateTime recordedAt;
  final bool isSync; // 是否已同步

  HealthRecord({
    required this.id,
    required this.userId,
    required this.type,
    required this.data,
    required this.recordedAt,
    this.isSync = false,
  });

  factory HealthRecord.fromJson(Map<String, dynamic> json) {
    return HealthRecord(
      id: json['id'],
      userId: json['user_id'],
      type: json['type'],
      data: json['data'],
      recordedAt: DateTime.parse(json['recorded_at']),
      isSync: json['is_sync'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'type': type,
      'data': data,
      'recorded_at': recordedAt.toIso8601String(),
      'is_sync': isSync,
    };
  }
} 