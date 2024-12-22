import 'package:get/get.dart';
import 'package:sqflite/sqflite.dart';
import '../data/models/chat_message.dart';
import '../data/models/chat_conversation.dart';
import '../data/database/database_helper.dart';
import 'doubao_service.dart';

class ChatService extends GetxService {
  final DatabaseHelper _db = DatabaseHelper();
  final DouBaoService _douBaoService = Get.find();
  final conversations = <ChatConversation>[].obs;
  final messages = <ChatMessage>[].obs;

  ChatService() {
    print('ChatService initialized');
  }

  Future<List<ChatMessage>> getMessages(int conversationId) async {
    final db = await _db.database;
    final List<Map<String, dynamic>> maps = await db.query(
      'messages',
      where: 'conversation_id = ?',
      whereArgs: [conversationId],
      orderBy: 'created_at DESC',
    );
    return List.generate(maps.length, (i) => ChatMessage.fromJson(maps[i]));
  }

  Future<String> sendMessage(String message, String assistantType) async {
    try {
      final response = await _douBaoService.chatWithAssistant(message, assistantType);
      
      final newMessage = ChatMessage(
        id: DateTime.now().toString(),
        conversationId: 1,
        content: message,
        type: ChatMessage.typeText,
        senderId: ChatMessage.senderUser,
        senderAvatar: 'assets/images/default_avatar.png',
        createdAt: DateTime.now(),
        isRead: true,
      );
      
      await _saveMessage(newMessage);
      messages.add(newMessage);
      
      return response;
    } catch (e) {
      print('Error in ChatService.sendMessage: $e');
      return '发送失败';
    }
  }

  Future<void> _saveMessage(ChatMessage message) async {
    final db = await _db.database;
    await db.insert(
      'messages',
      message.toJson(),
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<String> getAiResponse(String message, String model) async {
    return await _douBaoService.sendMessage(message, model);
  }

  Future<void> markMessageAsRead(String messageId) async {
    final db = await _db.database;
    await db.update(
      'messages',
      {'is_read': 1},
      where: 'id = ?',
      whereArgs: [messageId],
    );
  }

  Future<void> deleteMessage(String messageId) async {
    final db = await _db.database;
    await db.delete(
      'messages',
      where: 'id = ?',
      whereArgs: [messageId],
    );
  }

  Future<List<ChatConversation>> getConversations() async {
    final db = await _db.database;
    final List<Map<String, dynamic>> maps = await db.query(
      'conversations',
      orderBy: 'updated_at DESC',
    );
    return List.generate(maps.length, (i) => ChatConversation.fromJson(maps[i]));
  }

  Future<ChatConversation> createConversation({
    required String title,
    required String model,
    required String avatar,
  }) async {
    final db = await _db.database;
    final conversation = ChatConversation(
      id: DateTime.now().millisecondsSinceEpoch,
      title: title,
      model: model,
      avatar: avatar,
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    );

    await db.insert(
      'conversations',
      conversation.toJson(),
      conflictAlgorithm: ConflictAlgorithm.replace,
    );

    return conversation;
  }

  Future<void> updateConversation(ChatConversation conversation) async {
    final db = await _db.database;
    await db.update(
      'conversations',
      conversation.toJson(),
      where: 'id = ?',
      whereArgs: [conversation.id],
    );
  }

  Future<void> deleteConversation(int conversationId) async {
    final db = await _db.database;
    await db.delete(
      'conversations',
      where: 'id = ?',
      whereArgs: [conversationId],
    );
    await db.delete(
      'messages',
      where: 'conversation_id = ?',
      whereArgs: [conversationId],
    );
  }
} 