import 'package:dartz/dartz.dart';
import 'package:equatable/equatable.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/core/usecases/usecase.dart';
import 'package:suoke_life/data/models/session_model.dart';
import 'package:suoke_life/domain/repositories/agent_repository.dart';

/// 创建会话用例
class CreateSessionUseCase implements UseCase<SessionModel, CreateSessionParams> {
  final AgentRepository repository;

  CreateSessionUseCase(this.repository);

  @override
  Future<Either<Failure, SessionModel>> call(CreateSessionParams params) {
    return repository.createSession(params.agentId, params.title);
  }
}

/// 创建会话参数
class CreateSessionParams extends Equatable {
  final String agentId;
  final String title;

  const CreateSessionParams({
    required this.agentId,
    required this.title,
  });

  @override
  List<Object> get props => [agentId, title];
}