import 'package:suoke_life/core/models/chat_message.dart';
import 'package:suoke_life/core/services/chat_service.dart';
import 'package:suoke_life/core/services/infrastructure/local_storage_service.dart';

class ChatServiceImpl implements ChatService {
  final LocalStorageService _localStorageService;

  ChatServiceImpl(this._localStorageService);

  @override
  Future<List<ChatMessage>> getChatHistory() async {
    final chatList = await _localStorageService.getChats();
    return chatList.map((e) => ChatMessage.fromJson(e)).toList();
  }

  @override
  Future<void> saveChatMessage(ChatMessage message) async {
    await _localStorageService.saveChat(message.text, message.isUser);
  }
} 