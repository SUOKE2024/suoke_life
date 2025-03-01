import 'package:equatable/equatable.dart';

/// 节点关系实体
class NodeRelation extends Equatable {
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
  
  /// 元数据
  final Map<String, dynamic>? metadata;
  
  /// 构造函数
  const NodeRelation({
    required this.id,
    required this.sourceNodeId,
    required this.targetNodeId,
    required this.relationType,
    this.weight,
    this.metadata,
  });
  
  /// 创建副本并更新字段
  NodeRelation copyWith({
    String? id,
    String? sourceNodeId,
    String? targetNodeId,
    String? relationType,
    double? weight,
    Map<String, dynamic>? metadata,
  }) {
    return NodeRelation(
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