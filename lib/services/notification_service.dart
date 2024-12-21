import '../data/remote/mysql/knowledge_database.dart';
import '../data/remote/redis/redis_cache.dart';
import '../data/remote/push/push_client.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'dart:io';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';

enum NotificationType {
  system,     // 系统通知
  business,   // 业务通知
  social,     // 社交通知
  marketing,  // 营销通知
}

enum NotificationPriority {
  low,
  normal,
  high,
  urgent,
}

class NotificationService {
  final KnowledgeDatabase _knowledgeDb;
  final RedisCache _redisCache;
  final PushClient _pushClient;
  final FirebaseMessaging _fcm;
  final LocalDatabase _localDb;

  NotificationService(
    this._knowledgeDb,
    this._redisCache,
    this._pushClient,
    this._fcm,
    this._localDb,
  );

  // 初始化通知服务
  Future<void> initialize() async {
    // 1. 请求通知权限
    await _fcm.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );

    // 2. 获取并更新FCM Token
    final token = await _fcm.getToken();
    if (token != null) {
      await _updateFcmToken(token);
    }

    // 3. 监听Token刷新
    _fcm.onTokenRefresh.listen(_updateFcmToken);

    // 4. 配置消息处理
    FirebaseMessaging.onMessage.listen(_handleForegroundMessage);
    FirebaseMessaging.onMessageOpenedApp.listen(_handleMessageOpenedApp);
    FirebaseMessaging.onBackgroundMessage(_handleBackgroundMessage);

    // 5. 初始化本地通知
    await _initializeLocalNotifications();
  }

  // 初始化本地通知
  Future<void> _initializeLocalNotifications() async {
    final flutterLocalNotificationsPlugin = FlutterLocalNotificationsPlugin();
    
    const initializationSettingsAndroid = 
        AndroidInitializationSettings('@mipmap/ic_launcher');
    
    final initializationSettingsIOS = DarwinInitializationSettings(
      requestAlertPermission: false,
      requestBadgePermission: false,
      requestSoundPermission: false,
    );
    
    final initializationSettings = InitializationSettings(
      android: initializationSettingsAndroid,
      iOS: initializationSettingsIOS,
    );
    
    await flutterLocalNotificationsPlugin.initialize(
      initializationSettings,
      onDidReceiveNotificationResponse: _handleLocalNotificationTap,
    );
  }

  // 显示本地通知
  Future<void> showLocalNotification(
    String title,
    String body,
    NotificationType type, {
    Map<String, dynamic>? data,
    String? imageUrl,
    bool playSound = true,
  }) async {
    final flutterLocalNotificationsPlugin = FlutterLocalNotificationsPlugin();
    
    // 1. 构建通知详情
    final androidDetails = AndroidNotificationDetails(
      'default_channel',
      'Default Channel',
      channelDescription: 'Default notification channel',
      importance: Importance.high,
      priority: Priority.high,
      playSound: playSound,
      styleInformation: imageUrl != null
          ? BigPictureStyleInformation(
              FilePathAndroidBitmap(await _downloadAndSaveImage(imageUrl)),
              hideExpandedLargeIcon: true,
            )
          : null,
    );
    
    final iOSDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: playSound,
    );
    
    final details = NotificationDetails(
      android: androidDetails,
      iOS: iOSDetails,
    );

    // 2. 显示通知
    await flutterLocalNotificationsPlugin.show(
      DateTime.now().millisecondsSinceEpoch.remainder(100000),
      title,
      body,
      details,
      payload: jsonEncode({
        'type': type.toString(),
        'data': data,
      }),
    );

    // 3. 保存通知记录
    await _saveNotification(
      title: title,
      body: body,
      type: type,
      data: data,
      isLocal: true,
    );
  }

  // 处理本地通知点击
  void _handleLocalNotificationTap(NotificationResponse response) {
    if (response.payload != null) {
      try {
        final payload = jsonDecode(response.payload!);
        final type = NotificationType.values.byName(payload['type']);
        _handleNotificationTap(type, payload['data']);
      } catch (e) {
        print('Error parsing notification payload: $e');
      }
    }
  }

  // 处理通知点击
  void _handleNotificationTap(
    NotificationType type,
    Map<String, dynamic>? data,
  ) {
    switch (type) {
      case NotificationType.system:
        // 处理系统通知点击
        break;
      case NotificationType.business:
        // 处理业务通知点击
        break;
      case NotificationType.social:
        // 处理社交通知点击
        break;
      case NotificationType.marketing:
        // 处理营销通知点击
        break;
    }
  }

  // 下载并保存图片
  Future<String> _downloadAndSaveImage(String imageUrl) async {
    final response = await http.get(Uri.parse(imageUrl));
    final documentDirectory = await getApplicationDocumentsDirectory();
    final file = File('${documentDirectory.path}/notification_image.jpg');
    await file.writeAsBytes(response.bodyBytes);
    return file.path;
  }

  // 发送通知
  Future<String> sendNotification(Notification notification) async {
    final notificationId = DateTime.now().millisecondsSinceEpoch.toString();
    
    // 1. 保存通知记录
    await _knowledgeDb._conn.query('''
      INSERT INTO notifications (
        id, type, priority, title, content, sender_id,
        receiver_id, metadata, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, NOW())
    ''', [
      notificationId,
      notification.type.toString(),
      notification.priority.toString(),
      notification.title,
      notification.content,
      notification.senderId,
      notification.receiverId,
      notification.metadata != null ? jsonEncode(notification.metadata) : null,
    ]);

    // 2. 更新未读计数
    final countKey = _getUnreadCountKey(notification.receiverId);
    await _redisCache.increment(countKey);

    // 3. 发送推送
    if (notification.needPush) {
      await _pushClient.sendPush(
        userId: notification.receiverId,
        title: notification.title,
        body: notification.content,
        data: {
          'type': notification.type.toString(),
          'notification_id': notificationId,
        },
      );
    }

    return notificationId;
  }

  // 批量发送通知
  Future<void> sendBatchNotifications(
    List<String> receiverIds,
    Notification template,
  ) async {
    // 1. 批量插入通知记录
    final batch = receiverIds.map((receiverId) {
      final notificationId = '${DateTime.now().millisecondsSinceEpoch}_$receiverId';
      return [
        notificationId,
        template.type.toString(),
        template.priority.toString(),
        template.title,
        template.content,
        template.senderId,
        receiverId,
        template.metadata != null ? jsonEncode(template.metadata) : null,
      ];
    }).toList();

    await _knowledgeDb._conn.queryMulti('''
      INSERT INTO notifications (
        id, type, priority, title, content, sender_id,
        receiver_id, metadata, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, NOW())
    ''', batch);

    // 2. 批量更新未读计数
    final pipeline = _redisCache.pipeline();
    for (final receiverId in receiverIds) {
      final countKey = _getUnreadCountKey(receiverId);
      pipeline.increment(countKey);
    }
    await pipeline.execute();

    // 3. 批量发送推送
    if (template.needPush) {
      await Future.wait(
        receiverIds.map((receiverId) => _pushClient.sendPush(
          userId: receiverId,
          title: template.title,
          body: template.content,
          data: {
            'type': template.type.toString(),
          },
        )),
      );
    }
  }

  // 标记通知为已读
  Future<void> markAsRead(String notificationId, String userId) async {
    await _knowledgeDb._conn.query('''
      UPDATE notifications 
      SET read_at = NOW()
      WHERE id = ? AND receiver_id = ?
    ''', [notificationId, userId]);

    // 更新未读计数
    final countKey = _getUnreadCountKey(userId);
    await _redisCache.decrement(countKey);
  }

  // 批量标记为已读
  Future<void> markAllAsRead(String userId, {NotificationType? type}) async {
    var query = '''
      UPDATE notifications 
      SET read_at = NOW()
      WHERE receiver_id = ? AND read_at IS NULL
    ''';
    final params = [userId];

    if (type != null) {
      query += ' AND type = ?';
      params.add(type.toString());
    }

    final result = await _knowledgeDb._conn.query(query, params);
    final updatedCount = result.affectedRows ?? 0;

    // 更新未读计数
    if (updatedCount > 0) {
      final countKey = _getUnreadCountKey(userId);
      await _redisCache.set(countKey, '0');
    }
  }

  // 获取通知列表
  Future<List<Notification>> getNotifications(
    String userId, {
    NotificationType? type,
    bool? unreadOnly,
    int? limit,
    int? offset,
  }) async {
    var query = '''
      SELECT * FROM notifications
      WHERE receiver_id = ?
    ''';
    final params = [userId];

    if (type != null) {
      query += ' AND type = ?';
      params.add(type.toString());
    }

    if (unreadOnly == true) {
      query += ' AND read_at IS NULL';
    }

    query += ' ORDER BY created_at DESC';

    if (limit != null) {
      query += ' LIMIT ?';
      params.add(limit);

      if (offset != null) {
        query += ' OFFSET ?';
        params.add(offset);
      }
    }

    final results = await _knowledgeDb._conn.query(query, params);
    return results.map((r) => Notification.fromJson(r.fields)).toList();
  }

  // 获取未读数量
  Future<int> getUnreadCount(String userId, {NotificationType? type}) async {
    if (type == null) {
      // 从缓存获取总未读数
      final countKey = _getUnreadCountKey(userId);
      final cached = await _redisCache.get(countKey);
      if (cached != null) {
        return int.parse(cached);
      }
    }

    // 从数据库获取
    var query = '''
      SELECT COUNT(*) as count 
      FROM notifications
      WHERE receiver_id = ? AND read_at IS NULL
    ''';
    final params = [userId];

    if (type != null) {
      query += ' AND type = ?';
      params.add(type.toString());
    }

    final results = await _knowledgeDb._conn.query(query, params);
    final count = results.first['count'] as int;

    // 更新缓存
    if (type == null) {
      final countKey = _getUnreadCountKey(userId);
      await _redisCache.set(countKey, count.toString());
    }

    return count;
  }

  // 删除通知
  Future<void> deleteNotification(String notificationId, String userId) async {
    await _knowledgeDb._conn.query('''
      DELETE FROM notifications 
      WHERE id = ? AND receiver_id = ?
    ''', [notificationId, userId]);
  }

  // 清理过期通知
  Future<void> cleanupNotifications(Duration retention) async {
    final cutoff = DateTime.now().subtract(retention);
    
    await _knowledgeDb._conn.query('''
      DELETE FROM notifications 
      WHERE created_at < ? AND read_at IS NOT NULL
    ''', [cutoff.toIso8601String()]);
  }

  // 获取未读计数缓存键
  String _getUnreadCountKey(String userId) {
    return 'notification:unread:$userId';
  }
}

class Notification {
  final String id;
  final NotificationType type;
  final NotificationPriority priority;
  final String title;
  final String content;
  final String? senderId;
  final String receiverId;
  final Map<String, dynamic>? metadata;
  final bool needPush;
  final DateTime createdAt;
  final DateTime? readAt;

  Notification({
    required this.id,
    required this.type,
    required this.priority,
    required this.title,
    required this.content,
    this.senderId,
    required this.receiverId,
    this.metadata,
    this.needPush = true,
    required this.createdAt,
    this.readAt,
  });

  factory Notification.fromJson(Map<String, dynamic> json) {
    return Notification(
      id: json['id'],
      type: NotificationType.values.byName(json['type']),
      priority: NotificationPriority.values.byName(json['priority']),
      title: json['title'],
      content: json['content'],
      senderId: json['sender_id'],
      receiverId: json['receiver_id'],
      metadata: json['metadata'] != null 
          ? jsonDecode(json['metadata'])
          : null,
      createdAt: DateTime.parse(json['created_at']),
      readAt: json['read_at'] != null 
          ? DateTime.parse(json['read_at'])
          : null,
    );
  }
}

// 后台消息处理
@pragma('vm:entry-point')
Future<void> _handleBackgroundMessage(RemoteMessage message) async {
  await Firebase.initializeApp();
  
  final localDb = await LocalDatabase.getInstance();
  await localDb.saveNotification(
    title: message.notification?.title ?? '',
    body: message.notification?.body ?? '',
    type: _getNotificationType(message.data['type']),
    data: message.data,
  );
} 