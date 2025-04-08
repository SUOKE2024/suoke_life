import 'package:equatable/equatable.dart';

/// 知识分类实体
class KnowledgeCategory extends Equatable {
  /// 唯一ID
  final String id;
  
  /// 分类名称
  final String name;
  
  /// 分类描述
  final String description;
  
  /// 图标URL
  final String iconUrl;
  
  /// 文章数量
  final int articleCount;
  
  /// 更新时间
  final DateTime updatedAt;

  const KnowledgeCategory({
    required this.id,
    required this.name,
    required this.description,
    required this.iconUrl,
    required this.articleCount,
    required this.updatedAt,
  });

  @override
  List<Object?> get props => [id, name, description, iconUrl, articleCount, updatedAt];
} 