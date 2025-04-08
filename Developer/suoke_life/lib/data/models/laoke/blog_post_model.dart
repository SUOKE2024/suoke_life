import 'package:suoke_life/domain/entities/laoke/blog_post.dart';

class BlogPostModel extends BlogPost {
  const BlogPostModel({
    required String id,
    required String title,
    required String content,
    required String summary,
    required String authorId,
    required String authorName,
    String? authorAvatarUrl,
    String? coverImageUrl,
    String? categoryId,
    String? categoryName,
    required List<String> tags,
    required int viewCount,
    required int likeCount,
    required int favoriteCount,
    required int shareCount,
    required int commentCount,
    required String status,
    required DateTime createdAt,
    required DateTime updatedAt,
    DateTime? publishedAt,
  }) : super(
          id: id,
          title: title,
          content: content,
          summary: summary,
          authorId: authorId,
          authorName: authorName,
          authorAvatarUrl: authorAvatarUrl,
          coverImageUrl: coverImageUrl,
          categoryId: categoryId,
          categoryName: categoryName,
          tags: tags,
          viewCount: viewCount,
          likeCount: likeCount,
          favoriteCount: favoriteCount,
          shareCount: shareCount,
          commentCount: commentCount,
          status: status,
          createdAt: createdAt,
          updatedAt: updatedAt,
          publishedAt: publishedAt,
        );

  factory BlogPostModel.fromJson(Map<String, dynamic> json) {
    return BlogPostModel(
      id: json['id'],
      title: json['title'],
      content: json['content'],
      summary: json['summary'] ?? '',
      authorId: json['author_id'] ?? '',
      authorName: json['author_name'] ?? '未知作者',
      authorAvatarUrl: json['author_avatar_url'],
      coverImageUrl: json['cover_image_url'],
      categoryId: json['category_id'],
      categoryName: json['category_name'],
      tags: json['tags'] != null
          ? List<String>.from(json['tags'])
          : <String>[],
      viewCount: json['view_count'] ?? 0,
      likeCount: json['like_count'] ?? 0,
      favoriteCount: json['favorite_count'] ?? 0,
      shareCount: json['share_count'] ?? 0,
      commentCount: json['comment_count'] ?? 0,
      status: json['status'] ?? 'published',
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : DateTime.now(),
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'])
          : DateTime.now(),
      publishedAt: json['published_at'] != null
          ? DateTime.parse(json['published_at'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'content': content,
      'summary': summary,
      'author_id': authorId,
      'author_name': authorName,
      'author_avatar_url': authorAvatarUrl,
      'cover_image_url': coverImageUrl,
      'category_id': categoryId,
      'category_name': categoryName,
      'tags': tags,
      'view_count': viewCount,
      'like_count': likeCount,
      'favorite_count': favoriteCount,
      'share_count': shareCount,
      'comment_count': commentCount,
      'status': status,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'published_at': publishedAt?.toIso8601String(),
    };
  }
} 