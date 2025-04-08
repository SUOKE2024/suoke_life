import 'package:dartz/dartz.dart';
import 'package:equatable/equatable.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/core/usecases/usecase.dart';
import 'package:suoke_life/domain/repositories/laoke_repository.dart';

/// 获取培训课程列表用例
class GetTrainingCourses implements UseCase<Map<String, dynamic>, TrainingCoursesParams> {
  final LaokeRepository repository;

  GetTrainingCourses(this.repository);

  @override
  Future<Either<Failure, Map<String, dynamic>>> call(TrainingCoursesParams params) {
    return repository.getTrainingCourses(
      categoryId: params.categoryId,
      level: params.level,
      page: params.page,
      limit: params.limit,
    );
  }
}

/// 获取培训课程列表参数
class TrainingCoursesParams extends Equatable {
  final String? categoryId;
  final String? level;
  final int page;
  final int limit;

  const TrainingCoursesParams({
    this.categoryId,
    this.level,
    this.page = 1,
    this.limit = 10,
  });

  @override
  List<Object?> get props => [categoryId, level, page, limit];
} 