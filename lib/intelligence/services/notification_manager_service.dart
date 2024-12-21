class NotificationManagerService extends GetxService {
  final SubscriptionService _subscriptionService;
  final EventTrackingService _eventTracking;
  final LogManagerService _logManager;
  
  // 通知配置
  static const Map<SubscriptionPlan, Map<String, dynamic>> _notificationConfig = {
    SubscriptionPlan.basic: {
      'channels': {'system', 'critical'},
      'max_daily': 10,
      'custom_channels': false,
    },
    SubscriptionPlan.pro: {
      'channels': {'system', 'critical', 'analysis', 'insights'},
      'max_daily': 50,
      'custom_channels': true,
    },
    SubscriptionPlan.premium: {
      'channels': {'system', 'critical', 'analysis', 'insights', 'custom'},
      'max_daily': -1,  // 无限制
      'custom_channels': true,
    },
  };
  
  // 通知计数器
  final Map<String, int> _dailyCount = {};
  
  // 用户订阅
  final Map<String, Set<String>> _userSubscriptions = {};
  
  NotificationManagerService({
    required SubscriptionService subscriptionService,
    required EventTrackingService eventTracking,
    required LogManagerService logManager,
  })  : _subscriptionService = subscriptionService,
        _eventTracking = eventTracking,
        _logManager = logManager {
    _startDailyReset();
  }

  Future<void> sendNotification(AINotification notification) async {
    try {
      // 验证通知权限
      if (!_canSendNotification(notification)) {
        throw AIException(
          '无权发送此类通知',
          code: 'NOTIFICATION_NOT_ALLOWED',
        );
      }

      // 检查每日限制
      if (!_checkDailyLimit(notification.userId)) {
        throw AIException(
          '已达到每日通知限制',
          code: 'DAILY_LIMIT_EXCEEDED',
        );
      }

      // 检查用户订阅
      if (!_isUserSubscribed(notification)) {
        return;  // 用户未订阅此类通知
      }

      // 发送通知
      await _deliverNotification(notification);
      
      // 更新计数
      _incrementDailyCount(notification.userId);
      
      // 记录事件
      await _trackNotificationEvent(notification, 'sent');
    } catch (e) {
      await _trackNotificationEvent(notification, 'failed', error: e);
      rethrow;
    }
  }

  Future<void> subscribeToChannel(
    String userId,
    String channel, {
    Map<String, dynamic>? preferences,
  }) async {
    try {
      // 验证通道
      if (!_isChannelAvailable(channel)) {
        throw AIException(
          '无效的通知通道',
          code: 'INVALID_CHANNEL',
        );
      }

      // 添加订阅
      _userSubscriptions
        .putIfAbsent(userId, () => {})
        .add(channel);
      
      // 记录事件
      await _trackSubscriptionEvent(
        userId,
        channel,
        'subscribed',
        preferences: preferences,
      );
    } catch (e) {
      await _logManager.log(
        'Channel subscription failed',
        userId: userId,
        assistantName: 'system',
        level: LogLevel.error,
        metadata: {
          'channel': channel,
          'error': e.toString(),
        },
      );
      rethrow;
    }
  }

  Future<void> unsubscribeFromChannel(
    String userId,
    String channel,
  ) async {
    try {
      _userSubscriptions[userId]?.remove(channel);
      
      await _trackSubscriptionEvent(
        userId,
        channel,
        'unsubscribed',
      );
    } catch (e) {
      await _logManager.log(
        'Channel unsubscription failed',
        userId: userId,
        assistantName: 'system',
        level: LogLevel.error,
        metadata: {
          'channel': channel,
          'error': e.toString(),
        },
      );
    }
  }

  Set<String> getAvailableChannels() {
    final plan = _subscriptionService.currentPlan;
    return _notificationConfig[plan]!['channels'] as Set<String>;
  }

  bool _canSendNotification(AINotification notification) {
    final plan = _subscriptionService.currentPlan;
    final config = _notificationConfig[plan]!;
    
    // 检查通道可用性
    if (!config['channels'].contains(notification.channel)) {
      return false;
    }
    
    // 检查自定义通道
    if (notification.channel == 'custom' && !config['custom_channels']) {
      return false;
    }
    
    return true;
  }

  bool _checkDailyLimit(String userId) {
    final plan = _subscriptionService.currentPlan;
    final maxDaily = _notificationConfig[plan]!['max_daily'] as int;
    
    if (maxDaily == -1) return true;  // 无限制
    
    final count = _dailyCount[userId] ?? 0;
    return count < maxDaily;
  }

  bool _isUserSubscribed(AINotification notification) {
    final subscriptions = _userSubscriptions[notification.userId];
    if (subscriptions == null) return false;
    
    return subscriptions.contains(notification.channel);
  }

  bool _isChannelAvailable(String channel) {
    final availableChannels = getAvailableChannels();
    return availableChannels.contains(channel);
  }

  void _incrementDailyCount(String userId) {
    _dailyCount[userId] = (_dailyCount[userId] ?? 0) + 1;
  }

  Future<void> _deliverNotification(AINotification notification) async {
    // TODO: 实现实际的通知发送逻辑
  }

  Future<void> _trackNotificationEvent(
    AINotification notification,
    String status, {
    dynamic error,
  }) async {
    await _eventTracking.trackEvent(AIEvent(
      id: 'notification_${DateTime.now().millisecondsSinceEpoch}',
      userId: notification.userId,
      assistantName: 'system',
      type: AIEventType.notification,
      data: {
        'notification_id': notification.id,
        'channel': notification.channel,
        'status': status,
        'error': error?.toString(),
      },
    ));
  }

  Future<void> _trackSubscriptionEvent(
    String userId,
    String channel,
    String action, {
    Map<String, dynamic>? preferences,
  }) async {
    await _eventTracking.trackEvent(AIEvent(
      id: 'subscription_${DateTime.now().millisecondsSinceEpoch}',
      userId: userId,
      assistantName: 'system',
      type: AIEventType.subscription,
      data: {
        'channel': channel,
        'action': action,
        'preferences': preferences,
      },
    ));
  }

  void _startDailyReset() {
    Timer.periodic(Duration(hours: 1), (_) {
      final now = DateTime.now();
      if (now.hour == 0) {  // 每天0点重置
        _dailyCount.clear();
      }
    });
  }
} 