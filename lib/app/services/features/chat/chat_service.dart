import '../../../data/models/chat_message.dart';

abstract class ChatService {
  Future<List<ChatMessage>> getMessages(String roomId);
  Future<void> sendMessage(String roomId, String content, String type);
} 