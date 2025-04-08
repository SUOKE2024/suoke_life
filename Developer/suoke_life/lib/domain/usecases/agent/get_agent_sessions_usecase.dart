import 'package:dartz/dartz.dart';
import 'package:equatable/equatable.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/core/usecases/usecase.dart';
import 'package:suoke_life/data/models/session_model.dart';
import 'package:suoke_life/domain/repositories/agent_repository.dart';

/// 获取智能体会话列表用例
class GetAgentSessionsUseCase implements UseCase<List<SessionModel>, AgentSessionsParams> {
  final AgentRepository repository;

  GetAgentSessionsUseCase(this.repository);

  @override
  Future<Either<Failure, List<SessionModel>>> call(AgentSessionsParams params) {
    return repository.getAgentSessions(params.agentId);
  }
}

/// 智能体会话参数
class AgentSessionsParams extends Equatable {
  final String agentId;

  const AgentSessionsParams({required this.agentId});

  @override
  List<Object> get props => [agentId];
}