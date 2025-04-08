import 'package:dartz/dartz.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:suoke_life/core/error/exceptions.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/core/network/network_info.dart';
import 'package:suoke_life/data/datasources/remote/laoke_remote_datasource.dart';
import 'package:suoke_life/data/repositories/laoke_repository_impl.dart';

import '../../mocks/laoke_mocks.mocks.dart';

void main() {
  late LaokeRepositoryImpl repository;
  late MockLaokeRemoteDataSource mockRemoteDataSource;
  late MockNetworkInfo mockNetworkInfo;

  setUp(() {
    mockRemoteDataSource = MockLaokeRemoteDataSource();
    mockNetworkInfo = MockNetworkInfo();
    repository = LaokeRepositoryImpl(
      remoteDataSource: mockRemoteDataSource,
      networkInfo: mockNetworkInfo,
    );
  });

  void runTestsOnline(Function body) {
    group('设备在线', () {
      setUp(() {
        when(mockNetworkInfo.isConnected).thenAnswer((_) async => true);
      });

      body();
    });
  }

  void runTestsOffline(Function body) {
    group('设备离线', () {
      setUp(() {
        when(mockNetworkInfo.isConnected).thenAnswer((_) async => false);
      });

      body();
    });
  }

  group('getTrainingCourses', () {
    final testTrainingCoursesResponse = {
      'items': [],
      'total': 0,
      'page': 1,
      'total_pages': 1,
    };

    runTestsOnline(() {
      test('当设备在线时，应该从远程数据源获取数据', () async {
        // 准备
        when(mockRemoteDataSource.getTrainingCourses(
          categoryId: anyNamed('categoryId'),
          level: anyNamed('level'),
          page: anyNamed('page'),
          limit: anyNamed('limit'),
        )).thenAnswer((_) async => testTrainingCoursesResponse);

        // 执行
        final result = await repository.getTrainingCourses(
          categoryId: 'cat1',
          level: '初级',
          page: 1,
          limit: 10,
        );

        // 验证
        verify(mockRemoteDataSource.getTrainingCourses(
          categoryId: 'cat1',
          level: '初级',
          page: 1,
          limit: 10,
        ));
        expect(result, equals(Right(testTrainingCoursesResponse)));
      });

      test('当远程数据源抛出ServerException时，应该返回ServerFailure', () async {
        // 准备
        when(mockRemoteDataSource.getTrainingCourses(
          categoryId: anyNamed('categoryId'),
          level: anyNamed('level'),
          page: anyNamed('page'),
          limit: anyNamed('limit'),
        )).thenThrow(ServerException(message: '获取培训课程失败', statusCode: 500));

        // 执行
        final result = await repository.getTrainingCourses(
          page: 1,
          limit: 10,
        );

        // 验证
        verify(mockRemoteDataSource.getTrainingCourses(
          page: 1,
          limit: 10,
        ));
        expect(result, equals(Left(ServerFailure(message: '获取培训课程失败'))));
      });
    });

    runTestsOffline(() {
      test('当设备离线时，应该返回NetworkFailure', () async {
        // 执行
        final result = await repository.getTrainingCourses(
          page: 1,
          limit: 10,
        );

        // 验证
        verifyZeroInteractions(mockRemoteDataSource);
        expect(result, equals(Left(NetworkFailure(message: '网络连接不可用'))));
      });
    });
  });

  group('getTrainingCourseById', () {
    final testTrainingCourseResponse = {
      'id': '1',
      'title': '测试课程',
    };

    runTestsOnline(() {
      test('当设备在线时，应该从远程数据源获取数据', () async {
        // 准备
        when(mockRemoteDataSource.getTrainingCourseById(any))
            .thenAnswer((_) async => testTrainingCourseResponse);

        // 执行
        final result = await repository.getTrainingCourseById('1');

        // 验证
        verify(mockRemoteDataSource.getTrainingCourseById('1'));
        expect(result, equals(Right(testTrainingCourseResponse)));
      });

      test('当远程数据源抛出ServerException时，应该返回ServerFailure', () async {
        // 准备
        when(mockRemoteDataSource.getTrainingCourseById(any))
            .thenThrow(ServerException(message: '获取培训课程详情失败', statusCode: 500));

        // 执行
        final result = await repository.getTrainingCourseById('1');

        // 验证
        verify(mockRemoteDataSource.getTrainingCourseById('1'));
        expect(result, equals(Left(ServerFailure(message: '获取培训课程详情失败'))));
      });
    });

    runTestsOffline(() {
      test('当设备离线时，应该返回NetworkFailure', () async {
        // 执行
        final result = await repository.getTrainingCourseById('1');

        // 验证
        verifyZeroInteractions(mockRemoteDataSource);
        expect(result, equals(Left(NetworkFailure(message: '网络连接不可用'))));
      });
    });
  });

  group('getBlogPosts', () {
    final testBlogPostsResponse = {
      'items': [],
      'total': 0,
      'page': 1,
      'total_pages': 1,
    };

    runTestsOnline(() {
      test('当设备在线时，应该从远程数据源获取数据', () async {
        // 准备
        when(mockRemoteDataSource.getBlogPosts(
          authorId: anyNamed('authorId'),
          categoryId: anyNamed('categoryId'),
          tag: anyNamed('tag'),
          status: anyNamed('status'),
          page: anyNamed('page'),
          limit: anyNamed('limit'),
        )).thenAnswer((_) async => testBlogPostsResponse);

        // 执行
        final result = await repository.getBlogPosts(
          authorId: 'author1',
          categoryId: 'cat1',
          tag: 'health',
          status: 'published',
          page: 1,
          limit: 10,
        );

        // 验证
        verify(mockRemoteDataSource.getBlogPosts(
          authorId: 'author1',
          categoryId: 'cat1',
          tag: 'health',
          status: 'published',
          page: 1,
          limit: 10,
        ));
        expect(result, equals(Right(testBlogPostsResponse)));
      });

      test('当远程数据源抛出ServerException时，应该返回ServerFailure', () async {
        // 准备
        when(mockRemoteDataSource.getBlogPosts(
          page: anyNamed('page'),
          limit: anyNamed('limit'),
        )).thenThrow(ServerException(message: '获取博客文章失败', statusCode: 500));

        // 执行
        final result = await repository.getBlogPosts(
          page: 1,
          limit: 10,
        );

        // 验证
        verify(mockRemoteDataSource.getBlogPosts(
          page: 1,
          limit: 10,
        ));
        expect(result, equals(Left(ServerFailure(message: '获取博客文章失败'))));
      });
    });

    runTestsOffline(() {
      test('当设备离线时，应该返回NetworkFailure', () async {
        // 执行
        final result = await repository.getBlogPosts(
          page: 1,
          limit: 10,
        );

        // 验证
        verifyZeroInteractions(mockRemoteDataSource);
        expect(result, equals(Left(NetworkFailure(message: '网络连接不可用'))));
      });
    });
  });

  group('getBlogPostById', () {
    final testBlogPostResponse = {
      'id': '1',
      'title': '测试文章',
    };

    runTestsOnline(() {
      test('当设备在线时，应该从远程数据源获取数据', () async {
        // 准备
        when(mockRemoteDataSource.getBlogPostById(any))
            .thenAnswer((_) async => testBlogPostResponse);

        // 执行
        final result = await repository.getBlogPostById('1');

        // 验证
        verify(mockRemoteDataSource.getBlogPostById('1'));
        expect(result, equals(Right(testBlogPostResponse)));
      });

      test('当远程数据源抛出ServerException时，应该返回ServerFailure', () async {
        // 准备
        when(mockRemoteDataSource.getBlogPostById(any))
            .thenThrow(ServerException(message: '获取博客文章详情失败', statusCode: 500));

        // 执行
        final result = await repository.getBlogPostById('1');

        // 验证
        verify(mockRemoteDataSource.getBlogPostById('1'));
        expect(result, equals(Left(ServerFailure(message: '获取博客文章详情失败'))));
      });
    });

    runTestsOffline(() {
      test('当设备离线时，应该返回NetworkFailure', () async {
        // 执行
        final result = await repository.getBlogPostById('1');

        // 验证
        verifyZeroInteractions(mockRemoteDataSource);
        expect(result, equals(Left(NetworkFailure(message: '网络连接不可用'))));
      });
    });
  });
} 