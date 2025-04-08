import 'package:dartz/dartz.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/core/usecases/usecase.dart';
import 'package:suoke_life/domain/entities/laoke/knowledge_category.dart';
import 'package:suoke_life/domain/repositories/laoke_repository.dart';

/// 获取知识分类用例
class GetKnowledgeCategories implements UseCase<List<KnowledgeCategory>, NoParams> {
  final LaokeRepository repository;

  GetKnowledgeCategories(this.repository);

  @override
  Future<Either<Failure, List<KnowledgeCategory>>> call(NoParams params) {
    return repository.getKnowledgeCategories();
  }
} 