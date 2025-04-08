import 'package:dartz/dartz.dart';
import 'package:equatable/equatable.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/core/usecases/usecase.dart';
import 'package:suoke_life/domain/repositories/laoke_repository.dart';

/// 获取培训课程详情用例
class GetTrainingCourseById implements UseCase<Map<String, dynamic>, TrainingCourseParams> {
  final LaokeRepository repository;

  GetTrainingCourseById(this.repository);

  @override
  Future<Either<Failure, Map<String, dynamic>>> call(TrainingCourseParams params) {
    return repository.getTrainingCourseById(params.id);
  }
}

/// 获取培训课程详情参数
class TrainingCourseParams extends Equatable {
  final String id;

  const TrainingCourseParams({required this.id});

  @override
  List<Object> get props => [id];
} 