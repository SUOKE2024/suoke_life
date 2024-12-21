import 'package:get/get.dart';
import '../data/models/chat.dart';
import '../data/models/message.dart';
import '../core/network/api_client.dart';
import 'dart:async';

class ChatService extends GetxService {
  final ApiClient _apiClient;
  
  ChatService({required ApiClient apiClient}) : _apiClient = apiClient;

  // 聊天更新流
  final _chatUpdateController = StreamController<Chat>.broadcast();
  Stream<Chat> get onChatUpdated => _chatUpdateController.stream;

  // 新聊天流
  final _newChatController = StreamController<Chat>.broadcast();
  Stream<Chat> get onNewChat => _newChatController.stream;

  // 获取聊天列表
  Future<List<Chat>> getChatList() async {
    try {
      final response = await _apiClient.get('/chats');
      return (response['chats'] as List)
          .map((json) => Chat.fromJson(json))
          .toList();
    } catch (e) {
      rethrow;
    }
  }

  // 获取聊天详情
  Future<Chat> getChat(String chatId) async {
    try {
      final response = await _apiClient.get('/chats/$chatId');
      return Chat.fromJson(response);
    } catch (e) {
      rethrow;
    }
  }

  // 获取��天消息
  Future<List<Message>> getMessages(String chatId, {int? limit, String? before}) async {
    try {
      final response = await _apiClient.get(
        '/chats/$chatId/messages',
        queryParameters: {
          if (limit != null) 'limit': limit,
          if (before != null) 'before': before,
        },
      );
      return (response['messages'] as List)
          .map((json) => Message.fromJson(json))
          .toList();
    } catch (e) {
      rethrow;
    }
  }

  // 发送消息
  Future<Message> sendMessage(String chatId, String content, {String type = 'text'}) async {
    try {
      final response = await _apiClient.post('/chats/$chatId/messages', data: {
        'content': content,
        'type': type,
      });
      return Message.fromJson(response);
    } catch (e) {
      rethrow;
    }
  }

  // 置顶/取消置顶聊天
  Future<void> togglePin(String chatId) async {
    try {
      await _apiClient.post('/chats/$chatId/pin');
    } catch (e) {
      rethrow;
    }
  }

  // 开启/关闭通知
  Future<void> toggleMute(String chatId) async {
    try {
      await _apiClient.post('/chats/$chatId/mute');
    } catch (e) {
      rethrow;
    }
  }

  // 删除聊天
  Future<void> deleteChat(String chatId) async {
    try {
      await _apiClient.delete('/chats/$chatId');
    } catch (e) {
      rethrow;
    }
  }

  // 标记消息已读
  Future<void> markAsRead(String chatId) async {
    try {
      await _apiClient.post('/chats/$chatId/read');
    } catch (e) {
      rethrow;
    }
  }

  @override
  void onClose() {
    _chatUpdateController.close();
    _newChatController.close();
    super.onClose();
  }
} 