import '../base/entity.dart';
import 'dart:convert';

/// 生活记录实体
class LifeRecord extends Entity {
  final int? id;
  final String title;
  final String content;
  final String timestamp;
  final String category;
  final List<String> tags;
  final String? location;
  final String userId;

  LifeRecord({
    this.id,
    required this.title,
    required this.content,
    required this.timestamp,
    required this.category,
    required this.tags,
    this.location,
    required this.userId,
  });

  @override
  int? get id => this.id;

  @override
  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'title': title,
      'content': content,
      'timestamp': timestamp,
      'category': category,
      'tags': json.encode(tags),
      'location': location,
      'user_id': userId,
    };
  }

  factory LifeRecord.fromMap(Map<String, dynamic> map) {
    return LifeRecord(
      id: map['id'] as int?,
      title: map['title'] as String,
      content: map['content'] as String,
      timestamp: map['timestamp'] as String,
      category: map['category'] as String,
      tags: List<String>.from(json.decode(map['tags'])),
      location: map['location'] as String?,
      userId: map['user_id'] as String,
    );
  }

  static String get tableName => 'life_records';

  static String get createTableSql => '''
    CREATE TABLE IF NOT EXISTS life_records(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT,
      content TEXT,
      timestamp TEXT,
      category TEXT,
      tags TEXT,
      location TEXT,
      user_id TEXT
    )
  ''';

  static List<String> get createIndexSql => [
    'CREATE INDEX idx_life_records_user ON life_records(user_id)',
    'CREATE INDEX idx_life_records_category ON life_records(category)',
    'CREATE INDEX idx_life_records_timestamp ON life_records(timestamp)',
  ];

  LifeRecord copyWith({
    int? id,
    String? title,
    String? content,
    String? timestamp,
    String? category,
    List<String>? tags,
    String? location,
    String? userId,
  }) {
    return LifeRecord(
      id: id ?? this.id,
      title: title ?? this.title,
      content: content ?? this.content,
      timestamp: timestamp ?? this.timestamp,
      category: category ?? this.category,
      tags: tags ?? this.tags,
      location: location ?? this.location,
      userId: userId ?? this.userId,
    );
  }

  @override
  String toString() {
    return 'LifeRecord(id: $id, title: $title, category: $category, timestamp: $timestamp, userId: $userId)';
  }
} 