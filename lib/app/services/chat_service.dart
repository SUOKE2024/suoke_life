import 'dart:convert';
import 'package:get/get.dart';
import '../core/database/database_helper.dart';
import '../data/models/ai_chat.dart';

class ChatService extends GetxService {
  final _db = DatabaseHelper.instance;

  Future<void> saveChat(AiChat chat) async {
    await _db.insert('ai_chats', chat.toMap());
  }

  Future<List<AiChat>> getChats() async {
    final maps = await _db.getAll('ai_chats');
    return maps.map((map) => AiChat.fromMap(map)).toList();
  }

  Future<void> deleteChat(String id) async {
    await _db.delete('ai_chats', id);
  }
} 