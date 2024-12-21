import 'package:hive/hive.dart';
import 'package:suoke_life/data/models/hive_type_ids.dart';

part 'life_record.g.dart';

@HiveType(typeId: HiveTypeIds.lifeRecord)
class LifeRecord extends HiveObject {
  @HiveField(0)
  final String id;

  @HiveField(1)
  final String title;

  @HiveField(2)
  final String? content;

  @HiveField(3)
  final String time;

  @HiveField(4)
  final List<String> tags;

  @HiveField(5)
  final String? location;

  @HiveField(6)
  final List<String>? images;

  @HiveField(7)
  final Map<String, dynamic>? metadata;

  @HiveField(8)
  final DateTime createdAt;

  @HiveField(9)
  final DateTime? updatedAt;

  LifeRecord({
    required this.id,
    required this.title,
    this.content,
    required this.time,
    this.tags = const [],
    this.location,
    this.images,
    this.metadata,
    required this.createdAt,
    this.updatedAt,
  });

  LifeRecord copyWith({
    String? title,
    String? content,
    String? time,
    List<String>? tags,
    String? location,
    List<String>? images,
    Map<String, dynamic>? metadata,
  }) {
    return LifeRecord(
      id: id,
      title: title ?? this.title,
      content: content ?? this.content,
      time: time ?? this.time,
      tags: tags ?? this.tags,
      location: location ?? this.location,
      images: images ?? this.images,
      metadata: metadata ?? this.metadata,
      createdAt: createdAt,
      updatedAt: DateTime.now(),
    );
  }

  // 从JSON创建
  factory LifeRecord.fromJson(Map<String, dynamic> json) {
    return LifeRecord(
      id: json['id'],
      title: json['title'],
      content: json['content'],
      time: json['time'],
      tags: List<String>.from(json['tags'] ?? []),
      location: json['location'],
      images: json['images'] != null ? List<String>.from(json['images']) : null,
      metadata: json['metadata'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: json['updated_at'] != null 
          ? DateTime.parse(json['updated_at']) 
          : null,
    );
  }

  // 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'content': content,
      'time': time,
      'tags': tags,
      'location': location,
      'images': images,
      'metadata': metadata,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
    };
  }
} 