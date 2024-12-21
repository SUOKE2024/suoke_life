import 'package:json_annotation/json_annotation.dart';

@JsonSerializable()
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

  factory LifeRecord.fromJson(Map<String, dynamic> json) => _$LifeRecordFromJson(json);
  Map<String, dynamic> toJson() => _$LifeRecordToJson(this);
} 