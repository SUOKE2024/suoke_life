import 'package:equatable/equatable.dart';

/// 博客文章实体
class BlogPost extends Equatable {
  /// 唯一ID
  final String id;
  
  /// 标题
  final String title;
  
  /// 文章内容
  final String content;
  
  /// 摘要
  final String summary;
  
  /// 作者ID
  final String authorId;
  
  /// 作者名
  final String authorName;
  
  /// 作者头像URL
  final String? authorAvatarUrl;
  
  /// 封面图片URL
  final String? coverImageUrl;
  
  /// 分类ID
  final String? categoryId;
  
  /// 分类名称
  final String? categoryName;
  
  /// 标签列表
  final List<String> tags;
  
  /// 阅读数
  final int viewCount;
  
  /// 点赞数
  final int likeCount;
  
  /// 收藏数
  final int favoriteCount;
  
  /// 分享数
  final int shareCount;
  
  /// 评论数
  final int commentCount;
  
  /// 状态（草稿、已发布、已归档）
  final String status;
  
  /// 创建时间
  final DateTime createdAt;
  
  /// 更新时间
  final DateTime updatedAt;
  
  /// 发布时间
  final DateTime? publishedAt;

  const BlogPost({
    required this.id,
    required this.title,
    required this.content,
    required this.summary,
    required this.authorId,
    required this.authorName,
    this.authorAvatarUrl,
    this.coverImageUrl,
    this.categoryId,
    this.categoryName,
    required this.tags,
    required this.viewCount,
    required this.likeCount,
    required this.favoriteCount,
    required this.shareCount,
    required this.commentCount,
    required this.status,
    required this.createdAt,
    required this.updatedAt,
    this.publishedAt,
  });

  @override
  List<Object?> get props => [
        id,
        title,
        content,
        summary,
        authorId,
        authorName,
        authorAvatarUrl,
        coverImageUrl,
        categoryId,
        categoryName,
        tags,
        viewCount,
        likeCount,
        favoriteCount,
        shareCount,
        commentCount,
        status,
        createdAt,
        updatedAt,
        publishedAt,
      ];
} 