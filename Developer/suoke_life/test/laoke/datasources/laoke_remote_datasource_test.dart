import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:suoke_life/core/error/exceptions.dart';
import 'package:suoke_life/core/network/api_client.dart';
import 'package:suoke_life/core/network/api_constants.dart';
import 'package:suoke_life/data/datasources/remote/laoke_remote_datasource.dart';
import 'package:suoke_life/data/models/laoke/blog_post_model.dart';
import 'package:suoke_life/data/models/laoke/training_course_model.dart';

import '../../mocks/laoke_mocks.mocks.dart';

void main() {
  late LaokeRemoteDataSourceImpl dataSource;
  late MockApiClient mockApiClient;

  setUp(() {
    mockApiClient = MockApiClient();
    dataSource = LaokeRemoteDataSourceImpl(apiClient: mockApiClient);
  });

  group('getTrainingCourses', () {
    final testCourseList = {
      'items': [
        {
          'id': '1',
          'title': '中医基础理论',
          'description': '课程描述',
          'instructor_name': '王老师',
          'level': '初级',
          'category_id': 'cat1',
          'category_name': '基础知识',
        }
      ],
      'total': 1,
      'page': 1,
      'total_pages': 1,
    };

    test('应该调用API并返回课程列表', () async {
      // 准备
      when(mockApiClient.get(
        any,
        queryParameters: anyNamed('queryParameters'),
      )).thenAnswer((_) async => testCourseList);

      // 执行
      final result = await dataSource.getTrainingCourses(
        categoryId: 'cat1',
        level: '初级',
        page: 1,
        limit: 10,
      );

      // 验证
      verify(mockApiClient.get(
        '${ApiConstants.laokeServiceBaseUrl}/courses',
        queryParameters: {
          'category_id': 'cat1',
          'level': '初级',
          'page': 1,
          'limit': 10,
        },
      ));
      expect(result, equals(testCourseList));
    });

    test('在服务器异常时应该抛出ServerException', () async {
      // 准备
      when(mockApiClient.get(
        any,
        queryParameters: anyNamed('queryParameters'),
      )).thenThrow(Exception('Server error'));

      // 执行和验证
      expect(
        () => dataSource.getTrainingCourses(page: 1, limit: 10),
        throwsA(isA<ServerException>()),
      );
    });
  });

  group('getTrainingCourseById', () {
    final testCourse = {
      'id': '1',
      'title': '中医基础理论',
      'description': '课程描述',
      'content': '课程内容...',
      'instructor_name': '王老师',
      'level': '初级',
      'category_id': 'cat1',
      'category_name': '基础知识',
      'chapters': [],
    };

    test('应该调用API并返回课程详情', () async {
      // 准备
      when(mockApiClient.get(any)).thenAnswer((_) async => testCourse);

      // 执行
      final result = await dataSource.getTrainingCourseById('1');

      // 验证
      verify(mockApiClient.get('${ApiConstants.laokeServiceBaseUrl}/courses/1'));
      expect(result, equals(testCourse));
    });

    test('在服务器异常时应该抛出ServerException', () async {
      // 准备
      when(mockApiClient.get(any)).thenThrow(Exception('Server error'));

      // 执行和验证
      expect(
        () => dataSource.getTrainingCourseById('1'),
        throwsA(isA<ServerException>()),
      );
    });
  });

  group('getBlogPosts', () {
    final testBlogPostList = {
      'items': [
        {
          'id': '1',
          'title': '中医养生之道',
          'summary': '文章摘要',
          'author_name': '张医生',
          'category_id': 'cat1',
          'category_name': '养生保健',
        }
      ],
      'total': 1,
      'page': 1,
      'total_pages': 1,
    };

    test('应该调用API并返回博客文章列表', () async {
      // 准备
      when(mockApiClient.get(
        any,
        queryParameters: anyNamed('queryParameters'),
      )).thenAnswer((_) async => testBlogPostList);

      // 执行
      final result = await dataSource.getBlogPosts(
        categoryId: 'cat1',
        authorId: 'author1',
        tag: 'health',
        status: 'published',
        page: 1,
        limit: 10,
      );

      // 验证
      verify(mockApiClient.get(
        '${ApiConstants.laokeServiceBaseUrl}/blog-posts',
        queryParameters: {
          'category_id': 'cat1',
          'author_id': 'author1',
          'tag': 'health',
          'status': 'published',
          'page': 1,
          'limit': 10,
        },
      ));
      expect(result, equals(testBlogPostList));
    });

    test('在服务器异常时应该抛出ServerException', () async {
      // 准备
      when(mockApiClient.get(
        any,
        queryParameters: anyNamed('queryParameters'),
      )).thenThrow(Exception('Server error'));

      // 执行和验证
      expect(
        () => dataSource.getBlogPosts(page: 1, limit: 10),
        throwsA(isA<ServerException>()),
      );
    });
  });

  group('getBlogPostById', () {
    final testBlogPost = {
      'id': '1',
      'title': '中医养生之道',
      'content': '文章内容...',
      'summary': '文章摘要',
      'author_id': 'author1',
      'author_name': '张医生',
      'category_id': 'cat1',
      'category_name': '养生保健',
    };

    test('应该调用API并返回博客文章详情', () async {
      // 准备
      when(mockApiClient.get(any)).thenAnswer((_) async => testBlogPost);

      // 执行
      final result = await dataSource.getBlogPostById('1');

      // 验证
      verify(mockApiClient.get('${ApiConstants.laokeServiceBaseUrl}/blog-posts/1'));
      expect(result, equals(testBlogPost));
    });

    test('在服务器异常时应该抛出ServerException', () async {
      // 准备
      when(mockApiClient.get(any)).thenThrow(Exception('Server error'));

      // 执行和验证
      expect(
        () => dataSource.getBlogPostById('1'),
        throwsA(isA<ServerException>()),
      );
    });
  });
} 