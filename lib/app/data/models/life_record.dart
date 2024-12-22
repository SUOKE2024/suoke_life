class LifeRecord {
  final String id;
  final String userId;
  final String type; // 记录类型
  final String title;
  final String content;
  final List<String> tags;
  final DateTime createdAt;
  final bool isSync;

  LifeRecord({
    required this.id,
    required this.userId,
    required this.type,
    required this.title,
    required this.content,
    required this.tags,
    required this.createdAt,
    this.isSync = false,
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'user_id': userId,
      'type': type,
      'title': title,
      'content': content,
      'tags': tags,
      'created_at': createdAt.toIso8601String(),
      'is_sync': isSync,
    };
  }

  factory LifeRecord.fromMap(Map<String, dynamic> map) {
    return LifeRecord(
      id: map['id'],
      userId: map['user_id'],
      type: map['type'],
      title: map['title'],
      content: map['content'],
      tags: List<String>.from(map['tags'] ?? []),
      createdAt: DateTime.parse(map['created_at']),
      isSync: map['is_sync'] ?? false,
    );
  }

  LifeRecord copyWith({
    String? id,
    String? userId,
    String? type,
    String? title,
    String? content,
    List<String>? tags,
    DateTime? createdAt,
    bool? isSync,
  }) {
    return LifeRecord(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      type: type ?? this.type,
      title: title ?? this.title,
      content: content ?? this.content,
      tags: tags ?? this.tags,
      createdAt: createdAt ?? this.createdAt,
      isSync: isSync ?? this.isSync,
    );
  }

  // 为了向后兼容，保留 toJson/fromJson 方法
  Map<String, dynamic> toJson() => toMap();
  factory LifeRecord.fromJson(Map<String, dynamic> json) => LifeRecord.fromMap(json);
} 