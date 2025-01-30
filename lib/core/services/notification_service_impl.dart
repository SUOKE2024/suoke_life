import 'package:suoke_life/lib/core/services/notification_service.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

class NotificationServiceImpl implements NotificationService {
  final FlutterLocalNotifications _localNotifications = FlutterLocalNotifications();

  @override
  Future<void> sendNotification(String message) async {
    try {
      // 实现通知逻辑
      // 这里假设使用本地通知插件发送通知
      const androidDetails = AndroidNotificationDetails(
        'default_channel',
        'Default Channel',
        channelDescription: 'Default notification channel',
        importance: Importance.high,
        priority: Priority.high,
      );

      const iOSDetails = DarwinNotificationDetails();

      const notificationDetails = NotificationDetails(
        android: androidDetails,
        iOS: iOSDetails,
      );

      await _localNotifications.show(
        0,
        '通知',
        message,
        notificationDetails,
      );

      print('Notification sent: $message');
    } catch (e) {
      print('Failed to send notification: $e');
    }
  }
} 