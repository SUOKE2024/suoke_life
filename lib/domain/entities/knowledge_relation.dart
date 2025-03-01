/// 知识图谱关系实体类
class KnowledgeRelation {
  /// 关系唯一标识
  final String id;

  /// 源节点ID
  final String sourceId;

  /// 目标节点ID
  final String targetId;

  /// 关系类型（例如：导致、治疗、预防等）
  final String type;

  /// 关系强度（用于影响连接线的粗细）
  final double strength;

  /// 关系描述
  final String description;

  /// 是否为双向关系
  final bool isBidirectional;

  /// 创建时间（ISO8601格式）
  final String? createdAt;

  /// 更新时间（ISO8601格式）
  final String? updatedAt;

  KnowledgeRelation({
    required this.id,
    required this.sourceId,
    required this.targetId,
    required this.type,
    this.strength = 1.0,
    this.description = '',
    this.isBidirectional = false,
    this.createdAt,
    this.updatedAt,
  });

  /// 从JSON映射创建实体
  factory KnowledgeRelation.fromJson(Map<String, dynamic> json) {
    return KnowledgeRelation(
      id: json['id'] as String,
      sourceId: json['sourceId'] as String,
      targetId: json['targetId'] as String,
      type: json['type'] as String,
      strength: (json['strength'] as num?)?.toDouble() ?? 1.0,
      description: json['description'] as String? ?? '',
      isBidirectional: json['isBidirectional'] as bool? ?? false,
      createdAt: json['createdAt'] as String?,
      updatedAt: json['updatedAt'] as String?,
    );
  }

  /// 从数据库映射创建实体（用于数据库操作）
  factory KnowledgeRelation.fromMap(Map<String, dynamic> map) {
    return KnowledgeRelation(
      id: map['id'] as String,
      sourceId: map['source_id'] as String,
      targetId: map['target_id'] as String,
      type: map['type'] as String,
      strength: (map['weight'] as num?)?.toDouble() ?? 1.0,
      description: map['description'] as String? ?? '',
      isBidirectional: (map['is_bidirectional'] as int? ?? 0) == 1,
      createdAt: map['created_at'] as String?,
      updatedAt: map['updated_at'] as String?,
    );
  }

  /// 将实体转换为JSON映射
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'sourceId': sourceId,
      'targetId': targetId,
      'type': type,
      'strength': strength,
      'description': description,
      'isBidirectional': isBidirectional,
      'createdAt': createdAt,
      'updatedAt': updatedAt,
    };
  }

  /// 将实体转换为数据库映射（用于数据库操作）
  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'source_id': sourceId,
      'target_id': targetId,
      'type': type,
      'weight': strength,
      'description': description,
      'is_bidirectional': isBidirectional ? 1 : 0,
      'created_at': createdAt,
      'updated_at': updatedAt,
    };
  }

  /// 创建一个具有新值的副本
  KnowledgeRelation copyWith({
    String? id,
    String? sourceId,
    String? targetId,
    String? type,
    double? strength,
    String? description,
    bool? isBidirectional,
    String? createdAt,
    String? updatedAt,
  }) {
    return KnowledgeRelation(
      id: id ?? this.id,
      sourceId: sourceId ?? this.sourceId,
      targetId: targetId ?? this.targetId,
      type: type ?? this.type,
      strength: strength ?? this.strength,
      description: description ?? this.description,
      isBidirectional: isBidirectional ?? this.isBidirectional,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}
