import 'package:equatable/equatable.dart';
import 'package:json_annotation/json_annotation.dart';

part 'node_relation_model.g.dart';

/// 节点关系模型
@JsonSerializable()
class NodeRelationModel extends Equatable {
  /// 关系ID
  final String id;
  
  /// 源节点ID
  final String sourceNodeId;
  
  /// 目标节点ID
  final String targetNodeId;
  
  /// 关系类型
  final String relationType;
  
  /// 关系权重
  final double? weight;
  
  /// 元数据（JSON字符串）
  final String? metadata;
  
  /// 构造函数
  const NodeRelationModel({
    required this.id,
    required this.sourceNodeId,
    required this.targetNodeId,
    required this.relationType,
    this.weight,
    this.metadata,
  });
  
  /// 从JSON创建实例
  factory NodeRelationModel.fromJson(Map<String, dynamic> json) => 
      _$NodeRelationModelFromJson(json);
  
  /// 转换为JSON
  Map<String, dynamic> toJson() => _$NodeRelationModelToJson(this);
  
  /// 创建副本并更新字段
  NodeRelationModel copyWith({
    String? id,
    String? sourceNodeId,
    String? targetNodeId,
    String? relationType,
    double? weight,
    String? metadata,
  }) {
    return NodeRelationModel(
      id: id ?? this.id,
      sourceNodeId: sourceNodeId ?? this.sourceNodeId,
      targetNodeId: targetNodeId ?? this.targetNodeId,
      relationType: relationType ?? this.relationType,
      weight: weight ?? this.weight,
      metadata: metadata ?? this.metadata,
    );
  }
  
  @override
  List<Object?> get props => [
    id, 
    sourceNodeId, 
    targetNodeId, 
    relationType, 
    weight, 
    metadata,
  ];
} 