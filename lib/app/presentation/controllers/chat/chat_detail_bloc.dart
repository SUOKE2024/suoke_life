import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:injectable/injectable.dart';
import '../../../data/models/chat_message.dart';
import '../../../services/features/chat/chat_service.dart';

// Events
abstract class ChatDetailEvent {
  const ChatDetailEvent();
}

class LoadMessages extends ChatDetailEvent {
  const LoadMessages();
}

class SendMessage extends ChatDetailEvent {
  final String content;
  const SendMessage(this.content);
}

// State
class ChatDetailState {
  final List<ChatMessage> messages;
  final bool isLoading;
  final String? error;

  const ChatDetailState({
    this.messages = const [],
    this.isLoading = false,
    this.error,
  });

  ChatDetailState copyWith({
    List<ChatMessage>? messages,
    bool? isLoading,
    String? error,
  }) {
    return ChatDetailState(
      messages: messages ?? this.messages,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

@injectable
class ChatDetailBloc extends Bloc<ChatDetailEvent, ChatDetailState> {
  final ChatService _chatService;

  ChatDetailBloc(this._chatService) : super(const ChatDetailState()) {
    on<LoadMessages>(_onLoadMessages);
    on<SendMessage>(_onSendMessage);
  }

  Future<void> _onLoadMessages(
    LoadMessages event,
    Emitter<ChatDetailState> emit,
  ) async {
    try {
      emit(state.copyWith(isLoading: true));
      final messages = await _chatService.getMessages();
      emit(state.copyWith(
        messages: messages,
        isLoading: false,
      ));
    } catch (e) {
      emit(state.copyWith(
        error: e.toString(),
        isLoading: false,
      ));
    }
  }

  Future<void> _onSendMessage(
    SendMessage event,
    Emitter<ChatDetailState> emit,
  ) async {
    try {
      await _chatService.sendMessage(event.content);
      add(const LoadMessages());
    } catch (e) {
      emit(state.copyWith(error: e.toString()));
    }
  }
} 