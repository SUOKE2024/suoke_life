import 'package:equatable/equatable.dart';

abstract class ChatDetailEvent extends Equatable {
  const ChatDetailEvent();

  @override
  List<Object?> get props => [];
}

class LoadChatDetailEvent extends ChatDetailEvent {
  final String chatId;
  const LoadChatDetailEvent(this.chatId);

  @override
  List<Object?> get props => [chatId];
} 