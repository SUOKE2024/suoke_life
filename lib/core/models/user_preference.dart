class UserPreference {
  final int? id;
  final String userId;
  final String agentId;
  final String key;
  final String value;
  final DateTime timestamp;

  UserPreference({
    this.id,
    required this.userId,
    required this.agentId,
    required this.key,
    required this.value,
    required this.timestamp,
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'userId': userId,
      'agentId': agentId,
      'key': key,
      'value': value,
      'timestamp': timestamp.millisecondsSinceEpoch, // 存储为时间戳
    };
  }

  factory UserPreference.fromMap(Map<String, dynamic> map) {
    return UserPreference(
      id: map['id'],
      userId: map['userId'],
      agentId: map['agentId'],
      key: map['key'],
      value: map['value'],
      timestamp: DateTime.fromMillisecondsSinceEpoch(map['timestamp']), // 从时间戳恢复
    );
  }
} 