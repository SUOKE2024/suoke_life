import 'package:dartz/dartz.dart';
import 'package:equatable/equatable.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/core/usecases/usecase.dart';
import 'package:suoke_life/data/models/knowledge_model.dart';
import 'package:suoke_life/domain/repositories/knowledge_repository.dart';

/// 获取知识节点列表用例
class GetNodesUseCase implements UseCase<List<KnowledgeNodeModel>, NodesParams> {
  final KnowledgeRepository repository;

  GetNodesUseCase(this.repository);

  @override
  Future<Either<Failure, List<KnowledgeNodeModel>>> call(NodesParams params) {
    return repository.getNodes(
      query: params.query,
      tags: params.tags,
      types: params.types,
      page: params.page,
      pageSize: params.pageSize,
    );
  }
}

/// 知识节点列表参数
class NodesParams extends Equatable {
  final String? query;
  final List<String>? tags;
  final List<String>? types;
  final int page;
  final int pageSize;

  const NodesParams({
    this.query,
    this.tags,
    this.types,
    this.page = 1,
    this.pageSize = 20,
  });

  @override
  List<Object?> get props => [query, tags, types, page, pageSize];
}