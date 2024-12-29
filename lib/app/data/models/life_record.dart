enum RecordType {
  daily,
  health,
  event,
  note,
}

class LifeRecord {
  final String id;
  final String userId;
  final String title;
  final String? content;
  final String type;
  final List<String>? images;
  final Map<String, dynamic>? metadata;
  final DateTime createdAt;

  LifeRecord({
    required this.id,
    required this.userId,
    required this.title,
    this.content,
    required this.type,
    this.images,
    this.metadata,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();

  factory LifeRecord.fromMap(Map<String, dynamic> map) {
    return LifeRecord(
      id: map['id'] as String,
      userId: map['user_id'] as String,
      title: map['title'] as String,
      content: map['content'] as String?,
      type: map['type'] as String,
      images: map['images'] != null 
          ? List<String>.from(map['images'] as List)
          : null,
      metadata: map['metadata'] != null 
          ? Map<String, dynamic>.from(map['metadata'] as Map)
          : null,
      createdAt: DateTime.fromMillisecondsSinceEpoch(map['created_at'] as int),
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'user_id': userId,
      'title': title,
      'content': content,
      'type': type,
      'images': images,
      'metadata': metadata,
      'created_at': createdAt.millisecondsSinceEpoch,
    };
  }
} 