import 'package:suoke_life/core/models/chat_message.dart';
import 'package:suoke_life/core/services/chat_service.dart';
import 'package:suoke_life/core/services/infrastructure/local_storage_service.dart';

class ChatServiceImpl implements ChatService {
  final LocalStorageService _localStorageService;

  ChatServiceImpl(this._localStorageService);

  @override
  Future<List<ChatMessage>> getChatHistory() async {
    final chatListString = await _localStorageService.getChatHistory();
    return chatListString.map((e) => ChatMessage.fromString(e)).toList();
  }

  @override
  Future<void> saveMessage(String message, bool isUser) async {
    List<String> chatHistory = await _localStorageService.getChatHistory();
    chatHistory.add(message);
    await _localStorageService.saveChatHistory(chatHistory);
  }

  @override
  Future<void> clearChatHistory() async {
    await _localStorageService.clearChatHistory();
  }

  @override
  Future<void> saveChatMessage(ChatMessage message) async {
    await _localStorageService.saveChat(message.text, message.isUser);
  }
} 