import 'package:injectable/injectable.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import '../logger/logger.dart';
import '../storage/local_storage.dart';

@singleton
class NotificationService {
  final FirebaseMessaging _messaging;
  final FlutterLocalNotificationsPlugin _localNotifications;
  final LocalStorage _storage;
  final AppLogger _logger;
  static const _tokenKey = 'fcm_token';

  NotificationService(
    this._messaging,
    this._localNotifications,
    this._storage,
    this._logger,
  );

  Future<void> init() async {
    try {
      // 配置本地通知
      await _initLocalNotifications();

      // 请求通知权限
      final settings = await _messaging.requestPermission(
        alert: true,
        badge: true,
        sound: true,
      );

      if (settings.authorizationStatus == AuthorizationStatus.authorized) {
        // 获取FCM令牌
        final token = await _messaging.getToken();
        if (token != null) {
          await _storage.setString(_tokenKey, token);
          _logger.info('FCM Token: $token');
        }

        // 监听令牌刷新
        _messaging.onTokenRefresh.listen((token) {
          _storage.setString(_tokenKey, token);
          _logger.info('FCM Token refreshed: $token');
        });

        // 配置消息处理
        _setupMessageHandlers();
      }
    } catch (e, stack) {
      _logger.error('Error initializing notification service', e, stack);
    }
  }

  Future<void> _initLocalNotifications() async {
    const initializationSettings = InitializationSettings(
      android: AndroidInitializationSettings('@mipmap/ic_launcher'),
      iOS: DarwinInitializationSettings(),
    );

    await _localNotifications.initialize(
      initializationSettings,
      onDidReceiveNotificationResponse: _onNotificationTapped,
    );
  }

  void _setupMessageHandlers() {
    // 处理前台消息
    FirebaseMessaging.onMessage.listen(_handleForegroundMessage);

    // 处理后台消息点击
    FirebaseMessaging.onMessageOpenedApp.listen(_handleMessageOpenedApp);
  }

  Future<void> _handleForegroundMessage(RemoteMessage message) async {
    _logger.info('Received foreground message: ${message.messageId}');

    final notification = message.notification;
    if (notification != null) {
      await _localNotifications.show(
        notification.hashCode,
        notification.title,
        notification.body,
        NotificationDetails(
          android: AndroidNotificationDetails(
            'default_channel',
            'Default Channel',
            importance: Importance.high,
            priority: Priority.high,
          ),
        ),
        payload: message.data.toString(),
      );
    }
  }

  void _handleMessageOpenedApp(RemoteMessage message) {
    _logger.info('Message opened app: ${message.messageId}');
    // 处理消息点击事件
  }

  void _onNotificationTapped(NotificationResponse response) {
    _logger.info('Notification tapped: ${response.payload}');
    // 处理通知点击事件
  }

  Future<void> subscribeToTopic(String topic) async {
    try {
      await _messaging.subscribeToTopic(topic);
      _logger.info('Subscribed to topic: $topic');
    } catch (e, stack) {
      _logger.error('Error subscribing to topic', e, stack);
    }
  }

  Future<void> unsubscribeFromTopic(String topic) async {
    try {
      await _messaging.unsubscribeFromTopic(topic);
      _logger.info('Unsubscribed from topic: $topic');
    } catch (e, stack) {
      _logger.error('Error unsubscribing from topic', e, stack);
    }
  }

  Future<String?> getToken() async {
    return _storage.getString(_tokenKey);
  }
} 