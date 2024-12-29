import 'package:mockito/mockito.dart';
import 'package:suoke_app/app/services/features/chat/chat_service.dart';
import 'package:suoke_app/app/data/models/chat_message.dart';

class MockChatService extends Mock implements ChatService {
  final List<ChatMessage> messages = [];

  @override
  Future<List<ChatMessage>> getMessages(String roomId) async {
    return messages.where((m) => m.roomId == roomId).toList();
  }

  @override
  Future<void> sendMessage(String roomId, String content, String type) async {
    messages.add(ChatMessage(
      id: DateTime.now().toString(),
      roomId: roomId,
      content: content,
      type: type,
      senderId: ChatMessage.userSenderId,
      timestamp: DateTime.now(),
    ));
  }
} 