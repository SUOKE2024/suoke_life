import 'package:dartz/dartz.dart';
import 'package:equatable/equatable.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/core/usecases/usecase.dart';
import 'package:suoke_life/domain/repositories/laoke_repository.dart';

/// 获取知识文章列表用例
class GetKnowledgeArticles implements UseCase<Map<String, dynamic>, KnowledgeArticlesParams> {
  final LaokeRepository repository;

  GetKnowledgeArticles(this.repository);

  @override
  Future<Either<Failure, Map<String, dynamic>>> call(KnowledgeArticlesParams params) {
    return repository.getKnowledgeArticles(
      categoryId: params.categoryId,
      page: params.page,
      limit: params.limit,
    );
  }
}

/// 获取知识文章列表参数
class KnowledgeArticlesParams extends Equatable {
  final String? categoryId;
  final int page;
  final int limit;

  const KnowledgeArticlesParams({
    this.categoryId,
    this.page = 1,
    this.limit = 10,
  });

  @override
  List<Object?> get props => [categoryId, page, limit];
} 