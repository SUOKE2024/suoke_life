import '../models/chat_message.dart';
import '../models/chat_info.dart';

abstract class ChatRepository {
  Future<List<ChatInfo>> getChats();
  Future<List<ChatInfo>> searchChats(String query);
  Future<List<ChatMessage>> getChatMessages(String chatId);
  Future<ChatMessage> sendMessage(String content);
} 