// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'knowledge_node_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

KnowledgeNodeModel _$KnowledgeNodeModelFromJson(Map<String, dynamic> json) =>
    KnowledgeNodeModel(
      id: json['id'] as String,
      type: json['type'] as String,
      title: json['title'] as String,
      description: json['description'] as String?,
      content: json['content'] as String?,
      createdAt: (json['createdAt'] as num).toInt(),
      updatedAt: (json['updatedAt'] as num).toInt(),
      metadata: json['metadata'] as String?,
      language: json['language'] as String? ?? 'zh-CN',
    );

Map<String, dynamic> _$KnowledgeNodeModelToJson(KnowledgeNodeModel instance) =>
    <String, dynamic>{
      'id': instance.id,
      'type': instance.type,
      'title': instance.title,
      'description': instance.description,
      'content': instance.content,
      'createdAt': instance.createdAt,
      'updatedAt': instance.updatedAt,
      'metadata': instance.metadata,
      'language': instance.language,
    };
