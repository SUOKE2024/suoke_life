import 'package:dartz/dartz.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mockito/mockito.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/di/providers/explore_providers.dart';
import 'package:suoke_life/domain/usecases/laoke/get_training_courses.dart';
import 'package:suoke_life/domain/usecases/laoke/get_blog_posts.dart';

class MockGetTrainingCourses extends Mock implements GetTrainingCourses {}
class MockGetBlogPosts extends Mock implements GetBlogPosts {}

void main() {
  group('TrainingCoursesNotifier', () {
    late TrainingCoursesNotifier notifier;
    late MockGetTrainingCourses mockGetTrainingCourses;

    final testCoursesResponse = {
      'items': [
        {'id': '1', 'title': '测试课程'}
      ],
      'total': 1,
      'page': 1,
      'total_pages': 1,
    };

    setUp(() {
      mockGetTrainingCourses = MockGetTrainingCourses();
      notifier = TrainingCoursesNotifier(
        getTrainingCourses: mockGetTrainingCourses,
      );
    });

    test('初始状态应该是加载中', () {
      expect(notifier.state.isLoading, true);
      expect(notifier.state.courses, isEmpty);
    });

    test('fetchCourses成功时应该更新状态', () async {
      // 准备
      when(mockGetTrainingCourses.call(anyNamed('params')))
          .thenAnswer((_) async => Right(testCoursesResponse));

      // 执行
      await notifier.fetchCourses(categoryId: 'cat1', level: '初级');

      // 验证
      expect(notifier.state.isLoading, false);
      expect(notifier.state.courses, equals(testCoursesResponse['items']));
      expect(notifier.state.totalCount, equals(testCoursesResponse['total']));
      expect(notifier.state.currentPage, equals(testCoursesResponse['page']));
      expect(notifier.state.totalPages, equals(testCoursesResponse['total_pages']));
      expect(notifier.state.errorMessage, isNull);
    });

    test('fetchCourses失败时应该设置错误信息', () async {
      // 准备
      when(mockGetTrainingCourses.call(anyNamed('params')))
          .thenAnswer((_) async => Left(ServerFailure(message: '服务器错误')));

      // 执行
      await notifier.fetchCourses();

      // 验证
      expect(notifier.state.isLoading, false);
      expect(notifier.state.courses, isEmpty);
      expect(notifier.state.errorMessage, equals('服务器错误'));
    });
  });

  group('BlogPostsNotifier', () {
    late BlogPostsNotifier notifier;
    late MockGetBlogPosts mockGetBlogPosts;

    final testPostsResponse = {
      'items': [
        {'id': '1', 'title': '测试文章'}
      ],
      'total': 1,
      'page': 1,
      'total_pages': 1,
    };

    setUp(() {
      mockGetBlogPosts = MockGetBlogPosts();
      notifier = BlogPostsNotifier(
        getBlogPosts: mockGetBlogPosts,
      );
    });

    test('初始状态应该是加载中', () {
      expect(notifier.state.isLoading, true);
      expect(notifier.state.posts, isEmpty);
    });

    test('fetchPosts成功时应该更新状态', () async {
      // 准备
      when(mockGetBlogPosts.call(anyNamed('params')))
          .thenAnswer((_) async => Right(testPostsResponse));

      // 执行
      await notifier.fetchPosts(categoryId: 'cat1', tag: 'health');

      // 验证
      expect(notifier.state.isLoading, false);
      expect(notifier.state.posts, equals(testPostsResponse['items']));
      expect(notifier.state.totalCount, equals(testPostsResponse['total']));
      expect(notifier.state.currentPage, equals(testPostsResponse['page']));
      expect(notifier.state.totalPages, equals(testPostsResponse['total_pages']));
      expect(notifier.state.errorMessage, isNull);
    });

    test('fetchPosts失败时应该设置错误信息', () async {
      // 准备
      when(mockGetBlogPosts.call(anyNamed('params')))
          .thenAnswer((_) async => Left(ServerFailure(message: '服务器错误')));

      // 执行
      await notifier.fetchPosts();

      // 验证
      expect(notifier.state.isLoading, false);
      expect(notifier.state.posts, isEmpty);
      expect(notifier.state.errorMessage, equals('服务器错误'));
    });
  });
} 