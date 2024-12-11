import 'package:flutter/foundation.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import '../models/notification.dart';

class NotificationService extends GetxController {
  final _notifications = <NotificationMessage>[];
  final FlutterLocalNotificationsPlugin _flutterLocalNotificationsPlugin =
      FlutterLocalNotificationsPlugin();

  List<NotificationMessage> get notifications => List.unmodifiable(_notifications);

  Future<void> init() async {
    const androidSettings = AndroidInitializationSettings('app_icon');
    const iosSettings = DarwinInitializationSettings();
    const initSettings = InitializationSettings(
      android: androidSettings,
      iOS: iosSettings,
    );

    await _flutterLocalNotificationsPlugin.initialize(
      initSettings,
      onDidReceiveNotificationResponse: (details) {
        // 处理通知点击
      },
    );
  }

  Future<void> showNotification(NotificationMessage notification) async {
    _notifications.add(notification);
    update();

    const androidDetails = AndroidNotificationDetails(
      'default_channel',
      'Default Channel',
      channelDescription: 'Default notification channel',
      importance: Importance.high,
      priority: Priority.high,
    );

    const iosDetails = DarwinNotificationDetails();

    const details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    await _flutterLocalNotificationsPlugin.show(
      notification.id.hashCode,
      notification.title,
      notification.body,
      details,
    );
  }

  void markAsRead(String id) {
    final notification = _notifications.firstWhere((n) => n.id == id);
    notification.isRead = true;
    update();
  }

  List<NotificationMessage> getUnreadNotifications() {
    return _notifications.where((n) => !n.isRead).toList();
  }
} 