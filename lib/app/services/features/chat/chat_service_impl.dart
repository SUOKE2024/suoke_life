import 'package:get/get.dart';
import '../../../data/helpers/database_helper.dart';
import '../../../data/models/chat_message.dart';
import 'chat_service.dart';

class ChatServiceImpl implements ChatService {
  final DatabaseHelper _db;

  ChatServiceImpl(this._db);

  @override
  Future<List<ChatMessage>> getMessages(String roomId) async {
    final results = await _db.query(
      'messages',
      where: 'room_id = ?',
      whereArgs: [roomId],
      orderBy: 'timestamp DESC',
    );
    return results.map((e) => ChatMessage.fromMap(e)).toList();
  }

  @override
  Future<void> sendMessage(String roomId, String content, String type) async {
    await _db.insert('messages', {
      'id': DateTime.now().toString(),
      'room_id': roomId,
      'content': content,
      'type': type,
      'sender_id': ChatMessage.userSenderId,
      'timestamp': DateTime.now().millisecondsSinceEpoch,
    });
  }
} 