import 'package:get/get.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class NotificationService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final FlutterLocalNotificationsPlugin _notifications = FlutterLocalNotificationsPlugin();
  final notificationHistory = <Map<String, dynamic>>[].obs;
  final notificationSettings = <String, dynamic>{}.obs;

  @override
  void onInit() {
    super.onInit();
    _initNotifications();
  }

  Future<void> _initNotifications() async {
    try {
      await _loadNotificationSettings();
      await _loadNotificationHistory();
      await _initializeLocalNotifications();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize notifications', data: {'error': e.toString()});
    }
  }

  // 显示通知
  Future<void> showNotification({
    required String title,
    required String body,
    String? payload,
    NotificationDetails? details,
    int id = 0,
  }) async {
    try {
      final notificationDetails = details ?? await _getDefaultNotificationDetails();
      
      await _notifications.show(
        id,
        title,
        body,
        notificationDetails,
        payload: payload,
      );

      await _recordNotification({
        'id': id,
        'title': title,
        'body': body,
        'payload': payload,
        'details': details?.toMap(),
      });
    } catch (e) {
      await _loggingService.log('error', 'Failed to show notification', data: {'title': title, 'error': e.toString()});
      rethrow;
    }
  }

  // 显示定时通知
  Future<void> scheduleNotification({
    required String title,
    required String body,
    required DateTime scheduledDate,
    String? payload,
    NotificationDetails? details,
    int id = 0,
  }) async {
    try {
      final notificationDetails = details ?? await _getDefaultNotificationDetails();
      
      await _notifications.zonedSchedule(
        id,
        title,
        body,
        scheduledDate.toLocal(),
        notificationDetails,
        androidAllowWhileIdle: true,
        uiLocalNotificationDateInterpretation:
            UILocalNotificationDateInterpretation.absoluteTime,
        payload: payload,
      );

      await _recordNotification({
        'id': id,
        'title': title,
        'body': body,
        'scheduled_date': scheduledDate.toIso8601String(),
        'payload': payload,
        'details': details?.toMap(),
      });
    } catch (e) {
      await _loggingService.log('error', 'Failed to schedule notification', data: {'title': title, 'error': e.toString()});
      rethrow;
    }
  }

  // 取消通知
  Future<void> cancelNotification(int id) async {
    try {
      await _notifications.cancel(id);
    } catch (e) {
      await _loggingService.log('error', 'Failed to cancel notification', data: {'id': id, 'error': e.toString()});
      rethrow;
    }
  }

  // 取消所有通知
  Future<void> cancelAllNotifications() async {
    try {
      await _notifications.cancelAll();
    } catch (e) {
      await _loggingService.log('error', 'Failed to cancel all notifications', data: {'error': e.toString()});
      rethrow;
    }
  }

  // 更新通知设置
  Future<void> updateNotificationSettings(Map<String, dynamic> settings) async {
    try {
      notificationSettings.value = settings;
      await _saveNotificationSettings();
    } catch (e) {
      await _loggingService.log('error', 'Failed to update notification settings', data: {'error': e.toString()});
      rethrow;
    }
  }

  // 获取通知历史
  Future<List<Map<String, dynamic>>> getNotificationHistory({
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      var history = notificationHistory.toList();

      if (startDate != null || endDate != null) {
        history = history.where((record) {
          final timestamp = DateTime.parse(record['timestamp']);
          if (startDate != null && timestamp.isBefore(startDate)) return false;
          if (endDate != null && timestamp.isAfter(endDate)) return false;
          return true;
        }).toList();
      }

      return history;
    } catch (e) {
      await _loggingService.log('error', 'Failed to get notification history', data: {'error': e.toString()});
      return [];
    }
  }

  Future<void> _initializeLocalNotifications() async {
    try {
      const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
      const iOSSettings = DarwinInitializationSettings();
      
      const initSettings = InitializationSettings(
        android: androidSettings,
        iOS: iOSSettings,
      );

      await _notifications.initialize(
        initSettings,
        onDidReceiveNotificationResponse: _onNotificationTapped,
      );
    } catch (e) {
      rethrow;
    }
  }

  Future<NotificationDetails> _getDefaultNotificationDetails() async {
    try {
      const androidDetails = AndroidNotificationDetails(
        'default_channel',
        'Default Channel',
        channelDescription: 'Default notification channel',
        importance: Importance.high,
        priority: Priority.high,
      );

      const iOSDetails = DarwinNotificationDetails();

      return const NotificationDetails(
        android: androidDetails,
        iOS: iOSDetails,
      );
    } catch (e) {
      rethrow;
    }
  }

  void _onNotificationTapped(NotificationResponse response) {
    try {
      // 处理通知点击事件
      if (response.payload != null) {
        // TODO: 处理通知点击
      }
    } catch (e) {
      _loggingService.log('error', 'Failed to handle notification tap', data: {'error': e.toString()});
    }
  }

  Future<void> _loadNotificationSettings() async {
    try {
      final settings = await _storageService.getLocal('notification_settings');
      if (settings != null) {
        notificationSettings.value = Map<String, dynamic>.from(settings);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveNotificationSettings() async {
    try {
      await _storageService.saveLocal('notification_settings', notificationSettings.value);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadNotificationHistory() async {
    try {
      final history = await _storageService.getLocal('notification_history');
      if (history != null) {
        notificationHistory.value = List<Map<String, dynamic>>.from(history);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveNotificationHistory() async {
    try {
      await _storageService.saveLocal('notification_history', notificationHistory);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _recordNotification(Map<String, dynamic> notification) async {
    try {
      final record = {
        ...notification,
        'timestamp': DateTime.now().toIso8601String(),
      };

      notificationHistory.insert(0, record);
      
      // 只保留最近1000条记录
      if (notificationHistory.length > 1000) {
        notificationHistory.removeRange(1000, notificationHistory.length);
      }
      
      await _saveNotificationHistory();
    } catch (e) {
      rethrow;
    }
  }
} 