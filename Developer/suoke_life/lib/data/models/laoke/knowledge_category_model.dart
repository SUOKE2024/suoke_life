import 'package:suoke_life/domain/entities/laoke/knowledge_category.dart';

class KnowledgeCategoryModel extends KnowledgeCategory {
  const KnowledgeCategoryModel({
    required String id,
    required String name,
    required String description,
    required String iconUrl,
    required int articleCount,
    required DateTime updatedAt,
  }) : super(
          id: id,
          name: name,
          description: description, 
          iconUrl: iconUrl,
          articleCount: articleCount,
          updatedAt: updatedAt,
        );

  factory KnowledgeCategoryModel.fromJson(Map<String, dynamic> json) {
    return KnowledgeCategoryModel(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      iconUrl: json['icon_url'] ?? '',
      articleCount: json['article_count'] ?? 0,
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'])
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'icon_url': iconUrl,
      'article_count': articleCount,
      'updated_at': updatedAt.toIso8601String(),
    };
  }
} 