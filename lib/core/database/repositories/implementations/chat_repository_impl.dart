// import 'package:injectable/injectable.dart';
// @Injectable(as: ChatRepository)
import 'package:suoke_app/app/domain/models/chat_message.dart';
import 'package:suoke_app/app/domain/models/chat_info.dart';
import 'package:suoke_app/app/domain/repositories/chat_repository.dart';
import 'package:suoke_app/app/core/network/network_service.dart';
import 'package:suoke_app/app/data/providers/database_provider.dart';
import 'package:sqflite/sqflite.dart' show ConflictAlgorithm;

class ChatRepositoryImpl implements ChatRepository {
  final DatabaseProvider _db;
  final NetworkService _network;

  ChatRepositoryImpl(this._db, this._network);

  @override
  Future<List<ChatInfo>> getChats() async {
    try {
      // 先从网络获取最新数据
      final response = await _network.get('/chats');
      final chats = (response.data as List)
          .map((json) => ChatInfo.fromJson(json))
          .toList();
      
      // 更新本地数据库
      await _db.transaction((txn) async {
        for (var chat in chats) {
          await txn.insert(
            'chats',
            chat.toJson(),
            conflictAlgorithm: ConflictAlgorithm.replace,
          );
        }
      });
      
      return chats;
    } catch (e) {
      // 如果网络请求失败，从本地数据库获取
      final result = await _db.query('chats');
      return result.map((row) => ChatInfo.fromJson(row)).toList();
    }
  }

  @override
  Future<List<ChatInfo>> searchChats(String query) async {
    final results = await _db.query(
      'chats',
      where: 'title LIKE ? OR last_message LIKE ?',
      whereArgs: ['%$query%', '%$query%'],
    );
    return results.map((row) => ChatInfo.fromJson(row)).toList();
  }

  @override
  Future<List<ChatMessage>> getChatMessages(String chatId) async {
    try {
      // 先从网络获取最新消息
      final response = await _network.get('/chats/$chatId/messages');
      final messages = (response.data as List)
          .map((json) => ChatMessage.fromJson(json))
          .toList();
      
      // 更新本地数据库
      await _db.transaction((txn) async {
        for (var message in messages) {
          await txn.insert(
            'messages',
            message.toJson(),
            conflictAlgorithm: ConflictAlgorithm.replace,
          );
        }
      });
      
      return messages;
    } catch (e) {
      // 如果网络请求失败，从本地获取
      final results = await _db.query(
        'messages',
        where: 'chat_id = ?',
        whereArgs: [chatId],
        orderBy: 'timestamp DESC',
        limit: 50,
      );
      return results.map((row) => ChatMessage.fromJson(row)).toList();
    }
  }

  @override
  Future<ChatMessage> sendMessage(String content) async {
    // 创建消息对象
    final message = ChatMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: content,
      senderId: 'user',  // 或从用户服务获取
      timestamp: DateTime.now(),
    );

    // 先保存到本地
    await _db.insert('messages', message.toJson());

    try {
      // 发送到服务器
      final response = await _network.post('/messages', data: message.toJson());
      final serverMessage = ChatMessage.fromJson(response.data);
      
      // 更新本地消息ID（使用服务器返回的ID）
      await _db.update(
        'messages',
        {'id': serverMessage.id},
        where: 'id = ?',
        whereArgs: [message.id],
      );
      
      return serverMessage;
    } catch (e) {
      // 如果网络请求失败，返回本地消息
      // 后续可以通过同步服务处理失败的消息
      return message;
    }
  }

  // 辅助方法：获取未同步的消息
  Future<List<ChatMessage>> _getUnsyncedMessages() async {
    final results = await _db.query(
      'messages',
      where: 'synced = ?',
      whereArgs: [0],
    );
    return results.map((row) => ChatMessage.fromJson(row)).toList();
  }

  // 同步本地消息到服务器
  Future<void> syncMessages() async {
    final unsynced = await _getUnsyncedMessages();
    for (var message in unsynced) {
      try {
        await _network.post('/messages', data: message.toJson());
        await _db.update(
          'messages',
          {'synced': 1},
          where: 'id = ?',
          whereArgs: [message.id],
        );
      } catch (e) {
        // 记录同步失败，稍后重试
        print('Failed to sync message: ${message.id}');
      }
    }
  }
} 