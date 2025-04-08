import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:suoke_life/data/models/laoke/blog_post_model.dart';
import 'package:suoke_life/domain/entities/laoke/blog_post.dart';

void main() {
  final blogPostModel = BlogPostModel(
    id: '1',
    title: '中医养生之道',
    content: '详细内容...',
    summary: '本文介绍了中医养生的方法和要点',
    authorId: 'author1',
    authorName: '张医生',
    authorAvatarUrl: 'https://example.com/avatar.jpg',
    coverImageUrl: 'https://example.com/cover.jpg',
    categoryId: 'cat1',
    categoryName: '养生保健',
    tags: ['养生', '中医', '健康'],
    viewCount: 100,
    likeCount: 50,
    favoriteCount: 30,
    shareCount: 10,
    commentCount: 5,
    status: 'published',
    createdAt: DateTime(2023, 1, 1),
    updatedAt: DateTime(2023, 1, 5),
    publishedAt: DateTime(2023, 1, 2),
  );

  final Map<String, dynamic> jsonMap = {
    'id': '1',
    'title': '中医养生之道',
    'content': '详细内容...',
    'summary': '本文介绍了中医养生的方法和要点',
    'author_id': 'author1',
    'author_name': '张医生',
    'author_avatar_url': 'https://example.com/avatar.jpg',
    'cover_image_url': 'https://example.com/cover.jpg',
    'category_id': 'cat1',
    'category_name': '养生保健',
    'tags': ['养生', '中医', '健康'],
    'view_count': 100,
    'like_count': 50,
    'favorite_count': 30,
    'share_count': 10,
    'comment_count': 5,
    'status': 'published',
    'created_at': '2023-01-01T00:00:00.000',
    'updated_at': '2023-01-05T00:00:00.000',
    'published_at': '2023-01-02T00:00:00.000',
  };

  group('BlogPostModel', () {
    test('应该是BlogPost的子类', () {
      // 验证
      expect(blogPostModel, isA<BlogPost>());
    });

    test('fromJson应该正确解析JSON', () {
      // 操作
      final result = BlogPostModel.fromJson(jsonMap);
      
      // 验证
      expect(result, equals(blogPostModel));
      expect(result.tags.length, equals(3));
      expect(result.status, equals('published'));
    });

    test('toJson应该正确转换为JSON', () {
      // 操作
      final result = blogPostModel.toJson();
      
      // 验证
      expect(result['id'], equals(jsonMap['id']));
      expect(result['title'], equals(jsonMap['title']));
      expect(result['author_name'], equals(jsonMap['author_name']));
      expect(result['tags'].length, equals(jsonMap['tags'].length));
    });

    test('处理缺少的字段', () {
      // 准备
      final incompleteJson = {
        'id': '2',
        'title': '四季养生方法',
        'content': '详细内容...',
      };
      
      // 操作
      final result = BlogPostModel.fromJson(incompleteJson);
      
      // 验证
      expect(result.id, equals('2'));
      expect(result.title, equals('四季养生方法'));
      expect(result.content, equals('详细内容...'));
      expect(result.summary, equals(''));
      expect(result.authorName, equals('未知作者'));
      expect(result.tags, isEmpty);
      expect(result.publishedAt, isNull);
    });
  });
} 