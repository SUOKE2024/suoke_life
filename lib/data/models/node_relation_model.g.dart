// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'node_relation_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

NodeRelationModel _$NodeRelationModelFromJson(Map<String, dynamic> json) =>
    NodeRelationModel(
      id: json['id'] as String,
      sourceNodeId: json['sourceNodeId'] as String,
      targetNodeId: json['targetNodeId'] as String,
      relationType: json['relationType'] as String,
      weight: (json['weight'] as num?)?.toDouble(),
      metadata: json['metadata'] as String?,
    );

Map<String, dynamic> _$NodeRelationModelToJson(NodeRelationModel instance) =>
    <String, dynamic>{
      'id': instance.id,
      'sourceNodeId': instance.sourceNodeId,
      'targetNodeId': instance.targetNodeId,
      'relationType': instance.relationType,
      'weight': instance.weight,
      'metadata': instance.metadata,
    };
