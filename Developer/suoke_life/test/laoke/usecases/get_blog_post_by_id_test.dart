import 'package:dartz/dartz.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:suoke_life/domain/usecases/laoke/get_blog_post_by_id.dart';

import '../../mocks/laoke_mocks.mocks.dart';

void main() {
  late GetBlogPostById usecase;
  late MockLaokeRepository mockRepository;

  setUp(() {
    mockRepository = MockLaokeRepository();
    usecase = GetBlogPostById(mockRepository);
  });

  final testParams = BlogPostParams(id: '1');
  final testResponse = {
    'id': '1',
    'title': '中医养生之道',
    'content': '详细内容...',
  };

  test('应该从仓库中获取博客文章详情', () async {
    // 准备
    when(mockRepository.getBlogPostById(any))
        .thenAnswer((_) async => Right(testResponse));

    // 执行
    final result = await usecase(testParams);

    // 验证
    expect(result, equals(Right(testResponse)));
    verify(mockRepository.getBlogPostById(testParams.id));
    verifyNoMoreInteractions(mockRepository);
  });
} 