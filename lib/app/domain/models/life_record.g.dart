// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'life_record.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

LifeRecord _$LifeRecordFromJson(Map<String, dynamic> json) => LifeRecord(
      id: json['id'] as String,
      title: json['title'] as String,
      content: json['content'] as String,
      createdAt: DateTime.parse(json['createdAt'] as String),
      tags:
          (json['tags'] as List<dynamic>?)?.map((e) => e as String).toList() ??
              const [],
    );

Map<String, dynamic> _$LifeRecordToJson(LifeRecord instance) =>
    <String, dynamic>{
      'id': instance.id,
      'title': instance.title,
      'content': instance.content,
      'createdAt': instance.createdAt.toIso8601String(),
      'tags': instance.tags,
    };
