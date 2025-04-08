import 'package:dartz/dartz.dart';
import 'package:equatable/equatable.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/core/usecases/usecase.dart';
import 'package:suoke_life/domain/entities/laoke/knowledge_article.dart';
import 'package:suoke_life/domain/repositories/laoke_repository.dart';

/// 获取知识文章详情用例
class GetKnowledgeArticleById implements UseCase<KnowledgeArticle, KnowledgeArticleParams> {
  final LaokeRepository repository;

  GetKnowledgeArticleById(this.repository);

  @override
  Future<Either<Failure, KnowledgeArticle>> call(KnowledgeArticleParams params) {
    return repository.getKnowledgeArticleById(params.id);
  }
}

/// 获取知识文章详情参数
class KnowledgeArticleParams extends Equatable {
  final String id;

  const KnowledgeArticleParams({required this.id});

  @override
  List<Object> get props => [id];
} 