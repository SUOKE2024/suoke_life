import 'package:dartz/dartz.dart';
import 'package:equatable/equatable.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/core/usecases/usecase.dart';
import 'package:suoke_life/data/models/session_model.dart';
import 'package:suoke_life/domain/repositories/agent_repository.dart';

/// 流式响应用例
class StreamFromAgentUseCase implements StreamUseCase<MessageModel, StreamMessageParams> {
  final AgentRepository repository;

  StreamFromAgentUseCase(this.repository);

  @override
  Stream<Either<Failure, MessageModel>> call(StreamMessageParams params) {
    return repository.streamFromAgent(
      params.agentId,
      params.message,
      sessionId: params.sessionId,
    );
  }
}

/// 流式消息参数
class StreamMessageParams extends Equatable {
  final String agentId;
  final String message;
  final String? sessionId;

  const StreamMessageParams({
    required this.agentId,
    required this.message,
    this.sessionId,
  });

  @override
  List<Object?> get props => [agentId, message, sessionId];
}