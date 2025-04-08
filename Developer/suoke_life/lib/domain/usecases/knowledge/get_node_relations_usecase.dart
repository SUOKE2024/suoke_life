import 'package:dartz/dartz.dart';
import 'package:equatable/equatable.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/core/usecases/usecase.dart';
import 'package:suoke_life/data/models/knowledge_model.dart';
import 'package:suoke_life/domain/repositories/knowledge_repository.dart';

/// 获取知识节点关系用例
class GetNodeRelationsUseCase implements UseCase<List<KnowledgeRelationModel>, NodeRelationsParams> {
  final KnowledgeRepository repository;

  GetNodeRelationsUseCase(this.repository);

  @override
  Future<Either<Failure, List<KnowledgeRelationModel>>> call(NodeRelationsParams params) {
    return repository.getNodeRelations(params.nodeId);
  }
}

/// 知识节点关系参数
class NodeRelationsParams extends Equatable {
  final String nodeId;

  const NodeRelationsParams({required this.nodeId});

  @override
  List<Object> get props => [nodeId];
}