import 'package:get/get.dart';
import '../core/network/api_client.dart';
import '../data/models/group_notification.dart';
import 'dart:async';

class GroupNotificationService extends GetxService {
  final ApiClient _apiClient;
  
  // 通知流
  final _notificationController = StreamController<GroupNotification>.broadcast();
  Stream<GroupNotification> get onNotificationReceived => _notificationController.stream;

  GroupNotificationService({required ApiClient apiClient}) : _apiClient = apiClient;

  // 获取群通知列表
  Future<List<GroupNotification>> getNotifications(String groupId) async {
    try {
      final response = await _apiClient.get('/groups/$groupId/notifications');
      return (response['notifications'] as List)
          .map((json) => GroupNotification.fromJson(json))
          .toList();
    } catch (e) {
      rethrow;
    }
  }

  // 发送群通知
  Future<void> sendNotification(String groupId, {
    required String type,
    required String content,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      await _apiClient.post('/groups/$groupId/notifications', data: {
        'type': type,
        'content': content,
        if (metadata != null) 'metadata': metadata,
      });
    } catch (e) {
      rethrow;
    }
  }

  // 处理入群申请
  Future<void> handleJoinRequest(String groupId, String userId, bool approved) async {
    try {
      await _apiClient.post('/groups/$groupId/join-requests/$userId', data: {
        'approved': approved,
      });
    } catch (e) {
      rethrow;
    }
  }

  // 标记通知已读
  Future<void> markAsRead(String groupId, List<String> notificationIds) async {
    try {
      await _apiClient.post('/groups/$groupId/notifications/read', data: {
        'notificationIds': notificationIds,
      });
    } catch (e) {
      rethrow;
    }
  }

  // 获取未读通知数
  Future<int> getUnreadCount(String groupId) async {
    try {
      final response = await _apiClient.get('/groups/$groupId/notifications/unread');
      return response['count'];
    } catch (e) {
      rethrow;
    }
  }

  // 清空通知
  Future<void> clearNotifications(String groupId) async {
    try {
      await _apiClient.delete('/groups/$groupId/notifications');
    } catch (e) {
      rethrow;
    }
  }

  // 处理收到的通知
  void handleNotificationReceived(GroupNotification notification) {
    _notificationController.add(notification);
  }

  @override
  void onClose() {
    _notificationController.close();
    super.onClose();
  }
} 