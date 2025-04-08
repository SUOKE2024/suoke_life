import 'package:dartz/dartz.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:suoke_life/domain/usecases/laoke/get_blog_posts.dart';

import '../../mocks/laoke_mocks.mocks.dart';

void main() {
  late GetBlogPosts usecase;
  late MockLaokeRepository mockRepository;

  setUp(() {
    mockRepository = MockLaokeRepository();
    usecase = GetBlogPosts(mockRepository);
  });

  final testParams = BlogPostsParams(
    authorId: 'author1',
    categoryId: 'cat1',
    tag: 'health',
    status: 'published',
    page: 1,
    limit: 10,
  );

  final testResponse = {
    'items': [
      {'id': '1', 'title': '中医养生之道'},
    ],
    'total': 1,
    'page': 1,
    'total_pages': 1,
  };

  test('应该从仓库中获取博客文章列表', () async {
    // 准备
    when(mockRepository.getBlogPosts(
      authorId: anyNamed('authorId'),
      categoryId: anyNamed('categoryId'),
      tag: anyNamed('tag'),
      status: anyNamed('status'),
      page: anyNamed('page'),
      limit: anyNamed('limit'),
    )).thenAnswer((_) async => Right(testResponse));

    // 执行
    final result = await usecase(testParams);

    // 验证
    expect(result, equals(Right(testResponse)));
    verify(mockRepository.getBlogPosts(
      authorId: testParams.authorId,
      categoryId: testParams.categoryId,
      tag: testParams.tag,
      status: testParams.status,
      page: testParams.page,
      limit: testParams.limit,
    ));
    verifyNoMoreInteractions(mockRepository);
  });
} 