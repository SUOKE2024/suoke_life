import 'package:equatable/equatable.dart';
import 'package:json_annotation/json_annotation.dart';

part 'knowledge_node_model.g.dart';

/// 知识节点模型
@JsonSerializable()
class KnowledgeNodeModel extends Equatable {
  /// 节点ID
  final String id;
  
  /// 节点类型
  final String type;
  
  /// 节点标题
  final String title;
  
  /// 节点描述
  final String? description;
  
  /// 节点内容
  final String? content;
  
  /// 创建时间
  final int createdAt;
  
  /// 更新时间
  final int updatedAt;
  
  /// 元数据（JSON字符串）
  final String? metadata;
  
  /// 向量嵌入
  @JsonKey(ignore: true)
  final List<double>? embedding;
  
  /// 语言
  final String language;
  
  /// 构造函数
  const KnowledgeNodeModel({
    required this.id,
    required this.type,
    required this.title,
    this.description,
    this.content,
    required this.createdAt,
    required this.updatedAt,
    this.metadata,
    this.embedding,
    this.language = 'zh-CN',
  });
  
  /// 从JSON创建实例
  factory KnowledgeNodeModel.fromJson(Map<String, dynamic> json) => 
      _$KnowledgeNodeModelFromJson(json);
  
  /// 转换为JSON
  Map<String, dynamic> toJson() => _$KnowledgeNodeModelToJson(this);
  
  /// 创建副本并更新字段
  KnowledgeNodeModel copyWith({
    String? id,
    String? type,
    String? title,
    String? description,
    String? content,
    int? createdAt,
    int? updatedAt,
    String? metadata,
    List<double>? embedding,
    String? language,
  }) {
    return KnowledgeNodeModel(
      id: id ?? this.id,
      type: type ?? this.type,
      title: title ?? this.title,
      description: description ?? this.description,
      content: content ?? this.content,
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
    type, 
    title, 
    description, 
    content, 
    createdAt, 
    updatedAt, 
    metadata, 
    language,
  ];
} 