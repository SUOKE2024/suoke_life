import 'package:suoke_life/lib/core/models/chat_message.dart';

abstract class ChatService {
  Future<List<ChatMessage>> getChatHistory();
  Future<void> saveChatMessage(ChatMessage message);
} 