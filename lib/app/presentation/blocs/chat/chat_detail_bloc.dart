import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../domain/repositories/chat_repository.dart';
import 'chat_detail_event.dart';
import 'chat_detail_state.dart';

class ChatDetailBloc extends Bloc<ChatDetailEvent, ChatDetailState> {
  final ChatRepository _chatRepository;
  final String chatId;

  ChatDetailBloc({
    required ChatRepository chatRepository,
    required this.chatId,
  }) : _chatRepository = chatRepository,
       super(ChatDetailInitial()) {
    on<LoadChatDetailEvent>(_onLoadChatDetail);
  }

  Future<void> _onLoadChatDetail(LoadChatDetailEvent event, Emitter<ChatDetailState> emit) async {
    emit(const ChatDetailLoading());
    try {
      final chatInfo = await _chatRepository.getChatInfo(event.chatId);
      final messages = await _chatRepository.getChatMessages(event.chatId);
      emit(ChatDetailLoaded(chatInfo: chatInfo, messages: messages));
    } catch (e) {
      emit(ChatDetailError(message: e.toString()));
    }
  }
} 