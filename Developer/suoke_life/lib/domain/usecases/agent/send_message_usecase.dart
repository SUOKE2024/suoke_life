import 'package:dartz/dartz.dart';
import 'package:equatable/equatable.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/core/usecases/usecase.dart';
import 'package:suoke_life/data/models/session_model.dart';
import 'package:suoke_life/domain/repositories/agent_repository.dart';

/// 发送消息用例
class SendMessageUseCase implements UseCase<MessageModel, MessageParams> {
  final AgentRepository repository;

  SendMessageUseCase(this.repository);

  @override
  Future<Either<Failure, MessageModel>> call(MessageParams params) {
    return repository.sendMessage(
      params.agentId,
      params.message,
      sessionId: params.sessionId,
    );
  }
}

/// 消息参数
class MessageParams extends Equatable {
  final String agentId;
  final String message;
  final String? sessionId;

  const MessageParams({
    required this.agentId,
    required this.message,
    this.sessionId,
  });

  @override
  List<Object?> get props => [agentId, message, sessionId];
}