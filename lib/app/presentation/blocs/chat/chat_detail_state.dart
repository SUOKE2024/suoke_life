import 'package:equatable/equatable.dart';
import '../../../domain/models/chat_info.dart';
import '../../../domain/models/chat_message.dart';

abstract class ChatDetailState extends Equatable {
  const ChatDetailState();

  @override
  List<Object?> get props => [];
}

class ChatDetailInitial extends ChatDetailState {}

class ChatDetailLoading extends ChatDetailState {
  const ChatDetailLoading();
}

class ChatDetailLoaded extends ChatDetailState {
  final ChatInfo chatInfo;
  final List<ChatMessage> messages;

  const ChatDetailLoaded({
    required this.chatInfo,
    required this.messages,
  });

  @override
  List<Object?> get props => [chatInfo, messages];
}

class ChatDetailError extends ChatDetailState {
  final String message;

  const ChatDetailError({required this.message});

  @override
  List<Object?> get props => [message];
} 