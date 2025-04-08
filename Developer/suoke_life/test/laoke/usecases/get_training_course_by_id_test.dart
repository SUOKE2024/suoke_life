import 'package:dartz/dartz.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:suoke_life/domain/usecases/laoke/get_training_course_by_id.dart';

import '../../mocks/laoke_mocks.mocks.dart';

void main() {
  late GetTrainingCourseById usecase;
  late MockLaokeRepository mockRepository;

  setUp(() {
    mockRepository = MockLaokeRepository();
    usecase = GetTrainingCourseById(mockRepository);
  });

  final testParams = TrainingCourseParams(id: '1');
  final testResponse = {
    'id': '1',
    'title': '中医基础理论',
    'content': '详细内容...',
  };

  test('应该从仓库中获取培训课程详情', () async {
    // 准备
    when(mockRepository.getTrainingCourseById(any))
        .thenAnswer((_) async => Right(testResponse));

    // 执行
    final result = await usecase(testParams);

    // 验证
    expect(result, equals(Right(testResponse)));
    verify(mockRepository.getTrainingCourseById(testParams.id));
    verifyNoMoreInteractions(mockRepository);
  });
} 