import 'package:get/get.dart';
import '../data/models/message.dart';
import '../core/network/api_client.dart';

class MessageService extends GetxService {
  final ApiClient _apiClient;
  
  MessageService({required ApiClient apiClient}) : _apiClient = apiClient;

  // 发送消息
  Future<Message> sendMessage(Message message) async {
    try {
      final response = await _apiClient.post(
        '/messages',
        data: message.toJson(),
      );
      return Message.fromJson(response);
    } catch (e) {
      rethrow;
    }
  }

  // 获取消息列表
  Future<List<Message>> getMessages(String chatId, {
    int? limit,
    String? before,
    String? after,
  }) async {
    try {
      final response = await _apiClient.get(
        '/messages',
        queryParameters: {
          'chatId': chatId,
          if (limit != null) 'limit': limit,
          if (before != null) 'before': before,
          if (after != null) 'after': after,
        },
      );
      return (response['messages'] as List)
          .map((json) => Message.fromJson(json))
          .toList();
    } catch (e) {
      rethrow;
    }
  }

  // 标记消息已读
  Future<void> markAsRead(String messageId) async {
    try {
      await _apiClient.put('/messages/$messageId/read');
    } catch (e) {
      rethrow;
    }
  }

  // 删除消息
  Future<void> deleteMessage(String messageId) async {
    try {
      await _apiClient.delete('/messages/$messageId');
    } catch (e) {
      rethrow;
    }
  }

  // 撤回消息
  Future<void> recallMessage(String messageId) async {
    try {
      await _apiClient.put('/messages/$messageId/recall');
    } catch (e) {
      rethrow;
    }
  }
} 