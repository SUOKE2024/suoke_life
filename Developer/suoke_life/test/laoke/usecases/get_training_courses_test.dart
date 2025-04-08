import 'package:dartz/dartz.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:suoke_life/domain/usecases/laoke/get_training_courses.dart';

import '../../mocks/laoke_mocks.mocks.dart';

void main() {
  late GetTrainingCourses usecase;
  late MockLaokeRepository mockRepository;

  setUp(() {
    mockRepository = MockLaokeRepository();
    usecase = GetTrainingCourses(mockRepository);
  });

  final testParams = TrainingCoursesParams(
    categoryId: 'cat1',
    level: '初级',
    page: 1,
    limit: 10,
  );

  final testResponse = {
    'items': [
      {'id': '1', 'title': '中医基础理论'},
    ],
    'total': 1,
    'page': 1,
    'total_pages': 1,
  };

  test('应该从仓库中获取培训课程列表', () async {
    // 准备
    when(mockRepository.getTrainingCourses(
      categoryId: anyNamed('categoryId'),
      level: anyNamed('level'),
      page: anyNamed('page'),
      limit: anyNamed('limit'),
    )).thenAnswer((_) async => Right(testResponse));

    // 执行
    final result = await usecase(testParams);

    // 验证
    expect(result, equals(Right(testResponse)));
    verify(mockRepository.getTrainingCourses(
      categoryId: testParams.categoryId,
      level: testParams.level,
      page: testParams.page,
      limit: testParams.limit,
    ));
    verifyNoMoreInteractions(mockRepository);
  });
} 