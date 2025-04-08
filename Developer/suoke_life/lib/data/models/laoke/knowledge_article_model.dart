import 'package:suoke_life/domain/entities/laoke/knowledge_article.dart';

class KnowledgeArticleModel extends KnowledgeArticle {
  const KnowledgeArticleModel({
    required String id,
    required String title,
    required String content,
    required String summary,
    required String authorName,
    String? coverImageUrl,
    required String categoryId,
    required String categoryName,
    required List<String> tags,
    required int viewCount,
    required int likeCount,
    required int favoriteCount,
    required int shareCount,
    required int commentCount,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) : super(
          id: id,
          title: title,
          content: content,
          summary: summary,
          authorName: authorName,
          coverImageUrl: coverImageUrl,
          categoryId: categoryId,
          categoryName: categoryName,
          tags: tags,
          viewCount: viewCount,
          likeCount: likeCount,
          favoriteCount: favoriteCount,
          shareCount: shareCount,
          commentCount: commentCount,
          createdAt: createdAt,
          updatedAt: updatedAt,
        );

  factory KnowledgeArticleModel.fromJson(Map<String, dynamic> json) {
    return KnowledgeArticleModel(
      id: json['id'],
      title: json['title'],
      content: json['content'],
      summary: json['summary'] ?? '',
      authorName: json['author_name'] ?? '老克',
      coverImageUrl: json['cover_image_url'],
      categoryId: json['category_id'] ?? '',
      categoryName: json['category_name'] ?? '',
      tags: json['tags'] != null
          ? List<String>.from(json['tags'])
          : <String>[],
      viewCount: json['view_count'] ?? 0,
      likeCount: json['like_count'] ?? 0,
      favoriteCount: json['favorite_count'] ?? 0,
      shareCount: json['share_count'] ?? 0,
      commentCount: json['comment_count'] ?? 0,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : DateTime.now(),
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'])
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'content': content,
      'summary': summary,
      'author_name': authorName,
      'cover_image_url': coverImageUrl,
      'category_id': categoryId,
      'category_name': categoryName,
      'tags': tags,
      'view_count': viewCount,
      'like_count': likeCount,
      'favorite_count': favoriteCount,
      'share_count': shareCount,
      'comment_count': commentCount,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }
} 