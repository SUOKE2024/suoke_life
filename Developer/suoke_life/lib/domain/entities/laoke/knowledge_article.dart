import 'package:equatable/equatable.dart';

/// 知识文章实体
class KnowledgeArticle extends Equatable {
  /// 唯一ID
  final String id;
  
  /// 标题
  final String title;
  
  /// 文章内容
  final String content;
  
  /// 摘要
  final String summary;
  
  /// 作者名
  final String authorName;
  
  /// 封面图片URL
  final String? coverImageUrl;
  
  /// 分类ID
  final String categoryId;
  
  /// 分类名称
  final String categoryName;
  
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
  
  /// 创建时间
  final DateTime createdAt;
  
  /// 更新时间
  final DateTime updatedAt;

  const KnowledgeArticle({
    required this.id,
    required this.title,
    required this.content,
    required this.summary,
    required this.authorName,
    this.coverImageUrl,
    required this.categoryId,
    required this.categoryName,
    required this.tags,
    required this.viewCount,
    required this.likeCount,
    required this.favoriteCount,
    required this.shareCount,
    required this.commentCount,
    required this.createdAt,
    required this.updatedAt,
  });

  @override
  List<Object?> get props => [
        id,
        title,
        content,
        summary,
        authorName,
        coverImageUrl,
        categoryId,
        categoryName,
        tags,
        viewCount,
        likeCount,
        favoriteCount,
        shareCount,
        commentCount,
        createdAt,
        updatedAt,
      ];
} 