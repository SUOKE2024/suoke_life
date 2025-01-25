import 'package:json_annotation/json_annotation.dart';

part 'life_record.g.dart';

@JsonSerializable()
class LifeRecord {
  final String id;
  final String title;
  final String content;
  final DateTime createdAt;
  final List<String> tags;

  const LifeRecord({
    required this.id,
    required this.title,
    required this.content,
    required this.createdAt,
    this.tags = const [],
  });

  factory LifeRecord.fromJson(Map<String, dynamic> json) => 
      _$LifeRecordFromJson(json);

  Map<String, dynamic> toJson() => _$LifeRecordToJson(this);
} 