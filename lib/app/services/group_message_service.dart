import 'package:get/get.dart';
import '../core/network/api_client.dart';
import '../data/models/message.dart';
import 'dart:async';

class GroupMessageService extends GetxService {
  final ApiClient _apiClient;
  
  // 消息更新流
  final _messageController = StreamController<Message>.broadcast();
  Stream<Message> get onMessageReceived => _messageController.stream;

  // 消息状态更新流
  final _messageStatusController = StreamController<Map<String, dynamic>>.broadcast();
  Stream<Map<String, dynamic>> get onMessageStatusChanged => _messageStatusController.stream;

  GroupMessageService({required ApiClient apiClient}) : _apiClient = apiClient;

  // 获取群聊消息
  Future<List<Message>> getMessages(String groupId, {
    int? limit,
    String? before,
    String? after,
  }) async {
    try {
      final response = await _apiClient.get(
        '/groups/$groupId/messages',
        queryParameters: {
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

  // 发送消息
  Future<Message> sendMessage(String groupId, {
    required String content,
    required String type,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final response = await _apiClient.post(
        '/groups/$groupId/messages',
        data: {
          'content': content,
          'type': type,
          if (metadata != null) 'metadata': metadata,
        },
      );
      return Message.fromJson(response);
    } catch (e) {
      rethrow;
    }
  }

  // 撤回消息
  Future<void> recallMessage(String groupId, String messageId) async {
    try {
      await _apiClient.delete('/groups/$groupId/messages/$messageId');
    } catch (e) {
      rethrow;
    }
  }

  // 标记消息已读
  Future<void> markAsRead(String groupId, List<String> messageIds) async {
    try {
      await _apiClient.post('/groups/$groupId/messages/read', data: {
        'messageIds': messageIds,
      });
    } catch (e) {
      rethrow;
    }
  }

  // 搜索消息
  Future<List<Message>> searchMessages(String groupId, String keyword) async {
    try {
      final response = await _apiClient.get(
        '/groups/$groupId/messages/search',
        queryParameters: {'keyword': keyword},
      );
      return (response['messages'] as List)
          .map((json) => Message.fromJson(json))
          .toList();
    } catch (e) {
      rethrow;
    }
  }

  // 获取未读消息数
  Future<int> getUnreadCount(String groupId) async {
    try {
      final response = await _apiClient.get('/groups/$groupId/messages/unread');
      return response['count'];
    } catch (e) {
      rethrow;
    }
  }

  // 清空聊天记录
  Future<void> clearMessages(String groupId) async {
    try {
      await _apiClient.delete('/groups/$groupId/messages');
    } catch (e) {
      rethrow;
    }
  }

  // 处理收到的消息
  void handleMessageReceived(Message message) {
    _messageController.add(message);
  }

  // 处理消息状态变更
  void handleMessageStatusChanged(String messageId, String status) {
    _messageStatusController.add({
      'messageId': messageId,
      'status': status,
    });
  }

  @override
  void onClose() {
    _messageController.close();
    _messageStatusController.close();
    super.onClose();
  }
} 