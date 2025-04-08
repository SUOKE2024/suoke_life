import 'package:dartz/dartz.dart';
import 'package:equatable/equatable.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/core/usecases/usecase.dart';
import 'package:suoke_life/data/models/session_model.dart';
import 'package:suoke_life/domain/repositories/agent_repository.dart';

/// 获取会话消息历史用例
class GetSessionMessagesUseCase implements UseCase<List<MessageModel>, SessionParams> {
  final AgentRepository repository;

  GetSessionMessagesUseCase(this.repository);

  @override
  Future<Either<Failure, List<MessageModel>>> call(SessionParams params) {
    return repository.getSessionMessages(params.sessionId);
  }
}

/// 会话参数
class SessionParams extends Equatable {
  final String sessionId;

  const SessionParams({required this.sessionId});

  @override
  List<Object> get props => [sessionId];
}