import 'package:equatable/equatable.dart';

/// 知识图谱节点实体类
class KnowledgeNode extends Equatable {
  /// 节点唯一标识
  final String id;

  /// 节点名称
  final String name;

  /// 节点类型（例如：疾病、症状、治疗方法等）
  final String type;

  /// 节点所属主题（例如：中医养生、西医诊断等）
  final String topic;

  /// 节点权重（用于影响节点大小和重要性）
  final double weight;

  /// 节点描述
  final String? description;

  /// 节点内容
  final String? content;

  /// 节点位置X坐标（用于图谱渲染）
  double? x;

  /// 节点位置Y坐标（用于图谱渲染）
  double? y;

  /// 是否固定位置
  bool isFixed;

  /// 创建时间（ISO8601格式）
  final DateTime createdAt;

  /// 更新时间（ISO8601格式）
  final DateTime updatedAt;

  /// 元数据
  final Map<String, dynamic>? metadata;

  /// 向量嵌入
  final List<double>? embedding;

  /// 语言
  final String language;

  const KnowledgeNode({
    required this.id,
    required this.name,
    required this.type,
    required this.topic,
    this.weight = 1.0,
    this.description,
    this.content,
    this.x,
    this.y,
    this.isFixed = false,
    required this.createdAt,
    required this.updatedAt,
    this.metadata,
    this.embedding,
    this.language = 'zh-CN',
  });

  /// 从JSON映射创建实体
  factory KnowledgeNode.fromJson(Map<String, dynamic> json) {
    return KnowledgeNode(
      id: json['id'] as String,
      name: json['name'] as String,
      type: json['type'] as String,
      topic: json['topic'] as String,
      weight: (json['weight'] as num?)?.toDouble() ?? 1.0,
      description: json['description'] as String?,
      content: json['content'] as String?,
      x: (json['x'] as num?)?.toDouble(),
      y: (json['y'] as num?)?.toDouble(),
      isFixed: json['isFixed'] as bool? ?? false,
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
      metadata: json['metadata'] as Map<String, dynamic>?,
      embedding: json['embedding'] as List<double>?,
      language: json['language'] as String? ?? 'zh-CN',
    );
  }

  /// 从数据库映射创建实体
  factory KnowledgeNode.fromMap(Map<String, dynamic> map) {
    return KnowledgeNode(
      id: map['id'] as String,
      name: map['name'] as String,
      type: map['type'] as String,
      topic: map['topic'] as String? ?? '',
      weight: (map['weight'] as num?)?.toDouble() ?? 1.0,
      description: map['description'] as String?,
      content: map['content'] as String?,
      x: (map['x'] as num?)?.toDouble(),
      y: (map['y'] as num?)?.toDouble(),
      isFixed: (map['is_fixed'] as int? ?? 0) == 1,
      createdAt: DateTime.parse(map['created_at'] as String),
      updatedAt: DateTime.parse(map['updated_at'] as String),
      metadata: map['metadata'] as Map<String, dynamic>?,
      embedding: map['embedding'] as List<double>?,
      language: map['language'] as String? ?? 'zh-CN',
    );
  }

  /// 将实体转换为JSON映射
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'type': type,
      'topic': topic,
      'weight': weight,
      'description': description,
      'content': content,
      'x': x,
      'y': y,
      'isFixed': isFixed,
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt.toIso8601String(),
      'metadata': metadata,
      'embedding': embedding,
      'language': language,
    };
  }

  /// 将实体转换为数据库映射
  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'name': name,
      'type': type,
      'topic': topic,
      'weight': weight,
      'description': description,
      'content': content,
      'x': x,
      'y': y,
      'is_fixed': isFixed ? 1 : 0,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'metadata': metadata,
      'embedding': embedding,
      'language': language,
    };
  }

  /// 创建一个具有新值的副本
  KnowledgeNode copyWith({
    String? id,
    String? name,
    String? type,
    String? topic,
    double? weight,
    String? description,
    String? content,
    double? x,
    double? y,
    bool? isFixed,
    DateTime? createdAt,
    DateTime? updatedAt,
    Map<String, dynamic>? metadata,
    List<double>? embedding,
    String? language,
  }) {
    return KnowledgeNode(
      id: id ?? this.id,
      name: name ?? this.name,
      type: type ?? this.type,
      topic: topic ?? this.topic,
      weight: weight ?? this.weight,
      description: description ?? this.description,
      content: content ?? this.content,
      x: x ?? this.x,
      y: y ?? this.y,
      isFixed: isFixed ?? this.isFixed,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      metadata: metadata ?? this.metadata,
      embedding: embedding ?? this.embedding,
      language: language ?? this.language,
    );
  }

  @override
  List<Object?> get props => [
    id, 
    name, 
    type, 
    topic, 
    weight, 
    description, 
    content, 
    x, 
    y, 
    isFixed, 
    createdAt, 
    updatedAt, 
    metadata, 
    embedding, 
    language,
  ];
}
