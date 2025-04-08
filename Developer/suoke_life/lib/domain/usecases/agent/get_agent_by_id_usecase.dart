import 'package:dartz/dartz.dart';
import 'package:equatable/equatable.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/core/usecases/usecase.dart';
import 'package:suoke_life/data/models/agent_model.dart';
import 'package:suoke_life/domain/repositories/agent_repository.dart';

/// 获取指定智能体用例
class GetAgentByIdUseCase implements UseCase<AgentModel, AgentParams> {
  final AgentRepository repository;

  GetAgentByIdUseCase(this.repository);

  @override
  Future<Either<Failure, AgentModel>> call(AgentParams params) {
    return repository.getAgentById(params.agentId);
  }
}

/// 智能体参数
class AgentParams extends Equatable {
  final String agentId;

  const AgentParams({required this.agentId});

  @override
  List<Object> get props => [agentId];
}