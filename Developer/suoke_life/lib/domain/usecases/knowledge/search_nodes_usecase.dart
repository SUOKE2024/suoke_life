import 'package:dartz/dartz.dart';
import 'package:equatable/equatable.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/core/usecases/usecase.dart';
import 'package:suoke_life/data/models/knowledge_model.dart';
import 'package:suoke_life/domain/repositories/knowledge_repository.dart';

/// 搜索知识节点用例
class SearchNodesUseCase implements UseCase<List<KnowledgeNodeModel>, SearchParams> {
  final KnowledgeRepository repository;

  SearchNodesUseCase(this.repository);

  @override
  Future<Either<Failure, List<KnowledgeNodeModel>>> call(SearchParams params) {
    return repository.searchNodes(params.query);
  }
}

/// 搜索参数
class SearchParams extends Equatable {
  final String query;

  const SearchParams({required this.query});

  @override
  List<Object> get props => [query];
}