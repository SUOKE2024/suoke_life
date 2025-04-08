import 'package:dartz/dartz.dart';
import 'package:equatable/equatable.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/core/usecases/usecase.dart';
import 'package:suoke_life/data/models/knowledge_model.dart';
import 'package:suoke_life/domain/repositories/knowledge_repository.dart';

/// 获取指定知识节点用例
class GetNodeByIdUseCase implements UseCase<KnowledgeNodeModel, NodeParams> {
  final KnowledgeRepository repository;

  GetNodeByIdUseCase(this.repository);

  @override
  Future<Either<Failure, KnowledgeNodeModel>> call(NodeParams params) {
    return repository.getNodeById(params.nodeId);
  }
}

/// 知识节点参数
class NodeParams extends Equatable {
  final String nodeId;

  const NodeParams({required this.nodeId});

  @override
  List<Object> get props => [nodeId];
}