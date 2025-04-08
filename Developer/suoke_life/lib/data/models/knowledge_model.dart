import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:flutter/foundation.dart';

part 'knowledge_model.freezed.dart';
part 'knowledge_model.g.dart';

/// 知识节点模型
@freezed
class KnowledgeNodeModel with _$KnowledgeNodeModel {
  const factory KnowledgeNodeModel({
    required String id,
    required String title,
    required String content,
    required List<String> tags,
    required String nodeType,
    required DateTime createdAt,
    required DateTime updatedAt,
    Map<String, dynamic>? metadata,
    List<KnowledgeRelationModel>? relations,
  }) = _KnowledgeNodeModel;

  factory KnowledgeNodeModel.fromJson(Map<String, dynamic> json) => _$KnowledgeNodeModelFromJson(json);
}

/// 知识关系模型
@freezed
class KnowledgeRelationModel with _$KnowledgeRelationModel {
  const factory KnowledgeRelationModel({
    required String id,
    required String sourceId,
    required String targetId,
    required String relationType,
    required DateTime createdAt,
    required DateTime updatedAt,
    Map<String, dynamic>? metadata,
  }) = _KnowledgeRelationModel;

  factory KnowledgeRelationModel.fromJson(Map<String, dynamic> json) => _$KnowledgeRelationModelFromJson(json);
} 